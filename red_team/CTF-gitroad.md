
# CTF朝圣之路——从零到专家的靶场练习顺序

## 引言：为什么CTF是渗透测试最好的修炼方式

书本可以教你TCP三次握手，但教不会你提权失败十次之后依然保持冷静的心态。视频可以演示SQL注入，但演示不出目标机 器在凌晨三点突然"复活"时的那种狂喜。

CTF靶场是渗透测试者最接近实战的修炼场。它们提供了四个书本永远无法提供的维度：

1. **反馈闭环**：输入payload，立即看到结果。对就是对，错就是错，没有中间地带。
2. **挫败感训练**：卡关是常态。在一次次失败中，你自然会学会排查思路、搜索技巧和耐心——这些恰恰是红队最核心的品质。
3. **知识缝合**：不会再有"今天学SQL注入，明天学XSS"的分科教学。一台靶机就是一场战争，你需要同时调动Web渗透、提权、内网横向移动等所有知识，知识在实战中自然缝合。
4. **成瘾性**：Flag不是奖励，拿Flag的**过程**才是。那种"我终于明白了"的顿悟快感，是任何被动学习都无法提供的。

以下是我为你规划的一条**科学递进的朝圣之路**——从Web基础到内网域渗透，每一阶段都有明确的目标、推荐的靶场和预计的耗时。只需一张桌、一台能跑虚拟机的电脑，外加一颗耐得住寂寞的心。

> "一名战士需要上阵杀敌，而你的实验室就是你的沙盘。" ——《黑客与画家》意译


## 第一阶段：入门启蒙——Web基础靶场

> **周期：第1-4周** | **难度：（1/10）** | **目标：掌握Web漏洞的基本概念与手工利用**

在学会跑之前，先学会爬。这一阶段的任务是**穷尽Web安全的知识地图**——不是浅尝辄止，而是把每一个漏洞类型都亲手利用至少10次。

### 1.1 PortSwigger Web Security Academy（首要推荐）

- **地址**：https://portswigger.net/web-security
- **费用**：完全免费
- **预计耗时**：3-4周（每天4小时）
- **前置要求**：HTTP基础、基本的Python或Bash使用能力

这是目前世界上最好的Web安全学习平台，没有之一。PortSwigger 是 Burp Suite 的开发商，他们的课程由浅入深，每一个漏洞类型都配有完整的交互式实验环境。**唯一的要求是注册账号。**

**按顺序完成以下专题：**

| 序号 | 专题 | 英文名 | 学习重点 |
|:---:|------|--------|----------|
| 1 | SQL注入 | SQL Injection | UNION注入、盲注（布尔/时间）、带外注入、数据库指纹识别 |
| 2 | 跨站脚本 | XSS | 反射型/存储型/DOM型、CSP绕过、Dangling Markup |
| 3 | 跨站请求伪造 | CSRF | Token绕过、SameSite Cookie绕过 |
| 4 | 服务端请求伪造 | SSRF | 基本SSRF、盲SSRF、针对内部服务的攻击 |
| 5 | 访问控制 | Access Control | IDOR、参数篡改、多步流程绕过 |
| 6 | 认证漏洞 | Authentication | 密码爆破、MFA绕过、密码重置投毒、OAuth攻击 |
| 7 | 目录遍历 | Directory Traversal | 路径穿越、文件包含 |
| 8 | 跨域资源共享 | CORS | 错误配置CORS导致的跨域攻击 |
| 9 | 点击劫持 | Clickjacking | Frame Bursting绕过、拖拽攻击 |
| 10 | WebSockets | WebSocket | WebSocket劫持、跨站WebSocket劫持 |
| 11 | 不安全的反序列化 | Insecure Deserialization | Java/PHP/Ruby反序列化漏洞 |
| 12 | 服务端模板注入 | SSTI | 识别模板引擎、构造RCE payload |
| 13 | GraphQL API | GraphQL API | 内省查询泄露、深度递归攻击 |

> **心得**：不要"读过就算了"。每个实验自己手工构造payload，而不是复制粘贴。你会惊讶地发现，花20分钟自己琢磨出来的注入点，比"看答案"通过的20个实验都记得牢。

### 1.2 DVWA（Damn Vulnerable Web Application）

- **地址**：https://github.com/digininja/DVWA
- **费用**：免费（本地搭建）
- **预计耗时**：1-2天
- **前置要求**：PHP + MySQL 环境（推荐 XAMPP 或 Docker）

DVWA是Web安全的"训练沙袋"。四个安全等级（Low / Medium / High / Impossible）让你逐步感受防护机制的升级，理解漏洞修复的本质。在完成 PortSwigger 之后，用 DVWA 所有四个等级通刷一遍，作为阶段性检验。

