"""Python scraper to collect NFT data and image from opensea 
"""

# import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
# import uuid
# import time
from selenium.webdriver.chrome.service import Service
import pandas as pd


class NFT_scraper:
    """ Prepare selenium chrome webdriver for scraping, set appropriate zoom of window,
         which is able to get all data of the page in two screen, initial screen and bottom screen.
    """
    def __init__(self):
        options = Options()
        options.add_argument("--headless")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.get("chrome://settings/")
        self.driver.execute_script("chrome.settingsPrivate.setDefaultZoom(0.25);")

        self.table = pd.DataFrame(
            columns=[
                "Rank",
                "Collection",
                "Volume",
                "24h %",
                "7d %",
                "Floor Price",
                "Owners",
                "Items",
            ]
        )

