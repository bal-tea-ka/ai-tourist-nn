"""
Pydantic схемы для маршрутов
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class UserLocation(BaseModel):
    """Местоположение пользователя"""
    address: str = Field(..., description="Адрес пользователя")
    latitude: float = Field(..., description="Широта", ge=-90, le=90)
    longitude: float = Field(..., description="Долгота", ge=-180, le=180)


class RouteRequest(BaseModel):
    """Запрос на генерацию маршрута"""
    user_interests: str = Field(..., description="Интересы пользователя", min_length=1)
    available_time_hours: int = Field(..., description="Доступное время (часы)", ge=1, le=8)
    user_location: UserLocation


class PlaceCoordinates(BaseModel):
    """Координаты места"""
    latitude: float
    longitude: float


class PlaceCategory(BaseModel):
    """Категория места"""
    id: int
    name: str


class Place(BaseModel):
    """Место в маршруте"""
    id: int
    title: str
    address: str
    coordinates: PlaceCoordinates
    category: PlaceCategory
    description: str
    visit_duration: int
    distance_from_user: float
    reasoning: Optional[str] = None


class RouteData(BaseModel):
    """Данные маршрута"""
    places: List[Place]
    route_order: List[int]
    total_places: int
    total_time_minutes: int
    total_distance_km: float
    walking_time_minutes: int
    visit_time_minutes: int
    map_data: dict


class RouteMetadata(BaseModel):
    """Метаданные запроса"""
    selected_categories: List[int]
    filtered_places_count: int
    request_id: str
    execution_time_ms: int


class RouteResponse(BaseModel):
    """Ответ с маршрутом"""
    route: RouteData
    metadata: RouteMetadata
