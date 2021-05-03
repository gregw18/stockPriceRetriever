"""
# Tests for retrievePrices class
# V0.01, May 2, 2021, GAW
"""

import datetime
import retrievePrices
import security
import settings

import pytest


badBucketNameFile = "nobucket-name.txt"
bucketNameFile = "bucket-name.txt"
myPrefix = "noprefix"
mysettings = settings.Settings()
symbolGoogle = "GOOGL"


class TestRetrievePrices():
    def test_getAMZN(self):
        mySettings = settings.Settings()
        myInfo = retrievePrices._get_price_yahoo(symbolGoogle, mysettings)
        assert myInfo.high52Week > 0
        assert myInfo.lastClosePrice > 0
        

    def test_split(self):
        testRange = "1,334.01 - 2,345.99"
        low, high = retrievePrices._split_price_range(testRange)
        assert low == 1334.01
        assert high == 2345.99


