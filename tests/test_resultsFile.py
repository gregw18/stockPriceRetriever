"""
# File to test resultsFile class
# V0.01, September 3, 2020, GAW
"""

import datetime

import pytest

from . import addSrcToPath

import resultsFile
import security
import settings

badBucketNameFile = "nobucket-name.txt"
bucketNameFile = "bucket-name.txt"
myPrefix = "noprefix"
mysettings = settings.Settings.instance()

@pytest.mark.integration
class TestResultsFile():
    def getSingleSecurityList(self):
        securities = []
        firstSec = security.Security()
        firstSec.pop("WEIBO", "WEI", 100, 200, 125)
        securities.append(firstSec)
        return securities

    def getMultipleSecurityList(self):
        securities = []
        firstSec = security.Security()
        firstSec.pop("WEIBO", "WEI", 100, 200, 125)
        securities.append(firstSec)

        secondSec = security.Security()
        secondSec.pop("ALIBABA", "ALI", 10, 20, 12.5)
        securities.append(secondSec)

        thirdSec = security.Security()
        thirdSec.pop("BAIDU", "BAI", 200, 300, 225)
        securities.append(thirdSec)
        return securities

    def test_writeSingleSecurity(self):
        """
        Test that get expected result when write single record.
        """
        securities = self.getSingleSecurityList()
        myResults = resultsFile.ResultsFile(mysettings.bucketName, mysettings.resultsPrefix)
        creationTime = datetime.datetime(2020, 9, 3, 19, 5)
        resFile = myResults.write_results_file(securities, creationTime)

        assert resFile == "res2020_09_03__19_05.txt"
        with open(resFile, 'r') as f:
            firstLine = f.readline().rstrip()
        assert firstLine == securities[0].write()

    def test_writeMultipleSecurity(self):
        """
        Test that get expected result when write several records.
        """
        securities = self.getMultipleSecurityList()
        # firstSec = security.Security()
        # firstSec.pop("WEIBO", "WEI", 100, 200, 125)
        # securities.append(firstSec)

        # secondSec = security.Security()
        # secondSec.pop("ALIBABA", "ALI", 10, 20, 12.5)
        # securities.append(secondSec)

        # thirdSec = security.Security()
        # thirdSec.pop("BAIDU", "BAI", 200, 300, 225)
        # securities.append(thirdSec)

        myResults = resultsFile.ResultsFile(mysettings.bucketName, mysettings.resultsPrefix)
        creationTime = datetime.datetime(2020, 9, 3, 19, 6)
        resFile = myResults.write_results_file(securities, creationTime)

        assert resFile == "res2020_09_03__19_06.txt"
        with open(resFile, 'r') as f:
            for sec in securities:
                thisLine = f.readline().rstrip()
                assert thisLine == sec.write()

    def test_readSingleSecurity(self):
        """
        Test can read in file containing single security.
        First, create file containing single security, then read it back and compare objects.
        """
        securities = self.getSingleSecurityList()
        myResults = resultsFile.ResultsFile(mysettings.bucketName, mysettings.resultsPrefix)
        creationTime = datetime.datetime(2020, 9, 3, 19, 7)
        resFile = myResults.write_results_file(securities, creationTime)

        assert resFile == "res2020_09_03__19_07.txt"
        retrievedResults = myResults.read_results_file(resFile)
        assert retrievedResults[0] == securities[0]
        assert len(retrievedResults) == len(securities)

    def test_readMultipleSecurity(self):
        """
        Test can read in file containing multiple securities.
        First, create file containing three securities, then read it back and compare objects.
        """
        securities = self.getMultipleSecurityList()
        myResults = resultsFile.ResultsFile(mysettings.bucketName, mysettings.resultsPrefix)
        creationTime = datetime.datetime(2020, 9, 3, 19, 8)
        resFile = myResults.write_results_file(securities, creationTime)

        assert resFile == "res2020_09_03__19_08.txt"
        retrievedResults = myResults.read_results_file(resFile)
        securities.sort(key=lambda x: x.get_sort_string())

        assert len(retrievedResults) == len(securities)
        for origSec, readSec in zip(securities, retrievedResults):
            assert origSec == readSec

    def test_noBucketNameFile(self):
        """
        Test that get error if bucket name file doesn't exist.
        with pytest.raises(FileNotFoundError):
        """
        myResults = resultsFile.ResultsFile("thisfiledoesntexist.txt", mysettings.resultsPrefix)
        assert myResults.bucketExists is False

    def test_get_file_date_from_name_simpleWithPrefix(self):
        myResults = resultsFile.ResultsFile(mysettings.bucketName, mysettings.resultsPrefix)
        fileDate = myResults.get_file_date_from_name("results/res2020_09_10__17_04.txt")
        assert fileDate == datetime.datetime(2020, 9, 10, 17, 4)

    def test_get_file_date_from_name_simpleNoPrefix(self):
        myResults = resultsFile.ResultsFile(mysettings.bucketName, mysettings.resultsPrefix)
        fileDate = myResults.get_file_date_from_name("res2018_10_30__23_59.txt")
        assert fileDate == datetime.datetime(2018, 10, 30, 23, 59)

    def test_get_file_date_from_name_future(self):
        myResults = resultsFile.ResultsFile(mysettings.bucketName, mysettings.resultsPrefix)
        fileDate = myResults.get_file_date_from_name("results/res2030_09_10__17_04.txt")
        assert fileDate == datetime.datetime(2030, 9, 10, 17, 4)

    def test_get_file_date_from_name_invalid(self):
        with pytest.raises(ValueError):
            myResults = resultsFile.ResultsFile(mysettings.bucketName, mysettings.resultsPrefix)
            fileDate = myResults.get_file_date_from_name("results/res2020_13_10__17_04.txt")
            assert fileDate is None
