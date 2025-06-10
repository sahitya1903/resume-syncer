from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import JSONResponse
from utils import findId, updateFile

app = FastAPI()


@app.post("/")
async def function(link: str = Form(...), file: UploadFile = File(...)):
    try:
        id = findId(link)
        new_file = updateFile(id, file)
        return JSONResponse(content={"File updated: ": new_file['name']})

    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


# todo: do auth with oidc