# 55 - Nginx 反向代理与负载均衡

> Nginx 不仅是高性能 Web 服务器，更是工业级的反向代理和负载均衡器。通过 `proxy_pass` 将请求转发到后端应用，通过 `upstream` 块实现多节点负载分发，通过健康检查自动剔除故障节点，通过缓存和限流保护后端——这些能力使 Nginx 成为现代微服务架构中不可或缺的反向代理层。本章在 [[24-Web服务器(Nginx+Apache)]] 的基础上深入反向代理、负载均衡和生产实践。

---

## 55.1 反向代理概念

### 正向代理 vs 反向代理

```
正向代理（Forward Proxy） 反向代理（Reverse Proxy）
 客户端 → 代理 → 互联网 客户端 → 代理 → 后端服务器
 隐藏客户端身份 隐藏服务器身份
 
 [Client A] ─┐ [Client A] ─┐
 [Client B] ─┤→ [Proxy] → [Internet] ├→ [Nginx] ─┬→ [Server 1]
 [Client C] ─┘ │ ├→ [Server 2]
 [Client B] ───┘ └→ [Server 3]
```

### 反向代理的核心作用

| 作用 | 说明 |
|------|------|
| **负载均衡** | 将请求分发到多台后端服务器 |
| **SSL 终止** | 在代理层解密 HTTPS，后端用 HTTP |
| **缓存** | 缓存静态/动态内容，减少后端负载 |
| **安全隔离** | 隐藏后端真实 IP，统一安全策略 |
| **压缩** | gzip/brotli 压缩响应 |
| **路由** | 按 URL 路径、域名分发到不同服务 |
| **限流** | 防止单客户端过度请求 |
| **WebSocket** | 代理 WebSocket 长连接 |

---

## 55.2 proxy_pass 基础

### 基本配置

```nginx
# /etc/nginx/conf.d/reverse-proxy.conf

server {
 listen 80;
 server_name api.example.com;

 location / {
 proxy_pass http://127.0.0.1:3000;
 proxy_set_header Host $host;
 proxy_set_header X-Real-IP $remote_addr;
 proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
 proxy_set_header X-Forwarded-Proto $scheme;
 }
}
```

### proxy_pass 的 URL 尾斜杠规则

```nginx
# 带 / — 替换匹配的前缀
location /api/ {
 proxy_pass http://backend/;
 # 请求 /api/users → 转发到 http://backend/users
}

# 不带 / — 保留完整路径
location /api/ {
 proxy_pass http://backend;
 # 请求 /api/users → 转发到 http://backend/api/users
}
```

### 常用 proxy_set_header

```nginx
# 向后端传递客户端真实信息的标准头集合
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Forwarded-Host $host;
proxy_set_header X-Forwarded-Port $server_port;

# 对于 WebSocket
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

### proxy 超时设置

```nginx
location / {
 proxy_pass http://backend;
 proxy_connect_timeout 60s; # 连接后端超时
 proxy_send_timeout 60s; # 发送请求到后端超时
 proxy_read_timeout 120s; # 等待后端响应超时
 proxy_buffering on;
 proxy_buffer_size 4k;
 proxy_buffers 8 16k;
 proxy_busy_buffers_size 32k;
}
```

---

## 55.3 upstream 负载均衡

### 负载均衡方法

Nginx 支持以下负载均衡算法：

| 方法 | 指令 | 说明 |
|------|------|------|
| 轮询（默认） | 无需额外指令 | 按顺序依次分配 |
| 加权轮询 | `weight=N` | 按权重比例分配 |
| 最少连接 | `least_conn` | 分发给当前连接数最少的后端 |
| IP 哈希 | `ip_hash` | 同一客户端 IP 始终路由到同一后端 |
| 通用哈希 | `hash $variable` | 按指定变量哈希分配 |
| 随机 | `random` | 随机选择（可配合 `two` 参数：选两个，择一） |

### upstream 块配置

```nginx
upstream backend_servers {
 # 轮询（默认）
 server 192.168.1.10:8080;
 server 192.168.1.11:8080;
 server 192.168.1.12:8080;
}

