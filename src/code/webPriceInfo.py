"""
Contains data for a single security needed for web page.
Includes logic to translate data into dictionary from security and prices.
V0.01, December 19, 2022, GAW
"""

from datetime import date

from security_groups import SecurityGroups

class WebPriceInfo:

    def __init__(self):
        self.name = ""
        self.currentPrice = 0
        self.lastClosePrice = 0
        self.buyPrice = 0
        self.sellPrice = 0
        self.periodStartPrice = 0
        self.periodLowPrice = 0
        self.periodHighPrice = 0
        self.status = ""
        self.group = ""
        self.rating = 0
        self.periodPrices = []
        self.periodDates = []

    def populate(self, mySecurity, myPrices):
        """
        Convert security and array of date/price pairs to this format.
        """
        self.name = mySecurity.name
        self.currentPrice = mySecurity.currentPrice
        self.lastClosePrice = mySecurity.lastClosePrice
        self.buyPrice = mySecurity.buyPrice
        self.sellPrice = mySecurity.sellPrice
        self.status = mySecurity.status
        self.periodPrices = self._get_prices_only(myPrices)
        self.periodDates = self._get_dates(myPrices)
        myGroups = SecurityGroups()
        self.rating, self.group = myGroups.get_values_for_webPriceInfo(self)
        if len(myPrices) > 0:
            self.periodStartPrice = myPrices[0]["price"]  # Price from first pair.
            self._set_high_low_prices()

    def getDict(self):
        """
        Convert this instance to a dictionary.
        Found that if left numbers as decimals, website received, for example \"1.234\",
        which it interpreted as a string, resulting in some strange comparisons. Hence,
        now converting numbers to floats.
        """
        myDict = {}
        myDict["name"] = self.name
        myDict["currentPrice"] = float(self.currentPrice)
        myDict["lastClosePrice"] = float(self.lastClosePrice)
        myDict["buyPrice"] = float(self.buyPrice)
        myDict["sellPrice"] = float(self.sellPrice)
        myDict["periodStartPrice"] = float(self.periodStartPrice)
        myDict["periodLowPrice"] = float(self.periodLowPrice)
        myDict["periodHighPrice"] = float(self.periodHighPrice)
        myDict["status"] = self.status
        myDict["group"] = self.group
        myDict["rating"] = self.rating
        myDict["periodPrices"] = self.periodPrices
        myDict["periodDates"] = self.periodDates
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
            if not( pair["price"] is None):
                prices.append(float(pair["price"]))
            else:
                prices.append(float(0))

        return prices

    def _get_dates(self, myPrices):
        """
        Convert historical prices from date/price pairs to a list of dates.
        """
        dates = []
        for pair in myPrices:
            dates.append(pair["priceDate"])

        return dates
