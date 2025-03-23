from fastapi import APIRouter
from app.api.endpoints import login
from app.api.endpoints import users
from app.api.endpoints import health
from app.api.endpoints import scrape

api_router = APIRouter()

# 注册路由
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(health.router, tags=["health"])
api_router.include_router(scrape.router, tags=["scrape"])