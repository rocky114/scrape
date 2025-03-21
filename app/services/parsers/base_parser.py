from abc import ABC, abstractmethod
from playwright.async_api import Page
from urllib.parse import urlparse

class BaseParser(ABC):
    @classmethod
    def match(cls, url: str) -> bool:
        domain = urlparse(url).netloc
        return cls.domain() in domain
    
    @staticmethod
    @abstractmethod
    def domain() -> str:
        """返回支持的域名关键字 （如 'njnu.edu.cn'）"""
        pass
    
    @staticmethod
    @abstractmethod
    async def parse(page: Page) -> dict:
        """解析页面并返回结构化数据"""
        pass