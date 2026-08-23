# 04 编辑器与 IDE 选择

Java 是所有主流语言中 IDE 依赖度最高的：静态类型 + 冗长样板代码 + 庞大类库，让智能补全和重构的价值被放大到极致。本章对比 IntelliJ IDEA、VS Code、Vim/Neovim 及老牌 Eclipse/NetBeans 四条路线，并给出明确建议。

---

## 一、为什么 Java 比 C 更依赖 IDE

先回答一个 C 程序员的合理疑问："我写 C 一直用 vim + gcc，为什么 Java 要上重型 IDE？"

| 维度 | C | Java |
|------|---|------|
| 标准库规模 | 极小（stdio/stdlib 等几十个头文件）| 巨大（java.util/java.io/java.net... 数千个类）|
| 样板代码量 | 少（无类概念）| 多（getter/setter/构造器/接口实现）|
| 重构频率 | 低（项目结构稳定）| 高（重命名方法/提取接口是日常）|
| 框架魔法 | 无 | 注解+反射+DI 容器，跳转与提示强依赖语义分析 |
| 编译反馈 | gcc 报错文本 | IDE 内即时红线 + 快速修复 |

结论：C 的世界里 vim + 手册页够用；Java 的世界里没有 IDE 补全，你会在查 API 文档上浪费大量时间。**但 jshell 与轻量编辑器也有其位置**——本章最后给出分阶段建议。

---

## 二、IntelliJ IDEA（强烈推荐）

JetBrains 出品，Java 生态的**事实标准**。国内招聘 JD 里"熟悉 IDEA"几乎不写但默认你会。

### 2.1 社区版 vs 旗舰版

| 能力 | Community（免费）| Ultimate（付费）|
|------|-----------------|----------------|
| 核心 Java / Kotlin 开发 | 支持 | 支持 |
| Maven / Gradle 构建 | 支持 | 支持 |
| Git 集成、调试、重构 | 支持 | 支持 |
| **Spring / Spring Boot 框架支持** | 不支持 | 支持（自动配置提示、Bean 导航）|
| **数据库工具** | 不支持 | 支持（内置 DataGrip 级别客户端）|
| HTTP Client（测 API）| 基础 | 完整 |
| JavaScript/TypeScript | 基础 | 完整（前端联调友好）|
| 远程开发 / Docker 编排增强 | 部分 | 完整 |
| 价格 | 免费 | 约 $8.9+/月；**学生邮箱免费申请** |

学生认证入口：<https://www.jetbrains.com/community/education/>（高校邮箱或学信网材料），拿到授权后 Ultimate 全家桶免费用到毕业。

### 2.2 安装

```bash
# Windows(winget)
winget install JetBrains.IntelliJIDEA.Community

# macOS(brew)
brew install --cask intellij-idea-ce      # 社区版
brew install --cask intellij-idea         # 旗舰版

# Linux(JetBrains Toolbox 是官方推荐管理器)
# 下载 toolbox: https://www.jetbrains.com/toolbox-app/
# 或 snap: sudo snap install intellij-idea-community --classic
```

### 2.3 初学者必调设置

首次启动后建议检查：

1. **主题与字号**：Settings → Appearance，字体建议 14+
2. **编码统一 UTF-8**：Settings → Editor → File Encodings，三处全部 UTF-8
3. **确认 JDK**：File → Project Structure → SDK，指向已装的 Temurin 21
4. **自动导入**：Settings → Editor → General → Auto Import，勾选 Add unambiguous imports
5. 关闭不必要的插件提速

> IDEA 本身就是 Java 写的（还记得 [[00_Java是什么|第一章]] 的应用全景图吗），第一次启动较慢属正常，之后索引缓存会加速。

---

## 三、VS Code 路线

已有 VS Code 使用习惯、或机器配置有限的读者可选。

### 3.1 安装扩展包

在扩展市场安装 **Extension Pack for Java**（微软官方），一键包含六个核心扩展：

| 扩展 | 职责 |
|------|------|
| Language Support for Java (红帽) | 基于 eclipse.jdt.ls 提供补全/诊断/跳转 |
| Debugger for Java | 断点调试 |
| Test Runner for Java | JUnit 测试集成 |
| Maven for Java | pom.xml 支持与常用命令 |
| Project Manager for Java | 项目视图管理 |
| Visual Studio IntelliCode | AI 补全排序 |

```bash
# 命令行批量安装
code --install-extension vscjava.vscode-java-pack
```

