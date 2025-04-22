from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page
from app.schemas.scrape import ScrapeResonse
from app.schemas.scrape import ScrapeRequest
import pandas as pd

class NJUParser(BaseParser):
    @staticmethod
    def domain() -> str:
        return "jjxy.ujs.edu.cn"
    
    @staticmethod
    def name() -> str:
        return "江苏大学京江学院"

    @staticmethod
    async def parse(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        ret: list[ScrapeResonse] = []

        try:
            newest_link = page.locator("div.v_news_content a")

            await newest_link.wait_for(state="attached")
            
            async with page.expect_download() as download_info:
                await newest_link.click()

            download = await download_info.value

            await download.save_as(download.suggested_filename)

            df = pd.read_excel(
                download.suggested_filename,
                header=None,
                skiprows=2,
                names=["专业名称", "计划数", "人数", "最高分", "最低分", "平均分"],
                keep_default_na=False,
                sheet_name="Sheet1",
                engine="openpyxl",
                dtype=str
            )

            academic_category_list: list[str] = []
            for _, row in df.iterrows():
                text = row.get("专业名称", "")
                if "总计" in text:
                    academic_category_list.append(text.split("总计")[0])

            i = 0
            for _, row in df.iterrows():
                major_name = row.get("专业名称", "")
                if "总计" in major_name:
                    i = i + 1
                    continue
                
                admission_type = request.admission_type
                if "艺术" in academic_category_list[i]:
                    admission_type = "艺术类"

                ret.append(ScrapeResonse(
                    province=request.province,
                    year=request.year,
                    admission_type=admission_type,
                    academic_category=academic_category_list[i],
                    major_name=major_name,
                    enrollment_quota=row["人数"],
                    highest_score=row["最高分"],
                    lowest_score=row["最低分"]
                ))
        except Exception as e:
            print(f"解析表格失败: {e}")   

            raise

        return ret