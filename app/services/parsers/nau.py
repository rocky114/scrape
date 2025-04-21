from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page
from app.schemas.scrape import ScrapeResonse
from app.schemas.scrape import ScrapeRequest

class PageParser(BaseParser):
    @staticmethod
    def domain() -> str:
        return "nau.edu.cn"
    
    @staticmethod
    def name() -> str:
        return "南京审计大学"

    @staticmethod
    async def parse(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        ret: list[ScrapeResonse] = []

        await page.locator(f'li:has-text("{request.year}")').click()
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(500)

        while True:
            # 初始表格数据 物理类+一般录取
            items = await PageParser.parse_table(page, request)
            ret.extend(items)

            # 检查是否有下一页
            next_btn = page.locator('button.btn-next:not([disabled])')
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
        await page.wait_for_selector("div.el-table__body-wrapper table:has(tbody tr)", state="attached", timeout=5000)
    
        # 步骤2：等待行数据加载
        await PageParser.wait_for_table_rows(page)

        row_data = await page.evaluate('''(request) => {
            const rows = document.querySelectorAll('div.el-table__body-wrapper table tbody tr');
            return Array.from(rows).map(row => {
                const columns = row.querySelectorAll('td');
                let admission_type = request.admission_type;                       
                if (columns[2].innerText.trim().includes("中外合作办学")) {
                    admission_type = "中外合作办学";
                }                        
                return columns.length > 0 ? {
                    year: request.year,
                    province: request.province,
                    admission_type: admission_type,                   
                    academic_category: columns[0].innerText.trim(),
                    major_name: columns[2].innerText.trim(),
                    lowest_score: columns[3].innerText.trim()     
                } : null;
            }).filter(item => item !== null);
        }''', {
            "year": request.year,
            "province": request.province,
            "admission_type": request.admission_type
        })

        return [ScrapeResonse(**item) for item in row_data]
    
    @staticmethod
    async def wait_for_table_rows(page: Page):
        """等待表格行加载完成"""
        try:
            # 条件1：等待至少1个tr存在（且列数正确）
            await page.wait_for_function('''() => {
                const rows = document.querySelectorAll('div.el-table__body-wrapper table tbody tr');
                return rows.length > 0 && rows[0].querySelectorAll('td').length >= 4;
            }''', timeout=10000)
                
        except Exception as e:
            print(f"等待表格行加载完成失败: {e}")
            raise