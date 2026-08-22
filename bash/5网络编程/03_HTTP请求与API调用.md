# HTTP 请求与 API 调用 | HTTP Requests & API Calls

## 章节概述

> **核心理念**：现代应用离不开 HTTP API 调用，Bash 虽然不是首选的 API 客户端语言，但通过 curl 和 jq 的组合，可以快速实现 REST API 交互、JSON 解析和错误处理，适合脚本化和自动化场景。

---

### 第1节：curl 调用 REST API

#### 1.1 GET 请求

```bash
# 基础 GET 请求
curl -s https://api.example.com/users

# 格式化输出 JSON
curl -s https://api.example.com/users | jq .

# 带查询参数
curl -s "https://api.example.com/users?page=1&limit=10"

# 多个查询参数（使用数组）
curl -s "https://api.example.com/users?status=active&role=admin"
```

#### 1.2 POST 请求

```bash
# 发送 JSON 数据
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"name":"John","email":"john@example.com"}' \
  https://api.example.com/users

# 从文件读取 JSON
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d @data.json \
  https://api.example.com/import

# 发送表单数据
curl -s -X POST \
  -d "username=admin&password=secret" \
  https://api.example.com/login
```

#### 1.3 PUT/PATCH/DELETE

```bash
# PUT 更新
curl -s -X PUT \
  -H "Content-Type: application/json" \
  -d '{"name":"John Updated"}' \
  https://api.example.com/users/123

# PATCH 部分更新
curl -s -X PATCH \
  -H "Content-Type: application/json" \
  -d '{"status":"inactive"}' \
  https://api.example.com/users/123

# DELETE 删除
curl -s -X DELETE https://api.example.com/users/123
```

#### 1.4 请求头处理

```bash
# 发送多个头
curl -s \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: $(uuidgen)" \
  -H "X-Correlation-ID: $(uuidgen)" \
  https://api.example.com/users

# 查看响应头
curl -sI https://api.example.com/users

# 只获取响应头
curl -s -o /dev/null -D - https://api.example.com/users
```

### 第2节：JSON 解析（jq）

#### 2.1 jq 基础

```bash
# 格式化 JSON
echo '{"name":"John","age":30}' | jq .

# 提取字段
echo '{"name":"John","age":30}' | jq '.name'

# 提取嵌套字段
echo '{"user":{"name":"John","address":{"city":"NYC"}}}' | jq '.user.address.city'

# 提取数组元素
echo '[{"id":1},{"id":2},{"id":3}]' | jq '.[0]'

# 提取数组元素的字段
echo '[{"id":1,"name":"A"},{"id":2,"name":"B"}]' | jq '.[].name'
```

#### 2.2 jq 高级用法

```bash
# 过滤数组
echo '[{"id":1,"status":"active"},{"id":2,"status":"inactive"}]' | \
  jq '.[] | select(.status == "active")'

# 重命名字段
echo '{"first_name":"John","last_name":"Doe"}' | \
  jq '{name: (.first_name + " " + .last_name)}'

# 合并对象
echo '{"a":1}' | jq '. + {"b":2}'

# 条件判断
echo '{"status":"active"}' | \
  jq 'if .status == "active" then "Enabled" else "Disabled" end'

# 格式化输出
echo '{"users":[{"name":"John"},{"name":"Jane"}]}' | \
  jq -r '.users[] | "\(.name)"'
```

#### 2.3 jq 与 curl 结合

```bash
# 提取用户列表
curl -s https://api.example.com/users | jq '.users[] | {id, name, email}'

# 过滤并格式化
curl -s https://api.example.com/users | \
  jq '.users[] | select(.status == "active") | "\(.name) (\(.email))"'

# 提取第一个用户
curl -s https://api.example.com/users | jq '.users[0]'

# 统计用户数量
curl -s https://api.example.com/users | jq '.users | length'
```

### 第3节：认证处理

#### 3.1 Bearer Token

```bash
# 直接使用 token
TOKEN="your_token_here"
curl -s -H "Authorization: Bearer $TOKEN" https://api.example.com/me

# 从登录响应获取 token
TOKEN=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"secret"}' \
  https://api.example.com/login | jq -r '.token')

# 使用获取的 token
curl -s -H "Authorization: Bearer $TOKEN" https://api.example.com/me
```

#### 3.2 Basic Auth

```bash
# 使用 -u 选项
curl -s -u username:password https://api.example.com/users

# Base64 编码
AUTH=$(echo -n "username:password" | base64)
curl -s -H "Authorization: Basic $AUTH" https://api.example.com/users
```

#### 3.3 API Key

```bash
# 作为头传递
curl -s -H "X-API-Key: your_api_key" https://api.example.com/data

# 作为查询参数
curl -s "https://api.example.com/data?api_key=your_api_key"

# 从环境变量读取
curl -s -H "X-API-Key: $API_KEY" https://api.example.com/data
```

#### 3.4 OAuth 2.0

```bash
# 获取 access_token
TOKEN=$(curl -s -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=$CLIENT_ID&client_secret=$CLIENT_SECRET" \
  https://auth.example.com/token | jq -r '.access_token')

# 使用 token
curl -s -H "Authorization: Bearer $TOKEN" https://api.example.com/data

# 刷新 token
REFRESH_TOKEN="your_refresh_token"
NEW_TOKEN=$(curl -s -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token&refresh_token=$REFRESH_TOKEN" \
  https://auth.example.com/token | jq -r '.access_token')
```

### 第4节：分页处理

#### 4.1 偏移量分页

