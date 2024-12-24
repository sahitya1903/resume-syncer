import os
import time
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# delete previous pdf file
for file in os.listdir(os.getcwd()):
    if file.endswith('.pdf'):
        os.remove(file)
        break
        # TODO: if possible, do this after commiting the pdf file in github actions

# Set Chrome preferences
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_experimental_option("prefs", {"profile.default_content_settings.popups": 0, "download.default_directory": os.getcwd()})

browser = webdriver.Chrome(options=options)

url = sys.argv[1]
browser.get(url)
wait = WebDriverWait(browser, 10)

# TODO: check for last updated date

download_link_element = wait.until(
    lambda driver: driver.find_element(
        By.CSS_SELECTOR,
        'a[aria-label="Download PDF"][data-disabled="false"]',
    )
)

download_link_element.click()

time.sleep(5)  # Wait for the download to complete
browser.quit()
