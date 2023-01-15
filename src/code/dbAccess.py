"""
All access to RDS goes through here, then on to the PyMySQL connector. Should contain no
business logic.
V0.02, November 9, 2022
"""

import boto3
import pymysql

import settings

#print("Starting dbAccess init")
client = boto3.client('rds')
mysettings = settings.Settings.instance()
dbConn = None
connected_status = False
#print("Finished dbAccess init, connected_status=", connected_status)

# Connect to RDS.
def connect():
    global connected_status, dbConn
    if not connected_status:
        try:
            token = client.generate_db_auth_token(DBHostname=mysettings.rds_endpoint,
                                                  Port=mysettings.rds_port,
                                                  DBUsername=mysettings.rds_user_name)
            print("rds_endpoint: ", mysettings.rds_endpoint)
            print("rds port: ", mysettings.rds_port)
            print("rds_user: ", mysettings.rds_user_name)
            print("db_name: ", mysettings.rds_db_name)
            #print(f"rds token length: {len(token)}")
            #print(f"{token=}")
            ssl = {'ca': 'rds-combined-ca-bundle.pem'}
            dbConn = pymysql.connect(host=mysettings.rds_endpoint,
                                     user=mysettings.rds_user_name,
                                     password=token,
                                     database=mysettings.rds_db_name,
                                     connect_timeout=10,
                                     ssl=ssl)
            print("Connection succeeded")
            connected_status = True
        except pymysql.MySQLError as e:
            connected_status = False
            print("Error (connect), could not connect to MySQL database ", mysettings.rds_db_name)
            print(e)
    else:
        print("Warning (connect): Already connected to MySQL database")

    return connected_status

def test_rds_connection():
    global connected_status, dbConn
    print("rds_endpoint: ", mysettings.rds_endpoint)
    print("rds port: ", mysettings.rds_port)
    print("rds_user: ", mysettings.rds_user_name)
    print("db_name: ", mysettings.rds_db_name)

    try:
        if connect():
            cur = dbConn.cursor()
            cur.execute("""Select now()""")
            query_results = cur.fetchall()
            print(query_results)
            print("Connection succeeded")
            cur.close()
            disconnect()
    except pymysql.MySQLError as e:
        print("Error, could not connect to MySQL database ", mysettings.rds_db_name)
        print(e)


# Create table defined by given command.
def create_table(tableCmd):
    global connected_status, dbConn
    created = False
    if connected_status:
        cursor = dbConn.cursor()
        try:
            print("Creating table, sql= ", tableCmd)
            cursor.execute(tableCmd)
            print("Successfully created table")
            created = True
        except pymysql.MySQLError as err:
            print("Error when creating table, ", err)
        cursor.close()
    else:
        print("Error (create_table) - not connected to database.")

    return created


# Check if requested table exists.
def does_table_exist(tableName):
    global connected_status, dbConn
    exists = False
    if connected_status:
        cursor = dbConn.cursor()
        try:
            print("Checking for table ", tableName)
            sqlCmd = (
                "SELECT count(*) FROM information_schema.tables "
                "WHERE (table_schema = %s) AND (table_name = %s)"
            )
            cursor.execute(sqlCmd, (mysettings.rds_db_name, tableName))
            numTables = cursor.fetchone()[0]
            print("numTables=", numTables)
            if numTables > 0:
                exists = True
        except pymysql.MySQLError as err:
            print("Error when checking for table, ", err)
        cursor.close()
    else:
        print("Error (does_table_exist) - not connected to database.")
    print("does_table_exist for ", tableName, " found ", exists)

    return exists

