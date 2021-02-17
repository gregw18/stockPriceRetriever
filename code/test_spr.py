"""
File to test some main spr functions
V0.04, May 15, 2020, GAW
"""

from retrievePrices import get_yahoo_ticker


def test_getPriceYahoo_NYSE():
    """
    Test that New York symbols aren't changed.
    """
    yTicker = get_yahoo_ticker("AAPL")
    assert yTicker == "AAPL"


def test_getPriceYahoo_TSX():
    """
    Test that get TSX tickers change.
    """
    yTicker = get_yahoo_ticker("TSX:ALA")
    assert yTicker == "ALA.TO"


def test_getPriceYahoo_TSXETF():
    """
    Test that get TSX ETF tickers change.
    """
    yTicker = get_yahoo_ticker("VCE.TRT")
    assert yTicker == "VCE.TO"
