from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from typing import Optional, List
from app.companies.schemas import Company
from app.data.schemas import TrainingDataSourceRead
from pydantic import ConfigDict

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
    payment_id: Optional[str] = None 
    is_verified: bool 
    is_active: bool 
    is_superuser: bool
    password_hash: str = Field(exclude=True)
    # companies: List[Company]
    created_at: datetime 
    updated_at: datetime 

class UserCompanyModel(UserModel):
    companies: List[Company] = []
    data: List[TrainingDataSourceRead] = []

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

    # class Config:
        # from_attributes = True
    model_config = ConfigDict(from_attributes=True)

class UserLoginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)

class UserUpdateModel(BaseModel):
    first_name: Optional[str] = Field(max_length=25)
    last_name: Optional[str] = Field(max_length=25)
    username: Optional[str] = Field(max_length=10)
    email: Optional[str] = Field(max_length=40)
    company_name: Optional[str] = None
    # has_paid: Optional[bool] = None
    # is_verified: Optional[bool] = None
    # is_active: Optional[bool] = None
    # is_superuser: Optional[bool] = None

class PasswordResetRequestModel(BaseModel):
    email: str


class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str




class SignupResponseModel(BaseModel):
    message: str
    user: UserResponseModel  # This already exists in your schema

    # class Config:
        # from_attributes = True  # Ensures compatibility with ORM models
    model_config = ConfigDict(from_attributes=True)