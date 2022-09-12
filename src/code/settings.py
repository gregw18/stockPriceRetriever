"""
Settings and settings class for stock price retriever.
V0.01, September 6, 2020, GAW.
"""

import json

from singleton import Singleton

# srcFile = "Portfolio.xls"
# srcTab = "Current"                 # name of tab in spreadsheet to read data from.
bucketNameFile = "bucket-name.txt"
alphaFile = "alpha.txt"
rdsEndpointFile = "dbendpoint.txt"
rdsSettings = "dbparams.json"

@Singleton
class Settings:
    """
    Settings class for stock price retriever.
    """

    def __init__(self):
        with open("settings.json", "r") as config_file:
            configData = json.load(config_file)
        self.srcFile = configData["srcfile"]
        self.srcTab = configData["srctab"]

        self.alphaBaseUrl = "https://www.alphavantage.co/query"
        self.alphaCallDelay = 20			# Number of seconds to wait before
                                                      # calling api (to avoid going over
                                                      # req/min limit.)
        self.respContName = "Global Quote"	# Name of master container in response.
        self.priceName = "05. price"		# Name of entry containing price.
        self.alphaApiTimeOut = 4
        self.alphaApiKey = self._read_setting_from_file(alphaFile)

        self.yahooCallDelay = 1
        self.errFile = "errors.txt"

        self.fileMaxAge = 30                    # Keep results files for this many days.
        self.resultsPrefix = "results"          # "directory" in S3 to store results files in.
        self.bucketName = self._read_setting_from_file(bucketNameFile)
        self.resultsTopicName = "StockRetrieverResultsTopic"

        # Database settings
        dbParams = self._read_db_settings(rdsSettings)
        self.rds_endpoint = self._read_setting_from_file(rdsEndpointFile)
        self.rds_port = "3306"
        self.rds_db_name = dbParams["Parameters"]["DbName"]
        self.rds_user_name = dbParams["Parameters"]["DbUserSR"]

        self.db_daily_history_code = "DAY"
        self.db_weekly_history_code = "WEEK"
        
        self.db_securities_table_name = "securities"
        self.db_daily_table_name = "dailyPriceHistory"
        self.db_weekly_table_name = "weeklyPriceHistory"
        self.db_admin_table_name = "admin"
        self.test_table_prefix = "test_"
        # Keeping daily prices for 100 days - approximately 3 months, and
        # weekly prices for 265 weeks - just over 5 years.
        self.daily_price_days_to_keep = 100
        self.weekly_price_weeks_to_keep = 70
        self.daily_price_code = "1d"
        self.weekly_price_code = "1wk"

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

    def _read_db_settings(self, fileName):
        """
        Read some rds settings from json file, return full dictionary of results.
        """
        f = open(fileName)
        params = json.load(f)
        f.close()

        return params

    def use_test_tables(self):
        """
        Switch settings to test database tables. Used for testing, but also required when
        updating structures of tables.
        """
        prefix = self.test_table_prefix
        if self.db_admin_table_name[0:5] != prefix:
            self.db_securities_table_name = prefix + self.db_securities_table_name
            self.db_daily_table_name = prefix + self.db_daily_table_name
            self.db_weekly_table_name = prefix + self.db_weekly_table_name
            self.db_admin_table_name = prefix + self.db_admin_table_name
