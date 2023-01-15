"""
File to test StockTarget class
V0.04, May 11, 2020, GAW
"""

import pytest

from . import addSrcToPath

import stockTarget


srcFile = "PortfolioTest.xls"
srcTab = "Current"


@pytest.mark.integration
class TestStockTarget():
    """
    Test for StockTarget.
    """

    def test_fileDoesntExist(self):
        """
        Test that get empty list when file doesn't exist.
        """
        myTargets = stockTarget.StockTarget()
        myList = myTargets.get_list("badfile.xls", srcTab)
        assert len(myList) == 0

    def test_tabDoesntExist(self):
        """
        Test that get empty list when tab doesn't exist.
        """
        myTargets = stockTarget.StockTarget()
        myList = myTargets.get_list(srcFile, "notab")
        assert len(myList) == 0

    def test_getExpected(self):
        """
        Test that get expected number of items in list, with expected symbols.
        """
        myTargets = stockTarget.StockTarget()
        myList = myTargets.get_list(srcFile, srcTab)
        assert len(myList) == 3
        assert myList[0].Symbol == "TSX:ALA"
        assert myList[1].Symbol == "TSLA"
        assert myList[2].Symbol == "SAN"
        assert myList[0].Buy_price == 6
        assert myList[0].Sell_price == 129
