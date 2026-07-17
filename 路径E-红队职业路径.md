## 路径 E -- 红队职业路径 (ArchStrike 体系)

> **重要说明**: 路径 E 是**职业方向路径**，不同于路径 A-D 的通识学习路径。前四条路径是计算机科学基础，所有方向的学习者都可以学习；路径 E 是基础完成后的**职业分化**——选择网络安全方向后，本路径指引如何利用 ArchStrike 工具体系进入渗透测试、红队攻防和 CTF 竞赛领域。
>
> 进入路径 E 之前，请确保已完成以下通识基础（根据红队方向选择性补齐）：
> - **C 语言基础**（路径 A Phase 1-4）：逆向工程、二进制漏洞利用的基础
> - **Python 编程**（[[red_team/补充-Python黑客脚本基础]] + [[数据结构/DSA学习路线]] Phase 1-2）：脚本自动化、payload 编写
> - **汇编基础**（[[汇编基础/ASM_01_寄存器与指令基础]]）：逆向分析、shellcode 编写
> - **Rust 基础**（路径 B Rust 章节）：高性能红队工具开发

---

## 路径概览

| 阶段 | 模块 | 时间 | 内容 |
|------|------|------|------|
| 前置准备 | Arch Linux + ArchStrike 安装 | 1天 | [[red_team/ArchStrike新手安装教程\|环境搭建]] |
| 第一阶段 | 网安基础知识 | 2-4周 | 网络/Web/系统/密码学/编程/方法论 10篇 |
| 第二阶段 | 渗透测试基础 (base) | 2-3周 | Linux命令、信息收集、扫描、漏洞利用、密码攻击 |
| 第三阶段 | Web安全 (web) | 3-4周 | HTTP协议、SQL注入、XSS/CSRF、文件包含、WAF绕过 |
| 第四阶段 | 进阶模块 (按需选学) | 灵活 | 无线攻防、逆向工程、提权、隧道代理 |
| 第五阶段 | 红队实战 | 2-4周 | 14天实训计划、AI辅助攻防、全链路演练 |
| 第六阶段 | CTF竞赛 | 持续 | Jeopardy/AwD/渗透模式, 题目分类训练 |

---

## 第一阶段 -- 网安基础知识 (建议 2-4 周)

