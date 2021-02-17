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

import resultsFile
import retrievePrices
from progArgs import ProgArgs
from sprEnums import Action
import security_groups
import settings


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


def display_graphs(fileName, myResultsFile):
    """
    Display a graph for each group of securities. Can only fit a limited number on each graph,
    so now displaying multiple graphs. Size defined by numCols and maxRows.
    """

    # secList = myResultsFile.read_results_file(fileName)
    secList = myResultsFile.read_results_file_s3(fileName)
    numSecurities = len(secList)
    if numSecurities > 0:
        # Get resorted version from security_groups.
        myGroups = security_groups.security_groups()
        secList = myGroups.get_sorted_list(secList)

        numCols = 3
        maxRows = 10
        graphSize = numCols * maxRows

        for graphNum in range(0, numSecurities, graphSize):
            # Make sure we don't go past end of list.
            if ((graphNum + 1) * graphSize) > numSecurities:
                graph(secList[graphNum:], numCols)
            else:
                graph(secList[graphNum:(graphNum + graphSize)], numCols)

    else:
        print("Unable to read any records from file: ", fileName)


def graph(secList, numCols):
    """
    Display bar graph for each security, in given list. Putting three graphs side by side,
    as they are rather small when all in one column.
    """

    numSecurities = len(secList)
    numRows = math.ceil(numSecurities/numCols)

    # Stupid logic - if ask for 1 row and y columns from plt.subplots, get axes.shape=(y,),
    #  not (1,y). Thus, my kludge is to ask for a minimum of 2 rows, end up with empty
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


def symbol_lookup(searchText):
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


def display_help():
    """
    Display help message.
    """
    print("Expect either 0, 1, 2 or 4 arguments:")
    print("\t-l 'stock name' to look up a symbol,")
    print("\t-g 'filename' to display results from a file,")
    print("\t-f 'filename' to look up and display results for symbols in a file.")
    print("\t-p yahoo/alpha to specify which provider to retrieve prices from.")
    print("\t-n no display - don't display graphs after retrieving prices.")
    print("\t-h display this help information.")
    print("0 arguments results in looking up results for symbols in the default")
    print("file 'Portfolio (copy).xls' in the default '2018' tab.")
    print("If 1 argument is provided it is assumed to be the name of the file containing symbols ")
    print("to retrieve prices for.")


if __name__ == "__main__":
    """
    Do price lookup, unless given -l option, in which case want to do symbol lookup.
    """
    print("argv: ", sys.argv, ", len=", len(sys.argv))

    myArgs = ProgArgs()
    myArgs.parse_args(sys.argv, settings.srcFile, settings.srcTab)

    if myArgs.action == Action.help:
        display_help()
    elif myArgs.action == Action.lookup:
        symbol_lookup(myArgs.symbol)
    elif myArgs.action == Action.graph:
        mysettings = settings.Settings()
        myResultsFile = resultsFile.ResultsFile(mysettings.bucketName, mysettings.resultsPrefix)
        display_graphs(myArgs.srcFile, myResultsFile)
    elif myArgs.action == Action.retrieve:
        mysettings = settings.Settings()
        myResultsFile = resultsFile.ResultsFile(mysettings.bucketName, mysettings.resultsPrefix)
        res_file = retrievePrices.retrieve_prices_from_file(myArgs.srcFile,
                                                            myArgs.srcTab,
                                                            myArgs.priceProvider,
                                                            mysettings,
                                                            myResultsFile)
        if myArgs.display:
            display_graphs(res_file, myResultsFile)
    else:
        print("Unrecognized action: ", myArgs.action)
