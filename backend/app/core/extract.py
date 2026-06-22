from fastapi import UploadFile

async def extract_file(file: UploadFile):
    content = await file.read()
    print(content)