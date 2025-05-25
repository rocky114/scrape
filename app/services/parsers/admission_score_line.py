from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page
from app.schemas.scrape import ScrapeResonse
from app.schemas.scrape import ScrapeRequest
import pandas as pd
import re

class PageParser(BaseParser):
    @staticmethod
    def domain() -> str:
        return ""
    
    @staticmethod
    def name() -> str:
        return "投档线"

    @staticmethod
    async def parse(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        ret: list[ScrapeResonse] = []

        try:
            links = await page.locator("#content a").all()
            for item in links:
                title = await item.inner_text()
                async with page.expect_download() as download_info:
                    await item.click()

                download = await download_info.value
                await download.save_as(download.suggested_filename)

                df = pd.read_excel(
                    download.suggested_filename,
                    header=5,
                    usecols=[1, 2, 3],
                    names=["university", "lowest_score", "admission_region"],
                    keep_default_na=False,
                    sheet_name="投档线",
                    engine="xlrd",
                    dtype=str
                ).dropna(how="all")

                subject_admission_dict = PageParser.extract_subject_admission_type_info(title)
                admission_type = subject_admission_dict.get("admission_type", "")
                admission_batch = subject_admission_dict.get("admission_batch", "")
                subject_category = subject_admission_dict.get("subject_category", "")

                # if admission_type not in ["军队", "公安政法", "航海", "地方专项计划", "乡村教师计划", "医学定向"]:
                    # admission_type = "普通类"

                for _, row in df.iterrows():
                    if not row["university"]:
                        continue

                    university_dict = PageParser.extract_university_major_subject_info(row["university"])
                    
                    university_name = university_dict.get("university", "")
                    major_group = university_dict.get("major_group", "")
                    second_subject_category = university_dict.get("subject", "")

                    lowest_score = row['lowest_score']
                    admission_region = ''
                    if '县' in lowest_score or '区' in lowest_score or '市' in lowest_score:
                        lowest_score = row['admission_region']
                        admission_region = row['lowest_score']
                            

                    ret.append(ScrapeResonse(
                        province=request.province, 
                        year=request.year,
                        admission_type=admission_type,
                        admission_batch=admission_batch,
                        admission_region=admission_region,
                        subject_category=f"{subject_category}{second_subject_category}",
                        major_group=major_group, 
                        university_name=university_name,
                        lowest_score=lowest_score,
                        )
                    )
        except Exception as e:
            print(f"解析表格失败: {e}")   
            raise

        return ret
    
    # 提取 院校, 专业组, 选考科目
    @staticmethod
    def extract_university_major_subject_info(text) -> dict[str, str]:
        pattern = r'([^\d]+)(\d+专业组)(\([^)]+\))(\([^)]+\))?'
        match = re.search(pattern, text)
        if not match:
            return {}
        
        college = match.group(1).strip()
        group = match.group(2)
        subject = match.group(3)
        
        # 拼接第二个括号内容到专业组后面
        if match.group(4):
            group += match.group(4)
        
        return {
            'university': college,
            'major_group': group,
            'subject': subject
        }

    @staticmethod        
    def extract_subject_admission_type_info(text) -> dict[str, str]:
        pattern = r"[（(](.*?)[）)]"  # 匹配括号内的内容（包括中文和英文括号）
        match = re.search(pattern, text)
        if not match:
            return {}
        
        content = match.group(1)  # "物理等科目类—其他院校"
        category, admission_type = content.split("—")
        category = category.replace("等科目类", "")

        admissin_batch = ""
        if "提前批" in text:
            admissin_batch = "提前批"
        elif "本科批" in text:
            admissin_batch = "本科批"
        elif "专科批" in text:
            admissin_batch = "专科批"

        return {
            "admission_type": admission_type,
            "admission_batch": admissin_batch,
            "subject_category": category
        }
