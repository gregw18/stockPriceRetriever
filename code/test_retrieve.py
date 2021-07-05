"""
# Tests for retrievePrices class
# V0.01, May 2, 2021, GAW
"""

import retrievePrices
import settings


badBucketNameFile = "nobucket-name.txt"
bucketNameFile = "bucket-name.txt"
myPrefix = "noprefix"
mysettings = settings.Settings()
symbolAmazon = "AMZN"


class TestRetrievePrices():
    """
    Testing that working with prices > 999.99 - had errors converting strings with commas
    to float.
    """
    def test_getAMZN(self):
        """
        Confirm that both values that are used as denominators are > 0.
        """
        mySettings = settings.Settings()
        myInfo = retrievePrices._get_price_yahoo(symbolAmazon, mySettings)
        assert myInfo.high52Week > 0
        assert myInfo.lastClosePrice > 0

    def test_split(self):
        """
        Verify that am now successfully splitting numbers containing commas.
        """
        testRange = "1,334.01 - 2,345.99"
        low, high = retrievePrices._split_price_range(testRange)
        assert low == 1334.01
        assert high == 2345.99