### 3.2 配置要点

settings.json 关键项：

```json
{
  "java.jdt.ls.java.home": "/path/to/jdk-21",
  "java.configuration.runtimes": [
    { "name": "JavaSE-21", "path": "/path/to/jdk-21", "default": true }
  ],
  "java.compile.nullAnalysis.mode": "automatic",
  "files.encoding": "utf8"
}
```

首次打开 Java 项目时右下角会提示导入——等待语言服务器完成索引（状态栏有进度）再开始写代码。

### 3.3 VS Code 路线的边界

| 场景 | 体验 |
|------|------|
| 单文件学习、刷题 | 流畅够用 |
| 中小型 Maven 项目 | 可用 |
| 大型多模块工程 | 明显慢于 IDEA，重构能力弱一档 |
| Spring 全家桶深度支持 | 需另装 Spring Boot Extension Pack，且仍不及 IDEA Ultimate |

配置排障小贴士：VS Code 的 Java 支持偶尔会"抽风"（补全失效、红线不消失），通用急救三板斧——

1. 命令面板执行 `Java: Clean Language Server Workspace` 并重启
2. 确认 `java.jdt.ls.java.home` 指向的 JDK 真实存在
3. 删除工作区 `.vscode/settings.json` 中冲突的手写配置，让默认值接管

---

## 四、Vim/Neovim 路线（终端党）

如果你已经跟随 [[../vim教程|Vim 教程]] 建立了肌肉记忆，可以用 **eclipse.jdt.ls（jdtls）** 语言服务器把 Neovim 武装成 Java 编辑器。VS Code 的 Java 支持底层用的也是它。

### 4.1 方案选择

| 方案 | 说明 |
|------|------|
| nvim-jdtls 插件（mfussenegger/nvim-jdtls) | 官方推荐的精细配置方案，需手写 setup |
| nvim-lspconfig + jdtls | 通用 LSP 配置方式 |
| LazyVim 等发行版自带 Java extras | 最省事 |

### 4.2 最小可用示例（nvim-lspconfig）

以 lazy.nvim 为例：

```lua
-- ~/.config/nvim/lua/plugins/lsp-java.lua
return {
  {
    "neovim/nvim-lspconfig",
    ft = { "java" },
    dependencies = { "mfussenegger/nvim-jdtls" },
    config = function()
      local jdtls = require("jdtls")
      -- jdtls 需要 workspace 目录存放索引缓存
      local ws_dir = vim.fn.stdpath("cache") .. "/jdtls-workspace"
      jdtls.start_or_attach({
        cmd = { "jdtls" },                       -- PATH 中的 jdtls 启动脚本
        root_dir = vim.fs.root(0, { ".git", "pom.xml", "build.gradle" }),
        settings = {
          java = {
            configuration = {
              runtimes = {
                {
                  name = "JavaSE-21",
                  path = vim.env.HOME .. "/.sdkman/candidates/java/current",
                  default = true,
                },
              },
            },
          },
        },
      })
    end,
  },
}
```

获得的能力：补全（omnifunc 由 LSP 接管）、go to definition/references、重命名重构、诊断列表、代码动作（`vim.lsp.buf.code_action()` 自动生成 getter/setter 等）。

缺失的能力：IDEA 级别的调试图形界面、可视化 profiler、开箱即用的框架感知。终端党用 `nvim-dap` 可以补上调试，配置成本较高。

> 定位判断：Vim 路线适合"主编辑器是 Neovim 的读者保持手感"，不适合作为学习 Java 第一年的主力——把精力花在语言本身而不是编辑器配置上更划算。

---

## 五、其他选择：Eclipse 与 NetBeans

| 维度 | Eclipse IDE | Apache NetBeans |
|------|-------------|-----------------|
| 出身 | IBM → Eclipse 基金会，Java IDE 元老 | Sun → Oracle → Apache |
| 免费 | 是 | 是 |
| 体积/速度 | 较重，插件生态庞杂 | 中等 |
| 现状 | 存量用户多（部分企业标准配置），新项目占比下降 | 小众但维护良好 |
| 特色 | RCP 富客户端开发、某些企业内部定制基于它 | 开箱即用度高，JavaFX 支持好 |
| 建议 | 有公司强制要求再用 | 了解即可 |

历史定位说明：2010 年代初"Eclipse vs IDEA"还是个争论话题，如今社区答案已收敛——**新学直接 IDEA，不必回头**。

---

## 六、综合对比表

