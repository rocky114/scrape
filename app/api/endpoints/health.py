from fastapi import APIRouter
from app.schemas.response import ResponseModel

router = APIRouter()

@router.get("/health", response_model=ResponseModel)
def health_check():
    return ResponseModel(status="success", message="ok")