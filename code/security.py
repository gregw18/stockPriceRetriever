"""
Security and stkGraphData classes, for my spr (stock price checker) program.
V0.01, February 26, 2019, GAW
"""

import math


class Security:
    """
    Track data for one stock/mutual fund/etf.
    """
    def __init__(self):
        self.name = ""
        self.symbol = ""
        self.buyPrice = 0
        self.sellPrice = 0
        self.currPrice = 0
        self.status = ""        # 0 = buy, 1 = sell, 2 = no action. Numbers chosen for sorting.

    def __eq__(self, other):
        areSame = False
        if self.name == other.name:
            if self.buyPrice == other.buyPrice:
                if self.sellPrice == other.sellPrice:
                    if self.currPrice == other.currPrice:
                        if self.status == other.status:
                            areSame = True
        return areSame

    def write(self):
        """
        Create comma delimited string of properties, for writing to a file.
        """
        retStr = ""
        retStr = retStr + self.name + ","
        retStr = retStr + self.symbol + ","
        retStr = retStr + str(self.buyPrice) + ","
        retStr = retStr + str(self.sellPrice) + ","
        retStr = retStr + str(self.currPrice) + ","
        retStr = retStr + self.status

        return retStr

    def read(self, textLine):
        """
        Given string, line from saved file, parse into properties. Reverses write.
        Note that am recalculating status in case someone manually adjusted price or status in
        the file.
        """
        textList = textLine.split(",")
        self.name      = textList[0]
        self.symbol    = textList[1]
        self.buyPrice  = float(textList[2])
        self.sellPrice = float(textList[3])
        self.currPrice = float(textList[4])
        self.status    = self.get_status()

    def get_status(self):
        """
        Calculate status for current security. See __init__ for values.
        """
        if self.currPrice < self.buyPrice:
            status = "0"
        elif self.currPrice > self.sellPrice:
            status = "1"
        else:
            status = "2"
        return status

    def pop(self, name, symbol, buyPrice, sellPrice, currPrice):
        """
        Populate from given properties.
        """
        self.name      = name
        self.symbol    = symbol
        self.buyPrice  = buyPrice
        self.sellPrice = sellPrice
        self.currPrice = currPrice
        self.status    = self.get_status()

    def pop_with_status(self, status, name, symbol, buyPrice, sellPrice, currPrice):
        """
        Populate from given properties, including status.
        """
        self.status    = status
        self.name      = name
        self.symbol    = symbol
        self.buyPrice  = buyPrice
        self.sellPrice = sellPrice
        self.currPrice = currPrice

    def pop_from_row(self, row, price):
        """
        Populate properties from row from spreadsheet.
        """
        self.name      = row.Stock
        self.symbol    = row.Symbol
        self.buyPrice  = row.Buy_price
        self.sellPrice = row.Sell_price
        self.currPrice = price
        self.status    = self.get_status()

    def get_sort_string(self):
        """
        Return string to sort this instance - status + name.
        Thus, all buys first, then all sells, then all no actions, sorted
        by name within each group. (Name is easier to read and interpret than many symbols.)
        """
        sortStr = self.status + self.name
        return sortStr

    def get_graph_data(self):
        """
        Translate current price info into info required to draw graph.
        """
        myData = StkGraphData()
        myData.noActionWid = self.sellPrice - self.buyPrice

        lowVal = self.buyPrice
        if self.currPrice < self.buyPrice:
            lowVal = self.currPrice
            myData.buyWid = self.buyPrice - self.currPrice

        highVal = self.sellPrice
        if self.currPrice > self.sellPrice:
            myData.sellWid = self.currPrice - self.sellPrice
            highVal = self.currPrice

        # if self.currPrice > self.buyPrice and self.currPrice < self.sellPrice:
        myData.priceLinePos = self.currPrice

        # Want both bounds to be to the nearest 10, so label ticks are easy to understand.
        myData.offset  = lowVal
        lowVal         = 10 * (math.floor(lowVal/10))
        highVal        = 10 * (math.ceil(highVal/10))
        myData.xBounds = [lowVal, highVal]

        return myData


class StkGraphData:
    """
    Contains data used to graph a given security.
    """

    def __init__(self):
        """
        Initialize to default values.
        """
        self.buyWid       = 0               # Width of buy bar.
        self.noActionWid  = 0               # Width of "no action" bar.
        self.sellWid      = 0               # Width of sell bar.
        self.priceLinePos = 0               # Horizontal position to draw current price line at.
                                            # Zero if in buy or sell range.
        self.xBounds      = [0, 0]          # Range of price values to display on x axis.
        self.offset       = 0               # Offset from 0 to start displaying bars.

    def get_string(self):
        """
        Return a string, can be used for troubleshooting.
        """
        retStr = ""
        retStr = retStr + "offset: "   + str(self.offset) + ", "
        retStr = retStr + "buy: "      + str(self.buyWid) + ", "
        retStr = retStr + "noAction: " + str(self.noActionWid) + ", "
        retStr = retStr + "sell: "     + str(self.sellWid) + ", "
        retStr = retStr + "line: "     + str(self.priceLinePos) + ", "
        retStr = retStr + "bounds: "   + str(self.xBounds[0]) + ":" + str(self.xBounds[1])

        return retStr
