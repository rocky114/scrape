from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page

class NJParser(BaseParser):
    @staticmethod
    def domain() -> str:
        return "bkzs.nju.edu.cn"
    

    @staticmethod
    async def parse(page: Page) -> dict:
        await page.wait_for_selector("#zsSsgradeListPlace")

        rows = await page.query_selector_all(".score-table tr")
        scores = []
        for row in rows:
            text = await row.inner_text()
            scores.append(text.strip())

        return {
            "uuniversity": "南京大学",
            "scores": scores,
        }