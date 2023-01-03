"""
Group and sort security_ratings.
V0.01, October 21, 2020
"""

#from decimal import Decimal

import security_rating
import sprEnums


class security_groups:
    """
    Class to create group a list of securities, with buy/sell/current prices, into buy, sell,
    near-buy, near-sell and middle groups, all sorted (furthest to least from buy/sell price,
    closest to furthest from buy/sell price, percent of range if middle.
    Includes logic to classify a given security into the appropriate group and then calculate
    the appropriate rating.
    """

    def __init__(self):
        #
        self.groups = {}

        self.rating_methods = {}
        self.rating_methods[sprEnums.GroupCodes.buy] = self._calc_rating_buy
        self.rating_methods[sprEnums.GroupCodes.near_buy] = self._calc_rating_middle
        self.rating_methods[sprEnums.GroupCodes.middle] = self._calc_rating_middle
        self.rating_methods[sprEnums.GroupCodes.near_sell] = self._calc_rating_middle
        self.rating_methods[sprEnums.GroupCodes.sell] = self._calc_rating_sell

        # Should group be sorted forward (false) or reverse (true)?
        # For buy, sell lists, want to see members furthest from middle first,
        # so descending for buy, descending for sell. For near buy/sell, want to see members
        # closest to edges first, so ascending for near_buy, descending for near_sell. For middle,
        # no real preference, going with ascending.
        # Actually, changed mind, would like to see entire list in order, from biggest buy to
        # biggest sell. Thus, believe that only buy should be reversed.
        self.sort_reverse = {}
        self.sort_reverse[sprEnums.GroupCodes.buy] = True
        self.sort_reverse[sprEnums.GroupCodes.near_buy] = False
        self.sort_reverse[sprEnums.GroupCodes.middle] = False
        self.sort_reverse[sprEnums.GroupCodes.near_sell] = False
        self.sort_reverse[sprEnums.GroupCodes.sell] = False

        self.group_text = {}
        self.group_text[sprEnums.GroupCodes.buy] = "1.buy"
        self.group_text[sprEnums.GroupCodes.near_buy] = "2.near buy"
        self.group_text[sprEnums.GroupCodes.middle] = "3.middle"
        self.group_text[sprEnums.GroupCodes.near_sell] = "4.near sell"
        self.group_text[sprEnums.GroupCodes.sell] = "5.sell"

    def populate(self, securitiesList):
        """
        Group given securities into groups, calculate rating for each security,
        sort each group.
        """
        # Clear out groups, create empty list for each group. (groups is a dict,
        # key = group code, val = list of security_ratings belonging to that group.)
        self.groups = {}
        for group in sprEnums.GroupCodes:
            self.groups[group] = []

        # Classify each security into the appropriate group, calculate the rating for it,
        # create a security_rating for it and add it to the appropriate group.
        for security in securitiesList:
            if security.symbol:
                thisGroup = self._get_group_code(security)
                thisRating = self.rating_methods[thisGroup](security)
                my_sec_rating = security_rating.security_rating()
                my_sec_rating.set_rating(security, thisRating)
                self.groups[thisGroup].append(my_sec_rating)

    def get_results_for_group(self, group_code):
        """
        Returns sorted list of securities for requested group.
        """
        self.groups[group_code].sort(key=lambda x: x.rating, reverse=self.sort_reverse[group_code])
        return self.groups[group_code]

    def get_sorted_list(self, orig_sec_list):
        """
        Sorts given securities list into a new one, from buy to sell.
        """
        self.populate(orig_sec_list)
        new_sec_list = []
        for groupCode in sprEnums.GroupCodes:
            for rating in self.get_results_for_group(groupCode):
                new_sec_list.append(rating.security)
        return new_sec_list

    def get_values_for_webPriceInfo(self, myWebInfo):
        """
        Calculates group and rating for given webPriceInfo.
        Saves group as text. Saves rating as negative number if in buy zone,
        so that when sort by rating get desired order.
        """
        rating = 0
        group = ""

        group_code = self._get_group_code(myWebInfo)
        group = self._get_group_text(group_code)
        rating = round(100 * self.rating_methods[group_code](myWebInfo), 2)
        if group_code == sprEnums.GroupCodes.buy:
            rating = 0 - rating

        return rating, group

    def _calc_rating_buy(self, this_security):
        """
        Calculate rating for securities in the buy zone: (buy - current) / buy
        Basically, percentage below buy price.
        """
        return (this_security.buyPrice - this_security.currentPrice) / this_security.buyPrice

    def _calc_rating_middle(self, this_security):
        """
        Calculate rating for securities in the middle zone: (current - buy) / (sell - buy)
        Basically, percentage of buy/sell range above buy.
        """
        return ((this_security.currentPrice - this_security.buyPrice) /
                (this_security.sellPrice - this_security.buyPrice))

    def _calc_rating_sell(self, this_security):
        """
        Calculate rating for securities in the sell zone: (current - sell) / sell
        Basically, percentage above sell price.
        """
        return (this_security.currentPrice - this_security.sellPrice) / this_security.sellPrice

    def _get_group_code(self, this_security):
        """
        Decide which group this security belongs in:
          If below buy price, buy
          If < 25% into buy-sell range, near buy
          If > sell price, sell
          If > 75% into buy-sell range, near sell
          Otherwise, middle
        """
        middle_range = float(this_security.sellPrice - this_security.buyPrice)
        if this_security.currentPrice < this_security.buyPrice:
            myGroup = sprEnums.GroupCodes.buy
        elif this_security.currentPrice - this_security.buyPrice < (.25 * middle_range):
            myGroup = sprEnums.GroupCodes.near_buy
        elif this_security.currentPrice > this_security.sellPrice:
            myGroup = sprEnums.GroupCodes.sell
        elif this_security.currentPrice - this_security.buyPrice > (0.75 * middle_range):
            myGroup = sprEnums.GroupCodes.near_sell
        else:
            myGroup = sprEnums.GroupCodes.middle
        return myGroup

    def _get_group_text(self, group_code):
        """
        Convert from group code to text.
        """
        text = "unknown"

        if group_code in self.group_text:
            text = self.group_text[group_code]

        return text

    def print_groups(self):
        """
        Print list of symbols in each group.
        """
        for group, ratings in self.groups.items():
            print("\n", group, ": ", end="")
            for rating in ratings:
                print(rating.security.symbol, ":", rating.rating, ", ", end="")
