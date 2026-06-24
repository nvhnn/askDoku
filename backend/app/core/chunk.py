import hashlib

def create_chunk_id(content: str) -> str:
    return hashlib.sha256(content.encode("UTF-8")).hexdigest()

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    words = text.split()
    chunks = []
    step = 0
    while step < len(words):
        end = step + chunk_size
        chunk_words = words[step:end]
        chunk_text = " ".join(chunk_words)
        chunks.append({
            "id": create_chunk_id(chunk_text), 
            "text": chunk_text
        })
        step += chunk_size - overlap

    return chunks 