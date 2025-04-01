from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    APP_NAME: str = "10 Academy Trainee API"
    API_V1_STR: str = "/api/v1"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    
    # Default values
    DEFAULT_RUN_STAGE: str = "prod"
    DEFAULT_ROLE: str = "trainee"
    DEFAULT_BATCH_SIZE: int = 20
    
    # File processing
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: list[str] = ["text/csv"]
    DEFAULT_ENCODING: str = "utf-8"
    DEFAULT_DELIMITER: str = ","
    
    # Required columns for batch processing
    REQUIRED_COLUMNS: list[str] = [
        "name",
        "email",
        "nationality",
        "gender",
        "date_of_birth"
    ]
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings() 