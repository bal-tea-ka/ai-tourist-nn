
🗺️ AI-помощник туриста | Нижний Новгород
Веб-приложение для генерации персональных туристических маршрутов по Нижнему Новгороду с использованием ИИ.

🚀 Технологии
Backend: FastAPI + PostgreSQL + Openrouter API

Frontend: HTML/CSS/JS + Bootstrap + Yandex Maps

📦 Структура проекта
├── backend/          # FastAPI приложение
├── frontend/         # Веб-интерфейс
├── docs/            # Документация
└── .github/         # CI/CD
🛠️ Локальная разработка
Backend
powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Отредактируйте в .env строчку подключения к вашей БД
uvicorn app.main:app --reload
Frontend
powershell
cd frontend
python -m http.server 3000
Откройте http://localhost:3000

📝 Конфигурация
Backend: Скопируйте +"backend/.env.example"+ в +"backend/.env"+ и замените строчку подключения к базе данных по образцу

🗄️ База данных

