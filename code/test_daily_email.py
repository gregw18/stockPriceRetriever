"""
File to test daily_email module.
V0.02, October 13, 2020, GAW
"""

import pytest

import daily_email
import security
import security_groups


class Test_daily_email:
    def createSecurity(self, name, symbol, buyPrice, sellPrice, currentPrice, lastClosePrice):
        mySec = security.Security()
        priceInfo = security.PriceInfo()
        priceInfo.currentPrice = currentPrice
        priceInfo.lastClosePrice = lastClosePrice
        mySec.pop_with_priceInfo(name, symbol, buyPrice, sellPrice, priceInfo)
        return mySec

    @pytest.mark.xfail
    def test_one_middle(self):
        """
        Test with one security, in middle.
        Not a unit test - just outputs what contents of email will look like, without
        having to run the lambda and send an email. Always fails.
        Note that layout of output doesn't exactly match email - display here shows leading
        space in body that doesn't appear in email.
        """
        secList = []
        buySec = self.createSecurity("SUNCOR", "SU", 10, 12, 11.6, 11)
        secList.append(buySec)
        buySec = self.createSecurity("Toronto Dominion", "TD", 40, 120, 116, 124)
        secList.append(buySec)
        buySec = self.createSecurity("Exxon", "XOM", 30, 65, 28, 26)
        secList.append(buySec)
        buySec = self.createSecurity("Manulife", "MFC", 20.4, 43.211, 24.5679, 34.5654)
        secList.append(buySec)
        buySec = self.createSecurity("Microsoft", "MSFT", 120.3, 230.211, 240.087999, 220.1234)
        secList.append(buySec)
        buySec = self.createSecurity("Apple", "AAPL", 20.3, 130.211, 14.087999, 12.09888)
        secList.append(buySec)
        myGroups = security_groups.security_groups()
        myGroups.populate(secList)

        mySubj, myBody = daily_email.get_email(myGroups)
        print("\nemail:", mySubj, "\n", myBody)
        assert True == False

    def test_empty_list(self):
        """
        Test results when pass in empty securities list.
        """
        secList = []
        myGroups = security_groups.security_groups()
        myGroups.populate(secList)
        mySubj, myBody = daily_email.get_email(myGroups)
        assert mySubj == ""
        assert myBody == ""
