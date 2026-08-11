# 部署：gunicorn 与 Docker (Deployment)
---

## 📖 章节概述

开发环境跑通了，下一步是将服务部署到生产环境。本章覆盖 WSGI 服务器 gunicorn（Flask 生产部署）、ASGI 服务器 uvicorn（FastAPI 生产部署）、Docker 容器化、Nginx 反向代理、systemd 服务管理，以及一个完整的 Docker Compose 示例——C 后端作为工作进程，Python Flask 提供 HTTP API 前端。

> **核心理念**：Python Web 应用的部署本质上是一个"进程管理 + 网络层"问题——你不直接暴露 Flask 的开发服务器，而是在它前面放一个生产级网关。这有点像 C 程序不会直接裸奔在公网上，而是包一层守护进程和 iptables 规则。Docker 则进一步将整个运行环境打包为可移植的容器，解决了"我机器上能跑，你机器上不行"的经典问题。

---

### 📚 第一节：WSGI 服务器 — gunicorn 部署 Flask

Flask 内置的 `app.run()` 调用的是 Werkzeug 开发服务器，单进程、单线程、无资源限制——生产环境**绝对不要用它**。

gunicorn（Green Unicorn）是 Python 生态中最成熟的 WSGI 生产服务器：

```bash
pip install gunicorn

# 基本启动
gunicorn -w 4 -b 0.0.0.0:8000 app:app
#         │    │               │  └─ Flask 实例变量名
#         │    │               └─ 模块名（app.py 中的 app = Flask(__name__)）
#         │    └─ 绑定地址和端口
#         └─ worker 进程数（一般 = CPU 核心数 × 2 + 1）
```

核心参数：

| 参数 | 含义 | 建议值 |
|------|------|--------|
| `-w` / `--workers` | 工作进程数 | `2 * CPU 核数 + 1` |
| `-b` / `--bind` | 绑定地址 | `0.0.0.0:8000` |
| `-k` / `--worker-class` | worker 类型 | `sync`（默认）, `gevent`（异步） |
| `--timeout` | 请求超时秒 | `30`（调用 C 后端时可加大） |
| `--max-requests` | worker 处理 N 请求后重启 | `10000`（防内存泄漏） |
| `--daemon` | 后台运行 | 生产环境不建议，用 systemd 管理 |
| `--access-logfile` | 访问日志文件 | `-` 表示 stdout |
| `--error-logfile` | 错误日志文件 | `-` 表示 stderr |

完整启动命令：

```bash
gunicorn \
    --workers 4 \
    --bind 0.0.0.0:8000 \
    --timeout 60 \
    --max-requests 10000 \
    --access-logfile /var/log/myapp/access.log \
    --error-logfile /var/log/myapp/error.log \
    app:app
```

配置文件的替代方案（`gunicorn.conf.py`）：

```python
bind = "0.0.0.0:8000"
workers = 4
timeout = 60
max_requests = 10000
accesslog = "/var/log/myapp/access.log"
errorlog = "/var/log/myapp/error.log"
```

```bash
gunicorn -c gunicorn.conf.py app:app
```

Worker 类型选择：

| Worker 类型 | 适用场景 | 注意 |
|------------|---------|------|
| `sync` | 一般 Web 应用，响应快 | 慢请求会阻塞 worker |
| `gevent` | 有 I/O 等待（调外部 API） | 需 `pip install gevent` |
| `gthread` | 多线程，适合调用 C 库 | 注意 GIL |

> 如果你的 Flask 端点通过 ctypes 调用 C 库做 CPU 密集型计算，`sync` worker + 多进程是最简单可靠的选择。

---

### 📚 第二节：ASGI 服务器 — uvicorn 部署 FastAPI

FastAPI 基于 ASGI 协议，用 uvicorn（或配合 gunicorn）作为生产服务器：

```bash
pip install uvicorn

# 单进程模式（开发）
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 多进程模式（生产）—— 使用 gunicorn 管理 uvicorn worker
pip install gunicorn
gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
```

WSGI vs ASGI 部署对照表：

| | Flask | FastAPI |
|---|-------|---------|
| 协议 | WSGI | ASGI |
| 开发服务器 | `app.run()` (Werkzeug) | `uvicorn main:app --reload` |
| 生产服务器 | `gunicorn app:app -w 4` | `gunicorn -k uvicorn.workers.UvicornWorker` |
| 或直接用 | — | `uvicorn main:app --workers 4` |

