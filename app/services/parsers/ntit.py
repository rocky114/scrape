from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page
from app.schemas.scrape import ScrapeResonse
from app.schemas.scrape import ScrapeRequest

class PageParser(BaseParser):
    @staticmethod
    def domain() -> str:
        return "ntit.edu.cn"
    
    @staticmethod
    def name() -> str:
        return "南通理工学院"

    @staticmethod
    async def parse(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        ret: list[ScrapeResonse] = []

        try:
            items = await PageParser.parse_table(page, request)
            ret.extend(items)
        except Exception as e:
            print(f"表格失败: {e}")

        return ret
    
    @staticmethod
    async def parse_table(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        """Helper function to extract table data from the page."""

        # 步骤1：确保表格可见
        # 等待表格刷新（DOM 更新）
        await page.wait_for_selector("table.MsoNormalTable:has(tbody tr)", state="attached", timeout=5000)
    
        # 步骤2：等待行数据加载
        # await PageParser.wait_for_table_rows(page)

        row_data = await page.evaluate('''(request) => {
            const rows = document.querySelectorAll('table.MsoNormalTable tbody tr');
            const result = [];

            let academicCategory = '';
            let minAdmissionScore = '';
                                                                                                                        
            return Array.from(rows).slice(1).map(row => {
                let columns = row.querySelectorAll('td[rowspan]');
                // 提取批次（跨行处理）
                if (columns.length == 3) {
                     // 提取专业组（跨行处理）
                    academicCategory = columns[0].innerText.trim().match(/[（(](.+?)[）)]/)?.[1];
                    
                    // 提取省控线（跨行处理）
                    minAdmissionScore = columns[2].innerText.trim(); 
                } else if (columns.length == 2) {
                    // 提取专业组（跨行处理）
                    academicCategory = columns[0].innerText.trim().match(/[（(](.+?)[）)]/)?.[1];
                    
                    // 提取省控线（跨行处理）
                    minAdmissionScore = columns[1].innerText.trim();                   
                }

                columns = row.querySelectorAll('td:not([rowspan])');                                            
                if (columns.length == 4) {
                    return {
                            year: request.year,
                            province: request.province,
                            admission_type: request.admission_type,
                            academic_category: academicCategory,                   
                            major_name: columns[1].innerText.trim(),
                            highest_score: columns[2].innerText.trim(),
                            lowest_score: columns[3].innerText.trim(),                                                                            
                            min_admission_score: minAdmissionScore
                        };
                } else if (columns.length == 7) {
                    return {
                            year: request.year,
                            province: request.province,
                            admission_type: request.admission_type,
                            academic_category: columns[1].innerText.trim().match(/[（(](.+?)[）)]/)?.[1],                   
                            major_name: columns[2].innerText.trim(),
                            highest_score: columns[5].innerText.trim(),
                            lowest_score: columns[6].innerText.trim(),                                                                            
                            min_admission_score: columns[4].innerText.trim()
                        };                
                }
            }).filter(item => item !== null);
        }''', {
            "year": request.year,
            "province": request.province,
            "admission_type": request.admission_type
        })

        print(f"{row_data}")
        page.wait_for_timeout(30)
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