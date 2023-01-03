"""
File to test webPriceInfo
V0.01, December 19, 2022, GAW
"""

from datetime import date, timedelta
import pytest

from . import addSrcToPath

from webPriceInfo import WebPriceInfo
from security import Security

"""
What to test:
    No prices
    Normal data, 20 date/price pairs
    Only one element in price pairs
    First element is lowest, last item is highest
    first element is highest, last item is lowest
    All items same price.

"""

@pytest.mark.unit
class TestWebPriceInfo():
    def setup(self):
        # A starter security for testing
        self.applesec = Security()
        self.applesec.pop("Apple", "AAPL", 123.45, 543.21, 200.33)
        self.applesec.id = 3
        self.applesec.fullHistoryDownloaded = False

    def test_no_prices(self):
        """
        Verify that don't crash if create webPriceInfo with empty prices.
        """
        mySec = self.applesec
        myInfo = WebPriceInfo()
        myInfo.populate(mySec, [])

        assert myInfo.currentPrice == mySec.currentPrice
        assert myInfo.periodStartPrice == 0
        assert myInfo.periodLowPrice == 0
        assert myInfo.periodHighPrice == 0

    def test_one_price(self):
        """
        Verify correct calculations with one price.
        """
        mySec = self.applesec
        myInfo = WebPriceInfo()
        prices = [{"priceDate": date(2022, 12, 19), "price": 123.45}]
        myInfo.populate(mySec, prices)

        assert myInfo.currentPrice == mySec.currentPrice
        assert myInfo.periodStartPrice == 123.45
        assert myInfo.periodLowPrice == 123.45
        assert myInfo.periodHighPrice == 123.45

    def test_increasing_price(self):
        """
        Verify correct calculations with increasing prices.
        """
        mySec = self.applesec
        myInfo = WebPriceInfo()
        prices = []
        lowPrice = 20
        incPrice = 1.32
        numRows = 20
        curDate = date(2021, 12, 19)
        for i in range(0, numRows):
            curDate += timedelta(1)
            curPrice = lowPrice + i * incPrice
            prices.append({"priceDate": curDate, "price": curPrice})
        print(f"prices: {prices}")
        myInfo.populate(mySec, prices)

        assert myInfo.periodStartPrice == prices[0]["price"]
        assert myInfo.periodLowPrice == lowPrice
        assert myInfo.periodHighPrice == prices[numRows - 1]["price"]

    def test_decreasing_price(self):
        """
        Verify correct calculations with decreasing prices.
        """
        mySec = self.applesec
        myInfo = WebPriceInfo()
        prices = []
        highPrice = 234.56
        decPrice = 1.32
        numRows = 20
        curDate = date(2021, 12, 19)
        for i in range(0, numRows):
            curDate += timedelta(1)
            curPrice = highPrice - i * decPrice
            prices.append({"priceDate": curDate, "price": curPrice})
        print(f"prices: {prices}")
        myInfo.populate(mySec, prices)

        assert myInfo.periodStartPrice == prices[0]["price"]
        assert myInfo.periodLowPrice == prices[numRows - 1]["price"]
        assert myInfo.periodHighPrice == highPrice

    def test_fixed_prices(self):
        """
        Verify correct calculations with manually set prices, low, high in middle.
        """
        mySec = self.applesec
        myInfo = WebPriceInfo()
        prices = []
        highPrice = 234.56
        lowPrice = 191.32
        curDate = date(2021, 12, 19)
        prices.append({"priceDate": curDate, "price": 201.3})
        curDate += timedelta(1)
        prices.append({"priceDate": curDate, "price": lowPrice})
        curDate += timedelta(1)
        prices.append({"priceDate": curDate, "price": 193.3})
        curDate += timedelta(1)
        prices.append({"priceDate": curDate, "price": 221.3})
        curDate += timedelta(1)
        prices.append({"priceDate": curDate, "price": 214.3})
        curDate += timedelta(1)
        prices.append({"priceDate": curDate, "price": 223.3})
        curDate += timedelta(1)
        prices.append({"priceDate": curDate, "price": 213.3})
        curDate += timedelta(1)
        prices.append({"priceDate": curDate, "price": highPrice})
        curDate += timedelta(1)
        prices.append({"priceDate": curDate, "price": 203.3})

        print(f"prices: {prices}")
        myInfo.populate(mySec, prices)

        assert myInfo.periodStartPrice == prices[0]["price"]
        assert myInfo.periodLowPrice == lowPrice
        assert myInfo.periodHighPrice == highPrice

    def test_dict_convert(self):
        """
        Verify that conversion to dictionary works correctly.
        """
        mySec = self.applesec
        myInfo = WebPriceInfo()
        prices = []
        pricesOnly = []
        datesOnly = []
        lowPrice = 20
        incPrice = 1.32
        numRows = 20
        curDate = date(2021, 12, 19)
        for i in range(0, numRows):
            curDate += timedelta(1)
            curPrice = lowPrice + i * incPrice
            prices.append({"priceDate": curDate, "price": curPrice})
            pricesOnly.append(curPrice)
            datesOnly.append(curDate)

        myInfo.populate(mySec, prices)
        myDict = myInfo.getDict()

        assert myDict["name"] == mySec.name
        assert myDict["currentPrice"] == mySec.currentPrice
        assert myDict["buyPrice"] == mySec.buyPrice
        assert myDict["sellPrice"] == mySec.sellPrice
        assert myDict["status"] == mySec.status
        assert myDict["periodStartPrice"] == prices[0]["price"]
        assert myDict["periodLowPrice"] == lowPrice
        assert myDict["periodHighPrice"] == prices[numRows - 1]["price"]
        assert myDict["group"] == myInfo.group
        assert myDict["rating"] == myInfo.rating
        assert myDict["periodPrices"] == pricesOnly
        assert myDict["periodDates"] == datesOnly

    """
    Group/rating tests:
        Test that get expected text for each group
        Test that get expected rating - negative if buy group.
    """
    def test_group_text_buy(self):
        """
        Verify that get expected text.
        """
        mySec = self.applesec
        mySec.currentPrice = 48
        mySec.buyPrice = 50
        mySec.sellPrice = 100
        myInfo = WebPriceInfo()
        prices = []
        myInfo.populate(mySec, prices)

        assert myInfo.group == "1.buy"
        assert myInfo.rating == 0 - (mySec.buyPrice - mySec.currentPrice) / mySec.buyPrice

    def test_group_text_near_sell(self):
        """
        Verify that get expected text.
        """
        mySec = self.applesec
        mySec.currentPrice = 90
        mySec.buyPrice = 50
        mySec.sellPrice = 100
        myInfo = WebPriceInfo()
        prices = []
        myInfo.populate(mySec, prices)

        assert myInfo.group == "4.near sell"
        assert myInfo.rating == (mySec.currentPrice - mySec.buyPrice) / (mySec.sellPrice - mySec.buyPrice)
