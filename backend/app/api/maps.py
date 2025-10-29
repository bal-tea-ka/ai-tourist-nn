"""
Maps API endpoint
Прокси для безопасной работы с Яндекс.Картами
"""
from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx
from app.config import settings

router = APIRouter()


class MapConfigResponse(BaseModel):
    """Конфигурация для карт"""
    api_key: str
    center: list[float]
    zoom: int


class GeocodeRequest(BaseModel):
    """Запрос геокодирования"""
    address: str


class GeocodeResponse(BaseModel):
    """Ответ геокодирования"""
    address: str
    latitude: float
    longitude: float
    formatted_address: Optional[str] = None


@router.get("/maps/config", response_model=MapConfigResponse)
async def get_map_config():
    """
    Получить конфигурацию для инициализации карты
    
    Returns:
        MapConfigResponse: API ключ и настройки карты
    """
    if not settings.YANDEX_MAPS_API_KEY:
        raise HTTPException(status_code=500, detail="Yandex Maps API key not configured")
    
    return {
        "api_key": settings.YANDEX_MAPS_API_KEY,
        "center": [56.3287, 44.0020],  # Нижний Новгород
        "zoom": 12
    }


@router.post("/maps/geocode", response_model=GeocodeResponse)
async def geocode_address(request: GeocodeRequest):
    """
    Геокодирование адреса через Яндекс Geocoder API
    
    Преимущество: API ключ геокодера полностью скрыт от фронтенда
    
    Args:
        request: Адрес для геокодирования
        
    Returns:
        GeocodeResponse: Координаты и отформатированный адрес
    """
    if not settings.YANDEX_GEOCODER_API_KEY:
        raise HTTPException(status_code=500, detail="Geocoder API key not configured")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://geocode-maps.yandex.ru/1.x/",
                params={
                    "apikey": settings.YANDEX_GEOCODER_API_KEY,
                    "geocode": f"Нижний Новгород, {request.address}",  # Добавляем город для точности
                    "format": "json",
                    "results": 1
                },
                timeout=10.0
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Парсим ответ
            geo_objects = data.get("response", {}).get("GeoObjectCollection", {}).get("featureMember", [])
            
            if not geo_objects:
                raise HTTPException(status_code=404, detail="Адрес не найден")
            
            # Берём первый результат
            geo_object = geo_objects[0]["GeoObject"]
            point = geo_object["Point"]["pos"]
            formatted_address = geo_object.get("metaDataProperty", {}).get("GeocoderMetaData", {}).get("text", "")
            
            # Координаты в формате "долгота широта"
            lon, lat = map(float, point.split())
            
            return {
                "address": request.address,
                "latitude": lat,
                "longitude": lon,
                "formatted_address": formatted_address
            }
            
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Geocoding API error: {str(e)}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Connection error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Geocoding error: {str(e)}")
        

@router.post("/maps/suggestions")
async def get_address_suggestions(query: dict = Body(...)):
    search_text = query.get("query")
    if not search_text:
        raise HTTPException(status_code=400, detail="Query is required")

    params = {
        "apikey" : settings.YANDEX_SUGGEST_API_URL,
        "v": 4,
        "type": "geo",
        "part": search_text,
        "lang": "ru_RU",
        "results": 5,

    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(params=params)
            response.raise_for_status()
            data = response.json()
            # Возвращаем список подсказок (обычно в data["suggestions"])
            return {"suggestions": data.get("suggestions", [])}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching suggestions: {e}")
