"""
Stats API endpoint
Статистика использования сервиса
"""
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user_request import UserRequest
from app.models.category import Category
from typing import Dict, List
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """
    Получить общую статистику использования сервиса
    
    Returns:
        dict: Статистика запросов, популярных категорий, средних значений
    """
    # Общее количество запросов
    total_requests_result = await db.execute(
        select(func.count()).select_from(UserRequest)
    )
    total_requests = total_requests_result.scalar()
    
    # Запросы за последние 24 часа
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_requests_result = await db.execute(
        select(func.count()).select_from(UserRequest)
        .where(UserRequest.created_at >= yesterday)
    )
    recent_requests = recent_requests_result.scalar()
    
    # Средние значения
    avg_result = await db.execute(
        select(
            func.avg(UserRequest.total_places).label('avg_places'),
            func.avg(UserRequest.total_distance_km).label('avg_distance'),
            func.avg(UserRequest.total_time_minutes).label('avg_time'),
            func.avg(UserRequest.execution_time_ms).label('avg_execution')
        )
    )
    avg_data = avg_result.first()
    
    # Популярные запросы (топ интересов)
    interests_result = await db.execute(
        select(UserRequest.user_interests, func.count().label('count'))
        .group_by(UserRequest.user_interests)
        .order_by(func.count().desc())
        .limit(10)
    )
    popular_interests = [
        {"interests": row[0], "count": row[1]} 
        for row in interests_result
    ]
    
    # Популярные локации
    locations_result = await db.execute(
        select(UserRequest.user_address, func.count().label('count'))
        .group_by(UserRequest.user_address)
        .order_by(func.count().desc())
        .limit(10)
    )
    popular_locations = [
        {"address": row[0], "count": row[1]} 
        for row in locations_result
    ]
    
    return {
        "total_requests": total_requests or 0,
        "recent_requests_24h": recent_requests or 0,
        "averages": {
            "places_per_route": round(avg_data[0], 1) if avg_data[0] else 0,
            "distance_km": round(avg_data[1], 2) if avg_data[1] else 0,
            "time_minutes": round(avg_data[2], 1) if avg_data[2] else 0,
            "execution_time_ms": round(avg_data[3], 1) if avg_data[3] else 0
        },
        "popular_interests": popular_interests,
        "popular_locations": popular_locations
    }


@router.get("/stats/categories")
async def get_category_stats(db: AsyncSession = Depends(get_db)):
    """
    Статистика по популярности категорий
    
    Returns:
        dict: Список категорий с количеством использований
    """
    # Получаем все категории
    categories_result = await db.execute(select(Category))
    categories = {cat.id: cat.name for cat in categories_result.scalars().all()}
    
    # Подсчитываем использование каждой категории
    category_stats = []
    
    for cat_id, cat_name in categories.items():
        # Считаем сколько раз категория встречалась в маршрутах
        count_result = await db.execute(
            select(func.count())
            .select_from(UserRequest)
            .where(UserRequest.selected_categories.contains([cat_id]))
        )
        count = count_result.scalar()
        
        category_stats.append({
            "category_id": cat_id,
            "category_name": cat_name,
            "usage_count": count or 0
        })
    
    # Сортируем по популярности
    category_stats.sort(key=lambda x: x['usage_count'], reverse=True)
    
    return {
        "categories": category_stats,
        "total_categories": len(category_stats)
    }
