from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page
from app.schemas.scrape import ScrapeResonse
from app.schemas.scrape import ScrapeRequest
import urllib.parse

class NJUParser(BaseParser):
    @staticmethod
    def domain() -> str:
        return ""
    
    @staticmethod
    def name() -> str:
        return "南京林业大学"

    @staticmethod
    async def parse(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        ret: list[ScrapeResonse] = []

        # 初始表格数据 物理类+一般录取
        try:
            params = {
                "year": request.year,       
                "provinceName": request.province,
                "kind": ''          
            }
            encoded_params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
            api_url = f"https://lqcx.njfu.edu.cn/enrollment/open/scoreList?{encoded_params}"
            
            headers = {
                'Referer': 'https://lqcx.njfu.edu.cn/page/data.html',
                'X-Requested-With': 'XMLHttpRequest' 
            }
            response = await page.request.get(api_url, headers=headers)
            if response.status != 200:
                raise ValueError(f"HTTP {response.status}: {await response.text()}")    

            data = await response.json()
            rows = data.get("data", [])

            for row in rows:
                admission_type = row.get('batch', '普通了')
                if '本科' in admission_type:
                    admission_type = '普通类'
                elif '艺术' in admission_type:
                    admission_type = '艺术类'

                subject_category = row.get('kind', '物理类')
                if '物理' in subject_category:
                    subject_category = '物理类'
                elif '历史' in subject_category:
                    subject_category = '历史类'
                elif '艺术' in subject_category:
                    if '淮安校区' in row.get('majorName', ''):
                        subject_category = '历史类'
                    else:
                        subject_category = '物理类'
                    
                ret.append(ScrapeResonse(
                    year=row.get('year', request.year),
                    province=request.province, 
                    major_name=row.get('majorName', ''), 
                    admission_type=admission_type, 
                    subject_category=subject_category,
                    lowest_score=row.get('minScore', ''),
                    highest_score=row.get('maxScore', '')
                    )
                )
            
        except Exception as e:
            print(f"解析专业录取分数表格失败: {e}")

        return ret
    
    