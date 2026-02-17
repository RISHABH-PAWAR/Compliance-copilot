"""AI Compliance Copilot - Configuration Management"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI Compliance Copilot"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    API_V1_PREFIX: str = "/api/v1"

    # MySQL Database
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "compliance_copilot"

    @property
    def MYSQL_DATABASE_URL(self) -> str:
        import os
        if self.APP_ENV == "development":
            # Ensure absolute path in the backend directory
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "compliance_copilot.db")
            return f"sqlite:///{db_path}"
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "compliance_copilot_docs"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Pinecone
    PINECONE_INDEX_NAME: str = "compliance-copilot"

    # AI Configuration
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: Optional[str] = None
    PINECONE_API_KEY: str = ""
    PINECONE_ENV: str = "us-east-1"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    DEFAULT_LLM_MODEL: str = "llama3-70b-8192"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # JWT
    JWT_SECRET_KEY: str = "jwt-dev-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_NAME: str = "AI Compliance Copilot"

    # Encryption
    ENCRYPTION_KEY: str = "dev-encryption-key-32-bytes-long!"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 50
    UPLOAD_DIR: str = "./uploads"

    # System settings from .env
    API_V1_STR: str = "/api/v1"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ALGORITHM: str = "HS256"
    MAX_UPLOAD_SIZE: int = 52428800
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "docx", "txt"]
    EMAILS_FROM_EMAIL: str = "no-reply@compliance-copilot.com"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
