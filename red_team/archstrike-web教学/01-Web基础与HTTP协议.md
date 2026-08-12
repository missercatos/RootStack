# 01-Web基础与HTTP协议

## 目录
- [[#一、HTTP协议详解|一、HTTP协议详解]]
 - [[#1.1 HTTP请求结构|1.1 HTTP请求结构]]
 - [[#1.2 HTTP请求方法详解|1.2 HTTP请求方法详解]]
 - [[#1.3 HTTP响应结构|1.3 HTTP响应结构]]
 - [[#1.4 HTTP状态码分类|1.4 HTTP状态码分类]]
 - [[#1.5 关键HTTP请求头详解|1.5 关键HTTP请求头详解]]
 - [[#1.6 关键HTTP响应头分析|1.6 关键HTTP响应头分析]]
- [[#二、HTTPS与TLS原理|二、HTTPS与TLS原理]]
 - [[#2.1 TLS握手过程|2.1 TLS握手过程]]
- [[#三、Cookie与Session机制|三、Cookie与Session机制]]
 - [[#3.1 Session工作流程|3.1 Session工作流程]]
 - [[#3.2 Cookie属性安全分析|3.2 Cookie属性安全分析]]
- [[#四、同源策略与CORS|四、同源策略与CORS]]
 - [[#4.1 同源策略|4.1 同源策略]]
 - [[#4.2 CORS跨域资源共享|4.2 CORS跨域资源共享]]
- [[#五、Firefox开发者工具实战|五、Firefox开发者工具实战]]
- [[#六、curl命令行HTTP操作|六、curl命令行HTTP操作]]
 - [[#6.1 curl基础命令|6.1 curl基础命令]]
 - [[#6.2 curl进阶技巧|6.2 curl进阶技巧]]
- [[#七、Burp Suite社区版入门|七、Burp Suite社区版入门]]
- [[#八、实践练习|八、实践练习]]

---

## 一、HTTP协议详解

本模块讨论HTTP协议的核心结构。前置知识请参阅 [[../网安基础知识/02-Web技术基础|Web技术基础]] 和 [[../前端基础/前端基础总目录|前端基础]]。

### 1.1 HTTP请求结构

HTTP请求由**请求行、请求头、空行、请求体**四部分组成。渗透测试中每个部分都有其攻击面。

```mermaid
flowchart LR
 client[客户端浏览器] --> req[构造HTTP请求]
 req --> parse[请求行: 方法+URI+版本]
 parse --> headers[请求头: Host/Cookie/UA...]
 headers --> blank[空行 CRLF]
 blank --> body[请求体: POST数据]
 body --> server[Web服务器处理]
 server --> resp[HTTP响应]
 resp --> client2[客户端渲染]
```

请求行格式：`<方法> <请求URI> <HTTP版本>`

```
GET /search?q=test HTTP/1.1
POST /login.php HTTP/1.1
PUT /upload/file HTTP/1.1
DELETE /user/123 HTTP/1.1
OPTIONS /api/data HTTP/1.1
HEAD /index.html HTTP/1.1
PATCH /user/123 HTTP/1.1
```

### 1.2 HTTP请求方法详解

| 方法 | 用途 | 渗透测试关注点 |
|------|------|--------------|
| GET | 请求资源，参数在URL中 | 参数易被日志记录，可利用IDOR漏洞 |
| POST | 提交数据，参数在请求体 | 数据可被篡改，测试参数污染 |
| PUT | 替换/创建指定资源 | 未授权访问可能导致任意文件上传 |
| DELETE | 删除指定资源 | 未授权删除风险 |
| PATCH | 部分修改资源 | 绕过前端验证修改敏感字段 |
| OPTIONS | 查询服务器支持的方法 | 可能泄露服务器配置信息 |
| HEAD | 同GET但只返回响应头 | 探测资源是否存在 |
| TRACE | 回显请求 | 存在XST跨站追踪漏洞风险 |
| CONNECT | 建立隧道 | 用于HTTPS代理 |

**渗透测试关注点：**
- GET参数容易被日志记录，可利用IDOR漏洞
- POST数据可被篡改，测试参数污染
- PUT/DELETE未授权访问可能导致任意文件上传/删除
- OPTIONS可能泄露服务器配置信息
- TRACE可能被利用进行XST攻击

### 1.3 HTTP响应结构

HTTP响应由**状态行、响应头、空行、响应体**组成：

```mermaid
flowchart TD
 S[服务器处理完成] --> SL[状态行: HTTP版本 状态码 原因短语]
 SL --> RH[响应头: Server/Set-Cookie/CSP...]
 RH --> BL[空行 CRLF]
 BL --> RB[响应体: HTML/JSON/XML...]
 RB --> END[浏览器解析渲染]
```

### 1.4 HTTP状态码分类

**1xx - 信息性响应：**
- `100 Continue` — 继续发送请求体
- `101 Switching Protocols` — 协议切换（WebSocket升级）

**2xx - 成功响应：**
- `200 OK` — 请求成功
- `201 Created` — 资源已创建
- `204 No Content` — 成功但无返回内容

**3xx - 重定向：**
- `301 Moved Permanently` — 永久重定向
- `302 Found` — 临时重定向（常被利用做钓鱼）
- `304 Not Modified` — 缓存有效
- `307 Temporary Redirect` — 保持请求方法不变的重定向

**4xx - 客户端错误（信息泄露重灾区）：**
- `400 Bad Request` — 请求格式错误
- `401 Unauthorized` — 需要认证
- `403 Forbidden` — 禁止访问（可能有隐藏资源）
- `404 Not Found` — 可探测目录结构
- `405 Method Not Allowed` — 可枚举允许的方法
- `413 Payload Too Large` — 请求体过大
- `429 Too Many Requests` — 频率限制（WAF/rate-limit）

**5xx - 服务器错误（可能泄露敏感信息）：**
- `500 Internal Server Error` — 输入异常可能触发SQL报错
- `502 Bad Gateway` — 可能存在SSRF
- `503 Service Unavailable` — 服务不可用
- `504 Gateway Timeout` — 网关超时

**渗透利用要点：** 400/403/404探测隐藏目录；500错误暴露数据库信息和绝对路径；3xx配合开放重定向漏洞进行钓鱼。

### 1.5 关键HTTP请求头详解

| 请求头 | 示例 | 攻击面 |
|--------|------|--------|
| `Host` | `example.com` | Host头注入 — 密码重置劫持、缓存投毒 |
| `User-Agent` | `Mozilla/5.0 ... Firefox/128.0` | 可伪造绕过简单UA检测 |
| `Cookie` | `PHPSESSID=abc123; security=low` | 会话劫持、Cookie注入、会话固定 |
| `Referer` | `http://example.com/page1` | 泄露敏感URL参数；检测CSRF防护 |
| `Authorization` | `Basic YWRtaW46cGFzc3dvcmQ=` | Base64编码非加密，可轻易解码 |
| `X-Forwarded-For` | `127.0.0.1` | 伪造后绕过IP限制、SQL注入IP字段 |
| `Content-Type` | `application/x-www-form-urlencoded` | 修改绕过WAF或实现文件上传 |

### 1.6 关键HTTP响应头分析

```
Server: Apache/2.4.41 (Ubuntu) # 泄露服务器版本 → 找准已知漏洞
X-Powered-By: PHP/7.4.3 # 泄露后端语言及版本 → 精准攻击

Set-Cookie: PHPSESSID=abc123; HttpOnly; Secure; SameSite=Strict
 HttpOnly → 阻止JavaScript读取Cookie（防XSS窃取）
 Secure → 仅通过HTTPS传输
 SameSite → 跨站请求控制（防CSRF）

Access-Control-Allow-Origin: * # CORS配置* → 存在CORS漏洞
Content-Security-Policy: default-src 'self' # CSP安全策略
X-Frame-Options: DENY # 防Clickjacking
X-Content-Type-Options: nosniff # 防MIME类型嗅探
Strict-Transport-Security: max-age=31536000 # HSTS强制HTTPS
```

渗透测试信息收集关注点：收集Server/X-Powered-By版本信息；检查安全头缺失；分析CORS宽松策略。

---

## 二、HTTPS与TLS原理

### 2.1 TLS握手过程

```mermaid
sequenceDiagram
 participant C as 客户端
 participant S as 服务器

 C->>S: (1) ClientHello<br/>支持的加密套件, 随机数1
 S->>C: (2) ServerHello<br/>选定加密套件, 随机数2, 证书
 C->>S: (3) ClientKeyExchange<br/>用服务器公钥加密的预主密钥
 C->>S: (4) ChangeCipherSpec<br/>切换加密
 S->>C: (5) ChangeCipherSpec<br/>切换加密
 Note over C,S: (6) 对称加密数据传输
 C<-->S: AES/ChaCha20 加密通信
```

关键概念：
- 非对称加密（RSA/ECDHE）用于密钥交换
- 对称加密（AES/ChaCha20）用于数据传输
- 数字证书由CA签发，用于验证服务器身份

渗透测试中的HTTPS：
- 使用Burp Suite导入CA证书即可拦截HTTPS流量
- 证书验证不当可能导致中间人攻击
- Heartbleed等SSL/TLS库漏洞可泄露内存数据

---

## 三、Cookie与Session机制

### 3.1 Session工作流程

HTTP是无状态协议，每次请求都是独立的。服务器需要Session机制识别"这个请求来自哪个用户"。

```mermaid
flowchart LR
 A[用户登录] --> B[服务器验证凭证]
 B --> C[创建Session]
 C --> D[生成SessionID]
 D --> E[Set-Cookie返回]
 E --> F[浏览器存储Cookie]
 F --> G[后续请求自动携带Cookie]
 G --> H[服务器查找Session]
 H --> I[识别用户身份]
```

### 3.2 Cookie属性安全分析

```
Set-Cookie: session=abc123; Domain=.example.com; Path=/;
 Expires=Wed, 21 Oct 2026 07:28:00 GMT;
 HttpOnly; Secure; SameSite=Lax
```

| 属性 | 作用 | 渗透视角 |
|------|------|---------|
| `Domain` | Cookie作用域 | 设置过宽 → 子域劫持可窃取Cookie |
| `Path` | Cookie作用路径 | 配合路径限制访问 |
| `Expires/Max-Age` | 过期时间，不设置则为会话Cookie | 持久Cookie增加窃取窗口 |
| `HttpOnly` | 防止JavaScript访问 | 没有 → XSS可直接`document.cookie`窃取 |
| `Secure` | 仅HTTPS传输 | 没有 → 中间人可截获Cookie |
| `SameSite` | Strict/Lax/None | None → CSRF攻击更容易 |
| 可预测的SessionID | — | 会话劫持 |

---

## 四、同源策略与CORS

### 4.1 同源策略

定义：**协议 + 域名 + 端口** 三者完全相同才算同源。

以 `http://example.com:80/page` 为例：
- `http://example.com:80/other` → **同源**
- `https://example.com:80/page` → 不同源（协议不同）
- `http://sub.example.com:80/` → 不同源（域名不同）
- `http://example.com:8080/` → 不同源（端口不同）

同源策略限制：
1. 不同源的DOM无法互相访问
2. 不同源的Cookie/LocalStorage无法读取
3. 不同源的AJAX请求被阻止（但请求可能发出 — **CSRF利用点！**）

### 4.2 CORS跨域资源共享

CORS是为了放宽同源策略而设计的机制。

**CORS常见漏洞模式：**
1. `Access-Control-Allow-Origin: *` 加上 `Allow-Credentials: true` → 任意域可读取带凭证的响应（高危！）
2. `Access-Control-Allow-Origin` 反射Origin头 → 任意域都可被信任
3. 子域名CORS配置宽松 → 结合子域劫持实现攻击

---

## 五、Firefox开发者工具实战

Firefox开发者工具是渗透测试中最常用的分析工具之一。参见 [[../前端基础/前端基础总目录|前端基础]] 了解DOM和JS基础。

```mermaid
flowchart TD
 F12[按F12打开] --> PANEL{选择面板}
 PANEL --> NET[Network: HTTP流量分析]
 PANEL --> CON[Console: 执行JS/查看错误]
 PANEL --> STO[Storage: Cookie/Storage查看]
 PANEL --> INS[Inspector: DOM编辑]
 PANEL --> DEB[Debugger: JS断点调试]
 PANEL --> SEC[Security: TLS证书]
 NET --> COPY[右键→Copy as cURL]
 CON --> COOKIE[document.cookie]
 STO --> EDIT[双击修改Cookie值]
 INS --> HTML[Edit as HTML]
```

**关键操作：**
- **Network标签：** 刷新页面观察所有请求 → 点击请求查看Headers/Cookies/Params/Response/Timings
- **筛选：** XHR仅看AJAX请求；JS/CSS/Img按资源类型过滤
- **右键请求 → 复制 → 复制为cURL：** 直接粘贴到终端使用
- **Console：** `document.cookie`查看Cookie；`navigator.userAgent`查看UA；`alert(document.domain)`测试弹窗
- **Storage：** 展开Cookies查看每个Cookie属性（HttpOnly/Secure/SameSite）
- **Inspector：** 查找隐藏的`<input type="hidden">`字段 — 可能存在可被篡改的敏感参数

---

## 六、curl命令行HTTP操作

### 6.1 curl基础命令

```bash
# 基本GET请求并显示响应头
curl -v http://testphp.vulnweb.com

# 仅显示响应头
curl -I http://testphp.vulnweb.com

# 跟随重定向
curl -L http://testphp.vulnweb.com

# 指定User-Agent
curl -A "CustomScanner/1.0" http://testphp.vulnweb.com

# 发送POST请求
curl -X POST -d "user=admin&pass=123" http://testphp.vulnweb.com/login.php

# 发送JSON数据
curl -X POST -H "Content-Type: application/json" \
 -d '{"user":"admin","pass":"123"}' http://example.com/api/login

# 携带Cookie
curl -b "PHPSESSID=abc123; security=low" http://example.com/page

# 保存响应到文件
curl -o output.html http://testphp.vulnweb.com

# 指定代理（配合Burp Suite）
curl -x http://127.0.0.1:8080 http://testphp.vulnweb.com

# 忽略SSL证书验证（测试环境可用）
curl -k https://self-signed.example.com

# 完整输出调试信息（包含SSL握手细节）
curl -vvv --trace-ascii trace.log https://example.com
```

### 6.2 curl进阶技巧

```bash
# 发送自定义头部
curl -H "X-Forwarded-For: 127.0.0.1" \
 -H "X-Forwarded-Host: internal.local" \
 http://example.com

# 上传文件
curl -F "file=@/path/to/shell.php" http://example.com/upload.php

# 指定HTTP方法（如PUT上传）
curl -X PUT -d @file.txt http://example.com/uploads/

# 测试HTTP方法
curl -X OPTIONS -v http://example.com

# 时间分析
curl -w "DNS: %{time_namelookup}s | Connect: %{time_connect}s | \
 TLS: %{time_appconnect}s | TTFB: %{time_starttransfer}s | \
 Total: %{time_total}s\n" -o /dev/null -s https://example.com
```

---

## 七、Burp Suite社区版入门

Burp Suite是Web渗透测试的瑞士军刀。ArchStrike中自带社区版。

```mermaid
flowchart TD
 B[启动Burp: burpsuite] --> P[临时项目 → Burp默认 → 启动]
 P --> PR[Proxy → Intercept标签]
 PR --> FF[Firefox代理: 127.0.0.1:8080]
 FF --> CERT[安装Burp CA证书: http:// burpsuite]
 CERT --> INT[开启Intercept → 拦截请求]
 INT --> ACT{操作}
 ACT --> FWD[Forward放行]
 ACT --> DROP[Drop丢弃]
 ACT --> EDIT[修改后Forward]
 ACT --> REP[Send to Repeater]
 REP --> SEND[Repeater中修改并重放]
```

**步骤概览：**
1. 终端输入 `burpsuite` 启动
2. 选择 "Temporary project" → "Use Burp defaults" → "Start Burp"
3. 确认代理监听在 `127.0.0.1:8080`
4. Firefox设置 → 手动代理配置 → HTTP代理 `127.0.0.1` 端口 `8080`，勾选"也将此代理用于HTTPS"
5. Firefox访问 `http://burpsuite` → 下载CA证书 → 导入并信任
6. 开启 Intercept → 访问目标 → 观察拦截的请求 → Forward放行

**Repeater重放：** 右键任意请求 → Send to Repeater → 修改请求 → 点击Send → 观察响应。用于手工测试和参数调优。

---

## 八、实践练习

### 实践任务 01-1：使用Firefox开发者工具分析HTTP流量

1. 打开Firefox，访问 `http://testphp.vulnweb.com`
2. 按F12 → Network标签 → 刷新页面
3. 找到第一个请求（一般是GET /），记录请求方法、状态码、Server头部、X-Powered-By头部、Content-Type
4. 点击任意链接观察产生的新请求
5. 搜索 "test"，观察GET参数 `?search=test` 的请求
6. 右键该请求 → 复制 → 复制为cURL → 粘贴到终端执行，对比结果

### 实践任务 01-2：使用curl测试HTTP

```bash
curl -I http://testphp.vulnweb.com
curl -v http://testphp.vulnweb.com/AJAX/index.php
curl -X OPTIONS -v http://testphp.vulnweb.com
curl -b "fakecookie=test123" http://testphp.vulnweb.com
```

### 实践任务 01-3：Burp Suite代理拦截

1. 启动Burp Suite → 配置Firefox代理
2. 访问 `http://testphp.vulnweb.com`
3. 在Burp中拦截请求 → 修改User-Agent为 `"Hacker/1.0"` → Forward
4. 在HTTP history中确认User-Agent已修改

### 实践任务 01-4：分析Cookie和Session

1. Firefox访问 `http://testphp.vulnweb.com`
2. F12 → Storage标签 → 观察Cookie列表
3. Console输入 `document.cookie` — 观察哪些Cookie可被JS读取（非HttpOnly）
4. 修改某个Cookie值，刷新页面观察变化

---

**常见问题：**
- **Q: Burp拦截HTTPS时Firefox显示安全警告？** A: 需要正确安装Burp CA证书，访问 `http://burpsuite` 下载并导入。
- **Q: `curl -I` 返回405 Method Not Allowed？** A: 某些服务器不接受HEAD方法，改用 `curl -v` 发送GET即可。
- **Q: Burp代理后无法联网？** A: 检查Burp是否开启了Intercept导致请求被拦截未Forward。

[[../总目录与快速查询|← 返回总目录]] | 下一模块：[[02-Web信息收集与侦察|02-Web信息收集与侦察]]