### 1.3 bWAPP

- **地址**：http://www.itsecgames.com/
- **费用**：免费（本地搭建）
- **预计耗时**：2-3天
- **前置要求**：同DVWA

bWAPP 包含超过100种漏洞，覆盖面比DVWA更广。特别是它收录了一些"冷门"漏洞类型（如 Host Header 注入、XXE、命令注入变种等），适合在 PortSwigger 和 DVWA 之后查漏补缺。

### 1.4 sqli-labs

- **地址**：https://github.com/Audi-1/sqli-labs
- **费用**：免费（本地搭建）
- **预计耗时**：3-5天
- **前置要求**：完成PortSwigger的SQL注入专题

如果你觉得自己SQL注入已经"会了"——去试试 sqli-labs 的65关。你会重新认识什么叫"会"。从简单的联合查询到复杂的堆叠注入、Order By 注入、HTTP参数污染，每一关都是一次小的顿悟。

> "当一个人执着于一门知识时，他必须在黑暗中独自摸索很久，才能找到答案。" —— 村上春树


## 第三阶段：系统渗透——VulnHub靶机实战

> **周期：第9-12周** | **难度：（4/10）** | **目标：从Web层渗透过渡到系统层提权**

VulnHub 提供的是完整的虚拟机镜像——你无法"重置单个漏洞"，只能在有限的信息下攻克整台机器。这种不确定性是最接近真实渗透的场景。所有靶机都可以用 VirtualBox 或 VMware 导入，完全离线运行。

- **地址**：https://www.vulnhub.com
- **费用**：完全免费
- **预计耗时**：3-4周
- **前置要求**：完成第二阶段TryHackMe基础路径

### 3.1 推荐靶机清单（由易到难）

| 序号 | 靶机名称 | 核心技能 | 难度 | 预计耗时 |
|:---:|----------|----------|:---:|:---:|
| 1 | **Kioptrix Level 1** | 基础侦察 → Samba漏洞利用 → 手动编译EXP | | 2-4h |
| 2 | **FristiLeaks** | Web信息泄露 → 图片马 → Base64编码绕过 → 内核提权 | | 3-5h |
| 3 | **Mr-Robot** | 多层渗透 → WordPress → 字典爆破 → SUID/nmap提权（致敬美剧《黑客军团》） | | 4-6h |
| 4 | **DC-1** | Drupal CMS利用（Drupalgeddon）、Hydra爆破、SUID find提权 | | 4-6h |
| 5 | **Brainpan** | Windows缓冲区溢出入门 → 逆向分析 → 手工构造Shellcode | | 6-10h |
| 6 | **SickOS 1.1** | Squid代理配置 → 代理链 → 内网Web渗透 | | 4-8h |
| 7 | **DevRandom** | CTF风格综合靶机 → 多步骤信息收集 | | 5-8h |
| 8 | **Tr0ll 系列（1-3）** | 极度强调枚举能力 → 不是难，是"藏得深" | | 3-6h/台 |

### 3.2 渗透方法论（务必养成习惯）

在第三阶段，你需要形成一套标准的渗透流程。对每一台靶机：

1. **侦察（Reconnaissance）**：`netdiscover` 发现IP → `nmap -sC -sV -p-` 全端口扫描
2. **枚举（Enumeration）**：Web目录扫描（gobuster / dirbuster / ffuf）→ SMB枚举（enum4linux）→ FTP/SNMP等服务版本研究
3. **漏洞利用（Exploitation）**：searchsploit 查找公开EXP → 手工适配 → 如果失败，为什么失败？
4. **提权（Privilege Escalation）**：linpeas.sh 自动枚举 → 手动审计 Cron jobs / SUID二进制文件 / 可写服务 / 内核版本 → GTFOBins 查阅绕过方法
5. **后渗透（Post-Exploitation）**：提取密码哈希、翻找敏感文件、画网络拓扑图

> "你不需要每台机器都打下来。你需要的是每一台机器打不下来的时候，下一次能在同样的坑上跨过去。"


## 第五阶段：中级挑战——HTB/PG中级靶机

> **周期：第17-20周** | **难度：（6/10）** | **目标：掌握定制化利用与Active Directory攻击**

进入第五阶段，你面对的不再是"有一个Exp就能打完"的机器。Medium难度的靶机往往需要**理解漏洞原理后手工构造利用代码**，或者组合多个低危漏洞形成攻击链。

### 5.1 HackTheBox Medium 退役机器

- **地址**：https://www.hackthebox.com
- **预计耗时**：3-4周
- **前置要求**：完成至少5台HTB Easy机器