server {
 listen 80;
 server_name app.example.com;

 location / {
 proxy_pass http://backend_servers;
 proxy_set_header Host $host;
 proxy_set_header X-Real-IP $remote_addr;
 }
}
```

### 加权轮询

```nginx
upstream backend_weighted {
 server 192.168.1.10:8080 weight=5; # 50% 流量
 server 192.168.1.11:8080 weight=3; # 30% 流量
 server 192.168.1.12:8080 weight=2; # 20% 流量
}
```

### 最少连接

```nginx
upstream backend_leastconn {
 least_conn;
 server 192.168.1.10:8080;
 server 192.168.1.11:8080;
 server 192.168.1.12:8080;
}
```

### IP 哈希（Session 保持）

```nginx
upstream backend_iphash {
 ip_hash;
 server 192.168.1.10:8080;
 server 192.168.1.11:8080;
 server 192.168.1.12:8080;
}
```

> 注意：`ip_hash` 只能基于前 3 个八位组（IPv4）或整个 IPv6 地址。当某台后端宕机时，该后端的流量会重新分配到其他节点。

### 一致性哈希（hash）

```nginx
upstream backend_hash {
 hash $request_uri consistent;
 server 192.168.1.10:8080;
 server 192.168.1.11:8080;
 server 192.168.1.12:8080;
}
```

`consistent` 参数使用 ketama 一致性哈希算法，增加/移除节点时只有少量请求的哈希映射会改变，适合缓存场景。

---

## 55.4 后端健康检查

### 被动健康检查（Nginx OSS 版）

```nginx
upstream backend_health {
 server 192.168.1.10:8080 max_fails=3 fail_timeout=30s;
 server 192.168.1.11:8080 max_fails=3 fail_timeout=30s;
 server 192.168.1.12:8080 max_fails=3 fail_timeout=30s backup;
 server 192.168.1.13:8080 down;
}
```

| 参数 | 说明 |
|------|------|
| `max_fails=N` | 在 `fail_timeout` 内失败 N 次后标记为不可用 |
| `fail_timeout=Ns` | 失败时间窗口 + 标记不可用的时长 |
| `backup` | 备用服务器，仅在其他全部不可用时启用 |
| `down` | 手动标记为不可用（维护窗口） |

### 主动健康检查（Nginx Plus / 模块）

```nginx
# Nginx Plus 商业版支持主动健康检查
# 开源版可使用 nginx_upstream_check 模块（需自行编译）
upstream backend_active {
 server 192.168.1.10:8080;
 server 192.168.1.11:8080;

 check interval=3000 rise=2 fall=5 timeout=1000 type=http;
 check_http_send "HEAD /health HTTP/1.0\r\n\r\n";
 check_http_expect_alive http_2xx http_3xx;
}
```

### 使用 map + 自定义健康端点

```nginx
# 开源版变通方案：定义一个健康检查 location
location /nginx-health {
 access_log off;
 return 200 "healthy\n";
 add_header Content-Type text/plain;
}
```

使用外部工具（如 `curl`、HAProxy、Keepalived）定期探测此端点。

---

## 55.5 SSL 终止

### 单站点 SSL 配置

```nginx
server {
 listen 443 ssl http2;
 server_name api.example.com;

 ssl_certificate /etc/nginx/ssl/api.example.com.crt;
 ssl_certificate_key /etc/nginx/ssl/api.example.com.key;

 # Let's Encrypt 证书（推荐）
 # ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
 # ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;

 ssl_protocols TLSv1.2 TLSv1.3;
 ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
 ssl_prefer_server_ciphers on;
 ssl_session_cache shared:SSL:10m;
 ssl_session_timeout 10m;

 location / {
 proxy_pass http://backend_servers;
 proxy_set_header Host $host;
 proxy_set_header X-Forwarded-Proto https;
 proxy_set_header X-Real-IP $remote_addr;
 }
}

