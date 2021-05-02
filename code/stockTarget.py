"""
Stock target class, for my spr (stock price retriever) program.
V0.04, May 11, 2020
Given name of a spreadsheet, reads contents, returns a list of valid rows.
Rows valid if contain security code, buy and sell prices, aren't marked
as "ignore".
"""

import os.path

import pandas as pd


class StockTarget:
    """
    Reads list of stock targets (security symbols) from given excel spreadsheet/tab.
    """
    def _is_rec_complete(self, row):
        """
        Ensure that required fields are populated for this record - symbol,
        buy price and sell price.
        """
        retVal = False
        if pd.isnull(row.Symbol):
            print("No symbol given for stock ", row.Stock)
        elif pd.isnull(row.Buy_price):
            print("No buy price given for stock ", row.Stock)
        elif pd.isnull(row.Sell_price):
            print("No sell price given for stock ", row.Stock)
        else:
            retVal = True

        return retVal

    def _get_worksheet(self, srcFile, tabName):
        """
        Open file for reading, retrieve the worksheet, return it. If hit error, return none.
        """
        myWs = None
        if os.path.isfile(srcFile):
            try:
                with pd.ExcelFile(srcFile) as xlFile:
                    myWs = xlFile.parse(tabName)

            except (FileNotFoundError, PermissionError, ValueError) as E:
                print("Exception when trying to read file: ", srcFile)
                print(E)
        else:
            print("Unable to find file: ", srcFile)

        return myWs

    def get_list(self, srcFile, tabName):
        """
        Read in list of securities, from given excel filename and tab.
        """
        securityList = []
        print("Starting stockTarget.get_list.")
        # Get dataframe from file.
        myWs = self._get_worksheet(srcFile, tabName)
        if not(myWs is None):
            # Loop through all records in spreadsheet, saving ones we want to retrieve prices for.
            for row in myWs.itertuples(index=False):
                if not (pd.isnull(row.Stock)) and row.Ignore == "N":
                    print("Looking at stock ", row.Stock)
                    if self._is_rec_complete(row):
                        securityList.append(row)

        return securityList
