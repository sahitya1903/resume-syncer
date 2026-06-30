import json
import os
import shutil
import sys
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

download_path = os.path.abspath(os.path.join(os.getcwd(), 'temp'))
os.makedirs(download_path, exist_ok=True)


class Browser(webdriver.Chrome):
    def __init__(self):

        # Set Chrome preferences
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
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

        latex = ''

        # the latex code is fetched in a websocket request
        for entry in self.get_log('performance'):
            try:
                message = json.loads(entry['message'])['message']
                if message['method'] == 'Network.webSocketFrameReceived':
                    payload = message['params']['response']['payloadData']
                    # print(payload)

                    if '\\begin{document}' in payload:
                        x = payload.find('[')
                        arr = json.loads(payload[x:])[1]
                        latex = '\n'.join(arr)

                        if latex == '':
                            print(payload)
                            raise ValueError("Couldn't parse ⚠️")

                        break
            except:
                pass

        if latex == '':
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

        # Wait for the download to complete robustly
        timeout = 30
        start_time = time.time()
        downloaded_file = None

        while time.time() - start_time < timeout:
            files = os.listdir(download_path)
            # Filter out in-progress chrome downloads
            completed_files = [f for f in files if not f.endswith('.crdownload') and not f.endswith('.tmp')]
            if completed_files:
                downloaded_file = completed_files[0]
                break
            time.sleep(1)

        if not downloaded_file:
            raise FileNotFoundError("PDF download timed out or failed ⚠️")

        print('Pdf downloaded 🎉')

        # Move the pdf to the root and clean up
        shutil.copy(os.path.join(download_path, downloaded_file), 'resume.pdf')
        os.remove(os.path.join(download_path, downloaded_file))


def save_latex_if_updated(latex, filename):
    # Normalize line endings to LF (\n) to prevent CRLF vs LF mismatches
    latex = latex.replace('\r\n', '\n').replace('\r', '\n')

    try:
        # Python's universal newlines mode (default) automatically translates CRLF/CR to LF (\n) on read
        with open(filename, 'r', encoding='utf-8') as file:
            if latex == file.read():
                return False

    except FileNotFoundError:
        print('First run 🏃‍♂️')

    # Write normalized LF content to file
    with open('resume.tex', 'w', newline='\n', encoding='utf-8') as file:
        file.write(latex)

    return True


# url = 'https://www.overleaf.com/read/nsgsskwncdmy#a859ac'
url = sys.argv[1]

browser = Browser()
try:
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

    with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
        fh.write('skip=False\n')
finally:
    browser.quit()
