# 从零开始：获取并运行一个 Python 项目

> 你在网上找到一个优秀的 Python 项目，想在自己的机器上跑起来。本章覆盖从"看到项目"到"成功运行"的完整流程：克隆代码、创建虚拟环境、安装依赖、配置环境变量、运行项目。

---

## 一、总体流程

```
找到项目 (GitHub/PyPI)
    ↓
克隆或下载代码
    ↓
创建虚拟环境 (隔离依赖)
    ↓
安装依赖 (pip install)
    ↓
配置环境 (环境变量/.env)
    ↓
运行项目
```

---

## 二、获取项目代码

### 2.1 从 GitHub 克隆

```bash
# 基本克隆
git clone https://github.com/user/project.git
cd project

# 只克隆某个分支（节省时间）
git clone -b main --depth 1 https://github.com/user/project.git

# 克隆后查看项目结构
ls -la
```

### 2.2 从 PyPI 安装（无需克隆）

```bash
# 如果项目已发布到 PyPI，直接安装即可
pip install httpx
pip install rich
pip install fastapi[all]  # 带可选依赖

# 查看已安装包的信息
pip show httpx
```

### 2.3 阅读 README

任何项目的第一步都是读 README。重点关注：

```bash
# 通常包含以下信息
cat README.md

# 重点找：
# 1. 安装要求 (Python 版本、系统依赖)
# 2. 安装命令 (pip install -r requirements.txt)
# 3. 运行方式 (python main.py)
# 4. 配置说明 (.env 文件、环境变量)
```

---

## 三、创建虚拟环境

> **为什么必须创建虚拟环境？** 不同项目可能需要不同版本的依赖。全局安装会导致版本冲突——项目 A 需要 `requests==2.28`，项目 B 需要 `requests==2.31`，两者不可调和。虚拟环境让每个项目拥有独立的依赖空间。

### 3.1 用 venv 创建（Python 内置）

```bash
# 进入项目目录后创建虚拟环境
cd project/
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows (PowerShell)

# 激活后命令行前会出现 (.venv) 标记
(.venv) $ python --version
(.venv) $ pip --version

# 退出虚拟环境
deactivate
```

### 3.2 用 uv 创建（推荐，更快）

```bash
# 安装 uv（如果没有）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境
uv venv

# 激活
source .venv/bin/activate

# uv 也可以直接管理依赖（替代 pip）
uv pip install -r requirements.txt
```

### 3.3 将 .venv 加入 .gitignore

```bash
# 虚拟环境不应提交到 Git
echo '.venv/' >> .gitignore
echo '__pycache__/' >> .gitignore
echo '*.pyc' >> .gitignore
git add .gitignore
git commit -m "Add .gitignore for Python project"
```

---

## 四、安装依赖

### 4.1 根据 requirements.txt 安装

```bash
# 确保虚拟环境已激活
source .venv/bin/activate

# 一键安装所有依赖
pip install -r requirements.txt

# 如果下载慢，使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或永久配置镜像
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4.2 根据 pyproject.toml 安装

```bash
# 现代项目通常用 pyproject.toml
pip install .

# 开发模式安装（修改代码后无需重新安装）
pip install -e .

# 带可选依赖安装
pip install ".[dev]"
pip install ".[test,docs]"
```

### 4.3 从 Git 安装（项目未发布到 PyPI）

```bash
# 直接从 GitHub 安装
pip install git+https://github.com/user/project.git

# 安装特定分支
pip install git+https://github.com/user/project.git@main

# 安装特定版本
pip install git+https://github.com/user/project.git@v1.2.3
```

### 4.4 安装本地项目

```bash
# 安装当前目录
pip install .

# 开发模式（推荐开发时使用）
pip install -e .

# 从 wheel 文件安装
pip install dist/project-1.0.0-py3-none-any.whl
```

### 4.5 验证安装

```bash
# 检查包是否安装成功
pip list
pip show package_name

# 尝试导入
python -c "import requests; print(requests.__version__)"
```

---

## 五、配置环境

### 5.1 环境变量

很多项目需要 API Key、数据库密码等敏感信息，通过环境变量传入：

```bash
# 方法一：临时设置（当前终端有效）
export API_KEY="sk-xxxxxxxxxxxx"
export DATABASE_URL="sqlite:///db.sqlite3"

# 方法二：写入 .env 文件（推荐）
cat > .env << 'EOF'
API_KEY=sk-xxxxxxxxxxxx
DATABASE_URL=sqlite:///db.sqlite3
DEBUG=true
EOF

