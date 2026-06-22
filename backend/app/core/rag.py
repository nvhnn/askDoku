from app.core.llm_clients import client
from fastapi import UploadFile

CHUNKS = 512

async def generate_response(question: str) -> str:
    # extract the file
    content = await file.read()
    print(content)

    # chunk it