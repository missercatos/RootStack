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
| 前置准备 | Arch Linux + ArchStrike 安装 | 1天 | [[ISSUES|环境搭建]] |
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
| 1 | [[red_team/网安基础知识/01-计算机网络基础]] | OSI/TCP-IP/DNS/ARP | [[汇编基础/ASM_01_寄存器与指令基础]] (网络协议底层视角); 408级别深度见 [[计算机网络/计算机网络_索引\|计算机网络教程]] |
| 2 | [[red_team/网安基础知识/02-Web技术基础]] | HTTP/HTTPS/Cookie/SOP | - |
| 3 | [[red_team/网安基础知识/05-编程基础]] | Bash + Python 基础 | [[ISSUES|Python黑客脚本]] |
| 4 | [[red_team/网安基础知识/03-操作系统基础]] | Linux/Windows系统管理 | [[ISSUES|C语言教程]] (系统编程理解) |
| 5 | [[red_team/网安基础知识/06-安全基础概念]] | CIA/STRIDE/CVE/CVSS | - |
| 6 | [[red_team/网安基础知识/07-渗透测试方法论]] | PTES/Kill Chain/MITRE ATT&CK | - |
| 7 | [[red_team/网安基础知识/04-密码学基础]] | 哈希/对称/非对称/PKI | [[|]] (数论基础) |
| 8-10 | [[red_team/网安基础知识/08-数据库基础]] / [[red_team/网安基础知识/09-认证与授权基础]] / [[red_team/网安基础知识/10-虚拟化与容器基础]] | 数据库/JWT/OAuth/Docker | - |

> **Python 练习**: 在学习编程基础时，配合 [[ISSUES|Python 力扣练习精选]] 做算法验证。力扣题目按安全相关性分组，边学边练。

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
| 04 | [[red_team/archstrike-web教学/04-SQL注入攻击]] | SQLi | [[ISSUES|数据结构]] (数据库结构理解) |
| 05 | [[red_team/archstrike-web教学/05-XSS与CSRF攻击]] | XSS/CSRF | - |
| 06 | [[red_team/archstrike-web教学/06-文件包含与命令注入]] | LFI/RFI/CMD | - |
| 07 | [[red_team/archstrike-web教学/07-认证与会话攻击]] | Auth/Session | - |
| 08 | [[red_team/archstrike-web教学/08-Web渗透综合实战]] | 综合演练 | - |
| 09 | [[red_team/archstrike-web教学/09-WAF绕过与高级技巧]] | WAF bypass | - |

> **前端深度**: Web安全深入者推荐先学 [[ISSUES|前端基础模块]]（25篇），从HTML/CSS/JS到浏览器安全模型、API安全、CSP绕过等，完整覆盖前端攻击面。

---

## 第四阶段 -- 进阶模块 (按需选学)

ArchStrike 工具组覆盖 10 个安全领域，每个领域 2-7 篇教程。

| 工具组 | 入口 | 内容 | 关联RootStack |
|--------|------|------|--------------|
| 侦察 (recon) | [[red_team/archstrike-recon教学/01-高级子域名与资产发现]] | amass/subfinder/Shodan/OSINT | - |
| 扫描 (scanner) | [[red_team/archstrike-scanner教学/01-高速大规模扫描技术]] | masscan/zmap | - |
| 漏洞利用 (exploit) | [[red_team/archstrike-exploit教学/01-漏洞利用框架精通]] | Metasploit高级/msfvenom | - |
| 密码破解 (cracking) | [[red_team/archstrike-cracking教学/01-在线密码攻击大师课]] | Hydra/Hashcat/John | - |
| 提权 (privesc) | [[red_team/archstrike-privilege-escalation教学/01-Linux权限提升完整指南]] | SUID/kernel exploits | [[ISSUES|系统内核]] |
| 隧道代理 (proxy) | [[red_team/archstrike-proxy教学/01-代理与隐蔽通信]] | SSH tunnels/chisel/Tor | - |
| 无线 (wireless) | [[red_team/archstrike-wireless教学/01-无线网络基础]] | WiFi/802.11/WPA破解 | - |
| 取证 (forensics) | [[red_team/archstrike-forensics教学/01-磁盘取证与反取证]] | Autopsy/Volatility | - |
| 模糊测试 (fuzz) | [[red_team/archstrike-fuzz教学/01-模糊测试入门与AFL实战]] | AFL++/ffuf/wfuzz | - |
| 恶意软件 (malware) | [[red_team/archstrike-malware教学/01-恶意软件分析入门]] | YARA/radare2 | [[ISSUES|汇编基础]] (逆向必备) |

---

## 第五阶段 -- 红队实战 (建议 2-4 周)

> 入口: [[ISSUES|实战教程总目录]]

14 天实战训练计划，从环境部署到全链路攻击演练。

