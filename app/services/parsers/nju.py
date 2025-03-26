from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page
from app.schemas.scrape import ScrapeResonse
import asyncio

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

        # 初始表格数据 物理类+一般录取
        try:
            items = await NJUParser.parse_table(page)
            ret.extend(items)
        except Exception as e:
            print(f"解析物理类+一般录取表格失败: {e}")

        # 切换到 物理类+中外合作办学
        try:
            await page.get_by_role("link", name="中外合作办学").click()

            items = await NJUParser.parse_table(page)

            ret.extend(items)
        except Exception as e:
            print(f"解析物理类+中外合作办学表格失败: {e}")   

        # 切换到 历史类+一般录取
        try:
            await page.get_by_role("link", name="历史类").click()

            items = await NJUParser.parse_table(page)

            ret.extend(items)
        except Exception as e:
            print(f"解析历史类+一般录取表格失败: {e}") 

        await asyncio.sleep(30)  # 强制等待2秒观察页面
        return ret
    
    @staticmethod
    async def parse_table(page: Page) -> list[ScrapeResonse]:
        """Helper function to extract table data from the page."""

        # 步骤1：确保表格可见
        # 等待表格刷新（DOM 更新）
        await page.wait_for_selector("table#zsSsgradeListPlace:has(tbody tr)", state="attached", timeout=5000)
    
        # 步骤2：等待行数据加载
        await NJUParser.wait_for_table_rows(page)

        row_data = await page.evaluate('''() => {
            const rows = document.querySelectorAll('table#zsSsgradeListPlace tbody tr');
            return Array.from(rows).map(row => {
                console.log(row.outerHTML)                       
                const columns = row.querySelectorAll('td');
                return columns.length > 0 ? {
                    year: columns[0].innerText.trim(),
                    province: columns[1].innerText.trim(),
                    academic_category: columns[2].innerText.trim(),
                    admission_type: columns[3].innerText.trim(),
                    min_score: columns[4].innerText.trim()     
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
                const rows = document.querySelectorAll('table.table_1 tbody tr');
                return rows.length > 0 && rows[0].querySelectorAll('td').length >= 5;
            }''', timeout=10000)
                
        except Exception as e:
            print(f"等待表格行加载完成失败: {e}")
            raise