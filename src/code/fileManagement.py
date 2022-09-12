"""
Delete old files from bucket, provide list of results files.
V0.01, September 17, 2020, GAW.
"""

import datetime

import boto3
from botocore.exceptions import NoCredentialsError

import resultsFile


class FileManagement:
    """
    Gives interface to some actions on files in S3 bucket - list of files in given bucket with given
    name prefix, sorted by age, and removing files over a certain age.
    """

    def __init__(self):
        self.s3 = boto3.resource('s3')

    def get_file_list_sorted_by_age(self, bucketName, resultsPrefix):
        """
        For given bucket and prefix (directory name), return list of keys, sorted
        by the date the file was created, oldest files first.
        Note that am taking file date from the file name rather than the S3 object's
        last_modified attribute so than can test - can't set last_modified.
        """
        myresultsFile = resultsFile.ResultsFile(bucketName, resultsPrefix)
        keyList = []
        try:
            fileBucket = self.s3.Bucket(bucketName)
            objList = list(fileBucket.objects.filter(Prefix=resultsPrefix))
            print("len(objList)=", len(objList))
            if len(objList) > 0:
                print("key=", objList[0].key)
                objList.sort(key=lambda x: myresultsFile.get_file_date_from_name(x.key),
                             reverse=False)
                keyList = [[x.key, myresultsFile.get_file_date_from_name(x.key)] for x in objList]

        except NoCredentialsError:
            print("Credentials not available.")

        return keyList

    def _get_files_to_delete(self, fullList, cutoffDate):
        """
        For given list of file keys/dates, return list of keys where date is <= cutoffDate.
        Assumes that list is sorted by date, with oldest files first.
        """
        filesToDelete = []
        print("===========\n", "cutoffDate=", cutoffDate)
        for thisFile, fileDate in fullList:
            print("fileDate=", fileDate)
            if fileDate <= cutoffDate:
                filesToDelete.append(thisFile)
            else:
                # Since provided list is sorted with oldest file first, once hit first
                # file that isn't old enough to delete, won't find any more to delete,
                # so time to quit.
                break

        return filesToDelete

    def _get_cutoff_date(self, effectiveDate, maxAge):
        """
        For given effective date and maximum age, calculate cutoff date, i.e. date where
        as of effectiveDate, files are more than maxAge days old.
        """
        cutoffDate = effectiveDate - datetime.timedelta(days=maxAge)

        return cutoffDate

    def _delete_files(self, bucketName, filesToDelete):
        """
        Delete files in given list from given bucket.
        """
        try:
            # Transform list of filenames to format required by delete_objects - list of
            # dictionaries, Key=filename to delete.
            deleteList = []
            for tmpFile in filesToDelete:
                tmpDic = {'Key': tmpFile}
                deleteList.append(tmpDic)

            print("deleteList=", deleteList)
            fileBucket = self.s3.Bucket(bucketName)
            response = fileBucket.delete_objects(Delete={'Objects': deleteList})
            print("delete response=", response)

        except NoCredentialsError:
            print("Credentials not available.")

    def remove_old_files(self, bucketName, resultsPrefix, effectiveDate, maxAge):
        """
        Delete files from given bucket, that have given prefix, and are older than
        given maxAge, which is assumed to be in days. I.e. clean out older files.
        Receives name of bucket, prefix to look for in file names, date to calculate
        age from and maximum age (in days) to keep files for. EffectiveDate parameter
        is included to make function easier to test.
        """
        sortedFiles = self.get_file_list_sorted_by_age(bucketName, resultsPrefix)
        print("len(sortedFiles)=", len(sortedFiles))
        if len(sortedFiles) > 0:
            cutoffDate = self._get_cutoff_date(effectiveDate, maxAge)
            print("cutoffDate=", cutoffDate)
            filesToDelete = self._get_files_to_delete(sortedFiles, cutoffDate)
            print("filesToDelete=", filesToDelete)
            if len(filesToDelete) > 0:
                self._delete_files(bucketName, filesToDelete)
