"""
Creating and reading results files, for stock price retriever.
V0.01, September 3, 2020, GAW.
"""

import datetime
import os.path

import boto3
from botocore.exceptions import NoCredentialsError

import security


class ResultsFile:
    """
    Logic for reading and writing results files, locally and on S3. Also contains logic
    for creating names, and converting from names back to a date.
    """

    def __init__(self, bucketName, resultsPrefix):
        """
        Verify that can get name of S3 bucket from local text file,
        and that the named bucket exists in S3.
        """
        self.resultsPrefix = resultsPrefix
        self.bucketExists = True
        self.bucketName = bucketName

        # Check that bucket with given name exists.
        try:
            s3 = boto3.resource('s3')
            if s3.Bucket(self.bucketName).creation_date is None:
                self.bucketExists = False

        except Exception as E:
            print("Exception when trying to check bucket: ", self.bucketName)
            print(E)
            self.bucketExists = False
        print("bucketExists=", self.bucketExists, " for bucket ", self.bucketName)

    def _get_results_filename(self, myDateTime):
        """
        Return name for today's results file, formatted as:
        resYYYY_MM_DD__HH_MM.txt.
        """
        nameStr = "res" + myDateTime.strftime("%Y_%m_%d__%H_%M") + ".txt"
        print("nameStr=", nameStr)

        return nameStr

    def get_file_date_from_name(self, filename):
        """
        Parse given object name to return datetime for when it was created.
        May include prefix (i.e. dir1/res2020_09_10__17_04.txt)
        """
        fileDate = None
        baseName = os.path.basename(filename)
        if len(baseName) == 24:
            fileYear = int(baseName[3:7])
            fileMonth = int(baseName[8:10])
            fileDay = int(baseName[11:13])
            fileHour = int(baseName[15:17])
            fileMin = int(baseName[18:20])
            fileDate = datetime.datetime(fileYear, fileMonth, fileDay, fileHour, fileMin)

        return fileDate

    def write_results_file(self, securitiesList, myDateTime):
        """
        Retrieve price for each symbol in list, using given function, save in a file.
        """

        resFile = ""
        if self.bucketExists:
            resFile = self._get_results_filename(myDateTime)

            # Open results file to write to.
            with open(resFile, 'w') as f:
                # Loop through all securities in list, getting and checking current price.
                for sec in securitiesList:
                    if sec.currPrice > 0:
                        # Don't write to file if no price, as resulting bar makes it look
                        # like should buy.
                        f.write(sec.write() + "\n")
        return resFile

    def _write_to_s3(self, resFile, resultsString):
        """
        Write given string to given object name in S3, in standard bucket, but under "results" key.
        """
        resFile = self.resultsPrefix + "/" + resFile
        s3 = boto3.resource('s3')
        try:
            s3.Object(self.bucketName, resFile).put(Body=resultsString)
        except NoCredentialsError:
            print("Credentials not available.")
            resFile = ""

        return resFile

    def write_results_s3(self, securitiesList, myDateTime):
        """
        Retrieve price for each symbol in list, using given function, save in S3.
        """

        resFile = ""
        resultsString = ""
        if self.bucketExists:
            # Open results file to write to.
            resFile = self._get_results_filename(myDateTime)

            # Loop through all securities in list, getting and checking current price.
            for sec in securitiesList:
                if sec.currPrice > 0:
                    # Don't save if no price, as resulting bar makes it look like should buy.
                    resultsString += sec.write() + "\n"

            # print("resultsString=", resultsString)
            resFile = self._write_to_s3(resFile, resultsString)
        else:
            print("Not saving file because bucket ", self.bucketName, " doesn't exist")

        return resFile

    def read_results_file_s3(self, filename):
        """
        Read in contents from a results file. Create a security for each record.
        add to a list, sort it and then return it.
        """
        secList = []
        if self.bucketExists:
            try:
                client = boto3.client('s3')
                for line in client.get_object(Bucket=self.bucketName,
                                              Key=filename)["Body"].iter_lines():
                    strLine = str(line)
                    thisSec = security.Security()
                    thisSec.read(strLine)
                    secList.append(thisSec)

                secList.sort(key=lambda x: x.get_sort_string())

            except (FileNotFoundError, PermissionError) as E:
                print("Exception when trying to read file: ", filename)
                print(E)
            except NoCredentialsError:
                print("Credentials not available.")
        else:
            print("Unable to find file: ", filename)

        return secList

    def read_results_file(self, filename):
        """
        Read in contents from a results file. Create a security for each record.
        add to a list, sort it and then return it.
        """
        secList = []
        if os.path.isfile(filename):
            try:
                with open(filename, 'r') as f:
                    for line in f:
                        thisSec = security.Security()
                        thisSec.read(line)
                        secList.append(thisSec)

                    secList.sort(key=lambda x: x.get_sort_string())

            except (FileNotFoundError, PermissionError) as E:
                print("Exception when trying to read file: ", filename)
                print(E)
        else:
            print("Unable to find file: ", filename)

        return secList
