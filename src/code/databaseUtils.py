"""
Some miscellaneous database logic - structure/creation of tables, 
removing outdated price history
V0.01, November 9, 2022
"""

from datetime import datetime
import json
import os
import sys

import dbAccess
import settings
import utilsInterface

# Creating tables for storing security and price history data.
def create_tables():
    tables = _get_table_definitions()
    mySettings = settings.Settings.instance()

    myUtilsInter = utilsInterface.UtilsInterface()
    if myUtilsInter.connect():
        create_table_set(tables, "")
        create_table_set(tables, mySettings.test_table_prefix)
        myUtilsInter.disconnect()

def create_table_set(tables, prefix):
    """
    Create table set - either prod (no prefix) or test.
    """
    for table_name in tables:
        table_desc = tables[table_name]
        table_cmd = table_desc % (prefix + table_name,)
        print("Creating table: ", table_name, ", sql= ", table_cmd)
        if dbAccess.create_table(table_cmd):
            print("Successfully created table ", table_name)
        else:
            print("Error when creating table ", table_name)

def _get_table_definitions():
    """
    Table definitions.
    """
    tables = {}
    tables["securities"]= (
        "CREATE TABLE %s ("
        "   `id` MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT,"
        "   name VARCHAR(40) NOT NULL,"
        "   symbol VARCHAR(20) NOT NULL,"
        "   fullHistoryDownloaded BOOL, "
        "   buyPrice DECIMAL(10,2),"
        "   sellPrice DECIMAL(10,2),"
        "   currentPrice DECIMAL(10,2),"
        "   currentPriceDate DATE,"
        "   previousClosePrice DECIMAL(10,2),"
        "   52WeekHighPrice Decimal(10,2),"
        "   52WeekLowPrice Decimal(10,2),"
        "   percentChangeToday Decimal(6,2),"
        "   PRIMARY KEY (`id`),"
        "   INDEX symbolIdx(symbol)"
        ") ENGINE=InnoDB"
        )
    tables["dailyPriceHistory"] = (
        "CREATE TABLE %s ("
        "   `id` MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT,"
        "   securityId MEDIUMINT UNSIGNED,"
        "   price DECIMAL(10,2),"
        "   priceDate DATE,"
        "   PRIMARY KEY (`id`),"
        "   INDEX securityIdIdx(securityId),"
        "   INDEX priceDateIdx(priceDate)"
        ") ENGINE=InnoDB"
    )
    tables["weeklyPriceHistory"] = (
        "CREATE TABLE %s ("
        "   `id` MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT,"
        "   securityId MEDIUMINT UNSIGNED,"
        "   price DECIMAL(10,2),"
        "   priceDate DATE,"
        "   PRIMARY KEY (`id`),"
        "   INDEX securityIdIdx(securityId),"
        "   INDEX priceDateIdx(priceDate)"
        ") ENGINE=InnoDB"
    )
    tables["admin"] = (
        "CREATE TABLE `%s` ("
        "   `id` MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT,"
        "   lastWeeklyPriceUpdate DATE,"
        "   lastGroomRun DATE,"
        "   PRIMARY KEY (`id`)"
        ") ENGINE=InnoDB"
    )

    return tables