| 维度 | IntelliJ IDEA | VS Code + Java 插件 | Neovim + jdtls | Eclipse |
|------|--------------|--------------------|----------------|---------|
| 启动速度 | 慢（数秒）| 快 | 快 | 慢 |
| 补全智能度 | 最高（类型推断/链式提示）| 中上（同款引擎，上下文整合略弱）| 中上 | 中 |
| 重构能力 | 最强（安全改名/提取方法/内联）| 基础集 | 基础集 | 强 |
| 调试体验 | 最佳（变量视图/表达式求值）| 良好 | 需 nvim-dap 配置 | 良好 |
| 内存占用 | 高（1-4GB 常见）| 中 | 低 | 高 |
| 框架支持（Spring）| Ultimate 顶级 | 扩展包中等 | 几乎无 | 插件中等 |
| 上手成本 | 低（图形化一切）| 低 | 高（需 LSP 知识）| 中 |
| 价格 | CE 免费 / UT 收费 | 免费 | 免费 | 免费 |
| 终端党友好度 | 低 | 中 | 最高 | 低 |

一句话选型：

- **不确定就选 IDEA 社区版**——零决策成本，行业默认
- 已是 VS Code 重度用户且只做轻量学习——VS Code 路线
- Neovim 主力且愿意付配置成本——jdtls 路线
- 公司指定 Eclipse——入乡随俗

---

## 七、分阶段使用建议

```mermaid
flowchart LR
    P1["入门篇<br/>语法学习"] -->|"IDEA CE<br/>单文件也能跑"| P2["深入篇<br/>Maven/Gradle 项目"]
    P2 -->|"继续 IDEA CE<br/>构建工具接管编译"| P3["工程化篇<br/>Spring Boot"]
    P3 -->|"需要数据库/Spring 增强"| UT["考虑 IDEA Ultimate<br/>学生免费"]
    P1 -.->|"随手试验"| JS["jshell<br/>不需要任何 IDE"]
```

1. **入门篇**：IDEA 社区版建一个空项目即可；同时养成开 jshell 的习惯，小片段验证不进 IDE
2. **深入篇**：项目开始用 Maven 组织，IDEA 直接打开 pom.xml 自动导入
3. **工程化篇**：涉及 Spring + 数据库时评估 Ultimate（学生认证免费）；届时 [[02_Linux环境配置|Linux 章]] 学过的命令行技能在远程部署中依然有用武之地
4. **任何时候**：不要因为 IDE 太聪明而跳过对手动流程的理解——下一章我们故意先用纯 javac 走一遍完整流程，就是为了打这个底

### 7.1 入门期推荐工作流

以 IDEA 社区版为例，入门阶段最省心的用法：

1. 新建项目：File → New → Project → 选 Java，Build system 保持 IntelliJ（先不碰 Maven），SDK 指向 Temurin 21
2. 在 `src` 目录右键 → New → Java Class，命名后直接写代码
3. 点 main 方法左侧绿色箭头运行——IDEA 内部帮你完成了 javac + java 两步
4. 想看"裸奔流程"时，打开 IDEA 底部 Terminal 标签页手动敲 javac/java 命令对照理解

