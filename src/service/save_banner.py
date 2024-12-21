import os
from fastapi import UploadFile
from datetime import datetime


async def save_banner_to_storage(file: UploadFile, course_id: int) -> str:
    file_extension = file.filename.split('.')[-1]
    filename = f"course_{course_id}_banner_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_extension}"

    file_path = os.path.join("banners", filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    return file_path
