# askDoku — RAG learning roadmap

A staged build plan for askDoku: an AI app where users upload PDFs/docs and ask questions about them. Built in raw Python (no LangChain) to learn RAG mechanics to the core, then layered up toward production-grade and portfolio-ready.

**Stack:** FastAPI + Python backend, Supabase + pgvector for storage, Voyage AI for embeddings, Claude API for generation, React + Vite + TS frontend (added from M1 onward).

**Principle for the whole project:** don't move to the next milestone until the current one actually works end-to-end. A working M0 is worth more than a half-finished M4.

---

## M0 — Naive RAG (backend only)

**What to expect:**
Single PDF upload, extract text, chunk it, embed the chunks, store them, then answer questions by retrieving the top-k most similar chunks and stuffing them into a prompt. No UI — test via FastAPI's auto-generated docs at `/docs` or `curl`.

**What you'll learn:**
- How embeddings actually represent meaning (and where they fail — try asking something with an exact ID/number and watch it struggle)
- Chunking tradeoffs: too small loses context, too large dilutes retrieval relevance
- Why "retrieval" is just nearest-neighbor search over vectors, not magic
- Prompt construction: how much context you can stuff in before the model gets confused or you waste tokens

**How to approach it:**
1. Get text extraction working first, in isolation — print the extracted text and read it. PDF extraction is messier than it looks (headers, footers, broken line breaks).
2. Chunk with a fixed size + overlap (e.g. 500 chars, 50 overlap) before trying anything fancier like semantic chunking.
3. Write `retrieve_context()` and `generate_response()` as two separate, testable functions — don't fuse them into one blob.
4. Manually inspect what gets retrieved for a few test questions before trusting the final answer. If retrieval is bad, no amount of prompt engineering fixes it.

**Tips & tricks:**
- Use deterministic chunk IDs (hash of content) so re-running ingestion doesn't create duplicates — upsert, don't insert blindly.
- Print/log the retrieved chunks during development. You want to *see* what the model sees.
- Don't reach for a reranker or hybrid search here even if it's tempting — naive cosine similarity is the right baseline to understand first.
- If answers seem wrong, check retrieval before blaming the LLM. 90% of "bad RAG answers" are bad retrieval, not bad generation.

---

## M1 — Minimal UI + deploy

**What to expect:**
A bare React+Vite+TS frontend: an upload form and a simple chat box hitting your FastAPI endpoints. No streaming, no styling polish. Deploy both sides immediately.

