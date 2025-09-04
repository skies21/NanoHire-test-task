from fastapi import FastAPI
from app.views import router as views_router
from app.database import init_db

app = FastAPI()

# Инициализируем базу данных
init_db()

app.include_router(views_router)
