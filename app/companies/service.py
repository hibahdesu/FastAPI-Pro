from sqlmodel.ext.asyncio.session import AsyncSession
from app.companies.schemas import CompanyCreateModel, CompanyUpdateModel
from sqlmodel import select, desc
from app.companies.models import Company

class CompanyService:
    async def get_all_companies(self, session: AsyncSession) -> list:
        statement = select(Company).order_by(desc(Company.created_at))

        results = await session.exec(statement)

        companies = results.all()

        return companies

    async def get_company(self, company_uid: str, session: AsyncSession):
        statement = select(Company).where(Company.uid == company_uid)

        results = await session.exec(statement)

        company = results.first()

        return company if company is not None else None

    async def create_company(self, company_data: CompanyCreateModel, session: AsyncSession) -> dict:
        company_data_dict = company_data.model_dump()

        new_company = Company(**company_data_dict)

        session.add(new_company)

        await session.commit()

        return new_company

    async def update_company(self, company_uid: str, update_data: CompanyUpdateModel, session: AsyncSession):
        company_to_update = await self.get_company(company_uid, session)


        if company_to_update is not None:

            update_data_dict = update_data.model_dump()

            for k, v in update_data_dict.items():
                setattr(company_to_update, k, v)

            await session.commit()

            return company_to_update
        
        else:
            return None

    async def delete_company(self, company_uid: str, session: AsyncSession):
        company_to_delete = await self.get_company(company_uid, session)

        if company_to_delete is not None:
            await session.delete(company_to_delete)

            await session.commit()

        else: 
            return None