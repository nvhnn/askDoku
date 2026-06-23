from fastapi import FastAPI, UploadFile
from app.core import ingest_document, retrieve_context, generate_response

app = FastAPI()

@app.post("/ingest")
async def ingest(file: UploadFile):
    content = await file.read()
    with open(f"test_docs/{file.filename}", "wb") as f:
        f.write(content)
    ingest_document(f"test_docs/{file.filename}")   
    return {"status": "ok"}

@app.post("/ask")
async def ask(question: str):
    context = retrieve_context(question)
    answer = generate_response(question, context)
    return {"answer": answer}