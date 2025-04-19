from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page
from app.schemas.scrape import ScrapeResonse
from app.schemas.scrape import ScrapeRequest

class NJUParser(BaseParser):
    @staticmethod
    def domain() -> str:
        return "zs.just.edu.cn"
    
    @staticmethod
    def name() -> str:
        return "江苏科技大学"

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
        await page.wait_for_selector("table:has(tbody tr)", state="attached")

        row_data = await page.evaluate('''(request) => {                      
            const rows = document.querySelectorAll('table tbody tr');
            let academic_category = "";
            return Array.from(rows).slice(1).map(row => {
                const columns = row.querySelectorAll('td');
                if (columns.length < 5) {
                    return null;                    
                }
                let title = columns[1].innerText.trim();
                if (title.includes('江苏科技大学')) {
                    academic_category = title.match(/[（(](.+?)[）)]/)?.[1]; // 匹配第一个括号内容                    
                    return null;                                  
                }
                                                                                  
                return {
                    year: request.year,
                    province: request.province,
                    admission_type: request.admission_type,
                    academic_category: academic_category,
                    major_name: columns[1].innerText.trim(), 
                    highest_score: columns[4].innerText.trim(),
                    lowest_score: columns[5].innerText.trim(), 
                    lowest_score_rank: columns[7].innerText.trim()  
                };
            }).filter(item => item !== null);
        }''', {
            "year": request.year,
            "province": request.province,
            "admission_type": request.admission_type 
        })

        return [ScrapeResonse(**item) for item in row_data]
    
