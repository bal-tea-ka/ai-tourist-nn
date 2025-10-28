"""
Routes API endpoint
Генерация персональных маршрутов с данными из БД
"""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.route import RouteRequest, RouteResponse
from app.database import get_db
from app.models.place import Place
from app.models.category import Category
import time
import random
import string
import math
from decimal import Decimal

router = APIRouter()


def generate_request_id() -> str:
    """Генерация уникального ID запроса"""
    return 'req_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))


def calculate_distance(lat1: float, lon1: float, lat2, lon2) -> float:
    """
    Рассчитать расстояние между двумя точками (формула Haversine)
    Возвращает расстояние в километрах
    """
    # Приводим Decimal к float
    lat1 = float(lat1)
    lon1 = float(lon1)
    lat2 = float(lat2)
    lon2 = float(lon2)
    
    R = 6371  # Радиус Земли в км
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


@router.post("/route/generate", response_model=RouteResponse)
async def generate_route(request: RouteRequest, db: AsyncSession = Depends(get_db)):
    """
    Генерация персонального туристического маршрута из реальных данных БД
    """
    start_time = time.time()
    
    try:
        # Получаем все активные места
        result = await db.execute(
            select(Place).where(Place.is_active == True)
        )
        all_places = list(result.scalars().all())
        
        if not all_places:
            # Если в БД нет мест, возвращаем пустой маршрут
            return {
                "route": {
                    "places": [],
                    "route_order": [],
                    "total_places": 0,
                    "total_time_minutes": 0,
                    "total_distance_km": 0.0,
                    "walking_time_minutes": 0,
                    "visit_time_minutes": 0,
                    "map_data": {
                        "center": [request.user_location.latitude, request.user_location.longitude],
                        "zoom": 13
                    }
                },
                "metadata": {
                    "selected_categories": [],
                    "filtered_places_count": 0,
                    "request_id": generate_request_id(),
                    "execution_time_ms": 0
                }
            }
        
        # Получаем все категории
        categories_result = await db.execute(select(Category))
        categories_dict = {cat.id: cat for cat in categories_result.scalars().all()}
        
        # Рассчитываем расстояния и фильтруем близкие места
        nearby_places = []
        for place in all_places:
            distance = calculate_distance(
                request.user_location.latitude,
                request.user_location.longitude,
                place.latitude,  # это Decimal из БД
                place.longitude   # это Decimal из БД
            )
            if distance <= 15:  # В радиусе 15 км
                nearby_places.append((place, distance))
        
        # Сортируем по расстоянию
        nearby_places.sort(key=lambda x: x[1])
        
        # Если не нашли места поблизости, берём ближайшие 10
        if not nearby_places:
            nearby_places = []
            for place in all_places[:10]:
                distance = calculate_distance(
                    request.user_location.latitude,
                    request.user_location.longitude,
                    place.latitude,
                    place.longitude
                )
                nearby_places.append((place, distance))
            nearby_places.sort(key=lambda x: x[1])
        
        # Выбираем места на основе доступного времени
        available_minutes = request.available_time_hours * 60
        selected_places = []
        total_visit_time = 0
        used_categories = set()
        
        # Выбираем разнообразные места
        for place, distance in nearby_places:
            category = categories_dict.get(place.category_id)
            if not category:
                continue
                
            # Пытаемся выбрать из разных категорий
            if place.category_id not in used_categories:
                if total_visit_time + category.avg_visit_duration <= available_minutes - 30:
                    selected_places.append((place, distance, category))
                    total_visit_time += category.avg_visit_duration
                    used_categories.add(place.category_id)
                    
                    if len(selected_places) >= 5:
                        break
        
        # Если выбрали мало мест, добавляем ещё
        if len(selected_places) < 3:
            for place, distance in nearby_places:
                if any(p.id == place.id for p, _, _ in selected_places):
                    continue
                    
                category = categories_dict.get(place.category_id)
                if not category:
                    continue
                    
                if total_visit_time + category.avg_visit_duration <= available_minutes - 30:
                    selected_places.append((place, distance, category))
                    total_visit_time += category.avg_visit_duration
                    
                    if len(selected_places) >= 5:
                        break
        
        # Формируем ответ
        places_data = []
        for place, distance, category in selected_places:
            # Безопасно получаем description_clean
            description = place.description_clean if place.description_clean else place.description
            if description and len(description) > 300:
                description = description[:300] + "..."
            elif not description:
                description = "Описание отсутствует"
            
            places_data.append({
                "id": place.id,
                "title": place.title,
                "address": place.address or "",
                "coordinates": {
                    "latitude": float(place.latitude),  # Decimal → float
                    "longitude": float(place.longitude)  # Decimal → float
                },
                "category": {
                    "id": category.id,
                    "name": category.name
                },
                "description": description,
                "visit_duration": category.avg_visit_duration,
                "distance_from_user": round(distance, 2),
                "reasoning": f"Место находится в {round(distance, 1)} км от вас и соответствует вашим интересам."
            })
        
        # Расчёты
        total_places = len(places_data)
        total_distance = sum(p["distance_from_user"] for p in places_data)
        walking_time = int(total_distance / 4.5 * 60) if total_distance > 0 else 0  # 4.5 км/ч
        total_time = total_visit_time + walking_time
        route_order = [p["id"] for p in places_data]
        
        # Время выполнения
        execution_time = int((time.time() - start_time) * 1000)
        
        return {
            "route": {
                "places": places_data,
                "route_order": route_order,
                "total_places": total_places,
                "total_time_minutes": total_time,
                "total_distance_km": round(total_distance, 2),
                "walking_time_minutes": walking_time,
                "visit_time_minutes": total_visit_time,
                "map_data": {
                    "center": [request.user_location.latitude, request.user_location.longitude],
                    "zoom": 13
                }
            },
            "metadata": {
                "selected_categories": list(used_categories),
                "filtered_places_count": len(nearby_places),
                "request_id": generate_request_id(),
                "execution_time_ms": execution_time
            }
        }
        
    except Exception as e:
        print(f"❌ Ошибка генерации маршрута: {e}")
        import traceback
        traceback.print_exc()
        raise
