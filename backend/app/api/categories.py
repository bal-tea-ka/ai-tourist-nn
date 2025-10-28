from fastapi import APIRouter

router = APIRouter()

# Временные данные категорий (пока нет БД)
CATEGORIES_DATA = [
    {
        "id": 1,
        "name": "Памятники и скульптуры",
        "description": "Памятники историческим личностям и скульптуры",
        "avg_visit_duration": 15,
        "icon": "monument",
        "places_count": 15
    },
    {
        "id": 2,
        "name": "Парки и скверы",
        "description": "Парки, скверы, сады для прогулок и отдыха",
        "avg_visit_duration": 45,
        "icon": "park",
        "places_count": 23
    },
    {
        "id": 3,
        "name": "Тактильные макеты",
        "description": "Тактильные макеты достопримечательностей для людей с ОВЗ",
        "avg_visit_duration": 10,
        "icon": "accessibility",
        "places_count": 12
    },
    {
        "id": 4,
        "name": "Набережные",
        "description": "Набережные рек Волги и Оки",
        "avg_visit_duration": 30,
        "icon": "water",
        "places_count": 7
    },
    {
        "id": 5,
        "name": "Архитектура и достопримечательности",
        "description": "Исторические здания, архитектурные памятники",
        "avg_visit_duration": 20,
        "icon": "building",
        "places_count": 62
    },
    {
        "id": 6,
        "name": "Культурные центры и досуг",
        "description": "Дворцы культуры, планетарии, кинотеатры",
        "avg_visit_duration": 60,
        "icon": "entertainment",
        "places_count": 39
    },
    {
        "id": 7,
        "name": "Музеи",
        "description": "Музеи, галереи, выставочные центры",
        "avg_visit_duration": 60,
        "icon": "museum",
        "places_count": 18
    },
    {
        "id": 8,
        "name": "Театры и филармонии",
        "description": "Театры, филармонии, концертные залы",
        "avg_visit_duration": 120,
        "icon": "theater",
        "places_count": 10
    },
    {
        "id": 10,
        "name": "Стрит-арт и мозаики",
        "description": "Уличное искусство, граффити, советские мозаики",
        "avg_visit_duration": 10,
        "icon": "art",
        "places_count": 72
    }
]


@router.get("/categories")
async def get_categories():
    """
    Получить список всех категорий мест
    
    Returns:
        dict: Список категорий с информацией
    """
    return {
        "categories": CATEGORIES_DATA,
        "total": len(CATEGORIES_DATA)
    }


@router.get("/categories/{category_id}")
async def get_category_by_id(category_id: int):
    """
    Получить информацию о конкретной категории
    
    Args:
        category_id: ID категории
        
    Returns:
        dict: Информация о категории
    """
    category = next((cat for cat in CATEGORIES_DATA if cat["id"] == category_id), None)
    
    if not category:
        return {
            "error": "Category not found",
            "category_id": category_id
        }
    
    return category
