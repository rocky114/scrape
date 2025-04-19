from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page
from app.schemas.scrape import ScrapeResonse
from app.schemas.scrape import ScrapeRequest

class NJUParser(BaseParser):
    @staticmethod
    def domain() -> str:
        return "zsservice.nuaa.edu.cn"
    
    @staticmethod
    def name() -> str:
        return "南京航空航天大学"

    @staticmethod
    async def parse(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        ret: list[ScrapeResonse] = []

        # 点击"2024"（精确文本匹配）
        await page.locator(f'li.filter-item:has-text("{request.year}")').click()

        # 点击"江苏省"（精确文本匹配）
        await page.locator(f'li.filter-item:has-text("{request.province}")').click()

        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(1000)

        # 初始表格数据 物理类+一般录取
        try:
            items = await NJUParser.parse_table(page, request=request)
            ret.extend(items)
        except Exception as e:
            print(f"解析专业录取分数表格失败: {e}")

        return ret
    
    @staticmethod
    async def parse_table(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        """Helper function to extract table data from the page."""

        # 步骤1：确保表格可见
        # 等待表格刷新（DOM 更新）
        await page.wait_for_selector("table.filter-table:has(tbody tr)", state="attached")

        row_data = await page.evaluate('''(request) => {
            const rows = document.querySelectorAll('table.filter-table')[1].querySelectorAll('tbody tr');

            return Array.from(rows).map(row => {
                const columns = row.querySelectorAll('td');
                return columns.length > 0 ? {
                    year: columns[0].innerText.trim(),
                    province: columns[1].innerText.trim(),
                    admission_type: columns[2].innerText.trim(),
                    academic_category: columns[3].innerText.trim(),              
                    major_name: columns[5].innerText.trim(),                        
                    highest_score: columns[6].innerText.trim(),
                    lowest_score: columns[7].innerText.trim()     
                } : null;
            }).filter(item => item !== null);
        }''', {
            "year": request.year
        })

        return [ScrapeResonse(**item) for item in row_data]
    
