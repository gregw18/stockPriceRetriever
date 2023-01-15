"""
Class to contain endpoint for web page lambda.
Retrieves data for all securities, for requested period, returns to caller.
V0.01, October 7, 2022
"""

import json
import os
import sys

import boto3

import settings
import securities

client = boto3.client('lambda')
mysettings = settings.Settings.instance()

def get_test_data():
    mySecurities = []
    mySecurities.append(create_test_security(
        name = "AMAZON",
        currentPrice = 14.35,
        periodStartPrice = 65.06,
        periodHighPrice = 88.11,
        periodLowPrice = 13.23,
        buyPrice = 8.4,
        sellPrice = 50.3,
        periodPrices = [65.06, 67.45, 69.32, 70.45, 64.33, 54.33, 52.65, 55.43, 48.22]
    ))

    mySecurities.append(create_test_security(
        name = "Microsoft",
        currentPrice = 239.04,
        periodStartPrice = 283.11,
        periodHighPrice = 349.67,
        periodLowPrice = 235.2,
        buyPrice = 170.90,
        sellPrice = 274.70,
        periodPrices = [283.11, 349.67, 323.4, 334.3, 232.1, 240.3, 338.6, 235.4, 233.2]
    ))

 #   name = "AMAZON"
 #   currentPrice = 14.35
 #   periodStartPrice = 65.06
 #   periodHighPrice = 88.11
 #   periodLowPrix = 13.23
 #   buyPrice = 8.4
 #   sellPrice = 50.3
 #   periodPrices = [65.06, 67.45, 69.32, 70.45, 64.33, 54.33, 52.65]
 #   body = {
 #       "name": name,
 #       "currentPrice": currentPrice,
 #       "periodStartPrice": periodStartPrice,
 #       "periodHighPrice": periodHighPrice,
 #       "periodLowPrix": periodLowPrix,
 #       "buyPrice": buyPrice,
 #       "sellPrice": sellPrice,
 #       "periodPrices": periodPrices
 #   }

    print("mySecurities: ", mySecurities)

    return mySecurities

def create_test_security(name, currentPrice, periodStartPrice, periodHighPrice,
                         periodLowPrice, buyPrice, sellPrice, periodPrices):

    thisSecurity = {
        "name": name,
        "currentPrice": currentPrice,
        "periodStartPrice": periodStartPrice,
        "periodHighPrice": periodHighPrice,
        "periodLowPrice": periodLowPrice,
        "buyPrice": buyPrice,
        "sellPrice": sellPrice,
        "periodPrices": periodPrices
    }

    return thisSecurity

"""
def test_rds_connection():
    rds_endpoint = ""
    rds_user = ""
    rds_pass = ""
    db_name = "stock-prices"
    try:
        conn = pymysql.connect(host=rds_endpoint, user=rds_user, passwd=rds_pass,
            db=db_name, connect_timeout=5)
        print("Connection succeeded")
    except pymysql.MySQLError as e:
        print("Error, could not connect to MySQL database ", db_name)
        print(e)
"""

def lambda_handler(event, context):
    """
    Standard handler for AWS Lambda.
    V1 - returning hardcoded data.
    """
    #databaseUtils.test_rds_connection()
    return get_website_data(event, context)

def get_website_data(event, context):
    """
    Standard handler for AWS Lambda.
    V1 - returning hardcoded data.
    """
    print("Starting get_website_data Lambda")
    print('## ENVIRONMENT VARIABLES\r' + str(dict(**os.environ)))
    print('python version=', sys.version)
    print("cwd=", os.getcwd())
    print("event=", event)
    print("context=", context)
    print("event.timeframe=", event["queryStringParameters"]["timeframe"])

    #body = get_test_data()
    body = get_web_data(event["queryStringParameters"]["timeframe"])
    #print(f"get_website_data, {body = }")
    response = {
        "statusCode": 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        "body": json.dumps(body, default=str)
    }
    print("Finished get_website_data, response: " + json.dumps(response))

    return response

def get_web_data(timePeriod):
    """
    Return securities data for requested time period.
    """
    mySecurities = securities.Securities()
    myWebPriceInfos = mySecurities.get_web_data(timePeriod)
    webPriceInfosList = []
    for item in myWebPriceInfos:
        webPriceInfosList.append(item.getDict())

    return webPriceInfosList
