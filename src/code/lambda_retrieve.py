"""
Stub for AWS Lambda function. Launches code to retrieve requested security prices,
store results in S3. Also removes old files after configured interval.
"""

from datetime import datetime
import os
import sys

import boto3

import daily_email
import resultsFile
import settings
from fileManagement import FileManagement


client = boto3.client('lambda')
mysettings = settings.Settings.instance()
myResultsFile = resultsFile.ResultsFile(mysettings.bucketName, mysettings.resultsPrefix)


def lambda_handler(event, context):
    """
    Standard handler for AWS Lambda.
    """
    print("Starting Lambda")
    print('## ENVIRONMENT VARIABLES\r' + str(dict(**os.environ)))
    print('python version=', sys.version)
    print("cwd=", os.getcwd())

    daily_email.send_from_db(mysettings.resultsTopicName, mysettings.websiteUrl)

    # Remove old files
    myManager = FileManagement()
    myManager.remove_old_files(mysettings.bucketName,
                               mysettings.resultsPrefix,
                               datetime.now(),
                               mysettings.fileMaxAge)
    print("Finished Lambda")


if __name__ == '__main__':
    lambda_handler("", "")
