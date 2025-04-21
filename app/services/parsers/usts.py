from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page
from app.schemas.scrape import ScrapeResonse
from app.schemas.scrape import ScrapeRequest

class PageParser(BaseParser):
    @staticmethod
    def domain() -> str:
        return "usts.edu.cn"
    
    @staticmethod
    def name() -> str:
        return "苏州科技大学"

    @staticmethod
    async def parse(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        ret: list[ScrapeResonse] = []

        try:
            items = await PageParser.parse_table(page, request)
            ret.extend(items)
        except Exception as e:
            print(f"解析表格失败: {e}")

        return ret
    
    @staticmethod
    async def parse_table(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        """Helper function to extract table data from the page."""

        # 第一层 iframe
        first_level_iframe = await page.wait_for_selector("iframe", timeout=30000)
        first_frame = await first_level_iframe.content_frame()
    
        # 第二层 iframe
        second_level_iframe = await first_frame.wait_for_selector("iframe", timeout=30000)
        frame = await second_level_iframe.content_frame()

        # 步骤1：确保表格可见
        # 等待表格刷新（DOM 更新）
        await frame.wait_for_selector("table:has(tbody tr)", state="attached", timeout=5000)
    
        # 步骤2：等待行数据加载
        # await PageParser.wait_for_table_rows(frame)

        row_data = await frame.evaluate('''(request) => {
            const rows = document.querySelectorAll('table tbody tr');
            return Array.from(rows).slice(2, -1).map(row => {
                const columns = row.querySelectorAll('td');

                return columns.length >= 9 ? {
                    year: request.year,
                    province: request.province,
                    academic_category: columns[2].innerText.trim(),
                    admission_type: columns[1].innerText.trim(),
                    major_name: columns[3].innerText.trim(),
                    enrollment_quota: columns[4].innerText.trim(),
                    highest_score: columns[5].innerText.trim(),
                    lowest_score: columns[6].innerText.trim()
                } : null;
            }).filter(item => item !== null);
        }''', {
            "year": request.year,
            "province": request.province
        })

        return [ScrapeResonse(**item) for item in row_data]
    
    @staticmethod
    async def wait_for_table_rows(page: Page):
        """等待表格行加载完成"""
        try:
            # 条件1：等待至少1个tr存在（且列数正确）
            await page.wait_for_function('''() => {
                const rows = document.querySelectorAll('table tbody tr');
                return rows.length > 0 && rows[0].querySelectorAll('td').length >= 5;
            }''', timeout=10000)
                
        except Exception as e:
            print(f"等待表格行加载完成失败: {e}")
            raise