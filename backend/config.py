from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Learning Platform"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./learning_platform.db"

    # JWT
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Groq API
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama3-70b-8192"

    # n8n
    N8N_WEBHOOK_URL: str = "http://localhost:5678/webhook"

    class Config:
        env_file = "../.env"
        case_sensitive = True

settings = Settings()
