"""
Проверка созданных таблиц
"""
import asyncio
from sqlalchemy import text
from app.database import engine

async def check_tables():
    async with engine.begin() as conn:
        result = await conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """))
        
        tables = result.fetchall()
        
        print("\n✅ Таблицы в базе данных:")
        for table in tables:
            print(f"  - {table[0]}")
        print()

asyncio.run(check_tables())
