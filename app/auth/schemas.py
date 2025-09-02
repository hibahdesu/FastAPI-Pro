from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from typing import Optional, List
from app.companies.schemas import Company

class UserCreateModel(BaseModel):
    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)
    username: str = Field(max_length=10)
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)


class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    company_name: Optional[str] = None 
    has_paid: bool
    company_name: Optional[str] = None 
    is_verified: bool 
    is_active: bool 
    is_superuser: bool
    password_hash: str = Field(exclude=True)
    # companies: List[Company]
    created_at: datetime 
    updated_at: datetime 

class UserCompanyModel(UserModel):
    companies: List[Company] = []

class UserResponseModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    company_name: Optional[str] = None
    payment_id: Optional[str] = None
    has_paid: bool = Field(default=False)
    is_verified: bool = Field(default=False)
    is_active: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserLoginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)