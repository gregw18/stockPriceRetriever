"""
Stock price retriever.
V0.01, February 25, 2019, GAW.
Retrieves list of stocks, targeted buy/sell prices from spreadsheet.
For each stock, retrieve current price. Display message if price is
below buy target or above sell target.
If receives -l option, tries to look up provided text's symbol (data
provider uses unusual and unlisted symbols for many Canadian securities.)
Put quotes around provided search terms so that they aren't considered
separate arguments. i.e. "python3 spr.py -l 'pump and dumps r us'".

V0.02, February 26, 2019, GAW.
Added -l option to look up symbol.

V0.03, February 26, 2019, GAW
Added -g option to graph results. Required adding ability to save results, read them back in.
"""


import json
import math
import sys
import socket

import matplotlib.pyplot as plt
import requests

import daily_email
import databaseUtils
from progArgs import ProgArgs
import resultsFile
import retrievePrices
import securities
import security_groups
import settings
from sprEnums import Action
import stockTarget
import utilsInterface


def set_axes_properties(ax, sec, graphData):
    """
    Set axes properties to display info for given security.
    """

    # Need to offset bars based on where x axis starts.
    xStart = graphData.offset
    mySym = sec.symbol
    ax.barh(mySym, graphData.buyWid, color='red', height=2, left=xStart)
    ax.barh(mySym, graphData.noActionWid, color='green', height=2, left=xStart + graphData.buyWid)
    ax.barh(mySym,
            graphData.sellWid,
            color='yellow',
            height=2,
            left=xStart + graphData.buyWid + graphData.noActionWid)
    # ax.set_ylabel(sec.name)
    ax.vlines(graphData.priceLinePos, -2, 2)
    ax.set_xbound(graphData.xBounds)


def display_graphs(fileName, tmpResultsFile):
    """
    Display a graph for each group of securities. Can only fit a limited number on each graph,
    so now displaying multiple graphs. Size defined by numCols and maxRows.
    """

    # secList = myResultsFile.read_results_file(fileName)
    secList = tmpResultsFile.read_results_file_s3(fileName)
    numSecurities = len(secList)
    if numSecurities > 0:
        # Get resorted version from security_groups.
        myGroups = security_groups.SecurityGroups()
        secList = myGroups.get_sorted_list(secList)

        numCols = 3
        maxRows = 10
        graphSize = numCols * maxRows

        for graphNum in range(0, numSecurities, graphSize):
            nextBatch = get_next_batch(secList, graphNum, graphSize)
            graph(nextBatch, numCols)

    else:
        print("Unable to read any records from file: ", fileName)


def get_next_batch(secList, graphNum, graphSize):
    """
    Return array containing next batch of up to graphSize elements, from secList array,
    starting at graphNum.
    """
    if ((graphNum + 1) + graphSize) > len(secList):
        return secList[graphNum:]
    else:
        return secList[graphNum:(graphNum + graphSize)]


def graph(secList, numCols):
    """
    Display bar graph for each security, in given list. Putting three graphs side by side,
    as they are rather small when all in one column.
    """

    numSecurities = len(secList)
    numRows = math.ceil(numSecurities/numCols)

    # Stupid logic - if ask for 1 row and y columns from plt.subplots, get axes.shape=(y,),
    # not (1,y). Thus, my kludge is to ask for a minimum of 2 rows, end up with empty
    # row sometimes.
    if numRows == 1:
        numRows = 2
    # print("numSec: ", numSecurities, ", numRows: ", numRows)

    # Create subplots to fit in all the securities
    fig, axes = plt.subplots(nrows=numRows, ncols=numCols)
    # print("shape(axes)=", axes.shape)

    # Set up "axes" for each security.
    for rowNum in range(0, numRows):
        for colNum in range(0, numCols):
            # First, make sure that we haven't run out of securities.
            securityNum = (rowNum * numCols) + colNum
            # print("row=", rowNum, ", col=", colNum, ", securityNum=", securityNum)
            if securityNum < numSecurities:
                graphData = secList[securityNum].get_graph_data()
                set_axes_properties(axes[rowNum, colNum], secList[securityNum], graphData)

    plt.subplots_adjust(left=0.1, right=0.95, bottom=0.05, top=0.95, wspace=0.2, hspace=0.4)
    plt.show(block=True)


