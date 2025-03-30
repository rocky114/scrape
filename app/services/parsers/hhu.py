from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page
from app.schemas.scrape import ScrapeResonse
from app.schemas.scrape import ScrapeRequest
import urllib.parse

class NJUParser(BaseParser):
    @staticmethod
    def domain() -> str:
        return "zsw.hhu.edu.cn"
    
    @staticmethod
    def name() -> str:
        return "河海大学"

    @staticmethod
    async def parse(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        ret: list[ScrapeResonse] = []

        # 初始表格数据 物理类+一般录取
        try:
            await page.locator("div.lsfscxDiv div.title").wait_for(state="attached")

            params = {
                'province': f'{request.province}',
                'year': f'{request.year}'
            }
            encoded_params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)

            # 3. 发送POST请求
            response = await page.request.post(
                'https://zsw.hhu.edu.cn/api/lsfs/fsList',
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Origin': 'https://zsw.hhu.edu.cn',
                    'Referer': 'https://zsw.hhu.edu.cn/lishifenshu.html',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                data=encoded_params
            )

            if response.status != 200:
                raise ValueError(f"HTTP {response.status}: {await response.text()}")    

            data = await response.json()
            rows = data.get("data", [])

            for row in rows:
                if row["major"] == "投档线":
                    continue

                ret.append(ScrapeResonse(
                    province=row["province"], 
                    year=request.year,
                    admission_type=row["type"],
                    academic_category=row["discipline"],
                    major_name=row["major"], 
                    min_admission_score=str(row["filescore"]),
                    highest_score=str(row["highestscore"]),
                    )
                )
            
        except Exception as e:
            print(f"解析专业录取分数表格失败: {e}")
            raise

        return ret
    
    