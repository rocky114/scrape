// 创建虚拟环境
python -m venv .venv

// 激活虚拟环境
source .venv/bin/activate

// 退出虚拟环境
deactivate

// 安装playwright
pip install playwright

// 安装chrome
playwright install chromium

// 安装chromium依赖
playwright install-deps chromium

// 安装api框架
pip install fastapi

// 安装wsgi服务
pip install "uvicorn[standard]"

// 生成依赖包requirements
pip freeze > requirements.txt

// 启动
uvicorn app.main:app --reload