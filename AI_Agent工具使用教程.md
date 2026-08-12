# AI Agent 工具使用教程

AI Agent 工具已从"玩具"演变为开发者日常生产中的核心工具。本教程涵盖主流 Agent 工具的推荐、安装、使用方式，以及作者的 Agent 使用哲学。

---

## 工具分类

AI 编码 Agent 按交互形态分三类：

| 类型 | 特点 | 代表 |
|------|------|------|
| **终端 CLI 型** | 在终端中运行，读取/编辑文件、执行命令，与编辑器解耦 | Claude Code、opencode、Codex CLI |
| **IDE 集成型** | 嵌入 VS Code/JetBrains 等编辑器，Tab 补全 + 内联对话 | GitHub Copilot、Continue |
| **AI-native 编辑器** | 在 VS Code 基础上深度重构，Agent 能力内建 | Cursor、Windsurf/Devin Desktop |

---

## 重点推荐

### Claude Code（第一推荐）

Anthropic 推出的终端原生编码 Agent。接受自然语言任务描述后，自动读取相关文件、编辑代码、运行测试、根据报错迭代修复。目前是**真正被大多数工作场景采用**的 Agent 工具，在 SWE-Bench Verified 等编码基准测试中持续领先。

**优点：**
- 深度推理能力强，200K token 超长上下文窗口
- 端到端自主完成任务，从理解到修改到验证全流程
- 编辑器无关，在任何工作流中都能嵌入

**缺点与风险：**
- **闭源黑盒**：核心代码不公开，无法审计内部行为
- **中国地区受限**：Anthropic 未在中国大陆提供服务，使用需科学上网（参见 [[科学上网]]），且访问稳定性不受保障
- **信息泄露风险**：代码和上下文数据经过 Anthropic 服务器处理，敏感项目存在数据外泄隐患
- **按量计费成本不可控**：大规模重构场景下 API 调用量可能飙升

**定价：** Pro $20/月 或 API 按量计费

---

### opencode（第二推荐 — 作者首选）

