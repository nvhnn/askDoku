from .extract import extract_document
from .chunk import chunk_text
from .embed import embed_document
from .store import store_chunks, store_document
import hashlib
import os

def get_document_id(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()

def get_filename(filepath: str) -> str:
    return os.path.basename(filepath)

def ingest_document(filepath: str, file_bytes: bytes):
    filename = get_filename(filepath)

    document_id = get_document_id(file_bytes)
    store_document(document_id, filename)
    pages = extract_document(filepath)
    chunks = chunk_text(pages, document_id)
    embeddings = embed_document([chunk["content"] for chunk in chunks])
    store_chunks(chunks, embeddings)