import json
import os
import shutil
import sys
import tempfile
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

TEX_FILE = 'resume.tex'
PDF_FILE = 'resume.pdf'


def find_latex_array(data):
    """Recursively find the list of source lines that contains the LaTeX document."""
    if isinstance(data, list):
        if all(isinstance(item, str) for item in data):
            return data if any('\\begin{document}' in item for item in data) else None
    elif isinstance(data, dict):
        data = data.values()
    else:
        return None

    for item in data:
        if (result := find_latex_array(item)) is not None:
            return result
    return None


class Browser(webdriver.Chrome):
    def __init__(self, download_dir):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        options.add_experimental_option('prefs', {'download.default_directory': download_dir})

        super().__init__(options=options)
        self.download_dir = download_dir
        self.wait = WebDriverWait(self, 60)

    def fetch_latex(self):
        self.wait.until(lambda d: d.find_element(By.CSS_SELECTOR, 'div[data-language="latex"]'))

        # The LaTeX source is delivered in a websocket frame, so read it from the performance log
        decoder = json.JSONDecoder()
        for entry in self.get_log('performance'):
            message = json.loads(entry['message'])['message']
            if message['method'] != 'Network.webSocketFrameReceived':
                continue

            payload = message['params']['response']['payloadData']
            if '\\begin{document}' not in payload:
                continue

            # Skip the socket.io prefix and decode the JSON body that follows it
            start = min(i for i in (payload.find('['), payload.find('{')) if i != -1)
            try:
                data, _ = decoder.raw_decode(payload, start)
            except json.JSONDecodeError:
                continue

            if lines := find_latex_array(data):
                return '\n'.join(lines)

        raise ValueError('Unable to fetch LaTeX source')

    def download_pdf(self, dest):
        self.wait.until(
            lambda d: d.find_element(By.CSS_SELECTOR, 'a[aria-label="Download PDF"][data-disabled="false"]')
        ).click()

        deadline = time.time() + 30
        while time.time() < deadline:
            # Ignore in-progress Chrome downloads
            done = [f for f in os.listdir(self.download_dir) if not f.endswith(('.crdownload', '.tmp'))]
            if done:
                shutil.move(os.path.join(self.download_dir, done[0]), dest)
                print('PDF downloaded')
                return
            time.sleep(1)

        raise TimeoutError('PDF download timed out')


def read_text(path):
    try:
        with open(path, encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None


def set_output(skip):
    """Expose skip=True/False to the later steps of the composite action."""
    if path := os.environ.get('GITHUB_OUTPUT'):
        with open(path, 'a', encoding='utf-8') as f:
            f.write(f'skip={skip}\n')


def main():
    if len(sys.argv) < 2:
        sys.exit('Usage: python selenium_script.py <overleaf_url>')

    with tempfile.TemporaryDirectory() as download_dir:
        browser = Browser(download_dir)
        try:
            browser.get(sys.argv[1])
            latex = browser.fetch_latex()

            if latex == read_text(TEX_FILE):
                print('No changes detected')
                set_output(True)
                return

            browser.download_pdf(PDF_FILE)
        finally:
            browser.quit()

    # Save the source only after the PDF is in place, so a failed download is retried on the next run
    with open(TEX_FILE, 'w', encoding='utf-8') as f:
        f.write(latex)
    set_output(False)


if __name__ == '__main__':
    main()
