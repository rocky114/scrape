from fastapi import APIRouter
from importlib import import_module
from pathlib import Path
from app.services.parsers.base_parser import BaseParser
from fastapi.responses import JSONResponse
from app.schemas.response import ResponseModel
from app.core.browser import manager
from app.schemas.scrape import ScrapeResonse
from app.schemas.scrape import ScrapeRequest

router = APIRouter()

# 动态加载所有解析器
def load_parsers():
    parse_dir = Path(__file__).parent.parent.parent / "services/parsers"
    modules = [f.stem for f in parse_dir.glob("*.py") if f.is_file() and f.stem != "__init__"]
    parsers = []
    for module in modules:
        mod = import_module(f"app.services.parsers.{module}")
        for attr in dir(mod):
            cls = getattr(mod, attr)
            try:
                if issubclass(cls, BaseParser) and cls != BaseParser:
                    parsers.append(cls)
            except TypeError:
                continue

    return parsers    

async def get_parser(url: str) -> BaseParser:
    for parser in load_parsers():
        if parser.match(url):
            return parser
        
    raise ValueError("No parser available for this URL")

@router.post("/scrape", response_model=ResponseModel[list[ScrapeResonse]])
async def scrape_data(request: ScrapeRequest):
    browser = await manager.playwright.chromium.launch(headless=False, slow_mo=500)
    
    try:
        # 匹配解析器
        parser = await get_parser(request.url)

        page = await browser.new_page()

         # 访问页面
        await page.goto(request.url, timeout=30000)

        # 等到dom加载完成
        await page.wait_for_load_state("domcontentloaded")

         # 执行解析器
        items = await parser.parse(page, request=request)

        return ResponseModel(status="success", data=items, message="ok")
    except Exception as e:
        return ResponseModel(status="error", message=f"occur err: {e}")
    finally:
        await browser.close()