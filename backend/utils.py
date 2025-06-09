from fastapi import UploadFile
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

credentials = service_account.Credentials.from_service_account_file(
    'service_account.json',
    scopes=['https://www.googleapis.com/auth/drive'],
)

drive = build('drive', 'v3', credentials=credentials)


def findId(link: str) -> str:
    # Find the id in link:
    # 'https://drive.google.com/file/d/<id>/view?...'

    return link[32 : link.find('/', 32)]


def updateFile(id: str, file: UploadFile) -> dict:
    new_file = (
        drive.files()
        .update(
            fileId=id,
            media_body=MediaIoBaseUpload(
                file.file,
                mimetype="application/pdf",
                resumable=True,
            ),
        )
        .execute()
    )
    return new_file
