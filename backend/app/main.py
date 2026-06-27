from fastapi import FastAPI, UploadFile
from fastapi.responses import StreamingResponse
from app.core import ingest_document, retrieve_context, generate_response
from fastapi.middleware.cors import CORSMiddleware
import json

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

def stream_story(question: str, contexts: list[dict]):
    for context in contexts:
        yield "data: " + json.dumps(context) + "\n\n"
    answers = generate_response(question, contexts)
    for answer in answers:
        yield "data: " + answer.replace("\n", "\\n") + "\n\n"
    yield "data: DONE\n\n"

@app.post("/ask")
async def ask(question: str):
    contexts = retrieve_context(question)
    return StreamingResponse(
        stream_story(question, contexts),
        media_type="text/event-stream"
        )