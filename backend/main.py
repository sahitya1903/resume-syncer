from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import JSONResponse
from utils import findId, updateFile

app = FastAPI()


@app.post("/")
async def function(link: str = Form(...), file: UploadFile = File(...)):
    print(f"\n--- Incoming Request received ---")
    print(f"Link: {link}")
    print(f"File Name: {file.filename}")
    try:
        id = findId(link)
        new_file = updateFile(id, file)
        print(f"Successfully processed request! Returning response...")
        return JSONResponse(content={"File updated: ": new_file['name']})

    except Exception as e:
        import traceback
        print(f"ERROR: Exception occurred while updating file!")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"detail": str(e)})


# todo: do auth with oidc