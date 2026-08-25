# 24 - Web 服务器（Nginx + Apache）

> Nginx 和 Apache 是 Linux 平台上最主流的两个 Web 服务器，共同承载了互联网上绝大多数网站。Nginx 以其事件驱动架构、高性能和反向代理能力著称；Apache 则以模块丰富、.htaccess 灵活配置和历史积累受到青睐。本章涵盖两者的基本安装、配置、SSL/TLS 证书部署，以及如何选择适合的 Web 服务器。

---

## 24.1 Nginx 与 Apache 概述

### 架构对比

```
Nginx（事件驱动） Apache（进程/线程驱动）

 Master Process Master Process
 │ │
 ┌─────┼─────┐ ┌────┼────┐
 │ │ │ │ │ │
 Worker Worker Worker Child Child Child
 │ │ │ (prefork/worker/event MPM)
 Event Event Event │ │ │
 Loop Loop Loop Thread/Process per Connection

非阻塞 I/O，单线程处理多连接 每个连接占用一个线程/进程
内存占用低，并发能力强 内存消耗随连接数线性增长
```

| 特性 | Nginx | Apache |
|------|-------|--------|
| 架构 | 事件驱动，非阻塞 I/O | 进程/线程驱动（MPM 模块） |
| 并发模型 | 少量 worker 处理万级连接 | 连接数 = 进程/线程数 |
| 静态文件 | 极高性能 | 良好 |
| 动态内容 | FastCGI/反向代理 | 内嵌模块（mod_php 等） |
| 配置 | 集中式，无 .htaccess | 集中式 + 目录级 .htaccess |
| 反向代理 | 原生设计，核心功能 | 模块支持（mod_proxy） |
| 模块系统 | 编译时静态链接 | 动态加载 + 编译时 |
| 市场份额 | 约 34%（持续增长） | 约 30%（持续下降） |

### 安装

```bash
# === Nginx ===
# Debian / Ubuntu
sudo apt install nginx

# RHEL / Fedora
sudo dnf install nginx
# RHEL 9 上可能需要 EPEL:
# sudo dnf install epel-release && sudo dnf install nginx

# openSUSE
sudo zypper install nginx

# Arch
sudo pacman -S nginx

# Alpine
apk add nginx

# === Apache (httpd) ===
# Debian / Ubuntu
sudo apt install apache2

# RHEL / Fedora
sudo dnf install httpd

# openSUSE
sudo zypper install apache2

# Arch
sudo pacman -S apache

# Alpine
apk add apache2
```

### 启动与验证

```bash
# Nginx
sudo systemctl enable --now nginx
sudo nginx -t # 测试配置
sudo nginx -s reload # 重载配置（不停机）
sudo nginx -s stop # 停止

# Apache
sudo systemctl enable --now httpd # RHEL/Fedora/Arch
sudo systemctl enable --now apache2 # Debian/Ubuntu
sudo apachectl configtest # 测试配置
sudo apachectl graceful # 优雅重载
```

---

## 24.2 基本 Nginx 配置

### 配置文件结构

```bash
# Nginx 配置目录（因发行版而异）
# Debian/Ubuntu: /etc/nginx/
# RHEL/Fedora: /etc/nginx/
# Arch: /etc/nginx/
# Alpine: /etc/nginx/

# 典型结构
/etc/nginx/
├── nginx.conf # 主配置文件
├── mime.types # MIME 类型定义
├── conf.d/ # 通用配置片段
├── sites-available/ # 可用站点（Debian/Ubuntu 习惯）
├── sites-enabled/ # 已启用站点（符号链接）
├── modules/ # 模块配置
└── snippets/ # 可复用配置片段
```

### 主配置文件 nginx.conf

