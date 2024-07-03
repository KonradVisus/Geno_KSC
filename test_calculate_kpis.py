import unittest
from datetime import datetime
from dateutil.relativedelta import relativedelta
from calculate_kpis import get_workdays


class TestGetWorkdays(unittest.TestCase):
    def test_get_workdays(self):
        # Test case 1: Calculate workdays for a single month
        t = datetime(2024, 1, 1)
        months = [1]
        expected_result = {1: 22}
        self.assertEqual(get_workdays(t, months), expected_result)

    def test_get_workdays2(self):
        # Test case 2: Calculate workdays for multiple months
        t = datetime(2024, 1, 1)
        months = [1, 2, 3]
        expected_result = {1: 22, 2: 21, 3: 20}
        self.assertEqual(get_workdays(t, months), expected_result)

    def test_get_workdays3(self):
        # Test case 3: Calculate workdays for a different year
        t = datetime(2024, 12, 1)
        months = [12]
        expected_result = {12: 20}
        self.assertEqual(get_workdays(t, months), expected_result)


if __name__ == "__main__":
    unittest.main()
