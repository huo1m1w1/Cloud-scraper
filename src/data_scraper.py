"""Python scraper to collect NFT data and image from opensea 
"""
import time
import asyncio
from pydantic import BaseModel
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class NFTData(BaseModel):
    rank: int
    collection: str
    volume: str
    change: str
    floor_price: str
    sales: str
    ownership_percentage: str
    owners: str
    items_percentage: str
    items: str


class NFTScraper:
    """Class for scraping NFT data from OpenSea."""
    URL = "https://opensea.io/rankings?sortBy=total_volume"
    XPATH = '//*[@id="main"]/div/div/div[3]/div/div[4]'

    def __init__(self):
        """Prepare selenium chrome webdriver for scraping."""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920x1080")
        options.add_argument("start-maximized")
        options.add_argument(
            "user-agent=[Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36]"
        )
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.table = pd.DataFrame(columns=NFTData.__fields__.keys())
        self.wait = WebDriverWait(self.driver, 10)

    async def collect_screen_data(self, xpath):
        """Collect dynamic website data from the current screen."""
        try:
            elements = self.wait.until(
                EC.presence_of_all_elements_located((By.XPATH, xpath))
                )
            return elements
        except TimeoutException:
            print(f"Timed out waiting for elements at XPath: {xpath}")
            return []

    def extract_text_from_data(self, data: any):
        """Extract the data and return as a list."""
        return [i.text for i in data][0].split("\n")

    def scrolling_screen_down(self, pixels) -> None:
        """Scroll down by the given number of pixels."""
        self.driver.execute_script("window.scrollBy(0, {});".format(pixels))

    def filling_missing_data(self, list_of_extracted_data):
        """Sometimes "Items" value is missing, filling the value with "_"."""
        for i in range(int(len(list_of_extracted_data) / 9)):
            if i * 10 + 8 > len(list_of_extracted_data):
                break

            if list_of_extracted_data[i * 10 + 8] == "—":
                list_of_extracted_data.insert(i * 10 + 9, "—")

    def slice_table_data(self, data):
        """Slice the table data into 10 columns."""
        return [data[i * 10 : i * 10 + 10] for i in range(int(len(data) / 10))]

    def convert_row_data_to_table(self, data):
        """Convert a list to a pandas DataFrame."""
        return pd.DataFrame(data, columns=NFTData.__fields__.keys())

    def scrolling_down_to_bottom(self):
        """Scroll down the page to the bottom."""
        html = self.driver.find_element(By.TAG_NAME, "html")
        html.send_keys(Keys.END)
        time.sleep(1)

    def click_button(self, key):
        """Click the button and return True if successful, False otherwise."""
        try:
            button = self.wait.until(EC.element_to_be_clickable((By.XPATH, key)))
            button.click()
            time.sleep(1)
            return True
        except (
            NoSuchElementException,
            TimeoutException,
            StaleElementReferenceException,
            ElementNotInteractableException,
            AttributeError
            ):
            return False

    def concatenate_table(self, table1, table2):
        """Concatenate two tables."""
        return pd.concat([table1, table2])

    def delete_duplicate_rows(self, rows):
        """Delete duplicate rows."""
        return rows.drop_duplicates(subset=["rank"])

    async def scrape_data(self, pos=2):
        """Scrape NFT data from the website."""
        self.driver.get(NFTScraper.URL)
        await asyncio.sleep(3)
        xpath = NFTScraper.XPATH
        for _ in range(pos):
            list_of_text = []
            tasks = []

            for _ in range(4):
                task = asyncio.create_task(self.collect_screen_data(xpath))
                tasks.append(task)
            elements_list = await asyncio.gather(*tasks)
            for elements in elements_list:

                text = self.extract_text_from_data(elements)
                list_of_text += text
                self.scrolling_screen_down(3000)

                await asyncio.sleep(1.5)

            self.filling_missing_data(list_of_text)
            row = self.slice_table_data(list_of_text)
            table = self.convert_row_data_to_table(row)
            table["rank"] = table["rank"].astype("int")
            table.sort_values(by=["rank"], inplace=True)
            table = self.delete_duplicate_rows(table)

            # Write table to CSV using a context manager
            with open("output.csv", mode="a", newline="", encoding="utf-8") as f:
                table.to_csv(f, index=False, header=False)

            self.click_button("//*[@id='main']/div/div[2]/button[2]")

            xpath = '//*[@id="main"]/div/div[1]/div[3]/div/div[4]'


async def main(pages_of_scraping=2):
    """Main function to execute the scraping process."""
    scraper = NFTScraper()
    await scraper.scrape_data(pages_of_scraping)
    scraper.driver.quit()


if __name__ == "__main__":
    pos = 2  # number of pages to scrape
    asyncio.run(main(pos))




