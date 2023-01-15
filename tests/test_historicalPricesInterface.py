"""
File to unit test historicalPricesInterface - mocks dbAccess.
V0.01, November 24, 2022, GAW
"""

from datetime import date, timedelta, datetime
from decimal import Decimal
import math
import random

from . import addSrcToPath
from . import helperMethods

import unittest
import pytest

import dbAccess
from historicalPricesInterface import HistoricalPricesInterface
import settings
from utilsInterface import UtilsInterface

"""
To Test
save_daily_price
    Correctly saves a price
save_weekly_price
    Grabs correct price when called on a Friday
    Grabs correct price when called on some other day.
save_daily_historical_prices
    Correctly saves multiple prices - up to 90
save_weekly_historical_prices
    Correctly saves multiple prices - up to 250
get_historical_prices
    Emits correct query, returns expected values
remove_old_prices
    Emits expected queries
delete_security
    Emits correct queries
"""


@pytest.mark.integration
@pytest.mark.database
class TestHistoricalPricesInterface(unittest.TestCase):
    def setUp(self):
        self.mysettings = settings.Settings.instance()
        helperMethods.adjust_settings_for_tests(self.mysettings)
        self.dailyPricesTable = self.mysettings.db_daily_table_name
        self.weeklyPricesTable = self.mysettings.db_weekly_table_name
        self.baseSecurityId = 3412

    def test_save_daily_price_for_security(self):
        """
        Integration test. Confirm that expected values end up in table.
        Add record for given securityId/date combo, read back in, confirm expected values,
        remove that record.
        """
        expectedPrice = Decimal(123.45)
        expectedDate = date(2022, 11, 20)
        secId = self.baseSecurityId

        utilsInterface = UtilsInterface()
        utilsInterface.connect()
        historyInterface = HistoricalPricesInterface()

        historyInterface.save_daily_price_for_security(secId, expectedPrice, expectedDate)

        query = f"securityId=%s AND priceDate=%s"
        records = dbAccess.select_data(self.dailyPricesTable,
                                       ["price"],
                                       query,
                                       (secId, expectedDate))

        self.assertAlmostEqual(records[0]["price"], expectedPrice)

        numDeleted = dbAccess.delete_data(self.dailyPricesTable, query, (secId, expectedDate))
        assert numDeleted == 1

        utilsInterface.disconnect()

    def test_save_daily_historical_prices(self):
        """
        Save fixed number of prices, verify that correct number of records are
        saved, verify some values.
        """
        basePrice = 43.22
        numPrices = 20
        secId = self.baseSecurityId + 1

        self.exercise_save_historical_prices(self.mysettings.db_daily_history_code,
                                             secId,
                                             basePrice,
                                             numPrices)

    def test_save_weekly_price_for_security(self):
        """
        Testing the special update that copies price for given date from daily table
        to the weekly table.
        """
        expectedPrice = Decimal(43.65)
        expectedDate = date(2022, 6, 13)
        secId = self.baseSecurityId + 2

        utilsInterface = UtilsInterface()
        utilsInterface.connect()
        historyInterface = HistoricalPricesInterface()

        # Save the daily price that want to use as basis for the weekly price, then
        # call the method to update the weekly price.
        historyInterface.save_daily_price_for_security(secId, expectedPrice, expectedDate)
        historyInterface.save_weekly_price_for_security(secId, expectedDate)

        # Retrieve the price from the weekly table, verify that matches original price.
        query = f"securityId=%s AND priceDate=%s"
        params = (secId, expectedDate)
        records = dbAccess.select_data(self.weeklyPricesTable, ["price"], query, params)
        numDailyDeleted = dbAccess.delete_data(self.dailyPricesTable, query, params)
        numWeeklyDeleted = dbAccess.delete_data(self.weeklyPricesTable, query, params)

        utilsInterface.disconnect()

        self.assertAlmostEqual(records[0]["price"], expectedPrice)
        assert numDailyDeleted == 1
        assert numWeeklyDeleted == 1

    """
    Testing removing old prices.
    first, need to verify whether want to delete for date < thresh or > thresh.
    then, verify that it deletes older stuff, leaves newer stuff.
    need date math to work across month ends, year ends.
    """
    def test_remove_old_prices_within_month(self):
        """
        Add some prices across date range, then see if can delete older ones.
        """
        daysToKeep = 11
        securityId = self.baseSecurityId + 4
        baseDate = date(2022, 11, 29)
        numPrices = 20
        timePeriod = self.mysettings.db_daily_history_code

        self.exercise_remove_old_prices(timePeriod, numPrices, daysToKeep, securityId, baseDate)

    def test_remove_old_prices_across_month(self):
        """
        Add some prices across date range, which happens to cross two month ends,
        then verify that correct records are deleted.
        """
        daysToKeep = 10
        securityId = self.baseSecurityId + 5
        baseDate = date(2022, 11, 9)
        numPrices = 50
        timePeriod = self.mysettings.db_daily_history_code

        self.exercise_remove_old_prices(timePeriod, numPrices, daysToKeep, securityId, baseDate)

    def test_remove_old_prices_across_year(self):
        """
        Add some prices across date range, which happens to cross a year end,
        then verify that correct records are deleted. Note that using Friday for base
        date as that is day weekly prices should be saved for.
        """
        daysToKeep = 30
        securityId = self.baseSecurityId + 6
        baseDate = date(2022, 2, 11)
        numPrices = 20
        timePeriod = self.mysettings.db_weekly_history_code

        self.exercise_remove_old_prices(timePeriod, numPrices, daysToKeep, securityId, baseDate)

    def test_delete_security_have_records(self):
        """
        Add some prices for a security, call delete, confirm none left
        """
        securityId = self.baseSecurityId + 7
        baseDate = datetime.now().date()
        basePrice = 200
        numPrices = 30
        timePeriod = self.mysettings.db_daily_history_code
        dailyPairs = self.generate_date_price_pairs(baseDate,
                                                    basePrice,
                                                    numPrices,
                                                    timePeriod)

        timePeriod = self.mysettings.db_weekly_history_code
        weeklyPairs = self.generate_date_price_pairs(baseDate,
                                                     basePrice,
                                                     numPrices,
                                                     timePeriod)

        utilsInterface = UtilsInterface()
        utilsInterface.connect()
        historyInterface = HistoricalPricesInterface()
        result = historyInterface.save_daily_historical_prices(securityId, dailyPairs)
        result = historyInterface.save_weekly_historical_prices(securityId, weeklyPairs)

        historyInterface.delete_security(securityId)

        query = "securityId = %s"
        params = (securityId,)
        dailyRecords = dbAccess.select_data(self.dailyPricesTable, ("id",), query, params)
        weeklyRecords = dbAccess.select_data(self.weeklyPricesTable, ("id",), query, params)

        assert len(dailyRecords) == 0
        assert len(weeklyRecords) == 0

    def test_delete_security_no_records(self):
        """
        Call delete for a security that doesn't exist, confirm no errors.
        """
        securityId = self.baseSecurityId + 2000

        utilsInterface = UtilsInterface()
        utilsInterface.connect()
        historyInterface = HistoricalPricesInterface()

        historyInterface.delete_security(securityId)

        query = "securityId = %s"
        params = (securityId,)
        dailyRecords = dbAccess.select_data(self.dailyPricesTable, ("id",), query, params)
        weeklyRecords = dbAccess.select_data(self.weeklyPricesTable, ("id",), query, params)

        assert len(dailyRecords) == 0
        assert len(weeklyRecords) == 0

    def test_num_fridays(self):
        """
        Testing a test - Is the calculation for number of fridays in a date
        range correct? Going through a full week.
        """
        numDays = 20
        baseDate = date(2022, 2, 4)
        assert self.get_number_fridays(baseDate, numDays) == 3

        baseDate = date(2022, 2, 3)
        assert self.get_number_fridays(baseDate, numDays) == 2

        baseDate = date(2022, 2, 2)
        assert self.get_number_fridays(baseDate, numDays) == 3

        baseDate = date(2022, 2, 1)
        assert self.get_number_fridays(baseDate, numDays) == 3

        baseDate = date(2022, 1, 31)
        assert self.get_number_fridays(baseDate, numDays) == 3

        baseDate = date(2022, 1, 30)
        assert self.get_number_fridays(baseDate, numDays) == 3

        baseDate = date(2022, 1, 29)
        assert self.get_number_fridays(baseDate, numDays) == 3

    def generate_date_price_pairs(self, startDate, startPrice, numPairs, timePeriod):
        """
        Generate requested sequence of date/price pairs.
        """
        newDate = startDate
        myDelta = None
        if timePeriod == self.mysettings.db_daily_history_code:
            myDelta = timedelta(days=1)
        elif timePeriod == self.mysettings.db_weekly_history_code:
            myDelta = timedelta(days=7)
        else:
            print(f"Error: (generate_date_price_pairs) unexpected time history code: {timePeriod}")

        # Add random number in 25% range around initial price to create prices.
        randRange = 0.25 * startPrice
        pairs = []
        for i in range(numPairs):
            priceDelta = random.uniform(-randRange, randRange)
            newPrice = round(Decimal(startPrice + priceDelta), 2)
            pairs.append((newDate, newPrice))
            newDate -= myDelta
        print(f"number of pairs is {len(pairs)}")

        return pairs

    def exercise_save_historical_prices(self,
                                        timePeriod,
                                        securityId,
                                        basePrice,
                                        numPrices):
        """
        Save fixed number of prices, verify that correct number of records are
        saved, verify some values.
        """
        baseDate = datetime.now().date()
        dataPairs = self.generate_date_price_pairs(baseDate,
                                                   basePrice,
                                                   numPrices,
                                                   timePeriod)

        utilsInterface = UtilsInterface()
        utilsInterface.connect()
        historyInterface = HistoricalPricesInterface()
        result = False
        tableName = self.dailyPricesTable
        if timePeriod == self.mysettings.db_daily_history_code:
            result = historyInterface.save_daily_historical_prices(securityId, dataPairs)
        elif timePeriod == self.mysettings.db_weekly_history_code:
            result = historyInterface.save_weekly_historical_prices(securityId, dataPairs)
            tableName = self.weeklyPricesTable
        else:
            print(f"Error: (exercise_save_historical_prices) unexpected time history code: ",
                  "{timePeriod}")

        assert result

        maxAge = numPrices
        if timePeriod == self.mysettings.db_weekly_history_code:
            # If doing weekly prices, want up to number of prices * 7 days per week as maximum age.
            maxAge = numPrices * 7

        # Retrieve and check saved records.
        savedRecords = historyInterface.get_historical_prices(securityId, tableName, maxAge)

        # Remove all records for this security before asserting, so that not left lying around.
        query = "securityId=%s"
        dbAccess.delete_data(tableName, query, (securityId,))
        undeleted = dbAccess.select_data(tableName, ("id",), "1=1")

        assert len(savedRecords) == numPrices
        self.assertAlmostEqual(savedRecords[0]["price"], dataPairs[0][1])
        self.assertAlmostEqual(savedRecords[numPrices - 1]["price"],
                               dataPairs[numPrices - 1][1])
        assert len(undeleted) == 0

    def exercise_remove_old_prices(self, timePeriod, numPrices, daysToKeep,
                                   securityId, baseDate):
        """
        Add some prices across date range, use remove_old_prices to remove older prices,
        then verify that correct records were deleted.
        """

        # Generate and save the prices.
        tableName = self.dailyPricesTable
        if timePeriod == self.mysettings.db_weekly_history_code:
            tableName = self.weeklyPricesTable
        else:
            print(f"Error: (exercise_remove_old_prices) unexpected time"
                  f" history code: {timePeriod}")
        basePrice = 100
        dataPairs = self.generate_date_price_pairs(baseDate,
                                                   basePrice,
                                                   numPrices,
                                                   timePeriod)

        utilsInterface = UtilsInterface()
        utilsInterface.connect()
        historyInterface = HistoricalPricesInterface()
        result = False

        if timePeriod == self.mysettings.db_daily_history_code:
            result = historyInterface.save_daily_historical_prices(securityId, dataPairs)
        elif timePeriod == self.mysettings.db_weekly_history_code:
            result = historyInterface.save_weekly_historical_prices(securityId, dataPairs)
        else:
            print(f"Error: (exercise_save_historical_prices) unexpected time history code: ",
                  "{timePeriod}")

        assert result

        # Remove older prices.
        timeDelta = timedelta(daysToKeep)
        dateThresh = baseDate - timeDelta

        numDeleted = historyInterface.remove_old_prices(tableName, dateThresh)

        # Retrieve and check saved records.
        query = "securityId = %s"
        params = (securityId,)
        remainingRecords = dbAccess.select_data(tableName, ("priceDate",), query, params)

        # Remove all records for this security before asserting, so that not left lying around.
        query = "securityId=%s"
        dbAccess.delete_data(tableName, query, (securityId,))

        # Find oldest date in remaining records, should be newer than threshold.
        minDate = datetime.now().date()
        for rec in remainingRecords:
            if rec["priceDate"] < minDate:
                minDate = rec["priceDate"]
        print(f"Minimum remaining date is {minDate}")
        assert minDate >= dateThresh
        expectedRecords = self.get_expected_remaining_records(baseDate, daysToKeep, timePeriod)
        assert len(remainingRecords) == expectedRecords

    def get_expected_remaining_records(self, baseDate, daysToKeep, timePeriod):
        """
        Calculate how many prices should be left, given how many days of data we want to keep
        and whether we are storing daily or weekly data.
        """
        expectedRemaining = 0
        if timePeriod == self.mysettings.db_daily_history_code:
            expectedRemaining = daysToKeep
        elif timePeriod == self.mysettings.db_weekly_history_code:
            expectedRemaining = self.get_number_fridays(baseDate, daysToKeep)
        else:
            print(f"Error: (get_expected_remaining_records) unexpected time history code: ",
                  "{timePeriod}")

        return expectedRemaining

    def get_number_fridays(self, baseDate, daysToKeep):
        """
        How to calculate how many Fridays are there between given date and N days prior to that
        date? If it is a Friday, divide number of days by 7, round up to nearest int.
        If not Friday, subtract number of days to get to Friday, then divide by 7 and roundup
        to nearest int.
        i.e. 20 days history to keep. If base day is
        Friday, Feb 4, back to Jan 15, 3 Fridays. roundup(20/7) = 3
        Thursday, Feb 3, Jan 14, 2 Fridays. roundup((20-6)/7) = 2
        Sunday, Jan 30, Jan 10, 3 Fridays, roundup((20-2)/7) = 3
        Saturday, Jan 29, Jan 9, 3 Fridays, roundup((20-1))/7) = 3
        Amount to subtract
        Day, weekday, # to subtract
        Monday, 1, 3
        Tuesday, 2, 4
        Wednesday, 3, 5
        Thursday, 4, 6
        Friday, 5, 0
        Saturday, 6, 1
        Sunday, 0, 2
        """
        offsets = [3, 4, 5, 6, 0, 1, 2]
        days = daysToKeep - offsets[baseDate.weekday()]
        print(f"baseDate={baseDate}, index={baseDate.weekday()}, days={days}")
        numWeeks = math.ceil(days/7)

        return numWeeks
