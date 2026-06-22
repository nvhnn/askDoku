from fastapi import FastAPI, UploadFile
from app.core.rag import generate_response

app = FastAPI()

@app.post("/upload")
async def upload_file(file: UploadFile):
    generate_response(file)
    return {"status": "ok"}