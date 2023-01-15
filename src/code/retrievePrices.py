"""
Retrieving prices, for stock price retriever.
V0.02, February 28, 2021, GAW.
"""

import datetime
import json
import socket
import time

import urllib3
import requests

import security
from securities import Securities
import stockTarget
from sprEnums import PriceProvider
import yahooInterface

def _get_price_alphavest(symbol, mysettings):
    """
    Return current price for given stock, 0 if hit an error.
    Note that am using alphavantage.co's api to retrieve prices. Has a limit of 5 requests per
    minute (and 500 per day) on the free tier, so am waiting 20s before each call, to stay legal.
    Also note that appears that if request a symbol that they don't recognize, they return
    an empty Global Quote object.
    Getting pricing from alphavest doesn't currently work, because the GLOBAL_QUOTE method
    doesn't return the 52 week range. Have hidden this option, may eventually try to find
    another method that returns everything I need.
    """
    time.sleep(mysettings.alphaCallDelay)
    price = 0
    try:
        reqParams = {'function': 'GLOBAL_QUOTE',
                     'symbol': symbol,
                     'apikey': mysettings.alphaApiKey,
                     'datatype': 'json'}
        r = requests.get(mysettings.alphaBaseUrl,
                         params=reqParams,
                         timeout=mysettings.alphaApiTimeOut)
        if r.ok:
            try:
                with open(symbol + ".json", 'w') as f:
                    json.dump(r.json(), f)

                price = r.json()[mysettings.respContName][mysettings.priceName]
            except (NameError, KeyError) as E:
                print("Couldn't find price element for ", symbol)
                print("E: ", E)
        else:
            print(r.ok, r.reason, r.request, r.status_code, r.text)
    except (ConnectionError,
            urllib3.exceptions.MaxRetryError,
            urllib3.exceptions.NewConnectionError,
            socket.timeout,
            NameError,
            requests.exceptions.ReadTimeout) as E:
        print("Failed to retrieve price for ", symbol)
        print(E)

    return float(price)

def retrieve_prices_using_db():
    """
    Retrieve and store daily/weekly prices, using list from database.
    """
    #myUtilsInter = UtilsInterface()
    mySecurities = Securities()

    #myUtilsInter.connect()
    numUpdates = mySecurities.do_daily_updates()
    print(f"retrieve_price_using_db resulted in {numUpdates} securities being updated.")
    #numUpdated = mySecurities.do_daily_price_update(datetime.date.today())
    #mySecurities.do_maintenance()
    #myUtilsInter.disconnect()

def retrieve_prices_from_file(excelFile,
                              excelTabName,
                              priceProvider,
                              mysettings,
                              myResultsFile):
    """
    Get list of securities that want to retrieve prices for.
    """
    print("in retrieve_and_show_prices")
    myList = stockTarget.StockTarget()
    symbolList = myList.get_list(excelFile, excelTabName)

    resFile = retrieve_prices(symbolList, priceProvider, mysettings, myResultsFile)

    return resFile


def retrieve_prices(symbolList, priceProvider, mysettings, myResultsFile):
    """
    Retrieve price for each symbol in list, using given function, save in a file.
    Returns name of file created.
    """

    if priceProvider == PriceProvider.alphavest:
        retrieveFn = _get_price_alphavest
    elif priceProvider == PriceProvider.yahoo:
        retrieveFn = yahooInterface.retrieve_daily_data
    else:
        print("Unrecognized price provider: ", priceProvider, ", using AlphaVest.")
        retrieveFn = _get_price_alphavest

    # Loop through all securities in list, getting and checking current price.
    securities = []
    for symbol in symbolList:
        print(symbol.Stock)
        priceInfo = retrieveFn(symbol.Symbol, mysettings)
        mySecurity = security.Security()
        mySecurity.pop_from_row(symbol, priceInfo)
        if priceInfo.currentPrice > 0:
            actionMsg = _get_action_msg(symbol, priceInfo.currentPrice)
            _display_msg(symbol, priceInfo.currentPrice, actionMsg)
            # Don't write to file if no price, as resulting bar makes it look like should buy.
            securities.append(mySecurity)

    # Save list to file/s3.
    # resFile = myResultsFile.write_results_file(securities, datetime.datetime.now())
    resFile = myResultsFile.write_results_s3(securities, datetime.datetime.now())

    return resFile


def _get_action_msg(symbol, price):
    """
    Return string containing what we should do for this security.
    """
    displayMsg = "Within range "
    if price < symbol.Buy_price:
        displayMsg = "*** Buy "
    elif price > symbol.Sell_price:
        displayMsg = "*** Sell "
    return displayMsg


def _display_msg(row, price, msg):
    """
    Display message for given stock.
    """
    print(msg, row.Stock,
          ", current price: ", price,
          ", buy price: ", row.Buy_price,
          ", sell price: ", row.Sell_price)
