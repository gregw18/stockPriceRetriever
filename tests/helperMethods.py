"""
File to test retrieving the data required for web site, via the Securities class
V0.01, December 16, 2022, GAW
"""

from . import addSrcToPath

def adjust_settings_for_tests(mySettings):
    """
    Change table names during testing so that tests hit tables that are identical
    to live but which start with "test_".
    """
    mySettings.use_test_tables()