```nginx
# /etc/nginx/nginx.conf（精简版）

user www-data; # worker 进程运行用户
worker_processes auto; # 自动匹配 CPU 核心数
pid /run/nginx.pid;
error_log /var/log/nginx/error.log warn;

events {
 worker_connections 1024; # 每个 worker 最大连接数
 use epoll; # Linux 上推荐
 multi_accept on; # 同时接受多个新连接
}

http {
 # 基础设置
 sendfile on;
 tcp_nopush on;
 tcp_nodelay on;
 keepalive_timeout 65;
 types_hash_max_size 2048;
 server_tokens off; # 隐藏版本号

 include /etc/nginx/mime.types;
 default_type application/octet-stream;

 # 日志格式
 log_format main '$remote_addr - $remote_user [$time_local] '
 '"$request" $status $body_bytes_sent '
 '"$http_referer" "$http_user_agent"';
 access_log /var/log/nginx/access.log main;

 # Gzip 压缩
 gzip on;
 gzip_types text/plain text/css application/json application/javascript text/xml;
 gzip_min_length 1024;

 # 包含站点配置
 include /etc/nginx/conf.d/*.conf;
 include /etc/nginx/sites-enabled/*; # Debian/Ubuntu
}
```

### Server Block（虚拟主机）

Nginx 的虚拟主机配置（类似 Apache 的 VirtualHost）：

```nginx
# /etc/nginx/sites-available/example.com（Debian/Ubuntu）
# 或 /etc/nginx/conf.d/example.com.conf（RHEL/Fedora）

# === HTTP → HTTPS 重定向 ===
server {
 listen 80;
 listen [::]:80;
 server_name example.com www.example.com;

 # 将 HTTP 请求重定向到 HTTPS
 return 301 https://$host$request_uri;
}

# === HTTPS 站点 ===
server {
 listen 443 ssl http2;
 listen [::]:443 ssl http2;
 server_name example.com www.example.com;

 # SSL 证书
 ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
 ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

 # SSL 优化
 ssl_protocols TLSv1.2 TLSv1.3;
 ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
 ssl_prefer_server_ciphers off;
 ssl_session_cache shared:SSL:10m;
 ssl_session_timeout 1d;

 # 网站根目录
 root /var/www/example.com/html;
 index index.html index.htm index.php;

 # 日志
 access_log /var/log/nginx/example.com.access.log;
 error_log /var/log/nginx/example.com.error.log;

 # Location 规则
 location / {
 try_files $uri $uri/ =404;
 }

 # 静态文件缓存
 location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
 expires 30d;
 add_header Cache-Control "public, immutable";
 }

 # 拒绝隐藏文件
 location ~ /\. {
 deny all;
 }

 # 代理 API 请求到后端
 location /api/ {
 proxy_pass http://127.0.0.1:3000;
 proxy_set_header Host $host;
 proxy_set_header X-Real-IP $remote_addr;
 proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
 proxy_set_header X-Forwarded-Proto $scheme;
 }
}
```

### 启用站点

```bash
# Debian/Ubuntu
sudo ln -s /etc/nginx/sites-available/example.com /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# RHEL/Fedora（.conf 文件直接放入 conf.d/ 即生效）
sudo cp example.com.conf /etc/nginx/conf.d/
sudo nginx -t && sudo systemctl reload nginx
```

---

## 24.3 基本 Apache 配置

### 配置文件结构

```bash
# Apache 配置目录
# Debian/Ubuntu: /etc/apache2/
# RHEL/Fedora: /etc/httpd/
# Arch: /etc/httpd/

# Debian/Ubuntu 结构
/etc/apache2/
├── apache2.conf # 主配置
├── ports.conf # 监听端口
├── mods-available/ # 可用模块
├── mods-enabled/ # 已启用模块
├── sites-available/ # 可用站点
├── sites-enabled/ # 已启用站点
└── conf-available/ # 可用配置片段

# RHEL/Fedora 结构
/etc/httpd/
├── conf/httpd.conf # 主配置
├── conf.d/ # 额外配置
├── conf.modules.d/ # 模块配置
└── logs -> /var/log/httpd # 日志
```

### VirtualHost 配置

