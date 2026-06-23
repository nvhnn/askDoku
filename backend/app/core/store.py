from .clients import supabase

def store_chunks(chunks: list[str], embeddings: list[list[float]]):
    for chunk, embedding in zip(chunks, embeddings):
        supabase.table("document_chunks").insert({"content": chunk, "embedding": list(embedding)}).execute()