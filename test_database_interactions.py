import unittest
from datetime import datetime
from database_interactions import determine_missing_data


class TestDetermineMissingData(unittest.TestCase):
    def test_determine_missing_kpis(self):
        # Test case 1: No missing months
        t1 = datetime(2024, 1, 1)
        expected_result1 = []
        self.assertEqual(determine_missing_data(t1), expected_result1)

    def test_determine_missing_kpis(self):
        # Test case 1: No missing months
        t1 = datetime(2024, 4, 1)
        expected_result1 = [1, 3, 4]
        self.assertEqual(determine_missing_data(t1), expected_result1)


if __name__ == "__main__":
    unittest.main()
