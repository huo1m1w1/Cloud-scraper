import unittest
from unittest.mock import MagicMock, call, patch
import time
import sys
import os
import pandas as pd
import asyncio
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
import tracemalloc
tracemalloc.start()
# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.data_scraper import NFTScraper


class CustomException(Exception):
    pass


class NFTScraperTest(unittest.TestCase):
    def setUp(self):
        self.button_click_count = 0
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.scraper = NFTScraper()
        # self.driver = webdriver.Chrome()  # Replace with the appropriate WebDriver for your browser
        self.wait = WebDriverWait(self.scraper.driver, 10)

    def tearDown(self):
        self.loop.close()
        self.scraper.driver.quit()

    async def collect_screen_data(self):
        try:
            print(self.scraper.XPATH)
            element = await self.wait.until(EC.presence_of_element_located((By.XPATH, self.scraper.XPATH)))
            screen_data = element.text  # Replace with the logic to extract the desired screen data
            return screen_data
        except TimeoutException as timeout_error:
            print(f"Timeout occurred: {str(timeout_error)}")
        except NoSuchElementException as element_error:
            print(f"Element not found: {str(element_error)}")
        except StaleElementReferenceException as stale_error:
            print(f"Stale element reference: {str(stale_error)}")   

    async def test_collect_screen_data(self):
        await self.scraper.driver.get(self.scraper.URL)
        result = await self.collect_screen_data()
        print(result)
        self.assertIsNotNone(result, msg="Test value is none.")
        # self.assertGreater(len(result), 0)
        # Process the result or perform assertions

    def test_collect_screen_data_wrapper(self):
        self.scraper.driver.get(self.scraper.URL)
        result = self.scraper.collect_screen_data()
        print(result)
        self.assertIsNotNone(result)

        # await self.test_collect_screen_data()

    @patch("selenium.webdriver.Chrome.find_element")
    def test_click_button(self, mock_find_element):
        key = "//*[@id='main']/div/div[2]/button[2]"  # Replace with the XPath of the button element
        mock_find_element.return_value.is_displayed.return_value.__eq__.return_value = True
        self.assertTrue(self.click_button(key))
        mock_find_element.assert_called_once_with(By.XPATH, key)
        self.assertEqual(self.button_click_count, 1)

    def click_button(self, key):
        """Click the button and return True if successful, False otherwise."""       

        try:
            button = self.wait.until(EC.element_to_be_clickable((By.XPATH, key)))
            button.click()
            self.button_click_count += 1
            time.sleep(1)
            return True
        except TimeoutException:
            return False

    def test_extract_text_from_data(self):
        mock_data = MagicMock()
        mock_data.text = "Test Data\nSecond Line"

        result = self.scraper.extract_text_from_data([mock_data])

        self.assertEqual(result, ["Test Data", "Second Line"])

    def test_filling_missing_data(self):
        data = ["Value 1", "Value 2", "Value 3", "Value 4", "Value 5", "Value 6", "Value 7", "Value 8", "—"]
        expected_data = ["Value 1", "Value 2", "Value 3", "Value 4", "Value 5", "Value 6", "Value 7", "Value 8", "—", "—"]

        self.scraper.filling_missing_data(data)

        self.assertEqual(data, expected_data)

    def test_slice_table_data(self):
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        expected_data = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]]

        result = self.scraper.slice_table_data(data)

        self.assertEqual(result, expected_data)

    def test_convert_row_data_to_table(self):
        data = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]]
        expected_columns = ["rank", "collection", "volume", "change", "floor_price",
                            "sales", "ownership_percentage", "owners", "items_percentage", "items"]

        table = self.scraper.convert_row_data_to_table(data)

        self.assertIsInstance(table, pd.DataFrame)
        self.assertEqual(list(table.columns), expected_columns)
        self.assertEqual(len(table), 2)
        self.assertEqual(table["rank"].tolist(), [1, 11])
        self.assertEqual(table["collection"].tolist(), [2, 12])
        # Test the remaining columns

    def test_scrolling_screen_down(self):
        mock_execute_script = self.scraper.driver.execute_script = MagicMock()

        pixels = 2000
        self.scraper.scrolling_screen_down(pixels)

        mock_execute_script.assert_called_once_with("window.scrollBy(0, 2000);")

    def test_scrolling_down_to_bottom(self):
        mock_html_element = MagicMock()
        # Mock the return value of driver.find_element
        self.scraper.driver.find_element = MagicMock(return_value=mock_html_element)

        # Call the method being tested
        self.scraper.scrolling_down_to_bottom()

        # Assert the expected call to find_element
        self.scraper.driver.find_element.assert_called_once_with(By.TAG_NAME, "html")
        mock_html_element.send_keys.assert_called_once_with(Keys.END)

    def test_click_button_element_not_found(self):
        # Mocking driver and other dependencies
        self.scraper.driver.find_element = MagicMock(side_effect=[False, False, True])  # Return False twice, then True
        self.scraper.driver.get = MagicMock()
        self.scraper.scrolling_screen_down = MagicMock()
        self.scraper.click_button("//*[@id='main']/div/div[2]/button[2]")
        self.scraper.click_button("//*[@id='main']/div/div[2]/button[2]")
        self.scraper.click_button("//*[@id='main']/div/div[2]/button[2]")

        # Assertions
        self.assertEqual(self.scraper.driver.find_element.call_count, 3)
        expected_calls = [call(By.XPATH, "//*[@id='main']/div/div[2]/button[2]")]
        self.scraper.driver.find_element.assert_has_calls(expected_calls)

    def test_concatenate_table(self):
        table1 = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        table2 = pd.DataFrame({"A": [7, 8, 9], "B": [10, 11, 12]})
        expected_table = pd.DataFrame({"A": [1, 2, 3, 7, 8, 9], "B": [4, 5, 6, 10, 11, 12]})

        result = self.scraper.concatenate_table(table1, table2).reset_index(drop=True)

        pd.testing.assert_frame_equal(result, expected_table)

    def test_delete_duplicate_rows(self):
        rows = pd.DataFrame({"rank": [1, 2, 3, 3, 4, 5], "B": [6, 7, 8, 8, 9, 10]})
        expected_rows = pd.DataFrame({"rank": [1, 2, 3, 4, 5], "B": [6, 7, 8, 9, 10]})

        result = self.scraper.delete_duplicate_rows(rows).reset_index(drop=True)

        pd.testing.assert_frame_equal(result, expected_rows)    

    def test_scrape_data(self):

        with patch.object(self.scraper.driver, 'get', return_value=None) as mock_get:
            with patch.object(self.scraper, 'collect_screen_data') as mock_collect_screen_data:
                mock_collect_screen_data.return_value = [[1, 2, 3]]  # Set the return value of collect_screen_data
                with patch.object(self.scraper, 'extract_text_from_data') as mock_extract_text_from_data:
                    with patch.object(self.scraper, 'scrolling_screen_down') as mock_scrolling_screen_down:
                        with patch.object(self.scraper, 'click_button') as mock_click_button:
                            with patch.object(self.scraper, 'convert_row_data_to_table') as mock_convert_row_data_to_table:
                                with patch.object(self.scraper, 'delete_duplicate_rows') as mock_delete_duplicate_rows:
 
                                    try:
                                        asyncio.run(self.scraper.scrape_data(2))
                                    except CustomException:
                                        pass

        mock_get.assert_called_once_with(NFTScraper.URL)
        mock_collect_screen_data.assert_called_with()
        mock_extract_text_from_data.assert_called_with([[1, 2, 3]])  # Update the assertion
        self.assertEqual(mock_scrolling_screen_down.call_count, 8)
        mock_scrolling_screen_down.assert_called()
        self.assertEqual(mock_click_button.call_count, 2)
        self.assertEqual(mock_convert_row_data_to_table.call_count, 2)  # Verify the call count
        self.assertEqual(mock_delete_duplicate_rows.call_count, 2)

    def test_close_driver(self):
        self.scraper.driver.quit = MagicMock()
        self.scraper.driver.quit()
        self.scraper.driver.quit.assert_called_once()


if __name__ == "__main__":
    unittest.main()









