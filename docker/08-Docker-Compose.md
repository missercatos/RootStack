# Docker Compose

## 8.1 安装与版本

```bash
# Docker Compose v2（推荐，作为 docker 子命令）
# Docker Desktop 自带
# Linux 手动安装
sudo apt install docker-compose-plugin  # Ubuntu
sudo pacman -S docker-compose  # Arch

# 验证
docker compose version

# v1（独立二进制，已废弃）
docker-compose version  # 旧版
```

## 8.2 compose.yaml 语法

### 文件结构
```yaml
services:        # 服务定义
  web:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./html:/usr/share/nginx/html:ro
    depends_on:
      - api
    restart: unless-stopped

  api:
    build: .
    environment:
      - DB_HOST=db
    networks:
      - backend

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: mydb
      POSTGRES_PASSWORD: secret
    volumes:
      - db_data:/var/lib/postgresql/data
    networks:
      - backend

volumes:         # 命名卷声明
  db_data:

networks:        # 网络声明
  backend:
```

### 常用配置项
```yaml
services:
  web:
    image: nginx:alpine           # 使用已有镜像
    build: .                       # 从 Dockerfile 构建
    build:
      context: .
      dockerfile: Dockerfile.prod
      args:
        VERSION: "1.0"
    ports:
      - "8080:80"                  # 宿主:容器
      - "127.0.0.1:8080:80"       # 限制访问
    volumes:
      - ./app:/app                 # Bind Mount
      - mydata:/data               # Volume
      - /tmp:/tmp:ro              # 只读
    environment:
      - DB_HOST=db
      - DB_PORT=5432
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
    networks:
      - frontend
      - backend
    restart: unless-stopped        # no / always / on-failure / unless-stopped
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80/"]
      interval: 30s
      timeout: 5s
      retries: 3
```

## 8.3 环境变量管理

### .env 文件
```bash
# .env
DB_PASSWORD=secret123
APP_PORT=8080
REDIS_HOST=redis
```

```yaml
# compose.yaml
services:
  web:
    image: nginx:alpine
    ports:
      - "${APP_PORT:-8080}:80"
    environment:
      - REDIS_HOST=${REDIS_HOST}
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
```

### 多环境配置
```yaml
# compose.yaml（基础）
services:
  web:
    build: .
    ports:
      - "8080:80"

# compose.override.yaml（开发环境，自动加载）
services:
  web:
    volumes:
      - ./app:/app
    command: npm run dev

# compose.prod.yaml（生产环境，手动指定）
# docker compose -f compose.yaml -f compose.prod.yaml up -d
services:
  web:
    restart: always
    logging:
      driver: json-file
      options:
        max-size: "10m"
```

### Profile 分组
```yaml
services:
  web:
    image: nginx:alpine
    profiles: ["web", "all"]

  db:
    image: postgres:16-alpine
    profiles: ["db", "all"]

  debug:
    image: busybox
    profiles: ["debug"]  # 只在需要时启动
```

```bash
# 启动默认服务
docker compose up -d

# 启动指定 profile
docker compose --profile web up -d
docker compose --profile debug up -d
docker compose --profile all up -d
```

## 8.4 完整示例：Web + DB + Cache

```yaml
services:
  web:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
      - REDIS_URL=redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - frontend
      - backend

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - pg_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d mydb"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - backend

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - backend

volumes:
  pg_data:
  redis_data:

networks:
  frontend:
  backend:
```

```bash
# 启动
docker compose up -d

# 查看状态
docker compose ps

# 查看日志
docker compose logs -f web

# 进入容器
docker compose exec web sh

# 停止并清理
docker compose down
docker compose down -v  # 同时删除卷
```

## 8.5 生命周期管理

```bash
# 启动
docker compose up -d
docker compose up -d --build      # 重新构建
docker compose up -d web          # 只启动特定服务

# 停止
docker compose stop               # 停止容器
docker compose down               # 停止并删除容器
docker compose down -v            # 同时删除卷

# 重启
docker compose restart
docker compose restart web

# 扩展服务
docker compose up -d --scale web=3

# 构建
docker compose build
docker compose build --no-cache

# 拉取镜像
docker compose pull
```

## 8.6 生产部署注意事项

### 资源限制
```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: 1G
        reservations:
          cpus: "0.5"
          memory: 256M
```

### 日志配置
```yaml
services:
  web:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

### 重启策略
```yaml
services:
  web:
    restart: unless-stopped  # 推荐生产环境
    # no: 不重启
    # always: 总是重启
    # on-failure: 非正常退出时重启
    # unless-stopped: 手动停止后不重启
```

### 调试技巧
```bash
# 查看配置解析结果
docker compose config

# 查看容器详情
docker compose ps -a
docker compose inspect web

# 实时日志
docker compose logs -f --tail 100

# 执行临时命令
docker compose run --rm web sh

# 强制重建
docker compose up -d --force-recreate

# 移除悬空资源
docker compose down --rmi local --volumes
```

### 最佳实践
```yaml
services:
  web:
    image: nginx:alpine
    # 使用具体版本标签，避免 latest
    # 合理设置资源限制
    # 配置健康检查
    # 使用命名卷持久化数据
    # 通过网络隔离敏感服务
```

```bash
# 生产环境建议
# 1. 使用 docker compose -f compose.prod.yaml up -d
# 2. 配置日志轮转防止磁盘占满
# 3. 设置合理的重启策略
# 4. 使用 secrets 管理敏感信息
# 5. 定期清理未使用的镜像和卷
```
