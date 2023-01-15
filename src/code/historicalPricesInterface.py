"""
Interface between securities/security and dbAccess for historical prices. Should contain no
business logic. Should not communicate directly with mySql.
V0.01, November 24, 2022
"""

from datetime import date, timedelta

import dbAccess
import settings


class HistoricalPricesInterface:

    def __init__(self):
        self.settings = settings.Settings.instance()
        self.dailyPricesTable = self.settings.db_daily_table_name
        self.weeklyPricesTable = self.settings.db_weekly_table_name
        self.fieldNames = ["id", "securityId", "priceDate", "price"]

    def save_daily_price_for_security(self, securityId, securityPrice, priceDate):
        """
        Add given price to daily price table.
        """
        return self._save_historical_prices(securityId,
                                            [(priceDate, securityPrice),],
                                            self.dailyPricesTable)

    def save_weekly_price_for_security(self, securityId, priceDate):
        """
        I am defining the weekly price as the closing price on Friday, even if Friday
        isn't a trading day. Function takes price for given security on given day from
        daily price table, adds record with that price and date to weekly price table.
        """
        params = (securityId, priceDate, securityId, priceDate)
        query = f"INSERT INTO {self.weeklyPricesTable} "
        query += "(securityId, priceDate, price) "
        query += "VALUES (%s, %s, "
        query += f"(SELECT price FROM {self.dailyPricesTable} "
        query += "WHERE securityId=%s AND priceDate=%s)) "

        return dbAccess.execute_update_data(query, params)

    def save_daily_historical_prices(self, securityId, datePricePairs):
        """
        Add record to daily price table for each date/price pair.
        """
        return self._save_historical_prices(securityId, datePricePairs, self.dailyPricesTable)

    def save_weekly_historical_prices(self, securityId, datePricePairs):
        """
        Add record to weekly price table for each date/price pair.
        """
        return self._save_historical_prices(securityId, datePricePairs, self.weeklyPricesTable)

    def get_historical_prices(self, securityId, tableName, maxAge):
        """
        Retrieve prices for requested security, for requested window of time.
        """
        dateThresh = date.today() - timedelta(days = maxAge)
        fields = ["priceDate", "price"]
        query = "securityId = %s AND  priceDate >= %s"
        records = dbAccess.select_data(tableName, fields, query, [securityId, dateThresh])

        return records

    def remove_old_prices(self, tableName, dateThreshold):
        """
        Remove prices older or equal to given threshold.
        """
        query = "priceDate <= %s"
        params = (dateThreshold,)
        return dbAccess.delete_data(tableName, query, params)

    def delete_security(self, securityId):
        """
        Delete all historical prices for given security.
        """
        query = "securityId = %s"
        params = (securityId,)
        numDeleted = dbAccess.delete_data(self.dailyPricesTable, query, params)
        numDeleted += dbAccess.delete_data(self.weeklyPricesTable, query, params)

        return numDeleted

    def reset_daily_prices(self):
        """
        Clean up tables so that daily price update can run again - delete any daily
        or weekly prices with today's date.
        """
        thisDate = date.today()
        query = "priceDate = %s"
        params = (thisDate,)
        dbAccess.delete_data(self.dailyPricesTable, query, params)
        dbAccess.delete_data(self.weeklyPricesTable, query, params)

    def _save_historical_prices(self, securityId, pricePairs, tableName):
        """
        Converts data to appropriate format for inserts, adds records to given table.
        """
        fieldNames = ["securityId", "priceDate", "price"]
        fieldValues = []
        for priceDate, price in pricePairs:
            fieldValues.append((securityId, priceDate, price))

        if len(fieldValues) > 0:
            savedOk = dbAccess.insert_data(tableName, fieldNames, fieldValues)
            print(f"_save_historical_prices on table {tableName} gave a result of {savedOk}")
        else:
            savedOk = False
            print("_save_historical_prices had no data to save.")

        return savedOk
