from .clients import supabase

def store_chunks(chunks: list[str], embeddings: list[list[float]]):
    for chunk, embedding in zip(chunks, embeddings):
        supabase.table("document_chunks").upsert({
            "chunk_id": chunk["chunk_id"],
            "document_id": chunk["document_id"],
            "page_number": chunk["page_number"],
            "section_title": chunk["section_title"],
            "content": chunk["content"],
            "embedding": list(embedding)
        }).execute()

def store_document(document_id: str, filename: str):
    supabase.table("documents").upsert({
        "document_id": document_id, 
        "filename": filename,
        "status": "processing"
    }).execute()

def update_document_status(document_id: str, status: str):
    supabase.table("documents").update({
        "status": status
    }).eq('document_id', document_id).execute()

def get_document_status(document_id: str) -> str | None:
    result = supabase.table("documents").select("status").eq("document_id", document_id).maybe_single().execute()
    return result.data["status"] if result.data else None