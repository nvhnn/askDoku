from app.core.extract import extract_document
from app.core.chunk import chunk_text

pages = extract_document("test_docs/PO.pdf")
print(f"{len(pages)} pages extracted")
print("First page sample:", pages[0])

chunks = chunk_text(pages, document_id="test123")
print(f"\n{len(chunks)} chunks total")
print("First chunk:", chunks[0])
