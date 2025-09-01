# # app/db/database.py
# from sqlmodel import SQLModel
# from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker
# from app.core.config import Config

# DATABASE_URL = Config.DATABASE_URL

# # Supabase PgBouncer requires disabling statement caching
# engine: AsyncEngine = create_async_engine(
#     url=DATABASE_URL,
#     echo=True,
#     pool_pre_ping=True,
# )


# async def init_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(SQLModel.metadata.create_all)
# backend/app/db/database.py



# backend/app/db/database.py
# import ssl
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker, declarative_base
# from app.core.config import Config

# ssl_context = ssl.create_default_context()
# ssl_context.check_hostname = False
# ssl_context.verify_mode = ssl.CERT_NONE

# engine = create_async_engine(
#     Config.DATABASE_URL,
#     pool_pre_ping=True,
#     connect_args={
#         "ssl": ssl_context,
#         "statement_cache_size": 0  # disables asyncpg prepared statement cache
#     },
#     execution_options={
#         "compiled_cache": None  # disables SQLAlchemy compiled cache
#     }
# )

# AsyncSessionLocal = sessionmaker(
#     bind=engine,
#     class_=AsyncSession,
#     expire_on_commit=False,
# )

# Base = declarative_base()

# async def get_db() -> AsyncSession:
#     async with AsyncSessionLocal() as session:
#         yield session

# async def init_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)


from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from app.core.config import Config
from sqlalchemy.pool import NullPool
from uuid import uuid4

# Async-compatible URL
DATABASE_URL = Config.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

print("✅ DATABASE_URL (sanitized):", DATABASE_URL)  # Just to verify at runtime

# Optionally: Add query param if connect_args isn't respected
# DATABASE_URL += "?statement_cache_size=0"

from uuid import uuid4

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4()}__",
    },
    poolclass=NullPool,
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with async_session() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)