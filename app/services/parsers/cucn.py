from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page
from app.schemas.scrape import ScrapeResonse
from app.schemas.scrape import ScrapeRequest

class PageParser(BaseParser):
    @staticmethod
    def domain() -> str:
        return "cucn.edu.cn"
    
    @staticmethod
    def name() -> str:
        return "南京传媒学院"

    @staticmethod
    async def parse(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        ret: list[ScrapeResonse] = []

        admission_type = await page.locator('#lei option:checked').inner_text()
        province = await page.locator('#sheng option:checked').inner_text()
        
        items = await PageParser.parse_table(page, admission_type, province, request.year)
        ret.extend(items)

        await page.select_option('select#lei', label="艺术类")

        await page.locator("input[type='submit']").click()
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(1000)

        admission_type = await page.locator('#lei option:checked').inner_text()
        province = await page.locator('#sheng option:checked').inner_text()
        
        items = await PageParser.parse_table(page, admission_type, province, request.year)
        ret.extend(items)

        return ret
    
    @staticmethod
    async def parse_table(page: Page, admission_type: str, province:str, year:str) -> list[ScrapeResonse]:
        """Helper function to extract table data from the page."""

        # 步骤1：确保表格可见
        # 等待表格刷新（DOM 更新）
        await page.wait_for_selector("table:has(tbody tr)", state="attached", timeout=5000)
    
        # 步骤2：等待行数据加载
        await PageParser.wait_for_table_rows(page)

        row_data = await page.evaluate('''(request) => {
            const rows = document.querySelectorAll('table tbody tr');
            let major_name = '';                           
            return Array.from(rows).map(row => {
                let columns = row.querySelectorAll('td[rowspan]');
                if (columns.length == 1) {
                     // 提取专业组（跨行处理）
                    major_name = columns[0].innerText.trim();
                } 

                columns = row.querySelectorAll('td:not([rowspan])');
                if (columns.length == 4) {
                    return {
                        year: request.year,
                        province: request.province,
                        admission_type: request.admission_type,                   
                        major_name: columns[0].innerText.trim(),                   
                        academic_category: columns[1].innerText.trim(),
                        lowest_score: columns[3].innerText.trim(),
                        highest_score: columns[2].innerText.trim()     
                    }                    
                } else if (columns.length == 3) {
                    return {
                        year: request.year,
                        province: request.province,
                        admission_type: request.admission_type,                   
                        major_name: major_name,                   
                        academic_category: columns[0].innerText.trim(),
                        lowest_score: columns[2].innerText.trim(),
                        highest_score: columns[1].innerText.trim()     
                    }                   
                }                        
                return null;
            }).filter(item => item !== null);
        }''', {
            "year": year,
            "province": province,
            "admission_type": admission_type
        })

        return [ScrapeResonse(**item) for item in row_data]
    
    @staticmethod
    async def wait_for_table_rows(page: Page):
        """等待表格行加载完成"""
        try:
            # 条件1：等待至少1个tr存在（且列数正确）
            await page.wait_for_function('''() => {
                const rows = document.querySelectorAll('table tbody tr');
                return rows.length > 0 && rows[0].querySelectorAll('td').length >= 4;
            }''', timeout=10000)
                
        except Exception as e:
            print(f"等待表格行加载完成失败: {e}")
            raise