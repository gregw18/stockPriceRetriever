"""
File to test Security class
V0.01, February 27, 2019, GAW
"""

import pandas as pd
import pytest

import security


class TestSecurity():
    def setup(self):
        # Dataframe column names.
        self.dfColNames = ["Stock",
                           "Buy_price",
                           "Sell_price",
                           "Symbol",
                           "Ignore"]
        self.testPrice = 11.59
        self.testPriceInfo = security.PriceInfo()
        self.testPriceInfo.currentPrice = self.testPrice
        self.testPriceInfo.lastClosePrice = 42.33
        self.testPriceInfo.low52Week = 33.21
        self.testPriceInfo.high52Week = 64.34

    def createSrcDf(self):
        """
        Create a dataframe that looks like row from source spreadsheet, with fixed values.
        """
        return pd.DataFrame(columns=self.dfColNames, data=[["AltaGas", 1, 29, "TSX:ALA", "N"]])

    def createSrcRow(self):
        """
        Create a row from a dataframe from source spreadsheet, with fixed values.
        """
        testDf = self.createSrcDf()
        return testDf.iloc[0]

    def test_pop_from_row_parsesCorrectly(self):
        """
        Test that properly parsing a dataframe.
        """
        testDf = self.createSrcDf()
        mySecurity = security.Security()
        firstRow = testDf.iloc[0]
        mySecurity.pop_from_row(firstRow, self.testPriceInfo)
        assert mySecurity.symbol == firstRow.Symbol
        assert mySecurity.buyPrice == firstRow.Buy_price
        assert mySecurity.sellPrice == firstRow.Sell_price
        assert mySecurity.name == firstRow.Stock
        assert mySecurity.currentPrice == self.testPriceInfo.currentPrice
        assert mySecurity.lastClosePrice == self.testPriceInfo.lastClosePrice
        assert mySecurity.low52Week == self.testPriceInfo.low52Week
        assert mySecurity.high52Week == self.testPriceInfo.high52Week

    def test_write(self):
        """
        Test that write function returns expected string.
        """
        testDf = self.createSrcDf()
        firstRow = testDf.iloc[0]
        mySecurity = security.Security()
        mySecurity.pop_from_row(firstRow, self.testPriceInfo)
        retStr = mySecurity.write()
        goodStr = firstRow.Stock + "," + firstRow.Symbol + "," + str(firstRow.Buy_price) + ","
        goodStr += str(firstRow.Sell_price) + "," + str(self.testPriceInfo.currentPrice) + ","
        goodStr += str(self.testPriceInfo.lastClosePrice) + ","
        goodStr += str(self.testPriceInfo.low52Week) + ","
        goodStr += str(self.testPriceInfo.high52Week) + "," + "2"
        assert retStr == goodStr

    def test_read_match(self):
        """
        Test that read function gives expected result.
        Creates a writeStr by creating a row and then a security.
        Then, pass that to read, verify that values are as expected.
        """
        myRow = self.createSrcRow()
        writeSecurity = security.Security()
        writeSecurity.pop_from_row(myRow, self.testPriceInfo)
        writeStr = writeSecurity.write()

        readSecurity = security.Security()
        readSecurity.read(writeStr)
        assert readSecurity == writeSecurity

    def test_read_fixesStatus(self):
        """
        Test an invalid record - i.e. change status after populating, write it, read it, confirm
        that has correct status after.
        """
        myRow = self.createSrcRow()
        writeSecurity = security.Security()
        writeSecurity.pop_from_row(myRow, self.testPriceInfo)
        writeSecurity.status = "0"
        writeStr = writeSecurity.write()

        readSecurity = security.Security()
        readSecurity.read(writeStr)
        assert readSecurity.name           == writeSecurity.name
        assert readSecurity.symbol         == writeSecurity.symbol
        assert readSecurity.buyPrice       == writeSecurity.buyPrice
        assert readSecurity.sellPrice      == writeSecurity.sellPrice
        assert readSecurity.currentPrice   == writeSecurity.currentPrice
        assert readSecurity.lastClosePrice == writeSecurity.lastClosePrice
        assert readSecurity.low52Week      == writeSecurity.low52Week
        assert readSecurity.high52Week     == writeSecurity.high52Week
        assert readSecurity.status         == "2"

    def run_get_status_test(self, price, expectedResult):
        """
        Test that get expected status for given price.
        """
        myRow = self.createSrcRow()
        mySecurity = security.Security()
        myPriceInfo = security.PriceInfo()
        myPriceInfo.currentPrice = price
        mySecurity.pop_from_row(myRow, myPriceInfo)
        calcStatus = mySecurity.get_status()
        assert calcStatus == expectedResult

    def test_get_status_noAction1(self):
        """
        price = 11.59, buy = 1, sell = 29, expect no action (2).
        """
        self.run_get_status_test(11.59, "2")

    def test_get_status_noAction2(self):
        """
        Price = 1, expect no action (2).
        """
        self.run_get_status_test(1, "2")

    def test_get_status_noAction3(self):
        """
        Price = 29, expect no action (2).
        """
        self.run_get_status_test(29, "2")

    def test_get_status_Buy1(self):
        """
        Price = 0.50, expect buy (0).
        """
        self.run_get_status_test(0.50, "0")

    def test_get_status_Sell1(self):
        """
        Price = 29.01, expect sell (1).
        """
        self.run_get_status_test(29.01, "1")

    def createSecurity(self, status, name, symbol, buyPrice, sellPrice, currentPrice):
        mySec = security.Security()
        mySec.pop_with_status(status, name, symbol, buyPrice, sellPrice, currentPrice)
        return mySec

    def test_sort1(self):
        """
        Create three securities, put in a list, then sort. Verify expected order.
        """
        sec1 = self.createSecurity("1", "Sell me", "S1", 1, 1, 1)
        sec2 = self.createSecurity("0", "Buy me", "B2", 1, 1, 1)
        sec3 = self.createSecurity("2", "Ignore", "I1", 1, 1, 1)
        sec4 = self.createSecurity("0", "And Buy me", "B1", 1, 1, 1)
        secList = [sec1, sec2, sec3, sec4]
        expectedSymbolList = ["B1", "B2", "S1", "I1"]
        secList.sort(key=lambda x: x.get_sort_string())
        for x, y in zip(secList, expectedSymbolList):
            assert x.symbol == y

    def test_StkGraphData_NoBuySell(self):
        """
        Create security with current within buy and sell, so shouldn't have buy or sell bars.
        """
        sec = self.createSecurity("1", "STOCK", "A", 5, 15, 10)
        myData = sec.get_graph_data()
        assert myData.buyWid == 0
        assert myData.sellWid == 0
        assert myData.noActionWid == 10
        assert myData.priceLinePos == 10
        assert myData.xBounds[0] == 0
        assert myData.xBounds[1] == 20

    def test_StkGraphData_BuyBar(self):
        """
        Create security with current within buy and sell, so shouldn't have buy or sell bars.
        """
        sec = self.createSecurity("1", "STOCK", "A", 15, 25, 2)
        myData = sec.get_graph_data()
        assert myData.buyWid == 13
        assert myData.sellWid == 0
        assert myData.noActionWid == 10
        assert myData.priceLinePos == 2
        assert myData.xBounds[0] == 0
        assert myData.xBounds[1] == 30

    def test_StkGraphData_SellBar(self):
        """
        Create security with current within buy and sell, so shouldn't have buy or sell bars.
        """
        sec = self.createSecurity("1", "STOCK", "A", 15, 205, 301)
        myData = sec.get_graph_data()
        assert myData.buyWid == 0
        assert myData.sellWid == 96
        assert myData.noActionWid == 190
        assert myData.priceLinePos == 301
        assert myData.xBounds[0] == 10
        assert myData.xBounds[1] == 310

    @pytest.mark.parametrize("current, lastClose, expected",
                             [(12, 10, 20),
                              (80, 100, -20),
                              (10, 10, 0),
                              (12, 0, 0)])
    def test_percentChange(self, current, lastClose, expected):
        """
        Create security with current within buy and sell, so shouldn't have buy or sell bars.
        Testing increase, decrease and no change.
        """
        testDf = self.createSrcDf()
        mySecurity = security.Security()
        firstRow = testDf.iloc[0]
        priceInfo = security.PriceInfo()
        priceInfo.currentPrice = current
        priceInfo.lastClosePrice = lastClose
        mySecurity.pop_from_row(firstRow, priceInfo)

        percentChange = mySecurity.get_percent_change_today()

        assert percentChange == expected

    @pytest.mark.parametrize("current, high52week, expected",
                             [(8, 10, 80),
                              (80, 80, 100),
                              (12, 10, 120),
                              (20, 0, 0)])
    def test_percentof52Week(self, current, high52week, expected):
        """
        Create security with current above, equal to and below 52 week high.
        """
        testDf = self.createSrcDf()
        mySecurity = security.Security()
        firstRow = testDf.iloc[0]
        priceInfo = security.PriceInfo()
        priceInfo.currentPrice = current
        priceInfo.high52Week = high52week
        mySecurity.pop_from_row(firstRow, priceInfo)

        percentage = mySecurity.get_percent_52_week_high()

        assert percentage == expected
