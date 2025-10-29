from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.schemas.route import RouteRequest, RouteResponse
from app.database import get_db
from app.models.place import Place
from app.models.category import Category
from app.ai.perplexity_api import call_perplexity
from app.ai.prompts import build_categories_prompt, build_route_prompt
from app.ai.parsers import parse_categories_response, parse_route_response
from app.utils import build_route_response
import time

router = APIRouter()

# Категории и времена можно брать из базы или конфигов
CATEGORY_NAMES = {
    1: 'Памятники и скульптуры',
    2: 'Парки и скверы',
    3: 'Тактильные макеты',
    4: 'Набережные',
    5: 'Архитектура и достопримечательности',
    6: 'Культурные центры и досуг',
    7: 'Музеи',
    8: 'Театры и филармонии',
    10: 'Стрит-арт и мозаики',
}

CATEGORY_TIMES = {1: 15, 2: 45, 3: 10, 4: 30, 5: 20, 6: 60, 7: 60, 8: 120, 10: 10}

DOMAIN_FILTER = ["visitnn.ru", "wikipedia.org", "tripadvisor.ru", "idoris.ru", "nnm.ru"]

@router.post("/route/generate", response_model=RouteResponse)
async def generate_route(
    route_request: RouteRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    start_time = time.time()
    request_id = f"req_{str(time.time_ns())[-8:]}"

    try:
        # Запрос категорий по интересам пользователя
        prompt1 = build_categories_prompt(CATEGORY_NAMES, CATEGORY_TIMES, route_request.user_interests)
        categories_text = await call_perplexity(prompt1, DOMAIN_FILTER)
        selected_cat_ids = parse_categories_response(categories_text)
        if not selected_cat_ids:
            selected_cat_ids = list(CATEGORY_NAMES.keys())

        # Получаем категории из БД (опционально, можно брать из локального словаря)
        categories_query = await db.execute(
            select(Category).where(Category.id.in_(selected_cat_ids))
        )
        categories = categories_query.scalars().all()

        # Получаем места из БД, фильтруя по выбранным категориям
        places_query = await db.execute(
            select(Place).where(
                Place.category_id.in_(selected_cat_ids),
                Place.is_active == True
            )
        )
        places_db = places_query.scalars().all()

        # Форматируем места для промта (запроса нейросети)
        places = []
        for place in places_db:
            visit_duration = CATEGORY_TIMES.get(place.category_id, 30)
            places.append({
                "title": place.title,
                "address": place.address,
                "avg_visit_duration": visit_duration
            })

        # Формируем prompt для генерации маршрута
        prompt2 = build_route_prompt(places, route_request.available_time_hours, {
            "latitude": route_request.user_location.latitude,
            "longitude": route_request.user_location.longitude,
        })

        # Запрашиваем маршрут у нейросети
        route_text = await call_perplexity(prompt2, DOMAIN_FILTER)

        # Парсим ответ в структуру для frontend
        route_places = parse_route_response(route_text)

        exec_time_ms = int((time.time() - start_time) * 1000)
        route_response = build_route_response(route_places, route_request, request_id, exec_time_ms)

        # Логируем запрос/ответ
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        from app.services.logging_service import log_route_request
        await log_route_request(db, route_request, route_response, request_id, exec_time_ms, client_ip, user_agent)

        return route_response

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
