# test_extract.py
from app.core.extract import extract_document

result = extract_document("test_docs/PO.pdf")

for entry in result:
    print(f"--- page {entry['page_number']} ---")
    print(entry['content'][:200])  # first 200 chars, avoid flooding terminal
    print()