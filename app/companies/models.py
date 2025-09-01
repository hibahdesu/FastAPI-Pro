# app/companies/models.py
from sqlmodel import SQLModel, Field, Column, String, Relationship
import sqlalchemy.dialects.postgresql as pg
from app.auth import models
from datetime import datetime
from pydantic import EmailStr
import uuid
from typing import Optional


class Company(SQLModel, table=True):
    __tablename__ = "companies"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )
    name: str
    email: EmailStr
    phone: str | None = None
    industry: str
    plan: str
    is_active: bool = True
    is_verified: bool = False
    monthly_ticket_limit: int 
    ticket_usage: int
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    user: Optional["models.User"] = Relationship(back_populates="company")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))


    def __repr__(self):
        return f"<Company {self.name} - {self.email}>"