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

def find_latex_array(data):
    if isinstance(data, list):
        if all(isinstance(item, str) for item in data) and any('\\begin{document}' in item for item in data):
            return data
        for item in data:
            res = find_latex_array(item)
            if res is not None:
                return res
    elif isinstance(data, dict):
        for val in data.values():
            res = find_latex_array(val)
            if res is not None:
                return res
    return None


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

    def fetch_latex(self):
        # wait for the latex to load
        self.wait.until(
            lambda driver: driver.find_element(
                By.CSS_SELECTOR,
                'div[data-language="latex"]',
            )
        )

        latex = ''
        decoder = json.JSONDecoder()

        # the latex code is fetched in a websocket request
        for entry in self.get_log('performance'):
            try:
                message = json.loads(entry['message'])['message']
                if message['method'] == 'Network.webSocketFrameReceived':
                    payload = message['params']['response']['payloadData']
                    # print(payload)

                    if '\\begin{document}' in payload:
                        start_idx = min((payload.find(c) for c in ('[', '{') if payload.find(c) != -1), default=-1)
                        if start_idx != -1:
                            data, _ = decoder.raw_decode(payload[start_idx:])
                            arr = find_latex_array(data)
                            if arr:
                                latex = '\n'.join(arr)
                                break
            except:
                pass

        if latex == '':
            raise ValueError('Unable to fetch ⚠️')

        return latex

    def download_pdf(self):
        # Clear the download path first to remove any stale files from previous runs
        for f in os.listdir(download_path):
            try:
                os.remove(os.path.join(download_path, f))
            except OSError:
                pass

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

        # Move the pdf to the root
        shutil.move(os.path.join(download_path, downloaded_file), 'resume.pdf')

def save_latex_if_updated(latex, filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            if latex == file.read():
                return False

    except FileNotFoundError:
        print('First run 🏃♂️')

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(latex)

    return True

if len(sys.argv) < 2:
    print("Error: Missing overleaf URL argument.")
    print("Usage: python selenium_script.py <overleaf_url>")
    sys.exit(1)
url = sys.argv[1]

# url = 'https://www.overleaf.com/read/xgkptdvgqhps#f17f92'

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
        github_output = os.environ.get('GITHUB_OUTPUT')
        if github_output:
            with open(github_output, 'a', encoding='utf-8') as fh:
                fh.write('skip=True\n')

        sys.exit(0)

    browser.download_pdf()

    github_output = os.environ.get('GITHUB_OUTPUT')
    if github_output:
        with open(github_output, 'a', encoding='utf-8') as fh:
            fh.write('skip=False\n')
finally:
    browser.quit()