| Day | 文件 | 内容 | 关联RootStack |
|-----|------|------|--------------|
| 1-2 | [[red_team/实战教程/01-面向世界实战-互联网旗标捕猎]] | PortSwigger/OverTheWire/SQLi/XSS | - |
| 3 | [[red_team/实战教程/02-ArchStrike环境部署与配置]] | ArchStrike工具链 | - |
| 4 | [[red_team/实战教程/03-互联网侦察与目标测绘]] | amass/nmap/gobuster/Shodan | - |
| 5-6 | [[red_team/实战教程/04-Web渗透深度实战]] | SQLi/XSS/SSRF/LFI/SSTI全payload | - |
| 7 | [[red_team/实战教程/05-Rust红队工具链与系统入侵]] | RustScan/feroxbuster/rustcat | [[ISSUES|Rust红队脚本]] |
| 8 | [[red_team/实战教程/06-AI辅助红队攻防]] | opencode/Claude Code/AI+C2 | - |
| 9 | [[red_team/实战教程/09-逆向工程与二进制攻防]] | Ghidra/ROP/pwntools | [[ISSUES|汇编基础]] |
| 10 | [[red_team/实战教程/10-漏洞利用与提权]] | Metasploit/mimikatz/privesc | - |
| 11 | [[red_team/实战教程/11-脚本与自动化兵器库]] | Bash/Python/PowerShell | [[red_team/补充-Python黑客脚本基础]] |
| 12 | [[red_team/实战教程/12-综合实战-红队全链路演练]] | recon→shell→privesc→domain | - |

实战教程还包含硬件攻防（ESP32 BadUSB, CH341A, Proxmark3）和无线/射频攻防（WiFi, BLE, SDR, NFC），详见 [[ISSUES|训练总目录]]。

---

## 第六阶段 -- CTF 竞赛：分化与方向选择

> 入口: [[ISSUES|CTF知识库总目录]] | [[red_team/ctf_trea/CTF简介|CTF 简介]] | [[red_team/ctf_trea/签到题|签到题全解]]

CTF 是检验网络安全能力的**试金石**——不需要成为顶级选手才算成功。CTF 的价值在于帮你**判断自己是否适合红队方向**，以及帮你**发现自己的技术偏好**。

### CTF 作为自我检测工具

```
          完成第一阶段基础知识 + 第二阶段渗透测试
                        │
                        ▼
              ┌── CTF 入门练习 ──┐
              │  (签到题 + Web基础)  │
              └────────┬─────────┘
                        │
            ┌───────────┴───────────┐
            ▼                       ▼
    做起来有感觉、能找到乐趣      做起来吃力、不感兴趣
            │                       │
            ▼                       ▼
      继续深入 CTF            考虑其他方向:
            │                  SRC漏洞挖掘 / 安全开发
    ┌───────┴───────┐          / 安全运维(DevSecOps)
    ▼               ▼          / 安全咨询 / 合规审计
  CTF 竞赛路线    SRC / Bug Bounty
```

### CTF 入门练习指南

本教程已完成的 CTF 内容（持续建设中）：

| 内容 | 文件 | 说明 |
|------|------|------|
| CTF 概述 | [[red_team/ctf_trea/CTF简介]] | CTF 历史、题目类型、团队构成 |
| 竞赛模式 | [[red_team/ctf_trea/竞赛模式]] | Jeopardy / AwD / AWP / RHG |
| 题目类型 | [[red_team/ctf_trea/题目类型]] | Web / Pwn / Reverse / Crypto / Misc |
| 签到题全解 | [[red_team/ctf_trea/签到题]] | 10 大类签到题陷阱 + Windows/Linux/macOS 三系统解法 |
| Web 入门 | [[red_team/ctf_trea/Web/Web]] | Web 类 CTF 前置技能 |

> 先从 [[red_team/ctf_trea/签到题|签到题]] 入手。签到题覆盖了 CTF 中最常见的文件转换、编码解码、网页隐写、图片隐写、流量分析等基础操作。**如果能独立解决签到题，说明你有红队的思维习惯。**

### 路径分化一：CTF 竞赛路线

如果 CTF 入门后发现自己对比赛感兴趣，继续深入：

```
Web基础 → SQLi/XSS/命令注入深度 → PWN 二进制漏洞利用 → Reverse 逆向
    → Crypto 密码学 → 混合题型 → Jeopardy 团队赛 → AwD 攻防对抗
```

| 阶段 | 内容 | 参考资源 |
|------|------|---------|
| CTF 基础 | 签到题 + Web 类题目 | [[red_team/ctf_trea/签到题]] [[red_team/ctf_trea/Web/Web]] |
| 专项突破 | PWN / Reverse / Crypto | [[red_team/ctf_trea/题目类型]] |
| 实战比赛 | CTFtime 平台各大赛事 | https://ctftime.org/ |
| 国内平台 | NSSCTF / CTFHub / Bugku | 在线训练环境 |

