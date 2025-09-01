# app/companies/routes.py
from fastapi import APIRouter, status, Depends
from app.companies.service import CompanyService
from app.db.database import get_db
from app.companies.schemas import CompanyCreateModel, CompanyUpdateModel, Company
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from typing import List
from app.auth.dependencies import AccessTokenBearer, RoleChecker


company_router = APIRouter()
company_service = CompanyService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(['admin', 'companyOwner', 'worker', 'user']))


@company_router.get("/", response_model=List[Company], dependencies=[role_checker])
async def get_all_companies(session: AsyncSession = Depends(get_db), 
                            user_details=Depends(access_token_bearer)):
    print(user_details)
    companies = await company_service.get_all_companies(session)
    return companies


@company_router.get("/user/{user_uid}", response_model=List[Company], dependencies=[role_checker])
async def get_user_companies_submissions(
                            user_uid:str,
                            session: AsyncSession = Depends(get_db), 
                            user_details=Depends(access_token_bearer)):
    print(user_details)
    companies = await company_service.get_user_company(user_uid, session)
    return companies


@company_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Company, dependencies=[role_checker])
async def create_a_company(company_data: CompanyCreateModel, session: AsyncSession = Depends(get_db), token_details: dict=Depends(access_token_bearer)) -> dict:
    user_uid = token_details.get('user')['user_uid']
    new_company = await company_service.create_company(company_data, user_uid, session)
    return new_company


@company_router.get("/{company_uid}", response_model=Company, dependencies=[role_checker])
async def get_a_company(company_uid: str, session: AsyncSession = Depends(get_db), token_details: dict=Depends(access_token_bearer)):
    company = await company_service.get_company(company_uid, session)

    if company:
        return company
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    


@company_router.patch("/{company_uid}", response_model=Company, dependencies=[role_checker])
async def update_a_company(company_uid: str, company_update_data: CompanyUpdateModel, session: AsyncSession = Depends(get_db), user_details=Depends(access_token_bearer)):
    updated_company = await company_service.update_company(company_uid, company_update_data, session)

    if updated_company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        
    else:
        return updated_company
        
    
@company_router.delete("/{company_uid}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker])
async def delete_a_company(company_uid: str, session: AsyncSession = Depends(get_db), user_details=Depends(access_token_bearer)):
    deleted_company = await company_service.delete_company(company_uid, session)

    if deleted_company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        
    else:
        return {}
        
    
    
    

