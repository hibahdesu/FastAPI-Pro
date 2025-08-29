from sqlmodel.ext.asyncio.session import AsyncSession
from app.companies.schemas import CompanyCreateModel, CompanyUpdateModel

class CompanyService:
    async def get_all_companies(self, session: AsyncSession) -> list:
        pass

    async def get_company(self, company_uid: str, session: AsyncSession):
        pass

    async def create_company(self, company_data: CompanyCreateModel, session: AsyncSession) -> dict:
        pass

    async def update_company(self, company_uid: str, update_data: CompanyUpdateModel, session: AsyncSession):
        pass

    async def delete_company(self, company_uid: str, session: AsyncSession):
        pass