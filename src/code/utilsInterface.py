"""
Interface to admin table. Should contain no
business logic. Should not communicate directly with mySql.
V0.01, November 23, 2022
"""

from datetime import date, timedelta

import dbAccess
import settings


class UtilsInterface:

    def __init__(self):
        self.settings = settings.Settings.instance()
        self.lastWeeklyDateField = "lastWeeklyPriceUpdate"
        self.lastGroomDateField = "lastGroomRun"
        self.fieldNames = ["id", self.lastWeeklyDateField, self.lastGroomDateField]
        self.adminTableName = self.settings.db_admin_table_name
        self.recId = self._ensure_record_exists()
        # Flag to track whether this instance did the connection. Only disconnect if we connected.
        self.we_connected = False

    def connect(self):
        """
        Connect to database.
        """
        if not dbAccess.connected_status:
            self.we_connected = True
            print("utilsInter connected.")
            return dbAccess.connect()
        else:
            self.we_connected = False
            print("utilsInter didn't connect, as are already connected.")
            return True

    def disconnect(self):
        """
        Disconnect from database
        """
        if dbAccess.connected_status:
            if self.we_connected:
                dbAccess.disconnect()
                print("utilsInter disconnected.")
            else:
                print("utilsInter did not disconnect, as we did not establish the connection.")
        else:
            print("utilsInter is not connected, so not disconnecting.")
        self.we_connected = False


    def get_last_weekly_update_date(self):
        """
        Assumes already connected to database.
        """
        record = self._get_first_record()
        return record[0][self.lastWeeklyDateField]

    def get_last_groom_date(self):
        """
        Assumes already connected to database.
        """
        record = self._get_first_record()
        return record[0][self.lastGroomDateField]

    def set_last_weekly_update_date(self):
        return self._update_date_field_with_today(self.lastWeeklyDateField)

    def set_last_groom_date(self):
        return self._update_date_field_with_today(self.lastGroomDateField)

    def reset_daily_prices(self):
        """
        Want to reset things to look like daily price update hasn't happened today.
        Thus, if lastWeeklyPriceUpdate is today, reset it to one week ago, so that if
        daily price update is run again today, the weekly price will also be updated.
        (Don't care if lastGroomRun is today - it's done. If daily price update runs
        again, grooming won't run again, and it doesn't need to.)
        """
        lastWeekly = self.get_last_weekly_update_date()
        if lastWeekly == date.today():
            newDate = lastWeekly - timedelta(7)
            self._update_date_field(self.lastWeeklyDateField, newDate)

    def _ensure_record_exists(self):
        """
        Check how many records are in the admin table. If not 1, delete all,
        add one, return its record id.
        """
        recId = 0

        # Ensure that have correct number of records, then read its id.
        self.connect()
        records = self._get_records()
        if not (records is None):
            if len(records) > 1:
                dbAccess.delete_data(self.adminTableName, "id>0")
                self._add_blank_record()
            elif len(records) == 0:
                self._add_blank_record()

            # Should be just one record now, so read it.
            records = self._get_records()
            if len(records) == 1:
                recId = records[0]["id"]
            else:
                print(f"UtilsInterface error: After correction, admin has {len(records)} records.")

        self.disconnect()

        return recId

    def _get_first_record(self):
        """
        Retrieves first record from admin table. (Should only ever be one record.)
        """
        return dbAccess.select_data(self.adminTableName, self.fieldNames, f"id={self.recId}")

    def _get_records(self):
        """
        Retrieves all records from admin table. (Should only ever be one record.)
        """
        records = dbAccess.select_data(self.adminTableName, self.fieldNames, "1=1")
        if records is None:
            print("It appears that the admin table doesn't exist.")
        elif len(records) > 1 or len(records) == 0:
            print(f"UtilsInterface error: admin has {len(records)} records.")

        return records

    def _add_blank_record(self):
        """
        Adds a record to admin table, with empty values. (Should only ever be one record.)
        """
        return dbAccess.insert_data(self.adminTableName, [], [])

    def _update_date_field_with_today(self, fieldName):
        return self._update_date_field(fieldName, date.today())

    def _update_date_field(self, fieldName, dateVal):
        updatedOk = False

        query = f"id={self.recId}"
        fieldNames = [fieldName]
        fieldValues = [dateVal]
        numUpdated = dbAccess.update_data(self.adminTableName, fieldNames, fieldValues, query)
        if numUpdated > -1:
            # dbAccess.update_date will return 0 if an update succeeded, but the record
            # wasn't changed because the new value and the existing value were the same.
            updatedOk = True
        else:
            print(f"UtilsInterface error: Failed to update {fieldName}.")

        return updatedOk
