"""
Delete old files from bucket, provide list of results files.
V0.01, September 17, 2020, GAW.
"""

import datetime
import pytest

import boto3
import botocore
from moto import mock_s3

from . import addSrcToPath

import fileManagement
import resultsFile

my_bucket = "fake_bucket"
my_prefix = "fake_prefix"
fake_accessKey = "TESTING"
fake_secretKey = "TESTING"


@pytest.mark.requiresMoto
@mock_s3
class TestFileManagement:
    """
    To test get_file_list_sorted_by_age need a list of files with different last_modified
    attributes, and not ordered by them.
    To test remove_old_files, need a list of files with different last_modified attributes,
    some more than X days in the past.
    """
    runcount = 0
    teardowncount = 0

    def setup(self):
        print("setup running, iteration: ", TestFileManagement.runcount,
              ", teardown=", TestFileManagement.teardowncount)
        self.sortedFilenamesWithDates = []
        self.unsortedFilenames = []
        TestFileManagement.runcount += 1
        client = boto3.client("s3",
                              aws_access_key_id=fake_accessKey,
                              aws_secret_access_key=fake_secretKey)
        try:
            s3 = boto3.resource("s3",
                                aws_access_key_id=fake_accessKey,
                                aws_secret_access_key=fake_secretKey)
            s3.meta.client.head_bucket(Bucket=my_bucket)
        except botocore.exceptions.ClientError:
            pass
        else:
            err = "Bucket {bucket} should not exist".format(bucket=my_bucket)
            raise EnvironmentError(err)

        client.create_bucket(Bucket=my_bucket)

    def teardown(self):
        """
        Remove bucket so that it doesn't exist for second test.
        """
        print("teardown running, runcount=", TestFileManagement.runcount,
              ", teardown=", TestFileManagement.teardowncount)
        TestFileManagement.teardowncount += 1
        s3 = boto3.resource("s3",
                            aws_access_key_id=fake_accessKey,
                            aws_secret_access_key=fake_secretKey)
        bucket = s3.Bucket(my_bucket)
        for key in bucket.objects.all():
            key.delete()
        bucket.delete()

    def _upload_test_files(self):
        """
        Put known set of files into a mocked bucket.
        """
        myresultsFile = resultsFile.ResultsFile(my_bucket, my_prefix)
        # Using date format of day, month, year.
        fileDates = [[1, 1, 2020],
                     [3, 1, 2020],
                     [25, 12, 2019],
                     [30, 7, 2020],
                     [28, 7, 2020],
                     [30, 6, 2020]]
        s3 = boto3.resource('s3')
        # self.unsortedFilenames = []
        self.sortedFilenamesWithDates = []
        for day, month, year in fileDates:
            fileDate = datetime.datetime(year, month, day)
            thisfilename = my_prefix + "/" + myresultsFile._get_results_filename(fileDate)
            s3.Object(my_bucket, thisfilename).put(Body="TEST FILE")
            self.sortedFilenamesWithDates.append([thisfilename, fileDate])

        self.unsortedFilenames = [x[0] for x in self.sortedFilenamesWithDates]
        self.sortedFilenamesWithDates.sort(key=lambda x: x[1], reverse=False)
        print("unsorted=", self.unsortedFilenames)
        print("sorted=", self.sortedFilenamesWithDates)

    def test_getSortedList(self):
        """
        Verify that get expected list of filenames, in expected order.
        """
        self._upload_test_files()
        myManager = fileManagement.FileManagement()
        testFiles = myManager.get_file_list_sorted_by_age(my_bucket, my_prefix)

        assert len(testFiles) == len(self.sortedFilenamesWithDates)
        for expected, actual in zip(self.sortedFilenamesWithDates, testFiles):
            assert expected[0] == actual[0]

    def test_remove_old_files(self):
        """
        Using hardcoded list of files from above, use remove_old_files to remove files
        more than 30 days old as of July 30, 2020.
        """
        self._upload_test_files()
        myManager = fileManagement.FileManagement()
        myManager.remove_old_files(my_bucket, my_prefix, datetime.datetime(2020, 7, 30), 30)

        actualRemainingFiles = myManager.get_file_list_sorted_by_age(my_bucket, my_prefix)

        expectedRemainingDates = [datetime.datetime(2020, 7, 28), datetime.datetime(2020, 7, 30)]
        assert len(actualRemainingFiles) == len(expectedRemainingDates)
        for expected, actual in zip(expectedRemainingDates, actualRemainingFiles):
            assert expected == actual[1]
