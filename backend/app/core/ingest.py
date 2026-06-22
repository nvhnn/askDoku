from .extract import extract_document
from .chunk import chunk_text

def ingest_document(filepath: str):
    # extract
    text = extract_document(filepath)
    # chunk
    chunks = chunk_text(text)
    # embed
    print(chunks)
    # store