"""
User Request Model - Логирование запросов пользователей
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class UserRequest(Base):
    """Модель для хранения запросов пользователей"""
    
    __tablename__ = "user_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Данные запроса
    user_interests = Column(String, nullable=False)
    available_time_hours = Column(Integer, nullable=False)
    user_address = Column(String, nullable=False)
    user_latitude = Column(Float, nullable=False)
    user_longitude = Column(Float, nullable=False)
    
    # Результаты
    total_places = Column(Integer, nullable=True)
    total_distance_km = Column(Float, nullable=True)
    total_time_minutes = Column(Integer, nullable=True)
    selected_categories = Column(JSON, nullable=True)  # Список ID категорий
    route_data = Column(JSON, nullable=True)  # Полный маршрут (опционально)
    
    # Метаданные
    request_id = Column(String, unique=True, index=True, nullable=False)
    execution_time_ms = Column(Integer, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<UserRequest {self.request_id}: {self.user_interests}>"
