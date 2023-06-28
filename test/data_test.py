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



if __name__ == "__main__":
    unittest.main()
