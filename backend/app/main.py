from fastapi import FastAPI, UploadFile
from app.core import ingest_document, retrieve_context, generate_response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origin = ['http://localhost:5173']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.post("/upload")
async def ingest(file: UploadFile):
    content = await file.read()
    with open(f"test_docs/{file.filename}", "wb") as f:
        f.write(content)
    ingest_document(f"test_docs/{file.filename}", content)
    return {"status": "ok"}

@app.post("/ask")
async def ask(question: str):
    contexts = retrieve_context(question)
    answer = generate_response(question, contexts)
    return {"answer": answer, "sources": contexts}