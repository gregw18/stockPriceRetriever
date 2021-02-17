"""
Settings and settings class for stock price retriever.
V0.01, September 6, 2020, GAW.
"""

srcFile = "Portfolio.xls"
srcTab = "2018"                 # name of tab in spreadsheet to read data from.
bucketNameFile = "bucket-name.txt"
alphaFile = "alpha.txt"


class Settings:
    """
    Settings class for stock price retriever.
    """

    def __init__(self):
        self.alphaBaseUrl = "https://www.alphavantage.co/query"
        self.alphaCallDelay = 20			# Number of seconds to wait before
                                                        # calling api (to avoid going over
                                                        # req/min limit.)
        self.respContName = "Global Quote"	# Name of master container in response.
        self.priceName = "05. price"		# Name of entry containing price.
        self.alphaApiTimeOut = 4
        self.alphaApiKey = self._read_setting_from_file(alphaFile)

        self.yahooCallDelay = 2
        self.errFile = "errors.txt"

        self.fileMaxAge = 30                    # Keep results files for this many days.
        self.resultsPrefix = "results"          # "directory" in S3 to store results files in.
        self.bucketName = self._read_setting_from_file(bucketNameFile)
        self.resultsTopicName = "StockRetrieverResultsTopic"

    def _read_bucket_name(self):
        """
        Get name of S3 bucket from local text file.
        """
        self.bucketName = ""
        try:
            with open(bucketNameFile, 'r') as f:
                self.bucketName = f.readline().rstrip()

        except (FileNotFoundError, PermissionError) as E:
            print("Exception when trying to read bucket name file: ", bucketNameFile)
            print(E)

    def _read_setting_from_file(self, fileName):
        """
        Get value for setting from local text file. Assumes file contains a single line,
        containing just the setting.
        """
        settingValue = ""
        try:
            with open(fileName, 'r') as f:
                settingValue = f.readline().rstrip()

        except (FileNotFoundError, PermissionError) as E:
            print("Exception when trying to read setting from file: ", fileName)
            print(E)

        return settingValue
