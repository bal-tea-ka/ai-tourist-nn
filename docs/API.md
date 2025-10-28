
API Документация
Базовый URL
text
http://localhost:8000/api
Endpoints
GET /health
Проверка работоспособности API

Response:

json
{
  "status": "ok"
}
GET /categories
Получение списка категорий мест

Response:

json
{
  "categories": [
    {
      "id": 1,
      "name": "Памятники и скульптуры",
      "avg_visit_duration": 15
    }
  ]
}
POST /route/generate
Генерация персонального маршрута

Request:

json
{
  "user_interests": "история, музеи",
  "available_time_hours": 3,
  "user_location": {
    "address": "Площадь Минина",
    "latitude": 56.3287,
    "longitude": 44.0020
  }
}
Response:

json
{
  "route": {
    "places": [...],
    "total_time_minutes": 165,
    "total_distance_km": 3.2
  }
}
