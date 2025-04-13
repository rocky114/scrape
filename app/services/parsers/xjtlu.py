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
        return "西交利物浦大学"

    @staticmethod
    async def parse(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        ret: list[ScrapeResonse] = []

        # 1. 定位"江苏省"按钮，获取动态ID
        jiangsu_button = page.locator(f'button.accordion-button:has-text("{request.province}")')
        target_id = await jiangsu_button.get_attribute("data-bs-target")  # 获取类似 "#collapsetwenty-one15-Vd6PW1N6Qg" 的值

        items = await PageParser.parse_table(page, request.year, request.province, request.admission_type, target_id)
        ret.extend(items)

        return ret
    
    @staticmethod
    async def parse_table(page: Page, year:str, province:str, admission_type:str, target_id:str) -> list[ScrapeResonse]:
        # 步骤1：确保表格可见
        # 等待表格刷新（DOM 更新）
        await page.wait_for_selector(f"{target_id} table:has(tbody tr)", state="attached", timeout=5000)
    
        # 步骤2：等待行数据加载
        # await PageParser.wait_for_table_rows(page)

        row_data = await page.evaluate('''(request) => {
            const rows = document.querySelectorAll(`${request.target_id} table tbody tr`);
                           
            return Array.from(rows).slice(1).map(row => {
                let columns = row.querySelectorAll('td:not([rowspan])');
                
                return columns.length > 0 ? {
                    year: request.year,
                    province: request.province,
                    admission_type: request.admission_type,
                    enrollment_quota: columns[3].innerText.trim(),                                      
                    major_name: columns[1].innerText.trim(),                   
                    academic_category: columns[0].innerText.trim().match(/[（(](.+?)[）)]/)?.[1],
                    lowest_score: columns[6].innerText.trim(),
                    highest_score: columns[4].innerText.trim()
                } : null;
            }).filter(item => item !== null);
        }''', {
            "year": year,
            "province": province,
            "admission_type": admission_type,
            "target_id": target_id
        })

        return [ScrapeResonse(**item) for item in row_data]
    
    @staticmethod
    async def wait_for_table_rows(page: Page):
        """等待表格行加载完成"""
        try:
            # 条件1：等待至少1个tr存在（且列数正确）
            await page.wait_for_function('''() => {
                const rows = document.querySelectorAll('table.el-table__body tbody tr');
                return rows.length > 0 && rows[0].querySelectorAll('td').length >= 4;
            }''', timeout=10000)
                
        except Exception as e:
            print(f"等待表格行加载完成失败: {e}")
            raise