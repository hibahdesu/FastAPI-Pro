# app/data/routes.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.database import get_db, supabase
from app.auth.dependencies import AccessTokenBearer
from app.data.schemas import TrainingDataSourceCreate, TrainingDataSourceRead
from app.data.service import TrainingDataService

import uuid
from datetime import datetime

router = APIRouter()
data_service = TrainingDataService()



# @router.post("/upload/{company_uid}", response_model=TrainingDataSourceRead)
# async def upload_file_for_company(
#     company_uid: str,
#     file: UploadFile = File(...),
#     session: AsyncSession = Depends(get_db),
#     token_details: dict = Depends(AccessTokenBearer())
# ):
#     try:
#         # Step 1: Read file content
#         file_bytes = await file.read()

#         # Step 2: Generate unique file path
#         file_path = f"{company_uid}/{uuid.uuid4()}_{file.filename}"

#         # Step 3: Upload file to Supabase (private bucket)
#         response = supabase.storage.from_("company-data").upload(file_path, file_bytes)
        
#         # DEBUG: print the response object
#         print("Upload response:", response)
#         print("Response type:", type(response))

#         # Check response properly
#         if not hasattr(response, "path") or not response.path:
#             raise HTTPException(status_code=500, detail="❌ Upload failed: No path in response")

#         # Step 4: Generate a signed URL (valid for 1 hour)
#         signed_url_response = supabase.storage.from_("company-data").create_signed_url(file_path, 3600)

#         if not signed_url_response or not signed_url_response.get("signedURL"):
#             raise HTTPException(status_code=500, detail="❌ Failed to generate signed URL")

#         # Step 5: Save metadata to the database
#         source_data = TrainingDataSourceCreate(
#             name=file.filename,
#             type=file.content_type,
#             file_path=file_path,
#             company_uid=company_uid,
#             status="uploaded"
#         )

#         new_source = await data_service.create_data_source(source_data, session)

#         return new_source

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.database import get_db, supabase
from app.auth.dependencies import AccessTokenBearer
from app.data.schemas import TrainingDataSourceCreate, TrainingDataSourceRead
from app.data.service import TrainingDataService
from app.data.models import TrainingDataChunk

import uuid
from datetime import datetime

from typing import List
import fitz  # PyMuPDF
import docx
import io

router = APIRouter()
data_service = TrainingDataService()


def chunk_text(text: str, max_tokens: int = 500) -> List[str]:
    words = text.split()
    return [" ".join(words[i:i + max_tokens]) for i in range(0, len(words), max_tokens)]


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text


def extract_text_from_docx(file_bytes: bytes) -> str:
    file_stream = io.BytesIO(file_bytes)
    doc = docx.Document(file_stream)
    return "\n".join([para.text for para in doc.paragraphs])


def extract_text(file: UploadFile, file_bytes: bytes) -> str:
    content_type = file.content_type

    if content_type == "application/pdf":
        return extract_text_from_pdf(file_bytes)
    elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(file_bytes)
    elif content_type.startswith("text/"):
        return file_bytes.decode("utf-8", errors="ignore")
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {content_type}")


@router.post("/upload/{company_uid}", response_model=TrainingDataSourceRead)
async def upload_file_for_company(
    company_uid: str,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
    token_details: dict = Depends(AccessTokenBearer())
):
    try:
        # Step 1: Read file content
        file_bytes = await file.read()

        # Step 2: Extract text
        try:
            file_text = extract_text(file, file_bytes)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Text extraction failed: {str(e)}")

        # Step 3: Generate unique file path
        file_path = f"{company_uid}/{uuid.uuid4()}_{file.filename}"

        # Step 4: Upload file to Supabase
        response = supabase.storage.from_("company-data").upload(file_path, file_bytes)

        if not hasattr(response, "path") or not response.path:
            raise HTTPException(status_code=500, detail="❌ Upload failed: No path in response")

        # Step 5: Generate signed URL
        signed_url_response = supabase.storage.from_("company-data").create_signed_url(file_path, 3600)

        if not signed_url_response or not signed_url_response.get("signedURL"):
            raise HTTPException(status_code=500, detail="❌ Failed to generate signed URL")

        # Step 6: Save metadata
        source_data = TrainingDataSourceCreate(
            name=file.filename,
            type=file.content_type,
            file_path=file_path,
            company_uid=company_uid,
            status="uploaded"
        )

        new_source = await data_service.create_data_source(source_data, session)

        # Step 7: Chunk and save content
        chunks = chunk_text(file_text)
        for idx, chunk in enumerate(chunks):
            new_chunk = TrainingDataChunk(
                source_uid=new_source.uid,
                content=chunk,
                chunk_index=idx,
                token_count=len(chunk.split())
            )
            session.add(new_chunk)

        await session.commit()

        return new_source

    except HTTPException:
        raise  # Re-raise known HTTP errors
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
