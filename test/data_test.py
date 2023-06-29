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

    def setUp(self):
        self.scraper = NFTScraper()

    def tearDown(self):
        self.scraper.driver.quit()

    @patch('NFTScraper.scrape_data')
    @patch('src.data_scraping.asyncio.run')
    def test_main(self, mock_run, mock_scrape_data):
        pages_of_scraping = 2
        self.scraper.scrape_data = MagicMock()
        mock_run.return_value = None

        self.scraper.main(pages_of_scraping)

        mock_run.assert_called_once_with(self.scraper.scrape_data(pages_of_scraping))
        self.scraper.scrape_data.assert_called_once_with(pages_of_scraping)

    @patch('src.data_scraping.time.sleep')
    @patch('src.data_scraping.Keys')
    @patch('src.data_scraping.NFTScraper.driver')
    def test_scrolling_down_to_bottom(self, mock_driver, mock_keys, mock_sleep):
        mock_html = mock_driver.find_element.return_value
        mock_keys.END = 'END'

        self.scraper.scrolling_down_to_bottom()

        mock_driver.find_element.assert_called_once_with(self.scraper.By.TAG_NAME, 'html')
        mock_html.send_keys.assert_called_once_with(mock_keys.END)
        mock_sleep.assert_called_once_with(1)

    @patch('src.data_scraping.wait')
    def test_click_button_successful(self, mock_wait):
        mock_button = mock_wait.until.return_value
        mock_button.click.return_value = None

        result = self.scraper.click_button('xpath')

        mock_wait.until.assert_called_once_with(self.scraper.EC.element_to_be_clickable.return_value)
        mock_button.click.assert_called_once_with()
        self.assertTrue(result)

    @patch('src.data_scraping.time.sleep')
    @patch('NFTScraper.wait')
    def test_click_button_unsuccessful(self, mock_wait, mock_sleep):
        mock_wait.until.side_effect = [TimeoutException]
        mock_sleep.return_value = None

        result = self.scraper.click_button('xpath')

        mock_wait.until.assert_called_once_with(self.scraper.EC.element_to_be_clickable.return_value)
        self.assertFalse(result)
        mock_sleep.assert_called_once_with(1)

    def test_concatenate_table(self):
        table1 = MagicMock()
        table2 = MagicMock()
        pd.concat.return_value = 'concatenated_table'

        result = self.scraper.concatenate_table(table1, table2)

        pd.concat.assert_called_once_with([table1, table2])
        self.assertEqual(result, 'concatenated_table')

    def test_delete_duplicate_rows(self):
        rows = MagicMock()
        rows.drop_duplicates.return_value = 'duplicated_rows'

        result = self.scraper.delete_duplicate_rows(rows)

        rows.drop_duplicates.assert_called_once_with(subset=['rank'])
        self.assertEqual(result, 'duplicated_rows')



if __name__ == "__main__":
    unittest.main()
