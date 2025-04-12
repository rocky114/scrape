from abc import ABC, abstractmethod
from playwright.async_api import Page
from urllib.parse import urlparse
from app.schemas.scrape import ScrapeResonse
from app.schemas.scrape import ScrapeRequest

class BaseParser(ABC):
    @classmethod
    def match(cls, university_name: str) -> bool:
        # domain = urlparse(url).netloc.lower()
        # 检查是否以目标域名结尾（包含直接相等的情况）
        return cls.name() == university_name
    
    @staticmethod
    @abstractmethod
    def domain() -> str:
        """返回支持的域名关键字 （如 'njnu.edu.cn'）"""
        pass

    @staticmethod
    @abstractmethod
    def name() -> str:
        """返回学校名称 （如 '南京大学'）"""
        pass
    
    @staticmethod
    @abstractmethod
    async def parse(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        """解析页面并返回结构化数据"""
        pass