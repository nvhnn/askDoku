from .extract import extract_document
from .chunk import chunk_text
from .embed import embed_document
from .store import store_chunks

def ingest_document(filepath: str):
    # extract
    text = extract_document(filepath)
    # chunk
    chunks = chunk_text(text)
    # embed
    embeddings = embed_document(chunk["text"] for chunk in chunks)
    # store
    store_chunks(chunks, embeddings)