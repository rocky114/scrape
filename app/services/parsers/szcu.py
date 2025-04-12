from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page
from app.schemas.scrape import ScrapeResonse
from app.schemas.scrape import ScrapeRequest

class PageParser(BaseParser):
    @staticmethod
    def domain() -> str:
        return "szcu.edu.cn"
    
    @staticmethod
    def name() -> str:
        return "苏州城市学院"

    @staticmethod
    async def parse(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        ret: list[ScrapeResonse] = []

        # 点击"江苏省"（精确文本匹配）
        await page.locator(f'div.item:has-text("{request.province}")').click()
        
        # 点击"2024"（精确文本匹配）
        await page.locator(f'div.item:has-text("{request.year}")').click()

        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(1000)

        items = await PageParser.parse_table(page)
        ret.extend(items)

        return ret
    
    @staticmethod
    async def parse_table(page: Page) -> list[ScrapeResonse]:
        """Helper function to extract table data from the page."""

        # 步骤1：确保表格可见
        # 等待表格刷新（DOM 更新）
        await page.wait_for_selector("table.el-table__body:has(tbody tr)", state="attached", timeout=5000)
    
        # 步骤2：等待行数据加载
        await PageParser.wait_for_table_rows(page)

        row_data = await page.evaluate('''(request) => {
            const rows = document.querySelectorAll('table.el-table__body')[1].querySelectorAll('tbody tr');
                           
            return Array.from(rows).map(row => {
                let columns = row.querySelectorAll('td');
                
                return columns.length > 0 ? {
                    year: columns[0].innerText.trim(),
                    province: columns[2].innerText.trim(),
                    admission_type: columns[4].innerText.trim(),
                    enrollment_quota: columns[5].innerText.trim(),                                      
                    major_name: columns[6].innerText.trim(),                   
                    academic_category: columns[3].innerText.trim(),
                    lowest_score: columns[8].innerText.trim(),
                    highest_score: columns[9].innerText.trim(),
                    min_admission_score: columns[11].innerText.trim()                      
                } : null;
            }).filter(item => item !== null);
        }''')

        return [ScrapeResonse(**item) for item in row_data]
    
    @staticmethod
    async def wait_for_table_rows(page: Page):
        """等待表格行加载完成"""
        try:
            # 条件1：等待至少1个tr存在（且列数正确）
            await page.wait_for_function('''() => {
                const rows = document.querySelectorAll('table.el-table__body')[1].querySelectorAll('tbody tr');
                return rows.length > 0 && rows[0].querySelectorAll('td').length >= 4;
            }''', timeout=10000)
                
        except Exception as e:
            print(f"等待表格行加载完成失败: {e}")
            raise