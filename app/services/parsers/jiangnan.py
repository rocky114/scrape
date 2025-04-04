from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page
from app.schemas.scrape import ScrapeResonse
from app.schemas.scrape import ScrapeRequest

class PageParser(BaseParser):
    @staticmethod
    def domain() -> str:
        return "jiangnan.edu.cn"
    
    @staticmethod
    def name() -> str:
        return "江南大学"

    @staticmethod
    async def parse(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        ret: list[ScrapeResonse] = []
        """物理类"""
        try:
            items = await PageParser.parse_table(page, request)
            ret.extend(items)
        except Exception as e:
            print(f"解析物理类+普通类取表格失败: {e}")

        try:
            await page.click('span.tag >> text="高校专项计划"')

            items = await PageParser.parse_table(page, request)

            ret.extend(items)
        except Exception as e:
            print(f"解析物理类+高校专项计划表格失败: {e}")   

        try:
            await page.click('span.tag >> text="中外合作办学"')

            items = await PageParser.parse_table(page, request)

            ret.extend(items)
        except Exception as e:
            print(f"解析物理类+中外合作办学表格失败: {e}") 

        """历史类"""
        try:
            await page.click('span.tag >> text="历史类"')

            items = await PageParser.parse_table(page, request)

            ret.extend(items)
        except Exception as e:
            print(f"解析历史类+普通类学表格失败: {e}") 

        try:
            await page.click('span.tag >> text="中外合作办学"')

            items = await PageParser.parse_table(page, request)

            ret.extend(items)
        except Exception as e:
            print(f"解析历史类+中外合作办学表格失败: {e}") 

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
            const rows = document.querySelectorAll('table.el-table__body')[1].querySelectorAll('tbody tr');
            return Array.from(rows).map(row => {
                const columns = row.querySelectorAll('td');
                return columns.length > 0 ? {
                    year: request.year,
                    province: request.province,
                    admission_type: request.admission_type,
                    major_name: columns[0].innerText.trim(),
                    academic_category: columns[1].innerText.trim(),
                    enrollment_quota: columns[2].innerText.trim(),
                    highest_score: columns[3].innerText.trim(),                                                                            
                    lowest_score: columns[4].innerText.trim(),
                    lowest_score_rank: columns[5].innerText.trim()                        
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
                const rows = document.querySelectorAll('table.el-table__body')[1].querySelectorAll('tbody tr');
                return rows.length > 0 && rows[0].querySelectorAll('td').length >= 5;
            }''', timeout=10000)
                
        except Exception as e:
            print(f"等待表格行加载完成失败: {e}")
            raise