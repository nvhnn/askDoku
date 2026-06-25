from app.core.clients import gemini, deepseek
from .embed import embed_document
from .clients import supabase

def generate_response(question: str, contexts: list[dict]) -> str:
    context_text = "\n\n".join(context["content"] for context in contexts)
    prompt = f"""
        Answer the question using only the context below. If the context doesn't contain enough information, say so.

        Context:
        {context_text}

        Question: {question}
    """

    res = deepseek.messages.create(
        model="deepseek-v4-flash",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return next(block.text for block in res.content if block.type == "text")

def retrieve_context(question: str) -> list[dict]:
   embedding = embed_document([question])[0]
   result = supabase.rpc(
      "match_documents",
      {"query_embedding": embedding, "match_count": 5}
   ).execute()
   return [{ 
        "content": row["content"], 
        "page_number": row["page_number"], 
        "document_id": row["document_id"], 
        "filename": row["filename"]
        } for row in result.data]