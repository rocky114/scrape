from playwright.async_api import async_playwright

class Manager:
    def __init__(self):
        self.playwright = None
        self.browser = None

    async def initialize(self):
        """初始化 Playwright  和浏览器实例"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)

    async def close(self):
        """关闭浏览器实例和 Playwright"""
        if self.browser:
            await self.browser.close()

        if self.playwright:
            await self.playwright.stop()

    
# 全局浏览器管理器
manager = Manager()