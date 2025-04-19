from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page
from app.schemas.scrape import ScrapeResonse
from app.schemas.scrape import ScrapeRequest
import pandas as pd

class NJUParser(BaseParser):
    @staticmethod
    def domain() -> str:
        return "zs.njupt.edu.cn"
    
    @staticmethod
    def name() -> str:
        return "南京邮电大学"

    @staticmethod
    async def parse(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        ret: list[ScrapeResonse] = []

        try:
            newest_link = page.locator("ul.news_list li:first-child a")

            await newest_link.wait_for(state="attached")
            
            async with page.expect_download() as download_info:
                await newest_link.click()

            download = await download_info.value

            await download.save_as(download.suggested_filename)

            df = pd.read_excel(
                download.suggested_filename,
                header=None,
                skiprows=2,
                names=["批次", "选考科目", "专业名称", "人数", "最高分", "最低分", "平均分"],
                keep_default_na=False,
                sheet_name=f"{request.province}",
                engine="openpyxl",
                dtype=str
            )

            current_admission_type = ""
            current_academic_category = ""

            for _, row in df.iterrows():
                if row["批次"] != "":
                    current_admission_type = row["批次"]

                if row.get("选考科目", "") != "":
                    current_academic_category = row["选考科目"]

                ret.append(ScrapeResonse(
                    province=request.province,
                    year=request.year,
                    admission_type=current_admission_type,
                    academic_category=current_academic_category,
                    major_name=row["专业名称"],
                    enrollment_quota=row["人数"],
                    highest_score=row["最高分"],
                    lowest_score=row["最低分"]
                ))
        except Exception as e:
            print(f"解析表格失败: {e}")   

            raise

        return ret