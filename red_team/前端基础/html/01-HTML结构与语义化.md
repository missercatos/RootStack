## 目录

- [[#一、文档类型声明|一、文档类型声明]]
- [[#二、HTML基本结构|二、HTML基本结构]]
- [[#三、常用标签全集|三、常用标签全集]]
- [[#四、属性系统|四、属性系统]]
- [[#五、DOM树与渲染流程|五、DOM树与渲染流程]]
- [[#六、HTML解析器的特性|六、HTML解析器的特性]]
- [[#七、红队视角总结|七、红队视角总结]]

---

## 一、文档类型声明

`<!DOCTYPE html>` 告诉浏览器使用标准模式（Standards Mode）渲染。没有它，浏览器进入怪异模式（Quirks Mode），布局行为完全不同。

```
<!DOCTYPE html>
<html lang="zh-CN">
```

红队关注点：某些老旧网站的怪异模式可能产生特殊的解析行为，可用于绕过XSS过滤。

## 二、HTML基本结构

```
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'">
  <title>页面标题</title>
  <link rel="stylesheet" href="style.css">
  <script src="app.js" defer></script>
</head>
<body>
  <div id="app">
    <h1>Hello World</h1>
    <p>这是一个段落</p>
  </div>
</body>
</html>
```

红队关注 `<meta http-equiv>` 标签：它可以在HTML层面设置CSP策略、重定向、Cookie等安全属性。理解`<meta>` 的 `http-equiv` 能力可帮助绕过某些安全限制。

## 三、常用标签全集

### 文本标签

| 标签 | 作用 | 安全相关 |
|------|------|---------|
| `<h1>-<h6>` | 标题 | 无直接影响 |
| `<p>` | 段落 | 无直接影响 |
| `<span>` | 行内容器 | 常用于XSS payload载体 |
| `<div>` | 块级容器 | 同上 |
| `<a>` | 超链接 | `javascript:` 伪协议、`target=_blank` 的 tabnabbing |
| `<br>` | 换行 | 可绕过某些基于长度的过滤器 |
| `<pre>` | 预格式化 | 保留空格，可混淆payload |
| `<code>` | 代码片段 | 与 `<pre>` 组合显示代码 |

### 媒体标签

| 标签 | XSS利用 |
|------|---------|
| `<img>` | `onerror=alert(1)`, `src=x` |
| `<svg>` | `<svg/onload=alert(1)>` |
| `<video>` | `<video><source onerror=alert(1)>` |
| `<audio>` | 同上 |
| `<object>` | `data=javascript:alert(1)` |
| `<embed>` | 同上 |

### 脚本相关

| 标签 | XSS利用 |
|------|---------|
| `<script>` | 最直接的XSS载体 |
| `<iframe>` | `srcdoc` 注入、sandbox绕过 |
| `<noscript>` | 无JS环境下的备用内容 |
| `<template>` | 内容不立即渲染，延迟XSS |
| `<style>` | CSS注入（可配合`@import`跨域） |

## 四、属性系统

### 通用属性（Global Attributes）

| 属性 | 说明 | 安全关注 |
|------|------|---------|
| `id` | 唯一标识 | DOM Clobbering：id与全局变量冲突 |
| `class` | CSS类 | 无直接影响 |
| `style` | 内联样式 | CSS注入入口 |
| `title` | 悬浮提示 | 可嵌入恶意内容（但通常不执行） |
| `hidden` | 隐藏元素 | 可用于隐蔽钓鱼页面元素 |
| `tabindex` | Tab键顺序 | 可用于操控用户焦点 |
| `contenteditable` | 可编辑 | 配合DOM XSS |

### 事件属性（Event Handler Attributes）

这是XSS最直接的利用方式：

| 事件 | 触发条件 | 典型payload |
|------|---------|------------|
| `onerror` | 资源加载失败 | `<img src=x onerror=alert(1)>` |
| `onload` | 元素加载完成 | `<body onload=alert(1)>` |
| `onclick` | 点击 | `<div onclick=alert(1)>` |
| `onfocus` | 获得焦点 | `<input autofocus onfocus=alert(1)>` |
| `onmouseover` | 鼠标悬停 | `<div onmouseover=alert(1)>` |
| `onanimationend` | 动画结束 | CSS动画自动触发（无需用户交互） |
| `ontransitionend` | 过渡结束 | CSS过渡自动触发 |
| `oninput` | 输入时 | `<input oninput=alert(1)>` |

无需用户交互的XSS最佳事件：`onerror`, `onload`, `onfocus(autofocus)`, `onanimationend`

### URL属性（危险）

这些属性接受URL，可注入 `javascript:` 伪协议：

| 属性 | 标签 | payload |
|------|------|---------|
| `src` | script, img, iframe | `<iframe src=javascript:alert(1)>` |
| `href` | a, link, area | `<a href=javascript:alert(1)>` |
| `action` | form | `<form action=javascript:alert(1)>` |
| `formaction` | button, input | `<button formaction=javascript:alert(1)>` |
| `data` | object | `<object data=javascript:alert(1)>` |

## 五、DOM树与渲染流程

浏览器从HTML到页面渲染的步骤：

1. **字节流 → 字符流**：根据编码（`<meta charset>`）解码
2. **字符流 → Token**：HTML Tokenizer 将字符转为标记
3. **Token → DOM节点**：Tree Construction 构建DOM树
4. **CSSOM树构建**：同时解析CSS
5. **Render Tree**：DOM + CSSOM = Render Tree
6. **Layout**：计算元素位置
7. **Paint**：绘制像素

```
HTML ──→ DOM Tree ──┐
                      ├──→ Render Tree ──→ Layout ──→ Paint
CSS  ──→ CSSOM Tree ──┘
```

红队核心知识点：
- HTML解析与XSS过滤器的对抗发生在步骤2-3
- 如果过滤器在Tokenizer层面做匹配，可能被编码绕过
- 如果过滤器在DOM构建后做匹配，可能被mXSS（突变XSS）绕过

## 六、HTML解析器的特性

### 宽松解析（Lenient Parsing）

HTML解析器极为宽容。即使标签没有正确闭合，也会尝试构造DOM。这一特性被广泛用于：

- **Tag逃逸**：`<scr<script>ipt>` 在过滤掉 `<script>` 后剩 `<script>`
- **属性截断**：利用引号不闭合打破过滤器预期
- **注释利用**：`<!--><script>alert(1)</script>-->`

### 自动补全（Tree Construction）

HTML解析器会自动补全缺失的标签：

```
<table><img src=x onerror=alert(1)></table>

解析器会在 <table> 内自动插入 <tbody><tr><td>,
导致 <img> 成为 <td> 的子元素，onerror仍然触发。
这种"意外的DOM结构"经常绕过XSS过滤器。
```

### SVG/Foreign Content模式

当解析器遇到 `<svg>` 或 `<math>`，进入 Foreign Content 模式，标签解析规则变化：

```
<svg><script>alert(1)</script></svg>

在SVG内，<script>的行为与HTML不同，
某些过滤器的白名单可能遗漏这种场景。
```

### 字符编码诡计

```
<meta charset="UTF-7">

如果服务器未正确设置Content-Type charset，
攻击者可通过UTF-7编码注入：+ADw-script+AD4-alert(1)+ADw-/script+AD4-
```

## 七、红队视角总结

### HTML5攻击面向量总表

| 攻击类型 | 核心原理 | 利用的HTML特性 |
|---------|---------|---------------|
| XSS | 注入可执行脚本 | 事件属性、script标签、javascript:协议 |
| mXSS | 解析器与序列化器对同一HTML的不同理解 | innerHTML的解析差异 |
| DOM Clobbering | id/name属性污染全局变量 | HTML的id到window对象的映射 |
| Clickjacking | 透明iframe覆盖诱骗点击 | iframe + CSS opacity |
| Tabnabbing | `target=_blank` 的 `window.opener` 引用 | a标签的target属性 |
| CSS注入 | 注入style标签或style属性 | style标签、@import |
| 模板注入 | 客户端模板引擎的表达式注入 | script标签的type属性差异 |

### 对应工具

- **Chrome DevTools**：Elements面板查看DOM, Console执行JS
- **Burp Suite**：拦截修改HTML, 测试XSS payload
- **DOM Invader**（Burp内置）：自动检测DOM XSS
- **XSStrike**：自动化XSS检测与payload生成

---
**返回** [[HTML基础总目录|HTML基础总目录]] | [[../前端基础总目录|前端基础总目录]]
