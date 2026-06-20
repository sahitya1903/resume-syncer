from fastapi import UploadFile
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

print("Loading service account credentials...")
credentials = service_account.Credentials.from_service_account_file(
    'service_account.json',
    scopes=['https://www.googleapis.com/auth/drive'],
)

print("Building Google Drive service client...")
drive = build('drive', 'v3', credentials=credentials, static_discovery=True)


def findId(link: str) -> str:
    # Find the id in link:
    # 'https://drive.google.com/file/d/<id>/view?...'
    file_id = link[32 : link.find('/', 32)]
    print(f"Parsed Google Drive file ID: {file_id}")
    return file_id


def updateFile(id: str, file: UploadFile) -> dict:
    print(f"Uploading file '{file.filename}' to Google Drive file ID: {id}...")
    
    # Using resumable=False for small files like resume PDFs to avoid chunking overhead/issues
    media = MediaIoBaseUpload(
        file.file,
        mimetype="application/pdf",
        resumable=False,
    )
    
    new_file = (
        drive.files()
        .update(
            fileId=id,
            media_body=media,
        )
        .execute()
    )
    print(f"File upload complete! Server response: {new_file}")
    return new_file
