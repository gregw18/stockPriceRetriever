"""
File to test daily_email module.
V0.02, October 13, 2020, GAW
"""

from datetime import date
import pytest

from . import addSrcToPath
from . import helperMethods

import daily_email
import dbAccess
import securitiesInterface
from security import Security, PriceInfo
import security_groups
import settings
import utilsInterface


@pytest.mark.unit
class Test_daily_email:
    @pytest.fixture(scope='class')
    def get_settings(self):
        mysettings = settings.Settings.instance()
        helperMethods.adjust_settings_for_tests(mysettings)
        return mysettings

    @pytest.fixture(scope='class')
    def getSecuritiesTable(self, get_settings):
        return get_settings.db_securities_table_name

    def createSecurity(self, name, symbol, buyPrice, sellPrice, currentPrice,
                       lastClosePrice, high52Week):
        mySec = Security()
        priceInfo = PriceInfo()
        priceInfo.currentPrice = currentPrice
        priceInfo.lastClosePrice = lastClosePrice
        priceInfo.high52Week = high52Week
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
        buySec = self.createSecurity("SUNCOR", "SU", 10, 12, 11.6, 11, 13)
        secList.append(buySec)
        buySec = self.createSecurity("Toronto Dominion", "TD", 40, 120, 116, 124, 140)
        secList.append(buySec)
        buySec = self.createSecurity("Exxon", "XOM", 30, 65, 28, 26, 60)
        secList.append(buySec)
        buySec = self.createSecurity("Manulife", "MFC", 20.4, 43.211, 24.5679, 34.5654, 42.112)
        secList.append(buySec)
        buySec = self.createSecurity("Microsoft", "MSFT", 120.3, 230.211, 240.087999,
                                     220.1234, 225.4321)
        secList.append(buySec)
        buySec = self.createSecurity("Apple", "AAPL", 20.3, 130.211, 14.087999, 12.09888, 80.4488)
        secList.append(buySec)
        myGroups = security_groups.SecurityGroups()
        myGroups.populate(secList)

        mySubj, myBody = daily_email.get_email(myGroups, "www.fakeurl.ca")
        print("\nemail:", mySubj, "\n", myBody)
        assert False

    def test_empty_list(self):
        """
        Test results when pass in empty securities list.
        """
        secList = []
        myGroups = security_groups.SecurityGroups()
        myGroups.populate(secList)
        mySubj, myBody = daily_email.get_email(myGroups, "www.fakeurl.ca")
        assert mySubj == ""
        assert myBody == ""

    def test_daily_email(self, getUtils, getDict, getSecuritiesTable, get_settings):
        """
        Test full process of generating and sending an email - full integration test.
        """
        currentDate = date.today()
        # print(f"1 currentDate = {currentDate}")

        getUtils.connect()
        secsDict = getDict
        secsDict["AAPL"].currentPriceDate = currentDate
        secsDict["MSFT"].currentPriceDate = currentDate
        secsDict["GOOGL"].currentPriceDate = currentDate
        self._save_to_securities(getSecuritiesTable, secsDict)

        sent = daily_email.send_from_db(get_settings.resultsTopicName, "www.fakeurl.ca")

        self._wipe_tables(secsDict, getSecuritiesTable)
        getUtils.disconnect()

        assert sent

    @pytest.fixture(scope='class')
    def getUtils(self):
        print("Running getUtils")
        return utilsInterface.UtilsInterface()

    @pytest.fixture(scope='class')
    def getSecuritiesInter(self):
        return securitiesInterface.SecuritiesInterface()

    @pytest.fixture()
    def getDict(self):
        # Some standard securities for testing
        oldDay = date(1999, 12, 31)
        secsDict = {}
        newsec = Security()
        newsec.pop("Apple", "AAPL", 123.45, 543.21, 200.33)
        newsec.fullHistoryDownloaded = True
        newsec.currentPriceDate = oldDay
        newsec.lastClosePrice = 198.45
        newsec.low52Week = 87.45
        newsec.high52Week = 345.54
        secsDict["AAPL"] = newsec

        msftsec = Security()
        msftsec.pop("Microsoft", "MSFT", 123.45, 543.21, 200.33)
        msftsec.fullHistoryDownloaded = True
        msftsec.currentPriceDate = oldDay
        msftsec.lastClosePrice = 205.45
        msftsec.low52Week = 67.45
        msftsec.high52Week = 245.54
        secsDict["MSFT"] = msftsec

        googlsec = Security()
        googlsec.pop("Alphabet", "GOOGL", 123.45, 543.21, 200.33)
        googlsec.fullHistoryDownloaded = True
        googlsec.currentPriceDate = oldDay
        googlsec.lastClosePrice = 188.45
        googlsec.low52Week = 97.45
        googlsec.high52Week = 445.54
        secsDict["GOOGL"] = googlsec

        return secsDict

    def _wipe_tables(self, myDict, getSecuritiesTable):
        """
        Delete all records from securities table, for securities
        that are in the provided dictionary of securities.
        """
        securityQuery = "id=%s"
        for tmpSecurity in myDict.values():
            dbAccess.delete_data(getSecuritiesTable, securityQuery, tmpSecurity.id)

    def _save_to_securities(self, getSecuritiesTable, secsDict):
        """
        Save current securities to securities table.
        """
        for tmpSecurity in secsDict.values():
            fieldNames = ["name", "symbol", "currentPrice", "currentPriceDate", "buyPrice",
                          "sellPrice", "fullHistoryDownloaded", "previousClosePrice",
                          "52WeekLowPrice", "52WeekHighPrice"]
            fieldValues = [None] * len(fieldNames)
            fieldValues[0] = tmpSecurity.name
            fieldValues[1] = tmpSecurity.symbol
            fieldValues[2] = tmpSecurity.currentPrice
            fieldValues[3] = tmpSecurity.currentPriceDate
            fieldValues[4] = tmpSecurity.buyPrice
            fieldValues[5] = tmpSecurity.sellPrice
            fieldValues[6] = tmpSecurity.fullHistoryDownloaded
            fieldValues[7] = tmpSecurity.lastClosePrice
            fieldValues[8] = tmpSecurity.low52Week
            fieldValues[9] = tmpSecurity.high52Week

            # Need to nest the list so that connector recognizes that adding one record
            # with five values, rather than five records with one value each.
            nestedValues = [fieldValues, ]
            dbAccess.insert_data(getSecuritiesTable, fieldNames, nestedValues)

            # Retrieve id for record just added, store in security.
            query = "symbol = %s"
            params = (tmpSecurity.symbol,)
            newId = dbAccess.select_data(getSecuritiesTable, ("id",), query, params)
            tmpSecurity.id = newId[0]["id"]
