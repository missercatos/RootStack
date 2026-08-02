## HTML/CSS -- CTF 前置技能

> `index.html` 是大多数 Web 题的入口，理解 HTML 和 CSS 基础是读网页源码、找隐藏信息的前提。

### 本知识库中的前端正式讲解

在深入 CTF 之前，建议先阅读：

- [[../../../../前端基础/前端基础总目录|前端基础总目录]] -- HTML、CSS、JS 的完整知识体系
- [[../../../../前端基础/html/01-HTML结构与语义化|01-HTML结构与语义化]] -- HTML 结构与标签基础
- [[../../../../前端基础/css/01-CSS选择器与样式基础|01-CSS选择器与样式基础]] -- CSS 选择器与样式
- [[../../../../网安基础知识/02-Web技术基础|02-Web技术基础]] -- HTTP 协议与 Web 技术综合讲解

### CTF 中 HTML 相关考点

| 考点 | 说明 | 常见题型 |
|------|------|---------|
| 查看源码 | HTML 注释里藏 flag | 源代码题 |
| 表单标签 | `<input>` 的限制，修改参数提权 | Cookie 题中的 hidden input |
| iframe 跨域 | 页面嵌套与 X-Frame-Options | CSP 绕过 |
| `<meta>` 标签 | 页面重定向、CSP 策略声明 | 客户端重定向 |
| view-source | 查看原始 HTML 不被 JS 混淆 | 信息收集第一步 |

### CTF 终端查看 HTML 源码

```bash
# 拉取页面源码
curl -s http://目标/

# 只抽 HTML 注释（flag 常藏在这里）
curl -s http://目标/ | grep -E '<!--.*-->'

# 只抽隐藏表单字段
curl -s http://目标/ | grep -E 'type="hidden"'

# 搜所有带 key/secret/flag 的标签
curl -s http://目标/ | grep -iE 'flag|key|secret|token'
```

### CSS 在 CTF 中的特殊考点

| 考点 | 说明 |
|------|------|
| CSS 注释 | `/* */` 中隐藏 flag |
| `display: none` | 隐藏的元素可能包含敏感信息 |
| `::after` / `::before` | 伪元素中的 content 属性藏 flag |
| CSS 注入 | SQL/命令注入后的信息回显位置 |
| 侧信道攻击 | 利用 CSS 选择器 + 请求探测用户输入 |

### 关联教程

- [[../HTTP协议/HTTP协议|HTTP 协议总览]] -- Web 前置技能中的 HTTP 考点
- [[../HTTP协议/源代码|源代码]] -- 响应包源码查找 flag 的原理与解法
- [[../../../../前端基础/前端基础总目录|前端基础总目录]] -- HTML/CSS/JS 完整知识体系
- [[../../../../前端基础/html/01-HTML结构与语义化|01-HTML结构与语义化]] -- HTML 标签与结构
- [[../../../../前端基础/css/01-CSS选择器与样式基础|01-CSS选择器与样式基础]] -- CSS 基础
