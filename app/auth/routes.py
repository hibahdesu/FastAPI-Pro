# app/auth/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.auth.schemas import UserCreateModel, UserModel, UserResponseModel, UserLoginModel
from app.auth.service import UserService
from app.db.database import get_db
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from app.auth.utils import create_access_token, decode_token, verify_password
from datetime import timedelta
from fastapi.responses import JSONResponse

auth_router = APIRouter()
user_service = UserService()

REFRESH_TOKEN_EXPIRY = 2

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


@auth_router.post('/login')
async def login_users(login_data: UserLoginModel, session: AsyncSession = Depends(get_db)):
    try:
        email = login_data.email
        password = login_data.password

        user = await user_service.get_user_by_email(email, session)
        if not user:
            print("❌ User not found:", email)
            raise HTTPException(status_code=403, detail="Invalid Email Or Password")

        print("🔐 Verifying password for:", email)
        print("Stored hash:", user.password_hash)

        password_valid = verify_password(password, user.password_hash)
        if not password_valid:
            print("❌ Invalid password")
            raise HTTPException(status_code=403, detail="Invalid Email Or Password")

        access_token = create_access_token(
            user_data={'email': user.email, 'user_uid': str(user.uid)}
        )
        
        refresh_token = create_access_token(
            user_data={'email': user.email, 'user_uid': str(user.uid)},
            refresh=True,
            expiry=timedelta(days=REFRESH_TOKEN_EXPIRY)
        )

        print("✅ Login successful for:", email)
        return JSONResponse(content={
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "email": user.email,
                "uid": str(user.uid)
            }
        })

    except Exception as e:
        print("🔥 Exception during login:", repr(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")