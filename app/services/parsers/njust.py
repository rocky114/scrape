from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page
from app.schemas.scrape import ScrapeResonse
from app.schemas.scrape import ScrapeRequest
import urllib.parse

class NJUParser(BaseParser):
    @staticmethod
    def domain() -> str:
        return "zsb.njust.edu.cn"
    
    @staticmethod
    def name() -> str:
        return "南京理工大学"

    @staticmethod
    async def parse(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        ret: list[ScrapeResonse] = []

        # 初始表格数据 物理类+一般录取
        try:
            params = {
                "pageSize": 100,       
                "rowoffset": 0,
                "val1": request.province          
            }
            encoded_params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
            api_url = f"https://zsb.njust.edu.cn/lqScore/initDateWebCon?{encoded_params}"
            
            headers = {
                'Referer': 'https://zsb.njust.edu.cn/lqjh_fsx',
                'X-Requested-With': 'XMLHttpRequest' 
            }
            response = await page.request.get(api_url, headers=headers)

            if response.status != 200:
                raise ValueError(f"HTTP {response.status}: {await response.text()}")    

            data = await response.json()
            rows = data.get("rows", [])

            for row in rows:
                ret.append(ScrapeResonse(
                    year=request.year,
                    province=row["province"], 
                    major_name=row["professional_name"], 
                    admission_type=row["class_name"], 
                    lowest_score=row["year3"]
                    )
                )
            
        except Exception as e:
            print(f"解析专业录取分数表格失败: {e}")

        return ret
    
    