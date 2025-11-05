import json
import re
import httpx
from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.category import Category  


def parse_categories_response(response_text: str) -> List[int]:
    """
    Парсит ответ нейросети, пытаясь найти JSON-массив с id категорий,
    например: [1, 3, 5].
    Возвращает список целых чисел.
    """
    # Ищем JSON массив в тексте с помощью регулярного выражения
    json_array_str = None
    match = re.search(r'\[\s*(\d+\s*,?\s*)+\]', response_text)
    if match:
        json_array_str = match.group(0)
    else:
        # Если JSON не найден, пытаемся взять весь текст как JSON
        json_array_str = response_text.strip()

    try:
        categories = json.loads(json_array_str)
        if isinstance(categories, list) and all(isinstance(i, int) for i in categories):
            return categories
        else:
            raise ValueError("Ответ не содержит список целых чисел")
    except json.JSONDecodeError as e:
        raise ValueError(f"Не удалось распарсить JSON: {str(e)}")

# Пример использования:
# response_text = "Согласно вашему запросу выбраны категории:\n[1, 3, 5]"
# selected_categories = parse_categories_response(response_text)
# print(selected_categories)  # [1, 3, 5]



async def get_categories_from_db(session: AsyncSession):
    result = await session.execute(select(Category))
    categories = result.scalars().all()
    category_names = {category.id: category.name for category in categories}
    category_times = {category.id: category.avg_visit_duration for category in categories}
    return category_names, category_times

# Построение карты категорий для быстрого поиска по названию
async def load_category_map(session: AsyncSession) -> Dict[str, Dict]:
    category_names, _ = await get_categories_from_db(session)
    category_map = {}
    for id_, name in category_names.items():
        category_map[name.lower()] = {"id": id_, "name": name}
    return category_map

def extract_category(title: str, category_map: Dict[str, Dict]) -> Dict:
    title_lower = title.lower()
    for cat_name, cat_obj in category_map.items():
        if cat_name in title_lower:
            return cat_obj
    return {"id": 0, "name": "Другое"}

def time_to_minutes(time1, time2):
    h1, m1 = map(int, time1.split(":"))
    h2, m2 = map(int, time2.split(":"))
    diff = (h2 - h1) * 60 + (m2 - m1)
    return diff if diff > 0 else 30  # по умолчанию 30, если время указано некорректно

import json
from typing import Dict
from difflib import get_close_matches


def match_place_with_db(place_title: str, category_map: Dict[str, Dict]) -> Dict:
    """
    По названию места пытаемся найти соответствующую категорию и id из базы.
    Здесь пример сопоставления по названию категории.
    Можно расширить по другим полям.
    """
    place_title_lower = place_title.lower()
    # Находим максимальное совпадение категории
    for cat_name, cat_obj in category_map.items():
        if cat_name in place_title_lower:
            return cat_obj
    # Если совпадений нет - вернем дефолт
    return {"id": 0, "name": "Другое"}

'''def clean_ai_response(response_text: str) -> str:
    start = response_text.find('[')
    end = response_text.rfind(']')
    if start == -1 or end == -1 or end < start:
        raise ValueError("В ответе нет валидного JSON массива")
    json_part = response_text[start:end + 1]
    return json_part.strip()'''

def clean_ai_response(response_text: str) -> str:
    """Извлекает JSON из ответа AI, игнорируя текст до/после"""
    import re

    # Убрать лишние пробелы и переносы
    response_text = response_text.strip()

    # Попытка 1: Найти JSON массив [...]
    start = response_text.find('[')
    end = response_text.rfind(']')

    if start != -1 and end != -1 and end >= start:
        json_part = response_text[start:end + 1]
        try:
            # Проверка что это валидный JSON
            import json
            json.loads(json_part)
            return json_part.strip()
        except:
            pass
    
    # Попытка 2: Найти JSON объект {...}
    start = response_text.find('{')
    end = response_text.rfind('}')
    
    if start != -1 and end != -1 and end >= start:
        json_part = response_text[start:end + 1]
        try:
            import json
            json.loads(json_part)
            return json_part.strip()
        except:
            pass
    
    # Если ничего не найдено - ошибка
    raise ValueError(f"В ответе нет валидного JSON. Ответ: {response_text[:100]}")




