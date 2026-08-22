# Bash 中的 Socket 编程：/dev/tcp | Socket Programming in Bash

## 章节概述

> **核心理念**：Bash 内置了 TCP/UDP 网络支持，通过 `/dev/tcp/host/port` 特殊文件可以直接进行 socket 操作，无需额外工具。这类似于 C 语言的 socket API，但更加简洁。

---

### 第1节：/dev/tcp/host/port

#### 1.1 基础连接

```bash
# 打开 TCP 连接
exec 3<>/dev/tcp/example.com/80

# 发送 HTTP 请求
echo -e "GET / HTTP/1.1\r\nHost: example.com\r\n\r\n" >&3

# 读取响应
cat <&3

# 关闭连接
exec 3>&-
```

#### 1.2 语法详解

```bash
# /dev/tcp 是 Bash 内置的特殊文件
# 语法: /dev/tcp/host/port

# 打开连接
exec 3<>/dev/tcp/192.168.1.100/22

# 使用域名
exec 3<>/dev/tcp/example.com/443

# UDP 连接
exec 3<>/dev/udp/example.com/53
```

### 第2节：文件描述符读写

#### 2.1 文件描述符操作

```bash
# 分配文件描述符
exec 3<> /dev/tcp/host/port

# 读取数据
read -t 5 line <&3

# 写入数据
echo "data" >&3

# 关闭文件描述符
exec 3>&-

# 关闭输入端
exec 3<&-

# 关闭输出端
exec 3>&-
```

#### 2.2 多文件描述符

```bash
# 同时管理多个连接
exec 3<>/dev/tcp/server1/80
exec 4<>/dev/tcp/server2/80

echo "Request 1" >&3
echo "Request 2" >&4

read response1 <&3
read response2 <&4

exec 3>&- 4>&-
```

### 第3节：TCP 服务器/客户端

#### 3.1 简单 TCP 服务器

```bash
#!/bin/bash
# 简单 TCP 服务器

PORT=12345

echo "Starting server on port $PORT..."

while true; do
    # 接受连接
    exec 3<>/dev/tcp/0.0.0.0/$PORT
    
    # 读取客户端数据
    read -t 10 client_data <&3
    echo "Received: $client_data"
    
    # 发送响应
    echo "Echo: $client_data" >&3
    
    # 关闭连接
    exec 3>&-
done
```

#### 3.2 并发 TCP 服务器

```bash
#!/bin/bash
# 并发 TCP 服务器

PORT=12345
MAX_CLIENTS=5

handle_client() {
    local client_fd=$1
    read -t 30 data <&$client_fd
    echo "Client sent: $data"
    echo "Response from server" >&$client_fd
    exec $client_fd>&-
}

# 监听并处理连接
exec 4<>/dev/tcp/0.0.0.0/$PORT

while true; do
    # 使用文件描述符 4 监听
    # 接受新连接到文件描述符 5
    exec 5<>/dev/tcp/0.0.0.0/$PORT
    
    # 后台处理客户端
    handle_client 5 &
    
    # 限制并发数
    while [ $(jobs -r | wc -l) -ge $MAX_CLIENTS ]; do
        wait -n
    done
done
```

#### 3.3 TCP 客户端

```bash
#!/bin/bash
# 简单 TCP 客户端

SERVER="example.com"
PORT=80

# 连接服务器
exec 3<>/dev/tcp/$SERVER/$PORT

# 发送数据
echo -e "GET / HTTP/1.1\r\nHost: $SERVER\r\n\r\n" >&3

# 读取响应
timeout 10 cat <&3

# 关闭连接
exec 3>&-
```

### 第4节：UDP 支持

#### 4.1 UDP 客户端

```bash
#!/bin/bash
# UDP 客户端

SERVER="8.8.8.8"
PORT=53

# 打开 UDP 连接
exec 3<>/dev/udp/$SERVER/$PORT

# 发送 DNS 查询（示例）
echo -ne '\x00\x01\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01' >&3

# 读取响应
timeout 5 cat <&3 | xxd

# 关闭连接
exec 3>&-
```

#### 4.2 UDP 服务器

```bash
#!/bin/bash
# UDP 服务器

PORT=9999

while true; do
    # 监听 UDP
    exec 3<>/dev/udp/0.0.0.0/$PORT
    
    # 读取数据
    read -t 10 data <&3
    echo "Received UDP: $data"
    
    # 发送响应
    echo "UDP Response" >&3
    
    exec 3>&-
done
```

### 第5节：超时设置

#### 5.1 连接超时

```bash
# 使用 timeout 命令
timeout 5 bash -c 'echo "data" > /dev/tcp/example.com/80'

# 使用 select 进行超时检测
{
    exec 3<>/dev/tcp/example.com/80
} 2>/dev/null

if [ $? -ne 0 ]; then
    echo "Connection failed"
fi
```

#### 5.2 读取超时

```bash
# read 的 -t 选项
exec 3<>/dev/tcp/example.com/80
read -t 10 response <&3
if [ $? -gt 128 ]; then
    echo "Read timed out"
fi
exec 3>&-
```

#### 5.3 写入超时

```bash
# 使用 timeout 限制写入时间
exec 3<>/dev/tcp/example.com/80
timeout 5 bash -c 'echo "data" >&3'
if [ $? -eq 124 ]; then
    echo "Write timed out"
fi
exec 3>&-
```

### 第6节：实际应用

#### 6.1 HTTP 客户端

```bash
#!/bin/bash
# 使用 /dev/tcp 的 HTTP 客端

http_get() {
    local host=$1
    local path=${2:-/}
    local port=80
    
    exec 3<>/dev/tcp/$host/$port
    
    echo -e "GET $path HTTP/1.1\r\nHost: $host\r\nConnection: close\r\n\r\n" >&3
    
    while IFS= read -t 10 line; do
        echo "$line"
    done <&3
    
    exec 3>&-
}

http_get example.com
```

#### 6.2 简单代理服务器

```bash
#!/bin/bash
# 简单 TCP 代理

LISTEN_PORT=8080
REMOTE_HOST="example.com"
REMOTE_PORT=80

exec 4<>/dev/tcp/0.0.0.0/$LISTEN_PORT

while true; do
    exec 5<>/dev/tcp/$REMOTE_HOST/$REMOTE_PORT
    
    # 双向数据转发
    while true; do
        read -t 5 data <&5 && echo "$data" >&5 &
        read -t 5 data <&5 && echo "$data" >&4 &
    done &
    
    exec 5>&-
done
```

#### 6.3 网络测试工具

```bash
#!/bin/bash
# 测试端口连通性

test_port() {
    local host=$1
    local port=$2
    local timeout=${3:-5}
    
    timeout $timeout bash -c "echo >/dev/tcp/$host/$port" 2>/dev/null
    return $?
}

# 测试多个端口
for port in 22 80 443 3306 6379; do
    if test_port "example.com" $port; then
        echo "Port $port: OPEN"
    else
        echo "Port $port: CLOSED"
    fi
done
```
