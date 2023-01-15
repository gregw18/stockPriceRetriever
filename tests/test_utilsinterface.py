"""
File to integration test utilsInterface.
V0.01, November 24, 2022, GAW
"""

from datetime import date
import pytest

from . import addSrcToPath
from . import helperMethods

import dbAccess
from utilsInterface import UtilsInterface
import settings

"""
To Test
    Startup
        If no record, adds one, returns null values
        If more than one record, deletes all, adds one, returns null values
    LastWeeklyUpdateDate
        If update value and retrieve, get expected value.
    LastGroomDate
        If update value and retrieve, get expected value.

"""

mysettings = settings.Settings.instance()
helperMethods.adjust_settings_for_tests(mysettings)


@pytest.mark.integration
@pytest.mark.database
class TestUtilsInterface():
    def setup(self):
        self.adminTableName = mysettings.db_admin_table_name

    def test_startup_no_records(self):
        """
        No records when try start up, should result create an empty record.
        """
        dbAccess.connect()
        self._zap_admin_db()

        # Creating UtilsInterface should ensure one record in admin table.
        myUtils = UtilsInterface()

        dbAccess.connect()
        assert self._get_record_count() == 1

        dbAccess.disconnect()

    def test_startup_multiple_records(self):
        """
        If have more than one record on startup, should wipe, add one good record.
        """
        dbAccess.connect()
        dbAccess.insert_data(self.adminTableName, [], [])
        dbAccess.insert_data(self.adminTableName, [], [])
        dbAccess.disconnect()

        # Creating UtilsInterface should ensure one record in admin table.
        myUtils = UtilsInterface()

        dbAccess.connect()
        assert self._get_record_count() == 1

        dbAccess.disconnect()

    def test_update_lastWeeklyUpdateDate(self):
        """
        Change value for lastWeeklyUpdateData, then confirm that was saved.
        """

        myUtils = UtilsInterface()

        myUtils.connect()
        myUtils.set_last_weekly_update_date()
        savedDate = myUtils.get_last_weekly_update_date()
        myUtils.disconnect()

        assert savedDate == date.today()

    def test_update_lastGroomRun(self):
        """
        Change value for lastGroomRun, then confirm that was saved.
        """

        myUtils = UtilsInterface()

        myUtils.connect()
        myUtils.set_last_groom_date()
        savedDate = myUtils.get_last_groom_date()
        myUtils.disconnect()

        assert savedDate == date.today()

    def _zap_admin_db(self):
        """
        Delete all records from admin table.
        """
        dbAccess.delete_data(self.adminTableName, "1=1")

    def _get_record_count(self):
        """
        Count how many records are in the admin table.
        """
        records = dbAccess.select_data(self.adminTableName, ["id"], "1=1")

        return len(records)
