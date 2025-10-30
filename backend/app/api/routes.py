from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.route import RouteRequest, RouteResponse
from app.database import get_db
from app.ai.perplexity_api import call_perplexity
from app.ai.prompts import build_categories_prompt, build_route_prompt
from app.ai.get_from_db import get_categories_from_db, get_places_from_db
from app.ai.parsers import parse_categories_response, parse_route_response, build_route_response
import time

router = APIRouter()


DOMAIN_FILTER = ["visitnn.ru", "tripadvisor.ru", "idoris.ru", "nnm.ru", "wikipedia.org"]

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
        category_names, category_times = await get_categories_from_db(db)

        print(f"category_names keys: {list(category_names.keys())} // type: {type(category_names)}")
        print(f"category_times keys: {list(category_times.keys())} // type: {type(category_times)}")

        prompt1 = build_categories_prompt(route_request.user_interests, category_names, category_times)
        categories_text = await call_perplexity(prompt1, DOMAIN_FILTER)
        selected_cat_ids = parse_categories_response(categories_text)
        if not selected_cat_ids:
            selected_cat_ids = list(category_names.keys())

        places = await get_places_from_db(db)   

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