# HTTP → HTTPS 重定向
server {
 listen 80;
 server_name api.example.com;
 return 301 https://$host$request_uri;
}
```

### 多站点 SSL（SNI）

```nginx
# Nginx 自动根据 SNI 选择合适的证书
server {
 listen 443 ssl http2;
 server_name site-a.example.com;
 ssl_certificate /etc/nginx/ssl/site-a.crt;
 ssl_certificate_key /etc/nginx/ssl/site-a.key;
 # ...
}

server {
 listen 443 ssl http2;
 server_name site-b.example.com;
 ssl_certificate /etc/nginx/ssl/site-b.crt;
 ssl_certificate_key /etc/nginx/ssl/site-b.key;
 # ...
}
```

---

## 55.6 WebSocket 代理

```nginx
server {
 listen 443 ssl http2;
 server_name ws.example.com;

 ssl_certificate /etc/letsencrypt/live/ws.example.com/fullchain.pem;
 ssl_certificate_key /etc/letsencrypt/live/ws.example.com/privkey.pem;

 location /ws/ {
 proxy_pass http://ws_backend;
 proxy_http_version 1.1;

 # WebSocket 必需的 Upgrade 头
 proxy_set_header Upgrade $http_upgrade;
 proxy_set_header Connection "upgrade";

 proxy_set_header Host $host;
 proxy_set_header X-Real-IP $remote_addr;
 proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
 proxy_set_header X-Forwarded-Proto $scheme;

 # WebSocket 长连接超时
 proxy_read_timeout 3600s;
 proxy_send_timeout 3600s;
 }
}

upstream ws_backend {
 server 127.0.0.1:3001;
 server 127.0.0.1:3002;
}
```

---

## 55.7 代理层缓存

```nginx
# 定义缓存路径
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:100m
 max_size=10g inactive=60m use_temp_path=off;

server {
 listen 80;
 server_name api.example.com;

 # 通用缓存配置
 proxy_cache api_cache;
 proxy_cache_valid 200 302 10m;
 proxy_cache_valid 404 1m;
 proxy_cache_use_stale error timeout updating http_500 http_502 http_503;
 proxy_cache_lock on;
 proxy_cache_background_update on;

 # 缓存 bypass 头（调试用）
 proxy_cache_bypass $http_cache_control;

 # 向客户端返回缓存状态头
 add_header X-Cache-Status $upstream_cache_status;

 location / {
 proxy_pass http://backend_servers;
 proxy_set_header Host $host;
 }

 # 特定路径更长的缓存时间
 location /static/ {
 proxy_pass http://backend_servers;
 proxy_cache_valid 200 1h;
 }

 # 不缓存的路径
 location /api/private/ {
 proxy_pass http://backend_servers;
 proxy_cache off;
 }
}
```

### 缓存状态变量

`$upstream_cache_status` 的可能值：

| 值 | 说明 |
|-----|------|
| `MISS` | 缓存未命中，请求已转发到后端 |
| `HIT` | 缓存命中 |
| `EXPIRED` | 缓存已过期，请求已转发到后端 |
| `STALE` | 使用过期的缓存（后端不可用时） |
| `UPDATING` | 已在更新，使用过期缓存响应 |
| `BYPASS` | 缓存被跳过 |
| `REVALIDATED` | 缓存已重新验证（by If-Modified-Since 等） |

---

## 55.8 速率限制

### limit_req_zone（请求速率限制）

```nginx
# 定义速率限制区域（10MB 共享内存，基于客户端 IP）
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

# 对登录接口做更严格的限制
limit_req_zone $binary_remote_addr zone=login_limit:10m rate=1r/m;

server {
 listen 80;
 server_name api.example.com;

 # API 全局限流：10 请求/秒，允许额外 5 个突发
 location /api/ {
 limit_req zone=api_limit burst=5 nodelay;
 proxy_pass http://backend_servers;
 }

 # 登录接口严格限流：1 请求/分钟
 location /api/login {
 limit_req zone=login_limit burst=2 nodelay;
 proxy_pass http://backend_servers;
 }

 # 带宽限制（下载限速）
 location /downloads/ {
 limit_rate 500k;
 limit_rate_after 2m;
 proxy_pass http://backend_servers;
 }
}
```

### limit_conn（并发连接限制）

```nginx
limit_conn_zone $binary_remote_addr zone=conn_limit:10m;