# Delete requested table.
def delete_table(tableName):
    global connected_status, dbConn
    deleted = False
    if connected_status:
        cursor = dbConn.cursor()
        try:
            print("Deleting table ", tableName)
            # Apparently mySql can't escape table names, so have to do myself.
            # Assumes table name doesn't come from external source.
            sqlCmd = "DROP TABLE IF EXISTS %s " % (tableName,)
            cursor.execute(sqlCmd)
            print("last statement was: ", cursor._last_executed)
            if not does_table_exist(tableName):
                deleted = True
        except pymysql.MySQLError as err:
            print("cursor.dict: ", cursor.__dict__)
            print("dir(cursor): ", dir(cursor))
            print("last statement was: ", cursor._last_executed)
            print("Error when deleting table, ", err)
        cursor.close()
    else:
        print("Error (delete_table) - not connected to database.")
    print("delete_table for ", tableName, "found ", deleted)

    return deleted

# Insert provided data into specified table.
def insert_data(tableName, fieldNames, fieldValues):
    global connected_status, dbConn
    inserted = False
    if connected_status:
        cursor = dbConn.cursor()
        try:
            # Need to turn field names into comma-delimited string,
            # and also create a string containing a "%s, " for each field.
            formattedFieldNames = ""
            fieldPlaceholders = ""
            for fieldName in fieldNames:
                formattedFieldNames += fieldName + ", "
                fieldPlaceholders += "%s, "
            # Strip trailing ", " from both strings
            formattedFieldNames = formattedFieldNames[:-2]
            fieldPlaceholders = fieldPlaceholders[:-2]

            sqlCmd = "INSERT INTO %s " % (tableName,)
            sqlCmd += "(%s) " % formattedFieldNames
            sqlCmd += "VALUES (" + fieldPlaceholders + ")"
            print("trying data insert, sql= ", sqlCmd)

            # If inserting empty record, executemany doesn't do anything,
            # because it iterates through provided fieldValues.
            if len(fieldValues) > 0:
                cursor.executemany(sqlCmd, fieldValues)
            else:
                cursor.execute(sqlCmd)
            print("last statement was: ", cursor._last_executed)
            dbConn.commit()
            print("Successfully inserted data")
            inserted = True
        except pymysql.MySQLError as err:
            print("last statement was: ", cursor._last_executed)
            print("Error when inserting data, ", err)
        cursor.close()
    else:
        print("Error (insert_data) - not connected to database.")
    print("insert_data for table ", tableName, " resulted in ", inserted)

    return inserted

# Select data - selected fields, from specified table, matching given query.
# Returns data as list of dictionary.
# Note that if use Python to insert a date (or, presumably, a datetime) into a
# query string, it appears to end up in the final sql query looking like
# “datefield=datetime.date(2022, 11, 23)". Somehow the connector ignores this
# and passes it straight to MySql, which can’t figure out what datetime.date
# is – over the connector it gives an “execute command denied to user … for routine
# datetime.date”, while if run directly at a mysql prompt it gives the more accurate
# response “FUNCTION datetime.date does not exist”. Could use python to force the
# datetime.date into a particular string format, then specify that format in the Sql
# command as well, but would have to do that everywhere call select_data.
# Alternatively, seems that can pass parameters for the where clause to the execute
# command, and those parameters can be datetime.date, which the connector does correctly
# translate.
def select_data(tableName, fieldNames, query, queryParams=()):
    global connected_status, dbConn
    returnData = None
    if connected_status:
        #cursor = dbConn.cursor(buffered=True, dictionary=True)
        cursor = pymysql.cursors.DictCursor(dbConn)
        try:
            formattedFieldNames = ""
            for fieldName in fieldNames:
                formattedFieldNames += fieldName + ", "
            # Strip trailing ", " from string
            formattedFieldNames = formattedFieldNames[:-2]
            sqlCmd = "SELECT %s " % formattedFieldNames
            sqlCmd += "FROM %s " % (tableName, )
            sqlCmd += "WHERE %s" % (query,)
            print("trying select, sql= ", sqlCmd)
            cursor.execute(sqlCmd, queryParams)
            print("last statement was: ", cursor._last_executed)
            returnData = cursor.fetchall()
            print("returnData: ", returnData)
            #print("type(returnData)= ", type(returnData))
        except pymysql.MySQLError as err:
            print("last statement was: ", cursor._last_executed)
            print("Error when selecting data, ", err)
        cursor.close()
    else:
        print("Error (select_data) - not connected to database.")
    if not (returnData is None):
        print("select_data is returning ", len(returnData), " records.")

    return returnData