> 入口: [[red_team/总目录与快速查询#模块快速查询\|总目录 → 1.基础知识]]

网安知识的前置基础，覆盖计算机网络、Web技术、操作系统、密码学、编程、安全概念、方法论等 10 个主题。

| 优先级 | 文件 | 核心内容 | 关联RootStack模块 |
|--------|------|---------|------------------|
| 1 | [[red_team/网安基础知识/01-计算机网络基础]] | OSI/TCP-IP/DNS/ARP | [[汇编基础/ASM_01_寄存器与指令基础]] (网络协议底层视角) |
| 2 | [[red_team/网安基础知识/02-Web技术基础]] | HTTP/HTTPS/Cookie/SOP | - |
| 3 | [[red_team/网安基础知识/05-编程基础]] | Bash + Python 基础 | [[red_team/补充-Python黑客脚本基础\|Python黑客脚本]] |
| 4 | [[red_team/网安基础知识/03-操作系统基础]] | Linux/Windows系统管理 | [[c语言教程/c目录\|C语言教程]] (系统编程理解) |
| 5 | [[red_team/网安基础知识/06-安全基础概念]] | CIA/STRIDE/CVE/CVSS | - |
| 6 | [[red_team/网安基础知识/07-渗透测试方法论]] | PTES/Kill Chain/MITRE ATT&CK | - |
| 7 | [[red_team/网安基础知识/04-密码学基础]] | 哈希/对称/非对称/PKI | [[|]] (数论基础) |
| 8-10 | [[red_team/网安基础知识/08-数据库基础]] / [[red_team/网安基础知识/09-认证与授权基础]] / [[red_team/网安基础知识/10-虚拟化与容器基础]] | 数据库/JWT/OAuth/Docker | - |

> **Python 练习**: 在学习编程基础时，配合 [[red_team/python\|Python 洛谷练习精选]] 做算法验证。洛谷题目按安全相关性分组，边学边练。

---

## 第二阶段 -- 渗透测试基础 (建议 2-3 周)

> 入口: [[red_team/总目录与快速查询#2. 渗透测试基础 (archstrike-base)\|总目录 → 2.渗透测试基础]]

ArchStrike base 工具组教程，覆盖红队基本操作流程：信息收集 → 扫描枚举 → 漏洞评估 → 密码攻击 → 嗅探 → 后渗透。

| 序号 | 文件 | 核心工具 | 关联RootStack |
|------|------|---------|--------------|
| 01 | [[red_team/archstrike-base教学/01-基础命令与Linux安全操作]] | bash/chmod/SSH | [[|]] (Linux基础) |
| 02 | [[red_team/archstrike-base教学/02-信息收集与侦察技术]] | theharvester/recon-ng | - |
| 03 | [[red_team/archstrike-base教学/03-网络扫描与枚举技术]] | nmap/masscan | - |
| 04 | [[red_team/archstrike-base教学/04-漏洞评估与利用基础]] | Metasploit/searchsploit | - |
| 05 | [[red_team/archstrike-base教学/05-密码攻击与破解技术]] | hydra/john | [[|]] (哈希与数论) |
| 06 | [[red_team/archstrike-base教学/06-网络嗅探与中间人攻击]] | Wireshark/bettercap | [[汇编基础/ASM_01_寄存器与指令基础]] (网络协议底层) |
| 07 | [[red_team/archstrike-base教学/07-后渗透与权限维持]] | Meterpreter | [[|]] (权限模型) |
| 08 | [[red_team/archstrike-base教学/08-痕迹清除与渗透报告]] | shred/logs | - |

---

## 第三阶段 -- Web 安全 (建议 3-4 周)

> 入口: [[red_team/总目录与快速查询#4. Web安全 (archstrike-web)\|总目录 → 4.Web安全]]

Web 渗透是红队最常见的攻击面。从 HTTP 协议开始，逐一掌握 SQL 注入、XSS/CSRF、文件包含、命令注入、认证攻击、WAF 绕过。

| 序号 | 文件 | 攻击类型 | 关联RootStack |
|------|------|---------|--------------|
| 01 | [[red_team/archstrike-web教学/01-Web基础与HTTP协议]] | HTTP基础 | - |
| 02 | [[red_team/archstrike-web教学/02-Web信息收集与侦察]] | Web指纹/扫描 | - |
| 03 | [[red_team/archstrike-web教学/03-Web漏洞扫描与检测]] | 自动化扫描 | - |
| 04 | [[red_team/archstrike-web教学/04-SQL注入攻击]] | SQLi | [[数据结构/DSA学习路线\|数据结构]] (数据库结构理解) |
| 05 | [[red_team/archstrike-web教学/05-XSS与CSRF攻击]] | XSS/CSRF | - |
| 06 | [[red_team/archstrike-web教学/06-文件包含与命令注入]] | LFI/RFI/CMD | - |
| 07 | [[red_team/archstrike-web教学/07-认证与会话攻击]] | Auth/Session | - |
| 08 | [[red_team/archstrike-web教学/08-Web渗透综合实战]] | 综合演练 | - |
| 09 | [[red_team/archstrike-web教学/09-WAF绕过与高级技巧]] | WAF bypass | - |

> **前端深度**: Web安全深入者推荐先学 [[red_team/前端基础/前端基础总目录\|前端基础模块]]（25篇），从HTML/CSS/JS到浏览器安全模型、API安全、CSP绕过等，完整覆盖前端攻击面。

---

## 第四阶段 -- 进阶模块 (按需选学)

ArchStrike 工具组覆盖 10 个安全领域，每个领域 2-7 篇教程。

| 工具组 | 入口 | 内容 | 关联RootStack |
|--------|------|------|--------------|
| 侦察 (recon) | [[red_team/archstrike-recon教学/01-高级子域名与资产发现]] | amass/subfinder/Shodan/OSINT | - |
| 扫描 (scanner) | [[red_team/archstrike-scanner教学/01-高速大规模扫描技术]] | masscan/zmap | - |
| 漏洞利用 (exploit) | [[red_team/archstrike-exploit教学/01-漏洞利用框架精通]] | Metasploit高级/msfvenom | - |
| 密码破解 (cracking) | [[red_team/archstrike-cracking教学/01-在线密码攻击大师课]] | Hydra/Hashcat/John | - |
| 提权 (privesc) | [[red_team/archstrike-privilege-escalation教学/01-Linux权限提升完整指南]] | SUID/kernel exploits | [[内核/系统内核/01_C语言与操作系统\|系统内核]] |
| 隧道代理 (proxy) | [[red_team/archstrike-proxy教学/01-代理与隐蔽通信]] | SSH tunnels/chisel/Tor | - |
| 无线 (wireless) | [[red_team/archstrike-wireless教学/01-无线网络基础]] | WiFi/802.11/WPA破解 | - |
| 取证 (forensics) | [[red_team/archstrike-forensics教学/01-磁盘取证与反取证]] | Autopsy/Volatility | - |
| 模糊测试 (fuzz) | [[red_team/archstrike-fuzz教学/01-模糊测试入门与AFL实战]] | AFL++/ffuf/wfuzz | - |
| 恶意软件 (malware) | [[red_team/archstrike-malware教学/01-恶意软件分析入门]] | YARA/radare2 | [[汇编基础/ASM_01_寄存器与指令基础\|汇编基础]] (逆向必备) |

---

## 第五阶段 -- 红队实战 (建议 2-4 周)

> 入口: [[red_team/实战教程/00-总目录与快速开始\|实战教程总目录]]

14 天实战训练计划，从环境部署到全链路攻击演练。

| Day | 文件 | 内容 | 关联RootStack |
|-----|------|------|--------------|
| 1-2 | [[red_team/实战教程/01-面向世界实战-互联网旗标捕猎]] | PortSwigger/OverTheWire/SQLi/XSS | - |
| 3 | [[red_team/实战教程/02-ArchStrike环境部署与配置]] | ArchStrike工具链 | - |
| 4 | [[red_team/实战教程/03-互联网侦察与目标测绘]] | amass/nmap/gobuster/Shodan | - |
| 5-6 | [[red_team/实战教程/04-Web渗透深度实战]] | SQLi/XSS/SSRF/LFI/SSTI全payload | - |
| 7 | [[red_team/实战教程/05-Rust红队工具链与系统入侵]] | RustScan/feroxbuster/rustcat | [[red_team/Rust红队脚本编程\|Rust红队脚本]] |
| 8 | [[red_team/实战教程/06-AI辅助红队攻防]] | opencode/Claude Code/AI+C2 | - |
| 9 | [[red_team/实战教程/09-逆向工程与二进制攻防]] | Ghidra/ROP/pwntools | [[汇编基础/ASM_01_寄存器与指令基础\|汇编基础]] |
| 10 | [[red_team/实战教程/10-漏洞利用与提权]] | Metasploit/mimikatz/privesc | - |
| 11 | [[red_team/实战教程/11-脚本与自动化兵器库]] | Bash/Python/PowerShell | [[red_team/补充-Python黑客脚本基础]] |
| 12 | [[red_team/实战教程/12-综合实战-红队全链路演练]] | recon→shell→privesc→domain | - |

实战教程还包含硬件攻防（ESP32 BadUSB, CH341A, Proxmark3）和无线/射频攻防（WiFi, BLE, SDR, NFC），详见 [[red_team/实战教程/00-总目录与快速开始\|训练总目录]]。

---

## 第六阶段 -- CTF 竞赛 (持续)

> 入口: [[red_team/ctf_trea/ctf解法与理论总目录\|CTF知识库总目录]]

| 文件 | 内容 |
|------|------|
| [[red_team/ctf_trea/CTF简介]] | CTF历史、题目类型、团队构成 |
| [[red_team/ctf_trea/竞赛模式]] | Jeopardy / AwD / AWP / RHG / KoH |
| [[red_team/ctf_trea/题目类型]] | Web / Pwn / Reverse / Crypto / Misc |
| [[red_team/ctf-git\|CTF思维框架]] | 攻击面分析、提权链思考、侦察优先 |
| [[red_team/CTF-gitroad\|CTF实战路线图]] | 从Web基础到域渗透, 6阶段进阶 |

CTF 对算法和编程能力有较高要求。建议边学 CTF 边回顾路径 D 的算法内容（[[路径D-DSA算法刷题\|DSA刷题路线图]]）以及 Python 编程练习（[[red_team/python\|Python洛谷练习]]）。

---

## 其他模块

### 服务器部署与运维 (QQ Bot 攻防实战)

> 入口: [[red_team/服务器部署与运维/服务器部署与运维总目录]]

以 QQ Bot 为载体的红蓝对抗实践：NapCat + AstrBot + DeepSeek 部署、攻击面分析、安全加固。适合学完渗透测试基础后进行全栈安全实战。

### AI 辅助红队

> 入口: [[red_team/AI_come\|AI辅助红队攻防 (2430行)]]

使用 opencode、Claude Code 等 AI 工具进行侦察、漏洞利用生成、代码审查、C2实现。

### Rust 红队

> 入口: [[red_team/Rust红队脚本编程\|Rust红队脚本编程]]

Rust 在红队中的优势（性能、内存安全、跨平台编译）、端口扫描器、HTTP客户端、反向 shell 等。

---

## 推荐学习顺序

```
通用基础（路径A-D 选择性补齐）
    │
    ▼
前置: Arch Linux + ArchStrike 安装
    │
    ├─► 网安基础知识 (10篇, 2-4周) ── Python 练习 ([[red_team/python\|洛谷]] + [[red_team/补充-Python黑客脚本基础]])
    │
    ├─► 渗透测试基础 (8篇, 2-3周)
    │
    ├─► Web安全 (9篇, 3-4周) ── 前端基础 (25篇, 选学)
    │
    ├─► 进阶模块 (按需选学: 无线/逆向/提权/隧道/取证/模糊测试/恶意软件)
    │
    ├─► 红队实战 (14天计划)
    │
    └─► CTF竞赛 (持续)
```

---

## 相关资源

- [[red_team/总目录与快速查询\|红队知识库总目录]] — ~125篇, 完整模块索引
- [[red_team/新手推荐学习方向\|新生推荐学习方向]] — 多方向入门指引
- [[red_team/补充-进阶学习与缺失领域分析\|进阶学习与缺失领域分析]] — 知识盲区补全
- [[red_team/真实实战-境外网站练手\|真实实战-境外网站练手]] — 合法靶场汇总
- [[git]] — Git 提交工具链，用于提交漏洞报告/红队工具代码