---

### 📚 第三节：Nginx 反向代理

Nginx 位于 gunicorn/uvicorn 前面，负责：
- 静态文件服务（直接返回，不经过 Python）
- 请求缓冲（保护后端 Python 进程）
- SSL 终止（HTTPS）
- 负载均衡（多个 gunicorn 实例）

基础 Nginx 配置 `/etc/nginx/sites-available/myapp`：

```nginx
upstream app_server {
    server 127.0.0.1:8000;    # gunicorn 监听地址
    # server 127.0.0.1:8001;  # 可添加多个后端做负载均衡
}

server {
    listen 80;
    server_name example.com;

    # 静态文件直接由 Nginx 提供（不经过 Python）
    location /static/ {
        alias /opt/myapp/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 其他请求代理给 gunicorn
    location / {
        proxy_pass http://app_server;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30;
        proxy_read_timeout 60;   # C 后端计算慢时可增大
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/
sudo nginx -t                    # 测试配置语法
sudo systemctl reload nginx      # 重新加载
```

> 如果你觉得 Nginx 配置太复杂，可以试试 **Caddy**——自动 HTTPS、配置极简（3 行起）、一个二进制文件。对于内部工具或小项目，Caddy 的学习成本远低于 Nginx。

---

### 📚 第四节：systemd 服务管理

将 gunicorn 注册为 systemd 服务，实现开机自启、崩溃自动重启、日志集成。

服务文件 `/etc/systemd/system/myapp.service`：

```ini
[Unit]
Description=MyApp Flask Web Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/myapp
Environment="PATH=/opt/myapp/venv/bin"
ExecStart=/opt/myapp/venv/bin/gunicorn \
    -c /opt/myapp/gunicorn.conf.py \
    app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

管理命令：

```bash
sudo systemctl daemon-reload     # 修改 service 文件后重载
sudo systemctl enable myapp      # 开机自启
sudo systemctl start myapp       # 启动
sudo systemctl status myapp      # 查看状态
sudo journalctl -u myapp -f      # 实时查看日志
sudo systemctl stop myapp        # 停止
```

---

### 📚 第五节：Docker 容器化

Docker 让环境一致性成为可能——容器内包含 Python 解释器、C 编译器、所有依赖和你的应用代码。

**基础 Dockerfile：**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖（C 程序运行时需要的库）
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsqlite3-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

**多阶段构建（编译 C 程序 + Python 运行）：**

```dockerfile
FROM gcc:13 AS c-builder
WORKDIR /src
COPY src/c-backend/ .
RUN gcc -O2 -o c-worker worker.c

FROM python:3.12-slim
WORKDIR /app
COPY --from=c-builder /src/c-worker /app/bin/c-worker

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY python-app/ .

EXPOSE 8000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

构建与运行：

```bash
docker build -t myapp:latest .
docker run -d -p 8000:8000 --name myapp myapp:latest
docker logs -f myapp
```

---

### 📚 第六节：Docker Compose — C 后端 + Python 前端

完整示例：C 计算程序作为 worker，Python Flask 作为 HTTP API 前端。

项目结构：

```
project/
├── docker-compose.yml
├── c-worker/
│   ├── Makefile
│   └── main.c
├── python-api/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
└── nginx/
    └── nginx.conf
```

`c-worker/main.c`（计算程序，从 stdin 读 JSON，输出 JSON 到 stdout）：

```c
#include <stdio.h>
#include <stdlib.h>
// reads: {"op":"add","a":3,"b":5}
// writes: {"result":8}
int main() {
    char line[256];
    while (fgets(line, sizeof(line), stdin)) {
        int a, b;
        sscanf(line, "{\"a\":%d,\"b\":%d}", &a, &b);
        printf("{\"result\":%d}\n", a + b);
        fflush(stdout);
    }
    return 0;
}
```

`python-api/app.py`：

```python
import subprocess, json
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/compute', methods=['POST'])
def compute():
    data = request.json
    proc = subprocess.run(
        ['/app/bin/c-worker'],
        input=json.dumps(data),
        capture_output=True, text=True
    )
    return jsonify(json.loads(proc.stdout))
```

`docker-compose.yml`：

