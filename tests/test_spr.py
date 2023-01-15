"""
File to test some main spr functions
V0.04, May 15, 2020, GAW
"""

import pytest

from . import addSrcToPath

from yahooInterface import get_yahoo_ticker
from spr import get_next_batch

@pytest.mark.integration
def test_getPriceYahoo_NYSE():
    """
    Test that New York symbols aren't changed.
    """
    yTicker = get_yahoo_ticker("AAPL")
    assert yTicker == "AAPL"


@pytest.mark.integration
def test_getPriceYahoo_TSX():
    """
    Test that get TSX tickers change.
    """
    yTicker = get_yahoo_ticker("TSX:ALA")
    assert yTicker == "ALA.TO"


@pytest.mark.integration
def test_getPriceYahoo_TSXETF():
    """
    Test that get TSX ETF tickers change.
    """
    yTicker = get_yahoo_ticker("VCE.TRT")
    assert yTicker == "VCE.TO"

@pytest.mark.unit
def test_nextBatch_oneElement():
    """
    Only have one element in array, should get one back
    """
    arr = [1]
    groupStart = 0
    groupSize = 20
    nextBatch = get_next_batch(arr, groupStart, groupSize)
    assert len(nextBatch) == 1

@pytest.mark.unit
def test_nextBatch_smallBatch():
    """
    Have less than max group size in batch, expect all items back
    """
    arr = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    groupStart = 0
    groupSize = 20
    nextBatch = get_next_batch(arr, groupStart, groupSize)
    assert len(nextBatch) == len(arr)

@pytest.mark.unit
def test_nextBatch_fullBatch():
    """
    Have exactly max group size in batch, expect all items back
    """
    arr = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    groupStart = 0
    groupSize = 10
    nextBatch = get_next_batch(arr, groupStart, groupSize)
    assert len(nextBatch) == len(arr)

@pytest.mark.unit
def test_nextBatch_justOverOneBatch():
    """
    Have one over max group size in batch, expect batch size items back first, then remainder.
    """
    arr = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    groupStart = 0
    groupSize = 10
    nextBatch = get_next_batch(arr, groupStart, groupSize)
    assert len(nextBatch) == groupSize
    nextBatch = get_next_batch(arr, groupSize, groupSize)
    assert len(nextBatch) == len(arr) - groupSize

@pytest.mark.unit
def test_nextBatch_TwoBatch():
    """
    Have exactly two times max group size in batch, expect two groups of size groupSize.
    """
    arr = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    groupStart = 0
    groupSize = 5
    nextBatch = get_next_batch(arr, groupStart, groupSize)
    assert len(nextBatch) == groupSize
    nextBatch = get_next_batch(arr, groupSize, groupSize)
    assert len(nextBatch) == len(arr) - groupSize


@pytest.mark.unit
def test_nextBatch_OverTwoBatch():
    """
    Have a few over two times max group size in batch, expect two groups of size groupSize
    then remainder.
    """
    arr = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    groupStart = 0
    groupSize = 5
    nextBatch = get_next_batch(arr, groupStart, groupSize)
    assert len(nextBatch) == groupSize
    nextBatch = get_next_batch(arr, groupSize, groupSize)
    assert len(nextBatch) == groupSize
    nextBatch = get_next_batch(arr, groupSize * 2, groupSize)
    assert len(nextBatch) == (len(arr) - (groupSize * 2))
