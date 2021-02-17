"""
File to test Security class
V0.01, February 27, 2019, GAW
"""

import pandas as pd

import security


class TestSecurity():
    def setup(self):
        self.dfColNames = ["Stock",
                           "Buy_price",
                           "Sell_price",
                           "Symbol",
                           "Ignore"]	# Dataframe column names.
        self.testPrice = 11.59

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
        mySecurity.pop_from_row(firstRow, self.testPrice)
        assert mySecurity.symbol == firstRow.Symbol
        assert mySecurity.buyPrice == firstRow.Buy_price
        assert mySecurity.sellPrice == firstRow.Sell_price
        assert mySecurity.name == firstRow.Stock
        assert mySecurity.currPrice == self.testPrice

    def test_write(self):
        """
        Test that write function returns expected string.
        """
        testDf = self.createSrcDf()
        firstRow = testDf.iloc[0]
        mySecurity = security.Security()
        mySecurity.pop_from_row(firstRow, self.testPrice)
        retStr = mySecurity.write()
        goodStr = firstRow.Stock + "," + firstRow.Symbol + "," + str(firstRow.Buy_price) + ","
        goodStr = goodStr + str(firstRow.Sell_price) + "," + str(self.testPrice) + "," + "2"
        assert retStr == goodStr

    def test_read_match(self):
        """
        Test that read function gives expected result.
        Creates a writeStr by creating a row and then a security.
        Then, pass that to read, verify that values are as expected.
        """
        myRow = self.createSrcRow()
        writeSecurity = security.Security()
        writeSecurity.pop_from_row(myRow, self.testPrice)
        writeStr = writeSecurity.write()

        readSecurity = security.Security()
        readSecurity.read(writeStr)
        assert readSecurity.name      == writeSecurity.name
        assert readSecurity.symbol    == writeSecurity.symbol
        assert readSecurity.buyPrice  == writeSecurity.buyPrice
        assert readSecurity.sellPrice == writeSecurity.sellPrice
        assert readSecurity.currPrice == writeSecurity.currPrice
        assert readSecurity.status    == writeSecurity.status

    def test_read_fixesStatus(self):
        """
        Test an invalid record - i.e. change status after populating, write it, read it, confirm
        that has correct status after.
        """
        myRow = self.createSrcRow()
        writeSecurity = security.Security()
        writeSecurity.pop_from_row(myRow, self.testPrice)
        writeSecurity.status = "0"
        writeStr = writeSecurity.write()

        readSecurity = security.Security()
        readSecurity.read(writeStr)
        assert readSecurity.name ==      writeSecurity.name
        assert readSecurity.symbol ==    writeSecurity.symbol
        assert readSecurity.buyPrice ==  writeSecurity.buyPrice
        assert readSecurity.sellPrice == writeSecurity.sellPrice
        assert readSecurity.currPrice == writeSecurity.currPrice
        assert readSecurity.status ==    "2"

    def run_get_status_test(self, price, expectedResult):
        """
        Test that get expected status for given price.
        """
        myRow = self.createSrcRow()
        mySecurity = security.Security()
        mySecurity.pop_from_row(myRow, price)
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

    def createSecurity(self, status, name, symbol, buyPrice, sellPrice, currPrice):
        mySec = security.Security()
        mySec.pop_with_status(status, name, symbol, buyPrice, sellPrice, currPrice)
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
