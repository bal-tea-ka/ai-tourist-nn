"""
Проверка загруженных данных
"""
import asyncio
from sqlalchemy import select, func
from app.database import async_session
from app.models.category import Category
from app.models.place import Place


async def check_data():
    async with async_session() as session:
        # Количество категорий
        result = await session.execute(select(func.count()).select_from(Category))
        categories_count = result.scalar()
        
        # Количество мест
        result = await session.execute(select(func.count()).select_from(Place))
        places_count = result.scalar()
        
        # Количество мест по категориям
        result = await session.execute(
            select(Category.name, func.count(Place.id))
            .join(Place)
            .group_by(Category.name)
        )
        
        print(f"\n✅ Категорий в БД: {categories_count}")
        print(f"✅ Мест в БД: {places_count}\n")
        print("📊 Распределение по категориям:")
        
        for name, count in result:
            print(f"  - {name}: {count} мест")


asyncio.run(check_data())
