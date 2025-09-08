# app/data/models.py
from sqlmodel import SQLModel, Field, Column, Relationship
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
import sqlalchemy.dialects.postgresql as pg
import uuid



if TYPE_CHECKING:
    from app.auth.models import User
    from app.companies.models import Company
class TrainingDataSource(SQLModel, table=True):
    __tablename__ = "training_data_sources"

    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    company_uid: uuid.UUID = Field(foreign_key="companies.uid", nullable=False)
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")

    type: str  # e.g., "pdf", "txt", "web", etc.
    name: str  # file name
    source_url: Optional[str] = None  # for web-based sources
    file_path: Optional[str] = None  # path in Supabase
    status: str = Field(default="processed")  # or "uploaded", "processing"
    user: Optional["User"] = Relationship(back_populates="data")
    company: Optional["Company"] = Relationship(back_populates="data")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    chunks: List["TrainingDataChunk"] = Relationship(back_populates="source")


class TrainingDataChunk(SQLModel, table=True):
    __tablename__ = "training_data_chunks"

    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    source_uid: uuid.UUID = Field(foreign_key="training_data_sources.uid", nullable=False)

    content: str  # the actual chunk text
    embedding: Optional[List[float]] = Field(
        sa_column=Column(pg.ARRAY(pg.FLOAT))
    )
    token_count: Optional[int] = None
    chunk_index: int  # the order of chunk in the file

    created_at: datetime = Field(default_factory=datetime.utcnow)

    source: Optional[TrainingDataSource] = Relationship(back_populates="chunks")
