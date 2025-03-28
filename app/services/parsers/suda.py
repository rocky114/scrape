from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page
from app.schemas.scrape import ScrapeResonse
from app.schemas.scrape import ScrapeRequest

class NJUParser(BaseParser):
    @staticmethod
    def domain() -> str:
        return "zsb.suda.edu.cn"
    
    @staticmethod
    def name() -> str:
        return "苏州大学"

    @staticmethod
    async def parse(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        ret: list[ScrapeResonse] = []

        # 初始表格数据 物理类+一般录取
        try:
            items = await NJUParser.parse_table(page, request=request)
            ret.extend(items)
        except Exception as e:
            print(f"解析专业录取分数表格失败: {e}")

        return ret
    
    @staticmethod
    async def parse_table(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        """Helper function to extract table data from the page."""

        # 步骤1：确保表格可见
        # 等待表格刷新（DOM 更新）
        await page.wait_for_selector("table#ctl00_ContentPlaceHolder1_GridView1:has(tbody tr)", state="attached")

        row_data = await page.evaluate('''(request) => {
            const rows = document.querySelectorAll('table#ctl00_ContentPlaceHolder1_GridView1 tbody tr');
            return Array.from(rows).slice(1).map(row => {
                console.log(row.outerHTML)                       
                const columns = row.querySelectorAll('td');
                return columns.length > 0 ? {
                    year: request.year,
                    province: request.province,
                    major_name: columns[0].innerText.trim(),              
                    academic_category: columns[2].innerText.trim(),
                    admission_type: request.admission_type,                  
                    highest_score: columns[3].innerText.trim(),
                    lowest_score: columns[4].innerText.trim()     
                } : null;
            }).filter(item => item !== null);
        }''', {
            "year": request.year,
            "province": request.province,
            "admission_type": request.admission_type 
        })

        return [ScrapeResonse(**item) for item in row_data]
    