def parse_route_response(response_text: str, category_map: Dict[str, Dict], db_places: Dict[str, int]) -> dict:
    """
    Разбирает JSON от нейросети с массивом мест без id,
    подставляет id из базы по названию и строит финальную структуру.
    
    db_places: словарь название места -> id из базы
    """

    try:
        places_from_ai = json.loads(response_text)
        if not isinstance(places_from_ai, list):
            raise ValueError("Ожидается список мест в JSON-ответе AI")
    except json.JSONDecodeError as e:
        raise ValueError(f"Невалидный JSON от AI: {str(e)}")

    places = []
    total_time_minutes = 0
    total_distance = 0.0

    for place in places_from_ai:
        title = place.get("title", "")
        category_obj = place.get("category", {})
        category_name = category_obj.get("name", "").lower()

        # Специфично сопоставляем с категорией из базы
        matched_category = match_place_with_db(category_name, category_map)

        # Получаем id места из базы по названию (или 0 если нет)
        place_id = db_places.get(title.lower(), 0)

        visit_duration = place.get("visit_duration", 30)
        distance_from_user = place.get("distance_from_user", 0.5)
        description = place.get("description", "")
        reasoning = place.get("reasoning", "")
        address = place.get("address", "")
        coordinates = place.get("coordinates", {"latitude": 0.0, "longitude": 0.0})

        total_time_minutes += visit_duration
        total_distance += distance_from_user

        places.append({
            "id": place_id,
            "title": title,
            "address": address,
            "coordinates": coordinates,
            "category": matched_category,
            "description": description,
            "visit_duration": visit_duration,
            "distance_from_user": distance_from_user,
            "reasoning": reasoning
        })

    walking_time_minutes = int((total_distance / 4.5) * 60) if total_distance > 0 else 0
    total_route_time = total_time_minutes + walking_time_minutes

    return {
        "route": {
            "places": places,
            "route_order": [p["id"] for p in places],
            "total_places": len(places),
            "total_time_minutes": total_route_time,
            "total_distance_km": round(total_distance, 2),
            "walking_time_minutes": walking_time_minutes,
            "visit_time_minutes": total_time_minutes,
            "map_data": {
                "center": [
                    sum(p["coordinates"]["latitude"] for p in places)/len(places) if places else 0.0,
                    sum(p["coordinates"]["longitude"] for p in places)/len(places) if places else 0.0,
                ],
                "zoom": 13
            }
        }
    }



def build_route_response_from_parsed(parsed_response: dict, route_request, request_id: str, exec_time_ms: int) -> dict:
    places = parsed_response.get("route", {}).get("places", [])
    total_places = len(places)
    total_visit_time = sum(place.get("visit_duration", 0) for place in places)
    total_distance = sum(place.get("distance_from_user", 0.0) for place in places)

    walking_time_minutes = int((total_distance / 4.5) * 60) if total_distance > 0 else 0
    total_time_minutes = total_visit_time + walking_time_minutes

    route_order = [place.get("id", idx) for idx, place in enumerate(places)]  # если id нет, берем индекс

    map_center = [
        getattr(route_request.user_location, "latitude", 0.0),
        getattr(route_request.user_location, "longitude", 0.0)
    ]

    response = {
        "route": {
            "places": places,
            "route_order": route_order,
            "total_places": total_places,
            "total_time_minutes": total_time_minutes,
            "total_distance_km": round(total_distance, 2),
            "walking_time_minutes": walking_time_minutes,
            "visit_time_minutes": total_visit_time,
            "map_data": {
                "center": map_center,
                "zoom": 13
            }
        },
        "metadata": {
            "selected_categories": list(set(place.get("category", {}).get("id") for place in places if place.get("category"))),
            "filtered_places_count": total_places,
            "request_id": request_id,
            "execution_time_ms": exec_time_ms
        }
    }

    return response



YANDEX_GEOCODER_API_URL = "https://geocode-maps.yandex.ru/1.x/"

async def geocode_place_yandex(api_key: str, place_title: str, address: str = None):
    query = place_title + address
    params = {
        "apikey": api_key,
        "format": "json",
        "geocode": query,
        "results": 1
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(YANDEX_GEOCODER_API_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
        try:
            pos = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
            lon, lat = map(float, pos.split())
            return lat, lon
        except (IndexError, KeyError):
            return None, None


async def update_coords_with_yandex_geocoder(api_key: str, parsed_response: dict) -> dict:
    places = parsed_response.get("route", {}).get("places", [])

    for place in places:
        lat, lon = await geocode_place_yandex(api_key, place.get("title", ""), place.get("address", ""))
        if lat is not None and lon is not None:
            place["coordinates"]["latitude"] = lat
            place["coordinates"]["longitude"] = lon

    return parsed_response
