"""
Interface between securities/security and dbAccess. Should contain no
business logic. Should not communicate directly with mySql.
V0.01, November 22, 2022
"""

from datetime import date, timedelta

import dbAccess
import settings


class SecuritiesInterface:

    def __init__(self):
        self.settings = settings.Settings.instance()
        self.securitiesTable = self.settings.db_securities_table_name
        self.fieldNames = ["id", "name", "symbol", "fullHistoryDownloaded", "buyPrice",
                           "sellPrice", "currentPrice", "currentPriceDate", "previousClosePrice",
                           "52weekLowPrice", "52weekHighPrice", "percentChangeToday"]

    def get_securities(self):
        """
        Return list of dictionaries, one dictionary for each security.
        """
        query = "1=1"
        results = dbAccess.select_data(self.securitiesTable, self.fieldNames, query)
        return results

    def add_security(self, newSecurity):
        """
        Add given targetSecurity to table. Need to ensure that don't have existing record
        with same symbol. Note that only saves a subset of fields - just those expected
        in the source list, not fields that are retrieved from internet as part of the
        daily price update.
        """
        addedOk = False
        mySymbol = newSecurity.symbol.upper()
        query = f"symbol= {mySymbol!r}"
        results = dbAccess.select_data(self.securitiesTable, ["ID",], query)
        if len(results) == 0:
            fieldNames = ["name", "symbol", "buyPrice", "sellPrice", "fullHistoryDownloaded"]
            fieldValues = [None] * len(fieldNames)
            fieldValues[0] = newSecurity.name
            fieldValues[1] = mySymbol
            fieldValues[2] = newSecurity.buyPrice
            fieldValues[3] = newSecurity.sellPrice
            fieldValues[4] = "N"

            # Need to nest the list so that connector recognizes that adding one record
            # with five values, rather than five records with one value each.
            nestedValues = [fieldValues,]
            if dbAccess.insert_data(self.securitiesTable, fieldNames, nestedValues):
                print(f"successfully added record for {mySymbol}")
                addedOk = True
            else:
                print(f"failed to add record for symbol {mySymbol}")

        else:
            print(f"Error: symbol {mySymbol} already exists in table {self.securitiesTable}")

        return addedOk

    def update_security(self, securityId, fieldNames, fieldValues):
        """
        Update security with given id with given values for provided fields.
        """
        updatedOk = False

        query = f"id={securityId}"
        numUpdated = dbAccess.update_data(self.securitiesTable, fieldNames, fieldValues, query)
        if numUpdated == 1:
            updatedOk = True

        return updatedOk

    def delete_security(self, deleteId):
        """
        Try to delete security for given id.
        """
        wasDeleted = False

        query = f"id={deleteId}"
        numDeleted = dbAccess.delete_data(self.securitiesTable, query)
        print(f"Deleting from {self.securitiesTable} with query {query} "
              f"resulted in {numDeleted} records being deleted.")
        if numDeleted == 1:
            wasDeleted = True

        return wasDeleted

    def mark_historical_data_retrieved(self, securityId):
        """
        Flag given security as having its historical data downloaded.
        """
        return self.update_security(securityId, ["fullHistoryDownloaded"], [True])

    def reset_daily_prices(self):
        """
        Clean up table so that can run daily price update again. Here, just reset the
        currentPriceDate to yesterday. Can't reset actual prices, as don't know what they
        were before the most recent update, and they will be overwritten by the next
        update anyway.
        """
        thisDate = date.today()
        query = "currentPriceDate = '%s'" % (thisDate,)
        fieldNames = ("currentPriceDate",)
        fieldValues = (thisDate - timedelta(1),)
        numUpdated = dbAccess.update_data(self.securitiesTable, fieldNames, fieldValues, query)
        print(f"securitiesInter.reset_daily_prices updated {numUpdated} records.")
