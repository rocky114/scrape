from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page
from app.schemas.scrape import ScrapeResonse
from app.schemas.scrape import ScrapeRequest

class PageParser(BaseParser):
    @staticmethod
    def domain() -> str:
        return "hytc.edu.cn"
    
    @staticmethod
    def name() -> str:
        return "淮阴师范学院"

    @staticmethod
    async def click_category(page: Page, academic_category: str):
        # 使用 data-value 属性定位
        selector = f'dd#scArea4 a[data-value="{academic_category}"]'
        await page.click(selector)
        await page.wait_for_load_state("networkidle")  # 等待页面更新

    @staticmethod
    async def parse(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        ret: list[ScrapeResonse] = []

        try:
            items = await PageParser.parse_table(page, request)
            ret.extend(items)
        except Exception as e:
            print(f"解析体育(物理类)表格失败: {e}")

        try:
            await PageParser.click_category(page, "物理类")
            items = await PageParser.parse_table(page, request)
            ret.extend(items)
        except Exception as e:
            print(f"解析物理类表格失败: {e}")  

        try:
            await PageParser.click_category(page, "历史类")
            items = await PageParser.parse_table(page, request)
            ret.extend(items)
        except Exception as e:
            print(f"解析历史类表格失败: {e}") 

        try:
            await PageParser.click_category(page, "体育(历史类)")
            items = await PageParser.parse_table(page, request)
            ret.extend(items)
        except Exception as e:
            print(f"解析体育(历史类)表格失败: {e}") 

        try:
            await PageParser.click_category(page, "艺术(物理类)")
            items = await PageParser.parse_table(page, request)
            ret.extend(items)
        except Exception as e:
            print(f"解析艺术(物理类)表格失败: {e}") 

        try:
            await PageParser.click_category(page, "艺术(历史类)")
            items = await PageParser.parse_table(page, request)
            ret.extend(items)
        except Exception as e:
            print(f"解析艺术(历史类)表格失败: {e}")  

        return ret
    
    @staticmethod
    async def parse_table(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        """Helper function to extract table data from the page."""

        # 步骤1：确保表格可见
        # 等待表格刷新（DOM 更新）
        await page.wait_for_selector("table.el-table__body:has(tbody tr)", state="attached", timeout=5000)
    
        # 步骤2：等待行数据加载
        await PageParser.wait_for_table_rows(page)

        row_data = await page.evaluate('''(request) => {
            const rows = document.querySelectorAll('table.el-table__body')[0].querySelectorAll('tbody tr');
            return Array.from(rows).map(row => {
                const columns = row.querySelectorAll('td');
                return columns.length > 0 ? {
                    year: request.year,
                    province: request.province,
                    academic_category: columns[1].innerText.trim(),
                    admission_type: columns[2].innerText.trim(),
                    major_name: columns[3].innerText.trim(),                   
                    min_admission_score: columns[4].innerText.trim(),  
                    lowest_score: columns[5].innerText.trim(),
                    lowest_score_rank: columns[6].innerText.trim()   
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
                const rows = document.querySelectorAll('table.el-table__body')[0].querySelectorAll('tbody tr');
                return rows.length > 0 && rows[0].querySelectorAll('td').length >= 5;
            }''', timeout=10000)
                
        except Exception as e:
            print(f"等待表格行加载完成失败: {e}")
            raise