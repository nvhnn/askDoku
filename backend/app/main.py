from fastapi import FastAPI, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from app.core import ingest_document, retrieve_context, generate_response, store_document, get_document_status, get_document_id
from fastapi.middleware.cors import CORSMiddleware
from google.genai.errors import ClientError
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
async def upload(file: UploadFile, background_tasks: BackgroundTasks):
	content = await file.read()
	with open(f"test_docs/{file.filename}", "wb") as f:
		f.write(content)
	document_id = get_document_id(content)
	store_document(document_id, file.filename)
	background_tasks.add_task(ingest_document, f"test_docs/{file.filename}", content)
	return {"document_id": document_id}

@app.get("/status/{document_id}")
def status(document_id: str):
	status = get_document_status(document_id)
	if status is None:
		raise HTTPException(status_code=404, detail="Document not found")
	return {"status": status}

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