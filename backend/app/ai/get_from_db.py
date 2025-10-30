from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.category import Category
from app.models.place import Place
from sqlalchemy.orm import joinedload

async def get_categories_from_db(session: AsyncSession):
    result = await session.execute(select(Category))
    categories = result.scalars().all()
    category_names = {category.id: category.name for category in categories}
    category_times = {category.id: category.avg_visit_duration for category in categories}
    return category_names, category_times

async def get_places_from_db(session: AsyncSession):
    result = await session.execute(
        select(Place).options(joinedload(Place.category)).where(Place.is_active == True)
    )
    places = result.scalars().all()
    place_list = []
    for place in places:
        place_list.append({
            "id" : place.id,
            "title": place.title,
            "address": place.address,
            "category": place.category.name if place.category else "",
            "avg_visit_duration": place.category.avg_visit_duration if place.category and hasattr(place.category, 'avg_visit_duration') else 30,
            "description": place.description
        })
    return place_list

