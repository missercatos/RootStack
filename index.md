
<h1 align="center">RootStack</h1>

<p align="center">
 <em>以 C 作为出发点，覆盖多领域、多计算机语言的百科全书式教程 —— C、C++、Python、Rust、数据结构与算法、Linux 系统、系统内核、汇编、网络安全（红队）</em>
</p>

<p align="center">
 <img src="https://img.shields.io/badge/版本-0.17.0-blue?style=flat-square" alt="version"/>
</p>

<p align="center">
 <a href="./git.md">Git 指南</a> · <a href="./github-settings.md">GitHub 设置</a> · <a href="./科学上网.md">科学上网</a> · <a href="./国际付费操作.md">国际付费</a> · <a href="./AI_Agent工具使用教程.md">AI Agent 工具</a> · <a href="./red_team/总目录与快速查询.md">红队知识库</a> · <a href="./ISSUES.md">参与贡献</a>
</p>

<p align="center">
 <b> 静态网站：<a href="https://rootstack.misser.top">rootstack.misser.top</a></b>
</p>

---

## 关于本教程

本教程体系是一套以 C 语言为核心、向上延伸至 C++ 和数据结构、向下探及汇编和内核的完整知识库。教程使用 [Obsidian](https://obsidian.md/) 的双向链接 \`[[文件名]]\` 组织内容，形成相互引用的知识网络。

**路径说明**: 路径 A-D 是**通识学习路径**，适合所有计算机学习者；路径 E 是**职业分化路径**——网络安全（红队），基于 ArchStrike 体系，已覆盖 ~125 篇知识库文件。通识路径学完后，按兴趣选择职业方向。

**本教程有瑕疵**。教程内容包含 AI 辅助生成的部分，可能存在概念偏差、代码错误或总结不到位的情况。请读者始终保持批判性阅读，不要盲目照搬。如果你发现错误或有改进建议，请见 [问题讨论区](ISSUES.md)——我们非常欢迎你的议题和 Pull Request，项目组在经过实践检验和综合讨论之后会进行修改。

---

## 推荐学习环境：Linux

本教程涉及编译、链接、系统调用、内核模块、汇编等底层内容。在 Windows 下学习 C/系统编程，频繁遇到 PATH 差异、缺少标准工具链、权限模型不一致、ABI 不同步等问题，每个问题都在分散你对核心知识的注意力。**推荐使用 Linux 作为学习环境**，一次解决所有环境问题，把精力留给真正要学的东西。

### 新手推荐：Linux Mint

最推荐新手用来踩坑的发行版是 [**Linux Mint**](https://linuxmint.com/)。
- 基于 Ubuntu LTS，软件兼容性好，apt 生态成熟
- Cinnamon 桌面体验接近 Windows，上手成本低
- 开箱即用，不需要折腾就能进入学习状态

至于 Ubuntu 和 RHEL/Fedora，它们广为人知更多是因为企业/服务器市场占有率大（大多为企业程序员在使用），而非对新手友好。Mint 在桌面体验上反而更适合初学者。

如果你已经对 Linux 有一定了解，Debian、Fedora、openSUSE 都是不错的选择。想深入系统底层的话，Arch Linux 也值得尝试，但不建议作为入门首选。

### 快速入门

- [Linux Mint 官网](https://linuxmint.com/) — 下载安装、查看文档
- [Linux Mint 中文社区](https://linuxmint.com.cn/) — 中文资料与交流

---

## AI Agent 工具

AI Agent 工具是当前开发者生产力的核心加速器——它们不只是代码补全，而是能自主理解项目、读取文件、编辑代码、运行测试并迭代修复的"AI 协作者"。本教程体系本身就是在 Agent 工具的辅助下编写和维护的。

教程涵盖主流 Agent 工具（Claude Code、opencode、Cursor、GitHub Copilot 等）的推荐、安装、使用方式，以及作者的安全优先、性能至上、终端黑窗口的使用哲学。详见 [AI_Agent工具使用教程](AI_Agent工具使用教程.md)。

---

## Obsidian 使用指南

本教程设计为在 Obsidian 中阅读以获得最佳体验（双向链接预览、图谱视图、可折叠答案）。以下是各平台的安装和导入方法：

### Linux

```bash
# Linux Mint / Ubuntu
sudo apt install obsidian

# Arch Linux
sudo pacman -S obsidian

# Flatpak (通用)
flatpak install flathub md.obsidian.Obsidian
```

### macOS

```bash
brew install --cask obsidian
```

### Windows

在 [obsidian.md/download](https://obsidian.md/download) 下载 `.exe` 安装包，运行安装即可。

### 导入本教程

1. 打开 Obsidian，点击 "Open folder as vault"
2. 选择本教程的根目录（即包含本 `README.md` 的文件夹）
3. Obsidian 会自动识别 `.obsidian/` 配置并加载所有双链接

导入后，从本文件（README）出发，通过 `双链接` 跳转到任意章节。阅读模式下按 `Ctrl/Cmd + 点击` 即可跳转。

---

## 教程体系结构

```
RootStack/ ├ v0.17.0
├── README.md ← 你在这里
│
├── 路径A-C主线.md C 主线: 从零到内核
├── 路径B-CPP主线.md C++ 主线: 从零到应用开发
├── 路径C-C向下兼容C++.md C → C++ 向下兼容
├── 路径D-DSA算法刷题.md 竞赛策略完全路线图 (力扣 + 多OJ)
├── 路径E-红队职业路径.md 网络安全职业路径 (含CTF→SRC/比赛分化)
├── 路径F-Rust学习路径.md Rust 学习路径 (含力扣练习与竞赛OJ)
├── 路径G-Java全栈路径.md Java 全栈职业路径 (Java核心+前端闭环 Phase 0-11)
├── 路径-考研408方向.md 408考研统一入口（四科阅读方向 + 章节索引整合）
├── 路径-工程化底层方向.md 底层系统工程化路径 (C/汇编/OS/内核)
├── 路径-工程化应用方向.md 应用层工程化路径 (C++/前后端/数据库)
│
├── linux/ Linux 百科全书式教程 (63章 + 4发行版完整指南)
│ ├── README.md Linux 教程总览与学习路线
│ ├── 01-Linux概述与历史.md → 63-包管理器崩溃恢复与驱动管理通用指南.md (63章主线)
│ ├── distro/
│ │ ├── arch/ Arch Linux 完整指南（含 NVIDIA Legacy 驱动迁移与故障恢复）
│ │ ├── debian/ Debian/Ubuntu 完整指南
│ │ ├── redhat/ RHEL/CentOS/Fedora/Rocky 完整指南
│ │ └── nix/ NixOS 声明式配置指南
│ └── resources/ 命令速查表 + 术语对照表
│
├── 算法/ 算法竞赛内容 (仅供 Path D 学习者)
│ ├── 算法技巧/ (28篇) 基础算法技巧 (数组/搜索/DP/图论等)
│ ├── 数学/ (5篇) 数论/组合数学/CRT (Phase 7)
│ ├── 搜索进阶/ (3篇) 双向搜索/A*/IDA* (Phase 8)
│ ├── DP优化/ (3篇) 单调队列/斜率/四边形不等式 (Phase 9)
│ ├── DP进阶/ (9篇) 区间DP/背包DP/树形DP/状压DP等 (Phase 6)
│ ├── 图论/ (15篇) 最短路/MST/拓扑排序/SCC/LCA/网络流等 (Phase 4)
│ ├── 字符串扩展/ (8篇) Trie/SA/SAM/Z函数/回文自动机等 (Phase 6)
│ ├── 杂项技巧/ (4篇) 莫队/CDQ/整体二分/ODT (Phase 10)
│ ├── 题目/ (8篇) 算法题目存档
│ └── 计算几何/ (3篇) 二维几何/凸包/半平面交 (Phase 11)
│
├── c语言教程/ C 语言: 入门 → 深化 → 库大全
│ ├── c目录.md
│ ├── 1入门/ (10篇) 2深化/ (9篇) 3数据结构/ (9篇)
│ ├── 4工程化/ (2篇) CMake深入 + C项目工程化(CI/静态分析/发布)
│ └── 库大全/ → 容器类库/ 功能类库/ 第三方库/
│
├── cpp教程/ C++ 教程: 基础 → 深化 → 容器库 → 功能库 → 第三方库
│ ├── cpp目录.md
│ ├── cpp基础教程/ (11篇) cpp深化教程/ (18篇, 含CMake深入+Conan/vcpkg)
│ ├── 容器库/ (5子目录) cpp功能库/ (8子目录)
│ └── cpp第三方库/ (11子目录, 网络含Web框架实战)
│
├── rust/ Rust 教程: 入门 → 深入 → 实践 → 工程 → 重构
│ ├── rust目录.md
│ ├── 1入门/ (14篇) 2深入/ (11篇) 3实践/ (7篇, 含axum Web开发)
│ ├── 4工程/ (14篇, 含sqlx+workspace) 5重构/ (6篇)
│
├── java/ (48篇) Java 全栈教程: 入门 → 深入 → 工程化 (Spring体系)
│ ├── java目录.md
│ ├── 1入门/ (18篇) 三平台环境配置 + 语法 + OOP核心
│ ├── 2深入/ (12篇) 集合源码 + 并发 + JVM + 设计模式
│ └── 3工程化/ (18篇) Maven/Gradle + Spring全家桶 + Docker/CI + 架构
│
├── 前端开发/ (~91篇) 前端全栈: 基础 → 框架 → 可视化 → 实战 → 融会贯通
│ ├── 引导阅读.md 按需求导引(六条路线+技术栈组合)
│ ├── 01-基础/ HTML+CSS+JS+TS (21篇)
│ ├── 02-CSS框架/ Tailwind+Bootstrap5+Bootstrap4+Foundation (10篇)
│ ├── 03-JS框架/ Vue2/Vue3/React/Next.js/Angular/AngularJS (25篇)
│ ├── 04-DOM与交互/ DOM+AJAX+JSON (8篇) 05-工具库/ jQuery系 (2篇)
│ ├── 06-数据可视化/ Chart.js+ECharts+Highcharts+SVG (12篇)
│ ├── 07-图标与UI/ Font-Awesome (2篇)
│ └── 08-项目实战/ (4篇) 09-融会贯通/ 工程化+联调+选型 (3篇)
│
├── lua-tutorial/ (7篇) Lua 教程: 简介 → 安装 → 基础 → 进阶 → 集成
│ ├── 00-lua简介.md 01-安装与环境配置.md 02-基础入门.md
│ ├── 03-进阶教程.md 04-C与C++集成.md
│   └── 05-Neovim示例.md          06-Love2D示例.md
│
├── python/ (~60篇)              Python 教程: 入门 → 精通 → 实战 → 专项工具
│   ├── python目录.md
│   ├── 1入门/ (8篇)               2精通/ (8篇)             3实战/ (5篇)
│   ├── 4库/                       5工程化/ (6篇)           6量化分析/ (6篇)
│   ├── 7科学计算/ (5篇)           8数据可视化/ (5篇)       9图形处理/ (4篇)
│   └── 10web应用/ (5篇)           11人工智能/ (6篇)
│
├── 数据结构/ (21篇)             语言无关的数据结构教程 + DSA学习路线
│ ├── A_数组_Array → T_图的高级算法 (共20篇，A-T连续编号)
│
├── 操作系统/ (10篇) 大学本科操作系统课标 + 深入底层扩展
│ ├── 操作系统_索引.md
│ ├── A_操作系统概述 / B_进程管理 / C_线程与并发 / D_CPU调度
│ ├── E_同步与死锁 / F_内存管理 / G_内存分配器 / H_文件系统 / I_进程间通信
│ └── J_IO管理
│
├── 计算机原理/ (10篇) 大学本科计算机组成原理课标 + 深入底层扩展
│ ├── 计算机原理_索引.md
│ ├── A_数据表示 / B_缓存层级 / C_CPU架构 / D_内存层次结构 / E_指令集体系结构
│ ├── F_总线系统 / G_输入输出系统 / H_CPU数据通路与控制器 / I_流水线与指令流水
│ └── J_运算方法与运算器
│
├── 计算机网络/ (7篇) 大学本科计算机网络课标 + 深入底层扩展 (408全覆盖)
│ ├── 计算机网络_索引.md
│ └── A_体系结构 / B_物理层 / C_数据链路层 / D_网络层 / E_传输层 / F_应用层
│
├── 密码学/ (~29篇) 全领域密码学教程: 导读 + 20个专题
│ ├── 密码学导读.md 阅读起点与学习路线
│ └── 专题/ 初等数论/古典/对称/哈希/公钥/椭圆曲线/格/后量子/量子/零知识证明/同态加密/数字签名/密钥管理/秘密共享/密码协议/侧信道/工具等
│
├── 内核/ (~35篇) 四种内核 + C与Rust新时代 + Rust内核开发
│ ├── 系统内核/ (7篇) 语言运行时内核/ (7篇)
│ ├── 工具内核/ (7篇) 游戏引擎内核/ (7篇)
│ ├── Rust内核/ (6篇) Rust 在内核中的实践
│ └── 内核索引.md C与Rust的内核新时代.md
│
├── 汇编基础/ (~16篇) x86/ARM 汇编教程 + 硬件直接操作
│ ├── 汇编目录.md
│ ├── 1基础/ (4篇) 2硬件操作/ (11篇)
│
├── 数据库/ (12篇) 多数据库教学: MySQL深入 + 全主流数据库
│ ├── 数据库目录.md
│ ├── mysql/ (5篇) 安装配置/SQL语法/查询进阶/索引事务/权限备份
│ ├── postgresql/ sqlite/ sqlserver/ oracle/
│ └── mongodb/ redis/
│
├── red_team/ (~186篇) 网络安全红队职业路径 (ArchStrike体系)
│ ├── 网安基础知识/ (10篇) 渗透测试方法论
│ ├── 前端基础/ (34篇) 实战教程/ (13篇，含14天实训)
│ ├── 数据库安全/ (10篇) 各数据库渗透: 探测/提权/破解
│ ├── archstrike-*教学/ (48篇) 10组ArchStrike工具教程
│ ├── 服务器部署与运维/ (4篇) QQ Bot攻防实战
│ └── ctf_trea/ (~51篇) CTF竞赛知识库
│ ├── Web/Web前置技能/ (HTTP协议/操作系统/数据库/HTML-CSS/程序语言)
│ ├── Web/Web工具配置/ (虚拟机/BurpSuite/Chrome/WebShell/菜刀/端口扫描/远程连接/目录爆破)
│ ├── Web/信息泄露/ (目录遍历)
│ └── Web/SQL/ (注入5型 + mysql结构9场景)
│
├── git.md Git 与 GitHub 终端操作指南 (17节)
├── github-settings.md GitHub 网页端设置指南（新增）
├── vim教程.md Vim 编辑器教程 (安装+快捷键+:指令大全+现代替代)
├── VSCODE的配置与使用.md VS Code 配置与使用 (安装+插件+快捷键+替代)
├── dsh.md DeepSeek Harness 教程 (安装+Web UI+Profile+插件开发与发布)
├── deepseek-harness/ (26篇) DSH框架深度教程: 认知+架构+实战+自建Harness
│ ├── deepseek-harness目录.md
│ ├── 1认知/ (3篇) 范式跃迁 + 全景 + Cordis论文精读
│ ├── 2架构/ (7篇) 内核/Profile/服务DI/事件/能力三角色/LLM适配/沙箱
│ ├── 3实战开发/ (9篇) 源码导读 + 插件全流程 + 发布
│ └── 4设计自己的Harness/ (7篇) 用Cordis从零造框架(含200行骨架源码)
├── npm.md npm 使用教程 (安装配置+版本管理+npx+进阶+排障)
├── VERSION                      项目版本号: 0.17.0
└── ISSUES.md 问题讨论与贡献指南
```

---

## 写在教程之前

本教程体系的目标是提供一套从 C 出发、延伸至系统底层的完整知识库，涵盖 C、C++、数据结构与算法、Linux 系统、操作系统内核、Rust 语言。我们追求的不是"一本通"的虚假承诺，而是一个结构清晰、双向链接、支持 AI 辅助学习的知识体系。

**核心原则**:

1. **精简内容，深入底层** -- 不在无关紧要处堆砌文字，关键节点深入讲解，其余留给读者思考。
2. **底层至上** -- C 和 C++ 不同于 Java/Python，它们靠近硬件。本教程体系涉及汇编、内存布局、指针本质等底层话题，从"CPU 看到了什么"的角度剖析。
3. **辩论式阅读** -- 希望读者带着批判态度阅读，将更多时间放在思考上。练习题的目的就是启发思考，不会就回去重想。
4. **双链接体系** -- 使用 Obsidian 双链接连接不同模块，形成计算机知识网络。
5. **不反对也不鼓吹 AI** -- 自我思考是第一要务，AI 工具进行辅助。推荐读者旁边开着 AI，遇到不懂的问题先自己对 AI 解释看法让其纠正，来形成自己的理解。
6. **实践为主，教程为辅** -- 真正的工程师经验来自项目堆砌和自我踩坑。本教程体系提供结构和指引，修炼靠个人。

---

## 内核 —— 技术栈的底层基石

C 语言之所以诞生，就是为了写操作系统内核。Dennis Ritchie 在 Bell Labs 创造 C 语言时，目标就是用它重写 Unix 内核（之前用汇编）。至今，Linux 内核（3000万行）、Windows NT 内核、FreeBSD 内核、以及几乎所有嵌入式 RTOS 都是用 C 写的。

### C 语言写内核的优势

- **零成本抽象**: C 的每个语法结构都直接映射到机器指令，没有隐藏的内存分配或运行时开销
- **直接硬件访问**: 指针可以映射到任意物理地址（MMIO），volatile 保证不会被优化掉
- **可预测的内存布局**: struct 的字段顺序和 padding 都是可控的
- **无运行时依赖**: 内核没有 libc，C 语言本身不需要运行时支持
- **ABI 稳定性**: C ABI 是事实上的跨语言标准，Rust/C++/Zig 都通过 C ABI 互操作

### 新时代: C 与 Rust 的结合

传统上 C 是内核的唯一选择。但约 70% 的 CVE 安全漏洞来自内存 bug。Rust 的所有权系统在编译期消除这些 bug，同时保持零成本抽象的承诺。

Linux 6.1 开始正式支持 Rust 内核模块。未来的趋势不是 C vs Rust，而是 **C AND Rust**：
- C 负责成熟稳定的核心子系统（调度器、内存管理、VFS）
- Rust 负责新开发的驱动和子系统（GPU driver、Binder、网络协议）
- 两者通过 C ABI 的 FFI 无缝交互

详见 [C与Rust的内核新时代](内核/C与Rust的内核新时代.md)

### 四种内核视角

| 内核类型 | 入口 | 代表 |
|---------|------|------|
| 系统内核 | [C语言与操作系统](ISSUES.md) | Linux, Windows, BSD |
| 语言运行时内核 | [语言运行时内核索引](ISSUES.md) | CRT, CPython, V8, JVM |
| 工具内核 | [工具内核索引](ISSUES.md) | SQLite, Redis, MySQL, Chromium |
| 游戏引擎内核 | [游戏引擎内核索引](ISSUES.md) | Unity, Unreal, raylib |

---

## 关于刷题

从工程化培训视角来看，算法竞赛并不是本教程体系下刷题的主要目的。刷题的唯一目的是**在自认为学会一个语法点或数据结构之后，去检验自己是否真的掌握了**。如果你阅读本教程的初衷不是为了竞赛，或者首要目标是步入工程化开发，我们不推荐将大量时间消耗在各大题库中。本教程在各章节末尾附带少量力扣题目，用于自检即可。

关于 AI 使用：题库平台普遍有反作弊机制。用 AI 进行**题目理解、思路讨论、代码审查**是安全且推荐的；但直接复制 AI 生成的代码提交到平台有封号风险。无论如何，本教程不推荐将刷题数量和排名放在自我思考之上。

### 推荐算法资源

以下开源项目可配合本教程的 DSA 模块使用：

| 项目 | 语言 | Stars | 说明 |
|------|------|-------|------|
| [OI-wiki](https://github.com/OI-wiki/OI-wiki) | 中文 | 26.3k | 编程竞赛百科，完整知识树，做题遇到不会的先查这里 |
| [TheAlgorithms/Python](https://github.com/TheAlgorithms/Python) | Python | 223k | 全部算法 Python 实现，教育级代码质量 |
| [TheAlgorithms/C](https://github.com/TheAlgorithms/C) | C | 22.2k | C 语言算法实现（本教程 C 主线的直接对照参考） |
| [TheAlgorithms/C-Plus-Plus](https://github.com/TheAlgorithms/C-Plus-Plus) | C++ | 34.5k | C++ 算法实现（本教程 C++ 主线的直接对照参考） |
| [TheAlgorithms/Java](https://github.com/TheAlgorithms/Java) | Java | 66k | Java 算法实现 |
| [TheAlgorithms/Rust](https://github.com/TheAlgorithms/Rust) | Rust | 25.9k | Rust 算法实现 |
| [TheAlgorithms/Go](https://github.com/TheAlgorithms/Go) | Go | 18.1k | Go 算法实现 |
| [awesome-algorithms](https://github.com/tayllan/awesome-algorithms) | 资源列表 | 25.4k | 算法学习精选书单/课程/竞赛网站/可视化工具 |
| [Algo-Atlas](https://github.com/lvy010/Algo-Atlas) | C++/Py | 493 | LeetCode 2000 题/8 月刷题计划，含完整分类笔记 |

详细用法见 [路径 D 的推荐资源章节](路径D-DSA算法刷题.md#推荐算法资源)。

---

## 学习路径（通识）

以下五条路径覆盖 C、C++、DSA、Rust 四大方向，适合所有计算机学习者，章节级阅读顺序、推荐阅读物、语言官方文档链接均已标注。

| 路径 | 文件 | 适合人群 |
|------|------|---------|
| A: C 主线 | [路径A-C主线](路径A-C主线.md) | 系统编程/嵌入式/内核开发 |
| B: C++ 主线 | [路径B-CPP主线](路径B-CPP主线.md) | 应用开发 + 底层贯通 |
| C: C→C++ | [路径C-C向下兼容C++](路径C-C向下兼容C++.md) | 先 C 后 C++ 向下兼容 |
| D: DSA 刷题 | [路径D-DSA算法刷题](路径D-DSA算法刷题.md) | 数据结构与算法/力扣练习/竞赛入门 |
| F: Rust 学习 | [路径F-Rust学习路径](路径F-Rust学习路径.md) | C++ 之后的系统编程进阶 |
| G: Java 全栈 | [路径G-Java全栈路径](路径G-Java全栈路径.md) | 直接学全栈开发, Java 为后端核心 (Spring体系) |

## 职业路径（分支）

以下路径为**职业方向分化**，前五条是通识基础，不分方向都可学习；从这里开始进入具体职业领域，需要通识基础作为前置。

| 路径 | 文件 | 适合人群 |
|------|------|---------|
| E: 红队 (ArchStrike) | [路径E-红队职业路径](路径E-红队职业路径.md) | 网络安全/渗透测试/CTF/红队攻防，含CTF→SRC/比赛分化 |

> 本教程体系可当作类百科全书使用，内容完善但体量庞大。若作为教程从头通读，效率不高。建议按照路径文件中的推荐阅读顺序，结合索引文件进行选择性学习。同时推荐与 AI 进行问答互动学习——在自认为掌握语法或数据结构之后，去 [力扣](https://leetcode.cn/) 做几道题验证即可。如遇到错误，不建议死磕，可用 AI 辅助纠正思路。

---

## 关于网络安全发行版

目前主流的面向网络安全的专用 Linux 发行版主要分三个体系：

1. **Kali Linux**（Debian 系）—— 由 Offensive Security 维护，最广为人知，工具齐全，基于 Debian 稳定版，适合从 Debian/Ubuntu 转过来的用户
2. **Arch 系（BlackArch / ArchStrike）** —— 滚动更新，工具库极大（BlackArch 有 2800+ 工具），DIY 程度高，适合熟悉 Arch 的用户
3. **Parrot OS**（Debian 系，独立分支）—— 轻量、注重隐私和开发环境，CTF 场景常见，介于 Kali 和日常使用之间

每个体系各有优劣：Kali 装完即用但臃肿；Arch 系灵活但需要一定 Linux 基础；Parrot 在资源和功能之间平衡较好。

RootStack 的网安部分基于 **ArchStrike（Arch 体系）**，因此要求使用者掌握 Arch Linux 的基本操作。但网安知识本身与发行版无关——即使你使用其他体系，知识点仍然适用。

另外，不一定要装专门的网安系统。**Windows + 合适的工具 + 自己写的脚本**，同样可以完成出色的安全测试工作。选择哪个发行版取决于你的使用习惯和具体场景。

---

## 各模块入口速查

| 模块 | 入口 | 说明 |
|------|------|------|
| C 语言 | [C 教程目录](c语言教程/c目录.md) | 入门 → 深化 → 3数据结构 → 库大全 |
| C++ | [C++ 教程目录](cpp教程/cpp目录.md) | 基础 → 深化 → 容器库 → 功能库 → 第三方库 |
| Python | [Python 教程目录](python/python目录.md) | 入门 → 精通 → 实战 → 库 → 工程化 → 专项工具 |
| Vim | [Vim 编辑器教程](vim教程.md) | Windows安装+快捷键大全+:指令大全+现代替代 |
| VS Code | [VS Code 配置与使用](VSCODE的配置与使用.md) | 三平台安装+中文/字体配置+插件+快捷键 |
| dsh | [DeepSeek Harness 教程](dsh.md) | 安装/Web UI/Profile/插件安装与开发/发布 |
| DSH 框架深度 | [DeepSeek Harness 完整教程](deepseek-harness/deepseek-harness目录.md) | Cordis架构+论文精读+插件实战+自建Harness (26篇) |
| npm | [npm 教程](npm.md) | 安装配置/基本使用/版本管理/npx/进阶/排障 |
| 数据结构 | [DSA 学习路线](数据结构/DSA学习路线.md) | 18个主题, Phase 1→6, 力扣题目 |
| 算法技巧 | [动态规划](算法/算法技巧/动态规划.md) | 24个算法专题, 语言无关 |
| 内核 | [内核总索引](内核/内核索引.md) | 四种内核 + C与Rust新时代 |
| 汇编 | [汇编基础教程](汇编基础/汇编目录.md) | 基础入门 → 硬件直接操作 (16篇) |
| 数据库 | [数据库教学目录](数据库/数据库目录.md) | MySQL深入 + PostgreSQL/SQLite/MSSQL/Oracle/MongoDB/Redis (12篇) |
| Java 全栈 | [Java 教程目录](java/java目录.md) | 入门 → 深入 → 工程化/Spring全家桶 (48篇), 路径G |
| 前端开发 | [前端引导阅读](前端开发/引导阅读.md) | HTML/CSS/JS/TS + Vue/React/Angular + 可视化, 按需路线 (~91篇) |
| 红队 | [红队知识库总目录](red_team/总目录与快速查询.md) | ArchStrike渗透体系, ~125篇, 职业路径 |
| AI Agent | [AI_Agent工具使用教程](AI_Agent工具使用教程.md) | 编码 Agent 工具推荐、安装、使用哲学 |

---

## 力扣即时练习

本教程体系以 [力扣 (LeetCode)](https://leetcode.cn/) 为推荐的日常练习平台。各语言基础、数据结构章节末尾附带对应力扣题目类型指引。

**学习路线** → 力扣 (适合求职/工程/理解数据结构) 
**竞赛路线** → 洛谷 + Codeforces + POJ/HDU + AtCoder (适合走算法竞赛的选手)

郑重提醒：刷题的意义在于**自检**，不在于数量和排名。每学完一个主题做 2-4 道题验证理解即可。关于 AI 与刷题的边界：用 AI 讨论题目思路是好的，但直接复制 AI 生成的代码提交有被检测和封号的风险。

---

## 快速参与贡献

RootStack 欢迎任何人贡献内容、修正错误或提出建议。

### 网页端操作（无需安装 Git）

1. **Fork 本项目** — 打开 GitHub 项目页，点击右上角 `Fork` 按钮
2. **提建议** — 点击仓库上方的 `Issues` 标签 → `New Issue`，描述你的问题或想法
3. **在线修改并提交 PR** — 在 GitHub 网页上浏览到要修改的文件，点击 编辑按钮 → 修改 → `Commit changes` → 选择 `Create a new branch` → `Propose changes` → 点击 `Create Pull Request`
4. **Fork 后如何同步上游** — 在 GitHub 网页上，你的 fork 仓库页点击 `Sync fork` → `Update branch`

### 终端操作（专业流程）

详见 [Git 与 GitHub 终端操作指南](git.md)，包含从安装到 PR 合并的完整教程。

```
# 极简流程：Fork → Clone → 修改 → PR
git clone https://github.com/你的用户名/RootStack.git
cd RootStack
git remote add upstream https://github.com/原项目名/RootStack.git
git checkout -b my-feature
# 修改文件...
git add .
git commit -m "说明你的修改"
git push origin my-feature
# 然后去 GitHub 网页点 "Compare & pull request"
```

### Git 安装（各平台）

| 平台 | 安装命令 | 备注 |
|------|---------|------|
| Linux (Debian/Ubuntu) | `sudo apt install git` | |
| Linux (Arch) | `sudo pacman -S git` | |
| macOS | `brew install git` | 也可从 git-scm.com 下载 .dmg |
| Windows | `winget install Git.Git` 或从 git-scm.com 下载 exe | |

**作者观点**：推荐使用终端里的原生 Git，而不是 `git.exe` 或 IDE 内置的 Git GUI。终端 Git 给你完整的能力、一致的跨平台体验，以及对每一步操作的掌控感。图形化的 Git 工具适合查看历史，但日常操作建议回归命令行。

---

## 求 Star

如果这个项目对你有帮助，欢迎在 [GitHub](https://github.com/missercatos/RootStack) 点个 **Star** (｡>﹏<｡) 你的支持是我们更新的动力！

---

## 致谢

本教程体系的开发过程中使用了以下 AI 辅助工具：

- [opencode](https://opencode.ai) — 项目重构与内容批量处理
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — 方案设计、内容编写与代码审查

关于这些工具的详细介绍、安装使用、安全风险及作者的 Agent 使用哲学，见 [AI_Agent工具使用教程](AI_Agent工具使用教程.md)。

感谢所有通过 [问题讨论区](ISSUES.md) 和 Pull Request 参与贡献的读者。

---
## 近期任务

 主要是两大任务，撰写密码学部分，与筛查优化数据结构部分。
 本教程虽然是整合了已有的开源知识，但大部分需要手动筛查和优化，即使有AI辅助也很难做完。另外本教程还有一些是没有被开源的教程，需要自己去探索撰写。
 
---
## 近期更新

> 以下为项目管理员维护的更新日志。新增内容、删除内容、重大修改请在此处简要记录。

| 日期 | 变更类型 | 说明 |
| ---- | --------- | ------------------------------------------------------------------------------------------------ |
| 7.13 | 首次提交项目 | 将作者以前的cpp_deep,c-learning项目整合起来并删减整理形成的一套教程 |
| 7.17 | 新增职业路径 | red_team/网络安全模块(~125篇, ArchStrike体系), 路径E红队职业路径, 学习/职业路径区分 |
| 7.18 | OI-wiki移植 | 从 OI-wiki 移植 32 篇算法文件: 图论(15篇) + 字符串扩展(8篇) + DP进阶(9篇), 新建 算法/图论/ 算法/字符串扩展/ 算法/DP进阶/ |
| 7.18 | Rust 教程整合 | 新增 Rust 教程体系 (~55篇: 入门14+深入11+实践6+工程12+重构6)，路径F-Rust学习路径，rust目录.md 索引，Rust内核融入 内核/Rust内核/，跨模块双链接 |
| 7.20 | 新增密码学 | 密码学是计算领域的一门重要学科，所以创建密码学部分。专门列一个类目。 |
| 7.22 | 网站上线 | 部署至 Cloudflare Pages，域名 rootstack.misser.top，GitHub Actions 自动发布 |
| 7.22 | 内容更新 | Linux 推荐改为 Mint，新增网安发行版说明，增加求 Star 链接，版本升至 0.5.0 |
| 7.31 | 新增Lua教程 | 新增 lua-tutorial/ (7篇: 简介+安装+基础+进阶+C/C++集成+Neovim+Love2D)，双链接接入 README/index，版本升至 0.8.0 |
| 8.11 | 新增Python教程 | 新增 python/ (~60篇: 入门7+精通8+实战5+库索引+工程化6+量化分析6+科学计算5+可视化5+图形4+Web5+AI6)，定位为C程序员的Python工具手册，双链接接入 README/index，版本升至 0.9.0 |
| 8.12 | 汇编重构+硬件操作 | 汇编基础/ 重构为分目录体系 (1基础/4篇 + 2硬件操作/11篇: Port I/O/MMIO/特权级/内联汇编精通/中断IDT/UART/VGA/PIT/键盘/引导/ARM)，以"直接操作硬件"为核心，全部示例 QEMU 可跑，版本升至 0.10.0 |
| 8.13 | 全库规范性修订 | 全库去除 emoji 表情符号 (141 文件)；python/汇编 选择题→力扣题目链接 (~770道)；ASCII 字符画→Mermaid 渲染图 (~20处)；README/index 补 python 条目+双链接修复；python 新增"写在教程之前"(三平台下载+编辑器)+全章 Windows/macOS 补充；新增 vim教程.md (Windows安装+快捷键+指令大全)。版本升至 0.11.0 |
| 8.14 | 编辑器三连+环境准备 | python 新增 1入门/00_准备工作.md (三平台环境配置+终端跑Python+编辑器选择)；vim教程.md 补全第九节"现代 Vim 上位替代" (IDE Vim插件/Neovim/LazyVim/ARKVim)；新增 VSCODE的配置与使用.md (三平台安装+中文界面+字体连字+插件配置+功能/快捷键+单语言替代)。版本升至 0.12.0
| 8.15 | dsh+npm 工具教程 | 新增 dsh.md (DeepSeek Harness: 安装/Web UI/Profile/插件安装卸载/插件开发与发布)；新增 npm.md (通用 npm 教程: 安装配置/版本管理/npx/workspaces/发布/排障)，两篇互相链接。版本升至 0.13.0
| 8.16 | 数据库三线扩充 | 新增 数据库/ (12篇: MySQL深入5章 + PostgreSQL/SQLite/MSSQL/Oracle/MongoDB/Redis)；red_team 新增 数据库安全/ (10篇: 渗透探测/MySQL UDF/MSSQL xp_cmdshell/Oracle/PostgreSQL/Redis 未授权与主从RCE/MongoDB/口令破解/工具链)；ctf_trea/Web 新增 SQL/ (16篇: 整数型/字符型/报错/布尔盲注/时间盲注 + mysql结构 Cookie/UA/Referer/二次注入/过滤空格/AND_OR/ORDER_BY/UPDATE/综合训练)。版本升至 0.14.0
| 8.17 | Java 全栈体系 + 三语言补缺 | 新增 java/ (48篇: 1入门18章三平台配置+OOP核心 / 2深入12章集合源码+并发+JVM / 3工程化18章 Maven+Spring全家桶+Docker/CI+应急排查+GitHub项目实战+架构入门)；新增 路径G-Java全栈路径 (Phase 0-10, 前端/运维规划中)；补缺 c语言教程/4工程化/ (CMake深入+C项目工程化)、cpp深化教程 16-17 (CMake进阶+Conan/vcpkg)、cpp第三方库 网络Web框架实战、rust 实践07 axum + 工程13-14 (sqlx+workspace)。版本升至 0.15.0 |
| 8.18 | DeepSeek Harness 框架深度教程 | 新增 deepseek-harness/ (26篇: 1认知3篇 范式跃迁+dsh全景+Cordis论文《A Programming Paradigm for Spatiotemporal Composability》精读 / 2架构7篇 Cordis内核+Fiber生命周期+Profile与Bundle分层+服务DI+事件四语义+能力三角色+LLM适配器StreamChunk+沙箱审批 / 3实战开发9篇 monorepo源码导读+插件全流程+defineTool+Config+Schemastery+热重载+类型安全+会话日志+发布 / 4设计自己的Harness7篇 决策树+200行Cordis骨架源码+工具流水线+多模型路由+安全审计+可观测回放+完整架构蓝图)；dsh.md 与新目录互链。版本升至 0.16.0 |
| 8.19 | 前端开发全栈目录 | 新增 前端开发/ (~91篇, 九子目录): 引导阅读.md 按需求六路线导引+四条技术栈组合 / 01-基础 HTML+CSS+JavaScript+TypeScript 21篇 / 02-CSS框架 Tailwind+Bootstrap5深入+Bootstrap4/Foundation速查 10篇 / 03-JS框架 Vue2/Vue3/React/Next.js/Angular 深入+AngularJS速查 25篇 / 04-DOM与交互+05-工具库+07-图标 12篇 / 06-数据可视化 Chart.js+ECharts+Highcharts+SVG 12篇 / 08-项目实战 企业官网+后台管理(Vue3)+数据看板(React)+电商首页(Tailwind) 4篇 / 09-融会贯通 工程化+Java前后端联调+技术栈选型 3篇；路径G 新增 Phase 11 前端闭环并接入引导阅读。版本升至 0.17.0 |