server {
 location / {
 limit_conn conn_limit 10; # 每 IP 最多 10 并发连接
 limit_conn_status 429; # 超限返回 429
 proxy_pass http://backend_servers;
 }
}
```

### 限流日志

```nginx
# 定义限流日志格式
limit_req_log_level warn;
log_format rate_limit '$remote_addr - $request - rate_limit_rejected';

server {
 # 限流达到时记录
 location /api/ {
 limit_req zone=api_limit burst=5 nodelay;
 limit_req_log_level error;
 proxy_pass http://backend_servers;
 }
}
```

---

## 55.9 常见反向代理模式

### 模式 1：微服务路由（按 URL 路径）

```nginx
server {
 listen 443 ssl http2;
 server_name services.example.com;

 # API 鉴权服务
 location /api/auth/ {
 proxy_pass http://auth_service;
 }

 # 用户服务
 location /api/users/ {
 proxy_pass http://user_service;
 }

 # 订单服务
 location /api/orders/ {
 proxy_pass http://order_service;
 }

 # 文件服务（直通上传）
 location /api/files/ {
 proxy_pass http://file_service;
 client_max_body_size 100m; # 大文件上传
 proxy_request_buffering off; # 禁用请求缓冲
 }
}

# 各服务 upstream 定义
upstream auth_service {
 server 10.0.0.10:3000;
 server 10.0.0.11:3000;
}

upstream user_service {
 server 10.0.0.20:4000;
 server 10.0.0.21:4000;
}

upstream order_service {
 server 10.0.0.30:5000;
 server 10.0.0.31:5000;
}

upstream file_service {
 server 10.0.0.40:6000;
}
```

### 模式 2：API 网关（多域名 + 路径路由）

```nginx
# 主 API 网关配置
server {
 listen 443 ssl http2;
 server_name api.example.com;

 # 认证后添加自定义头
 location / {
 auth_request /internal/auth;
 auth_request_set $user_id $upstream_http_x_user_id;

 proxy_set_header X-User-ID $user_id;
 proxy_pass http://microservices;
 }

 # 内部认证端点
 location = /internal/auth {
 internal;
 proxy_pass http://auth_service/verify;
 proxy_pass_request_body off;
 proxy_set_header Content-Length "";
 proxy_set_header X-Original-URI $request_uri;
 }
}

upstream microservices {
 hash $request_uri consistent;
 server 10.0.0.100:8080;
 server 10.0.0.101:8080;
}
```

### 模式 3：前后端分离（SPA + API）

```nginx
server {
 listen 443 ssl http2;
 server_name app.example.com;

 root /var/www/app/dist;

 # API 请求转发到后端
 location /api/ {
 proxy_pass http://backend_servers;
 proxy_set_header Host $host;
 proxy_set_header X-Real-IP $remote_addr;
 proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
 }

 # SPA 静态文件
 location / {
 try_files $uri $uri/ /index.html;
 }

 # 静态资源长期缓存
 location /assets/ {
 expires 1y;
 add_header Cache-Control "public, immutable";
 }
}
```

---

## 55.10 实战：Nginx 前端 + 多语言后端

### 场景描述

一个生产环境部署：Nginx 作为入口，前端为静态 React 应用，后端有 Python Flask（端口 5000）、Node.js Express（端口 3000）、内部管理服务（端口 8080）。

```nginx
# /etc/nginx/conf.d/production.conf

# === 全局限流配置 ===
limit_req_zone $binary_remote_addr zone=global:10m rate=30r/s;
limit_req_zone $binary_remote_addr zone=login:10m rate=1r/m;

# === 后端 upstream 组 ===
upstream flask_api {
 least_conn;
 server 127.0.0.1:5000 max_fails=3 fail_timeout=30s;
 server 127.0.0.1:5001 max_fails=3 fail_timeout=30s;
 keepalive 32;
}

