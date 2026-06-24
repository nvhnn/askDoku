import hashlib

def create_chunk_id(content: str) -> str:
    return hashlib.sha256(content.encode("UTF-8")).hexdigest()

def chunk_text(pages: list[dict], document_id, chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    chunks = []
    for page in pages:
        words = page["content"].split()
        step = 0
        while step < len(words):
            end = step + chunk_size
            chunk_words = words[step:end]
            chunk_content = " ".join(chunk_words)
            chunks.append({
                "chunk_id": create_chunk_id(chunk_content),
                "document_id": document_id,
                "page_number": page["page_number"],
                "section_title": None,
                "content": chunk_content
            })
            step += chunk_size - overlap

    return chunks 