# Docker 与虚拟环境

## 13.1 Python 虚拟环境

### 容器内是否需要虚拟环境

```bash
# 问题：容器本身就是隔离环境，还需要 venv 吗？

# 答案：一般不需要
# Docker 容器已经是隔离的文件系统
# 但以下情况可能需要：
# 1. 多个 Python 项目共享一个基础镜像
# 2. CI/CD 中需要隔离构建环境
# 3. 开发环境中需要切换 Python 版本
```

### 在容器内使用 venv
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 创建虚拟环境
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 安装依赖（在 venv 中）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

CMD ["python", "app.py"]
```

### requirements.txt 管理
```bash
# 生成 requirements.txt
pip freeze > requirements.txt

# 安装依赖
pip install -r requirements.txt

# 使用 pip-tools 固定版本
pip install pip-tools
pip-compile requirements.in
pip install -r requirements.txt
```

### Docker Compose 中的 Python 环境
```yaml
services:
  api:
    build: .
    volumes:
      - ./app:/app
      - venv_data:/opt/venv  # 持久化虚拟环境
    command: python -m uvicorn main:app --reload

volumes:
  venv_data:
```

## 13.2 Node.js 版本管理

### Node 版本选择
```bash
# Dockerfile 中直接指定 Node 版本
FROM node:20-alpine  # LTS 版本
FROM node:18-alpine  # 老版本
FROM node:22-alpine  # 最新版本

# 不需要 nvm
# Docker 的 FROM 指令就是最好的版本管理
```

### 容器内使用 nvm（不推荐）
```dockerfile
# 不推荐：nvm 会增加镜像体积
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y curl
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
ENV NVM_DIR=/root/.nvm
RUN . "$NVM_DIR/nvm.sh" && nvm install 20

# 推荐：直接用官方 Node 镜像
FROM node:20-alpine
```

## 13.3 数据库开发环境

### 一键拉起完整环境
```yaml
# docker-compose.dev.yml
services:
  # 后端 API
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./app:/app
    environment:
      DATABASE_URL: postgresql://dev:dev@postgres:5432/mydb
      REDIS_URL: redis://redis:6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: python -m uvicorn main:app --reload

  # PostgreSQL
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev
    ports:
      - "5432:5432"
    volumes:
      - pg_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dev -d mydb"]
      interval: 5s
      timeout: 5s
      retries: 5

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # phpMyAdmin（可选）
  phpmyadmin:
    image: phpmyadmin:latest
    ports:
      - "8080:80"
    environment:
      PMA_HOST: postgres
      PMA_PORT: 5432
    depends_on:
      - postgres

volumes:
  pg_data:
  redis_data:
```

```bash
# 启动完整环境
docker compose -f docker-compose.dev.yml up -d

# 查看状态
docker compose ps

# 连接数据库
docker compose exec postgres psql -U dev -d mydb

# 停止并清理
docker compose down -v
```

### 数据库初始化脚本
```sql
-- init.sql
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (name, email) VALUES
    ('Alice', 'alice@example.com'),
    ('Bob', 'bob@example.com');
```

## 13.4 开发环境一键拉起

### 热重载配置
```yaml
# docker-compose.dev.yml
services:
  node-app:
    build:
      context: .
      target: development
    volumes:
      - ./src:/app/src            # 代码热重载
      - /app/node_modules         # 排除 node_modules
    command: npm run dev
    ports:
      - "3000:3000"
      - "9229:9229"              # 调试端口

  python-app:
    build: .
    volumes:
      - ./app:/app               # 代码热重载
    command: python -m uvicorn main:app --reload --host 0.0.0.0
    ports:
      - "8000:8000"
```

### VS Code Dev Containers
```json
// .devcontainer/devcontainer.json
{
  "name": "My App",
  "dockerComposeFile": "docker-compose.dev.yml",
  "service": "api",
  "workspaceFolder": "/app",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "dbaeumer.vscode-eslint"
      ]
    }
  }
}
```

## 13.5 CI/CD 中的 Docker

### GitHub Actions 示例
```yaml
# .github/workflows/docker.yml
name: Build and Push Docker Image

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: myuser/myapp:${{ github.sha }}
```

### GitLab CI 示例
```yaml
# .gitlab-ci.yml
build:
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t myregistry/myapp:$CI_COMMIT_SHA .
    - docker push myregistry/myapp:$CI_COMMIT_SHA
  only:
    - main
```

## 13.6 常见问题与排查

### 容器内权限问题
```bash
# 虚拟环境目录权限不足时
RUN chown -R appuser:appuser /opt/venv
USER appuser

# 或者使用 root（不推荐生产环境）
USER root
```

### 依赖安装失败排查
```bash
# 查看构建日志
docker compose build --no-cache api

# 进入容器检查
docker compose run --rm api bash

# 检查 Python 版本
python --version

# 检查 pip 安装路径
pip show fastapi
```

### 缓存优化技巧
```dockerfile
# 先复制依赖文件，再复制代码
# 利用 Docker 层缓存，代码修改不会重新安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# npm 同理
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
```

### 开发与生产环境分离
```dockerfile
# 多阶段构建
FROM node:20-alpine AS development
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
CMD ["npm", "run", "dev"]

FROM node:20-alpine AS production
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
CMD ["node", "dist/index.js"]
```

```bash
# 开发环境
docker compose --profile dev up

# 生产环境
docker compose --profile prod up
```
