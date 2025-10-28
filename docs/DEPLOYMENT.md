
Инструкция по деплою
Backend (Render)
Создать аккаунт на render.com

Создать PostgreSQL базу (Free tier)

Создать Web Service:

Build Command: +"pip install -r backend/requirements.txt"+

Start Command: +"cd backend && uvicorn app.main:app --host 0.0.0.0 --port "+

Добавить переменные окружения из .env.example

Frontend (Vercel)
Создать аккаунт на vercel.com

Импортировать GitHub репозиторий

Root Directory: +"frontend/"+

Deploy
