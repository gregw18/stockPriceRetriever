"""
File to integration test dbAccess - actually hits database.
V0.01, November 10, 2022, GAW
"""

from datetime import date
from decimal import *
import pytest

from . import addSrcToPath
from . import helperMethods

import dbAccess
import settings

@pytest.mark.integration
@pytest.mark.database
class TestDbAccess():
    def setup(self):
        mySettings = settings.Settings.instance()
        helperMethods.adjust_settings_for_tests(mySettings)

        self.adminTable = mySettings.db_admin_table_name
        self.dailyPricesTable = mySettings.db_daily_table_name
        self.securitiesTable = mySettings.db_securities_table_name
        self.testTableName1 = "TestTable1"
        self.knownGoodTableName = self.adminTable
        self.knownBadTableName = "notable"
        self.testTable1Def = (
            "CREATE TABLE TestTable1 ("
            "   `id` MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT,"
            "   testField1 MEDIUMINT UNSIGNED,"
            "   testDate DATE,"
            "   testPrice DECIMAL(10,2),"
            "   PRIMARY KEY (`id`)"
            ") ENGINE=InnoDB"
        )

    def wipeTables(self):
        print("running test_dbAccess.wipeTables")
        query = "1=1"
        dbAccess.delete_data(self.securitiesTable, query)
        dbAccess.delete_data(self.dailyPricesTable, query)
        return True

    def test_create_table(self):
        """
        Test that am correctly creating a table (and also checking for its existence
        and deleting it).
        """
        if not dbAccess.connect():
            assert False, "unable to connect to database"
            return

        if dbAccess.does_table_exist(self.testTableName1):
            assert dbAccess.delete_table(self.testTableName1) == True

        result = dbAccess.create_table(self.testTable1Def)
        if result:
            assert dbAccess.does_table_exist(self.testTableName1) == True
            assert dbAccess.delete_table(self.testTableName1) == True
        else:
            assert False, "create_table call failed"
        dbAccess.disconnect()

    def test_does_table_exist_exists(self):
        """
        Test that can verify that a table exists
        """
        if not dbAccess.connect():
            assert False, "unable to connect to database"
            return

        assertMsg = "assumes that table %s should always exist" % (self.knownGoodTableName,)
        assert dbAccess.does_table_exist(self.knownGoodTableName) == True, assertMsg

        dbAccess.disconnect()

    def test_does_table_exist_doesntexist(self):
        """
        Test that can verify that a table doesn't exist
        """
        if not dbAccess.connect():
            assert False, "unable to connect to database"
            return

        assertMsg = "table %s shouldn't exist" % (self.knownBadTableName,)
        assert dbAccess.does_table_exist(self.knownBadTableName) == False, assertMsg

        dbAccess.disconnect()

    # Testing insert_data. One record success. Multiple records success. Bad field name, 
    # bad table name, mismatched fields and data. Various field types - string, number, date.
    # Need to delete records when complete each test.
    def test_insert_one_record(self):
        """
        Insert a single record, should succeed.
        """
        table = self.securitiesTable
        fields = ("Name", "Symbol", "BuyPrice", "SellPrice")
        values = [("Amazon", "AMZN", 150.01, 300.21),]

        if not dbAccess.connect():
            assert False, "unable to connect to database"
        
        result = dbAccess.insert_data(table, fields, values)
        dbAccess.delete_data(table, "Symbol='AMZN'")
        dbAccess.disconnect()

        assertMsg = "Failed to insert a single record"
        assert result == True, assertMsg


    def test_insert_one_record_with_date(self):
        """
        Insert a single record, should succeed.
        """
        table = self.securitiesTable
        fields = ("Name", "Symbol", "BuyPrice", "SellPrice", "currentPriceDate")
        values = [("Amazon", "AMZN3", 150.01, 300.21, date(2023, 12, 31)),]

        if not dbAccess.connect():
            assert False, "unable to connect to database"

        result = dbAccess.insert_data(table, fields, values)
        dbAccess.delete_data(table, "Symbol='AMZN3'")
        dbAccess.disconnect()

        assertMsg = "Failed to insert a single record"
        assert result == True, assertMsg


    def test_insert_empty_record(self):
        """
        Insert an empty record, should succeed.
        """
        table = self.securitiesTable
        fields = ()
        values = []

        if not dbAccess.connect():
            assert False, "unable to connect to database"
        
        result = dbAccess.insert_data(table, fields, values)
        dbAccess.delete_data(table, "Symbol=''")

        dbAccess.disconnect()

        assertMsg = "Failed to insert a single record"
        assert result == True, assertMsg


    def test_insert_three_records(self):
        """
        Insert three records (and then delete them), should succeed.
        """
        table = self.securitiesTable
        fields = ("Name", "Symbol", "BuyPrice", "SellPrice")
        values = [  ("Amazon", "AMZN", 150.01, 300.21), 
                    ("Microsoft", "MSFT", 100.34, 234.56),
                    ("Google", "GOOG", 304.56, 543.21)]

        if not dbAccess.connect():
            assert False, "unable to connect to database"

        result = dbAccess.insert_data(table, fields, values)
        dbAccess.delete_data(table, "Symbol='AMZN' OR Symbol='MSFT' OR Symbol='GOOG'")
        
        dbAccess.disconnect()

        assertMsg = "Failed to insert records"
        assert result == True, assertMsg

    def test_insert_bad_field(self):
        """
        Insert a single record, with a bad field name.
        """
        table = self.securitiesTable
        fields = ("Name", "Symbol", "BoughtPrice", "SellPrice")
        values = [("Amazon2", "AMZN", 150.01, 300.21),]

        if not dbAccess.connect():
            assert False, "unable to connect to database"
        
        assertMsg = "Insert succeeded despite bad field name"
        assert dbAccess.insert_data(table, fields, values) == False, assertMsg

        dbAccess.disconnect()


    def test_insert_bad_table(self):
        """
        Insert a single record, with a bad table name.
        """
        table = self.knownBadTableName
        fields = ("Name", "Symbol", "BuyPrice", "SellPrice")
        values = [("Amazon2", "AMZN", 150.01, 300.21),]

        if not dbAccess.connect():
            assert False, "unable to connect to database"
        
        assertMsg = "Insert succeeded despite bad table name"
        assert dbAccess.insert_data(table, fields, values) == False, assertMsg

        dbAccess.disconnect()


    # Note: Wanted to have a test that failed because was putting invalid data
    # into a field, but it looks like that isn't possible - can put numbers in string fields,
    # strings in numeric fields and numbers and strings in date fields.
    #def test_insert_bad_field_data(self):
    #    """
    #    Insert a single record, with a number in a string field.
    #    """
    #    table = self.securitiesTable
    #    fields = ("Name", "Symbol", "BuyPrice", "SellPrice", "currentPriceDate")
    #    values = [("Amazon2", 0, "number", 300.21, "mydate"),]

    #    if not dbAccess.connect():
    #        assert False, "unable to connect to database"
        
    #    assertMsg = "Insert succeeded despite bad field data"
    #    assert dbAccess.insert_data(table, fields, values) == False, assertMsg

    #    dbAccess.disconnect()


    # Testing deleting records. Delete one record, multiple. No match - 0 records.
    # Bad table name, bad field names, bad query. Multi-field query.
    def test_delete_one_record(self):
        """
        Insert a single record, then delete it. Should succeed.
        """
        table = self.securitiesTable
        fields = ("Name", "Symbol", "BuyPrice", "SellPrice")
        values = [("Amazon", "AMZN", 150.01, 300.21),]

        if not dbAccess.connect():
            assert False, "unable to connect to database"
        
        assertMsg = "Failed to delete a single record"
        if dbAccess.insert_data(table, fields, values):
            query = "Symbol='AMZN'"
            assertMsg = "Failed to delete one record"
            numDeleted = dbAccess.delete_data(table, query)
            assert numDeleted == 1, assertMsg
        else:
            assert False, "Insert failed in delete test."

        dbAccess.disconnect()

    def test_delete_one_record_bad_table_name(self):
        """
        Try deleting from a table that doesn't exist.
        """
        table = self.knownBadTableName

        if not dbAccess.connect():
            assert False, "unable to connect to database"
        
        assertMsg = "Managed to delete from a table that doesn't exist."
        query = "Symbol='AMZN4'"
        numDeleted = dbAccess.delete_data(table, query)
        assert numDeleted == 0, assertMsg

        dbAccess.disconnect()


    def test_delete_one_record_bad_field_name(self):
        """
        Try deleting records with a query which includes a bad field name.
        """
        table = self.securitiesTable
        query = "Symbol='AMZN' AND NOTFIELD='BAD'"

        if not dbAccess.connect():
            assert False, "unable to connect to database"
        
        assertMsg = "Managed to delete from a table based on a bad field name"
        numDeleted = dbAccess.delete_data(table, query)
        assert numDeleted == 0, assertMsg

        dbAccess.disconnect()


    # Testing update_data. Updating one record, multiple records.
    # Updating a single field, multiple fields. Various field types - strings
    # numbers and dates.
    # Bad field name, bad table name.
    # Need to insert known record to start, update, confirm change and then delete
    # records when complete each test.
    def test_update_one_record(self):
        """
        Update a single record, should succeed.
        """
        table = self.securitiesTable
        fields = ("Name", "Symbol", "BuyPrice", "SellPrice")
        values = [("Amazon", "AMZN5", 150.01, 300.21),]

        if not dbAccess.connect():
            assert False, "unable to connect to database"
        self.wipeTables()
        
        assertMsg = "Failed to insert a single record"
        assert dbAccess.insert_data(table, fields, values) == True, assertMsg
        
        updateFields = ("Name", "percentChangeToday", "currentPriceDate")
        updateValues = ("Amazing", -15.4, date(2022, 1, 28))
        query = "Symbol='AMZN5'"
        updateResult = dbAccess.update_data(table, updateFields, updateValues, query)
        data = dbAccess.select_data(table, updateFields, query)
        dbAccess.delete_data(table, "Symbol='AMZN5'")

        dbAccess.disconnect()

        assert updateResult == 1
        assert data[0]["percentChangeToday"] == Decimal('-15.4')


    def test_update_multiple_records(self):
        """
        Update multiple records, should succeed.
        """
        table = self.securitiesTable
        fields = ("Name", "Symbol", "BuyPrice", "SellPrice")
        values = [("Amazon", "AMZN6", 150.01, 300.21),
                    ("Amazon2", "AMZN6", 50.01, 30.21),
                    ("Amazon3", "AMZN6", 10.21, 230.1),]

        if not dbAccess.connect():
            assert False, "unable to connect to database"
        
        assertMsg = "Failed to insert records"
        assert dbAccess.insert_data(table, fields, values) == True, assertMsg
        
        updateFields = ("Name", "percentChangeToday", "currentPriceDate")
        updateValues = ("Amazing", -15.4, date(2022, 1, 28))
        query = "Symbol='AMZN6'"
        updateResult = dbAccess.update_data(table, updateFields, updateValues, query)

        data = dbAccess.select_data(table, updateFields, query)
        dbAccess.delete_data(table, "Symbol='AMZN6'")

        dbAccess.disconnect()

        assert updateResult == 3
        assert data[0]["Name"] == "Amazing"
        assert data[2]["currentPriceDate"] == date(2022, 1, 28)


    def test_update_bad_update_field(self):
        """
        Update a single record, try updating field that doesn't exist.
        """
        table = self.securitiesTable
        fields = ("Name", "Symbol", "BuyPrice", "SellPrice")
        values = [("Amazon", "AMZN7", 150.01, 300.21),]

        if not dbAccess.connect():
            assert False, "unable to connect to database"
        
        assertMsg = "Failed to insert a single record"
        assert dbAccess.insert_data(table, fields, values) == True, assertMsg
        
        updateFields = ("zzName", "percentChangeToday", "currentPriceDate")
        updateValues = ("Amazing", -15.4, date(2022, 1, 28))
        query = "Symbol='AMZN7'"
        updateResult = dbAccess.update_data(table, updateFields, updateValues, query)
        dbAccess.delete_data(table, "Symbol='AMZN7'")

        dbAccess.disconnect()

        assert updateResult == -1

    def test_update_bad_query_field(self):
        """
        Update a single record, querying field that doesn't exist.
        """
        table = self.securitiesTable
        fields = ("Name", "Symbol", "BuyPrice", "SellPrice")
        values = [("Amazon", "AMZN8", 150.01, 300.21),]

        if not dbAccess.connect():
            assert False, "unable to connect to database"
        
        assertMsg = "Failed to insert a single record"
        assert dbAccess.insert_data(table, fields, values) == True, assertMsg
        
        updateFields = ("Name", "percentChangeToday", "currentPriceDate")
        updateValues = ("Amazing", -15.4, date(2022, 1, 28))
        query = "Symbolaz='AMZN8'"
        updateResult = dbAccess.update_data(table, updateFields, updateValues, query)
        dbAccess.delete_data(table, "Symbol='AMZN8'")

        dbAccess.disconnect()

        assert updateResult == -1

    def test_update_no_query_match(self):
        """
        Update a single record, with query that has no matching records.
        """
        table = self.securitiesTable

        if not dbAccess.connect():
            assert False, "unable to connect to database"
        
        dbAccess.delete_data(table, "Symbol='r3dgeadtt'")
        
        updateFields = ("Name", "percentChangeToday", "currentPriceDate")
        updateValues = ("Amazing", -15.4, date(2022, 1, 28))
        query = "Symbol='r3dgeadtt'"
        assert dbAccess.update_data(table, updateFields, updateValues, query) == 0
        
        dbAccess.disconnect()

    # To test: single record, multiple records, no matching records.
    # Various field types - string, numeric and date.
    # Single field equality query, multi field equality, all num < value.
    def test_select_one_record(self):
        """
        select a single record, various field types.
        """
        table = self.securitiesTable
        fields = ("Name", "Symbol", "BuyPrice", "SellPrice", "currentPriceDate")
        values = [("Amazon", "AMZN9", 150.01, 300.21, date(2023, 3, 28)),]

        if not dbAccess.connect():
            assert False, "unable to connect to database"
        
        assertMsg = "Failed to insert a single record"
        assert dbAccess.insert_data(table, fields, values) == True, assertMsg
        
        selectFields = ("Name", "Symbol", "SellPrice", "currentPriceDate")
        query = "Symbol='AMZN9'"
        data = dbAccess.select_data(table, selectFields, query)
        dbAccess.delete_data(table, "Symbol='AMZN9'")

        dbAccess.disconnect()

        assert len(data) == 1
        assert data[0]["Name"] == "Amazon"
        assert data[0]["Symbol"] == "AMZN9"
        assert data[0]["SellPrice"] == Decimal('300.21')
        assert data[0]["currentPriceDate"] == date(2023, 3, 28)


    def test_select_multiple_records(self):
        """
        select a several records, various field types.
        """
        table = self.securitiesTable
        fields = ("Name", "Symbol", "BuyPrice", "SellPrice", "currentPriceDate")
        values = [  ("Amazon", "AMZN10", 150.01, 30.21,  date(2023, 1, 28)),
                    ("Amazon", "AMZN11", 350.01, 200.21, date(2022, 3, 26)), 
                    ("Amazon", "AMZN12", 50.01,  100.21, date(2021, 6, 8))]

        if not dbAccess.connect():
            assert False, "unable to connect to database"
        
        assertMsg = "Failed to insert records"
        assert dbAccess.insert_data(table, fields, values) == True, assertMsg
        
        selectFields = ("Name", "Symbol", "SellPrice", "currentPriceDate")
        query = "Name='Amazon'"
        data = dbAccess.select_data(table, selectFields, query)
        dbAccess.delete_data(table, "Symbol in ('AMZN10', 'AMZN11', 'AMZN12')")

        dbAccess.disconnect()

        assert len(data) == 3
        assert data[2]["Name"] == "Amazon"
        assert data[2]["Symbol"] == "AMZN12"
        assert data[2]["SellPrice"] == Decimal('100.21')
        assert data[2]["currentPriceDate"] == date(2021, 6, 8)


    def test_select_zero_records(self):
        """
        Query with no matches.
        """
        table = self.securitiesTable

        if not dbAccess.connect():
            assert False, "unable to connect to database"
        
        selectFields = ("Name", "Symbol", "SellPrice", "currentPriceDate")
        query = "Symbol='ZZDDER'"
        data = dbAccess.select_data(table, selectFields, query)
        assert len(data) == 0, "Found a non-existent record!"

        dbAccess.disconnect()

    def test_select_multi_field_query(self):
        """
        select one record, with query containing multiple fields.
        """
        table = self.securitiesTable
        fields = ("Name", "Symbol", "BuyPrice", "SellPrice", "currentPriceDate")
        values = [  ("Amazon", "AMZN13", 150.01, 30.21,  date(2023, 1, 28)),
                    ("Amazon", "AMZN14", 350.01, 200.21, date(2022, 3, 26)), 
                    ("Amazon", "AMZN15", 50.01,  100.21, date(2021, 6, 8))]

        if not dbAccess.connect():
            assert False, "unable to connect to database"
        
        assertMsg = "Failed to insert records"
        assert dbAccess.insert_data(table, fields, values) == True, assertMsg
        
        selectFields = ("Name", "Symbol", "SellPrice", "currentPriceDate")
        query = "Name='Amazon' AND BuyPrice=350.01"
        data = dbAccess.select_data(table, selectFields, query)
        dbAccess.delete_data(table, "Symbol in ('AMZN13', 'AMZN14', 'AMZN15')")

        dbAccess.disconnect()

        assert len(data) == 1
        assert data[0]["Name"] == "Amazon"
        assert data[0]["Symbol"] == "AMZN14"
        assert data[0]["SellPrice"] == Decimal('200.21')



    def test_select_less_than_query(self):
        """
        select one record, with query containing <.
        """
        table = self.securitiesTable
        fields = ("Name", "Symbol", "BuyPrice", "SellPrice", "currentPriceDate")
        values = [  ("Amazon", "AMZN16", 150.01, 30.21,  date(2023, 1, 28)),
                    ("Amazon", "AMZN17", 350.01, 200.21, date(2022, 3, 26)), 
                    ("Amazon", "AMZN18", 50.01,  100.21, date(2021, 6, 8))]

        if not dbAccess.connect():
            assert False, "unable to connect to database"
        self.wipeTables()
        
        assertMsg = "Failed to insert records"
        assert dbAccess.insert_data(table, fields, values) == True, assertMsg
        
        selectFields = ("Name", "Symbol", "SellPrice", "currentPriceDate")
        query = "BuyPrice < 350.01"
        data = dbAccess.select_data(table, selectFields, query)
        dbAccess.delete_data(table, "Symbol in ('AMZN16', 'AMZN17', 'AMZN18')")

        dbAccess.disconnect()

        assert len(data) == 2
        assert data[1]["Symbol"] == "AMZN18"
        assert data[1]["SellPrice"] == Decimal('100.21')


    
    def test_execute_update(self):
        """
        Run an update that accesses multiple tables.
        """
        if not dbAccess.connect():
            assert False, "unable to connect to database"
        
        # Add record to securities.
        table = self.securitiesTable
        myDate = date(2022, 11, 18)
        fields = ("Name", "Symbol", "BuyPrice", "SellPrice")
        values = [("Amazon", "AMZN19", 150.01, 300.21),]
        assertMsg = "Failed to insert a single record"
        assert dbAccess.insert_data(table, fields, values) == True, assertMsg

        # Get id for just added security.
        selectFields = ("ID",)
        query = "Symbol='AMZN19'"
        data = dbAccess.select_data(table, selectFields, query)
        myId = data[0]["ID"]

        # Add corresponding record to daily prices.
        priceTable = self.dailyPricesTable
        priceFields = ("SecurityId", "PriceDate", "price")
        priceValues = [(myId, myDate, "299.32")]

        assertMsg = "Failed to insert data into daily price history"
        assert dbAccess.insert_data(priceTable, priceFields, priceValues) == True, assertMsg

        # Run the test - update currentPrice, currentPriceDate in securities based on value
        # from daily prices table
        params = (myId, myDate, myDate)
        query = f"UPDATE {table} SET currentPrice = "
        query += f"(SELECT price FROM {priceTable} "
        query += "WHERE SecurityId=%s AND PriceDate=%s), "
        query += "currentPriceDate = %s "

        #query = "UPDATE %s SET currentPrice = " % (table,)
        #query += "(SELECT price FROM %s " % (priceTable,)
        #query += "WHERE SecurityId=%s AND PriceDate='%s'), " % (myId, myDate)
        #query += "currentPriceDate = '%s' " % (myDate,)
        executeResult = dbAccess.execute_update_data(query, params)

        # Verify that price was updated.
        data = dbAccess.select_data(table, ("currentPrice",), "Symbol='AMZN19'")

        # Delete records from both tables.
        dbAccess.delete_data(table, "Symbol='AMZN19'")
        dbAccess.delete_data(priceTable, "SecurityId=%s AND PriceDate='%s'" % (myId, myDate))

        dbAccess.disconnect()

        assert executeResult == 1
        assert data[0]["currentPrice"] == Decimal('299.32')
