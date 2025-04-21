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
        return "南京工业职业技术大学"

    @staticmethod
    async def parse(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        ret: list[ScrapeResonse] = []
        
        items = await PageParser.parse_table(page, request)
        ret.extend(items)

        return ret
    
    @staticmethod
    async def parse_table(page: Page, request:ScrapeRequest) -> list[ScrapeResonse]:
        # 步骤1：确保表格可见
        # 等待表格刷新（DOM 更新）
        await page.wait_for_selector("table:has(tbody tr)", state="attached", timeout=5000)
    
        # 步骤2：等待行数据加载
        # await PageParser.wait_for_table_rows(page)

        row_data = await page.evaluate('''(request) => {
            const rows = document.querySelectorAll('table tbody tr');
            let academic_category = '';  
            let admission_type = '';                         
            return Array.from(rows).slice(1).map(row => {
                let columns = row.querySelectorAll('td[rowspan]');
                // 提取批次（跨行处理）
                if (columns.length == 1) {
                    academic_category = columns[0].innerText.trim().split("首选")[1] ?? "";
                    admission_type = columns[0].innerText.trim();          
                } 

                columns = row.querySelectorAll('td:not([rowspan])');                         
                return columns.length > 0 ? {
                    year: request.year,
                    province: request.province,
                    admission_type: admission_type,                   
                    major_name: columns[0].innerText.trim(),                   
                    academic_category: academic_category,
                    lowest_score: columns[1].innerText.trim(),
                    lowest_score_rank: columns[2].innerText.trim()     
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
                const rows = document.querySelectorAll('table tbody tr');
                return rows.length > 0 && rows[0].querySelectorAll('td').length >= 4;
            }''', timeout=10000)
                
        except Exception as e:
            print(f"等待表格行加载完成失败: {e}")
            raise