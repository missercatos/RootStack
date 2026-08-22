# 网络工具：curl, wget, nc, nmap | Network Tools

## 章节概述

> **核心理念**：网络工具是 Linux 系统管理员和开发者的瑞士军刀——从 HTTP 请求到端口扫描，从文件下载到网络调试，每个工具都有其独特的用途。掌握这些工具就像掌握 C 语言的网络编程库一样重要。

---

### 第1节：curl 选项详解

#### 1.1 基础请求

```bash
# GET 请求
curl https://api.example.com/users

# 输出到文件
curl -o file.tar.gz https://example.com/download.tar.gz

# 仅显示状态码
curl -s -o /dev/null -w "%{http_code}" https://api.example.com/health

# 跟随重定向
curl -L https://example.com

# 显示响应头
curl -I https://api.example.com/users

# 显示详细信息
curl -v https://api.example.com/users
```

#### 1.2 POST 请求

```bash
# 发送表单数据
curl -X POST -d "username=admin&password=secret" https://api.example.com/login

# 发送 JSON 数据
curl -X POST -H "Content-Type: application/json" \
  -d '{"name":"John","email":"john@example.com"}' \
  https://api.example.com/users

# 从文件读取数据
curl -X POST -d @data.json https://api.example.com/import

# 上传文件
curl -X POST -F "file=@document.pdf" https://api.example.com/upload

# 上传多个文件
curl -X POST \
  -F "file1=@photo1.jpg" \
  -F "file2=@photo2.jpg" \
  https://api.example.com/upload
```

#### 1.3 认证与头信息

```bash
# Basic 认证
curl -u username:password https://api.example.com/users

# Bearer Token
curl -H "Authorization: Bearer TOKEN" https://api.example.com/me

# 自定义头
curl -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  https://api.example.com/users

# 使用 cookie
curl -b cookies.txt -c cookies.txt https://example.com/login

# 设置 User-Agent
curl -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" https://example.com
```

#### 1.4 高级选项

```bash
# 限制下载速度
curl --limit-rate 100K https://example.com/large-file.zip

# 设置超时
curl --connect-timeout 10 --max-time 30 https://api.example.com

# 重试
curl --retry 3 --retry-delay 5 https://unstable-api.com

# 忽略 SSL 证书验证（仅测试环境）
curl -k https://self-signed.example.com

# 使用代理
curl -x http://proxy.example.com:8080 https://api.example.com

# 显示下载进度
curl -# -o file.zip https://example.com/download.zip
```

#### 1.5 curl 输出格式

```bash
# 自定义输出格式
curl -s -w "\nHTTP Status: %{http_code}\nTime Total: %{time_total}s\n" \
  -o /dev/null https://api.example.com

# 常用变量
# %{http_code}    - HTTP 状态码
# %{time_total}   - 总耗时
# %{size_download} - 下载大小
# %{speed_download} - 下载速度
```

### 第2节：wget 下载

#### 2.1 基础下载

```bash
# 下载文件
wget https://example.com/file.tar.gz

# 指定输出文件名
wget -O output.zip https://example.com/download

# 断点续传
wget -c https://example.com/large-file.zip

# 后台下载
wget -b https://example.com/large-file.zip

# 递归下载整个网站
wget -r -np -nH --cut-dirs=5 https://example.com/docs/

# 限制下载速度
wget --limit-rate=200k https://example.com/file.zip
```

#### 2.2 wget 高级用法

```bash
# 从文件读取 URL 列表
wget -i urls.txt

# 测试链接是否有效
wget --spider https://example.com

# 下载指定类型的文件
wget -A "*.pdf,*.docx" -r https://example.com/documents/

# 排除指定类型
wget -R "*.html,*.css" -r https://example.com/

# 代理设置
wget -e http_proxy=http://proxy.example.com:8080 https://example.com

# 使用 cookie
wget --load-cookies cookies.txt https://example.com/protected
```

#### 2.3 wget vs curl 对比

| 特性 | wget | curl |
|------|------|------|
| 下载文件 | 更简单 | 需要 `-o` |
| 断点续传 | 内置 `-c` | 需要 `-C -` |
| 递归下载 | 内置 `-r` | 不支持 |
| 后台下载 | 内置 `-b` | 不支持 |
| HTTP 请求 | 有限 | 更强大 |
| API 调用 | 不适合 | 非常适合 |
| 上传文件 | 有限 | 功能丰富 |

