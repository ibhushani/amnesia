"""
API Configuration Settings
"""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Amnesia VMUaaS"
    API_V1_STR: str = "/api/v1"
    DEBUG_MODE: bool = True
    
    # Storage Paths
    STORAGE_ROOT: str = "./storage"
    MODEL_STORAGE: str = "./storage/models"
    DATA_STORAGE: str = "./storage/data"
    CERT_STORAGE: str = "./storage/certificates"
    
    # Redis / Celery
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./amnesia.db")

    class Config:
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()