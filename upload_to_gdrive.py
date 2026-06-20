import os
import sys
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Retrieve environment variables
gdrive_link = os.environ.get("GDRIVE_LINK")
service_account_info_str = os.environ.get("GDRIVE_SERVICE_ACCOUNT_KEY")

if not gdrive_link or not service_account_info_str:
    print("Error: Missing GDRIVE_LINK or GDRIVE_SERVICE_ACCOUNT_KEY environment variables.")
    sys.exit(1)


def find_id(link: str) -> str:
    # Find the id in the link (e.g. 'https://drive.google.com/file/d/<id>/view?...')
    if "/d/" in link:
        start = link.find("/d/") + 3
        end = link.find("/", start)
        if end == -1:
            return link[start:]
        return link[start:end]
    raise ValueError(f"Could not parse file ID from link: {link}")


try:
    file_id = find_id(gdrive_link)
    print(f"Parsed Google Drive file ID: {file_id}")

    # Load credentials from the JSON string provided as input/secret
    service_account_info = json.loads(service_account_info_str)
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=['https://www.googleapis.com/auth/drive'],
    )

    # Build drive client with static discovery to avoid network overhead
    drive = build('drive', 'v3', credentials=credentials, static_discovery=True)

    # Use MediaFileUpload to upload the file directly from the filesystem
    media = MediaFileUpload(
        'resume.pdf',
        mimetype='application/pdf',
        resumable=False
    )

    print(f"Uploading 'resume.pdf' to Google Drive file ID: {file_id}...")
    new_file = drive.files().update(
        fileId=file_id,
        media_body=media
    ).execute()

    print(f"Successfully uploaded! File name on Google Drive: {new_file.get('name')}")

except Exception as e:
    print(f"Error during Google Drive upload: {e}")
    sys.exit(1)
