"""
Security and stkGraphData classes, for my spr (stock price checker) program.
Includes price DTO (data transfer object) class.
V0.02, February 28, 2021, GAW
"""

from decimal import Decimal
import math
from datetime import date

class PriceInfo:
    """
    Used to return price data after retrieve it from provider.
    """

    currentPrice = 0
    lastClosePrice = 0
    low52Week = 0
    high52Week = 0


class Security:
    """
    Track data for one stock/mutual fund/etf.
    """
    def __init__(self):
        self.id = 0
        self.name = ""
        self.symbol = ""
        self.buyPrice = 0
        self.sellPrice = 0
        self.currentPrice = 0
        self.currentPriceDate = None
        self.lastClosePrice = 0
        self.low52Week = 0
        self.high52Week = 0
        self.status = ""        # 0 = buy, 1 = sell, 2 = no action. Numbers chosen for sorting.
        self.fullHistoryDownloaded = False

    def __eq__(self, other):
        areSame = False
        if self.name == other.name:
            if self.buyPrice == other.buyPrice:
                if self.sellPrice == other.sellPrice:
                    if self.currentPrice == other.currentPrice:
                        if self.status == other.status:
                            if self.lastClosePrice == other.lastClosePrice:
                                if self.low52Week == other.low52Week:
                                    if self.high52Week == other.high52Week:
                                        areSame = True
        return areSame

    def __str__(self):
        return self.write()
                
    def write(self):
        """
        Create comma delimited string of properties, for writing to a file.
        """
        retStr = ""
        retStr = retStr + self.name + ","
        retStr = retStr + self.symbol + ","
        retStr = retStr + str(self.buyPrice) + ","
        retStr = retStr + str(self.sellPrice) + ","
        retStr = retStr + str(self.currentPrice) + ","
        retStr = retStr + str(self.currentPriceDate) + ","
        retStr = retStr + str(self.lastClosePrice) + ","
        retStr = retStr + str(self.low52Week) + ","
        retStr = retStr + str(self.high52Week) + ","
        retStr = retStr + self.status + ","
        retStr = retStr + str(self.fullHistoryDownloaded)

        return retStr

    def read(self, textLine):
        """
        Given string, line from saved file, parse into properties. Reverses write.
        Note that am recalculating status in case someone manually adjusted price or status in
        the file.
        """
        textList = textLine.split(",")
        self.name       = textList[0]
        self.symbol     = textList[1]
        self.buyPrice   = float(textList[2])
        self.sellPrice  = float(textList[3])
        self.currentPrice  = float(textList[4])
        if textList[5] == 'None':
            self.currentPriceDate = None
        else:
            self.currentPriceDate = date.fromisoformat(textList[5])
        self.lastClosePrice = float(textList[6])
        self.low52Week  = float(textList[7])
        self.high52Week = float(textList[8])
        self.status     = self.get_status()
        self.fullHistoryDownloaded = bool(textList[10])

    def get_status(self):
        """
        Calculate status for current security. See __init__ for values.
        CurrentPrice can be none if security was populated from a targetSecurity.
        """
        status = ""
        if not (self.currentPrice is None):
            if self.currentPrice < self.buyPrice:
                status = "0"
            elif self.currentPrice > self.sellPrice:
                status = "1"
            else:
                status = "2"
        return status

    def pop(self, name, symbol, buyPrice, sellPrice, currentPrice):
        """
        Populate from given properties.
        """
        self.name      = name
        self.symbol    = symbol
        self.buyPrice  = buyPrice
        self.sellPrice = sellPrice
        self.currentPrice = currentPrice
        self.status    = self.get_status()

    def pop_with_status(self, status, name, symbol, buyPrice, sellPrice, currentPrice):
        """
        Populate from given properties, including status.
        """
        self.status    = status
        self.name      = name
        self.symbol    = symbol
        self.buyPrice  = buyPrice
        self.sellPrice = sellPrice
        self.currentPrice = currentPrice

    def pop_with_priceInfo(self, name, symbol, buyPrice, sellPrice, priceInfo):
        """
        Populate from given properties.
        """
        self.name       = name
        self.symbol     = symbol
        self.buyPrice   = buyPrice
        self.sellPrice  = sellPrice
        self.currentPrice  = priceInfo.currentPrice
        self.currentPriceDate = date.today()
        self.lastClosePrice = priceInfo.lastClosePrice
        self.low52Week  = priceInfo.low52Week
        self.high52Week = priceInfo.high52Week
        self.status     = self.get_status()

    def pop_from_row(self, row, priceInfo):
        """
        Populate properties from row from spreadsheet.
        """
        self.name       = row.Stock
        self.symbol     = row.Symbol
        self.buyPrice   = row.Buy_price
        self.sellPrice  = row.Sell_price
        self.currentPrice  = priceInfo.currentPrice
        self.currentPriceDate  = date.today()
        self.lastClosePrice = priceInfo.lastClosePrice
        self.low52Week  = priceInfo.low52Week
        self.high52Week = priceInfo.high52Week
        self.status     = self.get_status()

    def pop_from_dict(self, secDict):
        """
        Populate from a dictionary taken from securities table.
        """
        self.id                     = secDict["id"]
        self.name                   = secDict["name"]
        self.symbol                 = secDict["symbol"]
        self.buyPrice               = self._to_dec(secDict["buyPrice"])
        self.sellPrice              = self._to_dec(secDict["sellPrice"])
        self.currentPrice           = self._to_dec(secDict["currentPrice"])
        self.currentPriceDate       = secDict["currentPriceDate"]
        self.lastClosePrice         = secDict["previousClosePrice"]
        self.low52Week              = self._to_dec(secDict["52weekLowPrice"])
        self.high52Week             = self._to_dec(secDict["52weekHighPrice"])
        self.status                 = self.get_status()        # 0 = buy, 1 = sell, 2 = no action. Numbers chosen for sorting.
        self.fullHistoryDownloaded  = secDict["fullHistoryDownloaded"]

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
        if self.currentPrice < self.buyPrice:
            lowVal = self.currentPrice
            myData.buyWid = self.buyPrice - self.currentPrice

        highVal = self.sellPrice
        if self.currentPrice > self.sellPrice:
            myData.sellWid = self.currentPrice - self.sellPrice
            highVal = self.currentPrice

        # if self.currentPrice > self.buyPrice and self.currentPrice < self.sellPrice:
        myData.priceLinePos = self.currentPrice

        # Want both bounds to be to the nearest 10, so label ticks are easy to understand.
        myData.offset  = lowVal
        lowVal         = 10 * (math.floor(lowVal/10))
        highVal        = 10 * (math.ceil(highVal/10))
        myData.xBounds = [lowVal, highVal]

        return myData

    def get_percent_change_today(self):
        """
        Calculate percentage change for today, using (current price - last close price) / last
        close price. Multiplying by 100 so get 20% rather than 0.20.
        """
        percentChangeToday = 0
        if self.lastClosePrice > 0:
            priceChangeToday = self.currentPrice - self.lastClosePrice
            percentChangeToday = (priceChangeToday / self.lastClosePrice) * 100
        else:
            print("Error, lastClosePrice=0 for security: ", self.symbol)

        return percentChangeToday

    def get_percent_52_week_high(self):
        """
        Calculate current price as a percentage of 52 week high.
        Multiplying by 100 so get 80% rather than 0.80.
        """
        percent = 0
        if self.high52Week > 0:
            percent = (self.currentPrice/self.high52Week) * 100
        else:
            print("Error, high52Week=0 for security:", self.symbol)

        return percent

    def get_changed_fields(self, newPriceInfo, currentDate):
        """
        Compare fields in given PriceInfo to values in this instance,
        putting fields with differences in parallel names and new values lists.
        """
        changedFields = []
        newValues = []

        if newPriceInfo.currentPrice != self.currentPrice:
            changedFields.append("currentPrice")
            newValues.append(newPriceInfo.currentPrice)
            changedFields.append("currentPriceDate")
            newValues.append(currentDate)
        
        if newPriceInfo.lastClosePrice != self.lastClosePrice:
            changedFields.append("previousClosePrice")
            newValues.append(newPriceInfo.lastClosePrice)

        if newPriceInfo.low52Week != self.low52Week:
            changedFields.append("52WeekLowPrice")
            newValues.append(newPriceInfo.low52Week)

        if newPriceInfo.high52Week != self.high52Week:
            changedFields.append("52WeekHighPrice")
            newValues.append(newPriceInfo.high52Week)

        return changedFields, newValues

    def update_values(self, newPriceInfo):
        """
        Copy given values to appropriate fields in current instance.
        """
        self.currentPrice = newPriceInfo.currentPrice
        self.currentPriceDate = date.today()
        self.lastClosePrice = newPriceInfo.lastClosePrice
        self.low52Week = newPriceInfo.low52Week
        self.high52Week = newPriceInfo.high52Week
    
    def _to_dec(self, origVal):
        returnVal = 0
        if not (origVal is None):
            returnVal = Decimal(origVal)
        
        return returnVal


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
