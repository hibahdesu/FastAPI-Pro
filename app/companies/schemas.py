# app/companies/schemas.py
from pydantic import BaseModel, EmailStr
from pydantic import Field
import uuid
from datetime import datetime

class CompanyBase(BaseModel):
    uid: uuid.UUID 
    name: str
    email: EmailStr
    phone: str 
    industry: str
    plan: str
    is_active: bool = False
    is_verified: bool = False
    monthly_ticket_limit: int = Field(default=5000)
    ticket_usage: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class CompanyCreateModel(BaseModel):
    name: str 
    email: EmailStr
    phone: str
    industry: str
    plan: str
    is_active: bool
    is_verified: bool 
    monthly_ticket_limit: int 
    ticket_usage: int 

class CompanyUpdateModel(BaseModel):
    name: str 
    email: EmailStr
    phone: str
    industry: str
    plan: str
    is_active: bool
    is_verified: bool 
    monthly_ticket_limit: int 
    ticket_usage: int 


