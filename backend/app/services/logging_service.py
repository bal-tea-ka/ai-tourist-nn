"""
Logging Service - Сервис для логирования запросов
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_request import UserRequest
from app.schemas.route import RouteRequest, RouteResponse
from typing import Optional


async def log_route_request(
    db: AsyncSession,
    request_data: RouteRequest,
    response_data: dict,
    request_id: str,
    execution_time_ms: int,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> UserRequest:
    """
    Сохранить запрос пользователя в БД
    
    Args:
        db: Сессия базы данных
        request_data: Данные запроса
        response_data: Данные ответа
        request_id: Уникальный ID запроса
        execution_time_ms: Время выполнения в миллисекундах
        ip_address: IP адрес пользователя
        user_agent: User Agent браузера
        
    Returns:
        UserRequest: Сохраненный объект запроса
    """
    user_request = UserRequest(
        user_interests=request_data.user_interests,
        available_time_hours=request_data.available_time_hours,
        user_address=request_data.user_location.address,
        user_latitude=request_data.user_location.latitude,
        user_longitude=request_data.user_location.longitude,
        total_places=response_data.get('route', {}).get('total_places', 0),
        total_distance_km=response_data.get('route', {}).get('total_distance_km', 0.0),
        total_time_minutes=response_data.get('route', {}).get('total_time_minutes', 0),
        selected_categories=response_data.get('metadata', {}).get('selected_categories', []),
        request_id=request_id,
        execution_time_ms=execution_time_ms,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    db.add(user_request)
    await db.commit()
    await db.refresh(user_request)
    
    return user_request
