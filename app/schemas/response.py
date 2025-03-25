from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

# 定义泛型类型
T = TypeVar('T')

class ResponseModel(BaseModel, Generic[T]):
    status: str
    data: Optional[T] = Field(default_factory=list)
    message: Optional[str] = Field(default="")

    class Config:
        # 允许使用任意数据类型
        arbitrary_types_allowed = True
