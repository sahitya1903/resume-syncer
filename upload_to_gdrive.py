import json
import os
import re
import sys

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def find_id(link):
    """Extract the file ID from a Drive share link, or return the input as-is if it is already a raw ID."""
    link = link.strip()
    match = re.search(r'(?:/d/|[?&]id=)([\w-]+)', link)
    return match.group(1) if match else link


def main():
    link = os.environ.get('GDRIVE_LINK')
    key = os.environ.get('GDRIVE_SERVICE_ACCOUNT_KEY')
    if not link or not key:
        sys.exit('Error: GDRIVE_LINK and GDRIVE_SERVICE_ACCOUNT_KEY must be set.')

    pdf_file = f"{sys.argv[1] if len(sys.argv) > 1 else 'resume'}.pdf"
    file_id = find_id(link)
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(key),
        scopes=['https://www.googleapis.com/auth/drive'],
    )
    drive = build('drive', 'v3', credentials=credentials)

    print(f'Uploading {pdf_file} to Google Drive file ID: {file_id}...')
    updated = drive.files().update(
        fileId=file_id,
        media_body=MediaFileUpload(pdf_file, mimetype='application/pdf'),
    ).execute()
    print(f"Uploaded! File name on Google Drive: {updated.get('name')}")


if __name__ == '__main__':
    main()
