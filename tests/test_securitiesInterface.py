"""
File to unit test securitiesInterface - mocks dbAccess.
V0.01, November 22, 2022, GAW
"""

from datetime import date
from decimal import *
import pytest
from unittest.mock import Mock, patch

from . import addSrcToPath

from securitiesInterface import SecuritiesInterface
from security import Security

"""
To Test
get_securities
    No connection
    No records
    One record
    Multiple records
update_security
    No matching security in table
    No fields to update
    Invalid field to update
    Update one field
    Update multiple fields
delete_security
    No matching security
    Matching security
add_security
    Valid values
    Matching symbol, differing capitalization
mark_historical_data_retrieved
    Invalid id
    Valid id
"""

@pytest.mark.unit
class TestSecuritiesInterface():
    def setup(self):
        self.security1 = {"id": 1,
                            "name": "Apple",
                            "symbol": "AAPL", 
                            "fullHistoryDownloaded": True,
                            "buyPrice": 102.31, 
                            "sellPrice": 202.33, 
                            "currentPrice": 154.32,
                            "currentDate": date(2022, 11, 21), 
                            "previousClosePrice": 156.33,
                            "52weekLowPrice": 132.1,
                            "52weekHighPrice": 187.4, 
                            "percentChangeToday": 5.4}
        self.security2 = {"id": 3,
                            "name": "Meta",
                            "symbol": "FBOOK", 
                            "fullHistoryDownloaded": True,
                            "buyPrice": 202.31, 
                            "sellPrice": 302.33, 
                            "currentPrice": 54.32,
                            "currentDate": date(2022, 11, 21), 
                            "previousClosePrice": 56.33,
                            "52weekLowPrice": 32.1,
                            "52weekHighPrice": 587.4, 
                            "percentChangeToday": -15.4}

    def test_get_securities_no_records(self):
        """
        No records when try to retrieve securities, should result in empty dictionary.
        """
        with patch('securitiesInterface.dbAccess.select_data', return_value=Mock()) as mock_select:
            mock_select.return_value = []
            myInterface = SecuritiesInterface()
            results = myInterface.get_securities()
            assert len(results) == 0
            mock_select.assert_called_once()

    def test_get_securities_one_record(self):
        """
        One record when try to retrieve securities, should result in one item in dictionary.
        """
        with patch('securitiesInterface.dbAccess.select_data', return_value=Mock()) as mock_select:
            data = [self.security1]
            mock_select.return_value = data
            myInterface = SecuritiesInterface()
            results = myInterface.get_securities()
            assert len(results) == 1
            mock_select.assert_called_once()

    def test_get_securities_two_records(self):
        """
        Two records when try to retrieve securities, should result in two items in dictionary.
        """
        with patch('securitiesInterface.dbAccess.select_data', return_value=Mock()) as mock_select:
            data = [self.security1, self.security2]
            mock_select.return_value = data
            myInterface = SecuritiesInterface()
            results = myInterface.get_securities()
            assert len(results) == 2
            mock_select.assert_called_once()

    def test_add_security_already_exists(self):
        """
        Try inserting a security when symbol already exists - expect to fail.
        """
        with patch('securitiesInterface.dbAccess.select_data', return_value=Mock()) as mock_select:
            mock_select.return_value = [{'symbol': "AAPL"}]
            testSecurity = self.createSecurity("Apple", "aapl", 103.4, 201.1)
            myInterface = SecuritiesInterface()
            result = myInterface.add_security(testSecurity)
            assert result == False
            mock_select.assert_called_once()

    def test_add_security_succeeds(self):
        """
        Try inserting a security successfully.
        """
        with patch('securitiesInterface.dbAccess.select_data', return_value=Mock()) as mock_select:
            mock_select.return_value = []
            with patch('securitiesInterface.dbAccess.insert_data', return_value=Mock()) as mock_insert:
                mock_insert.return_value = 1
                testSecurity = self.createSecurity("Apple", "aapl", 103.4, 201.1)
                myInterface = SecuritiesInterface()
                result = myInterface.add_security(testSecurity)
                assert result == True

    def test_update_security_match(self):
        """
        Try updating a security that exists.
        """
        with patch('securitiesInterface.dbAccess.update_data', return_value=Mock()) as mock_update:
            mock_update.return_value = 1
            myInterface = SecuritiesInterface()
            wasUpdated = myInterface.update_security(4, ["buyPrice"], [135.4])
            assert wasUpdated == True
            mock_update.assert_called_once()

    def test_update_security_no_match(self):
        """
        Try updating a security that doesn't exist.
        """
        with patch('securitiesInterface.dbAccess.update_data', return_value=Mock()) as mock_update:
            mock_update.return_value = 0
            myInterface = SecuritiesInterface()
            wasUpdated = myInterface.update_security(5, ["buyPrice"], [135.4])
            assert wasUpdated == False
            mock_update.assert_called_once()

    def test_delete_security_match(self):
        """
        Try deleting a security that exists.
        """
        with patch('securitiesInterface.dbAccess.delete_data', return_value=Mock()) as mock_delete:
            mock_delete.return_value = 1
            myInterface = SecuritiesInterface()
            wasDeleted = myInterface.delete_security(4)
            assert wasDeleted == True
            mock_delete.assert_called_once_with(myInterface.securitiesTable, "id=4")

    def test_delete_security_no_match(self):
        """
        Try deleting a security that doesn't exist.
        """
        with patch('securitiesInterface.dbAccess.delete_data', return_value=Mock()) as mock_delete:
            mock_delete.return_value = 0
            myInterface = SecuritiesInterface()
            wasDeleted = myInterface.delete_security(5)
            assert wasDeleted == False
            mock_delete.assert_called_once_with(myInterface.securitiesTable, "id=5")


    def createSecurity(self, name, symbol, buyPrice, sellPrice):
        mySec = Security()
        mySec.pop(name, symbol, buyPrice, sellPrice, 0)
        return mySec