| 机器 | 核心技能 |
|------|----------|
| **Forest** | AS-REP Roasting → DCSync → 全域接管 |
| **Resolute** | LDAP匿名查询 → DNSAdmin利用 → Dll劫持 |
| **Mantis** | DNS枚举 → Kerberos票据攻击 → MSSQL利用 |
| **Sniper** | LFI + 文件上传链 → NTLM中继 → 手工提权 |
| **Delivery** | 子域枚举 → Mattermost凭证泄露 → hashcat规则破解 |
| **Stacked** | 子域枚举 → Git泄露 → 钓鱼邮件 → CVE利用 |
| **Writeup** | CMS Made Simple SQL注入 → SSH登录 → 通过PATH劫持提权 |

### 5.2 OffSec Proving Grounds（PG Play——免费）

- **地址**：https://www.offsec.com/labs/
- **费用**：Play 免费；Practice 需订阅（$19/月）
- **预计耗时**：2-3周
- **前置要求**：HTB Easy熟练

Proving Grounds 是 OffSec（OSCP考试机构）推出的官方靶场。虽然名气不如HTB，但靶机质量很高，且与OSCP考试风格高度一致。

**Play（免费）推荐：**

| 机器 | 核心技能 |
|------|----------|
| **ClamAV** | ClamAV CVE → Sendmail利用 |
| **Jacko** | Web + 密码喷洒 + MSI提权 |
| **Sorcerer** | 多重SSH隧道 + 内网Web |
| **Slort** | Web渗透 + 服务利用 + 内核提权 |
| **Snookums** | 多层攻击链 |

### 5.3 Proving Grounds Practice（付费，推荐）

| 机器 | 核心技能 |
|------|----------|
| **Kevin** | 综合渗透 → 多服务多漏洞 |
| **Nukem** | 子域枚举 → Web漏洞 → 提权链 |
| **Peppo** | Docker逃逸 |

> **为什么引入PG？** OffSec的靶机有一个特点：攻击路径是**线性的**——你必须按设计者期望的路径走。而HTB的靶机往往有多个可能的入口点。训练线性思维对OSCP考试至关重要，而HTB训练的是"真实渗透"中的发散思维。两种训练都不可或缺。


## 第七阶段：专家级——高级挑战

> **周期：24周后** | **难度：（9-10/10）** | **目标：成为真正的渗透专家**

当你完成前六个阶段，你已经有能力进入以下级别的挑战。这一阶段没有"毕业"，只有永无止境的攀登。

### 7.1 HackTheBox Hard / Insane 级别

进入Hard/Insane的世界，意味着：
- 你需要**自己逆向分析二进制文件**，挖掘0day级别的漏洞
- 攻击路径被深度隐藏，可能需要在多层内网之间跳转
- 可能需要利用多个低危漏洞构造长链攻击
- 甚至需要绕过杀软、EDR

### 7.2 OffSec Proving Grounds（Practice Tier 全刷）

逐一攻克PG Practice中所有的中级/高级机器，这是准备OSCP/OSEP/OSWE的最佳训练场。

### 7.3 Pentester Academy Labs

- **地址**：https://www.pentesteracademy.com
- **特色**：拥有大量专业化的实验课程（Kerberos攻击、SCCM攻击、Linux内网渗透等），视频讲解非常详尽。

### 7.4 真实CTF比赛

真正的试金石是参加顶级CTF比赛：

- **DEF CON CTF 资格赛**：CTF界的"世界杯"
- **Google CTF**：Google主办的顶级赛事
- **Plaid CTF**：卡内基梅隆大学Plaid Parliament of Pwning主办的硬核比赛
- **HITCON CTF**：台湾代表队主办，亚洲最高水平
- **Real World CTF**：长亭科技主办，侧重真实场景

> **参加策略**：不要怕"上去就挂"。第一次参加DEF CON资格赛，你大概率一道题都做不出来——这太正常了。你的目标是**看懂Writeup**，并**复现其中的技术**。参加5场顶级CTF之后，你会发现自己看待漏洞的眼光已经完全不同。


## 最后的叮咛

这条路很长，非常长。从你第一次在DVWA里输入 `' OR 1=1 --`，到你有能力在DEF CON资格赛里独立拿下pwn题，中间可能隔着两年、三年，甚至更长。但每一次卡关时，请记住：

**你不是遇到了瓶颈，你只是离答案更近了一步。**

渗透测试的本质不是"知道多少漏洞"，而是在完全未知的环境下，保持冷静、系统地排查、不断地假设与验证。你在CTF里培养的每一分耐心，都是未来面对真实红队任务时最宝贵的武器。

现在，打开你的终端，开始第一台靶机吧。

```bash
# 你的第一个命令
docker run --rm -it -p 80:80 vulnerables/web-dvwa
```

> *"通往精通的旅途没有捷径，但每一步都通向星辰。" —— 匿名红队老兵*
