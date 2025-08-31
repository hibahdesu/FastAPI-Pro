from sqlmodel import SQLModel, Field, Column
from typing import Optional
import uuid
from datetime import datetime
import sqlalchemy.dialects.postgresql as pg


class User(SQLModel, table=True):
    __tablename__ = "users"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )
    username: str = Field(nullable=False)
    email: str = Field(nullable=False, unique=True)
    first_name: str
    last_name: str
    company_name: Optional[str] = None
    payment_id: Optional[str] = None
    has_paid: bool = Field(default=False)
    is_verified: bool = Field(default=False)
    is_active: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    password_hash: str = Field(exclude=True)  # Do not include in the response model
    created_at: datetime = Field(default_factory=datetime.utcnow)  # Use default_factory to generate current time
    updated_at: datetime = Field(default_factory=datetime.utcnow)  # Use default_factory to generate current time

    def __repr__(self):
        return f"<User {self.username}>"
