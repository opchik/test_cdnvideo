import os
from typing import Optional

class Settings:
    """Настройки приложения"""
    APP_NAME: str = "City API"
    VERSION: str = "1.0.0"
    
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    RELOAD: bool = os.getenv("RELOAD", "false").lower() == "true"
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    GEOCODING_BASE_URL: str = os.getenv("GEOCODING_BASE_URL", "")
    GEOCODING_USER_AGENT: str = os.getenv("GEOCODING_USER_AGENT", "")
    
    CORS_ORIGINS: list = ["*"]

settings = Settings()