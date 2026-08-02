本文件夹按 CTF 技能树方向组织，包含理论总览与解题实践。

## 阅读指引

如果你是 CTF 新手，建议按以下顺序阅读：

1. 先读 **[[CTF简介]]** -- 了解 CTF 是什么、Flag 是什么、如何组队
2. 再读 **[[竞赛模式]]** -- 了解各类赛制的规则与特点
3. 接着读 **[[比赛形式]]** -- 了解线上赛与线下赛的区别
4. 然后读 **[[题目类型]]** -- 了解 CTF 的五大题型分类
5. 确定兴趣方向后，进入具体分类学习技巧
6. 做题前先读 **[[使用习惯]]** -- 了解做题方式与终端习惯的定位

## 理论总览

- [[CTF简介]] -- CTF 起源、Flag 定义、队伍结构
- [[竞赛模式]] -- 理论题 / Jeopardy / AwD / AWP / RHG / RW / KoH / Mix
- [[比赛形式]] -- 线上赛与线下赛对比
- [[题目类型]] -- Web / Pwn / Reverse / Crypto / Misc 全解析

## 当前已有教程

- [[Web/Web|Web 方向总览]] -- Web 方向 CTF 题型与解题思路总览
- [[Web/Web前置技能/HTTP协议/HTTP协议|HTTP 协议总览]] -- HTTP 协议基础与 CTF 考点总览
- [[Web/Web前置技能/HTTP协议/请求方式|请求方式]] -- 自定义 HTTP 方法修改解题
- [[Web/Web前置技能/HTTP协议/302跳转|302 跳转]] -- 重定向响应中隐藏 flag 解题
- [[Web/Web前置技能/HTTP协议/Cookie|Cookie]] -- 篡改 Cookie 获取 flag 解题
- [[Web/Web前置技能/HTTP协议/基本认证|基本认证]] -- Basic 认证爆破解题
- [[Web/Web前置技能/HTTP协议/源代码|源代码]] -- 响应包源码查找 flag 解题
- [[Web/Web前置技能/操作系统/操作系统|操作系统]] -- Linux 环境与命令基础
- [[Web/Web前置技能/数据库/数据库|数据库]] -- SQL 语法与数据库操作
- [[Web/Web前置技能/HTML-CSS/HTML-CSS|HTML/CSS]] -- 前端页面结构基础
- [[Web/Web前置技能/程序语言/程序语言|程序语言]] -- PHP/Python 核心语法
- [[Web/Web工具配置/虚拟机/虚拟机|虚拟机]] -- 靶场环境搭建
- [[Web/Web工具配置/BurpSuite/BurpSuite|BurpSuite]] -- 代理拦截与请求修改
- [[Web/Web工具配置/Chrome/Chrome|Chrome]] -- DevTools 与浏览器扩展
- [[Web/Web工具配置/WebShell/WebShell|WebShell]] -- 一句话木马与后门
- [[Web/Web工具配置/菜刀类工具/菜刀类工具|菜刀类工具]] -- 蚁剑/冰蝎连接工具
- [[Web/Web工具配置/端口扫描/端口扫描|端口扫描]] -- nmap/curl 端口探测
- [[Web/Web工具配置/远程连接/远程连接|远程连接]] -- SSH/nc 反弹 shell
- [[Web/Web工具配置/目录爆破/目录爆破|目录爆破]] -- dirsearch/gobuster 路径探测
- [[Web/信息泄露/目录遍历|目录遍历]] -- 目录索引泄露与逐层追踪解题
- [[使用习惯]] -- 做题方式与终端习惯定位

## 做题练习平台

以下平台提供在线 CTF 题目，无需本地搭建环境：

| 平台 | 网址 | 说明 |
|------|------|------|
| CTFHub | https://www.ctfhub.com | Web 技能树，按专题分类 |
| 攻防世界 | https://adworld.xctf.org.cn | 新手区有历年真题 |
| CTFshow | https://ctf.show | Web 入门题单 |
| NSSCTF | https://www.nssctf.cn | 综合题目 + 动态靶机 |
| BugKu | https://ctf.bugku.com | 适合新手入门 |
| 青少年CTF | https://www.qsnctf.com | 入门友好 |

## 关联教程（本知识库）

- [[../网安基础知识/01-计算机网络基础|01-计算机网络基础]] -- 网络模型与协议基础
- [[../网安基础知识/02-Web技术基础|02-Web技术基础]] -- HTTP 协议深度解析
- [[../archstrike-web教学/01-Web基础与HTTP协议|01-Web基础与HTTP协议]] -- Web 安全场景实战
- [[../总目录与快速查询|总目录与快速查询]] -- 红队完整知识体系

## 规划中的技能树（持续更新）

Web 前置技能 -> HTTP 协议、操作系统、数据库、HTML/CSS、程序语言
Web 工具配置 -> 虚拟机、BurpSuite、Chrome、WebShell、菜刀、端口扫描、远程连接、目录爆破
Web 方向     -> SQL 注入、XSS、文件上传等
Misc         -> 图片隐写、流量分析、编码解码等
Crypto       -> 古典密码、现代密码等