### 路径分化二：SRC / 漏洞挖掘 / 渗透测试

如果 CTF 让你确认了自己对实战攻防的兴趣，但比赛的压力和题目设计不是你的菜：

```
CTF基础训练 (培养攻击思维)
    │
    ├─► SRC 漏洞响应平台 (补天、漏洞盒子、HackerOne)
    │   └─ 实战挖洞：Web 漏洞、逻辑漏洞、越权
    │
    ├─► Bug Bounty (HackerOne / Bugcrowd / Immunefi)
    │   └─ 国际化众测，Web3/智能合约新方向
    │
    ├─► 企业内部红队 (Red Team Operations)
    │   └─ 渗透测试 → 红蓝对抗 → APT 模拟
    │
    ├─► 安全研究 (Vulnerability Research)
    │   └─ 0day 挖掘、内核漏洞、浏览器沙箱逃逸
    │
    └─► 安全工具开发
        └─ Rust/Go/Python 编写自动化扫描器、C2框架
```

### 路径分化三：CTF 之外的网络安全职业

不是所有人都适合做攻击者。网络安全是一个**进攻与防御并重**的领域：

| 方向 | 内容 | 前置 |
|------|------|------|
| 安全运维 (DevSecOps) | CI/CD 安全、容器安全、云安全 | 路径A + 网安基础 |
| 安全开发 | 安全 SDK / 加密库 / WAF 开发 | 路径B + Rust/Go |
| 安全咨询 | 等保测评、ISO 27001、风险评估 | 网安基础 + 项目管理 |
| 威胁情报 | APT 追踪、IOC 分析、威胁建模 | CTF 逆向经验 + 英语 |
| 电子取证 | 磁盘取证、内存取证、手机取证 | 逆向基础 + 文件系统 |
| 区块链安全 | 智能合约审计、DeFi 攻击分析 | Solidity + CTF Crypto |

---

### CTF 学习资源

| 资源 | 链接 | 说明 |
|------|------|------|
| CTF Wiki | https://ctf-wiki.org/ | 中文 CTF 百科 |
| CTFtime | https://ctftime.org/ | 国际 CTF 赛历 |
| NSSCTF | https://www.nssctf.cn/ | 国内在线 CTF 训练平台 |
| CTFHub | https://www.ctfhub.com/ | 技能树式训练 |
| Bugku | https://ctf.bugku.com/ | 各类题型训练 |
| Pwn College | https://pwn.college/ | 二进制安全系统课程 |

> CTF 对算法和编程能力有较高要求。建议边学 CTF 边回顾路径 D 的算法内容（[[ISSUES|DSA刷题路线图]]）以及 Python 编程练习（[[ISSUES|Python力扣练习]]）。

---

## 其他模块

### 服务器部署与运维 (QQ Bot 攻防实战)

> 入口: [[red_team/服务器部署与运维/服务器部署与运维总目录]]

以 QQ Bot 为载体的红蓝对抗实践：NapCat + AstrBot + DeepSeek 部署、攻击面分析、安全加固。适合学完渗透测试基础后进行全栈安全实战。

### AI 辅助红队

> 入口: [[ISSUES|AI辅助红队攻防 (2430行)]]

使用 opencode、Claude Code 等 AI 工具进行侦察、漏洞利用生成、代码审查、C2实现。

### Rust 红队

> 入口: [[ISSUES|Rust红队脚本编程]]

Rust 在红队中的优势（性能、内存安全、跨平台编译）、端口扫描器、HTTP客户端、反向 shell 等。

---

## 推荐学习顺序

```
通用基础（路径A-D 选择性补齐）
    │
    ▼
前置: Arch Linux + ArchStrike 安装
    │
    ├─► 网安基础知识 (10篇, 2-4周) ── Python 练习 ([[ISSUES|力扣]] + [[red_team/补充-Python黑客脚本基础]])
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

- [[ISSUES|红队知识库总目录]] — ~125篇, 完整模块索引
- [[ISSUES|新生推荐学习方向]] — 多方向入门指引
- [[ISSUES|进阶学习与缺失领域分析]] — 知识盲区补全
- [[ISSUES|真实实战-境外网站练手]] — 合法靶场汇总
- [[408统考索引]] — 408考研四科考点交叉映射
- [[计算机网络/计算机网络_索引|计算机网络教程]] — 408级别网络协议深度
- [[操作系统/操作系统_索引|操作系统教程]] — 10篇操作系统底层
- [[计算机原理/计算机原理_索引|计算机原理教程]] — 10篇组成原理
- [[git]] — Git 提交工具链，用于提交漏洞报告/红队工具代码
