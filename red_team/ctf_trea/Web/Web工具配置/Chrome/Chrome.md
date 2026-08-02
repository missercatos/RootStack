## Chrome -- 工具配置

> 即使本知识库偏向终端习惯，浏览器的 DevTools 仍然是 Web 题的重要辅助工具——看页面渲染、调试 JS、检查 DOM 都离不开它。

### 常用功能速查

| 功能 | 入口 | CTF 典型用途 |
|------|------|-------------|
| 查看源代码 | `Ctrl+U` | 找 HTML 注释中的 flag |
| DevTools → Network | `F12` → Network | 看请求/响应、拦截包 |
| DevTools → Application | `F12` → Application | 修改 Cookie/Storage/Local Storage |
| DevTools → Console | `F12` → Console | 执行 JS、调试交互逻辑 |
| DevTools → Element | `F12` → Element | 查看 DOM、修改 hidden 值 |
| 无痕窗口 | `Ctrl+Shift+N` | 避免旧 Cookie/缓存干扰 |

### 推荐扩展

| 扩展 | 用途 |
|------|------|
| Proxy SwitchyOmega | 快速切换代理（配合 Burp） |
| HackBar | 快速构造 HTTP 请求参数 |
| Wappalyzer | 识别目标网站技术栈 |
| ModHeader | 修改请求头 |

### 终端替代对照

| Chrome 操作 | 终端替代 |
|------------|---------|
| 看页面源码 | `curl -s URL` |
| 看响应头 | `curl -s -D - URL` |
| 修改 Cookie | `curl -b "key=value" URL` |
| 修改 User-Agent | `curl -A "Mozilla/..." URL` |
| 模拟 POST 表单 | `curl -X POST -d "key=val" URL` |
| JavaScript 调试 | 分析逻辑后用 node 复现 |

### 关联教程

- [[../BurpSuite/BurpSuite|BurpSuite 配置]] -- 配合 Burp 的代理设置
- [[../../Web前置技能/HTTP协议/HTTP协议|HTTP 协议总览]] -- HTTP 协议基础
- [[../../Web前置技能/HTTP协议/源代码|源代码解题]] -- 查看页面源码找 flag
- [[../../使用习惯|使用习惯]] -- 终端习惯与图形化习惯说明