### 第3节：nc (netcat)

#### 3.1 端口扫描

```bash
# 扫描单个端口
nc -zv example.com 80

# 扫描端口范围
nc -zv example.com 80-100

# 扫描多个端口
nc -zv example.com 80 443 8080

# 扫描并等待连接
nc -zv -w 3 example.com 80

# TCP 扫描（默认）
nc -zv example.com 80

# UDP 扫描
nc -zuv example.com 53
```

#### 3.2 简单聊天

```bash
# 服务端（监听）
nc -l -p 12345

# 客户端（连接）
nc example.com 12345

# 带聊天界面
nc -l -p 12345 | while read line; do echo "$(date): $line"; done
```

#### 3.3 文件传输

```bash
# 发送文件
nc -l -p 12345 < file.tar.gz

# 接收文件
nc example.com 12345 > received_file.tar.gz

# 发送目录
tar czf - /path/to/dir | nc -l -p 12345

# 接收目录
nc example.com 12345 | tar xzf -

# 带进度显示
pv file.tar.gz | nc -l -p 12345
```

#### 3.4 简单 HTTP 服务器

```bash
# 一行启动 HTTP 服务器
while true; do echo -e "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<h1>Hello</h1>" | nc -l -p 8080; done

# 使用 socat（更强大）
socat TCP-LISTEN:8080,fork,reuseaddr SYSTEM:"echo HTTP/1.1 200 OK; echo Content-Type\: text/html; echo; echo Hello"
```

### 第4节：nmap 基本扫描

#### 4.1 基础扫描

```bash
# 端口扫描
nmap example.com

# 扫描特定端口
nmap -p 80,443 example.com

# 扫描端口范围
nmap -p 1-1024 example.com

# 扫描所有端口
nmap -p- example.com

# 快速扫描常用端口
nmap -F example.com
```

#### 4.2 扫描类型

```bash
# TCP SYN 扫描（半开扫描，需要 root）
sudo nmap -sS example.com

# TCP 连接扫描
nmap -sT example.com

# UDP 扫描
sudo nmap -sU example.com

# 服务版本检测
nmap -sV example.com

# 操作系统检测
sudo nmap -O example.com

# 全面扫描
sudo nmap -A -T4 example.com
```

#### 4.3 nmap 输出

```bash
# 输出为普通格式
nmap -oN scan.txt example.com

# 输出为 XML 格式
nmap -oX scan.xml example.com

# 输出为可脚本使用格式
nmap -oG scan.grep example.com

# 输出为所有格式
nmap -oA scan example.com
```

### 第5节：综合实战

#### 5.1 API 健康检查脚本

```bash
#!/bin/bash
# API 健康检查脚本

URLS=(
    "https://api.example.com/health"
    "https://web.example.com/health"
    "https://db.example.com/health"
)

for url in "${URLS[@]}"; do
    status=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "$url")
    if [ "$status" -eq 200 ]; then
        echo "[OK] $url"
    else
        echo "[FAIL] $url (HTTP $status)"
    fi
done
```

#### 5.2 批量端口扫描

```bash
#!/bin/bash
# 批量扫描多个服务器的常用端口

SERVERS=("web1" "web2" "db1" "db2")
PORTS=(22 80 443 3306 6379 8080)

for server in "${SERVERS[@]}"; do
    echo "=== Scanning $server ==="
    for port in "${PORTS[@]}"; do
        result=$(nc -zv -w 2 "$server" "$port" 2>&1)
        if echo "$result" | grep -q "succeeded"; then
            echo "  Port $port: OPEN"
        else
            echo "  Port $port: CLOSED"
        fi
    done
    echo ""
done
```

#### 5.3 网络速度测试

```bash
#!/bin/bash
# 网络速度测试

# 下载速度测试
echo "=== Download Speed ==="
curl -o /dev/null -w "Speed: %{speed_download} bytes/sec\n" \
  https://speed.cloudflare.com/__down?bytes=10000000

# 上传速度测试
echo "=== Upload Speed ==="
dd if=/dev/zero bs=1M count=10 2>/dev/null | \
  curl -X POST -d @- -w "Speed: %{speed_upload} bytes/sec\n" \
  https://speed.cloudflare.com/__up

# 延迟测试
echo "=== Latency ==="
ping -c 10 8.8.8.8 | tail -1
```
