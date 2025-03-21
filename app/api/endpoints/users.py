from fastapi import APIRouter
from app.schemas.response import ResponseModel
from app.schemas.user import UserResponse

router = APIRouter()

@router.get("/users", response_model=ResponseModel[list[UserResponse]])
def get_users():
    users = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ]

    return ResponseModel[list[UserResponse]](status="success", data=users)