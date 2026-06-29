from app.core.clients import deepseek, GENERATION_MODEL
from .embed import embed_document
from .clients import supabase

MAX_TURNS = 3

def rewrite_query(convo: list[dict]):
	prompt = f"""
		You are a query rewriter for a RAG system.

		Given a conversation history, rewrite the last user message into a self-contained search query that captures the full intent without relying on prior context.

		Rules:
		- If the message is already standalone and specific, return it unchanged
		- Resolve pronouns and references ("it", "that", "the previous one") using earlier turns
		- Expand topic fragments into complete, searchable questions
		- Output only the rewritten query — no explanation, no quotes, no punctuation changes
	"""

	res = deepseek.messages.create(
		model=GENERATION_MODEL,
		max_tokens=200,
		thinking={"type": "disabled"},
		system=prompt,
		messages= convo[-4:]
	)
	
	for content in res.content:
		if content.type == 'text':
			return content.text


def generate_response(contexts: list[dict], convo: list[dict]):
	context_text = "\n\n".join(context["content"] for context in contexts)
	prompt = f"""
		Answer the question using only the context below. If the context doesn't contain enough information, say so.
		Format your response using markdown: use headers (##, ###), bullet points, bold text, and numbered lists where appropriate to make the answer clear and easy to read.

		Context: {context_text}
	"""

	with deepseek.messages.stream(
		model=GENERATION_MODEL,
		max_tokens=4096,
		system=prompt,
		messages=convo[-(MAX_TURNS * 2 + 1):]
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