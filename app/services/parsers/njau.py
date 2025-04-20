from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page
from app.schemas.scrape import ScrapeResonse
from app.schemas.scrape import ScrapeRequest

class PageParser(BaseParser):
    @staticmethod
    def domain() -> str:
        return ""
    
    @staticmethod
    def name() -> str:
        return "南京农业大学"

    @staticmethod
    async def parse(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        ret: list[ScrapeResonse] = []

        """历史类"""
        items = await PageParser.parse_table(page, request)
        ret.extend(items)

        """物理类"""
        await page.locator(f'div.filter a[data-value="物理类"]').click()
        items = await PageParser.parse_table(page, request)
        ret.extend(items)

        request.admission_type = "提前批"
        await page.locator(f'div.filter a[data-value="提前批"]').click()
        items = await PageParser.parse_table(page, request)
        ret.extend(items)

        request.admission_type = "高校专项计划"
        await page.locator(f'div.filter a[data-value="高校专项计划"]').click()
        items = await PageParser.parse_table(page, request)
        ret.extend(items)

        """艺术(历史类)"""
        request.admission_type = "艺术类"
        await page.locator(f'div.filter a[data-value="艺术(历史类)"]').click()
        items = await PageParser.parse_table(page, request)
        ret.extend(items)
        
        """艺术(物理类)"""
        request.admission_type = "艺术类"
        await page.locator(f'div.filter a[data-value="艺术(物理类)"]').click()
        items = await PageParser.parse_table(page, request)
        ret.extend(items) 

        return ret
    
    @staticmethod
    async def parse_table(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(500)

        # 步骤1：确保表格可见
        # 等待表格刷新（DOM 更新）
        await page.wait_for_selector("table#sszygradeListPlace:has(tbody tr)", state="attached", timeout=5000)
    
        # 步骤2：等待行数据加载
        await PageParser.wait_for_table_rows(page)

        row_data = await page.evaluate('''(request) => {
            const rows = document.querySelectorAll('table#sszygradeListPlace tbody tr');
            return Array.from(rows).map(row => {
                const columns = row.querySelectorAll('td');
                return columns.length > 0 ? {
                    year: columns[0].innerText.trim(),
                    province: columns[1].innerText.trim(),
                    admission_type: request.admission_type,                   
                    academic_category: columns[2].innerText.trim(),
                    major_name: columns[3].innerText.trim(),
                    lowest_score: columns[4].innerText.trim(),
                    highest_score: columns[6].innerText.trim()                     
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
                const rows = document.querySelectorAll('table#sszygradeListPlace tbody tr');
                return rows.length > 0 && rows[0].querySelectorAll('td').length >= 5;
            }''', timeout=10000)
                
        except Exception as e:
            print(f"等待表格行加载完成失败: {e}")
            raise