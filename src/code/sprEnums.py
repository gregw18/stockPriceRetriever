"""
Enums for stock price retriever.
v0.01, September 2, 2020
"""

from enum import Enum


class Action(Enum):
    """
    List of actions that program supports. Most can only be used from command line.
    """
    help = 1
    lookup = 2          # Symbol lookup
    graph = 3           # Display prices
    retrieve = 4        # Retrieve and display prices
    createDb = 5        # Create or update structure of tables.
    loadNew = 6         # Load new list of securities from excel file
    retrieveDb = 7      # Retrieve prices for symbols in database
    clearDaily = 8      # Reset database so can re-run daily price ipmort.
    dailyEmail = 9      # Download prices and send email.

class PriceProvider(Enum):
    """
    List of providers that we can get prices from.
    """
    alphavest = 1
    yahoo = 2


class GroupCodes(Enum):
    """
    Codes for security groups.
    """
    buy = 1
    near_buy = 2
    middle = 3
    near_sell = 4
    sell = 5

class timePeriods(Enum):
    """
    Time periods that can request data for, along with number of days in each period.
    """
    day = 1
    days30 = 30
    months3 = 31 * 3
    years1 = 365 * 1
    years3 = 365 * 3
    years5 = 365 * 5

def get_timePeriod_from_text(timeDesc):
    """
    Convert string describing time period to appropriate enum member.
    """
    conversions = {}
    conversions["1day"] = timePeriods.day
    conversions["30days"] = timePeriods.days30
    conversions["3months"] = timePeriods.months3
    conversions["1year"] = timePeriods.years1
    conversions["3years"] = timePeriods.years3
    conversions["5years"] = timePeriods.years5

    timePeriod = timePeriods.days30
    if timeDesc in conversions:
        timePeriod = conversions[timeDesc]
    else:
        print(f"sprEnums.get_member_from_text received unknown timeDesc: {timeDesc}")

    return timePeriod
