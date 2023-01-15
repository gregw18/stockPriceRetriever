"""
Retrieving data from yahoo
V0.01, December 7, 2022, GAW.
"""

import math
import sys
import time
from urllib.error import HTTPError

from yahoo_fin.stock_info import get_quote_table, get_data

import security

def retrieve_daily_data(symbol, mysettings):
    """
    Return current price for given stock, 0 if hit an error.
    Note that am using Yahoo Finance to retrieve prices.
    Also note that appears that if request a symbol that they don't recognize, they return
    an empty Global Quote object.
    """
    time.sleep(mysettings.yahooCallDelay)
    yahooSymbol = get_yahoo_ticker(symbol)
    priceInfo = security.PriceInfo()

    # Try up to three times if fail.
    for i in range(0, 3):
        try:
            quote_table = get_quote_table(yahooSymbol)
            priceInfo.currentPrice = round(float(quote_table['Quote Price']), 2)
            priceInfo.lastClosePrice = round(float(quote_table['Previous Close']), 2)
            low, high = _split_price_range(quote_table['52 Week Range'])
            priceInfo.low52Week = low
            priceInfo.high52Week = high
            break
        except (ValueError, IndexError, ImportError, HTTPError) as E:
            print("retrieve_daily_data failed to retrieve price for ", yahooSymbol)
            print(f"{E=}")
            if E.args[0] == "No tables found" or E.args[0] == "list index out of range":
                break
            E = sys.exc_info()[0]
            print(f"exc_info, {E=}")

    return priceInfo

def retrieve_historical_prices(symbol, oldestDate, newestDate, priceFrequency):
    """
    Retrieve historical prices for requested symbol, over requested time period,
    at requested frequency. Frequency should be 1d for daily or 1w for weekly.
    Note that weekly prices appear to return closing price for Monday, rather than
    Friday, which I thought would be a more natural day to end the week.
    Also, it will return the weekly price for any week covered by the time period,
    even if the time period doesn't include the Monday. I.e. if, on a Tuesday, ask for
    last 5 days, will get the price for the previous day plus the price for the previous
    Monday, as the interval includes the thursday and Friday from the previous week.
    Returns list of date/price pairs.
    """
    yahooSymbol = get_yahoo_ticker(symbol)
    srcData = None
    for i in range(0, 2):
        try:
            srcData = get_data(yahooSymbol, start_date = oldestDate,
                               end_date = newestDate, interval = priceFrequency)
            break
        except (AssertionError, KeyError) as E:
            # Generally means symbol not found, so no point retrying.
            print("retrieve_historical_prices failed to retrieve price for ", yahooSymbol)
            print(f"{E=}")
            E = sys.exc_info()[0]
            print(f"exc_info, {E=}")
            break
        except (IndexError, ImportError, HTTPError) as E:
            print("retrieve_historical_prices failed to retrieve price for ", yahooSymbol)
            print(E)
            E = sys.exc_info()[0]
            print(E)

    pairs = []
    if not (srcData is None):
        for dateVal in srcData.index:
            # If the Monday is a holiday, interface appears to return a record, but
            # with nan as the value - don't want to save.
            if not (math.isnan(srcData.adjclose[dateVal])):
                pairs.append((dateVal, srcData.adjclose[dateVal]))
        print(f"retrieve_historical_prices is returning {len(pairs)} prices.")

    return pairs

def get_yahoo_ticker(symbol):
    """
    Convert from Alphavest symbol to Yahoo symbol.
    First conversion: For TSX stocks, from TSX:xxx to xxx.TO
    Second conversion: For TSX ETFs, from xxx.TRT to xxx.TO
    """
    yTicker = symbol
    if symbol[0:4] == "TSX:":
        yTicker = symbol[4:] + ".TO"
    elif symbol[-4:] == ".TRT":
        yTicker = symbol[0:-4] + ".TO"

    return yTicker


def _split_price_range(priceRangeStr):
    """
    Given a 52-week price range, in the format '99.99 - 99.99', where 99.99 can be any reasonable
    stock price, return the low and high prices as floats.
    Remove commas so that conversion to float will work when price > 999.99.
    """
    cleanStr = priceRangeStr.replace(",", "")
    split_pos = cleanStr.find('-')
    low = round(float(cleanStr[0:split_pos]), 2)
    high = round(float(cleanStr[split_pos + 1:]), 2)

    return low, high
