"""
Тест подключения к PostgreSQL
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.config import settings

async def test_connection():
    """Проверка подключения к базе данных"""
    try:
        engine = create_async_engine(settings.DATABASE_URL, echo=True)
        
        async with engine.begin() as conn:
            # Используем text() для raw SQL в SQLAlchemy 2.0
            result = await conn.execute(text("SELECT version();"))
            version = result.fetchone()
            print(f"\n✅ Подключение успешно!")
            print(f"PostgreSQL версия: {version[0]}\n")
        
        await engine.dispose()
        
    except Exception as e:
        print(f"\n❌ Ошибка подключения: {e}\n")

if __name__ == "__main__":
    asyncio.run(test_connection())
