import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import unittest
from unittest.mock import patch, MagicMock, Mock
from pandas.testing import assert_frame_equal
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service as Chrome
from selenium.webdriver import Chrome as ChromeDriver
import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_scraping import NFTScraper


class TestNFTScraper(unittest.TestCase):
    @patch.object(ChromeDriver, "get")
    @patch.object(ChromeDriver, "execute_script")
    def setUp(self, mock_execute_script, mock_get):
        self.scraper = NFTScraper()
        self.scraper.driver = ChromeDriver(service=Chrome())
        mock_get.return_value = None
        self.mock_execute_script = mock_execute_script

    def tearDown(self):
        self.scraper.driver.quit()

    @patch("src.data_scraping.NFTScraper.collect_screen_data")
    @patch.object(ChromeDriver, "get")
    def test_initialization(self, mock_get, mock_collect_screen_data):
        self.assertIsInstance(self.scraper.driver, ChromeDriver)
        self.mock_execute_script.assert_called_once_with(
            "chrome.settingsPrivate.setDefaultZoom(0.25);"
        )
        mock_get.assert_called_once_with("chrome://settings/")
        expected_columns = [
            "Rank",
            "Collection",
            "Volume",
            "24h %",
            "7d %",
            "Floor Price",
            "Owners",
            "Items",
        ]
        self.assertEqual(list(self.scraper.table.columns), expected_columns)
    @patch("src.data_scraping.NFTScraper.collect_screen_data")
    def test_extract_text_from_data(self, mock_collect_screen_data):
        element = Mock()
        element.text = "1\nCollection 1\n100\n\n0.1\n50\n50%\n10"
        mock_collect_screen_data.return_value = [element]
        data = self.scraper.extract_text_from_data([element])
        expected_data = ["1", "Collection 1", "100", "", "0.1", "50", "50%", "10"]
        self.assertEqual(data, expected_data)

    @patch("src.data_scraping.NFTScraper.slice_table_data")
    def test_convert_row_data_to_table(self, mock_slice_table_data):
        mock_slice_table_data.return_value = [
            ["1", "Collection 1", "100", "+10%", "0.1", "50", "50%", "10", "25%", "20"],
            ["2", "Collection 2", "200", "-5%", "0.2", "30", "40%", "8", "20%", "15"],
        ]
        data = self.scraper.convert_row_data_to_table(
            mock_slice_table_data.return_value
        )
        expected_rank = 1
        expected_collection = "Collection 1"
        expected_shape = (2, 10)

        self.assertEqual(int(data.iloc[0]["Rank"]), expected_rank)
        self.assertEqual(data.iloc[0]["Collection"], expected_collection)
        self.assertEqual(data.shape, expected_shape)

    @patch("src.data_scraping.NFTScraper.collect_screen_data")
    def test_filling_missing_data(self, mock_collect_screen_data):
        data = ["1", "Collection 1", "100", "", "0.1", "50", "50%", "10"]
        expected_data = ["1", "Collection 1", "100", "", "0.1", "50", "50%", "10"]
        self.scraper.filling_missing_data(data)
        self.assertEqual(data, expected_data)


if __name__ == "__main__":
    unittest.main()
