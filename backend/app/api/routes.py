from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.route import RouteRequest, RouteResponse
from app.database import get_db
from app.models.place import Place
from app.config import settings
from app.ai.deepseek_api import ask_openrouter
from app.ai.prompts import build_categories_prompt, build_route_prompt
from app.ai.get_from_db import get_categories_from_db, get_places_from_db
from app.ai.parsers import build_route_response_from_parsed, clean_ai_response, load_category_map, parse_categories_response, parse_route_response, update_coords_with_yandex_geocoder
import time
import uuid

router = APIRouter()


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
        categories_text = await ask_openrouter(prompt1, settings.AI_API_KEY)
        cleaned_categories_text = clean_ai_response(categories_text)
        print(f"parse_categories_response input: {repr(cleaned_categories_text)}")
        if not cleaned_categories_text.strip():
            raise ValueError("Пустой ответ для парсинга категорий")

       
        selected_cat_ids = parse_categories_response(cleaned_categories_text)
        if not selected_cat_ids:
            selected_cat_ids = list(category_names.keys())

        places = await get_places_from_db(db)   

        # Формируем prompt для генерации маршрута
        prompt2 = build_route_prompt(places, route_request.available_time_hours, {
            "latitude": route_request.user_location.latitude,
            "longitude": route_request.user_location.longitude,
        })

        # Запрашиваем маршрут у нейросети
        route_text = await ask_openrouter(prompt2, settings.AI_API_KEY)
        cleaned_route_text = clean_ai_response(route_text)
        print("AI response:", cleaned_route_text)

        # Парсим ответ в структуру для frontend
        category_map = await load_category_map(db)

        result = await db.execute(select(Place))  
        db_places_list = result.scalars().all()
        db_places = {place.title.lower(): place.id for place in db_places_list}
        parsed_response = parse_route_response(cleaned_route_text, category_map, db_places)
        parsed_response = await update_coords_with_yandex_geocoder(settings.YANDEX_GEOCODER_API_KEY, parsed_response)
        request_id = str(uuid.uuid4())
        exec_time_ms = int((time.time() - start_time) * 1000)      
        route_response_dict = build_route_response_from_parsed(parsed_response, route_request, request_id, exec_time_ms )
        route_response = RouteResponse.parse_obj(route_response_dict)
        print(f"\n\nBilded route responce: {route_response}\n\n")
        

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
