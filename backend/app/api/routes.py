"""
Routes API endpoint
Генерация персональных маршрутов с логированием
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.route import RouteRequest, RouteResponse
from app.database import get_db
from app.models.place import Place
from app.models.category import Category
from app.services.logging_service import log_route_request
import time
import random
import string
import math

router = APIRouter()


def generate_request_id() -> str:
    """Генерация уникального ID запроса"""
    return 'req_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))


def calculate_distance(lat1: float, lon1: float, lat2, lon2) -> float:
    """Рассчитать расстояние между двумя точками (формула Haversine)"""
    lat1 = float(lat1)
    lon1 = float(lon1)
    lat2 = float(lat2)
    lon2 = float(lon2)
    
    R = 6371
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


@router.post("/route/generate", response_model=RouteResponse)
async def generate_route(
    route_request: RouteRequest, 
    request: Request,  # ← Добавили для получения IP и User-Agent
    db: AsyncSession = Depends(get_db)
):
    """
    Генерация персонального туристического маршрута с логированием
    """
    start_time = time.time()
    request_id = generate_request_id()
    
    try:
        # Получаем все активные места
        result = await db.execute(
            select(Place).where(Place.is_active == True)
        )
        all_places = list(result.scalars().all())
        
        if not all_places:
            response_data = {
                "route": {
                    "places": [],
                    "route_order": [],
                    "total_places": 0,
                    "total_time_minutes": 0,
                    "total_distance_km": 0.0,
                    "walking_time_minutes": 0,
                    "visit_time_minutes": 0,
                    "map_data": {
                        "center": [route_request.user_location.latitude, route_request.user_location.longitude],
                        "zoom": 13
                    }
                },
                "metadata": {
                    "selected_categories": [],
                    "filtered_places_count": 0,
                    "request_id": request_id,
                    "execution_time_ms": 0
                }
            }
            return response_data
        
        # Получаем все категории
        categories_result = await db.execute(select(Category))
        categories_dict = {cat.id: cat for cat in categories_result.scalars().all()}
        
        # Рассчитываем расстояния и фильтруем близкие места
        nearby_places = []
        for place in all_places:
            distance = calculate_distance(
                route_request.user_location.latitude,
                route_request.user_location.longitude,
                place.latitude,
                place.longitude
            )
            if distance <= 15:
                nearby_places.append((place, distance))
        
        nearby_places.sort(key=lambda x: x[1])
        
        if not nearby_places:
            nearby_places = []
            for place in all_places[:10]:
                distance = calculate_distance(
                    route_request.user_location.latitude,
                    route_request.user_location.longitude,
                    place.latitude,
                    place.longitude
                )
                nearby_places.append((place, distance))
            nearby_places.sort(key=lambda x: x[1])
        
        # Выбираем места
        available_minutes = route_request.available_time_hours * 60
        selected_places = []
        total_visit_time = 0
        used_categories = set()
        
        for place, distance in nearby_places:
            category = categories_dict.get(place.category_id)
            if not category:
                continue
                
            if place.category_id not in used_categories:
                if total_visit_time + category.avg_visit_duration <= available_minutes - 30:
                    selected_places.append((place, distance, category))
                    total_visit_time += category.avg_visit_duration
                    used_categories.add(place.category_id)
                    
                    if len(selected_places) >= 5:
                        break
        
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
                    "latitude": float(place.latitude),
                    "longitude": float(place.longitude)
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
        walking_time = int(total_distance / 4.5 * 60) if total_distance > 0 else 0
        total_time = total_visit_time + walking_time
        route_order = [p["id"] for p in places_data]
        
        execution_time = int((time.time() - start_time) * 1000)
        
        response_data = {
            "route": {
                "places": places_data,
                "route_order": route_order,
                "total_places": total_places,
                "total_time_minutes": total_time,
                "total_distance_km": round(total_distance, 2),
                "walking_time_minutes": walking_time,
                "visit_time_minutes": total_visit_time,
                "map_data": {
                    "center": [route_request.user_location.latitude, route_request.user_location.longitude],
                    "zoom": 13
                }
            },
            "metadata": {
                "selected_categories": list(used_categories),
                "filtered_places_count": len(nearby_places),
                "request_id": request_id,
                "execution_time_ms": execution_time
            }
        }
        
        # Логируем запрос в БД
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", None)
        
        await log_route_request(
            db=db,
            request_data=route_request,
            response_data=response_data,
            request_id=request_id,
            execution_time_ms=execution_time,
            ip_address=client_ip,
            user_agent=user_agent
        )
        
        return response_data
        
    except Exception as e:
        print(f"❌ Ошибка генерации маршрута: {e}")
        import traceback
        traceback.print_exc()
        raise
