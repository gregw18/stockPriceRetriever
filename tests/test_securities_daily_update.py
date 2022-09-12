"""
File to test daily update parts of the Securities class.
V0.01, December 11, 2022, GAW
"""

from datetime import date, timedelta
from decimal import Decimal
import pytest
from unittest.mock import Mock, patch, call

from . import addSrcToPath
from . import helperMethods

import dbAccess
import securities
import securitiesInterface
from security import Security
import settings
import utilsInterface
from yahooInterface import retrieve_daily_data

mySettings = settings.Settings.instance()
helperMethods.adjust_settings_for_tests(mySettings)

@pytest.mark.database
class TestSecurities():
    def setup(self):
        self.securitiesDbName = mySettings.db_securities_table_name
        self.dailyDbName = mySettings.db_daily_table_name
        self.weeklyDbName = mySettings.db_weekly_table_name
        self.adminDbName = mySettings.db_admin_table_name
        self.securitiesFields = ("id", "name", "symbol", "fullHistoryDownloaded",
                                    "buyPrice", "sellPrice")

    @pytest.fixture()
    def getDict(self):
        # Some standard securities for testing
        oldDay = date(1999, 12, 31)
        secsDict = {}
        newsec = Security()
        newsec.pop("Apple", "AAPL", 123.45, 543.21, 200.33)
        newsec.fullHistoryDownloaded = True
        newsec.currentPriceDate = oldDay
        secsDict["AAPL"] = newsec

        msftsec = Security()
        msftsec.pop("Microsoft", "MSFT", 123.45, 543.21, 200.33)
        msftsec.fullHistoryDownloaded = True
        msftsec.currentPriceDate = oldDay
        secsDict["MSFT"] = msftsec

        googlsec = Security()
        googlsec.pop("Alphabet", "GOOGL", 123.45, 543.21, 200.33)
        googlsec.fullHistoryDownloaded = True
        googlsec.currentPriceDate = oldDay
        secsDict["GOOGL"] = googlsec

        return secsDict

    @pytest.fixture(scope='class')
    def getSecurities(self):
        return securities.Securities()

    @pytest.fixture(scope='class')
    def getSecuritiesInter(self):
        return securitiesInterface.SecuritiesInterface()

    @pytest.fixture(scope='class')
    def getUtils(self):
        print("Running getUtils")
        return utilsInterface.UtilsInterface()

    """
    Testing _get_weekly_price_date:
        Every day of week, Sunday to Saturday.
        Across months.
        Across years.
    """
    testdata = [
        (date(2023, 1, 1), date(2022, 12, 30)), # Sunday in 2023 to Friday in previous year.
        (date(2022, 11, 7), date(2022, 11, 4)), # Monday
        (date(2022, 10, 4), date(2022, 9, 30)), # Tuesday in October to Friday in September.
        (date(2022, 10, 12), date(2022, 10, 7)), # Wednesday
        (date(2022, 11, 3), date(2022, 10, 28)), # Thursday in November to Friday in October.
        (date(2022, 12, 9), date(2022, 12, 9)), # Friday
        (date(2022, 11, 19), date(2022, 11, 18))# Saturday
    ]

    @pytest.mark.parametrize("current,expected", testdata)
    @pytest.mark.unit
    def test_get_weekly_price_date_various(self, getSecurities, current, expected):
        """
        If today is monday, last Friday should be 3 days ago.
        """
        lastFriday = getSecurities._get_weekly_price_date(current)
        
        assert lastFriday == expected

    """
    Testing _get_symbols_needing_price_update
        first only
        last only
        all
        none
    """
    day0 = date.today()
    prevDay = day0 - timedelta(1)
    testdata = [
        (prevDay, day0, day0, ("AAPL",)),   # First requires updating.
        (day0, day0, prevDay, ("GOOGL",)),  # Last requires updating.
        (prevDay, prevDay, prevDay, ("AAPL", "GOOGL", "MSFT")),  # All require updating.
        (day0, day0, day0, ())              # None require updating.
    ]

    @pytest.mark.unit
    @pytest.mark.parametrize("dateA,dateM,dateG,expected", testdata)
    def test_get_symbols_needing_price_update(self, getSecurities, getDict,
                                            dateA, dateM, dateG, expected):
        # First security needs update.
        secsDict = getDict
        today = date.today()
        secsDict["AAPL"].currentPriceDate = dateA
        secsDict["MSFT"].currentPriceDate = dateM
        secsDict["GOOGL"].currentPriceDate = dateG
        getSecurities.securitiesDict = secsDict

        symbols = getSecurities._get_symbols_needing_price_update(today)

        for tmpSymbol in expected:
            assert tmpSymbol in symbols
        assert len(symbols) == len(expected)

    """
    Testing daily update. 
        Want to verify that correct parts fire on correct days - i.e. weekly, grooming, 
        full downloads. Also need to verify that correct prices for just securities needing
        updates end up in the correct places in tables.
        Does grooming run. Put some old prices in history tables, run, verify deleted.
        Does weekly update run. Run with a date of Friday, verify records added to weekly history.
        Does full downloads. Mark a security as not downloaded, run, verify records in history.
        Prices. Clear databases. Set up list of securities. Run download. For each security, verify
        that either saved price matches manually retrieved price or price was correctly 
        not downloaded.
    """

    @pytest.mark.integration
    def test_only_download_necessary_plus_full(self, getUtils, getSecurities, 
                                                getSecuritiesInter, getDict):
        """
        Verify that downloads daily prices for expected securities and weekly prices
        for one.
        """
        secsDict = getDict
        getSecurities.securitiesDict = secsDict

        getUtils.connect()

        # Set dates to determine which should be downloaded.
        currentDate = self._get_latest_weekday()
        print(f"1 currentDate = {currentDate}")
        secsDict["AAPL"].currentPriceDate = currentDate
        secsDict["MSFT"].currentPriceDate = currentDate - timedelta(1)
        secsDict["GOOGL"].currentPriceDate = currentDate - timedelta(1)
        self._save_to_securities(getSecuritiesInter, secsDict)

        # Run daily download routine.
        print(f"Finished saving data, calling do_daily")
        numUpdated = getSecurities.do_daily_price_update(currentDate)
        print(f"Finished do_daily, starting checks, numUpdated={numUpdated}.")
        print(f"2 currentDate = {currentDate}")

        # do_daily_price_update disconnects from db, so reconnect here.
        getUtils.connect()

        # Verify that values in securities table are correct.
        prices = self._retrieve_saved_data(("MSFT", "GOOGL"), secsDict, currentDate)
        print(f"3 currentDate = {currentDate}")

        # Confirm that didn't download any data for security that was already downloaded.
        self._confirm_no_saved_data_for_security(secsDict["AAPL"])

        self._wipe_tables(secsDict)
        getUtils.disconnect()

        print(f"4 currentDate = {currentDate}")
        self._compare_saved_data(prices, currentDate)

        assert numUpdated == 2

    @pytest.mark.unit
    def test_dont_update_weekly_date(self, getUtils, getSecurities, 
                                    getSecuritiesInter, getDict):
        """
        Verify that when call do_daily_price_update, lastWeeklyPriceUpdate field in 
        admin table isn't updated, when don't need to do weekly price update.
        Set field to known value, which shouldn't require update.
        Call method, mocking as much as possible.
        Verify that field value didn't change.
        """
        getUtils.connect()

        secsDict = getDict
        currentDate = self._get_latest_weekday()
        print(f"1 currentDate = {currentDate}")
        secsDict["AAPL"].currentPriceDate = currentDate
        secsDict["MSFT"].currentPriceDate = currentDate - timedelta(1)
        secsDict["GOOGL"].currentPriceDate = currentDate - timedelta(1)
        self._save_to_securities(getSecuritiesInter, secsDict)

        today = date.today()
        fields = ("lastWeeklyPriceUpdate",)
        values = (today + timedelta(1),)
        query = "1=1"
        dbAccess.update_data(self.adminDbName, fields, values, query)

        with patch('utilsInterface.UtilsInterface.set_last_weekly_update_date', 
                    return_value=Mock()) as mock_update_weekly:
            mock_update_weekly.return_value = None
            numUpdated = getSecurities.do_daily_price_update(today)

            self._wipe_tables(secsDict)
            getUtils.disconnect()

            mock_update_weekly.assert_not_called()

    @pytest.mark.integration
    def test_reset_daily_prices(self, getUtils, getSecurities, getDict, getSecuritiesInter):
        """ 
        Test that tables are in expected condition after doing reset. I.e. currentPriceDate
         in securities is yesterday, there are no records in daily/weekly price history
        tables with today's date and lastWeeklyUpdateDate in admin is one week ago.
        """
        # Make it look like daily price update just ran.
        getUtils.connect()
        secsDict = getDict
        secsDict["AAPL"].currentPriceDate = date.today()
        secsDict["MSFT"].currentPriceDate = date.today()
        secsDict["GOOGL"].currentPriceDate = date.today()
        self._save_to_securities(getSecuritiesInter, secsDict)

        fieldNames = ("securityId", "priceDate", "price")
        fieldVals = ( 
                        (secsDict["AAPL"].id, date.today(), 132.44),
                        (secsDict["MSFT"].id, date.today(), 432.33)
                    )
        dbAccess.insert_data(self.dailyDbName, fieldNames, fieldVals)
        dbAccess.insert_data(self.weeklyDbName, fieldNames, fieldVals)

        dbAccess.update_data(self.adminDbName, ("lastWeeklyPriceUpdate",), (date.today(),), "1=1")

        # Run the reset.
        getSecurities.reset_daily_prices()

        # Get results.
        params = (date.today(),)
        query = "currentPriceDate = %s"
        matchingSecurities = dbAccess.select_data(self.securitiesDbName, ("id",), query, params)
        query = "priceDate = %s"
        matchingDailyPrices = dbAccess.select_data(self.dailyDbName, ("id",), query, params)
        matchingWeeklyPrices = dbAccess.select_data(self.weeklyDbName, ("id",), query, params)
        lastWeekly = getUtils.get_last_weekly_update_date()

        self._wipe_tables(secsDict)
        getUtils.disconnect()

        assert len(matchingSecurities) == 0
        assert len(matchingDailyPrices) == 0
        assert len(matchingWeeklyPrices) == 0
        assert lastWeekly == date.today() - timedelta(7)
        
    def _approx_dec(self, val):
        """
        Return a value that can be compared to a decimal.
        """
        return pytest.approx(Decimal(val), Decimal(0.001))

    def _retrieve_saved_data(self, symbols, secsDict, currentDate):
        """
        Retrieve and save price data for requested symbols.
        Returns list, containing dictionary for each symbol. Dictionary
        consists of webPrices, securitiesPrices and dailyPrices, retrieved
        from the web, the securities table and the daily history tables,
        respectively.
        """
        prices = []
        for symbol in symbols:
            webPrices = retrieve_daily_data(symbol, mySettings)

            fields = ("currentPrice", "currentPriceDate", "previousClosePrice",
                        "52WeekHighPrice", "52WeekLowPrice")
            query = "symbol = %s"
            securitiesPrices = dbAccess.select_data(self.securitiesDbName, fields, query, (symbol,))

            fields = ("price",)
            query = "securityId = %s AND priceDate = %s"
            params = (secsDict[symbol].id, currentDate)
            dailyPrices = dbAccess.select_data(self.dailyDbName, fields, query, params)

            prices.append({"webPrices": webPrices,
                            "securitiesPrices": securitiesPrices,
                            "dailyPrices": dailyPrices})

        return prices

    def _compare_saved_data(self, prices, currentDate):
        """
        Do assertions on data previously retrieved.
        Have retrieval and assertions separated so that can manually clean up
        database in between. If do assertions first, if one fails, program stops,
        cleanup never runs. (There has to be a better way, but I haven't found it yet.)
        """
        for priceDict in prices:
            securitiesPrices = priceDict["securitiesPrices"]
            webPrices = priceDict["webPrices"]
            dailyPrices = priceDict["dailyPrices"]
            assert securitiesPrices[0]["currentPrice"] == self._approx_dec(webPrices.currentPrice)
            assert securitiesPrices[0]["currentPriceDate"] == currentDate
            assert securitiesPrices[0]["previousClosePrice"] == self._approx_dec(webPrices.lastClosePrice)
            assert securitiesPrices[0]["52WeekHighPrice"] == self._approx_dec(webPrices.high52Week)
            assert securitiesPrices[0]["52WeekLowPrice"] == self._approx_dec(webPrices.low52Week)

            assert dailyPrices[0]["price"] == self._approx_dec(webPrices.currentPrice)

    def compare_downloaded_saved_prices(self, tmpSec, table, frequency, today, startDate):
        """
        Retrieve data for given security/frequency from web. Compare
        to saved data.
        """
        yahooData = yahooInterface.retrieve_historical_prices(tmpSec.symbol, 
                                    startDate, today, frequency)
        savedData = self.retrieve_saved_prices(table, tmpSec.id)

        for i in range(len(yahooData)):
            assert yahooData[i][0] == savedData[i]["priceDate"]
            assert Decimal(yahooData[i][1]) == pytest.approx(savedData[i]["price"], Decimal(0.001))

    def _confirm_no_saved_data_for_security(self, tmpSec):
        # Confirm that didn't download any data for given security.
        savedDailies = self._retrieve_saved_prices(self.dailyDbName, tmpSec.id)
        assert len(savedDailies) == 0
        savedWeeklies = self._retrieve_saved_prices(self.weeklyDbName, tmpSec.id)
        assert len(savedWeeklies) == 0

    def _retrieve_saved_prices(self, table, secId):
        historyFields = ("priceDate", "price")
        query = "securityId = %s"
        return dbAccess.select_data(table, historyFields, query, secId)

    def _wipe_tables(self, myDict):
        """
        Delete all records from securities, daily and weekly price history tables, for securities
        that are in the provided dictionary of securities.
        """
        historyQuery = "securityId = %s"
        securityQuery = "id=%s"
        for tmpSecurity in myDict.values():
            dbAccess.delete_data(self.securitiesDbName, securityQuery, tmpSecurity.id)
            dbAccess.delete_data(self.dailyDbName, historyQuery, tmpSecurity.id)
            dbAccess.delete_data(self.weeklyDbName, historyQuery, tmpSecurity.id)

    def _save_to_securities(self, getSecurities, secsDict):
        """
        Save current securities to securities table.
        """
        for tmpSecurity in secsDict.values():
            fieldNames=["name", "symbol", "currentPriceDate", "buyPrice",
                        "sellPrice", "fullHistoryDownloaded"]
            fieldValues = [None] * len(fieldNames)
            fieldValues[0] = tmpSecurity.name
            fieldValues[1] = tmpSecurity.symbol
            fieldValues[2] = tmpSecurity.currentPriceDate
            fieldValues[3] = tmpSecurity.buyPrice
            fieldValues[4] = tmpSecurity.sellPrice
            fieldValues[5] = tmpSecurity.fullHistoryDownloaded
            
            # Need to nest the list so that connector recognizes that adding one record
            # with five values, rather than five records with one value each.
            nestedValues = [fieldValues,]
            dbAccess.insert_data(self.securitiesDbName, fieldNames, nestedValues)
            
            # Retrieve id for record just added, store in security.
            query = "symbol = %s"
            params = (tmpSecurity.symbol,)
            newId = dbAccess.select_data(self.securitiesDbName, ("id",), query, params)
            tmpSecurity.id = newId[0]["id"]

    def _get_latest_weekday(self):
        """
        Return date of latest weekday - either today or earlier. Used to avoid
        running tests with a current date of a weekend.
        """
        latest = date.today()
        dow = latest.isoweekday()
        if dow > 5:
            latest = latest - timedelta(dow-5)
        print(f"_get_latest_weekday is returning {latest}")

        return latest

