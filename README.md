
🗺️ AI-помощник туриста | Нижний Новгород
Веб-приложение для генерации персональных туристических маршрутов по Нижнему Новгороду с использованием ИИ.

🚀 Технологии
Backend: FastAPI + PostgreSQL + Perplexity API

Frontend: HTML/CSS/JS + Bootstrap + Yandex Maps

Хостинг: Render (backend) + Vercel (frontend)

📦 Структура проекта
text
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
# Отредактируйте .env и добавьте API ключи
uvicorn app.main:app --reload
Frontend
powershell
cd frontend
python -m http.server 3000
Откройте http://localhost:3000

📝 Конфигурация
Backend: Скопируйте +"backend/.env.example"+ в +"backend/.env"+ и заполните переменные

Frontend: В +"frontend/js/config.js"+ замените YOUR_API_KEY на ваш ключ Яндекс.Карт

🗄️ База данных
Структура БД описана в +"docs/DATABASE.md"+

📖 Документация
API: +"docs/API.md"+

Деплой: +"docs/DEPLOYMENT.md"+

База данных: +"docs/DATABASE.md"+

👥 Команда
[Добавьте имена участников команды]

📄 Лицензия
MIT
