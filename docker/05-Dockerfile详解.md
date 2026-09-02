# Dockerfile 详解

## 5.1 指令详解

### FROM —— 指定基础镜像
```dockerfile
FROM ubuntu:22.04
FROM python:3.12-slim
FROM golang:1.22-alpine AS builder  # 命名阶段
FROM scratch                        # 空镜像（用于静态二进制）
```

### RUN —— 构建时执行命令
```dockerfile
# shell 格式（通过 /bin/sh -c 执行）
RUN apt-get update && apt-get install -y curl

# exec 格式（直接执行，不经过 shell）
RUN ["/usr/bin/apt-get", "update"]

# 最佳实践：合并命令减少层数
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

### COPY —— 复制文件
```dockerfile
COPY . .                           # 复制整个上下文
COPY requirements.txt /app/        # 复制单个文件
COPY --chown=appuser:appuser . .   # 设置所有者
COPY --chmod=755 script.sh /app/   # 设置权限（BuildKit）
```

### ADD —— 复制文件（特殊功能）
```dockerfile
# 自动解压 tar 文件
ADD app.tar.gz /app/

# 从 URL 下载
ADD https://example.com/file.zip /tmp/

# 注意：一般推荐用 COPY，只有需要自动解压时才用 ADD
```

### WORKDIR —— 设置工作目录
```dockerfile
WORKDIR /app
# 后续指令都在 /app 下执行
# 如果目录不存在会自动创建
WORKDIR /app/src
```

### ENV —— 设置环境变量
```dockerfile
ENV APP_HOME=/app
ENV APP_PORT=8080
ENV PYTHONUNBUFFERED=1
# 环境变量在构建和运行时都有效
```

### ARG —— 构建参数
```dockerfile
ARG VERSION=1.0
ARG DEBIAN_FRONTEND=noninteractive
# 只在构建时有效，运行时不存在
# 可通过 docker build --build-arg VERSION=2.0 覆盖
```

### EXPOSE —— 声明端口
```dockerfile
EXPOSE 80
EXPOSE 443
# 只是文档性质，实际端口映射靠 docker run -p
```

### USER —— 切换用户
```dockerfile
RUN useradd -r -s /usr/bin/nologin appuser
USER appuser
# 后续指令都以 appuser 身份执行
```

### ENTRYPOINT —— 入口命令
```dockerfile
# exec 格式（推荐）
ENTRYPOINT ["python", "app.py"]

# shell 格式（不推荐，信号传递有问题）
ENTRYPOINT python app.py

# ENTRYPOINT 不可被 docker run 参数覆盖
# 但可以通过 --entrypoint 覆盖
```

### CMD —— 默认参数
```dockerfile
# exec 格式
CMD ["python", "app.py"]

# shell 格式
CMD python app.py

# CMD 可被 docker run 参数覆盖
# docker run myimage other_command  → 执行 other_command
```

### ENTRYPOINT vs CMD 组合
```dockerfile
ENTRYPOINT ["python"]
CMD ["app.py"]
# docker run myimage           → python app.py
# docker run myimage test.py   → python test.py（CMD 被覆盖）

ENTRYPOINT ["python"]
# 无 CMD 时
# docker run myimage           → python（无参数，报错）
# docker run myimage app.py    → python app.py
```

### VOLUME —— 声明卷挂载点
```dockerfile
VOLUME /data
VOLUME ["/var/log", "/var/data"]
# 运行时自动创建匿名卷
```

### HEALTHCHECK —— 健康检查
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

HEALTHCHECK NONE  # 禁用健康检查
```

### LABEL —— 元数据
```dockerfile
LABEL maintainer="user@example.com"
LABEL version="1.0" \
      description="My application"
```

### SHELL —— 更改默认 shell
```dockerfile
SHELL ["/bin/bash", "-c"]
RUN echo "Using bash" && ls -la
```

### STOPSIGNAL —— 停止信号
```dockerfile
STOPSIGNAL SIGQUIT
```

## 5.2 ENTRYPOINT vs CMD 深入

| 特性 | ENTRYPOINT | CMD |
|------|-----------|-----|
| 可被 docker run 覆盖 | 否（需 --entrypoint） | 是 |
| 用途 | 固定执行命令 | 默认参数 |
| 组合使用 | ENTRYPOINT 是命令，CMD 是参数 | |

```bash
# 示例
# Dockerfile:
# ENTRYPOINT ["python"]
# CMD ["app.py"]

docker run myimage              # → python app.py
docker run myimage test.py      # → python test.py（CMD 被覆盖）
docker run --entrypoint bash myimage  # → bash（ENTRYPOINT 被覆盖）
```

## 5.3 COPY vs ADD

| 特性 | COPY | ADD |
|------|------|-----|
| 基本复制 | ✅ | ✅ |
| 自动解压 tar | ❌ | ✅ |
| 从 URL 下载 | ❌ | ✅ |
| 推荐使用 | ✅ 一般情况 | 仅需自动解压时 |

## 5.4 最小基础镜像选择

| 基础镜像 | 大小 | 适用场景 |
|----------|------|---------|
| scratch | 0MB | 静态二进制（Go/Rust） |
| alpine | ~5MB | 需要包管理器的轻量场景 |
| distroless | ~20MB | 生产环境（无 shell） |
| slim/debian-slim | ~80MB | 需要 Debian 兼容 |
| ubuntu | ~77MB | 需要完整 Ubuntu |
| ubuntu-full | ~200MB+ | 开发环境 |

```dockerfile
# Go 静态二进制：用 scratch
FROM scratch
COPY --from=builder /app/server /server
ENTRYPOINT ["/server"]

# Python 轻量：用 alpine
FROM python:3.12-alpine

# 生产环境：用 distroless
FROM gcr.io/distroless/python3-debian12
```

## 5.5 多阶段构建最佳实践

```dockerfile
# === 阶段 1：构建 ===
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# === 阶段 2：生产运行 ===
FROM node:20-alpine
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
WORKDIR /app
COPY --from=builder --chown=appuser:appgroup /app/dist ./dist
COPY --from=builder --chown=appuser:appgroup /app/node_modules ./node_modules
USER appuser
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

## 5.6 最佳实践总结

### 安全
- 不要用 root 运行容器（USER 指令）
- 不要在镜像中存储密钥（使用 BuildKit secret mount）
- 扫描漏洞（docker scout / trivy）

### 体积
- 用小基础镜像（alpine / distroless / scratch）
- 多阶段构建
- .dockerignore 排除无关文件
- 合并 RUN 命令减少层数
- 清理包管理器缓存

### 构建速度
- 依赖文件先 COPY，代码后 COPY（利用缓存）
- BuildKit 缓存挂载（--mount=type=cache）
- 并行构建（docker buildx）

### 运行时
- 使用 exec 格式的 ENTRYPOINT/CMD
- 设置 HEALTHCHECK
- 单一职责（一个容器一个服务）

## 5.7 安全扫描
```bash
# Docker Scout（内置）
docker scout cves myapp:latest

# Trivy（第三方，更全面）
trivy image myapp:latest
trivy image --severity HIGH,CRITICAL myapp:latest
```
