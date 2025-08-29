# app/companies/routes.py
from fastapi import APIRouter, status, Depends
from app.companies.service import CompanyService
from app.db.database import get_db
from app.companies.models import Company
from app.companies.schemas import CompanyCreateModel, CompanyUpdateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from typing import List


company_router = APIRouter()
company_service = CompanyService()

@company_router.get("/", response_model=List[Company])
async def get_all_companies(session: AsyncSession = Depends(get_db)):
    companies = await company_service.get_all_companies(session)
    return companies


@company_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Company)
async def create_a_company(company_data: CompanyCreateModel, session: AsyncSession = Depends(get_db)) -> dict:
    new_company = await company_service.create_company(company_data, session)
    return new_company


@company_router.get("/{company_uid}", response_model=Company)
async def get_a_company(company_uid: str, session: AsyncSession = Depends(get_db)):
    company = await company_service.get_company(company_uid, session)

    if company:
        return company
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    


@company_router.patch("/{company_uid}", response_model=Company)
async def update_a_company(company_uid: str, company_update_data: CompanyUpdateModel, session: AsyncSession = Depends(get_db)):
    updated_company = await company_service.update_company(company_uid, company_update_data, session)

    if updated_company:
        return updated_company
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    


@company_router.delete("/{company_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_a_company(company_uid: str, session: AsyncSession = Depends(get_db)):
    deleted_company = await company_service.delete_company(company_uid, session)

    if deleted_company:
        return None
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    
    
    

