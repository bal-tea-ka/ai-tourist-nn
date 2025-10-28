from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.models.category import Category
from app.models.place import Place

router = APIRouter()


@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    """
    Получить список всех категорий мест из базы данных
    
    Returns:
        dict: Список категорий с количеством мест
    """
    # Получаем категории с подсчётом мест
    query = (
        select(
            Category,
            func.count(Place.id).label('places_count')
        )
        .outerjoin(Place)
        .group_by(Category.id)
        .order_by(Category.id)
    )
    
    result = await db.execute(query)
    categories_data = []
    
    for category, places_count in result:
        categories_data.append({
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "avg_visit_duration": category.avg_visit_duration,
            "icon": "default",  # можно добавить иконки позже
            "places_count": places_count
        })
    
    return {
        "categories": categories_data,
        "total": len(categories_data)
    }


@router.get("/categories/{category_id}")
async def get_category_by_id(category_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получить информацию о конкретной категории
    
    Args:
        category_id: ID категории
        
    Returns:
        dict: Информация о категории
    """
    # Получаем категорию
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    category = result.scalar_one_or_none()
    
    if not category:
        return {
            "error": "Category not found",
            "category_id": category_id
        }
    
    # Считаем количество мест
    count_result = await db.execute(
        select(func.count()).select_from(Place).where(Place.category_id == category_id)
    )
    places_count = count_result.scalar()
    
    return {
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "avg_visit_duration": category.avg_visit_duration,
        "icon": "default",
        "places_count": places_count
    }
