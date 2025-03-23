from fastapi import APIRouter
from importlib import import_module
from pathlib import Path
from app.services.parsers.base_parser import BaseParser
from fastapi.responses import JSONResponse
from app.schemas.response import ResponseModel
from app.core.browser import manager

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

@router.get("/scrape", response_model=ResponseModel)
async def scrape_data(url: str):
    browser = await manager.playwright.chromium.launch(headless=False)
    context = await browser.new_context()

    try:
        # 匹配解析器
        parser = await get_parser(url)

        page = await context.new_page()

         # 访问页面
        await page.goto(url, timeout=30000)

        # 等到dom加载完成
        await page.wait_for_load_state("domcontentloaded")

        # 匹配解析器
        parser = await get_parser(url)

         # 执行解析器
        data = await parser.parse(page)

        print(data)

        return ResponseModel(status="success", message="ok")
    finally:
        await context.close()
        await browser.close()