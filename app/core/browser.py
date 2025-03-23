from playwright.async_api import async_playwright

class Manager:
    def __init__(self):
        self.playwright = None

    async def initialize(self):
        """初始化 Playwright  和浏览器实例"""
        self.playwright = await async_playwright().start()

    async def close(self):
        """关闭浏览器实例和 Playwright"""
        try:
            if self.playwright:
                await self.playwright.stop()
        except RuntimeError as e:
            print(f"关闭 Playwright 时出错: {e}")

    
# 全局浏览器管理器
manager = Manager()