```apache
# /etc/apache2/sites-available/example.com.conf（Debian/Ubuntu）

# === 监听端口 ===
# 在 ports.conf 中已定义: Listen 80, Listen 443

# === HTTP 站点（重定向到 HTTPS）===
<VirtualHost *:80>
 ServerName example.com
 ServerAlias www.example.com
 Redirect permanent / https://example.com/
</VirtualHost>

# === HTTPS 站点 ===
<VirtualHost *:443>
 ServerName example.com
 ServerAlias www.example.com

 # 网站根目录
 DocumentRoot /var/www/example.com/html

 # SSL
 SSLEngine on
 SSLCertificateFile /etc/letsencrypt/live/example.com/fullchain.pem
 SSLCertificateKeyFile /etc/letsencrypt/live/example.com/privkey.pem

 # 目录权限
 <Directory /var/www/example.com/html>
 Options -Indexes +FollowSymLinks
 AllowOverride All # 允许 .htaccess
 Require all granted
 </Directory>

 # 日志
 ErrorLog ${APACHE_LOG_DIR}/example.com.error.log
 CustomLog ${APACHE_LOG_DIR}/example.com.access.log combined

 # 拒绝 .ht 文件
 <FilesMatch "^\.ht">
 Require all denied
 </FilesMatch>

 # 缓存静态资源
 <FilesMatch "\.(ico|pdf|jpg|jpeg|png|gif|js|css|svg)$">
 Header set Cache-Control "max-age=2592000, public, immutable"
 </FilesMatch>

 # 反向代理到后端应用
 ProxyPreserveHost On
 ProxyPass /api/ http://127.0.0.1:3000/
 ProxyPassReverse /api/ http://127.0.0.1:3000/
</VirtualHost>
```

### 启用站点与模块

```bash
# Debian/Ubuntu
sudo a2ensite example.com.conf # 启用站点
sudo a2dissite 000-default.conf # 禁用默认站点
sudo a2enmod ssl rewrite proxy proxy_http # 启用模块
sudo a2dismod autoindex # 禁用模块
sudo apachectl configtest # 测试配置
sudo systemctl reload apache2

# RHEL/Fedora（直接放入 conf.d/ 即生效）
# 模块默认加载，不需要显式启用
sudo systemctl reload httpd
```

---

## 24.4 SSL/TLS 与 Let's Encrypt

### 获取免费证书（Certbot）

```bash
# 安装 Certbot
# Debian/Ubuntu
sudo apt install certbot python3-certbot-nginx # Nginx 插件
sudo apt install certbot python3-certbot-apache # Apache 插件

# RHEL/Fedora
sudo dnf install certbot python3-certbot-nginx
sudo dnf install certbot python3-certbot-apache

# Alpine
apk add certbot certbot-nginx certbot-apache

# Arch
sudo pacman -S certbot certbot-nginx certbot-apache

# === Nginx 自动获取并配置 ===
sudo certbot --nginx -d example.com -d www.example.com

# === Apache 自动获取并配置 ===
sudo certbot --apache -d example.com -d www.example.com

# === 仅获取证书（手动配置 Web 服务器）===
sudo certbot certonly --webroot -w /var/www/example.com/html \
 -d example.com -d www.example.com

# === 通配符证书（需要 DNS 验证）===
sudo certbot certonly --manual --preferred-challenges dns \
 -d "*.example.com" -d example.com
```

### 证书自动续期

```bash
# Certbot 安装时自动创建 systemd timer 或 cron job

# 手动测试续期（不实际更新）
sudo certbot renew --dry-run

# 强制续期
sudo certbot renew --force-renewal

# 续期后重启 Web 服务器
sudo certbot renew --post-hook "systemctl reload nginx"

# 查看 systemd timer
systemctl list-timers | grep certbot
```

### Nginx SSL 优化配置

```nginx
# 推荐的 SSL 设置（/etc/nginx/snippets/ssl-params.conf）
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:
 ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:
 ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305;
ssl_prefer_server_ciphers off;

ssl_session_cache shared:SSL:50m;
ssl_session_timeout 1d;
ssl_session_tickets off;

ssl_dhparam /etc/nginx/dhparam.pem; # 需要生成
# openssl dhparam -out /etc/nginx/dhparam.pem 4096

# HSTS（强制 HTTPS，谨慎使用）
add_header Strict-Transport-Security "max-age=63072000" always;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
```

### 检查 SSL 配置

```bash
# Qualys SSL Labs 在线测试：
# https://www.ssllabs.com/ssltest/

# 命令行测试
openssl s_client -connect example.com:443 -servername example.com
curl -I https://example.com

# 使用 testssl.sh
git clone https://github.com/drwetter/testssl.sh.git
./testssl.sh/testssl.sh example.com
```

---

## 24.5 静态文件服务

### Nginx 静态站点

