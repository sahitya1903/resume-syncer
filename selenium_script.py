import json
import os
import re
import shutil
import sys
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

download_path = os.path.abspath(os.path.join(os.getcwd(), 'temp'))


class Browser(webdriver.Chrome):
    def __init__(self):

        # Set Chrome preferences
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        options.add_experimental_option(
            'prefs',
            {
                'profile.default_content_settings.popups': 0,
                'download.default_directory': download_path,
            },
        )

        super().__init__(options=options)
        self.wait = WebDriverWait(self, 60)

    def open(self, url):
        self.get(url)

    def fetch_latex(self):
        # wait for the latex to load
        self.wait.until(
            lambda driver: driver.find_element(
                By.CSS_SELECTOR,
                'div[data-language="latex"]',
            )
        )

        # the latex code is fetched in a websocket request
        for entry in browser.get_log('performance'):
            try:
                message = json.loads(entry['message'])['message']
                if message['method'] == 'Network.webSocketFrameReceived':
                    payload = message['params']['response']['payloadData']

                    if '\\begin{document}' in payload:
                        l = eval(
                            re.search(
                                r'\+\[null,([\s\S]*?),\d+,\[\],\{\}\]', payload
                            ).group(1)
                        )
                        latex = '\n'.join(l)
            except:
                pass

        if not latex:
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
        time.sleep(5)  # Wait for the download to complete
        print('Pdf downloaded 🎉')

        # download the pdf in a temp folder, move it to the root and then delete the temp folder
        pdf = os.listdir('temp')[0]
        shutil.copy(f'temp/{pdf}', 'resume.pdf')


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


# url = 'https://www.overleaf.com/read/nsgsskwncdmy#a859ac'
url = sys.argv[1]

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