```yaml
version: '3.8'
services:
  c-worker:
    build:
      context: ./c-worker
      dockerfile: Dockerfile
    image: c-worker:latest

  python-api:
    build:
      context: ./python-api
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    depends_on:
      - c-worker
    volumes:
      - shared-data:/tmp/shared

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ./python-api/static:/usr/share/nginx/html/static:ro
    depends_on:
      - python-api

volumes:
  shared-data:
```

> 这个架构实现了完整的"C 后端 + Python 前端"分层：C 处理计算密集型任务，Python 处理 HTTP 协议和业务逻辑，Nginx 处理静态文件和反向代理。C 程序员可以从最内层（C worker）写到最外层（Nginx），全栈贯通。

---

### 📝 小节练习

> [!question] 选择题 1
> gunicorn 的 `-w` 参数控制什么？
> - [ ] A. 监听端口
> - [ ] B. Worker 进程数量
> - [ ] C. Worker 类型
> - [ ] D. 超时时间
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `-w` 或 `--workers` 指定 gunicorn 预派生多少个 worker 进程来处理请求。每个 worker 是一个独立的操作系统进程。

> [!question] 判断题 1
> Docker 容器内的 `EXPOSE` 指令会自动将端口映射到宿主机。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `EXPOSE` 只是一个文档性质的声明，告诉使用者该容器打算监听的端口。真正的端口映射需要在 `docker run -p 8000:8000` 或 docker-compose 的 `ports:` 中显式指定。

> [!question] 选择题 2
> Nginx 反向代理配置中，`proxy_pass http://app_server;` 的作用是？
> - [ ] A. 将请求原封不动返回给客户端
> - [ ] B. 将请求转发给上游的 gunicorn/uvicorn 进程
> - [ ] C. 将静态文件发送给后端
> - [ ] D. 设置 HTTP 响应头
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `proxy_pass` 将匹配的请求转发到指定的上游服务器（即 gunicorn/uvicorn），并将响应返回给客户端。这是反向代理的核心指令。

---

## 📋 章节测试

### 一、判断题（正确选 ✅，错误选 ❌）

> [!question] 判断题 1
> Flask 的 `app.run(host='0.0.0.0', port=80)` 后就可以安全地用于生产环境。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `app.run()` 启动的是单线程开发服务器，没有进程管理、连接队列小、安全性差。生产环境必须使用 gunicorn/uvicorn 等专门的 WSGI/ASGI 服务器。

> [!question] 判断题 2
> gunicorn 可以直接运行 FastAPI 应用，不需要额外的 worker class。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: FastAPI 是 ASGI 应用，需要 ASGI worker。在 gunicorn 中需要使用 `--worker-class uvicorn.workers.UvicornWorker` 来运行 FastAPI。或者直接用 uvicorn。

> [!question] 判断题 3
> Nginx 的 `location /static/` 配置可以让 Nginx 直接提供静态文件，请求不会到达 Python 进程。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 这正是 Nginx 反向代理的核心价值之一——静态文件由 Nginx 高效处理（零拷贝、异步 I/O），只有动态请求才转发给 Python 进程。

> [!question] 判断题 4
> systemd 服务的 `Restart=always` 意味着进程崩溃后 systemd 会自动重启它。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `Restart=always` 表示无论进程以何种方式退出，systemd 都会自动重新启动它。配合 `RestartSec=5` 设置重启前的等待时间。

> [!question] 判断题 5
> Docker 多阶段构建可以在一个 Dockerfile 中完成 C 程序编译和 Python 环境配置，最终镜像只包含运行时必需的文件。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 多阶段构建（multi-stage build）使用 `FROM ... AS stage` 在编译阶段安装完整工具链，然后用 `COPY --from=stage` 只复制编译产物到最终镜像，大大减小镜像体积。

---

### 二、选择题（单项选择题）

> [!question] 选择题 1
> 以下哪个命令可以正确启动一个 4 worker 的 gunicorn 服务？
> - [ ] A. `gunicorn app:app`
> - [ ] B. `gunicorn -w 4 -b 0.0.0.0:8000 app:app`
> - [ ] C. `gunicorn --workers app:app`
> - [ ] D. `gunicorn run app:app`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `-w 4` 设置 4 个 worker，`-b 0.0.0.0:8000` 绑定地址和端口，`app:app` 格式为 `模块名:Flask实例名`。

