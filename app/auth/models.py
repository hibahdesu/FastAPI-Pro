from sqlmodel import SQLModel, Field, Column, String
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
    username: str
    email: str
    first_name: str
    last_name: str
    company_name: str
    has_paid: bool = Field(default=False)
    payment_id: str = Column(String, nullable=True)
    is_verified: bool = Field(default=False)
    is_active: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    password_hash: str = Field(exclude=True)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    def __repr__(self):
        return f"<User {self.username}>"
