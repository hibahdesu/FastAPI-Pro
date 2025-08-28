# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # PostgreSQL connection
    DATABASE_URL: str

    # Supabase REST access
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_JWT_SECRET: str

    ASTRA_DB_API_ENDPOINT: str
    ASTRA_DB_APPLICATION_TOKEN: str
    ASTRA_DB_KEYSPACE: str

    # JWT auth for your FastAPI app
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    # Moyasar API Key
    MOYASAR_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

Config = Settings()
