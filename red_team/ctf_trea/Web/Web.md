## Web 方向总览

Web 方向是 CTF 中最常见、入门门槛相对较低的题型方向，涵盖从 HTTP 协议到服务器端漏洞的多个层面。Web 题目通常给出一个 URL，选手需通过对该 Web 应用进行漏洞探测与利用来获取 flag。

```mermaid
mindmap
  root((Web CTF))
    HTTP 协议攻击
      自定义请求方法
      302 跳转
      Cookie 篡改
      基本认证
      源代码
      Host 头注入
      HTTP 请求走私
      缓存投毒
    注入类
      SQL 注入
      NoSQL 注入
      XPath 注入
      SSTI 模板注入
    XSS
      反射型 XSS
      存储型 XSS
      DOM 型 XSS
    CSRF
    文件操作
      文件包含 LFI/RFI
      文件上传
      文件读取
    代码执行
      RCE
      命令注入
      代码注入
    认证与会话
      Cookie 伪造
      Session 劫持
      JWT 攻击
      SSRF
    其他
      CORS 配置错误
      WebSocket 攻击
      Prototype Pollution
```

### Web 在 CTF 中的含义

Web 方向考察选手对网络应用全链路的理解与攻击能力，包括但不限于：

- 客户端与服务端的通信协议（[[Web前置技能/HTTP协议/HTTP协议|HTTP/HTTPS]]）
- 服务端脚本语言的安全问题（PHP、Python、Java、Node.js 等）
- 数据库交互安全（SQL 注入等）
- 身份认证与会话管理
- 文件操作与命令执行

### 常见 Web 题型

| 分类 | 考点举例 | 双链指引 |
|------|---------|---------|
| HTTP 协议攻击 | 自定义方法、请求走私、Host 头 | [[Web前置技能/HTTP协议/HTTP协议|HTTP 协议总览]] |
| SQL 注入 | 联合查询、盲注、报错注入 | `Web前置技能/SQL注入` (待编写)（规划中） |
| XSS | 反射型、存储型、DOM 型 | `Web前置技能/XSS` (待编写)（规划中） |
| 文件包含 | LFI、RFI、php:// 伪协议 | `Web前置技能/文件包含` (待编写)（规划中） |
| 文件上传 | 绕过 Content-Type、文件头检查 | `Web前置技能/文件上传` (待编写)（规划中） |
| 命令执行 | RCE、命令注入、代码执行 | `Web前置技能/命令执行` (待编写)（规划中） |
| SSRF | 内网探测、协议转换 | `Web前置技能/SSRF` (待编写)（规划中） |

### 常见解题思路

1. **信息收集** -- 访问目标、查看页面源码、响应头、robots.txt、sitemap.xml、注释信息
2. **协议分析** -- 用 Burp Suite 拦截请求，观察 HTTP 方法、头部、Cookie、参数
3. **参数篡改** -- 修改 GET/POST 参数、Cookie、Header 中的关键字段
4. **代码审计** -- 若题目提供源码，寻找过滤缺陷、逻辑漏洞
5. **漏洞利用** -- 构造 Payload，使用 sqlmap、XSStrike 等工具辅助
6. **权限提升** -- 从低权限漏洞升级到更高权限的信息获取

### ArchStrike 关联

本知识库的 [[../../archstrike-web教学/01-Web基础与HTTP协议|archstrike-web教学]] 模块提供 Web 安全从基础到进阶的完整工具链与实战场景，涵盖 HTTP 协议、SQL 注入、XSS、命令注入等各方向。

### 前置技能

- [[Web前置技能/HTTP协议/HTTP协议|HTTP 协议基础]] -- CTF 中 HTTP 相关题目与突破点
- [[../../网安基础知识/02-Web技术基础|Web 技术基础]] -- 本知识库中 HTTP 协议的完整讲解
- [[../../archstrike-web教学/01-Web基础与HTTP协议|Web 基础与 HTTP 协议]] -- ArchStrike 环境下的 Web 安全实战
- [[../../网安基础知识/01-计算机网络基础|计算机网络基础]] -- OSI 模型与 TCP/IP 协议栈

### 相关文章

- [[../题目类型#Web|题目类型 - Web]] -- CTF 题型总览中的 Web 分类
- [[../竞赛模式#Jeopardy-解题|竞赛模式 - Jeopardy]] -- 解题模式下的 Web 题目
- [[../ctf解法与理论总目录|CTF 总目录]] -- CTF 理论学习与练习平台
