from fastapi import APIRouter
from app.schemas.login import LoginRequest
from app.schemas.response import ResponseModel
from app.core.browser import manager

router = APIRouter()

@router.post("/login", response_model=ResponseModel)
async def login(item : LoginRequest):
    context = await manager.browser.new_context()

    try:
        page = await context.new_page()
    finally:
        context.close()