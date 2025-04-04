from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.browser import manager
from app.api.routers import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await manager.initialize()

        yield
    finally:
        await manager.close()


app = FastAPI(title="Project", lifespan=lifespan)

# 加载路由
app.include_router(api_router, prefix="/api/v1")