[opencode](https://opencode.ai) 是目前社区最活跃的开源编码 Agent，完全开源（GitHub 160K+ Stars）。支持终端、桌面应用、IDE 扩展三种使用方式。

**优点：**
- **完全开源**：代码公开可审计，无闭源后门风险
- **数据自主可控**：可选择本地模型或自托管 provider，代码不经过第三方
- **多 Provider 支持**：可接入 Claude、GPT、Gemini 等 75+ 模型，也可使用内置免费模型
- **LSP 感知**：自动加载对应语言的 LSP，为 LLM 提供类型信息
- **多会话**：同一项目可并行运行多个 Agent

**缺点：**
- 性能在复杂多步骤任务上可能不及 Claude Code
- 社区驱动，部分功能迭代速度不如商业产品
- 生态文档丰富度与旗舰产品尚有差距

**定价：** 免费

| 对比维度 | Claude Code | opencode |
| ---- | --------------- | --------------------- |
| 开源 | 闭源 | Apache 2.0 |
| 数据可控 | 经 Anthropic 服务器 | 可本地/自托管 |
| 中国可用 | 需科学上网 | 无限制 |
| 推理质量 | 5 | 4 |
| 社区生态 | 商业支持 | 160K+ Stars, 900+ 贡献者 |
| 价格 | $20/月 或 API 按量 | 免费 |

---

## 其他图形化产品

| 产品 | 类型 | 说明 | 定价 |
|------|------|------|------|
| **Cursor** | AI-native IDE | VS Code fork，深度 Agent 能力，多文件编辑最强之一 | Free / $20/月 Pro |
| **Windsurf / Devin Desktop** | AI-native IDE | Codeium 出品，Cascade Agent 模式，免费额度慷慨 | Free / $15/月 Pro |
| **GitHub Copilot** | IDE 插件 | 微软/GitHub 出品，VS Code/JetBrains 深度集成，企业级合规 | $10/月 Individual |
| **Continue** | IDE 开源插件 | 开源 IDE 插件，可接入任意模型，本地优先 | 免费 |

---

## 下载与安装

### Claude Code

```bash
# npm 安装（全平台）
npm install -g @anthropic-ai/claude-code

# 或使用 Anthropic 提供的安装脚本
curl -fsSL https://docs.anthropic.com/claude-code/install | bash
```

安装后运行 `claude` 启动，首次运行需登录 Anthropic 账号并配置 API Key。

### opencode

```bash
# 一键安装脚本（全平台）
curl -fsSL https://opencode.ai/install | bash

# macOS (Homebrew)
brew install opencode

# Linux (Debian/Ubuntu)
curl -fsSL https://opencode.ai/install | bash

# Linux (Arch) — 通过 paru 或 yay 从 AUR 安装
paru -S opencode
# 或手动安装
curl -fsSL https://opencode.ai/install | bash

# Linux (RHEL/Fedora)
curl -fsSL https://opencode.ai/install | bash

# Windows (winget)
winget install opencode
# 或手动下载安装包
# 访问 https://opencode.ai/download 下载 .exe

# npm 安装
npm install -g @opencode/opencode
```

### Cursor

访问 [cursor.com](https://cursor.com) 下载对应系统安装包：
- **Windows**: `.exe` 安装包
- **macOS**: `.dmg` 或 `brew install --cask cursor`
- **Linux (Debian/Ubuntu)**: `.deb` 包
- **Linux (Arch)**: AUR — `paru -S cursor-bin`
- **Linux (RHEL/Fedora)**: `.rpm` 包

### GitHub Copilot

- **VS Code**: 扩展面板搜索 "GitHub Copilot" 安装
- **JetBrains**: Plugins 市场搜索 "GitHub Copilot"
- **全平台**: 也可通过 `npm install -f @github/copilot` 安装 CLI 版

---

## 使用方式

### opencode 基础用法

```bash
# 在当前目录启动（默认 TUI 模式）
opencode

# 直接在命令行描述任务
opencode "为这个项目的 README 添加安装说明"

# 指定模型
opencode --model claude-sonnet-4-20250514

# 指定会话文件
opencode --session my-session.json
```

### Claude Code 基础用法

```bash
# 启动交互式会话
claude

# 单次任务
claude "重构这个模块，提取公共接口"

# 从文件读取任务描述
claude "$(cat task.md)"
```

### Skill 与配置机制

Skill 是 Agent 工具的个性化配置单元，用于定义 Agent 的行为、风格和工具权限：

**opencode 配置（`/home/a/RootStack/opencode.jsonc`）：**

```jsonc
{
 "customInstructions": "你是一个严谨的系统编程导师。回答时：\n1. 优先用 C 语言举例\n2. 必须指出内存布局和性能影响\n3. 如果不确定，直接说不知道",
 "allowedTools": ["read", "edit", "grep", "glob", "bash"],
 "model": "claude-sonnet-4-20250514",
 "tabAutocomplete": false
}
```

**Claude Code 配置（`~/Library/Application Support/Claude/claude.json`）：**

```json
{
 "allowReadOnly": false,
 "skipConfirmation": false,
 "theme": "dark"
}
```

Skill 的本教程相关用法：可在项目根目录放置 `.opencode/rules.md` 或 `.claude.md`，让 Agent 自动加载本知识库的约定。

---

## 作者的 Agent 工具使用哲学

### 第一原则：安全

任何 AI 产品都必须注意安全问题。Agent 工具拥有读写文件、执行命令的权限，本质上是"能操作你电脑的 AI"。将代码完整的发给闭源商业服务存在数据泄露风险。因此作者眼中 **opencode 等开源工具在安全性上显著优于闭源旗舰产品**——代码不离开本地，可审计，可自托管。

### 第二原则：性能

Agent 工具是投入生产的工具，要看重生产力。如果一个工具在安全上有优势但完成任务效率极低，那也是不可接受的。在实际使用中，可以混合策略：**日常开发用 opencode 保证安全，在需要深度推理的复杂重构场景临时使用 Claude Code**（注意脱敏）。

### 第三原则：使用习惯

Agent 工具的个性化定制（Skill、自定义指令、工具权限配置）决定了它和你工作流的契合度。支持社区贡献的皮肤/主题，但有节制：
- 配色和提示词风格可以自定义
- **不过度美化**——花哨的 UI 分散注意力，影响操作手感
- 作者偏好**完全终端模式**，不使用桌面 GUI，保持黑窗口的专注度

```bash
# 作者的日常：只有黑窗口
# 左终端: opencode 会话
# 右终端: 普通 shell
# 没有花哨的 UI，只有代码和对话
```

### AI 的特殊用法

**嵌入知识库问答：**
在 RootStack 根目录启动 opencode，直接提问知识库内容：
```
> C 语言的数组退化是什么？给我看代码例子
```
Agent 会自动 grep 相关文件、读取内容并给出带代码引用的回答。

**重复性工作自动化：**
```
> 帮我把这个 Markdown 文件里所有的错别字"部份"改为"部分"
> 检查这篇博客的语法错误并纠正
> 给这个目录下的所有 .c 文件添加统一的版权头注释
```

**AI 学习法（自检模式）：**
这是本教程推荐的学习方法——让 AI 充当你的考官：
```
> 你读一下 /RootStack/数据结构/A_数组_Array.md，然后出 5 道题考我
> 我对数组退化这个概念不清楚，帮我解释并出两道巩固题
```
这和本教程各章节末尾的练习思路一致：**学完知识点后让 AI 出题检验，答错的部分让 AI 针对性补充讲解。**

---

## 附：官方资源

| 工具 | 官方文档 | GitHub |
|------|---------|--------|
| opencode | [opencode.ai/docs](https://opencode.ai/docs) | [github.com/anomalyco/opencode](https://github.com/anomalyco/opencode) |
| Claude Code | [docs.anthropic.com/claude-code](https://docs.anthropic.com/en/docs/claude-code) | 闭源 |
| Cursor | [cursor.com/docs](https://docs.cursor.com) | 闭源 |
| Continue | [continue.dev/docs](https://docs.continue.dev) | [github.com/continuedev/continue](https://github.com/continuedev/continue) |
