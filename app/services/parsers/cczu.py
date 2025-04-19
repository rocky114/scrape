from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page
from app.schemas.scrape import ScrapeResonse
from app.schemas.scrape import ScrapeRequest

class NJUParser(BaseParser):
    @staticmethod
    def domain() -> str:
        return "cdzs.cczu.edu.cn"
    
    @staticmethod
    def name() -> str:
        return "常州大学"

    @staticmethod
    async def parse(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        ret: list[ScrapeResonse] = []

        # 切换到 物理类+中外合作办学
        try:
            await page.locator("div#searchBox input#searchBtn").click()

            items = await NJUParser.parse_table(page, request)

            ret.extend(items)
        except Exception as e:
            print(f"解析表格失败: {e}")   

            raise

        return ret
    
    @staticmethod
    async def parse_table(page: Page, request:ScrapeRequest) -> list[ScrapeResonse]:
        """Helper function to extract table data from the page."""

        # 步骤1：确保表格可见
        # 等待表格刷新（DOM 更新）
        await page.wait_for_selector("div#result table:has(tbody tr)", state="attached", timeout=5000)
    
        # 步骤2：等待行数据加载
        # await NJUParser.wait_for_table_rows(page)

        row_data = await page.evaluate('''(request) => {
            const rows = document.querySelectorAll('div#result table tbody tr');
            return Array.from(rows).slice(1).map(row => {
                const columns = row.querySelectorAll('td');
                return {
                    year: request.year,
                    province: columns[0].innerText.trim(),
                    academic_category: columns[1].innerText.trim(),
                    admission_type: columns[2].innerText.trim(),
                    major_name: columns[3].innerText.trim(),
                    enrollment_quota: columns[4].innerText.trim(),
                    highest_score: columns[5].innerText.trim(),
                    highest_score_rank: columns[6].innerText.trim(),
                    lowest_score: columns[7].innerText.trim(),
                    lowest_score_rank: columns[8].innerText.trim()     
                };
            }).filter(item => item !== null);
        }''', {
            "year": request.year
        })

        return [ScrapeResonse(**item) for item in row_data]
    
    @staticmethod
    async def wait_for_table_rows(page: Page):
        """等待表格行加载完成"""
        try:
            # 条件1：等待至少1个tr存在（且列数正确）
            await page.wait_for_function('''() => {
                const rows = document.querySelectorAll('div#result table tbody tr');
                return rows.length > 0 && rows[0].querySelectorAll('td').length >= 5;
            }''', timeout=10000)
                
        except Exception as e:
            print(f"等待表格行加载完成失败: {e}")
            raise