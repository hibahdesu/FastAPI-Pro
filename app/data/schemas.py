# app/data/schemas.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid


class TrainingDataSourceCreate(BaseModel):
    name: str
    type: str  # e.g. "application/pdf"
    file_path: str
    company_uid: uuid.UUID
    status: str = "uploaded"



class TrainingDataSourceRead(BaseModel):
    uid: uuid.UUID
    name: str
    type: str
    file_path: str
    user_uid: Optional[uuid.UUID]
    company_uid: Optional[uuid.UUID]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TrainingDataSourceUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None