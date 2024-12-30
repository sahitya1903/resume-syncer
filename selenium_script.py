import os
import sys
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

print(os.getcwd())

# delete previous pdf file
for file in os.listdir(os.getcwd()):
    if file.endswith('.pdf'):
        os.remove(file)
        break
    # Fixme: If there are other pdf files in the directory, this will randomly delete one of them

# Set Chrome preferences
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_experimental_option("prefs", {"profile.default_content_settings.popups": 0, "download.default_directory": os.getcwd()})

browser = webdriver.Chrome(options=options)

url = sys.argv[1]
browser.get(url)
wait = WebDriverWait(browser, 60)

# Fetch the latex code
div_element = wait.until(
    lambda driver: driver.find_element(
        By.CSS_SELECTOR,
        'div[data-language="latex"]',
    )
)

# Scroll the div to ensure lazy-loaded content is loaded

browser.execute_script("document.body.style.zoom='0.1';")
time.sleep(10)
scroll_ele = browser.find_element(By.CSS_SELECTOR, 'div.cm-scroller')
scroll_height = scroll_ele.get_attribute('scrollHeight')
browser.execute_script("arguments[0].scrollTo(0, arguments[1]);", scroll_ele, scroll_height)

# Fixme: I'm zooming out to 10% to ensure the entire content of .tex file is loaded; this may not work if the .tex file is longer.
# I couldn't find a way to deal with lazy loading

latex = div_element.text

# Ensure the entire latex code is fetched
if not latex.endswith(r'\end{document}'):
    print('Unable to fetch')
    exit(1)

# if there are changes in latex file, proceed with downloading the pdf
with open("resume.tex", "r+") as file:
    if latex == file.read():
        print("No changes detected")
        with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
            print(f"should_run_task2={flag}", file=fh)
        sys.exit(0)
    else:
        file.seek(0)
        file.write(latex)

# click on the download button to get the pdf
download_btn = wait.until(
    lambda driver: driver.find_element(
        By.CSS_SELECTOR,
        'a[aria-label="Download PDF"][data-disabled="false"]',
    )
)

download_btn.click()
print('Pdf downloaded')

time.sleep(5)  # Wait for the download to complete
browser.quit()
