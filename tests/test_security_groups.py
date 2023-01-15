"""
File to test security_groups class
V0.01, October 21, 2020, GAW
"""

from decimal import Decimal
import pytest

from . import addSrcToPath

import security
import security_groups
import sprEnums


@pytest.mark.unit
class Test_security_groups:
    def setup_method(self):
        self.groups = security_groups.SecurityGroups()

    def createSecurity(self, name, symbol, buyPrice, sellPrice, currentPrice):
        mySec = security.Security()
        mySec.pop(name, symbol, buyPrice, sellPrice, currentPrice)
        return mySec

    def test_single_buy(self):
        """
        Test that get one security in buy group.
        """
        secList = []
        buySec = self.createSecurity("SUNCOR", "SU", 30, 60, 28)
        secList.append(buySec)

        self.groups.populate(secList)

        buys = self.groups.get_results_for_group(sprEnums.GroupCodes.buy)

        assert len(buys) == 1
        assert buys[0].rating == 1/15
        assert buys[0].security.symbol == "SU"

    def test_single_near_buy(self):
        """
        Test that get one security in near_buy group.
        """
        secList = []
        buySec = self.createSecurity("SUNCOR", "SU", 30, 60, 37)
        secList.append(buySec)

        self.groups.populate(secList)

        near_buys = self.groups.get_results_for_group(sprEnums.GroupCodes.near_buy)

        assert len(near_buys) == 1
        assert near_buys[0].rating == 7/30
        assert near_buys[0].security.symbol == "SU"

    def test_single_near_sell(self):
        """
        Test that get one security in near_sell group.
        """
        secList = []
        buySec = self.createSecurity("SUNCOR", "SU", 30, 60, 53)
        secList.append(buySec)

        self.groups.populate(secList)

        near_sells = self.groups.get_results_for_group(sprEnums.GroupCodes.near_sell)

        assert len(near_sells) == 1
        assert round(near_sells[0].rating, 2) == round(23/30, 2)
        assert near_sells[0].security.symbol == "SU"

    def test_single_sell(self):
        """
        Test that get one security in sell group.
        """
        secList = []
        buySec = self.createSecurity("SUNCOR", "SU", 30, 60, 146)
        secList.append(buySec)

        self.groups.populate(secList)

        sells = self.groups.get_results_for_group(sprEnums.GroupCodes.sell)

        assert len(sells) == 1
        assert round(sells[0].rating, 2) == round(86/60, 2)
        assert sells[0].security.symbol == "SU"
        assert len(self.groups.get_results_for_group(sprEnums.GroupCodes.buy)) == 0

    def test_overlap_middle(self):
        """
        Test that get one security in middle group, when have tight range.
        """
        secList = []
        buySec = self.createSecurity("SUNCOR", "SU", 10, 12, 11)
        secList.append(buySec)

        self.groups.populate(secList)

        middles = self.groups.get_results_for_group(sprEnums.GroupCodes.middle)

        assert len(middles) == 1
        assert round(middles[0].rating, 2) == 1/2
        assert middles[0].security.symbol == "SU"
        assert len(self.groups.get_results_for_group(sprEnums.GroupCodes.buy)) == 0

    def test_overlap_near_sell(self):
        """
        Test that get one security in near_sell group, when have tight range.
        """
        secList = []
        buySec = self.createSecurity("SUNCOR", "SU", 10, 12, 11.6)
        secList.append(buySec)

        self.groups.populate(secList)

        results = self.groups.get_results_for_group(sprEnums.GroupCodes.near_sell)

        assert len(results) == 1
        assert round(results[0].rating, 2) == 1.6/2
        assert results[0].security.symbol == "SU"
        assert len(self.groups.get_results_for_group(sprEnums.GroupCodes.buy)) == 0

    def test_buy_sort(self):
        """
        Test that get expected order in buy group.
        """
        secList = []
        buySec = self.createSecurity("SUNCOR", "SU", 30, 60, 28)
        secList.append(buySec)
        buySec = self.createSecurity("TD", "TD", 30, 60, 8)
        secList.append(buySec)
        buySec = self.createSecurity("Manulife", "MFC", 30, 60, 18)
        secList.append(buySec)

        self.groups.populate(secList)

        results = self.groups.get_results_for_group(sprEnums.GroupCodes.buy)

        assert len(results) == 3
        assert results[0].security.symbol == "TD"
        assert results[1].security.symbol == "MFC"
        assert results[2].security.symbol == "SU"
        assert results[0].rating == 22/30

    def test_sell_sort(self):
        """
        Test that get expected order in sell group.
        """
        secList = []
        buySec = self.createSecurity("SUNCOR", "SU", 30, 60, 62)
        secList.append(buySec)
        buySec = self.createSecurity("TD", "TD", 30, 60, 88)
        secList.append(buySec)
        buySec = self.createSecurity("Manulife", "MFC", 30, 60, 108)
        secList.append(buySec)

        self.groups.populate(secList)

        results = self.groups.get_results_for_group(sprEnums.GroupCodes.sell)

        assert len(results) == 3
        assert results[0].security.symbol == "SU"
        assert results[1].security.symbol == "TD"
        assert results[2].security.symbol == "MFC"
        assert results[2].rating == 48/60

    def test_near_buy_sort(self):
        """
        Test that get expected order in near_buy group.
        """
        secList = []
        buySec = self.createSecurity("SUNCOR", "SU", 30, 60, 37)
        secList.append(buySec)
        buySec = self.createSecurity("TD", "TD", 30, 60, 33)
        secList.append(buySec)
        buySec = self.createSecurity("Manulife", "MFC", 30, 60, 32)
        secList.append(buySec)

        self.groups.populate(secList)

        results = self.groups.get_results_for_group(sprEnums.GroupCodes.near_buy)

        assert len(results) == 3
        assert results[0].security.symbol == "MFC"
        assert results[1].security.symbol == "TD"
        assert results[2].security.symbol == "SU"
        assert results[0].rating == 2/30

    def test_near_sell_sort(self):
        """
        Test that get expected order in near_sell group.
        """
        secList = []
        buySec = self.createSecurity("SUNCOR", "SU", 30, 60, 54)
        secList.append(buySec)
        buySec = self.createSecurity("TD", "TD", 30, 60, 59)
        secList.append(buySec)
        buySec = self.createSecurity("Manulife", "MFC", 30, 60, 57)
        secList.append(buySec)

        self.groups.populate(secList)

        results = self.groups.get_results_for_group(sprEnums.GroupCodes.near_sell)

        assert len(results) == 3
        assert results[0].security.symbol == "SU"
        assert results[1].security.symbol == "MFC"
        assert results[2].security.symbol == "TD"
        assert results[2].rating == 29/30

    def test_middle_sort(self):
        """
        Test that get expected order in middle group.
        """
        secList = []
        buySec = self.createSecurity("SUNCOR", "SU", 30, 60, 38)
        secList.append(buySec)
        buySec = self.createSecurity("TD", "TD", 30, 60, 51)
        secList.append(buySec)
        buySec = self.createSecurity("Manulife", "MFC", 30, 60, 42)
        secList.append(buySec)

        self.groups.populate(secList)

        results = self.groups.get_results_for_group(sprEnums.GroupCodes.middle)

        assert len(results) == 3
        assert results[0].security.symbol == "SU"
        assert results[1].security.symbol == "MFC"
        assert results[2].security.symbol == "TD"
        assert results[2].rating == 21/30

    def test_multi_groups(self):
        """
        Test multiple groups.
        """
        secList = []
        buySec = self.createSecurity("SUNCOR", "SU", 30, 60, 38)
        secList.append(buySec)
        buySec = self.createSecurity("TD", "TD", 30, 60, 54)
        secList.append(buySec)
        buySec = self.createSecurity("Manulife", "MFC", 30, 60, 42)
        secList.append(buySec)
        buySec = self.createSecurity("Algonquin", "AQN", 30, 60, 58)
        secList.append(buySec)
        buySec = self.createSecurity("Norwegian", "NCLH", 30, 60, 51)
        secList.append(buySec)

        self.groups.populate(secList)

        self.groups.print_groups()

        middle_results = self.groups.get_results_for_group(sprEnums.GroupCodes.middle)
        assert len(middle_results) == 3
        assert middle_results[0].security.symbol == "SU"
        assert middle_results[1].security.symbol == "MFC"
        assert middle_results[2].security.symbol == "NCLH"

        near_sell_results = self.groups.get_results_for_group(sprEnums.GroupCodes.near_sell)
        assert len(near_sell_results) == 2
        assert near_sell_results[0].security.symbol == "TD"
        assert near_sell_results[1].security.symbol == "AQN"

    def test_all_groups_bid_dataset(self):
        """
        Test all groups, using data from actual day, a few stocks manipulated
        so that would have some buy zone members. See res2020_10_22__22_06.ods
        """

        # Format of lists is name, symbol, buy price, sell price, current price,
        # expected group code, expected rating.
        srcList = []
        srcList.append(["banco santander", "SAN", 1.3, 3.11, 2.0199,
                        sprEnums.GroupCodes.middle, 0.39779])
        srcList.append(["Bell Canada", "BCE", 48, 61, 56.1699,
                        sprEnums.GroupCodes.middle, 0.6284])
        srcList.append(["BMO US Preferred", "ZHP", 11.7, 23.75, 23.65,
                        sprEnums.GroupCodes.near_sell, 0.9917])
        srcList.append(["Canadian Pacific", "CP", 243, 418.9, 415.1099,
                        sprEnums.GroupCodes.near_sell, 0.9784])
        srcList.append(["Eli Lilly", "LLY", 93.1, 171.1, 141.6499,
                        sprEnums.GroupCodes.middle, 0.6224])
        srcList.append(["Encana", "OVV", 2.55, 18, 1.10999,
                        sprEnums.GroupCodes.buy, 0.5647])
        srcList.append(["Exxon", "XOM", 25.5, 73.1, 34.86,
                        sprEnums.GroupCodes.near_buy, 0.1966])
        srcList.append(["First Asset Tech Giant", "TXF", 13, 24, 19,
                        sprEnums.GroupCodes.middle, 0.5454])
        srcList.append(["Home Depot", "HD", 131.7, 334.8, 281.16,
                        sprEnums.GroupCodes.middle, 0.7359])
        srcList.append(["Horizons Preferred", "HPR", 4.1, 10.7, 7.65,
                        sprEnums.GroupCodes.middle, 0.5378])
        srcList.append(["Inter Pipeline", "IPL", 6.03, 24.9, 3.9399,
                        sprEnums.GroupCodes.buy, 0.3466])
        srcList.append(["Johnson and Johnson", "JNJ", 90, 170, 145.08,
                        sprEnums.GroupCodes.middle, 0.6885])
        srcList.append(["Manulife Financial", "MFC", 10, 29, 18.89,
                        sprEnums.GroupCodes.middle, 0.4679])
        srcList.append(["Microsoft", "MSFT", 115, 230.3, 214.8899,
                        sprEnums.GroupCodes.near_sell, 0.8663])
        srcList.append(["Suncor Energy", "SU", 15.03, 53, 16.07,
                        sprEnums.GroupCodes.near_buy, 0.02739])
        srcList.append(["TD Bank", "TD", 51.3, 87.8, 60.02,
                        sprEnums.GroupCodes.near_buy, 0.2389])
        srcList.append(["VG Dev Europe", "VE", 25, 49, 27.06,
                        sprEnums.GroupCodes.near_buy, 0.08583])
        srcList.append(["VG Emerg Mkt", "VWO", 26, 65, 45.15,
                        sprEnums.GroupCodes.middle, 0.4910])
        srcList.append(["VG Canada Index", "VCE", 13, 34.5, 34.54,
                        sprEnums.GroupCodes.sell, 0.00115])
        srcList.append(["Air Canada", "AC", 10.33, 48, 16.77,
                        sprEnums.GroupCodes.near_buy, 0.17095])
        srcList.append(["Alexion Pharma", "ALXN", 83.7, 315, 119.67,
                        sprEnums.GroupCodes.near_buy, 0.1555])
        srcList.append(["Algonquin Power", "AQN", 14.79, 20.5, 20.54,
                        sprEnums.GroupCodes.sell, 0.0024])
        srcList.append(["Apple", "AAPL", 48.3, 101.1, 115.75,
                        sprEnums.GroupCodes.sell, 0.1449])
        srcList.append(["Biogen", "BIIB", 241.3, 451, 266.7999,
                        sprEnums.GroupCodes.near_buy, 0.1216])
        srcList.append(["Boeing", "BA", 93.55, 380, 169.07,
                        sprEnums.GroupCodes.middle, 0.26364])
        srcList.append(["Boston Scientific", "BSX", 27.5, 43, 36.86,
                        sprEnums.GroupCodes.middle, 0.6038])
        srcList.append(["CAE Electronics", "CAE", 15.1, 32, 23.26,
                        sprEnums.GroupCodes.middle, 0.4828])
        srcList.append(["Canadian Apartment", "CAR", 41, 58, 44.15,
                        sprEnums.GroupCodes.near_buy, 0.1853])
        srcList.append(["CNH Industrial", "CNHI", 5.76, 10.75, 8.5,
                        sprEnums.GroupCodes.middle, 0.5491])
        srcList.append(["Delta Airlines", "DAL", 19.51, 53, 33.72,
                        sprEnums.GroupCodes.middle, 0.4243])
        srcList.append(["Disney", "DIS", 110, 210, 127.5599,
                        sprEnums.GroupCodes.near_buy, 0.175599])
        srcList.append(["Dollarama", "DOL", 37.95, 53, 50.39,
                        sprEnums.GroupCodes.near_sell, 0.82657])
        srcList.append(["Illumina", "ILMN", 245, 445, 325.92,
                        sprEnums.GroupCodes.middle, 0.4046])
        srcList.append(["InterRent", "IIP", 10.8, 38.5, 9.87,
                        sprEnums.GroupCodes.buy, 0.0861])
        srcList.append(["Norwegian Cruise", "NCLH", 8.51, 42, 17.7099,
                        sprEnums.GroupCodes.middle, 0.2747])
        srcList.append(["Peyto Exploration", "PEY", 0.92, 4.5, 3.0999,
                        sprEnums.GroupCodes.middle, 0.6089])
        srcList.append(["Riocan Real Estate", "REI", 13.5, 28.3, 14.77999,
                        sprEnums.GroupCodes.near_buy, 0.08648])
        srcList.append(["Seven Generations Energy", "VII", 1.31, 4.7, 4.78,
                        sprEnums.GroupCodes.sell, 0.01702])
        srcList.append(["T Rowe Price", "TROW", 96, 130, 146.36,
                        sprEnums.GroupCodes.sell, 0.12584])
        srcList.append(["Telus", "T", 20.3, 29.7, 24.04,
                        sprEnums.GroupCodes.middle, 0.39787])
        srcList.append(["TJX", "TJX", 35.71, 61, 56.02,
                        sprEnums.GroupCodes.near_sell, 0.80308])
        srcList.append(["Tourmaline Oil", "TOU", 7.05, 14.7, 18.86,
                        sprEnums.GroupCodes.sell, 0.28299])
        srcList.append(["Transcanada Pipelines", "TRP", 47.51, 73, 35.65,
                        sprEnums.GroupCodes.buy, 0.2496])

        secList = []
        for stock in srcList:
            newSec = self.createSecurity(stock[0], stock[1], Decimal(stock[2]),
                                         Decimal(stock[3]), Decimal(stock[4]))
            secList.append(newSec)

        self.groups.populate(secList)

        # self.groups.print_groups()

        # Verify that each group has expected number of members.
        for groupCode in sprEnums.GroupCodes:
            assert len(self.groups.get_results_for_group(groupCode)) == \
                   self._get_count_for_code(srcList, groupCode)

        # Verify that each stock is in expected group and has expected rating.
        for stock in srcList:
            targetGroup = self.groups.get_results_for_group(stock[5])
            myRating = self._get_rating_for_symbol(targetGroup, stock[1])
            if myRating:
                assert myRating.security.symbol == stock[1]
                assert abs(myRating.rating - Decimal(stock[6])) < 0.001
            else:
                assert False, "Unable to find symbol in group:" + stock[1] + stock[5]
                # assertTrue(False, "Unable to find symbol in group:" + stock[1] + stock[5])

        # Verify that, within each group, stocks are sorted properly. For buy, ratings should
        # ratings should decrease, for rest should increase.
        for groupCode in sprEnums.GroupCodes:
            targetGroup = self.groups.get_results_for_group(groupCode)
            counted = 0
            lastRating = 0
            for rating in targetGroup:
                if counted > 0:
                    if groupCode == sprEnums.GroupCodes.buy:
                        assert rating.rating <= lastRating
                    else:
                        assert rating.rating >= lastRating
                counted += 1
                lastRating = rating.rating

    def _get_count_for_code(self, srcList, groupCode):
        """
        Count number if items in given list of lists that have given groupCode.
        """
        numFound = 0
        for stock in srcList:
            if stock[5] == groupCode:
                numFound += 1
        return numFound

    def _get_rating_for_symbol(self, targetGroup, stockSymbol):
        """
        Find and return rating for requested symbol in given list of ratings.
        """
        myRating = None
        for rating in targetGroup:
            if rating.security.symbol == stockSymbol:
                myRating = rating
                break
        return myRating
