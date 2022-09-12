"""
File to test web_endpoint lambda.
V0.02, October 17, 2022, GAW
"""

from datetime import date, timedelta
import json
import pytest
from unittest.mock import Mock, patch, call

from . import addSrcToPath

import security
import web_endpoint
import webPriceInfo
#import security_groups

@pytest.mark.unit
class Test_web_endpoint:
    """def createSecurity(self, name, symbol, buyPrice, sellPrice, currentPrice,
                       lastClosePrice, high52Week):
        mySec = security.Security()
        priceInfo = security.PriceInfo()
        priceInfo.currentPrice = currentPrice
        priceInfo.lastClosePrice = lastClosePrice
        priceInfo.high52Week = high52Week
        mySec.pop_with_priceInfo(name, symbol, buyPrice, sellPrice, priceInfo)
        return mySec
    """

    def test_get_website_data(self):
        """
        Testing that get something back, when run locally.
        """

        with patch('historicalPricesInterface.HistoricalPricesInterface.remove_old_prices', 
                    return_value=Mock()) as mock_remove:
            mock_remove.return_value = 5

    #myWebPriceInfos = mySecurities.get_web_data(timePeriod)
        with patch('securities.Securities.get_web_data', return_value=Mock()) as mock_data:
            mock_data.return_value = self.gen_two_webPriceInfos()
            
            result = web_endpoint.get_website_data({"queryStringParameters": {"timeframe": "30days"}}, "morestuff")
            
            #print("test result:" + json.dumps(result))
            assert len(result) > 0
            body = result["body"]
            #print(f"{body=}")

            reconstituted = json.loads(result["body"])
            #print(f"test_get_website_data, {reconstituted=}")
            assert len(reconstituted) == 2

    def gen_two_webPriceInfos(self):
        applesec = security.Security()
        applesec.pop("Apple", "AAPL", 123.45, 543.21, 200.33)
        applesec.id = 3
        applesec.fullHistoryDownloaded = False

        msftsec = security.Security()
        msftsec.pop("Microsoft", "MSFT", 223.45, 343.21, 80.33)
        msftsec.id = 3
        msftsec.fullHistoryDownloaded = False

        infos = []
        appleInfo = webPriceInfo.WebPriceInfo()
        appleInfo.populate(applesec, self.gen_prices(applesec))
        infos.append(appleInfo)

        msftInfo = webPriceInfo.WebPriceInfo()
        msftInfo.populate(msftsec, self.gen_prices(msftsec))
        infos.append(msftInfo)

        return infos

    def gen_prices(self, mySec):
        highPrice = mySec.currentPrice
        decPrice = 1.32
        numRows = 30
        curDate = date(2021, 12, 19)

        prices = []
        for i in range(0, numRows):
            curDate += timedelta(1)
            curPrice = highPrice - i * decPrice
            prices.append({"priceDate": curDate, "price": curPrice})
        print(f"prices: {prices}")

        return prices
