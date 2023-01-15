"""
Subset of data in security, the fields that come from the excel file containing
the list of securities that want to follow, their symbols and buy/sell prices.
V0.01, November 30, 2022, GAW
"""


class TargetSecurity:
    """
    Track data from source file for one stock/mutual fund/etf.
    """
    def __init__(self):
        self.name = ""
        self.symbol = ""
        self.buyPrice = 0
        self.sellPrice = 0

    def populate_from_row(self, rowData):
        """
        Populate instance from provided row of data.
        Assumes already verified that fields are populated.
        """
        self.name = rowData.Stock
        self.symbol = rowData.Symbol
        self.buyPrice = rowData.Buy_price
        self.sellPrice = rowData.Sell_price

    def populate_from_dict(self, dictData):
        """
        Populate instance from provided row of data.
        Assumes already verified that fields are populated.
        """
        self.name = dictData["Stock"]
        self.symbol = dictData["Symbol"]
        self.buyPrice = dictData["Buy_price"]
        self.sellPrice = dictData["Sell_price"]
