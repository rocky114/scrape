from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page
from app.schemas.scrape import ScrapeResonse
from app.schemas.scrape import ScrapeRequest

class PageParser(BaseParser):
    @staticmethod
    def domain() -> str:
        return "tecwx.suda.edu.cn"
    
    @staticmethod
    def name() -> str:
        return "苏州大学应用技术学院"

    @staticmethod
    async def parse(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        ret: list[ScrapeResonse] = []
        # 点击"2024"（精确文本匹配）
        await page.locator(f'div.item:has-text("{request.year}")').click()

        # 点击"江苏省"（精确文本匹配）
        await page.locator(f'div.item:has-text("{request.province}")').click()

        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(1000)

        items = await PageParser.parse_table(page, request)
        ret.extend(items)

        return ret
    
    @staticmethod
    async def parse_table(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        # 步骤1：确保表格可见
        # 等待表格刷新（DOM 更新）
        await page.wait_for_selector("table.el-table__body:has(tbody tr)", state="attached", timeout=5000)
    
        # 步骤2：等待行数据加载
        # await PageParser.wait_for_table_rows(page)

        row_data = await page.evaluate('''(request) => {
            const rows = document.querySelectorAll('table.el-table__body')[1].querySelectorAll('tbody tr');
                           
            return Array.from(rows).map(row => {
                let columns = row.querySelectorAll('td');
                let admission_type = request.admission_type;
                if (columns[4].innerText.trim().includes("艺术")) {
                    admission_type = "艺术类";                   
                }
                return columns.length > 0 ? {
                    year: columns[1].innerText.trim(),
                    province: columns[2].innerText.trim(),
                    admission_type: admission_type,
                    enrollment_quota: columns[6].innerText.trim(),                                      
                    major_name: columns[5].innerText.trim(),                   
                    academic_category: columns[3].innerText.trim().match(/[（(](.+?)[）)]/)?.[1],
                    lowest_score: columns[8].innerText.trim(),
                    highest_score: columns[9].innerText.trim()
                } : null;
            }).filter(item => item !== null);
        }''', {
            "admission_type": request.admission_type
        })

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