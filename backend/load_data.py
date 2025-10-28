"""
Скрипт для загрузки данных из Excel в PostgreSQL
"""
import asyncio
import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session, engine
from app.models.category import Category
from app.models.place import Place
import re

# Маппинг category_id из датасета на наши категории
CATEGORY_MAPPING = {
    1: 1,   # Памятники и скульптуры
    2: 2,   # Парки и скверы
    3: 3,   # Тактильные макеты
    4: 4,   # Набережные
    5: 5,   # Архитектура и достопримечательности
    6: 6,   # Культурные центры и досуг
    7: 7,   # Музеи
    8: 8,   # Театры и филармонии
    10: 9,  # Стрит-арт и мозаики (category_id 10 в датасете → 9 в нашей БД)
}


def extract_coordinates(coordinate_str):
    """
    Извлечь широту и долготу из строки POINT (longitude latitude)
    """
    if not coordinate_str or pd.isna(coordinate_str):
        return None, None
    
    match = re.search(r'POINT \(([\d.]+) ([\d.]+)\)', coordinate_str)
    if match:
        longitude = float(match.group(1))
        latitude = float(match.group(2))
        return latitude, longitude
    return None, None


async def load_categories():
    """Загрузить категории в БД"""
    categories_data = [
        {"id": 1, "name": "Памятники и скульптуры", "description": "Памятники историческим личностям и скульптуры", "avg_visit_duration": 15},
        {"id": 2, "name": "Парки и скверы", "description": "Парки, скверы, сады для прогулок и отдыха", "avg_visit_duration": 45},
        {"id": 3, "name": "Тактильные макеты", "description": "Тактильные макеты достопримечательностей для людей с ОВЗ", "avg_visit_duration": 10},
        {"id": 4, "name": "Набережные", "description": "Набережные рек Волги и Оки", "avg_visit_duration": 30},
        {"id": 5, "name": "Архитектура и достопримечательности", "description": "Исторические здания, архитектурные памятники", "avg_visit_duration": 20},
        {"id": 6, "name": "Культурные центры и досуг", "description": "Дворцы культуры, планетарии, кинотеатры", "avg_visit_duration": 60},
        {"id": 7, "name": "Музеи", "description": "Музеи, галереи, выставочные центры", "avg_visit_duration": 60},
        {"id": 8, "name": "Театры и филармонии", "description": "Театры, филармонии, концертные залы", "avg_visit_duration": 120},
        {"id": 9, "name": "Стрит-арт и мозаики", "description": "Уличное искусство, граффити, советские мозаики", "avg_visit_duration": 10},
    ]
    
    async with async_session() as session:
        for cat_data in categories_data:
            # Проверяем, существует ли категория
            result = await session.execute(
                select(Category).where(Category.id == cat_data["id"])
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                category = Category(**cat_data)
                session.add(category)
        
        await session.commit()
        print(f"✅ Загружено {len(categories_data)} категорий")


async def load_places():
    """Загрузить места из Excel файла"""
    # Чтение Excel файла
    df = pd.read_excel('cultural_objects_mnn.xlsx')
    
    print(f"📊 Загружено {len(df)} записей из файла")
    
    loaded_count = 0
    skipped_count = 0
    
    async with async_session() as session:
        for _, row in df.iterrows():
            try:
                # Извлекаем координаты
                latitude, longitude = extract_coordinates(row.get('coordinate'))
                
                if not latitude or not longitude:
                    skipped_count += 1
                    continue
                
                # Маппим category_id
                original_cat_id = row.get('category_id')
                category_id = CATEGORY_MAPPING.get(original_cat_id)
                
                if not category_id:
                    skipped_count += 1
                    continue
                
                # Проверяем, существует ли место
                result = await session.execute(
                    select(Place).where(Place.id == int(row['id']))
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    skipped_count += 1
                    continue
                
                # Обработка значений (заменяем nan на None или пустую строку)
                title = str(row.get('title', ''))
                address = str(row.get('address', '')) if pd.notna(row.get('address')) else ''
                description = str(row.get('description', ''))[:1000] if pd.notna(row.get('description')) else ''
                url = str(row.get('url', '')) if pd.notna(row.get('url')) else None
                
                # Создаём место
                place = Place(
                    id=int(row['id']),
                    title=title,
                    address=address,
                    latitude=float(latitude),
                    longitude=float(longitude),
                    description=description,
                    description_clean=clean_html(description),
                    category_id=int(category_id),
                    url=url
                )
                
                session.add(place)
                loaded_count += 1
                
                # Коммитим каждые 50 записей
                if loaded_count % 50 == 0:
                    await session.commit()
                    print(f"  💾 Сохранено {loaded_count} мест...")
                
            except Exception as e:
                print(f"❌ Ошибка при обработке записи {row.get('id')}: {e}")
                skipped_count += 1
                continue
        
        # Финальный коммит
        await session.commit()
    
    print(f"✅ Загружено мест: {loaded_count}")
    print(f"⚠️  Пропущено: {skipped_count}")


def clean_html(text):
    """Удалить HTML теги из текста"""
    if not text:
        return ""
    # Удаляем HTML теги
    clean = re.sub(r'<[^>]+>', '', str(text))
    # Убираем лишние пробелы
    clean = ' '.join(clean.split())
    return clean[:1000]  # ограничиваем длину

async def main():
    """Главная функция"""
    print("🚀 Начало загрузки данных...")
    
    # Загружаем категории
    await load_categories()
    
    # Загружаем места
    await load_places()
    
    print("✅ Загрузка завершена!")


if __name__ == "__main__":
    asyncio.run(main())
