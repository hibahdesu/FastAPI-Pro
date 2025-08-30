from fastapi import APIRouter, Depends, HTTPException
from app.auth.schemas import UserCreateModel

auth_router = APIRouter()

auth_router.post('/signup')
async def create_user_account(user_data: UserCreateModel):
    pass