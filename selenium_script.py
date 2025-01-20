import os
import sys
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# delete the previous pdf file
for file in os.listdir(os.getcwd()):
    if file.endswith('.pdf'):
        os.remove(file)
        break
    # Fixme: If there are other pdf files in the directory, this will randomly delete one of them


class Browser(webdriver.Chrome):
    def __init__(self):

        # Set Chrome preferences
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_experimental_option(
            'prefs',
            {
                'profile.default_content_settings.popups': 0,
                'download.default_directory': os.getcwd(),
            },
        )

        super().__init__(options=options)
        self.wait = WebDriverWait(self, 60)

    def open(self, url):
        self.get(url)

    def fetch_latex(self):
        # Fetch the latex code
        div_element = self.wait.until(
            lambda driver: driver.find_element(
                By.CSS_SELECTOR,
                'div[data-language="latex"]',
            )
        )

        # Scroll the div to ensure .tex code is copied from the lazy-loaded div

        self.execute_script('document.body.style.zoom="0.1"')
        time.sleep(10)
        scroll_ele = self.find_element(By.CSS_SELECTOR, 'div.cm-scroller')
        scroll_height = scroll_ele.get_attribute('scrollHeight')
        self.execute_script(
            'arguments[0].scrollTo(0, arguments[1]);',
            scroll_ele,
            scroll_height,
        )

        # Fixme: I'm zooming out to 10% to ensure the entire content of .tex file is loaded; this may not work if the .tex file is longer.
        # I couldn't find a reliable way to deal with lazy loading

        latex = div_element.text

        # Ensure the entire latex code is fetched
        if not latex.endswith(r'\end{document}'):
            raise ValueError('Unable to fetch ⚠️')

        return latex

    def download_pdf(self):
        # click on the download button to get the pdf
        download_btn = self.wait.until(
            lambda driver: driver.find_element(
                By.CSS_SELECTOR,
                'a[aria-label="Download PDF"][data-disabled="false"]',
            )
        )

        download_btn.click()
        print('Pdf downloaded 🎉')

        time.sleep(5)  # Wait for the download to complete


def save_latex_if_updated(latex, filename):
    # if there are no changes in latex file do sys.exit(0) and skip next steps
    try:
        with open(filename) as file:
            if latex == file.read():
                return False

    except FileNotFoundError:
        print('First run 🏃‍♂️')

    # if latex file is not found or if it has changed, write it and download pdf
    with open('resume.tex', 'w') as file:
        file.write(latex)

    return True


url = 'https://www.overleaf.com/read/nsgsskwncdmy#a859ac'
# url = sys.argv[1]

browser = Browser()
browser.get(url)

try:
    latex = browser.fetch_latex()
except Exception as e:
    print(e)
    sys.exit(1)

changes_detected = save_latex_if_updated(latex, 'resume.tex')

if not changes_detected:
    print('No changes detected ✅️')

    # setting github env var: skip=True
    with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
        fh.write('skip=True\n')

    sys.exit(0)

browser.download_pdf()

browser.quit()

with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
    fh.write('skip=False\n')
