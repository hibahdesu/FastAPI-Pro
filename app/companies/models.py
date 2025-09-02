# app/companies/models.py
from sqlmodel import SQLModel, Field, Column, String, Relationship
import sqlalchemy.dialects.postgresql as pg
from app.auth.models import User
# from app.billing.models import Billing
from datetime import datetime
from pydantic import EmailStr
import uuid
from typing import Optional, TYPE_CHECKING

# if TYPE_CHECKING:
    
#     from app.billing.models import Billing

    
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
    user: Optional["User"] = Relationship(back_populates="company")

    # billing: Optional["Billing"] = Relationship(back_populates="company", sa_relationship_kwargs={"uselist": False})
    # billing: Optional["Billing"] = Relationship(
    #     back_populates="company", sa_relationship_kwargs={"uselist": False}
    # )
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))


    def __repr__(self):
        return f"<Company {self.name} - {self.email}>"