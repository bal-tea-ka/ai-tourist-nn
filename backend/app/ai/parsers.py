def parse_categories_response(response_text: str) -> list[int]:
    """
    Парсит ответ нейросети с выбранными категориями.
    Ожидается, что ответ будет в формате JSON-списка ID категорий, например: [1, 3, 5]
    """
    import json

    try:
        categories = json.loads(response_text)
        if isinstance(categories, list) and all(isinstance(cat_id, int) for cat_id in categories):
            return categories
    except json.JSONDecodeError:
        pass

    return []

def parse_route_response(response_text: str) -> list[dict]:
    """
    Парсит ответ нейросети с предложенным маршрутом.
    Ожидается, что ответ будет в формате JSON-списка объектов маршрута.
    Каждый объект должен содержать поля: title, address, category, visit_duration, notes.
    """
    import json

    try:
        route = json.loads(response_text)
        if isinstance(route, list) and all(isinstance(item, dict) for item in route):
            return route
    except json.JSONDecodeError:
        pass

    return []

def build_route_response(places: list, route_request, request_id: str, exec_time_ms: int) -> dict:
    """
    Формирует структуру RouteResponse для фронтенда.

    places: список мест, где каждое место - словарь с ключами:
        id, title, address, coordinates, category, description, visit_duration, distance_from_user, reasoning
    route_request: исходный запрос пользователя (Pydantic-модель)
    request_id: уникальный ID запроса
    exec_time_ms: время обработки запроса в миллисекундах

    Возвращает словарь с нужной вложенной структурой.
    """

    total_places = len(places)
    total_visit_time = sum(place.get("visit_duration", 0) for place in places)
    total_distance = sum(place.get("distance_from_user", 0.0) for place in places)

    # Пример расчета времени ходьбы (если нужно, здесь можно добавить более точную логику)
    walking_time_minutes = int((total_distance / 4.5) * 60) if total_distance > 0 else 0

    total_time_minutes = total_visit_time + walking_time_minutes

    route_order = [place["id"] for place in places]

    map_center = [
        route_request.user_location.latitude,
        route_request.user_location.longitude
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
