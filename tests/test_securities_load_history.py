"""
File to test loading security price histories via the Securities class
V0.01, December 7, 2022, GAW
"""

from decimal import Decimal
import pytest

from . import addSrcToPath
from . import helperMethods

import dbAccess
import securities
#import securitiesInterface
from security import Security
import settings
#import targetSecurity
import utilsInterface
import yahooInterface


"""
What to test:
    Only download data for securities that haven't already downloaded.
        Set specified securities in securities table, some downloaded, some not.
        Call load.
        Verify that retrieve was only called for ones which weren't downloaded.
    Once download data, internal list has download set to true for that security.
    If hit error, process stops, doesn't mark that security as downloaded.
    Correct daily and weekly prices are stored in database.
    Unit or integration? Integration seems right, as this is nearly a complete process.

    Want to mock yahooInterface - don't want to get real prices, want fake ones so
    that easier to verify that correct data was saved.
"""

# Doing this here so that table names are adjusted before instantiating securities, etc.
mySettings = settings.Settings.instance()
helperMethods.adjust_settings_for_tests(mySettings)

@pytest.mark.integration
@pytest.mark.database
class TestSecuritiesLoadHistory():
    def setup(self):
        print("Running setup")
        self.dailyDbName = mySettings.db_daily_table_name
        self.weeklyDbName = mySettings.db_weekly_table_name
        self.securitiesTable = mySettings.db_securities_table_name
        self.securitiesFields = ("id", "name", "symbol", "fullHistoryDownloaded",
                                 "buyPrice", "sellPrice")

        # Some standard securities for testing
        self.secsDict = {}
        newsec = Security()
        newsec.pop("Apple", "AAPL", 123.45, 543.21, 200.33)
        newsec.id = 3
        newsec.fullHistoryDownloaded = False
        self.secsDict["AAPL"] = newsec

        msftsec = Security()
        msftsec.pop("Microsoft", "MSFT", 123.45, 543.21, 200.33)
        msftsec.id = 4
        msftsec.fullHistoryDownloaded = True
        self.secsDict["MSFT"] = msftsec

        googlsec = Security()
        googlsec.pop("Alphabet", "GOOGL", 123.45, 543.21, 200.33)
        googlsec.id = 5
        googlsec.fullHistoryDownloaded = False
        self.secsDict["GOOGL"] = googlsec

        print("Setup complete")

    @pytest.fixture(scope='class')
    def getSecurities(self):
        print("Running getSecurities")
        return securities.Securities()

    #@pytest.fixture(scope='class')
    #def getSecuritiesInter(self):
    #    print("Running getSecuritiesInter")
    #    return securitiesInterface.SecuritiesInterface()

    @pytest.fixture(scope='class')
    def getUtils(self):
        print("Running getUtils")
        return utilsInterface.UtilsInterface()

    def test_only_download_necessary(self, getUtils, getSecurities):
        """
        Verify that only tries to retrieve data for securities which don't already have
        full data downloaded.
        """
        getSecurities.securitiesDict = self.secsDict

        getUtils.connect()

        # Retrieve historic prices from web and save in tables.
        numDownloaded = getSecurities.retrieve_full_price_histories()

        # For each security that we should have downloaded, manually retrieve historic
        # prices from web, read corresponding data from table, verify that are same.
        today, dailyHistoryStart, weeklyHistoryStart = getSecurities._get_full_history_dates()
        self.compare_prices(self.secsDict["AAPL"],
                            today,
                            dailyHistoryStart,
                            weeklyHistoryStart)
        self.compare_prices(self.secsDict["GOOGL"],
                            today,
                            dailyHistoryStart,
                            weeklyHistoryStart)

        # Confirm that didn't download any data for security that was already downloaded.
        tmpSec = self.secsDict["MSFT"]
        self.confirm_no_saved_data_for_security(tmpSec)
        #savedDailies = self.retrieve_saved_prices(self.dailyDbName, tmpSec.id)
        #assert len(savedDailies) == 0
        #savedWeeklies = self.retrieve_saved_prices(self.weeklyDbName, tmpSec.id)
        #assert len(savedWeeklies) == 0

        self._wipe_history_tables(self.secsDict)
        getUtils.disconnect()

        assert numDownloaded == 2
        for tmpSecurity in getSecurities.securitiesDict.values():
            assert tmpSecurity.fullHistoryDownloaded

    def test_no_download_required(self, getUtils, getSecurities):
        """
        No securities require download.
        """
        # Create a dictionary containing one security, which doesn't require downloading.
        noDownload = {}
        noDownload["MSFT"] = self.secsDict["MSFT"]
        getSecurities.securitiesDict = noDownload

        getUtils.connect()

        # Retrieve historic prices from web and save in tables.
        numDownloaded = getSecurities.retrieve_full_price_histories()

        # Confirm that didn't download any data for security that was already downloaded.
        tmpSec = self.secsDict["MSFT"]
        self.confirm_no_saved_data_for_security(tmpSec)

        self._wipe_history_tables(self.secsDict)
        getUtils.disconnect()

        assert numDownloaded == 0

    def test_bad_symbol(self, getUtils, getSecurities):
        """
        One bad symbol, shouldn't call any save routines.
        """
        # Create a dictionary containing one security, which has an invalid symbol.
        badSymbol = "ALXN"
        badsec = Security()
        badsec.pop("Alexion", badSymbol, 123.45, 543.21, 200.33)
        badsec.id = 6
        badsec.fullHistoryDownloaded = False

        noDownload = {}
        noDownload[badSymbol] = badsec
        getSecurities.securitiesDict = noDownload

        getUtils.connect()

        # Retrieve historic prices from web and save in tables.
        numDownloaded = getSecurities.retrieve_full_price_histories()

        # Confirm that didn't download any data for security that was already downloaded.
        tmpSec = noDownload[badSymbol]
        self.confirm_no_saved_data_for_security(tmpSec)

        self._wipe_history_tables(noDownload)
        getUtils.disconnect()

        assert numDownloaded == 0

    def compare_prices(self, tmpSec, today, dailyHistoryStart, weeklyHistoryStart):
        # Compare daily and weekly prices, downloaded vs saved, for given security.
        self.compare_downloaded_saved_prices(tmpSec, self.dailyDbName,
                                             mySettings.daily_price_code,
                                             today, dailyHistoryStart)
        self.compare_downloaded_saved_prices(tmpSec, self.weeklyDbName,
                                             mySettings.weekly_price_code,
                                             today, weeklyHistoryStart)

    def compare_downloaded_saved_prices(self, tmpSec, table, frequency, today, startDate):
        # Retrieve data for given security/frequency from web. Compare
        # to saved data.
        yahooData = yahooInterface.retrieve_historical_prices(tmpSec.symbol,
                                                              startDate,
                                                              today,
                                                              frequency)
        savedData = self.retrieve_saved_prices(table, tmpSec.id)

        for i in range(len(yahooData)):
            assert yahooData[i][0] == savedData[i]["priceDate"]
            assert Decimal(yahooData[i][1]) == pytest.approx(savedData[i]["price"], Decimal(0.001))

    def confirm_no_saved_data_for_security(self, tmpSec):
        # Confirm that didn't download any data for given security.
        #tmpSec = self.secsDict["MSFT"]
        savedDailies = self.retrieve_saved_prices(self.dailyDbName, tmpSec.id)
        assert len(savedDailies) == 0
        savedWeeklies = self.retrieve_saved_prices(self.weeklyDbName, tmpSec.id)
        assert len(savedWeeklies) == 0

    def retrieve_saved_prices(self, table, secId):
        historyFields = ("priceDate", "price")
        query = "securityId = %s"
        return dbAccess.select_data(table, historyFields, query, secId)

    def _wipe_history_tables(self, secsDict):
        """
        Delete all records from daily and weekly price history tables, for securities
        that are in the provided dictionary of securities.
        """
        query = "securityId = %s"
        for tmpSecurity in secsDict.values():
            dbAccess.delete_data(self.dailyDbName, query, tmpSecurity.id)
            dbAccess.delete_data(self.weeklyDbName, query, tmpSecurity.id)
