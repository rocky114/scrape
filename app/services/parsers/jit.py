from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page
from app.schemas.scrape import ScrapeResonse
from app.schemas.scrape import ScrapeRequest

class PageParser(BaseParser):
    @staticmethod
    def domain() -> str:
        return "jit.edu.cn"
    
    @staticmethod
    def name() -> str:
        return "金陵科技学院"

    @staticmethod
    async def parse(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        ret: list[ScrapeResonse] = []
        """省份"""
        await page.select_option('div.chaxun-anniu div li:nth-child(1) select', value=f'{request.year}')
        await page.select_option('div.chaxun-anniu div li:nth-child(2) select', value=f'{request.province}')
        await page.select_option('div.chaxun-anniu div li:nth-child(3) select', value=f'{request.admission_type}')

        await page.locator("div.chaxun-anniu div li:nth-child(4) a.erss").click()
        await page.wait_for_load_state("networkidle")

        while True:
            # 初始表格数据 物理类+一般录取
            items = await PageParser.parse_table(page, request)
            ret.extend(items)

            # 检查是否有下一页
            next_btn = page.locator('.layui-laypage-next:not(.layui-disabled)')
            if not await next_btn.count():
                break  # 没有下一页，退出循环

            # 点击下一页
            await next_btn.click()
            await page.wait_for_load_state("networkidle")  # 等待加载完成
            await page.wait_for_timeout(1000)
        return ret
    
    @staticmethod
    async def parse_table(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        """Helper function to extract table data from the page."""

        # 步骤1：确保表格可见
        # 等待表格刷新（DOM 更新）
        await page.wait_for_selector("div.layui-table-body table:has(tbody tr)", state="attached", timeout=5000)
    
        # 步骤2：等待行数据加载
        await PageParser.wait_for_table_rows(page)

        row_data = await page.evaluate('''() => {
            const rows = document.querySelectorAll('div.layui-table-body table tbody tr');
            return Array.from(rows).map(row => {
                const columns = row.querySelectorAll('td');
                return columns.length > 0 ? {
                    year: columns[0].innerText.trim(),
                    province: columns[1].innerText.trim(),
                    admission_type: columns[2].innerText.trim(),                   
                    major_name: columns[5].innerText.trim(),                   
                    academic_category: columns[3].innerText.trim(),
                    lowest_score: columns[7].innerText.trim()
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
                const rows = document.querySelectorAll('div.layui-table-body table tbody tr');
                return rows.length > 0 && rows[0].querySelectorAll('td').length >= 5;
            }''', timeout=10000)
                
        except Exception as e:
            print(f"等待表格行加载完成失败: {e}")
            raise