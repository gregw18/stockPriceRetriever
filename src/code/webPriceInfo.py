"""
Contains data for a single security needed for web page.
Includes logic to translate data into dictionary from security and prices.
V0.01, December 19, 2022, GAW
"""

from datetime import date

class WebPriceInfo:

    def __init__(self):
        self.name = ""
        self.currentPrice = 0
        self.buyPrice = 0
        self.sellPrice = 0
        self.periodStartPrice = 0
        self.periodLowPrice = 0
        self.periodHighPrice = 0
        self.status = ""
        self.periodPrices = []
        self.periodDates = []

    def populate(self, mySecurity, myPrices):
        """
        Convert security and array of date/price pairs to this format.
        """
        self.name = mySecurity.name
        self.currentPrice = mySecurity.currentPrice
        self.buyPrice = mySecurity.buyPrice
        self.sellPrice = mySecurity.sellPrice
        self.status = mySecurity.status
        #self.periodPrices = myPrices
        self.periodPrices = self._get_prices_only(myPrices)
        self.periodDates = self._get_dates(myPrices)
        if len(myPrices) > 0:
            self.periodStartPrice = myPrices[0]["price"]  # Price from first pair.
            self._set_high_low_prices()

    def getDict(self):
        """
        Convert this instance to a dictionary.
        """
        myDict = {}
        myDict["name"] = self.name
        myDict["currentPrice"] = self.currentPrice
        myDict["buyPrice"] = self.buyPrice
        myDict["sellPrice"] = self.sellPrice
        myDict["periodStartPrice"] = self.periodStartPrice
        myDict["periodLowPrice"] = self.periodLowPrice
        myDict["periodHighPrice"] = self.periodHighPrice
        myDict["status"] = self.status
        myDict["periodPrices"] = self.periodPrices
        myDict["periodDate"] = self.periodDates
        print(f"getDict, {myDict = }")
        
        return myDict

    def _set_high_low_prices(self):
        """
        Find lowest and highest prices from list, store in periodLow/High
        """

        min = self.periodPrices[0]
        #min = self.periodPrices[0]["price"]
        max = min
        for val in self.periodPrices:
            if val < min:
                min = val
            if val > max:
                max = val
        
        self.periodLowPrice = min
        self.periodHighPrice = max

    def _get_prices_only(self, myPrices):
        """
        Convert historical prices from date/price pairs to a list of prices.
        """
        prices = []
        for pair in myPrices:
            prices.append(pair["price"])

        return prices

    def _get_dates(self, myPrices):
        """
        Convert historical prices from date/price pairs to a list of dates.
        """
        dates = []
        for pair in myPrices:
            dates.append(pair["priceDate"])

        return dates
