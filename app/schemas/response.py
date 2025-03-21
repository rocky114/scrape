from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel

# 定义泛型类型
T = TypeVar('T')

class ResponseModel(BaseModel, Generic[T]):
    status: str
    data: Optional[T] = None
    message: Optional[str] = None

    class Config:
        # 允许使用任意数据类型
        arbitrary_types_allowed = True