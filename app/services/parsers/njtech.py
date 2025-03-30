from app.services.parsers.base_parser import BaseParser
from playwright.async_api import Page
from app.schemas.scrape import ScrapeResonse
from app.schemas.scrape import ScrapeRequest
import pytesseract
from PIL import Image
import io

class NJUParser(BaseParser):
    @staticmethod
    def domain() -> str:
        return "zhaosheng.njtech.edu.cn"
    
    @staticmethod
    def name() -> str:
        return "南京工业大学"

    @staticmethod
    async def parse(page: Page, request: ScrapeRequest) -> list[ScrapeResonse]:
        ret: list[ScrapeResonse] = []

        # 初始表格数据 物理类+一般录取
        try:
            # 2. 等待图片元素加载（增强稳定性）
            img_locator = page.locator("div.content-box img")
            await img_locator.wait_for(state="attached")  # 10秒超时

            raise ConnectionError(f"图片OCR暂未实现, 请等待...")


            # 3. 获取图片URL（处理可能的相对路径）
            """
            img_url = await img_locator.get_attribute("src")
            if not img_url:
                raise ValueError("未找到图片URL")
            
            response = await page.request.get(img_url)
            if response.status != 200:
                raise ConnectionError(f"图片下载失败，状态码: {response.status}")
            
            img = Image.open(io.BytesIO(await response.body()))
            # 使用Tesseract OCR识别文字
            text = pytesseract.image_to_string(img)
            print(text)"
            """
        except Exception as e:
            print(f"解析专业录取分数表格失败: {e}")

        return ret