# 方法三：在激活虚拟环境时自动加载
echo 'set -a; source .env; set +a' >> .venv/bin/activate
```

### 5.2 用 python-dotenv 加载 .env

```python
# 在代码中加载 .env 文件
from dotenv import load_dotenv
import os

load_dotenv()  # 加载 .env 文件

api_key = os.getenv("API_KEY")
debug = os.getenv("DEBUG", "false").lower() == "true"
```

```bash
# 安装 python-dotenv
pip install python-dotenv
```

### 5.3 配置文件

有些项目使用配置文件而非环境变量：

```bash
# 常见配置文件位置
config.yaml
config.toml
config.json
settings.py
```

---

## 六、运行项目

### 6.1 查看项目入口

```bash
# 方法一：看 README
cat README.md | grep -A5 "Usage\|Quick Start\|运行"

# 方法二：看 pyproject.toml 的 scripts 入口
cat pyproject.toml | grep -A3 "\[project.scripts\]"

# 方法三：看 setup.py 的 entry_points
cat setup.py | grep -A3 "entry_points"

# 方法四：直接看目录结构
ls *.py  # 根目录下的 .py 文件
ls src/  # src 目录下的模块
```

### 6.2 常见运行方式

```bash
# 方式一：直接运行主脚本
python main.py
python app.py
python run.py

# 方式二：模块方式运行
python -m project_name
python -m uvicorn main:app --reload  # FastAPI 项目

# 方式三：通过安装的命令行工具
# 如果 pyproject.toml 定义了 scripts
project_name --help
uvicorn --help

# 方式四：Makefile
make run
make dev
```

### 6.3 常见问题排查

```bash
# 问题：ModuleNotFoundError
# 原因：依赖未安装或未激活虚拟环境
source .venv/bin/activate
pip install -r requirements.txt

# 问题：Python 版本不对
# 检查项目要求的版本
cat pyproject.toml | grep python
# 使用正确版本创建虚拟环境
python3.11 -m venv .venv  # 如果项目要求 3.11

# 问题：权限错误
# 不要用 sudo pip install，用虚拟环境
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 问题：网络超时
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 问题：缺少系统依赖
# 某些 Python 包需要系统库
sudo apt install libpq-dev  # psycopg2 需要
sudo apt install libffi-dev  # cffi 需要
```

---

## 七、完整实战示例

### 示例一：运行一个 FastAPI 项目

```bash
# 1. 克隆
git clone https://github.com/tiangolo/full-stack-fastapi-template.git
cd full-stack-fastapi-template

# 2. 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 填入必要的配置

# 5. 运行
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# 访问 http://localhost:8000/docs 查看 API 文档
```

### 示例二：运行一个 CLI 工具

```bash
# 1. 安装（无需克隆）
pip install httpx

# 2. 直接使用
httpx https://httpbin.org/get

# 或者克隆后开发模式安装
git clone https://github.com/encode/httpx.git
cd httpx
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 示例三：运行一个数据分析项目

```bash
# 1. 克隆
git clone https://github.com/pola-rs/polars.git
cd polars

# 2. 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 3. 安装（项目使用 pyproject.toml）
pip install -e ".[dev]"

# 4. 运行测试
python -m pytest

# 5. 使用
python -c "import polars as pl; print(pl.DataFrame({'a': [1,2,3]}))"
```

---

## 八、常用命令速查

| 操作 | 命令 |
|------|------|
| 创建虚拟环境 | `python3 -m venv .venv` |
| 激活虚拟环境 | `source .venv/bin/activate` |
| 退出虚拟环境 | `deactivate` |
| 安装依赖 | `pip install -r requirements.txt` |
| 安装包 | `pip install package_name` |
| 卸载包 | `pip uninstall package_name` |
| 查看已安装包 | `pip list` |
| 查看包信息 | `pip show package_name` |
| 导出依赖 | `pip freeze > requirements.txt` |
| 配置镜像 | `pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple` |
| 运行 Python | `python script.py` 或 `python -m module` |
| 检查 Python 版本 | `python --version` |

---

## 九、与 C 项目对比

| 概念 | Python | C |
|------|--------|---|
| 依赖管理 | `pip install -r requirements.txt` | `apt install libcurl-dev` |
| 隔离环境 | `venv` 虚拟环境 | `LD_LIBRARY_PATH` 或容器 |
| 项目配置 | `pyproject.toml` | `CMakeLists.txt` |
| 安装依赖 | `pip install .` | `cmake --install .` |
| 运行项目 | `python main.py` | `./build/myapp` |
| 开发模式 | `pip install -e .` | `make && ./build/myapp` |
| 版本管理 | `pyenv` 或 `uv python` | 系统包管理器 |
