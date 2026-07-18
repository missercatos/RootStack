## 目录

- [[#一、REST API基础|一、REST API基础]]
- [[#二、API认证方式|二、API认证方式]]
- [[#三、API参数攻击|三、API参数攻击]]
- [[#四、IDOR不安全的直接对象引用|四、IDOR]]
- [[#五、批量赋值攻击|五、批量赋值攻击]]
- [[#六、API速率限制绕过|六、API速率限制绕过]]
- [[#七、API版本化安全问题|七、API版本化安全问题]]
- [[#八、红队视角总结|八、红队视角总结]]

---

## 一、REST API基础

### RESTful资源命名

```
GET    /api/users           # 列表
POST   /api/users           # 创建
GET    /api/users/123       # 详情
PUT    /api/users/123       # 全量更新
PATCH  /api/users/123       # 部分更新
DELETE /api/users/123       # 删除
```

### API文档与发现

```bash
# Swagger / OpenAPI
curl https://target.com/swagger.json
curl https://target.com/api-docs
curl https://target.com/v2/api-docs
curl https://target.com/v3/api-docs

# 常见文档路径
/api/swagger.json
/api/v1/openapi.json
/swagger-ui.html
/docs
/redoc
/graphql  (GraphQL的内省查询)
```

## 二、API认证方式

### 常见认证方式

| 方式 | Header示例 | 安全等级 | 常见漏洞 |
|------|-----------|:---:|---------|
| Bearer Token | `Authorization: Bearer eyJ...` | 中 | Token泄露、弱签名 |
| API Key | `X-API-Key: abc123` | 低 | 可预测、泄露在代码中 |
| Basic Auth | `Authorization: Basic base64(user:pass)` | 低 | 明文传输、base64可解码 |
| OAuth 2.0 | `Authorization: Bearer access_token` | 高 | 配置错误 |
| Session Cookie | `Cookie: session=abc` | 中 | CSRF、Session固定 |
| HMAC签名 | `X-Signature: sha256=...` | 高 | 时间戳验证不当 |

### JWT API认证方案

```javascript
// Access Token + Refresh Token 模式
// 短生命期Access Token（15分钟）
// 长生命期Refresh Token（7天）

// 请求API时：
fetch('/api/data', {
  headers: { 'Authorization': `Bearer ${accessToken}` }
});

// Token过期后：
fetch('/api/refresh', {
  method: 'POST',
  credentials: 'include',  // Refresh Token在HttpOnly Cookie中
}).then(r => r.json())
  .then(data => { accessToken = data.access_token; });
```

## 三、API参数攻击

### 参数污染 (Parameter Pollution)

```http
# 原始请求
GET /api/user?id=123

# 参数污染
GET /api/user?id=123&id=456
# 不同框架处理方式不同：
# PHP → 取最后一个：456
# Node.js (Express) → 取第一个：123
# Python (Flask) → 取第一个：123
# Java (Spring) → 取第一个或最后一个（版本有关）
# .NET → 数组：123,456

# 利用：绕过过滤器
GET /api/admin?id=1&id=2  # 如果过滤器检查id=1但实际执行id=2
```

### 参数类型混淆

```json
# 原始期望
{ "id": 123 }

# 类型混淆payload
{ "id": "123" }                 # string 代替 number
{ "id": [123] }                 # array 代替 number
{ "id": { "$gt": 0 } }         # MongoDB注入！
{ "id": true }                  # boolean
{ "id": null }                  # null
```

### 深层参数注入

```json
# 原始
{ "user": { "name": "Alice" } }

# 注入额外参数
{ "user": { "name": "Alice", "role": "admin" } }

# 或通过扁平的参数名
# user[role]=admin
# user.isAdmin=true
```

## 四、IDOR（不安全的直接对象引用）

### 原理

当API使用可预测的ID直接引用对象，且未做权限检查时：

```
# 用户A只能看到自己的订单
GET /api/orders/1234  → 200 OK {order for user A}

# 但可以枚举其他用户的订单
GET /api/orders/1235  → 200 OK {order for user B}  ← IDOR！
GET /api/orders/1236  → 200 OK {order for user C}
```

### IDOR测试方法

```bash
# 1. 创建两个账号A和B
# 2. 用A登录，记录A的资源ID
# 3. 用A的Session，尝试访问B的资源ID
# 4. 如果成功 → IDOR

# 自动化IDOR测试 (Autorize Burp插件)
# 插件自动替换Cookie/Token，检测跨账号访问
```

### IDOR常见目标

| 端点 | 参数 | 风险 |
|------|------|------|
| `/api/users/<id>` | 递增数值ID | 用户枚举 |
| `/api/orders/<uuid>` | UUID也可能被猜测 | 订单泄露 |
| `/api/files/<hash>` | 文件Hash | 任意文件下载 |
| `/api/invoices/<id>` | PDF发票ID | 财务数据泄露 |
| `/api/admin/users/<id>` | 管理员API未鉴权 | 水平/垂直越权 |

## 五、批量赋值攻击

### 原理

API接收整个JSON对象并直接写入数据库，攻击者可以注入额外的字段：

```json
// 注册接口的预期请求
POST /api/register
{ "username": "newuser", "password": "password123" }

// 批量赋值攻击
POST /api/register
{ 
  "username": "newuser",
  "password": "password123",
  "role": "admin",         // ← 注入角色字段
  "isVerified": true,      // ← 绕过邮箱验证
  "balance": 999999        // ← 修改余额
}
```

### 不同框架的批量赋值

| 框架 | 脆弱模式 | 防御 |
|------|---------|------|
| Django | ModelForm未指定fields | `fields = ['name', 'email']` |
| Rails | 未使用strong parameters | `params.require(:user).permit(:name, :email)` |
| Express | 直接spread req.body | 手动白名单 |
| Spring | 未使用@JsonIgnore | + `@JsonProperty(access = READ_ONLY)` |
| Laravel | 未使用$fillable/$guarded | `protected $fillable = [...]` |

### 检测方法

```bash
# 1. 正常请求，记录所有参数
POST /api/profile
{"name": "Alice", "email": "alice@example.com"}

# 2. 添加额外字段
POST /api/profile
{"name": "Alice", "email": "alice@example.com", "isAdmin": true, "role": "admin"}

# 3. 检查是否有非预期行为
GET /api/profile
{"name": "Alice", "email": "alice@example.com", "role": "admin"}  # ← 批量赋值成功！
```

## 六、API速率限制绕过

### 绕过技术

```bash
# 1. 修改请求来源
X-Forwarded-For: 127.0.0.1
X-Real-IP: 10.0.0.1

# 2. 在参数中添加空值
GET /api/user?limit=100&limit=200&limit=300
# 可能绕过limit检查

# 3. 使用不同的端点
GET /api/users/1
GET /api/v2/users/1
GET /api/admin/users/1
# 不同端点可能有不同的速率限制

# 4. 同时使用多种认证方式
GET /api/user → API Key
GET /api/user?access_token=xxx → Bearer
# 不同的认证方式可能独立计数

# 5. 使用分页绕过
GET /api/users?page=1&per_page=1
GET /api/users?page=2&per_page=1
# 每页1条，快速遍历
```

## 七、API版本化安全问题

### 版本间的安全问题

```
/api/v1/users (有权限检查)
/api/v2/users (开发中，可能无权限检查)
/api/users (默认路由，可能连到过期版本)
/api/internal/users (内部API，可能绕过鉴权)
/api/beta/users  (Beta版本，权限不完善)
```

### 常见版本路径

```bash
# 版本路径探测
/api/v1/
/api/v2/
/api/latest/
/api/deprecated/
/api/internal/
/api/admin/
/api/legacy/
/api/old/

# 检测各版本的权限差异
GET /api/v1/admin/users → 403 Forbidden
GET /api/v2/admin/users → 200 OK  ← 新版本未配置权限！
```

## 八、红队视角总结

### API测试检查清单

- [ ] 所有端点都列出了吗？（Swagger/OpenAPI文档发现）
- [ ] 认证是否在所有端点一致？
- [ ] 参数污染是否导致未预期行为？
- [ ] 是否存在IDOR？（跨账号资源访问）
- [ ] 批量赋值是否可以修改敏感字段？
- [ ] 速率限制是否可绕过？
- [ ] 不同API版本之间权限是否一致？
- [ ] 是否使用了不安全的HTTP方法？（PUT/DELETE）

### 工具

| 工具 | 用途 |
|------|------|
| Burp Suite + Autorize | 自动化IDOR检测 |
| Postman Collections | 批量API测试 |
| Arjun | HTTP参数发现 |
| Kiterunner | API端点爆破 |
| ffuf | API目录fuzzing |
| Swagger Parser | OpenAPI文档分析 |

---
**返回** [[../前端基础总目录|前端基础总目录]]
