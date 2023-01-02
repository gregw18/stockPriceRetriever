"""
Interface securities collection.
Should not communicate directly with mySql.
V0.01, November 23, 2022
"""

#from memory_profiler import profile

from datetime import datetime, date, timedelta
import json
import os
import sys

import dbAccess
from historicalPricesInterface import HistoricalPricesInterface
import settings
from securitiesInterface import SecuritiesInterface
from security import Security
import sprEnums
from utilsInterface import UtilsInterface
from webPriceInfo import WebPriceInfo
from yahooInterface import retrieve_historical_prices, retrieve_daily_data

class Securities:

    def __init__(self):
        self.mySettings = settings.Settings.instance()
        self.securitiesDict = {}
        self.dailyHistoryCode = self.mySettings.db_daily_history_code
        self.weeklyHistoryCode = self.mySettings.db_weekly_history_code
        self.securitiesInter = SecuritiesInterface()
        self.historyInter = HistoricalPricesInterface()
        self.utilsInter = UtilsInterface()

    def __str__(self):
        """
        Return contents of securitiesDict, for troubleshooting purposes.
        """
        retStr = ""
        for key in self.securitiesDict:
            retStr += "\n" + str(self.securitiesDict[key])

        return retStr

    def do_maintenance(self):
        self.utilsInter.connect()
        if self._isPriceGroomingDue():
            self._groomPrices()
        self.utilsInter.disconnect()

    def do_daily_updates(self):
        """
        Runs the stuff that should run every day - price update and price grooming.
        """
        #myUtilsInter = UtilsInterface()
        self.utilsInter.connect()
        self.load()
        numUpdated = self.do_daily_price_update(date.today())
        self.do_maintenance()
        self.utilsInter.disconnect()

        return numUpdated

    def load(self):
        """
        Read in securities from securities table. Convert to a dictionary of security,
        key = symbol.
        """
        print(f"\nStarting load.")
        dbSecurities = self.securitiesInter.get_securities()

        if not (dbSecurities is None):
            self.securitiesDict = {}
            for tmpSecurity in dbSecurities:
                newSec = Security()
                newSec.pop_from_dict(tmpSecurity)
                #print(f"load adding security {newSec}")
                self.securitiesDict[newSec.symbol] = newSec
                print(f"load just read in security with symbol {newSec.symbol}")
        else:
                print("Securities.load: No securities were found in the table.")
        print(f"load completed with {len(self.securitiesDict)} records in securitiesDict.\n")

    def loadNewList(self, targetSecurities):
        """
        Receives: dictionary of targetSecurity, key = symbol.
        Returns: True if succeeds, false otherwise.
        Updates list of securities in database to match given list.
        1. Delete any securities in the database that aren't in the new list.
        2. For given list, if already exists in database, update name, buy/sell prices.
                if doesn't already exist, add it.
        3. Retrieve historical prices for that don't have them.
        4. Finally, clear out existing in-memory list and reload.
        """
        updated = False
        print(f"\nStarting loadNewList")
        self._remove_missing_securities(targetSecurities)
        for symbol in targetSecurities:
            #print(f"loadNewList is looking at symbol {symbol}")
            newTarget = targetSecurities[symbol]
            #print(f"newTarget = {newTarget}, name = {newTarget.name}")
            if symbol in self.securitiesDict:
                self._update_security(newTarget)
            else:
                #print(f"About to try adding security: {symbol}")
                self._add_security(newTarget)
            
        self.load()
        updated = self.retrieve_full_price_histories()
        print(f"Finished loadNewList.\n")

        return updated

    #@profile
    def do_daily_price_update(self, currentDate):
        """
        Daily price update process. Ensures that have full price history downloaded for
        every security, runs grooming to remove old prices, ensures that every security
        has been updated with today's closing price, and, if it is appropriate, updates
        the weekly closing price for every security.
        Also uses new data to update in-memory collection of securities.
        Receives: Date running update for (assumed to be today, but useful for testing.)
        Returns: Number of securities that downloaded price for.
        """
        print(f"Starting do_daily_price_update, currentDate={currentDate}")
        numUpdated = 0
        #self.utilsInter.connect()
        
        # Check if we've already run today.
        symbolsToUpdate = self._get_symbols_needing_price_update(currentDate)
        if len(symbolsToUpdate) == 0:
            print(f"Exiting do_daily_price_update because already ran today.")
            return numUpdated

        if not self._are_all_downloaded(self.securitiesDict):
            self.retrieve_full_price_histories()

        weeklyUpdateDue = self._is_weekly_price_update_due()
        weeklyPriceDate = self._get_weekly_price_date(currentDate)
        
        # Do prices for all securities that we haven't previously done today.
        for tmpSymbol in symbolsToUpdate:
            newPrice = retrieve_daily_data(tmpSymbol, self.mySettings)
            print(f"newPrice={newPrice}")
            if newPrice.currentPrice > 0:
                tmpSecurity = self.securitiesDict[tmpSymbol]
                changedFieldNames, newValues = tmpSecurity.get_changed_fields(newPrice, currentDate)
                print(f"changedFieldNames={changedFieldNames}, newValues={newValues}")
                if len(changedFieldNames) > 0:
                    print(f"Attempting to do updates for {tmpSecurity}.")
                    self.securitiesInter.update_security(tmpSecurity.id, changedFieldNames, newValues)
                    self.historyInter.save_daily_price_for_security(tmpSecurity.id, 
                                                                    newPrice.currentPrice, 
                                                                    currentDate)
                    if weeklyUpdateDue:
                        self.historyInter.save_weekly_price_for_security(tmpSecurity.id, 
                                                                        weeklyPriceDate)
                    tmpSecurity.update_values(newPrice)
                    numUpdated += 1
            else:
                print(f"Failed to retrieve daily price for {tmpSymbol}, so didn't save anything.")

        if weeklyUpdateDue:
            self.utilsInter.set_last_weekly_update_date()

        #self.utilsInter.disconnect()
        print(f"Finished do_daily_price_update, numUpdated={numUpdated}")

        return numUpdated

    def reset_daily_prices(self):
        """
        Reset database so that can re-run daily price update, without getting multiple
        records for the same date.
        Resets currentPriceDate in securities table to yesterday, so that price update
        will run gain. Note that not replacing currentPrice or previousClosePrice, as don't
        know what previous values were, and will be replaced anyway if re-run daily price update.
        Deletes any daily/weekly prices with today's date. If weekly price update ran today,
        reset lastWeeklyPriceUpdate in admin table to a week ago.
        """
        self.utilsInter.connect()
        self.securitiesInter.reset_daily_prices()
        self.historyInter.reset_daily_prices()
        self.utilsInter.reset_daily_prices()
        self.utilsInter.disconnect()

    def retrieve_full_price_histories(self):
        """
        Download full daily/weekly price histories for any security for which we
        don't already have them.
        """
        today, dailyHistoryStart, weeklyHistoryStart = self._get_full_history_dates()

        # Retrieve and store daily and weekly price data for each security that
        # hasn't already had it done.
        numDownloaded = 0
        for tmpSecurity in self.securitiesDict.values():
            print(f"retrieve_full_price_history working on {tmpSecurity.symbol}")
            if not (tmpSecurity.fullHistoryDownloaded):
                dailyPrices = retrieve_historical_prices(tmpSecurity.symbol,
                                                            dailyHistoryStart,
                                                            today,
                                                            self.mySettings.daily_price_code)
                if len(dailyPrices) > 0:
                    # Don't go any further if first download failed.
                    downloaded = self.historyInter.save_daily_historical_prices(tmpSecurity.id, dailyPrices)
                    print(f"retrieve_full_price_history saved daily prices.")

                    weeklyPrices = retrieve_historical_prices(tmpSecurity.symbol,
                                                                weeklyHistoryStart,
                                                                today,
                                                                self.mySettings.weekly_price_code)
                    if downloaded:
                        downloaded = downloaded and self.historyInter.save_weekly_historical_prices(tmpSecurity.id, weeklyPrices)
                    print(f"retrieve_full_price_history saved weekly prices.")
                    if downloaded:
                        self.securitiesInter.mark_historical_data_retrieved(tmpSecurity.id)
                        tmpSecurity.fullHistoryDownloaded = True
                        numDownloaded += 1
                    else:
                        print(f"retrieve_full_price_histories failed to save data for "
                                f"symbol: {tmpSecurity.symbol}")

        return numDownloaded

    def retrieve_email_info(self):
        """
        Return a sorted list of securities.
        """
        emailSecs = []
        for tmpSec in self.securitiesDict.values():
            emailSecs.append(tmpSec)
        
        emailSecs.sort(key=lambda x: x.get_sort_string())

        return emailSecs

    def get_web_data(self, timePeriod):
        """
        Retrieve security and price info required for website.
        Returns a webPriceInfo for each security.
        """
        timeEnum = sprEnums.get_timePeriod_from_text(timePeriod)
        historyTable = self._get_history_table(timeEnum)
        maxAge = self._get_price_max_age(timeEnum)

        self.utilsInter.connect()

        # Verify have loaded securities list from database.
        if len(self.securitiesDict) == 0:
            self.load()

        webSecs = []
        for tmpSec in self.securitiesDict.values():
            historicalPrices = self.historyInter.get_historical_prices(tmpSec.id, 
                                                                        historyTable, 
                                                                        maxAge)
            tmpWebPrice = WebPriceInfo()
            tmpWebPrice.populate(tmpSec, historicalPrices)
            webSecs.append(tmpWebPrice)

        self.utilsInter.disconnect()

        return webSecs

    def _get_history_table(self, timeEnum):
        """
        Decide whether to read prices from daily or weekly history table.
        """
        if timeEnum in (sprEnums.timePeriods.day, sprEnums.timePeriods.days30, sprEnums.timePeriods.months3):
            table = self.mySettings.db_daily_table_name
        else:
            table = self.mySettings.db_weekly_table_name

        return table

    def _get_price_max_age(self,timeEnum):
        """ 
        Convert from time period enum to number of days of price history that want
        to display. Note that the value of the enum is actually the number of days - 
        clever solution or painful hack?
        """

        return timeEnum.value

    def _get_full_history_dates(self):
        """
        Return dates for daily and weekly periods that want price histories for.
        Returns: today, date to start daily prices from, date to start weekly prices from.
        """
        today = date.today()
        dailyDelta = timedelta(self.mySettings.daily_price_days_to_keep)
        dailyHistoryStart = today - dailyDelta
        weeklyDelta = timedelta(self.mySettings.weekly_price_weeks_to_keep * 7)
        weeklyHistoryStart = today - weeklyDelta

        return (today, dailyHistoryStart, weeklyHistoryStart)

    def _add_security(self, newTargetSecurity):
        """
        Add given TargetSecurity to database. Need to ensure that don't have existing record
        with same symbol. Note that only saves a subset of fields - just those expected
        in the source list, not fields that are retrieved from internet as part of the 
        daily price update.
        """
        return self.securitiesInter.add_security(newTargetSecurity)

    def _get_symbols_needing_price_update(self, currentDate):
        """
        Return list containing symbols for securities which haven't had daily price
        update done today.
        """
        symbols = []
        for tmpSecurity in self.securitiesDict.values():
            if tmpSecurity.currentPriceDate is None:
                # Happens when security just loaded, haven't done a daily update yet.
                symbols.append(tmpSecurity.symbol)
            elif tmpSecurity.currentPriceDate < currentDate:
                symbols.append(tmpSecurity.symbol)

        return symbols

    def _update_security(self, newTargetSecurity):
        """
        Compare values in given targetSecurity with values for same symbol in current
        in-memory list. For each, add field name, value to lists, to update database.
        """
        updated = True
        fields = []
        values = []
        symbol = newTargetSecurity.symbol
        print(f"_update_security is working on target {symbol}")

        existingSecurity = self.securitiesDict[symbol]
        if newTargetSecurity.name != existingSecurity.name:
            fields.append("name")
            values.append(newTargetSecurity.name)
        if newTargetSecurity.buyPrice != existingSecurity.buyPrice:
            fields.append("buyPrice")
            values.append(newTargetSecurity.buyPrice)
        if newTargetSecurity.sellPrice != existingSecurity.sellPrice:
            fields.append("sellPrice")
            values.append(newTargetSecurity.sellPrice)

        if len(fields) > 0:
            updated = self.securitiesInter.update_security(existingSecurity.id, fields, values)
        
        return updated

    def _remove_missing_securities(self, targetSecurities):
        """
        Receives: dictionary of targetSecurity, one for each security in new excel file.
        Returns: True if succeeds, False otherwise.
        If there are any securities in the currently loaded securities dictionary, that 
        don't exist in the provided new list, then we no longer want to track them. Thus,
        delete them from the database - securities and history tables.
        """
        for key in self.securitiesDict:
            tmpSecurity = self.securitiesDict[key]
            #print(f"_remove_missing_securities looking at security {tmpSecurity}")
            if not (key in targetSecurities):
                self._delete_security(tmpSecurity)
                print(f"_remove_missing_securities removed {key}")
        return True


    def _are_all_downloaded(self, targetSecurities):
        """
        Receives: Dictionary of security, one for each security in securities table.
        Returns: True if all securities have full histories downloaded, false otherwise.
        """
        allDownloaded = True
        for tmpSec in self.securitiesDict.values():
            if not (tmpSec.fullHistoryDownloaded):
                allDownloaded = False
                break

        return allDownloaded

    def _delete_security(self, security):
        """
        Remove given security from securities and history tables.
        """
        myId = security.id
        numDeleted = self.historyInter.delete_security(myId)
        print(f"_delete_security deleted {numDeleted} history records for {security.symbol}")
        deleteResult = self.securitiesInter.delete_security(myId)
        print(f"_delete_security result for deleting security was {deleteResult}")

    def _is_weekly_price_update_due(self):
        """
        Do we need to run weekly price update today?
        This method reads last weekly price date from db, then calls logic to check, to
        simplify testing.
        """
        lastWeekly = self.utilsInter.get_last_weekly_update_date()
        return self._checkWeeklyDate(date.today(), lastWeekly)

    def _get_weekly_price_date(self, currentDay):
        """
        Calculate date to store with weekly closing price - the Friday of the week.
        If today is Friday, then today, otherwise the most recent Friday. If dow = 4,
        return today. If 5 or 6, return today - (dow - 4). If 0-3, return today - (dow + 3).
        """
        lastFriday = None
        dow = currentDay.weekday()
        print(f"_get_weekly_price_date, currentDay={currentDay}, dow={dow}")

        if dow == 4:
            lastFriday = currentDay
            print(f"_get_weekly_price_date, friday")
        elif dow > 4:
            td = timedelta(dow - 4)
            lastFriday = currentDay - td
            print(f"_get_weekly_price_date, after friday, td={td}")
        else:
            td = timedelta(dow + 3)
            lastFriday = currentDay - td
            print(f"_get_weekly_price_date, before friday, td={td}")

        return lastFriday

    def _checkWeeklyDate(self, currentDate, lastWeeklyDate):
        """
        Want to run weekly price update every Friday, or the first following day, 
        if it didn't run on the previous Friday.
        """
        doWeekly = False
        if lastWeeklyDate is None:
            if currentDate.weekday() == 4:
                doWeekly = True
        else:
            if currentDate.weekday() == 4 and lastWeeklyDate < currentDate:
                doWeekly = True
                print("Today is Friday, so yes.")
            elif (currentDate - lastWeeklyDate).days > 7:
                doWeekly = True
                print("More than 7 days ago, so yes.")
            
        return doWeekly

    def _isPriceGroomingDue(self):
        """
        Do we need to run grooming today?
        This method reads last grooming date from db, then calls logic to check, to
        simplify testing.
        """
        lastGrooming = self.utilsInter.get_last_groom_date()
        return self._checkGroomingDate(date.today(), lastGrooming)

    def _checkGroomingDate(self, currentDate, lastGroomDate):
        """
        Want to remove older daily and weekly prices once a month. Am running grooming by
        by default on 5th of month, but, since this lambda doesn't run on weekends, am also
        running if it has been more than one month since it last ran. (Think that if just
        ran it if over a month since last run, given that lambda only runs on weekdays, day
        that this runs would slowly advance, increasing the amount of data that is stored.)
        Finally, if lastGroomDate is null, we've never run grooming, so this is probably
        a goot time to start.
        """
        doGrooming = False
        if lastGroomDate is None:
            doGrooming = True
        elif currentDate.day == 5 and lastGroomDate != currentDate:
            doGrooming = True
            print("Today is the 5th, so yes.")
        elif (currentDate - lastGroomDate).days > 31:
            doGrooming = True
            print("More than 31 days ago, so yes.")
            
        return doGrooming

    def _groomPrices(self):
        """
        Delete daily and weekly closing prices older than given thresholds.
        """
        daysToKeep = self.mySettings.daily_price_days_to_keep
        self._groomPricesForTable(self.mySettings.db_daily_table_name, daysToKeep)

        weeksToKeep = self.mySettings.weekly_price_weeks_to_keep
        self._groomPricesForTable(self.mySettings.db_weekly_table_name, weeksToKeep * 7)

    def _groomPricesForTable(self, tableName, daysToKeep):
        """
        Delete prices older than given threshold.
        """
        daysThreshold = date.today() - timedelta(daysToKeep)
        numDeleted = self.historyInter.remove_old_prices(tableName, daysThreshold)
        print(f"Removed {numDeleted} records from table {tableName}.")