VS Code 用户对应流程：装好扩展包后新建 `.java` 文件直接写，右上角 Run 按钮；终端里 Ctrl+` 打开集成终端。

共同原则：**IDE 的运行按钮是黑盒加速器，Terminal 是白盒验证器**，两者交替使用才学得扎实。

---


## 八、IDEA 高频快捷键（提前背，终身受益）

工具效率的一半在快捷键。以下按使用频率排序，Windows/Linux 与 macOS 双栏：

| 操作 | Win/Linux | macOS |
|------|-----------|-------|
| 万能搜索（双击 Shift）| Double Shift | Double Shift |
| 查找动作/设置 | Ctrl+Shift+A | Cmd+Shift+A |
| 补全 | Ctrl+Space | Ctrl+Space |
| 快速修复 / 意图操作 | Alt+Enter | Option+Enter |
| 格式化代码 | Ctrl+Alt+L | Cmd+Option+L |
| 重命名（重构）| Shift+F6 | Shift+F6 |
| 跳转到定义 | Ctrl+B | Cmd+B |
| 跳转到用法 | Ctrl+Alt+F7 | Cmd+Option+F7 |
| 生成代码（getter/setter 等）| Alt+Insert | Cmd+N |
| 注释行 | Ctrl+/ | Cmd+/ |
| 复制当前行 | Ctrl+D | Cmd+D |
| 运行当前配置 | Shift+F10 | Ctrl+R |
| 调试运行 | Shift+F9 | Ctrl+D(调试键位有差异,以实际为准) |

> 记忆策略：不要一次背完。前四个（万能搜索、快速修复、格式化、重命名）覆盖日常 80% 场景，用一周自然固化。

## 九、插件与进阶话题

### 9.1 IDEA 推荐插件

| 插件 | 用途 |
|------|------|
| Lombok Support | 配合 @Data 等注解消除 getter/setter 样板（工程化篇讲）|
| .ignore | 维护 .gitignore |
| GitToolBox | git 状态增强 |
| Translation | 划词翻译英文报错与文档 |

克制原则：插件装多了启动变慢、索引变慢，按需添加。

### 9.2 远程开发

IDEA 与 VS Code 均支持"本地界面 + 远程引擎"模式：代码和语言服务跑在 Linux 服务器上，本地只做展示。对 RootStack 读者意义在于——[[02_Linux环境配置|Linux 章]] 的服务器环境可以直接作为开发后端，本地 mac/Windows 无需重复配 JDK。此功能旗舰版更完整，工程化篇部署章节会实践一次完整流程。

### 9.3 AI 辅助补全

GitHub Copilot、JetBrains AI Assistant 等均可用。学习期的建议：**初学阶段慎用强生成**——让 AI 替你写 main 方法体，等于跳过了建立肌肉记忆的过程；用它解释报错、审查你的代码则收益明显。

---

## 十、jshell：不需要 IDE 的快速试验

JDK 9 起自带的交互式解释器（REPL）。写一行看一行结果，是验证 API 行为的最快途径：

```bash
$ jshell
jshell> System.out.println("hello")
hello

jshell> 21 * 2
$2 ==> 42
```

详细用法见下一章 [[05_第一个程序与jshell|第一个程序与 jshell]]。这里只想建立观念：**不是每个问题都值得开 IDE 建工程**。"这个方法返回什么？""这行正则对不对？"——jshell 十秒出答案。

各环境启动速记：

| 环境 | 命令 |
|------|------|
| 任意平台终端 | `jshell` |
| IDEA 内置 | Tools → JShell Console（社区版也有）|
| 带依赖运行 | `jshell --class-path xxx.jar` |

---

## 十一、常见问题排查

| 现象 | 解决 |
|------|------|
| IDEA 打不开项目，提示 No SDK | File → Project Structure → SDK → 添加 JDK 并指向安装目录 |
| VS Code 补全迟迟不出来 | 语言服务器未完成索引，看右下角进度；或 `Java: Clean Language Server Workspace` 重启 |
| IDEA 中文乱码 | Settings → Editor → File Encodings 全部 UTF-8；Help → Edit Custom VM Options 加 `-Dfile.encoding=UTF-8` |
| Neovim jdtls 连不上 | 确认 `jdtls` 在 PATH 中；`:LspInfo` 查看日志；workspace 缓存目录可删重建 |
| 笔记本内存小跑不动 IDEA | Help → Change Memory Settings 调到 2048MB；关闭无关插件；或改用 VS Code |

---

## 十二、本章小结

- Java 对 IDE 的依赖度远高于 C：大库 + 样板代码 + 重构频繁，智能辅助价值极大
- **首选 IntelliJ IDEA 社区版**：免费、行业标准；Ultimate 的 Spring/数据库能力等工程化阶段再上，学生免费
- VS Code + Extension Pack for Java 是合格的轻量路线；Neovim + jdtls 服务于终端党，底层与 VS Code 同源（eclipse.jdt.ls）
- Eclipse/NetBeans 了解历史地位即可，新学不必选
- 快捷键先记四个：双击 Shift 万能搜索、Alt+Enter 快速修复、Ctrl+Alt+L 格式化、Shift+F6 重命名
- 分阶段策略：入门 CE 够用，工程化按需 UT；jshell 随时处理小验证
- 工具为学习服务：手动 javac 流程仍要掌握，下一章从它讲起

## LeetCode 巩固

本章无新语法，热身题不变：[两数之和](https://leetcode.cn/problems/two-sum/)。

一个实用建议：在 LeetCode 网页端刷题不需要本地 IDE，但把代码同步保存到本地仓库是好习惯。等下一章学完 main 方法与 jshell，就可以把题解放进自己的 `leetcode` 目录里用 `java` 直接运行验证。
