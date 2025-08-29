from fastapi import FastAPI
from app.companies.routes import company_router
from contextlib import asynccontextmanager
from app.db.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code here
    print('Server started...')
    await init_db()
    yield
    # Shutdown code here
    print('Server has been stopped...')

version="v1"

app = FastAPI(
    title="Kaleem Backend",
    description="Backend API for Kaleem Application",
    version=version,
    lifespan=lifespan
)

app.include_router(company_router, prefix=f"/api/{version}/companies", tags=["companies"])