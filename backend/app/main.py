"""
FastAPI приложение - AI-помощник туриста
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Импортируем роутер
from app.api import health

app = FastAPI(
    title="AI Tourist Assistant API",
    description="API для генерации туристических маршрутов",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роуты
app.include_router(health.router, prefix="/api", tags=["Health"])


@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "AI Tourist Assistant API",
        "version": "1.0.0",
        "docs": "/docs"
    }
