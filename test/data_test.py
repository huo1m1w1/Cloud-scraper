import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import unittest
from unittest.mock import MagicMock
from your_module import NFT_scraper

class NFTScraperTestCase(unittest.TestCase):
    def setUp(self):
        self.scraper = NFT_scraper()

    def tearDown(self):
        self.scraper.driver.quit()

    def test_initialization(self):
        self.assertIsInstance(self.scraper.driver, MagicMock)
        self.assertEqual(self.scraper.driver.get.call_count, 1)
        self.assertEqual(
            self.scraper.driver.get.call_args[0][0], "chrome://settings/"
        )
        self.assertEqual(self.scraper.driver.execute_script.call_count, 1)
        self.assertEqual(
            self.scraper.driver.execute_script.call_args[0][0],
            "chrome.settingsPrivate.setDefaultZoom(0.25);",
        )
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