from app.core.clients import deepseek, GENERATION_MODEL
from .embed import embed_document
from .clients import supabase

def generate_response(question: str, contexts: list[dict], history_convo: list[dict]):
	context_text = "\n\n".join(context["content"] for context in contexts)
	prompt = f"""
		Answer the question using only the context below. If the context doesn't contain enough information, say so.
		Format your response using markdown: use headers (##, ###), bullet points, bold text, and numbered lists where appropriate to make the answer clear and easy to read.

		Context: {context_text}

		Conversation History: {history_convo}

		Question: {question}
	"""

	with deepseek.messages.stream(
		model=GENERATION_MODEL,
		max_tokens=4096,
		messages=history_convo + [{"role": "user", "content": prompt}]
	) as stream:
		for text in stream.text_stream:
			yield text

def retrieve_context(question: str) -> list[dict]:
	embedding = embed_document([question])[0]
	result = supabase.rpc(
		"match_documents",
		{"query_embedding": embedding, "match_count": 5}
	).execute()
	return [{
		"page_number": row["page_number"], 
		"document_id": row["document_id"], 
		"filename": row["filename"],
		"content": row["content"],
		"similarity": row["similarity"]
		} for row in result.data]