# app/data/service.py
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.data.models import TrainingDataSource
from app.data.schemas import TrainingDataSourceCreate
from datetime import datetime


class TrainingDataService:

    async def create_data_source(
        self, data: TrainingDataSourceCreate, session: AsyncSession
    ) -> TrainingDataSource:
        new_source = TrainingDataSource(
            name=data.name,
            type=data.type,
            file_path=data.file_path,
            company_uid=data.company_uid,
            status=data.status,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        session.add(new_source)
        await session.commit()
        await session.refresh(new_source)
        return new_source

    async def get_data_sources_for_company(
        self, company_uid: str, session: AsyncSession
    ) -> list[TrainingDataSource]:
        statement = select(TrainingDataSource).where(
            TrainingDataSource.company_uid == company_uid
        ).order_by(TrainingDataSource.created_at.desc())

        results = await session.exec(statement)
        return results.all()
