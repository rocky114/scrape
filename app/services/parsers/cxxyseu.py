from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page
from app.schemas.scrape import ScrapeResonse
from app.schemas.scrape import ScrapeRequest

class PageParser(BaseParser):
    @staticmethod
    def domain() -> str:
        return "cxxy.seu.edu.cn"
    
    @staticmethod
    def name() -> str:
        return "东南大学成贤学院"

    @staticmethod
    async def parse(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        ret: list[ScrapeResonse] = []

        # 1. 获取iframe的Frame对象（这才是能执行evaluate的对象）
        iframe_element = await page.wait_for_selector("iframe", state="attached", timeout=10000)
        frame = await iframe_element.content_frame()
        
        # 2. 等待iframe内容加载
        await frame.wait_for_selector("body", state="visible", timeout=15000)

        # 3. 选择年份
        await frame.click('.select2-selection')
        await frame.click(f'.select2-results__option:has-text("{request.year}")')

        # 4. 选择省份
        await frame.click(f'label:has-text("{request.province}")')

        await frame.locator("input.btnPrint").click()

        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(1000)

        # 初始表格数据 物理类+一般录取
        try:
            items = await PageParser.parse_table(frame, request=request)
            ret.extend(items)
        except Exception as e:
            print(f"解析专业录取分数表格失败: {e}")

        return ret
    
    @staticmethod
    async def parse_table(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        """Helper function to extract table data from the page."""

        await page.wait_for_selector("table.cq_resultTable:has(tbody tr)", state="attached", timeout=30000)

        row_data = await page.evaluate('''(request) => {
            const rows = document.querySelector('table.cq_resultTable').querySelectorAll('tbody tr');
            return Array.from(rows).slice(1).map(row => {
                const columns = row.querySelectorAll('td');
                return columns.length > 0 ? {
                    year: columns[0].innerText.trim(),
                    province: columns[1].innerText.trim(),
                    admission_type: request.admission_type,
                    academic_category: columns[3].innerText.trim(),
                    major_name: columns[4].innerText.trim(),                        
                    highest_score: columns[5].innerText.trim(),
                    lowest_score: columns[6].innerText.trim()
                } : null;
            }).filter(item => item !== null);
        }''', {
            "admission_type": request.admission_type 
        })

        return [ScrapeResonse(**item) for item in row_data]
    
