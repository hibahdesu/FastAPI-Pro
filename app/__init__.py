# app/__init__.py
from fastapi import FastAPI
from app.companies.routes import company_router
from contextlib import asynccontextmanager
from app.db.database import init_db, engine
from app.auth.routes import auth_router
from app.data.routes import router as data_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code here
    print('Server started...')
    from app.companies.models import Company
    await init_db()
    yield
    # Shutdown code here
    print('Server has been stopped...')
    # await engine.dispose()  # ✅ Clean up async connections


version="v1"

app = FastAPI(
    title="Kaleem Backend",
    description="Backend API for Kaleem Application",
    version=version,
    # lifespan=lifespan
)


app.include_router(company_router, prefix=f"/api/{version}/companies", tags=["companies"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])
app.include_router(data_router, prefix=f"/api/{version}/data", tags=["data"])