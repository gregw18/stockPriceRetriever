"""
2nd file to test Security class - get_changed_fields and update_values.
V0.01, December 10, 2022, GAW
"""

from datetime import date
import pytest

from . import addSrcToPath

from security import Security, PriceInfo

"""
get_changed_fields
    Verify correct values get to correct fields
    Verify unchanged fields don't change
    Verify get nothing back if no values change.

update_values
    Verify correct values get to correct fields.
"""

@pytest.mark.unit
class TestSecurity2():
    #def setup(self):
    #    self.testPrice = 11.59
    #    self.testPriceInfo = security.PriceInfo()
    #    self.testPriceInfo.currentPrice = self.testPrice
    #    self.testPriceInfo.lastClosePrice = 42.33
    #    self.testPriceInfo.low52Week = 33.21
    #    self.testPriceInfo.high52Week = 64.34

    def _create_priceInfo(self):
        """
        Test updating one field.
        """
        #Create a security with data from PriceInfo.
        newInfo = PriceInfo()
        newInfo.currentPrice = 101.2
        newInfo.lastClosePrice = 101.1
        newInfo.low52Week = 78.45
        newInfo.high52Week = 104.3

        return newInfo

    def test_get_changed_fields_one_field(self):
        """
        Test updating one field.
        """
        #Create a security with data from PriceInfo.
        newInfo = self._create_priceInfo()
        testSecurity = Security()
        testSecurity.pop_with_priceInfo("TEST1", "TST1", 85, 110, newInfo)

        # Change one value in priceInfo, verify get just that field back.
        newInfo.low52Week = 68
        changedFieldNames, newValues = testSecurity.get_changed_fields(newInfo, date.today())

        assert changedFieldNames[0] == "52WeekLowPrice"
        assert newValues[0] == newInfo.low52Week
        assert len(changedFieldNames) == 1
        assert len(newValues) == 1

    def test_get_changed_fields_date_only(self):
        """
        Test that recognizes when only currentPriceDate field changes.
        """
        #Create a security with data from PriceInfo.
        newInfo = self._create_priceInfo()
        testSecurity = Security()
        testSecurity.pop_with_priceInfo("TEST1", "TST1", 85, 110, newInfo)
        testSecurity.currentPriceDate = date(2022, 12, 30)

        changedFieldNames, newValues = testSecurity.get_changed_fields(newInfo, date.today())

        assert changedFieldNames[0] == "currentPriceDate"
        assert newValues[0] == date.today()
        assert len(changedFieldNames) == 1
        assert len(newValues) == 1

    def test_get_changed_fields_all_fields(self):
        """
        Test updating all fields.
        """
        #Create a security with data from PriceInfo.
        newInfo = self._create_priceInfo()

        testSecurity = Security()
        testSecurity.pop_with_priceInfo("TEST2", "TST2", 85, 110, newInfo)

        # Change all values in priceInfo, verify get everything back.
        newInfo.currentPrice += 11.2
        newInfo.lastClosePrice -= 10.1
        newInfo.low52Week -= 8.4
        newInfo.high52Week += 10.33
        changedFieldNames, newValues = testSecurity.get_changed_fields(newInfo, date.today())

        assert "currentPrice" in changedFieldNames
        assert "currentPriceDate" in changedFieldNames
        assert "previousClosePrice" in changedFieldNames
        assert "52WeekLowPrice" in changedFieldNames
        assert "52WeekHighPrice" in changedFieldNames
        assert newValues[0] == newInfo.currentPrice
        assert newValues[1] == date.today()
        assert newValues[2] == newInfo.lastClosePrice
        assert newValues[3] == newInfo.low52Week
        assert newValues[4] == newInfo.high52Week
        assert len(changedFieldNames) == 5
        assert len(newValues) == 5


    def test_get_changed_fields_no_changes(self):
        """
        No changes, expect empty lists back.
        """
        #Create a security with data from PriceInfo.
        newInfo = self._create_priceInfo()
        testSecurity = Security()
        testSecurity.pop_with_priceInfo("TEST3", "TST3", 85, 110, newInfo)

        changedFieldNames, newValues = testSecurity.get_changed_fields(newInfo, date.today())

        assert len(changedFieldNames) == 0
        assert len(newValues) == 0

    def test_update_values_all_fields(self):
        """
        Test updating all fields.
        """
        #Create a security with data from PriceInfo.
        newInfo = self._create_priceInfo()

        testSecurity = Security()
        testSecurity.pop_with_priceInfo("TEST3", "TST3", 85, 110, newInfo)

        # Change all values in priceInfo, verify get everything back.
        newInfo.currentPrice += 11.2
        newInfo.lastClosePrice -= 10.1
        newInfo.low52Week -= 8.4
        newInfo.high52Week += 10.33
        testSecurity.update_values(newInfo)

        assert testSecurity.currentPrice == newInfo.currentPrice
        assert testSecurity.lastClosePrice == newInfo.lastClosePrice
        assert testSecurity.low52Week == newInfo.low52Week
        assert testSecurity.high52Week == newInfo.high52Week
