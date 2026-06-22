from fastapi import FastAPI, UploadFile
from app.core import ingest_document

app = FastAPI()

@app.post("/ingest")
async def ingest(file: UploadFile):
    content = await file.read()
    with open(f"test_docs/{file.filename}", "wb") as f:
        f.write(content)
    ingest_document(f"test_docs/{file.filename}")   
    return {"status": "ok"}