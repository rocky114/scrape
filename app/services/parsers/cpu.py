from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page
from app.schemas.scrape import ScrapeResonse
from app.schemas.scrape import ScrapeRequest

class PageParser(BaseParser):
    @staticmethod
    def domain() -> str:
        return "cpu.edu.cn"
    
    @staticmethod
    def name() -> str:
        return "中国药科大学"

    @staticmethod
    async def parse(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        ret: list[ScrapeResonse] = []
        """省份"""
        await page.select_option('select#sf', value=f'{request.province}')
        await page.locator("div.butt input[type='submit']").click()
        await page.wait_for_load_state("networkidle")

        while True:
            # 初始表格数据 物理类+一般录取
            items = await PageParser.parse_table(page, request)
            ret.extend(items)

            # 2. 获取当前页和总页数
            current_page = int(await page.inner_text('em.curr_page'))
            total_pages = int(await page.inner_text('em.all_pages'))

            if current_page >= total_pages:
                print(f"已经到最后一页:{current_page}")
                break
            
            await page.click("a.next")
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(1000)

        return ret
    
    @staticmethod
    async def parse_table(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        """Helper function to extract table data from the page."""

        # 步骤1：确保表格可见
        # 等待表格刷新（DOM 更新）
        await page.wait_for_selector("table.news_table:has(tbody tr)", state="attached", timeout=5000)
    
        # 步骤2：等待行数据加载
        await PageParser.wait_for_table_rows(page)

        row_data = await page.evaluate('''(request) => {
            const rows = document.querySelectorAll('table.news_table tbody tr');
            return Array.from(rows).slice(1).map(row => {
                const columns = row.querySelectorAll('td');
                let major_name = columns[0].innerText.trim();
                let admission_type = request.admission_type;
                if (major_name.includes("中外合作办学")) {
                    admission_type = "中外合作办学";                      
                } else if (major_name.includes("高校专项")) {
                    admission_type = "高校专项";             
                }
                return columns.length > 0 ? {
                    year: request.year,
                    province: request.province,
                    admission_type: admission_type,                   
                    major_name: major_name,                   
                    academic_category: columns[1].innerText.trim(),
                    lowest_score: columns[3].innerText.trim(),
                    highest_score: columns[2].innerText.trim()     
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
                const rows = document.querySelectorAll('table.news_table tbody tr');
                return rows.length > 0 && rows[0].querySelectorAll('td').length >= 5;
            }''', timeout=10000)
                
        except Exception as e:
            print(f"等待表格行加载完成失败: {e}")
            raise