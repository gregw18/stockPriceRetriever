"""
File to test retrieving some settings.
V0.01, October 27, 2022, GAW
"""

from . import addSrcToPath

import pytest

import settings

@pytest.mark.unit
def test_rds_connection():
    mysettings = settings.Settings.instance()
    assert mysettings.rds_db_name == "stock_retriever_db"

def test_test_tables():
    """
    Verify that if call use_test_tables twice, still end up with correct table names.
    Since settings is a singleton, and other tests are also calling use_test_tables, can't
    assume that have expected name. So, manually set expected prod name, call, reset
    when done.
    """
    mysettings = settings.Settings.instance()

    origAdminName = mysettings.db_admin_table_name

    expectedName = "admin"
    mysettings.db_admin_table_name = expectedName
    mysettings.use_test_tables()

    assert mysettings.db_admin_table_name == "test_" + expectedName

    # Call second time, verify that name didn't change.
    mysettings.use_test_tables()
    
    assert mysettings.db_admin_table_name == "test_" + expectedName

    mysettings.db_admin_table_name = origAdminName
