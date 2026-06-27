from .clients import gemini
from google.genai import types
from google.genai.errors import ClientError
from google.genai.types import HttpOptions, HttpRetryOptions
import time
import random

_BATCH_SIZE = 20
_MAX_RETRIES = 6
_INITIAL_BACKOFF = 5.0
_INTER_BATCH_DELAY = 1.0  # seconds between batches to stay under RPM limits

def embed_document(chunks: list[str]) -> list[list[float]]:
	embeddings = []
	for i in range(0, len(chunks), _BATCH_SIZE):
		if i > 0:
			time.sleep(_INTER_BATCH_DELAY)
		batch = chunks[i:i + _BATCH_SIZE]
		backoff = _INITIAL_BACKOFF
		for attempt in range(_MAX_RETRIES):
			try:
				res = gemini.models.embed_content(
						model="gemini-embedding-001",
						contents=[types.Content(parts=[types.Part.from_text(text=chunk)]) for chunk in batch],
						config=types.EmbedContentConfig(
							http_options=HttpOptions(retry_options=HttpRetryOptions(attempts=1))
						)
				)
				embeddings.extend(emb.values for emb in res.embeddings)
				break
			except ClientError as e:
				if e.code == 429 and attempt < _MAX_RETRIES - 1:
					details = e.details.get('error', {}).get('details', [])
					retry_delay = None
					for detail in details:
						if detail.get('@type', '').endswith('.RetryInfo'):
							raw = detail.get('retryDelay', '')
							if raw.endswith('s'):
								retry_delay = int(raw[:-1])
							break
					sleep_for = retry_delay if retry_delay else backoff
					# add jitter to avoid thundering herd
					sleep_for += random.uniform(0, sleep_for * 0.2)
					time.sleep(sleep_for)
					if not retry_delay:
						backoff = min(backoff * 2, 120)
				else:
					raise

	return embeddings