upstream nodejs_ws {
 ip_hash;
 server 127.0.0.1:3000 max_fails=2 fail_timeout=15s;
 server 127.0.0.1:3001 max_fails=2 fail_timeout=15s;
}

upstream admin_panel {
 server 127.0.0.1:8080;
}

# === 主站点 ===
server {
 listen 443 ssl http2;
 server_name mysite.com;

 ssl_certificate /etc/letsencrypt/live/mysite.com/fullchain.pem;
 ssl_certificate_key /etc/letsencrypt/live/mysite.com/privkey.pem;

 root /var/www/mysite/dist;
 index index.html;
 charset utf-8;

 # 全局限流
 limit_req zone=global burst=10 nodelay;

 # 前端 SPA
 location / {
 try_files $uri $uri/ /index.html;
 }

 location /assets/ {
 expires 1y;
 add_header Cache-Control "public, immutable";
 }

 # Python Flask REST API
 location /api/v1/ {
 proxy_pass http://flask_api;
 proxy_http_version 1.1;
 proxy_set_header Host $host;
 proxy_set_header X-Real-IP $remote_addr;
 proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
 proxy_set_header X-Forwarded-Proto $scheme;
 proxy_set_header Connection "";
 }

 # 登录接口 — 严格限流
 location = /api/v1/login {
 limit_req zone=login burst=2 nodelay;
 proxy_pass http://flask_api;
 proxy_set_header Host $host;
 proxy_set_header X-Real-IP $remote_addr;
 }

 # Node.js WebSocket
 location /ws/ {
 proxy_pass http://nodejs_ws;
 proxy_http_version 1.1;
 proxy_set_header Upgrade $http_upgrade;
 proxy_set_header Connection "upgrade";
 proxy_set_header Host $host;
 proxy_set_header X-Real-IP $remote_addr;
 proxy_read_timeout 3600s;
 }

 # 内部管理后台（仅允许内网访问）
 location /admin/ {
 allow 10.0.0.0/8;
 allow 192.168.0.0/16;
 deny all;

 proxy_pass http://admin_panel;
 proxy_set_header Host $host;
 proxy_set_header X-Real-IP $remote_addr;
 }
}

# === HTTP 重定向到 HTTPS ===
server {
 listen 80;
 server_name mysite.com;
 return 301 https://$host$request_uri;
}
```

### 启动与验证

```bash
# 启动后端服务
cd /opt/app/flask && gunicorn -w 4 -b 127.0.0.1:5000 app:app &
cd /opt/app/flask2 && gunicorn -w 4 -b 127.0.0.1:5001 app:app &
cd /opt/app/nodejs && node server.js & # 监听 127.0.0.1:3000
cd /opt/app/nodejs2 && node server.js & # 监听 127.0.0.1:3001

# 测试 Nginx 配置
sudo nginx -t

# 重载配置
sudo nginx -s reload

# 验证后端可达
curl -I https://mysite.com/api/v1/health
curl -I -H "Upgrade: websocket" -H "Connection: upgrade" https://mysite.com/ws/
```

---

## 55.11 调试与监控反向代理

### Nginx 访问日志增强

```nginx
# 自定义日志格式，包含 upstream 相关信息
log_format upstream_info '$remote_addr - $remote_user [$time_local] '
 '"$request" $status $body_bytes_sent '
 '"$http_referer" "$http_user_agent" '
 'upstream=[$upstream_addr] '
 'rt=$upstream_response_time '
 'uct=$upstream_connect_time '
 'uht=$upstream_header_time '
 'cache=$upstream_cache_status';

access_log /var/log/nginx/access.log upstream_info;
```

### 实时监控工具

```bash
# 查看哪个 backend 收到最多请求
tail -f /var/log/nginx/access.log | grep -oP 'upstream=\[\K[^\]]+' | sort | uniq -c

# 查看响应时间分布（慢请求排查）
tail -f /var/log/nginx/access.log | grep -oP 'rt=\K[0-9.]+' | sort -n

# 使用 ngxtop（实时 Nginx 访问统计）
sudo apt install python3-pip -y
pip install ngxtop
ngxtop -l /var/log/nginx/access.log

