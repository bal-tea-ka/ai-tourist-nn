"""
Конфигурация приложения
"""
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Основные настройки
    PROJECT_NAME: str = "AI Tourist Assistant"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # База данных
    DATABASE_URL: str
    
    # API ключи
    AI_API_KEY: str = ""
    YANDEX_MAPS_API_KEY: str = ""
    YANDEX_GEOCODER_API_KEY: str = ""
    YANDEX_SUGGEST_API_URL: str = ""
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # Настройки маршрутов
    MAX_SEARCH_RADIUS_KM: int = 20
    WALKING_SPEED_KMH: float = 4.5
    MIN_PLACES_IN_ROUTE: int = 1
    MAX_PLACES_IN_ROUTE: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def get_cors_origins(self) -> List[str]:
        """Получить список CORS origins"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

settings = Settings()
