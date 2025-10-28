from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Основные настройки
    PROJECT_NAME: str = "AI Tourist Assistant"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # База данных
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/tourist_db"
    
    # API ключи
    PERPLEXITY_API_KEY: str = ""
    YANDEX_GEOCODER_API_KEY: str = ""
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Настройки маршрутов
    MAX_SEARCH_RADIUS_KM: int = 20
    WALKING_SPEED_KMH: float = 4.5
    MIN_PLACES_IN_ROUTE: int = 1
    MAX_PLACES_IN_ROUTE: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