# 查看 Nginx stub_status 模块的状态
# 在配置中添加：
# location /nginx_status {
# stub_status on;
# access_log off;
# allow 127.0.0.1;
# deny all;
# }
curl http://127.0.0.1/nginx_status
# Active connections: 291
# server accepts handled requests
# 16630948 16630948 31070465
# Reading: 6 Writing: 179 Waiting: 106
```

### stub_status 指标解读

| 指标 | 说明 |
|------|------|
| Active connections | 当前活动连接数（含等待） |
| accepts | 已接受的总连接数 |
| handled | 已处理的总连接数 |
| requests | 已处理的总请求数 |
| Reading | 正在读取请求头 |
| Writing | 正在读取请求体/处理/发送响应 |
| Waiting | 保持连接（keep-alive）等待中 |

---

## 55.12 高可用反向代理

单台 Nginx 反向代理存在单点故障风险。生产环境通常配合 Keepalived 实现高可用。

```nginx
# 两台 Nginx 节点运行相同配置
# 配合 Keepalived 提供虚拟 IP（VIP）漂移
# 见 [[61-高可用与集群]]
```

简要示例：

```bash
# Node 1（主）
sudo apt install keepalived -y
sudo vim /etc/keepalived/keepalived.conf
```

```
vrrp_instance VI_1 {
 state MASTER
 interface eth0
 virtual_router_id 51
 priority 100
 advert_int 1
 authentication {
 auth_type PASS
 auth_pass s3cr3t
 }
 virtual_ipaddress {
 192.168.1.100/24
 }
}
```

```bash
sudo systemctl enable --now keepalived
# DNS 将 api.example.com 指向 VIP 192.168.1.100
```

详见 [[61-高可用与集群]]。

---

## 55.13 故障排查清单

| 症状 | 可能原因 | 排查命令 |
|------|---------|---------|
| 502 Bad Gateway | 后端服务未运行 | `curl http://127.0.0.1:3000` |
| 504 Gateway Timeout | 后端响应过慢 | 检查 `proxy_read_timeout`，查看后端负载 |
| 连接被拒绝 | 后端端口未监听 | `ss -tlnp | grep 3000` |
| 部分后端不可用 | 健康检查标记下线 | 检查 Nginx error.log |
| WebSocket 断开 | 未设置 Upgrade 头 | 确认 `proxy_set_header Upgrade` |
| 缓存不生效 | 路径或状态码不匹配 | `curl -I` 查看 `X-Cache-Status` |
| SSL 证书问题 | 证书过期或路径错误 | `openssl x509 -in cert.crt -noout -dates` |
| 限流误伤正常用户 | burst 值太小 | 增大 burst 或使用 `$binary_remote_addr` |

```bash
# 快速诊断脚本
#!/bin/bash
echo "=== Nginx 状态 ==="
systemctl status nginx --no-pager | head -5

echo "=== 后端健康检查 ==="
for backend in 3000 3001 5000 5001 8080; do
 curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$backend/health 2>/dev/null \
 && echo " :$backend OK" || echo " :$backend FAIL"
done

echo "=== 最近 Nginx 错误 ==="
tail -5 /var/log/nginx/error.log
```

---

## 55.14 本章总结

| 功能 | 核心指令 | 参考 |
|------|---------|------|
| 反向代理 | `proxy_pass` | 本章 [[24-Web服务器(Nginx+Apache)]] |
| 负载均衡 | `upstream` + `server` | 本章 |
| 健康检查 | `max_fails` / `fail_timeout` | 本章 |
| SSL 终止 | `ssl_certificate` + `listen 443 ssl` | 本章 |
| WebSocket | `proxy_set_header Upgrade` | 本章 |
| 缓存 | `proxy_cache_path` / `proxy_cache` | 本章 |
| 限流 | `limit_req_zone` / `limit_conn` | 本章 |
| 高可用 | Keepalived VRRP | [[61-高可用与集群]] |
| 监控 | stub_status / ngxtop | 本章 [[58-监控系统(Prometheus+Grafana)]] |
