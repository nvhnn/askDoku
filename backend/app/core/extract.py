
from pypdf import PdfReader
import docx

def extract_document(filepath: str) -> str:
    if filepath.endswith(".pdf"):
        reader = PdfReader(filepath)
        text = "\n".join(page.extract_text() for page in reader.pages)
        return text
    
    elif filepath.endswith(".docx"):
        doc = docx.Document(filepath)
        text = "\n".join(p.text for p in doc.paragraphs)
        return text
    
    elif filepath.endswith((".txt", ".md")):
        with open(filepath, "r", encoding="UTF-8") as f:
            return f.read()
        
    else:
        raise ValueError(f"Unsupported file type: {filepath}")