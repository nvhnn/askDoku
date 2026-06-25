from .clients import gemini
from google import genai
from google.genai import types

BATCH_SIZE = 50

def embed_document(chunks: list[str]) -> list[list[float]]:
    embeddings = []
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        res = gemini.models.embed_content(
            model="gemini-embedding-001",
            contents=[types.Content(parts=[types.Part.from_text(text=chunk)]) for chunk in batch]
        )
        embeddings.extend(emb.values for emb in res.embeddings)
        
    return embeddings