```nginx
server {
 listen 80;
 server_name static.example.com;
 root /var/www/static;

 location / {
 index index.html;
 try_files $uri $uri/ =404;
 }

 # Gzip 预压缩文件
 location ~ \.js\.gz$ {
 add_header Content-Encoding gzip;
 gzip off;
 types { application/javascript gz; }
 }

 # 大文件支持
 location /downloads/ {
 alias /var/www/downloads/;
 autoindex on; # 目录列表
 autoindex_exact_size off; # 显示人类可读大小
 autoindex_localtime on; # 本地时间
 }
}
```

### Apache 静态站点

```apache
<VirtualHost *:80>
 ServerName static.example.com
 DocumentRoot /var/www/static

 <Directory /var/www/static>
 Options -Indexes +FollowSymLinks
 AllowOverride None
 Require all granted
 </Directory>

 # 启用 mod_expires 和 mod_headers 进行缓存
 ExpiresActive On
 ExpiresByType text/css "access plus 1 month"
 ExpiresByType application/javascript "access plus 1 month"
 ExpiresByType image/jpeg "access plus 1 year"
</VirtualHost>
```

---

## 24.6 反向代理概念

反向代理是 Web 服务器将请求转发给后端应用服务器的模式。Nginx 在这方面是行业标准，详细内容见 [[57-Nginx反向代理与负载均衡]]。

```nginx
# Nginx 反向代理基础示例
location /app/ {
 proxy_pass http://127.0.0.1:3000/;
 proxy_set_header Host $host;
 proxy_set_header X-Real-IP $remote_addr;
 proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
 proxy_set_header X-Forwarded-Proto $scheme;
 proxy_connect_timeout 60s;
 proxy_read_timeout 60s;
}

# WebSocket 代理
location /ws/ {
 proxy_pass http://127.0.0.1:3001;
 proxy_http_version 1.1;
 proxy_set_header Upgrade $http_upgrade;
 proxy_set_header Connection "upgrade";
}
```

```apache
# Apache 反向代理（需启用 mod_proxy, mod_proxy_http）
ProxyRequests Off
ProxyPreserveHost On

<Location "/app/">
 ProxyPass http://127.0.0.1:3000/
 ProxyPassReverse http://127.0.0.1:3000/
</Location>
```

---

## 24.7 选择 Nginx 还是 Apache

### 决策指南

| 场景 | 推荐 | 理由 |
|------|------|------|
| 高并发静态文件 | Nginx | 事件驱动，内存效率高 |
| 反向代理 / 负载均衡 | Nginx | 原生设计，性能优异 |
| 共享主机（.htaccess） | Apache | 用户级配置灵活性 |
| PHP 传统应用（WordPress 等） | Apache | mod_php + .htaccess 生态 |
| 微服务网关 | Nginx | 轻量、快速、功能聚焦 |
| 复杂认证/授权 | Apache | 模块更丰富 |
| 初学者入门 | Nginx | 配置文件更简洁直观 |
| 现代应用部署 | Nginx | 与容器、CI/CD 集成更自然 |

### 两者共存

两者可以在同一台服务器上协作：Nginx 作为前端反向代理处理静态文件和 SSL 终结，Apache 作为后端处理动态内容。

```
客户端 → Nginx (:443) → [静态文件直接返回]
 → [动态请求代理到] → Apache (:8080)
```

```nginx
# Nginx 作为前端
server {
 listen 443 ssl;
 server_name example.com;

 location /static/ {
 root /var/www/example.com;
 }

 location / {
 proxy_pass http://127.0.0.1:8080;
 }
}
```

---

## 24.8 相关章节

- [[57-Nginx反向代理与负载均衡]] — Nginx 反向代理高级配置、负载均衡策略
- [[28-系统安全加固与审计]] — Web 服务器安全加固
- [[24-防火墙与安全]] — 防火墙端口控制（80/443）
- [[58-数据库运维(主从+备份+优化)]] — Web 应用后端数据库管理

---

> **小结**：选择 Web 服务器的关键是理解负载特征。Nginx 适合高并发、静态文件和反向代理场景，Apache 在需要 .htaccess 灵活性和丰富模块生态时更合适。无论选择哪个，SSL/TLS 是必须的——Let's Encrypt 让 HTTPS 零成本部署成为可能。