> [!question] 选择题 2
> systemd 服务文件中 `WorkingDirectory` 指令的作用是？
> - [ ] A. 设置服务二进制文件的位置
> - [ ] B. 设置服务进程的工作目录
> - [ ] C. 设置日志文件目录
> - [ ] D. 设置服务启动顺序
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `WorkingDirectory` 设置服务进程的当前工作目录，影响相对路径（如模板文件、静态文件、配置文件）的查找。

> [!question] 选择题 3
> Dockerfile 中 `COPY requirements.txt .` 中的 `.` 是指？
> - [ ] A. Docker 守护进程的工作目录
> - [ ] B. Dockerfile 所在的宿主机构建上下文目录
> - [ ] C. 容器内的 `WORKDIR` 设置的目录
> - [ ] D. 容器内的根目录 `/`
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: `COPY` 的第一个路径相对于构建上下文（宿主机），第二个路径 `.` 相对于容器内的 `WORKDIR`（默认 `/`，但通常通过 `WORKDIR /app` 设置）。

> [!question] 选择题 4
> 以下哪个不是 Nginx 在生产环境中的典型作用？
> - [ ] A. 静态文件服务
> - [ ] B. SSL/TLS 终端
> - [ ] C. 执行 Python 代码
> - [ ] D. 请求负载均衡
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: Nginx 不执行 Python 代码——它做反向代理、静态文件、SSL 终止和负载均衡。Python 代码由 gunicorn/uvicorn 进程执行。Nginx 是 C 写的 Web 服务器，理解它的边界很重要。

> [!question] 选择题 5
> gunicorn 的 `--max-requests 10000` 参数解决什么问题？
> - [ ] A. 防止单个 IP 访问 10000 次
> - [ ] B. worker 处理 10000 个请求后自动重启，防止内存泄漏
> - [ ] C. 限制总请求量为 10000
> - [ ] D. 设置每个 worker 的并发请求数为 10000
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `--max-requests` 让每个 worker 在处理指定数量的请求后自动退出并重启。这是防御性措施——即使 Python 代码存在缓慢的内存泄漏，也能通过周期性重启保持服务稳定。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：gunicorn 生产部署
> **难度**: ⭐⭐
>
> 将第 1 章的 Flask 应用用 gunicorn 部署：
> 1. 创建 `gunicorn.conf.py` 配置文件（4 worker + 日志路径）
> 2. 用 `gunicorn -c gunicorn.conf.py app:app` 启动
> 3. 使用 `ab -n 1000 -c 10 http://127.0.0.1:8000/`（ApacheBench）压测，对比 `app.run()` 和 gunicorn 的吞吐量差异

> [!example] 练习题 2：Docker 化
> **难度**: ⭐⭐⭐
>
> 为你的 Flask 或 FastAPI 应用编写 Dockerfile：
> - 使用 `python:3.12-slim` 基础镜像
> - 通过 `requirements.txt` 安装依赖
> - 用 gunicorn 作为 CMD
> - 构建镜像并运行容器，从浏览器验证

> [!example] 练习题 3：多阶段构建 — C + Python
> **难度**: ⭐⭐⭐⭐
>
> 创建一个 Dockerfile，使用多阶段构建：
> - 第一阶段：用 `gcc:13` 编译一个简单的 C 程序（如读取 `stdin`、做计算、写 `stdout`）
> - 第二阶段：基于 `python:3.12-slim`，复制编译好的 C 二进制文件，安装 Flask，运行应用
> - 构建并验证 Python 能通过 `subprocess` 调用容器内的 C 程序

> [!example] 练习题 4：完整部署栈
> **难度**: ⭐⭐⭐⭐
>
> 编写一个 `docker-compose.yml`，包含：
> - `python-api`：你的 Flask 应用（gunicorn 部署）
> - `nginx`：Nginx 反向代理，配置 `/static/` 走 Nginx，`/api/` 代理到 Flask
> - 使用 `depends_on` 确保启动顺序
> - 启动后用 `curl http://localhost/` 和 `curl http://localhost/api/...` 验证静态文件和 API 代理都正常工作

> [!example] 练习题 5：systemd 服务
> **难度**: ⭐⭐⭐
>
> 编写一个 systemd service 文件，管理你的 Python Web 应用：
> - 用户为 `www-data`
> - 工作目录为 `/opt/myapp`
> - 使用虚拟环境中的 gunicorn
> - 崩溃自动重启，重启延迟 5 秒
> - 使用 `journalctl -u myapp -f` 验证日志输出正常
