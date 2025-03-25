from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page
from app.schemas.scrape import ScrapeResonse

class NJUParser(BaseParser):
    @staticmethod
    def domain() -> str:
        return "bkzs.nju.edu.cn"
    
    @staticmethod
    def name() -> str:
        return "南京大学"

    @staticmethod
    async def parse(page: Page) -> list[ScrapeResonse]:
        ret: list[ScrapeResonse] = []

        # 初始表格数据
        try:
            items = await NJUParser.parse_table(page)
            ret.extend(items)
        except Exception as e:
            print(f"解析初始化表格失败: {e}")

        # 切换到历史类
        try:
            await page.get_by_role("link", name="历史类").click()
            # 等待表格刷新（网络空闲 + DOM 更新）
            await page.wait_for_load_state("networkidle")
            await page.wait_for_selector("table.table_1:has(tbody tr)", state="attached", timeout=5000)

            items = await NJUParser.parse_table(page)

            ret.extend(items)
        except Exception as e:
            print(f"解析历史类表格失败: {e}")

        return ret
    
    @staticmethod
    async def parse_table(page: Page) -> list[ScrapeResonse]:
        """Helper function to extract table data from the page."""

        row_data = await page.evaluate('''() => {
            const rows = document.querySelectorAll('table.table_1 tbody tr');
            return Array.from(rows).map(row => {
                const columns = row.querySelectorAll('td');
                return columns.length > 0 ? {
                    year: columns[0].innerText.trim(),
                    province: columns[1].innerText.trim(),
                    academic_category: columns[2].innerText.trim(),
                    type: columns[3].innerText.trim(),
                    minimum_score: columns[4].innerText.trim()     
                } : null;
            }).filter(item => item !== null);
        }''')

        return [ScrapeResonse(**item) for item in row_data]