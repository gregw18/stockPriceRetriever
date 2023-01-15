"""
# Tests for retrievePrices class
# V0.01, May 2, 2021, GAW
"""

from datetime import date, timedelta, datetime
import pytest

from . import addSrcToPath

import settings
import yahooInterface

badBucketNameFile = "nobucket-name.txt"
bucketNameFile = "bucket-name.txt"
myPrefix = "noprefix"
mysettings = settings.Settings.instance()
symbolAmazon = "AMZN"
symbolExxon = "XOM"
symbolBad = "Z23C"
badFrequency = "1c"

@pytest.mark.integration
class TestRetrievePrices():
    """
    Testing that working with prices > 999.99 - had errors converting strings with commas
    to float.
    """
    def test_getAMZN(self):
        """
        Confirm that both values that are used as denominators are > 0.
        """
        myInfo = yahooInterface.retrieve_daily_data(symbolAmazon, mysettings)
        assert myInfo.high52Week > 0
        assert myInfo.lastClosePrice > 0

    def test_split(self):
        """
        Verify that am now successfully splitting numbers containing commas.
        """
        testRange = "1,334.01 - 2,345.99"
        low, high = yahooInterface._split_price_range(testRange)
        assert low == 1334.01
        assert high == 2345.99

    def test_yahoo_daily_bad_symbol(self):
        """
        Try to retrieve daily data for bad symbol.
        """
        priceInfo = yahooInterface.retrieve_daily_data(symbolBad, mysettings)

        assert priceInfo.currentPrice == 0

    def test_yahoo_daily_bad_symbol2(self):
        """
        Try to retrieve daily data for bad symbol.
        """
        priceInfo = yahooInterface.retrieve_daily_data('ALXN', mysettings)

        assert priceInfo.currentPrice == 0

    def test_yahoo_historical_daily_1week(self):
        """
        Retrieve daily prices for amazon for last week. Should all be > 0.
        Note that if use now for newest data, test fails if last week includes a holiday.
        """
        timePeriod = timedelta(7)
        newestDate = date(2022, 12, 19)
        oldestDate = newestDate - timePeriod
        prices = yahooInterface.retrieve_historical_prices(symbolAmazon,
                                                           oldestDate,
                                                           newestDate,
                                                           mysettings.daily_price_code)
        assert len(prices) == 5
        for price in prices:
            assert price[1] > 0

    def test_yahoo_historical_daily_90days(self):
        """
        Retrieve daily prices for Exxon for last 90 days. Should all be > 0.
        """
        timePeriod = timedelta(90)
        oldestDate = datetime.now().date() - timePeriod
        prices = yahooInterface.retrieve_historical_prices(symbolExxon,
                                                           oldestDate,
                                                           datetime.now().date(),
                                                           mysettings.daily_price_code)
        assert len(prices) > 60
        for price in prices:
            assert price[1] > 0

    def test_yahoo_historical_weekly_1week(self):
        """
        Retrieve weekly prices for Exxon for one week. Should all be > 0.
        See yahooInterface.retrieve_historical_prices comments for some
        unexpected behaviours regarding weekly prices.
        """
        timePeriod = timedelta(2)
        newestDate = date(2022, 11, 2)
        oldestDate = newestDate - timePeriod
        prices = yahooInterface.retrieve_historical_prices(symbolExxon,
                                                           oldestDate,
                                                           newestDate,
                                                           mysettings.weekly_price_code)
        assert len(prices) == 1
        for price in prices:
            assert price[1] > 0

    def test_yahoo_historical_weekly_60weeks(self):
        """
        Retrieve weekly prices for Exxon for 60 weeks. Should all be > 0.
        See yahooInterface.retrieve_historical_prices comments for some
        unexpected behaviours regarding weekly prices.
        """
        timePeriod = timedelta(60 * 7 - 3)
        newestDate = date(2022, 12, 2)
        oldestDate = newestDate - timePeriod
        prices = yahooInterface.retrieve_historical_prices(symbolExxon,
                                                           oldestDate,
                                                           newestDate,
                                                           mysettings.weekly_price_code)
        assert len(prices) == 60
        for price in prices:
            assert price[1] > 0

    def test_yahoo_historical_bad_symbol(self):
        """
        Provide bad symbol, expect error.
        """
        timePeriod = timedelta(4)
        oldestDate = datetime.now().date() - timePeriod
        prices = None
        prices = yahooInterface.retrieve_historical_prices(symbolBad,
                                                           oldestDate,
                                                           datetime.now().date(),
                                                           mysettings.daily_price_code)

        assert len(prices) == 0

    def test_yahoo_historical_bad_frequency(self):
        """
        Provide bad frequency, expect error.
        """
        timePeriod = timedelta(4)
        oldestDate = datetime.now().date() - timePeriod
        prices = None
        prices = yahooInterface.retrieve_historical_prices(symbolBad,
                                                           oldestDate,
                                                           datetime.now().date(),
                                                           badFrequency)

        assert len(prices) == 0