```bash
#!/bin/bash
# 偏移量分页处理

PAGE=1
LIMIT=100
HAS_MORE=true

while [ "$HAS_MORE" = true ]; do
    RESPONSE=$(curl -s "https://api.example.com/users?page=$PAGE&limit=$LIMIT")
    
    # 处理数据
    echo "$RESPONSE" | jq -r '.users[] | .id'
    
    # 检查是否有更多数据
    COUNT=$(echo "$RESPONSE" | jq '.users | length')
    if [ "$COUNT" -lt "$LIMIT" ]; then
        HAS_MORE=false
    else
        PAGE=$((PAGE + 1))
    fi
done
```

#### 4.2 游标分页

```bash
#!/bin/bash
# 游标分页处理

CURSOR=""
HAS_MORE=true

while [ "$HAS_MORE" = true ]; do
    if [ -z "$CURSOR" ]; then
        RESPONSE=$(curl -s "https://api.example.com/users?limit=100")
    else
        RESPONSE=$(curl -s "https://api.example.com/users?limit=100&cursor=$CURSOR")
    fi
    
    # 处理数据
    echo "$RESPONSE" | jq -r '.users[] | .id'
    
    # 获取下一页游标
    CURSOR=$(echo "$RESPONSE" | jq -r '.next_cursor // empty')
    HAS_MORE=$(echo "$RESPONSE" | jq -r '.has_more')
done
```

#### 4.3 时间戳分页

```bash
#!/bin/bash
# 时间戳分页处理

LAST_TIMESTAMP=""

while true; do
    if [ -z "$LAST_TIMESTAMP" ]; then
        RESPONSE=$(curl -s "https://api.example.com/events?limit=100")
    else
        RESPONSE=$(curl -s "https://api.example.com/events?limit=100&since=$LAST_TIMESTAMP")
    fi
    
    # 处理数据
    EVENT_COUNT=$(echo "$RESPONSE" | jq '.events | length')
    if [ "$EVENT_COUNT" -eq 0 ]; then
        break
    fi
    
    echo "$RESPONSE" | jq -r '.events[] | "\(.timestamp) \(.name)"'
    
    # 更新时间戳
    LAST_TIMESTAMP=$(echo "$RESPONSE" | jq -r '.events[-1].timestamp')
done
```

### 第5节：错误处理

#### 5.1 HTTP 状态码检查

```bash
# 检查响应状态码
RESPONSE=$(curl -s -w "\n%{http_code}" https://api.example.com/users)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

case $HTTP_CODE in
    200)
        echo "Success: $BODY"
        ;;
    401)
        echo "Unauthorized: Check your token"
        exit 1
        ;;
    404)
        echo "Not Found: Resource doesn't exist"
        exit 1
        ;;
    429)
        echo "Rate Limited: Too many requests"
        sleep 60
        ;;
    500)
        echo "Server Error: Try again later"
        exit 1
        ;;
    *)
        echo "Error: HTTP $HTTP_CODE"
        exit 1
        ;;
esac
```

#### 5.2 重试机制

```bash
#!/bin/bash
# 带重试的 API 调用

max_retries=3
retry_delay=5

for ((i=1; i<=max_retries; i++)); do
    RESPONSE=$(curl -s -w "\n%{http_code}" \
        --connect-timeout 10 \
        --max-time 30 \
        https://api.example.com/data)
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" -eq 200 ]; then
        echo "$BODY"
        exit 0
    fi
    
    echo "Attempt $i failed (HTTP $HTTP_CODE)"
    if [ $i -lt $max_retries ]; then
        sleep $retry_delay
    fi
done

echo "All attempts failed"
exit 1
```

#### 5.3 超时处理

```bash
#!/bin/bash
# 超时处理

timeout 30 bash -c '
    RESPONSE=$(curl -s https://api.example.com/slow-endpoint)
    if [ $? -eq 0 ]; then
        echo "$RESPONSE" | jq .
    fi
'

if [ $? -eq 124 ]; then
    echo "Request timed out"
    exit 1
fi
```

### 第6节：综合实战

#### 6.1 GitHub API 调用

```bash
#!/bin/bash
# GitHub API 示例

TOKEN="${GITHUB_TOKEN}"
REPO="owner/repo"

# 获取仓库信息
curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/$REPO" | jq '{name, description, stargazers_count}'

# 获取 issues
curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/$REPO/issues?state=open&per_page=10" | \
  jq '.[] | {number, title, user: .user.login}'

# 创建 issue
curl -s -X POST \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Bug Report","body":"Description of the bug"}' \
  "https://api.github.com/repos/$REPO/issues" | jq '.number'
```

#### 6.2 Kubernetes API 调用

```bash
#!/bin/bash
# Kubernetes API 示例

KUBE_TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
KUBE_CA=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
KUBE_API=https://kubernetes.default.svc

# 获取 pods
curl -s --cacert $KUBE_CA \
  -H "Authorization: Bearer $KUBE_TOKEN" \
  "$KUBE_API/api/v1/namespaces/default/pods" | \
  jq '.items[] | {name: .metadata.name, status: .status.phase}'

# 获取 deployments
curl -s --cacert $KUBE_CA \
  -H "Authorization: Bearer $KUBE_TOKEN" \
  "$KUBE_API/apis/apps/v1/namespaces/default/deployments" | \
  jq '.items[] | {name: .metadata.name, replicas: .spec.replicas}'
```

#### 6.3 AWS API 调用

```bash
#!/bin/bash
# AWS API 示例（简化版）

# 获取 S3 存储桶列表
aws s3 ls | awk '{print $3}'

# 上传文件
aws s3 cp file.txt s3://my-bucket/path/

# 列出对象
aws s3 ls s3://my-bucket/path/ --recursive
```
