"""
File to test Securities class
V0.01, November 30, 2022, GAW
"""

import datetime
from pandas import DataFrame
import pytest
from unittest.mock import Mock, patch, call

from . import addSrcToPath
from . import helperMethods

import dbAccess
import securities
import securitiesInterface
from security import Security
import settings
import targetSecurity

mySettings = settings.Settings.instance()
helperMethods.adjust_settings_for_tests(mySettings)

@pytest.mark.unit
@pytest.mark.database
class TestSecurities():
    def setup(self):
        self.dailyDbName = mySettings.db_daily_table_name
        self.weeklyDbName = mySettings.db_weekly_table_name
        self.securitiesTable = mySettings.db_securities_table_name
        self.securitiesFields = ("id", "name", "symbol", "fullHistoryDownloaded",
                                    "buyPrice", "sellPrice")

        # Some standard securities for testing
        self.secsDict = {}
        newsec = Security()
        newsec.pop("Apple", "AAPL", 123.45, 543.21, 200.33)
        self.secsDict["AAPL"] = newsec

        msftsec = Security()
        msftsec.pop("Microsoft", "MSFT", 123.45, 543.21, 200.33)
        self.secsDict["MSFT"] = msftsec

        googlsec = Security()
        googlsec.pop("Alphabet", "GOOGL", 123.45, 543.21, 200.33)
        self.secsDict["GOOGL"] = googlsec

    @pytest.fixture(scope='class')
    def getSecurities(self):
        return securities.Securities()

    @pytest.fixture(scope='class')
    def getSecuritiesInter(self):
        return securitiesInterface.SecuritiesInterface()

    """
    Grooming tests:
        5th of month.
        4th of month.
        5th of month but already ran.
        20 days since last ran
        31 days since last ran
        32 days since last ran.
    """
    def test_checkGroomDate_5th(self, getSecurities):
        """
        Today is the 5th, last ran yesterday. Still want to run, because it is 5th.
        """
        today = datetime.date(2022, 11, 5)
        lastGroomDate = datetime.date(2022, 11, 4)
        doGrooming = getSecurities._checkGroomingDate(today, lastGroomDate)
        assert doGrooming == True

    def test_checkGroomDate_4th(self, getSecurities):
        """
        Today is 4th, last ran four weeks ago. Shouldn't run.
        """
        today = datetime.date(2022, 11, 4)
        lastGroomDate = today - datetime.timedelta(28)
        doGrooming = getSecurities._checkGroomingDate(today, lastGroomDate)
        assert doGrooming == False

    def test_checkGroomDate_5th_alreadyRan(self, getSecurities):
        """
        Today is 5th, last ran today. Shouldn't run.
        """
        today = datetime.date(2022, 11, 5)
        lastGroomDate = today
        doGrooming = getSecurities._checkGroomingDate(today, lastGroomDate)
        assert doGrooming == False

    def test_checkGroomDate_20daysago(self, getSecurities):
        """
        Last ran 20 days ago. Shouldn't run.
        """
        today = datetime.date(2022, 11, 4)
        lastGroomDate = today - datetime.timedelta(20)
        doGrooming = getSecurities._checkGroomingDate(today, lastGroomDate)
        assert doGrooming == False

    def test_checkGroomDate_32daysago(self, getSecurities):
        """
        Last ran 32 days ago. Should run.
        """
        today = datetime.date(2022, 11, 4)
        lastGroomDate = today - datetime.timedelta(32)
        doGrooming = getSecurities._checkGroomingDate(today, lastGroomDate)
        assert doGrooming == True

    def test_checkGroomDate_41daysago(self, getSecurities):
        """
        Last ran 41 days ago. Should run.
        """
        today = datetime.date(2022, 11, 4)
        lastGroomDate = today - datetime.timedelta(41)
        doGrooming = getSecurities._checkGroomingDate(today, lastGroomDate)
        assert doGrooming == True

    def test_checkGroomDate_null(self, getSecurities):
        """
        Has never previously run. Should run.
        """
        today = datetime.date(2022, 11, 4)
        lastGroomDate = None
        doGrooming = getSecurities._checkGroomingDate(today, lastGroomDate)
        assert doGrooming == True

    """
    IsWeeklyDue tests
        Friday.
        Thursday.
        Saturday.
        Friday but already ran.
        Monday, 6 days since last ran.
        Monday, 7 days since last ran
        Monday, 8 days since last ran.

    """
    def test_checkWeeklyDate_Friday(self, getSecurities):
        """
        Friday, last run a week ago. Should run.
        """
        today = datetime.date(2022, 11, 25)
        lastWeeklyDate = today - datetime.timedelta(7)
        doWeekly = getSecurities._checkWeeklyDate(today, lastWeeklyDate)
        assert doWeekly == True

    def test_checkWeeklyDate_Thursday(self, getSecurities):
        """
        Thursday, last run a week ago. Shouldn't run.
        """
        today = datetime.date(2022, 11, 24)
        lastWeeklyDate = today - datetime.timedelta(7)
        doWeekly = getSecurities._checkWeeklyDate(today, lastWeeklyDate)
        assert doWeekly == False

    def test_checkWeeklyDate_Saturday(self, getSecurities):
        """
        Saturday, last run a week ago. Shouldn't run.
        """
        today = datetime.date(2022, 11, 26)
        lastWeeklyDate = today - datetime.timedelta(7)
        doWeekly = getSecurities._checkWeeklyDate(today, lastWeeklyDate)
        assert doWeekly == False

    def test_checkWeeklyDate_6DaysSince(self, getSecurities):
        """
        Monday, 6 days since last run. Shouldn't run.
        """
        today = datetime.date(2022, 11, 21)
        lastWeeklyDate = today - datetime.timedelta(6)
        doWeekly = getSecurities._checkWeeklyDate(today, lastWeeklyDate)
        assert doWeekly == False

    def test_checkWeeklyDate_7DaysSince(self, getSecurities):
        """
        Monday, 7 days since last run. Shouldn't run.
        """
        today = datetime.date(2022, 11, 21)
        lastWeeklyDate = today - datetime.timedelta(7)
        doWeekly = getSecurities._checkWeeklyDate(today, lastWeeklyDate)
        assert doWeekly == False

    def test_checkWeeklyDate_8DaysSince(self, getSecurities):
        """
        Monday, 8 days since last run. Should run.
        """
        today = datetime.date(2022, 11, 21)
        lastWeeklyDate = today - datetime.timedelta(8)
        doWeekly = getSecurities._checkWeeklyDate(today, lastWeeklyDate)
        assert doWeekly == True

    def test_checkWeeklyDate_Never(self, getSecurities):
        """
        Friday, never previously run. Should run.
        """
        today = datetime.date(2022, 11, 25)
        lastWeeklyDate = None
        doWeekly = getSecurities._checkWeeklyDate(today, lastWeeklyDate)
        assert doWeekly == True

    def test_get_symbols_currentPriceDate_None(self, getSecurities):
        """
        If have a security with none as the currentPriceDate, _get_symbols_needing_price_update
        should return it.
        All securities in local dict have empty currentPriceDate, so set one to today,
        so that it won't appear in the list.
        """
        nonesec = Security()
        nonesec.pop("Exxon", "XOM", 123.45, 543.21, 200.33)
        nonesec.currentPriceDate = None
        self.secsDict["XOM"] = nonesec
        self.secsDict["AAPL"].currentPriceDate = datetime.date.today()
        getSecurities.securitiesDict = self.secsDict
        
        needies = getSecurities._get_symbols_needing_price_update(datetime.date.today())

        assert len(needies) == len(self.secsDict) - 1
        assert "XOM" in needies
        assert not("AAPL" in needies)
    
    """
    Grooming tests. When call do_maintenance, want to verify contents of
    both calls to historyInterface.remove_old_prices.
    """
    def test_groom_prices(self, getSecurities):
        """
        Verify that when call _groomPrices, expected calls
        are made to historyInterface.
        """
        #dbAccess.connect()
        with patch('historicalPricesInterface.HistoricalPricesInterface.remove_old_prices', 
                    return_value=Mock()) as mock_remove:
            mock_remove.return_value = 5
            #with patch('historicalPricesInterface.HistoricalPricesInterface.remove_old_prices', 
            #            return_value=Mock()) as mock_remove:
            getSecurities._groomPrices()
            #dbAccess.disconnect()
        
            daysToKeep = mySettings.daily_price_days_to_keep
            weeksToKeep = mySettings.weekly_price_weeks_to_keep
            daysThreshold = datetime.date.today() - datetime.timedelta(daysToKeep)
            weeksThreshold = datetime.date.today() - datetime.timedelta(weeksToKeep * 7)
            
            calls = [call(self.dailyDbName, daysThreshold), call(self.weeklyDbName,weeksThreshold)]
            mock_remove.assert_has_calls(calls)

    """
    LoadNewList tests.
    These are integration tests - want to manually store securities in table at start,
    allow changes to be made, then verify what is in table when finished.
    """
    @pytest.mark.integration
    def test_loadNewList_remove_existing(self, getSecurities, getSecuritiesInter):
        """
        Provide new list that is missing a security that is in current list.
        Should result in in-memory list dropping that security.
        Put expected securities in table.
        Load into memory.
        Create dictionary of new TargetSecurity, key = symbol, with one of 
        existing not included.
        Call loadNewList.
        Verify that table has lost one security
        Verify that expected security is gone from in-memory.
        """
        # Clear out securities table.
        dbAccess.connect()
        dbAccess.delete_data(self.securitiesTable, "1=1")

        # Add securities to table, then load into memory.
        self._save_to_securities_table(getSecuritiesInter, 
                                        ["AAPL", "MSFT", "GOOGL"])
        getSecurities.load()

        # Create dictionary representing list of new securities.
        newSecs = self._create_targets_dict(["AAPL", "MSFT"])

        with patch('securities.Securities.retrieve_full_price_histories',
                        return_value=Mock()) as mock_retrieve:
            mock_retrieve.return_value = 3
            getSecurities.loadNewList(newSecs)

        dbRecs = dbAccess.select_data(self.securitiesTable, self.securitiesFields, "1=1")

        # Clear out securities and price history tables.
        numDeleted = dbAccess.delete_data(self.securitiesTable, "1=1")
        #self._wipe_history_tables(self.secsDict)
        dbAccess.disconnect()

        assert len(dbRecs) == 2
        inMemRecs = getSecurities.securitiesDict
        assert (not ("GOOGL" in inMemRecs))
        assert "AAPL" in inMemRecs
        assert "MSFT" in inMemRecs

    @pytest.mark.integration
    def test_loadNewList_add_Two(self, getSecurities, getSecuritiesInter):
        """
        Provide new list that contains two new securities not in current list.
        """
        # Clear out securities table.
        dbAccess.connect()
        dbAccess.delete_data(self.securitiesTable, "1=1")

        # Add securities to table, then load into memory -"current list".
        self._save_to_securities_table(getSecuritiesInter, 
                                        ["MSFT"])
        getSecurities.load()

        # Create dictionary representing list of new securities.
        newSecs = self._create_targets_dict(["AAPL", "MSFT", "GOOGL"])

        with patch('securities.Securities.retrieve_full_price_histories',
                        return_value=Mock()) as mock_retrieve:
            mock_retrieve.return_value = 3
            getSecurities.loadNewList(newSecs)

        dbRecs = dbAccess.select_data(self.securitiesTable, self.securitiesFields, "1=1")

        # Clear out securities table.
        numDeleted = dbAccess.delete_data(self.securitiesTable, "1=1")
        dbAccess.disconnect()

        assert len(dbRecs) == 3
        inMemRecs = getSecurities.securitiesDict
        assert "GOOGL" in inMemRecs
        assert "AAPL" in inMemRecs
        assert "MSFT" in inMemRecs

    @pytest.mark.integration
    def test_loadNewList_test_all(self, getSecurities, getSecuritiesInter):
        """
        Adding one security, removing one, modifying third.
        """
        # Clear out securities table.
        dbAccess.connect()
        dbAccess.delete_data(self.securitiesTable, "1=1")

        # Add securities to table, then load into memory -"current list".
        self._save_to_securities_table(getSecuritiesInter, 
                                        ["MSFT", "AAPL"])
        getSecurities.load()

        # Create dictionary representing list of new securities.
        newSecs = self._create_targets_dict(["AAPL", "GOOGL"])
        newSecs["AAPL"].name = "ORANGE"

        with patch('securities.Securities.retrieve_full_price_histories',
                        return_value=Mock()) as mock_retrieve:
            mock_retrieve.return_value = 3
            getSecurities.loadNewList(newSecs)

        dbRecs = dbAccess.select_data(self.securitiesTable, self.securitiesFields, "1=1")

        # Clear out securities table.
        numDeleted = dbAccess.delete_data(self.securitiesTable, "1=1")
        dbAccess.disconnect()

        assert len(dbRecs) == 2
        inMemRecs = getSecurities.securitiesDict
        assert "GOOGL" in inMemRecs
        assert "AAPL" in inMemRecs
        assert not ("MSFT" in inMemRecs)
        assert inMemRecs["AAPL"].name == "ORANGE"

    def _to_target_security(self, mySecurity):
        """
        Create new TargetSecurity from some fields in given security.
        """
        newTarget = targetSecurity.TargetSecurity()
        newTarget.name = mySecurity.name
        newTarget.symbol = mySecurity.symbol
        newTarget.buyPrice = mySecurity.buyPrice
        newTarget.sellPrice = mySecurity.sellPrice

        return newTarget

    def _save_to_securities_table(self, securitiesInter, secsList):
        """
        Save requested securities to securities table.
        """
        for mySec in secsList:
            securitiesInter.add_security(self.secsDict[mySec])

    def _create_targets_dict(self, symbolsList):
        """
        Create dictionary of TargetSecurity, containing requested symbols.
        """
        newDict = {}
        for symbol in symbolsList:
            tmpTarget = self._to_target_security(self.secsDict[symbol])
            newDict[symbol] = tmpTarget
        
        return newDict
