# app/data/service.py
# app/data/service.py

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.data.models import TrainingDataSource, TrainingDataChunk
from app.data.schemas import TrainingDataSourceCreate, TrainingDataSourceUpdate
from typing import Optional
from datetime import datetime
from app.companies.service import CompanyService
from app.auth.service import UserService
from fastapi.exceptions import HTTPException
from fastapi import HTTPException, status

from app.core.config import Config
from app.vectorstore.qdrant_client import get_client
from sentence_transformers import SentenceTransformer
import uuid

company_service = CompanyService()
user_service = UserService()


class TrainingDataService:

    async def create_data_source(
        self, user_email: str, company_uid: str, data: TrainingDataSourceCreate, session: AsyncSession
    ) -> TrainingDataSource:
        try:
            company = await company_service.get_company(company_uid, session)
            user = await user_service.get_user_by_email(user_email, session)
            new_data = TrainingDataSource(**data.model_dump())

            new_data.user = user
            new_data.company = company

            session.add(new_data)
            await session.commit()
            return new_data

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def get_data_sources_for_company(
        self, company_uid: str, session: AsyncSession
    ) -> list[TrainingDataSource]:
        statement = select(TrainingDataSource).where(
            TrainingDataSource.company_uid == company_uid
        ).order_by(TrainingDataSource.created_at.desc())

        results = await session.exec(statement)
        return results.all()

    async def update_data_source(
        self, file_uid: str, update_data: TrainingDataSourceUpdate, session: AsyncSession
    ) -> Optional[TrainingDataSource]:
        statement = select(TrainingDataSource).where(TrainingDataSource.uid == file_uid)
        result = await session.exec(statement)
        file_obj = result.first()

        if not file_obj:
            return None

        update_data_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_data_dict.items():
            setattr(file_obj, key, value)

        await session.commit()
        await session.refresh(file_obj)
        return file_obj

    async def delete_data_source(self, file_uid: str, session: AsyncSession) -> bool:
        statement = select(TrainingDataSource).where(TrainingDataSource.uid == file_uid)
        result = await session.exec(statement)
        file_obj = result.first()

        if not file_obj:
            return False

        await session.delete(file_obj)
        await session.commit()
        return True

    # ✅ NEW METHOD: Embeds and uploads chunks to Qdrant
    async def process_chunks_for_vector_search(
        self,
        source_uid: str,
        chunks: list[str],
        company_uid: str,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        qdrant = get_client()
        collection_name = f"company_{company_uid}"

        # 1. Ensure collection exists (or recreate it)
        qdrant.recreate_collection(
            collection_name=collection_name,
            vectors_config={
                "size": 384,
                "distance": "Cosine"
            }
        )

        # 2. Load the sentence-transformer model
        embedder = SentenceTransformer(model_name)

        # 3. Generate embeddings
        embeddings = embedder.encode(chunks).tolist()

        # 4. Prepare Qdrant points
        points = []
        for idx, (text, vector) in enumerate(zip(chunks, embeddings)):
            points.append({
                "id": str(uuid.uuid4()),
                "vector": vector,
                "payload": {
                    "text": text,
                    "chunk_index": idx,
                    "source_uid": source_uid,
                    "company_uid": company_uid,
                }
            })

        # 5. Upsert to Qdrant
        qdrant.upsert(collection_name=collection_name, points=points)
        print(f"✅ Embedded {len(points)} chunks for {collection_name}")
