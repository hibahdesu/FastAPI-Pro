from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from uuid import uuid4
from datetime import datetime
from app.whatsapp.models import WhatsAppChannel

class Bot(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str
    company_id: str = Field(foreign_key="company.id")
    default_language: str = Field(default="en")
    fallback_message: str = Field(default="Sorry, I didn’t understand that.")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    whatsapp_channel: Optional["WhatsAppChannel"] = Relationship(back_populates="bot")
