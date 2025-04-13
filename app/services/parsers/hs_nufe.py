from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page
from app.schemas.scrape import ScrapeResonse
from app.schemas.scrape import ScrapeRequest
import pandas as pd

class NJUParser(BaseParser):
    @staticmethod
    def domain() -> str:
        return ""
    
    @staticmethod
    def name() -> str:
        return "南京财经大学红山学院"

    @staticmethod
    async def parse(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        ret: list[ScrapeResonse] = []

        try:
            newest_link = page.locator("ul.wp_article_list li:first-child a")

            await newest_link.wait_for(state="attached")
            
            async with page.expect_download() as download_info:
                await newest_link.click()

            download = await download_info.value

            await download.save_as(download.suggested_filename)

            df = pd.read_excel(
                download.suggested_filename,
                header=None,
                skiprows=2,
                #names=["批次", "选考科目", "专业名称", "人数", "最高分", "最低分", "平均分"],
                keep_default_na=False,
                # sheet_name="",
                engine="openpyxl",
                dtype=str
            )

            academic_category_1 = ""
            academic_category_2 = ""
            admission_type = ""

            result = df.iloc[:, [0,1,2]]

            for _, row in result.iterrows():
                if row[0] == "专业":
                    academic_category_1 = row[1]
                    academic_category_2 = row[2]
                elif row[0] == "批次":
                    admission_type = row[1]
                elif row[0] in ["二本省控线", "本科线", "校控线"]:
                    continue
                else:
                    ret.append(ScrapeResonse(
                        province=request.province,
                        year=request.year,
                        admission_type=admission_type,
                        academic_category=academic_category_1,
                        major_name=row[0],
                        lowest_score=row[1]
                    ))
                    ret.append(ScrapeResonse(
                        province=request.province,
                        year=request.year,
                        admission_type=admission_type,
                        academic_category=academic_category_2,
                        major_name=row[0],
                        lowest_score=row[2]
                    ))
        except Exception as e:
            print(f"解析表格失败: {e}")   

            raise

        return ret