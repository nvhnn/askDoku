"""
Baseline test: exact-match questions against vector-only retrieval.

Expectation: all (or most) of these should FAIL — i.e., the expected answer
does not appear in the top-5 retrieved chunks. That confirms vector search
alone cannot handle exact identifier lookups, motivating hybrid search (M4).

Run from the backend/ directory:
    python -m test_files.test_exact_match_retrieval

Results are printed to stdout and written to
    test_files/exact_match_results_baseline.json
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.rag import retrieve_context

FIXTURE_PATH = Path(__file__).parent / "exact_match_fixture.json"
OUTPUT_PATH = Path(__file__).parent / "exact_match_results_baseline.json"


def answer_found(expected: str, chunks: list[dict]) -> bool:
    expected_lower = expected.lower()
    return any(expected_lower in chunk["content"].lower() for chunk in chunks)


def run():
    fixture = json.loads(FIXTURE_PATH.read_text())
    results = []
    passed = 0
    failed = 0

    print("=" * 70)
    print("Exact-match retrieval baseline (vector-only)")
    print("=" * 70)

    for case in fixture:
        question = case["question"]
        expected = case["expected_answer"]

        chunks = retrieve_context(question)
        found = answer_found(expected, chunks)

        status = "PASS" if found else "FAIL"
        if found:
            passed += 1
        else:
            failed += 1

        print(f"\n[{status}] {case['id']}")
        print(f"  Q: {question}")
        print(f"  Expected: {expected}")
        print(f"  Top-5 retrieved chunks:")
        for i, chunk in enumerate(chunks, 1):
            snippet = chunk["content"].replace("\n", " ")[:120]
            sim = round(chunk.get("similarity", 0), 4)
            print(f"    {i}. (sim={sim}) [{chunk.get('filename', '?')} p{chunk.get('page_number', '?')}] {snippet}...")

        results.append({
            "id": case["id"],
            "question": question,
            "expected_answer": expected,
            "source_file": case["source_file"],
            "status": status,
            "retrieved_chunks": [
                {
                    "rank": i + 1,
                    "filename": c.get("filename"),
                    "page_number": c.get("page_number"),
                    "similarity": round(c.get("similarity", 0), 4),
                    "content_snippet": c["content"][:300],
                }
                for i, c in enumerate(chunks)
            ],
        })

    print("\n" + "=" * 70)
    print(f"Results: {passed} passed / {failed} failed out of {len(fixture)} cases")
    print(f"(FAIL = vector search missed the exact answer — expected for this baseline)")
    print("=" * 70)

    OUTPUT_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nFull results saved to {OUTPUT_PATH}")

    return results


if __name__ == "__main__":
    run()
