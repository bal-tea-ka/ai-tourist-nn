"""
Routes API endpoint
Генерация персональных маршрутов
"""
from fastapi import APIRouter
from app.schemas.route import RouteRequest, RouteResponse
import time
import random
import string

router = APIRouter()


def generate_request_id() -> str:
    """Генерация уникального ID запроса"""
    return 'req_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))


@router.post("/route/generate", response_model=RouteResponse)
async def generate_route(request: RouteRequest):
    """
    Генерация персонального туристического маршрута
    
    Args:
        request: Данные запроса (интересы, время, местоположение)
        
    Returns:
        RouteResponse: Сгенерированный маршрут с местами
    """
    start_time = time.time()
    
    # Временные моковые данные (пока нет БД и Perplexity API)
    mock_places = [
        {
            "id": 57,
            "title": "Памятник Петру I",
            "address": "Нижний Новгород, Нижне-Волжская набережная",
            "coordinates": {
                "latitude": 56.331576,
                "longitude": 44.003277
            },
            "category": {
                "id": 1,
                "name": "Памятники и скульптуры"
            },
            "description": "Памятник Петру I открыт 24 сентября 2014 года. Он установлен напротив Зачатьевской башни Нижегородского кремля.",
            "visit_duration": 15,
            "distance_from_user": 0.8,
            "reasoning": "Выбран благодаря вашему интересу к истории. Памятник расположен в историческом центре."
        },
        {
            "id": 122,
            "title": "Нижегородский Кремль",
            "address": "Нижний Новгород, Кремль",
            "coordinates": {
                "latitude": 56.328,
                "longitude": 44.002
            },
            "category": {
                "id": 5,
                "name": "Архитектура и достопримечательности"
            },
            "description": "Кремль - главная достопримечательность Нижнего Новгорода, построен в XVI веке.",
            "visit_duration": 60,
            "distance_from_user": 1.0,
            "reasoning": "Главная историческая достопримечательность города, соответствует вашим интересам."
        },
        {
            "id": 51,
            "title": "Большая Покровская улица",
            "address": "Нижний Новгород, Большая Покровская улица",
            "coordinates": {
                "latitude": 56.324,
                "longitude": 44.001
            },
            "category": {
                "id": 5,
                "name": "Архитектура и достопримечательности"
            },
            "description": "Главная пешеходная улица города с историческими зданиями и современными арт-объектами.",
            "visit_duration": 45,
            "distance_from_user": 1.5,
            "reasoning": "Пешеходная улица с архитектурой и стрит-артом, идеально подходит под ваши интересы."
        }
    ]
    
    # Выбираем места на основе доступного времени
    available_minutes = request.available_time_hours * 60
    selected_places = []
    total_visit_time = 0
    
    for place in mock_places:
        if total_visit_time + place["visit_duration"] <= available_minutes - 30:  # оставляем время на дорогу
            selected_places.append(place)
            total_visit_time += place["visit_duration"]
    
    # Расчёт общего времени и расстояния
    total_places = len(selected_places)
    walking_time = int(total_places * 15)  # примерно 15 минут между местами
    total_time = total_visit_time + walking_time
    total_distance = sum(place["distance_from_user"] for place in selected_places)
    
    # Порядок посещения (по расстоянию от пользователя)
    route_order = [place["id"] for place in selected_places]
    
    # Время выполнения
    execution_time = int((time.time() - start_time) * 1000)
    
    return {
        "route": {
            "places": selected_places,
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
            "selected_categories": [1, 5],  # Моковые категории
            "filtered_places_count": len(mock_places),
            "request_id": generate_request_id(),
            "execution_time_ms": execution_time
        }
    }
