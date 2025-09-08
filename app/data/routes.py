# app/data/routes.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.database import get_db, supabase
from app.auth.dependencies import AccessTokenBearer
from app.data.schemas import TrainingDataSourceCreate, TrainingDataSourceRead, TrainingDataSourceUpdate
from app.data.service import TrainingDataService
from app.data.models import TrainingDataChunk, TrainingDataSource
import uuid
from datetime import datetime
from app.auth.dependencies import AccessTokenBearer
from app.data.schemas import TrainingDataSourceCreate, TrainingDataSourceRead
from app.data.service import TrainingDataService
from app.data.models import TrainingDataChunk
from app.auth.roles import admin_only, company_roles, all_roles, user_only
from app.companies.service import CompanyService
from app.auth.service import UserService
import logging


from typing import List
import fitz  # PyMuPDF
import docx
import io

router = APIRouter()
data_service = TrainingDataService()
company_service = CompanyService()
user_service = UserService()


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
        logging.info(f"Upload started for company_uid={company_uid} file={file.filename}")

        file_bytes = await file.read()

        try:
            file_text = extract_text(file, file_bytes)
            logging.info(f"Extracted text length: {len(file_text)}")
        except Exception as e:
            logging.error(f"Text extraction failed: {e}")
            raise HTTPException(status_code=400, detail=f"Text extraction failed: {str(e)}")

        file_path = f"{company_uid}/{uuid.uuid4()}_{file.filename}"
        logging.info(f"Uploading file to path: {file_path}")

        response = supabase.storage.from_("company-data").upload(file_path, file_bytes)

        if not hasattr(response, "path") or not response.path:
            logging.error(f"Upload failed, response: {response}")
            raise HTTPException(status_code=500, detail="❌ Upload failed: No path in response")

        signed_url_response = supabase.storage.from_("company-data").create_signed_url(file_path, 3600)

        if not signed_url_response or not signed_url_response.get("signedURL"):
            logging.error(f"Signed URL generation failed, response: {signed_url_response}")
            raise HTTPException(status_code=500, detail="❌ Failed to generate signed URL")

        source_data = TrainingDataSourceCreate(
            name=file.filename,
            type=file.content_type,
            file_path=file_path,
            company_uid=company_uid,
            status="uploaded"
        )

        new_source = await data_service.create_data_source(
            user_email=token_details['user']['email'],
            company_uid=company_uid,
            data=source_data,
            session=session
        )

        chunks = chunk_text(file_text)
        logging.info(f"Chunked text into {len(chunks)} chunks")

        for idx, chunk in enumerate(chunks):
            new_chunk = TrainingDataChunk(
                source_uid=new_source.uid,
                content=chunk,
                chunk_index=idx,
                token_count=len(chunk.split())
            )
            session.add(new_chunk)

        await session.commit()

        # ✅ Qdrant vector embedding step goes HERE
        await data_service.process_chunks_for_vector_search(
            source_uid=new_source.uid,
            chunks=chunks,
            company_uid=company_uid,
            # session=session 
        )

        logging.info("Upload, DB commit, and Qdrant embedding successful")

        return new_source

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/files/{company_uid}", response_model=List[TrainingDataSourceRead])
async def get_files_for_company(
    company_uid: str,
    session: AsyncSession = Depends(get_db),
    token_details: dict = Depends(AccessTokenBearer())
):
    files = await data_service.get_data_sources_for_company(company_uid, session)
    return files

from app.data.schemas import TrainingDataSourceUpdate

@router.patch("/files/{file_uid}", response_model=TrainingDataSourceRead)
async def update_file(
    file_uid: str,
    update_data: TrainingDataSourceUpdate,
    session: AsyncSession = Depends(get_db),
    token_details: dict = Depends(AccessTokenBearer())
):
    updated_file = await data_service.update_data_source(file_uid, update_data, session)
    if not updated_file:
        raise HTTPException(status_code=404, detail="File not found")
    return updated_file


@router.delete("/files/{file_uid}", status_code=204)
async def delete_file(
    file_uid: str,
    session: AsyncSession = Depends(get_db),
    token_details: dict = Depends(AccessTokenBearer())
):
    success = await data_service.delete_data_source(file_uid, session)
    if not success:
        raise HTTPException(status_code=404, detail="File not found")

    return {"detail": "File deleted"}