def symbol_lookup(searchText, alphaApiKey, alphaBaseUrl, alphaApiTimeOut):
    """
    Use AlphaVest's Symbol_Search endpoint to try to find symbol for given search text.
    (Their symbols are rather nonstandard, especially for non-US securities.)
    """
    try:
        reqParams = {'function': 'SYMBOL_SEARCH',
                     'keywords': searchText,
                     'apikey': alphaApiKey,
                     'datatype': 'json'}
        r = requests.get(alphaBaseUrl, params=reqParams, timeout=alphaApiTimeOut)
        print("response code: ", r.status_code)
        print("url: ", r.url)
        if r.ok:
            with open("searchResult.json", 'w') as f:
                json.dump(r.json(), f)
        else:
            print(r.ok, r.reason, r.request, r.status_code, r.text)
    except (ConnectionError, socket.timeout, NameError) as E:
        print("Failed to retrieve search results for '", searchText, "'")
        print(E)

def _load_new_file(srcFile, srcTab):
    """
    Update securities list with contents of given file.
    """
    # Read in contents of file.
    myList = stockTarget.StockTarget()
    # newTargets = myList.get_list(srcFile, srcTab)
    newTargets = myList.read_target_securities(srcFile, srcTab)

    if len(newTargets) > 0:
        myUtilsInter = utilsInterface.UtilsInterface()
        print("_load_new_file about to connect.")
        myUtilsInter.connect()
        print("_load_new_file about to init securities.")

        mySecurities = securities.Securities()
        print("_load_new_file about to mysecurities.load")
        mySecurities.load()
        print("_load_new_file about to loadNewList.")
        mySecurities.loadNewList(newTargets)
        print("_load_new_file about to disconnect.")

        myUtilsInter.disconnect()
        print(f"Successfully read in {len(newTargets)} securities.")
    else:
        print(f"Failed to read any securities from file {srcFile}, tab {srcTab}")

def _reset_daily_prices():
    """
    Reset database so that daily price update will run again, without duplicating
    any records.
    """
    mySecs = securities.Securities()
    mySecs.reset_daily_prices()

def display_help():
    """
    Display help message.
    """
    print("Expect either 0, 1, 2 or 4 arguments:")
    # Not showing this option as it requires an AlphaVest api key.
    # print("\t-l 'stock name' to look up a symbol,")
    print("\t-e to retrieve prices and send email, for symbols in database.")
    print("\t-g 'filename' to display results from a file,")
    print("\t-f 'filename' to retrieve and display results for symbols in a file.")
    print("\t-d to create or update structure of tables in database.")
    print("\t-o 'filename' to load a new set of securities from specified excel file.")
    print("\t-r to retrieve latest prices for symbols in database.")
    print("\t-c to clear any prices that were updated today, so can re-run daily price update.")
    # Not showing this option as it requires an AlphaVest api key.
    # print("\t-p yahoo/alpha to specify which provider to retrieve prices from.")
    print("\t-n no display - don't display graphs after retrieving prices.")
    print("\t-h display this help information.")
    print("0 arguments results in retrieving results for symbols in the default")
    print("file 'Portfolio.xls' in the default 'Current' tab.")
    print("If 1 argument is provided it is assumed to be the name of the file containing symbols ")
    print("to retrieve prices for.")


if __name__ == "__main__":
    """
    Do price lookup, unless given -l option, in which case want to do symbol lookup.
    """
    print("argv: ", sys.argv, ", len=", len(sys.argv))

    myArgs = ProgArgs()
    mysettings = settings.Settings.instance()
    myArgs.parse_args(sys.argv, mysettings.srcFile, mysettings.srcTab)

    if myArgs.action == Action.help:
        display_help()
    elif myArgs.action == Action.lookup:
        symbol_lookup(myArgs.symbol,
                      mysettings.alphaApiKey,
                      mysettings.alphaBaseUrl,
                      mysettings.alphaApiTimeOut)
    elif myArgs.action == Action.graph:
        myResultsFile = resultsFile.ResultsFile(mysettings.bucketName, mysettings.resultsPrefix)
        display_graphs(myArgs.srcFile, myResultsFile)
    elif myArgs.action == Action.retrieveDb:
        retrievePrices.retrieve_prices_using_db()
    elif myArgs.action == Action.clearDaily:
        _reset_daily_prices()
    elif myArgs.action == Action.dailyEmail:
        daily_email.send_from_db(mysettings.resultsTopicName, mysettings.websiteUrl)
    elif myArgs.action == Action.retrieve:
        myResultsFile = resultsFile.ResultsFile(mysettings.bucketName, mysettings.resultsPrefix)
        res_file = retrievePrices.retrieve_prices_from_file(myArgs.srcFile,
                                                            myArgs.srcTab,
                                                            myArgs.priceProvider,
                                                            mysettings,
                                                            myResultsFile)
        if myArgs.display:
            display_graphs(res_file, myResultsFile)
    elif myArgs.action == Action.loadNew:
        _load_new_file(myArgs.srcFile, myArgs.srcTab)
    elif myArgs.action == Action.createDb:
        databaseUtils.create_tables()
    else:
        print("Unrecognized action: ", myArgs.action)
