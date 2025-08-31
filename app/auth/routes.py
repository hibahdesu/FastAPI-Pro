# app/auth/routes.py
# app/auth/routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from app.auth.schemas import UserCreateModel, UserModel, UserResponseModel
from app.auth.service import UserService
from app.db.database import get_db
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException

auth_router = APIRouter()
user_service = UserService()

# @auth_router.post('/signup', response_model=UserModel, status_code=status.HTTP_201_CREATED)
# async def create_user_account(user_data: UserCreateModel, session: AsyncSession = Depends(get_db)):
#     email = user_data.email

#     user_exists = await user_service.user_exists(email, session)

#     if user_exists:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User with email already exists")
    
#     new_user = await user_service.create_user(user_data, session)

#     return new_user


@auth_router.post('/signup', response_model=UserResponseModel, status_code=status.HTTP_201_CREATED)
async def create_user_account(user_data: UserCreateModel, session: AsyncSession = Depends(get_db)):
    print("📥 Received signup request")

    email = user_data.email
    user_exists = await user_service.user_exists(email, session)
    if user_exists:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User with email already exists")

    new_user = await user_service.create_user(user_data, session)
    response_data = UserResponseModel.from_orm(new_user)
    print("✅ Returning user:", response_data)
    return response_data

@auth_router.get("/ping")
async def ping():
    return {"message": "pong"}