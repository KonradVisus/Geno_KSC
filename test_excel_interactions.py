import unittest
from datetime import datetime
from excel_interactions import available_data
import pandas as pd


class TestAvailableData(unittest.TestCase):
    def test_available_data(self):
        # Test case 1: All dataframes have the same available months
        df_mail_order = pd.DataFrame(
            {
                "Zeitstempel": [
                    datetime(2024, 1, 1),
                    datetime(2024, 2, 1),
                    datetime(2024, 3, 1),
                ],
            }
        )
        df_mail_service = pd.DataFrame(
            {
                "Zeitstempel": [
                    datetime(2024, 1, 1),
                    datetime(2024, 2, 1),
                    datetime(2024, 3, 1),
                ],
            }
        )
        df_correspondence = pd.DataFrame(
            {
                "Zeitstempel": [
                    datetime(2024, 1, 1),
                    datetime(2024, 2, 1),
                    datetime(2024, 3, 1),
                ],
            }
        )
        df_vak = pd.DataFrame(
            {
                "Zeitstempel": [
                    datetime(2024, 1, 1),
                    datetime(2024, 2, 1),
                    datetime(2024, 3, 1),
                ],
            }
        )
        expected_result = [1, 2, 3]
        self.assertEqual(
            available_data(df_mail_order, df_mail_service, df_correspondence, df_vak),
            expected_result,
        )

    def test_available_data2(self):
        # Test case 2: Different available months in dataframes
        df_mail_order = pd.DataFrame(
            {
                "Zeitstempel": [
                    datetime(2024, 1, 1),
                    datetime(2024, 2, 1),
                    datetime(2024, 3, 1),
                ],
            }
        )
        df_mail_service = pd.DataFrame(
            {
                "Zeitstempel": [
                    datetime(2024, 2, 1),
                    datetime(2024, 3, 1),
                    datetime(2024, 4, 1),
                ],
            }
        )
        df_correspondence = pd.DataFrame(
            {
                "Zeitstempel": [
                    datetime(2024, 1, 1),
                    datetime(2024, 3, 1),
                    datetime(2024, 4, 1),
                ],
            }
        )
        df_vak = pd.DataFrame(
            {
                "Zeitstempel": [
                    datetime(2024, 1, 1),
                    datetime(2024, 2, 1),
                    datetime(2024, 4, 1),
                ],
            }
        )
        expected_result = []
        self.assertEqual(
            available_data(df_mail_order, df_mail_service, df_correspondence, df_vak),
            expected_result,
        )


if __name__ == "__main__":
    unittest.main()
