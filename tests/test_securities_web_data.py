"""
File to test retrieving the data required for web site, via the Securities class
V0.01, December 19, 2022, GAW
"""

from datetime import date, timedelta
from decimal import *
from pandas import DataFrame
import pytest
import random
from unittest.mock import Mock, patch, call

from . import addSrcToPath
from . import helperMethods

import securities
from security import Security
import settings
import sprEnums

mySettings = settings.Settings.instance()
helperMethods.adjust_settings_for_tests(mySettings)

@pytest.mark.unit
class TestSecuritiesWebData():
    def setup(self):
        print("Running setup")
        #self.mySettings = settings.Settings.instance()
        self.dailyDbName = mySettings.db_daily_table_name
        self.weeklyDbName = mySettings.db_weekly_table_name

        # Some standard securities for testing
        self.secsDict = {}
        applsec = Security()
        applsec.pop("Apple", "AAPL", 123.45, 543.21, 200.33)
        applsec.id = 3
        applsec.fullHistoryDownloaded = False
        self.secsDict["AAPL"] = applsec

        msftsec = Security()
        msftsec.pop("Microsoft", "MSFT", 123.45, 543.21, 200.33)
        msftsec.id = 4
        msftsec.fullHistoryDownloaded = True
        self.secsDict["MSFT"] = msftsec

        googlsec = Security()
        googlsec.pop("Alphabet", "GOOGL", 123.45, 543.21, 200.33)
        googlsec.id = 5
        googlsec.fullHistoryDownloaded = False
        self.secsDict["GOOGL"] = googlsec
        print("Setup complete")

    @pytest.fixture(scope='class')
    def getSecurities(self):
        return securities.Securities()

    def test_timePeriods_good_convert(self):
        """ 
        Verify that can convert a description to an enum name and corresponding value.
        """
        name = "3months"

        myEnum = sprEnums.get_timePeriod_from_text(name)

        assert myEnum == sprEnums.timePeriods.months3
        assert myEnum.value == 31 * 3

    def test_timePeriods_bad_name(self):
        """ 
        Verify that bad name returns zero value.
        """
        name = "Snoopy"

        myEnum = sprEnums.get_timePeriod_from_text(name)

        assert myEnum == sprEnums.timePeriods.days30

    """
    get_web_data tests. Returns nothing if nothing in securities dictionary, expected
    number of items if more than one item. One item returns one item. day, days30 and
    months3 return data from daily table, years1, years3 and years5 return from weekly
    table.
    """
    def test_zero_items(self, getSecurities):
        """
        No items in securities dictionary.
        """
        mySecs = getSecurities
        mySecs.securitiesDict = {}
        myPi = mySecs.get_web_data("1day")
        print(f"myPi={myPi}")

        assert len(myPi) == 0

    def test_oneDay_one_item(self, getSecurities):
        """
        One item in securities dictionary, one day of prices.
        """
        numDays = 1
        mySec = self.secsDict["AAPL"]
        mySecs = getSecurities
        mySecs.securitiesDict = {"AAPL": mySec}
        with patch('historicalPricesInterface.HistoricalPricesInterface.get_historical_prices', 
                    return_value=Mock()) as mock_get:
            mock_get.return_value = self._get_historical_prices(numDays)

            myPi = mySecs.get_web_data("1day")
            print(f"myPi={myPi}")

            assert len(myPi) == 1
            assert len(myPi[0].periodPrices) == numDays
            mock_get.assert_called_once_with(mySec.id, self.dailyDbName, numDays)

    def test_30Days_two_item(self, getSecurities):
        """
        Two items in securities dictionary, 30 days of prices.
        """
        numDays = 30
        applSec = self.secsDict["AAPL"]
        msftSec = self.secsDict["MSFT"]
        mySecs = getSecurities
        mySecs.securitiesDict = {"AAPL": applSec, "MSFT": msftSec}
        with patch('historicalPricesInterface.HistoricalPricesInterface.get_historical_prices', 
                    return_value=Mock()) as mock_get:
            mock_get.return_value = self._get_historical_prices(numDays)

            myPi = mySecs.get_web_data("30days")

            assert len(myPi) == 2
            assert myPi[0].periodDates[0] == date.today() - timedelta(numDays)
            mock_get.assert_called_with(msftSec.id, self.dailyDbName, numDays)

    def test_90Days_three_item(self, getSecurities):
        """
        Three items in securities dictionary, 93 days of prices.
        """
        numDays = 93
        mySecs = getSecurities
        mySecs.securitiesDict = self.secsDict
        with patch('historicalPricesInterface.HistoricalPricesInterface.get_historical_prices', 
                    return_value=Mock()) as mock_get:
            mock_get.return_value = self._get_historical_prices(numDays)

            myPi = mySecs.get_web_data("3months")

            assert len(myPi) == 3
            assert myPi[0].periodDates[0] == date.today() - timedelta(numDays)
            mock_get.assert_called_with(self.secsDict["GOOGL"].id, self.dailyDbName, numDays)


    @pytest.mark.parametrize("numDays, timePeriod",
                             [(365, "1year"),
                              (365 * 3, "3years"),
                              (365 * 5, "5years")])
    def test_various_years_three_items(self, getSecurities, numDays, timePeriod):
        """
        Three items in securities dictionary, one/three/five years of prices.
        """
        mySecs = getSecurities
        mySecs.securitiesDict = self.secsDict
        with patch('historicalPricesInterface.HistoricalPricesInterface.get_historical_prices', 
                    return_value=Mock()) as mock_get:
            mock_get.return_value = self._get_historical_prices(numDays)

            myPi = mySecs.get_web_data(timePeriod)

            assert len(myPi) == 3
            assert myPi[0].periodDates[0] == date.today() - timedelta(numDays)
            mock_get.assert_called_with(self.secsDict["GOOGL"].id, self.weeklyDbName, numDays)

    def _get_historical_prices(self, numDays):
        """
        Create list of priceDate/price dictionaries, to simulate data returned by
        get_historical_prices.
        """
        startDate = date.today() - timedelta(numDays)
        prices = []
        startPrice = 65.43
        randRange = 0.45 * startPrice
        newDate = startDate
        myDelta = timedelta(1)
        if numDays > 100:
            myDelta = timedelta(7)
        for i in range(numDays):
            priceDelta = random.uniform(-randRange, randRange)
            newPrice = round(Decimal(startPrice + priceDelta),2)
            prices.append({"priceDate": newDate, "price": newPrice})
            newDate += myDelta

        return prices

