from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page
from app.schemas.scrape import ScrapeResonse
from app.schemas.scrape import ScrapeRequest
import urllib.parse

class NJUParser(BaseParser):
    @staticmethod
    def domain() -> str:
        return "zs.cumt.edu.cn"
    
    @staticmethod
    def name() -> str:
        return "中国矿业大学"

    @staticmethod
    async def parse(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        ret: list[ScrapeResonse] = []

        # 初始表格数据 物理类+一般录取
        try:
            params = {
                "filter_column": f'{{"A":"{request.province}", "B":"{request.year}"}}',       
                "sch_school_id": 18907,
                "page": 1,
                "page_size": 100          
            }
            encoded_params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
            api_url = f"https://job-web-api.jobpi.cn/enroll/501?{encoded_params}"
            print(f"url: {api_url}")
            
            headers = {
                'Referer': 'https://zs.cumt.edu.cn'
            }
            response = await page.request.get(api_url, headers=headers)

            if response.status != 200:
                raise ValueError(f"HTTP {response.status}: {await response.text()}")    

            data = await response.json()
            rows = data.get("data", []).get("list", [])

            for row in rows:
                ret.append(ScrapeResonse(
                    province=row["A"], 
                    year=row["B"],
                    admission_type=row["C"],
                    academic_category=row["D"],
                    major_name=row["F"], 
                    lowest_score=row["G"],
                    lowest_score_rank=row["H"]
                    )
                )
            
        except Exception as e:
            print(f"解析专业录取分数表格失败: {e}")

        return ret
    
    