**What you'll learn:**
- Wiring a frontend to a backend you built yourself end-to-end (file upload via `multipart/form-data`, then a simple POST for questions)
- Deployment basics for this exact stack (you've done this before with ppij-shop, so this should be fast): FastAPI → Railway/Render, React → Vercel

**How to approach it:**
1. Resist the urge to add styling yet. Get the unstyled version working and deployed first.
2. Deploy early, even with bugs — having a live URL from day one means you're never caught without something to show.
3. Use plain `fetch()` calls, no state management library — you don't need Zustand/Redux for this scope.

**Tips & tricks:**
- CORS will bite you the first time frontend and backend are on different domains — configure it once, early, so it's not a surprise later.
- Keep environment variables (API URLs, keys) out of the frontend bundle — anything in Vite's `import.meta.env` ships to the browser.
- A live but ugly demo beats a polished one stuck on localhost.
- **Protect your wallet before going public.** Your backend holds the Claude and Voyage API keys — any request that hits your endpoints spends your money, including bots that scan the internet for exposed URLs, not just real visitors. Before sharing the link:
  - Set hard spending caps in the Anthropic Console and Voyage dashboard (your safety net even if everything else fails).
  - Gate `/upload` and `/ask` behind Clerk auth (same as Uns/Amal+) so anonymous traffic can't hit them at all.
  - Add basic rate limiting (`slowapi` for FastAPI) even for logged-in users, e.g. `@limiter.limit("10/minute")`.
  - For a demo specifically: cap file size, cap questions per session, and consider pre-loading sample docs instead of open upload — fewer attack surfaces, more controlled demo.

---

## M2 — Multi-file ingestion + citations

**What to expect:**
Support PDF, DOCX, and TXT. Tag every chunk with its source filename and page number. Render citations in the UI as clickable badges ("contract.pdf, p.3").

**What you'll learn:**
- Real-world parsing differences across file formats (`pypdf`, `python-docx`, plain reads)
- Metadata design: deciding what to attach to a chunk (source, page, maybe section heading) so it's useful at answer time
- How to constrain retrieval by metadata (e.g. "only search within this user's uploaded files")

**How to approach it:**
1. Add one file format at a time, fully working, before adding the next.
2. Pass `user_id` server-side from the authenticated session — never trust a client-supplied ID (same pattern you already use in Uns).
3. Build citation rendering as soon as metadata exists — it's a small UI change but it's the single biggest trust signal in the whole product.

**Tips & tricks:**
- Scanned/image-based PDFs need OCR — decide upfront whether that's in scope or explicitly unsupported. Don't let it block you.
- If a question spans multiple files, log which files contributed to the answer — useful for debugging and a good demo moment.

---

## M3 — Retrieved-chunks panel + streaming

**What to expect:**
Two upgrades at once: a UI toggle that reveals exactly which chunks were retrieved (with similarity scores), and token-by-token streaming for answers instead of one big blob.

**What you'll learn:**
- Server-Sent Events (SSE) or chunked responses for streaming — a different pattern from anything in Uns or Amal+, and broadly transferable to any chat-style AI product
- How to surface retrieval internals in a UI without overwhelming the user (collapsed by default, expandable on demand)

**How to approach it:**
1. Get streaming working in isolation first (e.g. stream to a terminal/curl) before wiring it into React.
2. In React, append tokens to state as they arrive rather than waiting for the full response — watch for re-render performance if you're not batching updates.
3. The retrieved-chunks panel can reuse data you already have from M0 — you're not adding new backend logic, just exposing it.

**Tips & tricks:**
- This is your best interview demo moment: you can point at the screen and say "here's exactly what got retrieved and why," which proves understanding rather than just describing it.
- Watch out for partial-JSON issues if you're streaming structured data — stream plain text for the answer, send structured metadata (chunks, scores) as a separate call or at the end.

---

## M4 — Hybrid search + reranking

**What to expect:**
Vector search alone misses exact terms (IDs, names, specific figures) because embeddings encode semantic similarity, not exact matches. Add BM25 keyword search alongside vector search, merge results, then rerank with a cross-encoder or Voyage's rerank endpoint.

**What you'll learn:**
- Why semantic search and keyword search solve different problems, and why production systems use both
- Score fusion (e.g. reciprocal rank fusion) to combine two ranked lists into one
- Reranking as a cheap second pass over a larger candidate set (retrieve 20, rerank, keep top 5)

**How to approach it:**
1. Build a small test set of exact-match questions first (e.g. "what's the contract ID?") — confirm they fail with vector-only search, so you can later prove the fix worked.
2. Add BM25 as a separate retrieval path, don't try to fuse it into the vector query itself.
3. Add reranking last, after hybrid search already works — it's a refinement on top, not a replacement.

**Tips & tricks:**
- `rank_bm25` (pure Python) is enough for BM25 here — no need for Elasticsearch at this scale.
- Log retrieval results before and after reranking side-by-side during development — the difference is often more dramatic than expected.

---

## M5 — Evaluation harness

**What to expect:**
A small, fixed set of test questions with known correct chunks/answers. Run retrieval before and after changes (like M4) and measure precision/recall and answer faithfulness — actual numbers, not vibes.

**What you'll learn:**
- This is the single most-skipped skill in personal RAG projects, and the one that separates "I followed a tutorial" from "I understand RAG." It's also what most production teams actually spend their time on.
- Basic retrieval metrics (precision@k, recall@k) and a simple LLM-as-judge approach for answer faithfulness

**How to approach it:**
1. Write 15–20 test questions across your uploaded docs, with the correct chunk(s) and an acceptable answer noted by hand.
2. Run your pipeline against this set, log retrieved chunks vs. expected, compute simple precision/recall.
3. Re-run the same set after M4's hybrid search + reranking — now you have a before/after number to talk about.

**Tips & tricks:**
- Keep the eval set small and high-quality rather than large and noisy — 20 carefully chosen questions beat 200 sloppy ones.
- Don't use the LLM to both generate test questions and grade its own answers without a sanity check — spot-check a sample by hand.
- This is your strongest interview line: "hybrid search improved retrieval recall by X%" is concrete in a way "I built RAG" never is.

---

## M6 — Multi-turn conversation

**What to expect:**
Follow-up questions ("what about section 2?") need to resolve using prior turns, not start from zero. Add session-based memory and query rewriting/contextualization.

**What you'll learn:**
- Why naive RAG breaks down in conversation (the embedding for "what about section 2?" alone is nearly meaningless)
- Query rewriting: using the LLM itself to rephrase a follow-up into a standalone question before retrieval

**How to approach it:**
1. Store conversation history per session (same `user_id`-scoped pattern as before).
2. Before retrieval, run a small rewrite step: feed the last 1–2 turns + the new question to the LLM, ask it to produce a standalone query.
3. Test explicitly with pronouns and vague references ("that", "it", "the other one") — these are where naive multi-turn breaks.

**Tips & tricks:**
- Don't pass the entire conversation history into every prompt — summarize or truncate, or token costs and latency creep up fast.
- This is also where your eval set from M5 earns its keep — re-run it to confirm multi-turn changes didn't regress single-turn accuracy.

---

## M7 — Agentic RAG (stretch, optional)

**What to expect:**
Compound questions ("compare the termination clauses across all three contracts") need the system to break the question apart, retrieve multiple times, then synthesize. Noticeably slower — multiple LLM calls per question — so this is a real tradeoff, not a free upgrade.

**What you'll learn:**
- Query decomposition: splitting one complex question into several retrievable sub-questions
- Basic agentic patterns (the `deepagents` library you're already exploring is relevant here) — routing, multi-step reasoning, tool use

**How to approach it:**
Only attempt this after M0–M6 are solid. It's the least essential for a strong interview story — M5's eval numbers and M4's hybrid search already prove deep understanding without this.

**Tips & tricks:**
- Cap the number of sub-questions/retrieval rounds to avoid runaway latency or cost.
- Be upfront in any demo that this mode is slower by design — it's a feature of doing more work, not a bug.

---

## General tips for the whole project

- **One stage at a time.** Resist bolting on the next feature before the current one is actually tested and working — it's the fastest way to end up debugging three problems at once.
- **Keep a before/after log.** Especially from M4 onward, jot down what broke and what improved at each step — this becomes your interview narrative almost for free.
- **Lean on raw Python, not frameworks, when something breaks.** If LangChain were doing this for you, a bug would be a black box. Writing it yourself means every error is traceable to a function you wrote.
- **Use Claude as a pairing partner, not an autopilot.** Ask it to explain *why* an approach works rather than just generating the code — the goal here is understanding, not just a working repo.
- **Deploy early and often.** A live link beats a perfect local build every time someone actually wants to see it.
- **M0–M3 alone is already a legitimate portfolio piece.** If time runs out, stopping there is not a failure — it's a complete, demoable RAG project.

---

## Glossary

- **Naive (RAG)** — the standard term in RAG literature for the simplest version of the pipeline: embed, retrieve top-k by similarity, stuff into a prompt, generate. Not an insult — like "naive Bayes," it just means no extra sophistication added yet. Anything past it (hybrid search, reranking, agentic) is usually called "advanced RAG."
- **Blob** — short for "binary large object," but used loosely here to mean *one undivided chunk of data*. "One big blob" response = the LLM finishes the whole answer before sending it, vs. streaming, where you get it token-by-token as it's generated.
- **Upsert** — "update or insert." Insert a row if its ID doesn't exist yet; update it in place if it does. This is why chunk IDs should be deterministic (a hash of the chunk's content) — re-running ingestion on the same file refreshes existing rows instead of creating duplicates.
- **CORS** (Cross-Origin Resource Sharing) — a browser security rule that blocks JavaScript on one domain (e.g. your Vercel frontend) from calling an API on a different domain (e.g. your Railway backend) unless the backend explicitly allows it via response headers. Works fine on localhost, then breaks the moment frontend and backend are deployed separately — configure it before that happens.
