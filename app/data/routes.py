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

        # Step 2: Generate unique file path
        file_path = f"{company_uid}/{uuid.uuid4()}_{file.filename}"

        # Step 3: Upload file to Supabase (private bucket)
        response = supabase.storage.from_("company-data").upload(file_path, file_bytes)
        
        # DEBUG: print the response object
        print("Upload response:", response)
        print("Response type:", type(response))

        # Check response properly
        if not hasattr(response, "path") or not response.path:
            raise HTTPException(status_code=500, detail="❌ Upload failed: No path in response")

        # Step 4: Generate a signed URL (valid for 1 hour)
        signed_url_response = supabase.storage.from_("company-data").create_signed_url(file_path, 3600)

        if not signed_url_response or not signed_url_response.get("signedURL"):
            raise HTTPException(status_code=500, detail="❌ Failed to generate signed URL")

        # Step 5: Save metadata to the database
        source_data = TrainingDataSourceCreate(
            name=file.filename,
            type=file.content_type,
            file_path=file_path,
            company_uid=company_uid,
            status="uploaded"
        )

        new_source = await data_service.create_data_source(source_data, session)

        return new_source

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
