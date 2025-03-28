from fastapi import APIRouter
from app.schemas.response import ResponseModel

router = APIRouter()

@router.get("/health", response_model=ResponseModel)
def health_check(page: str | None = None):
    if page :
        print("health?page={page}")
    else:
        print(f"health")    
    return ResponseModel(status="success", message="ok")