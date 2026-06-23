from app.core.clients import gemini
from fastapi import UploadFile

CHUNKS = 512

async def generate_response(question: str) -> str:
    # extract the file
    content = await file.read()
    print(content)

    # chunk it