# Update one record in a table using provided fields and values.
def update_data(tableName, fieldNames, fieldValues, query):
    global connected_status, dbConn
    numUpdated = -1
    if connected_status:
        cursor = dbConn.cursor()
        try:
            # Need to turn field names and values into comma-delimited string,
            # like "field1='value1', field2='value2'" etc.
            #formattedUpdates = ""
            #for fieldName, fieldValue in zip(fieldNames, fieldValues):
            #    formattedUpdates += fieldName + "=" + fieldValue + ", "

            formattedUpdates = ""
            for fieldName in fieldNames:
                formattedUpdates += fieldName + " = %s, "

            # Strip trailing ", " from both strings
            formattedUpdates = formattedUpdates[:-2]

            sqlCmd = "UPDATE %s " % (tableName,)
            sqlCmd += "SET " + formattedUpdates
            sqlCmd += " WHERE %s " % (query,)
            print("trying data update, sql= ", sqlCmd)
            cursor.execute(sqlCmd, fieldValues)
            numUpdated = cursor.rowcount
            print("last statement was: ", cursor._last_executed)
            dbConn.commit()
            print("Successfully updated data")
        except pymysql.MySQLError as err:
            print("last statement was: ", cursor._last_executed)
            print("Error when updating data, ", err)
        cursor.close()
    else:
        print("Error (update_data) - not connected to database.")
    print("update_data for table ", tableName, " affected ", numUpdated, " records.")

    return numUpdated

# Delete requested data from specified table.
# Query should be of the form "field=`value`", with additional clauses connected by
# and or or.
def delete_data(tableName, query, queryParams=()):
    global connected_status, dbConn
    numDeleted = 0
    if connected_status:
        cursor = dbConn.cursor()
        try:
            print("Deleting data from ", tableName, ", query=", query)
            # Apparently mySql can't escape table names, so have to do myself.
            # Assumes table name doesn't come from external source.
            sqlCmd = "DELETE FROM %s " % (tableName,)
            sqlCmd += "WHERE %s " % (query,)
            cursor.execute(sqlCmd, queryParams)
            numDeleted = cursor.rowcount
            print("rowcount=", numDeleted)
            print("last statement was: ", cursor._last_executed)
            dbConn.commit()
        except pymysql.MySQLError as err:
            print("last statement was: ", cursor._last_executed)
            print("Error when deleting data, ", err)
        cursor.close()
    else:
        print("Error (delete_data) - not connected to database.")
    print("delete_data for ", tableName, " removed ", numDeleted, " records.")

    return numDeleted

# Takes given query and executes it. Intended for updates that reference more
# than one table.
def execute_update_data(query, queryParams=()):
    global connected_status, dbConn
    numUpdated = 0
    if connected_status:
        cursor = dbConn.cursor()
        try:
            print("trying execute_update_data, sql= ", query)
            cursor.execute(query, queryParams)
            numUpdated = cursor.rowcount
            print("last statement was: ", cursor._last_executed)
            dbConn.commit()
            print("Successfully updated data")
        except pymysql.MySQLError as err:
            print("last statement was: ", cursor._last_executed)
            print("Error when running execute_update_data, ", err)
        cursor.close()
    else:
        print("Error (execute_update_data) - not connected to database.")
    print("execute_update_data affected ", numUpdated, " records.")

    return numUpdated

# Runs any arbitrary command.
def execute_command(cmd):
    global connected_status, dbConn
    if connected_status:
        cursor = dbConn.cursor()
        try:
            cursor.execute(cmd)
        except pymysql.MySQLError as err:
            print("Last statement was: ", cursor._last_executed)
            print("Error when running execute_command, ", err)

# Disconnect from RDS.
def disconnect():
    global connected_status, dbConn
    if connected_status:
        dbConn.close()
        connected_status = False
        print("Closed db connection.")
