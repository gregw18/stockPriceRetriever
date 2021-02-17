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
