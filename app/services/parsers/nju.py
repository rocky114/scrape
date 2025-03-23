from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page
from app.schemas.scrape import ScrapeResonse

class NJParser(BaseParser):
    @staticmethod
    def domain() -> str:
        return "bkzs.nju.edu.cn"
    
    @staticmethod
    def name() -> str:
        return "南京大学"

    @staticmethod
    async def parse(page: Page) -> list[ScrapeResonse]:
        items = await page.evaluate('''() => {
                const rows = document.querySelectorAll('table.table_1 tbody tr');
                const data = [];
                rows.forEach(row => {
                    const columns = row.querySelectorAll('td');
                    if (columns.length > 0) {
                        data.push({
                            year: columns[0].innerText.trim(),
                            province: columns[1].innerText.trim(),
                            academic_category: columns[2].innerText.trim(),
                            type: columns[3].innerText.trim(),
                            minimum_score: columns[4].innerText.trim()     
                        });
                    }
                });

                return data;             
        }''')

        for item in items:
            print(item)

        return []