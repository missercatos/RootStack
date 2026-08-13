# VS Code 的配置与使用 (VS Code Setup & Usage)
---

## 为什么要推荐 VS Code

VS Code（Visual Studio Code）是微软开源的跨平台编辑器，是目前全球使用率最高的开发者工具。它定位是"编辑器 + 插件生态"，用轻量换取全功能：

| 优势 | 说明 |
|------|------|
| 免费开源 | 完全免费，代码在 GitHub 公开，无商业限制 |
| 跨平台 | Windows / macOS / Linux 全支持，配置可同步 |
| 插件生态 | 插件市场数十万扩展，语言/主题/工具全覆盖 |
| 轻量快速 | 启动和响应远快于重量级 IDE，无项目也能用 |
| 内置能力 | 终端、调试、Git、任务、远程开发开箱即用 |
| 与 C 生态配合 | C/C++、CMake、Python、汇编插件齐全，本仓库教程均可用它 |

> 定位：VS Code 是一个"装了插件的编辑器"。它不是某个语言的专属 IDE，而是**所有语言共用的工作台**——这正是它区别于 PyCharm（只管 Python）、IDEA（只管 Java）的核心价值。

---

### 第一节：不同系统的下载安装
---

1.1 Windows
-----------

| 方式 | 命令 / 操作 |
|------|-------------|
| 官网安装包 | 下载 [code.visualstudio.com](https://code.visualstudio.com/) 的 User Installer (.exe)，双击安装 |
| winget | `winget install vscode` |
| Chocolatey | `choco install vscode` |

安装选项建议：

| 选项 | 建议 |
|------|------|
| 添加到 PATH | 勾选（终端可输 `code` 打开） |
| 添加到资源管理器右键菜单 | 勾选（方便） |
| 关联文件类型 | 勾选 |
| 创建桌面快捷方式 | 随意 |

> 安装完成后，在任意目录的终端输入 `code .` 即可用 VS Code 打开当前文件夹——这个习惯会贯穿整个教程。

1.2 macOS
---------

| 方式 | 命令 / 操作 |
|------|-------------|
| 官网 .dmg | 下载 dmg，拖入 Applications 文件夹 |
| Homebrew | `brew install --cask visual-studio-code` |

首次打开可能需要"在系统设置中允许应用"（受 Gatekeeper 限制）。安装后可在 VS Code 内 `Cmd+Shift+P` → 输入 "Shell Command" → 安装 `code` 命令到 PATH。

1.3 Linux
---------

| 发行版 | 命令 |
|--------|------|
| Debian / Ubuntu | 官网下载 .deb 双击安装，或 `sudo dpkg -i code_*.deb` |
| Fedora / RHEL | 官网 .rpm，或 `sudo rpm -i code_*.rpm` |
| Arch | `sudo pacman -S code` |
| 通用 | Snap：`sudo snap install code --classic` |
| 通用 | 官网 .tar.gz 解压即可用（免安装） |

> 跨平台提示：Linux 上若 `code` 命令不可用，在 VS Code 内 `Ctrl+Shift+P` 搜索 "Install 'code' command in PATH" 修复。

---

### 第二节：基础配置（中文界面 + 字体）
---

2.1 中文语言包
-------------

VS Code 默认英文界面，安装语言包后变为简体中文：

1. 打开扩展面板：`Ctrl+Shift+X`（macOS：`Cmd+Shift+X`）
2. 搜索 `Chinese (Simplified) Language Pack`
3. 安装后右下角提示重启，重启即生效

> 建议界面语言跟随系统语言，但**代码和文档保持英文习惯**——查报错、看文档时英文资料永远是第一手。

2.2 字体与连字
-------------

推荐的编程字体（都免费、开源）：

| 字体 | 特点 | 安装方式 |
|------|------|----------|
| Fira Code | 支持连字（`!=` `=>` 显示为图形符号），编程字体标杆 | [GitHub Releases](https://github.com/tonsky/FiraCode) 下载后双击安装 |
| Cascadia Code | 微软出品，Windows 官方终端同款 | winget：`winget install Microsoft.CascadiaCode` |
| JetBrains Mono | JetBrains 出品，清晰紧凑 | [官网](https://www.jetbrains.com/lp/mono/) 下载 |

安装字体后，在 VS Code 设置里启用：

1. `Ctrl+,`（macOS：`Cmd+,`）打开设置
2. 搜索 `font-family`，把字体名加在最前面：`Fira Code, Consolas, monospace`
3. 搜索 `font-ligatures`，勾选启用连字

> 效果对比：连字开启后，`->` `<=` `!=` 显示为符号而非字符序列，可读性提升明显。设置都写入 `settings.json`（右下角打开设置 JSON 即可看到），跨平台同步配置文件即可带到任何机器。

---

### 第三节：插件配置（编程体验优化）
---

3.1 必装插件（通用）

| 插件 | 作用 |
|------|------|
| **Chinese Language Pack** | 中文界面 |
| **Prettier - Code formatter** | 统一代码格式（JS/TS/JSON/Markdown 等） |
| **Error Lens** | 报错直接显示在代码行尾，不用悬停 |
| **GitLens** | 查看每行代码的提交历史、作者、blame |
| **Material Icon Theme** | 文件图标，目录结构一眼可辨 |
| **Path Intellisense** | 路径自动补全 |
| **Todo Tree** | 高亮 TODO/FIXME 注释并列出清单 |

3.2 按语言安装

| 语言 | 插件组合 |
|------|----------|
| Python | Python（微软官方，含 Pylance 补全 + 调试 + 虚拟环境识别） |
| C / C++ | C/C++（微软官方，含 IntelliSense + 调试）、CMake Tools |
| 汇编 | x86 and x86_64 Assembly（语法高亮 + 缩进）、GDB Debugger |
| Markdown | Markdown All in One（预览、表格、目录） |
| JSON / YAML | YAML（校验 + 补全）、JSON Tools |

> 使用说明：C/C++ 插件首次打开 C 项目会提示安装编译器；Windows 上推荐装 MSYS2 或 Visual Studio Build Tools（见 C 教程环境配置章节），Linux 装 `gcc` 即可，macOS 装 Xcode Command Line Tools。

3.3 教程类插件

| 插件 | 内容 |
|------|------|
| Learn Vim | 在 VS Code 内交互式练习 Vim 键位（配合本仓库 vim教程） |
| Python Interactive Window | Jupyter 风格交互式执行 |
| GitHub Copilot | AI 代码补全（付费，试用 30 天；类光标补全可看 Continue 等开源替代） |

3.4 安装方式汇总

```text
Ctrl+Shift+X 打开扩展面板 → 搜索插件名 → 安装 → （部分）重启
```

命令行安装（配合 `code` 命令）：

```bash
code --install-extension ms-python.python
code --install-extension ms-vscode.cpptools
```

---

### 第四节：核心功能
---

| 功能 | 入口 | 说明 |
|------|------|------|
| 命令面板 | `Ctrl+Shift+P` | 所有操作的入口，输入命令名即可执行 |
| 快速打开 | `Ctrl+P` | 输文件名跳转，`:` 后跟行号直达指定行 |
| 内置终端 | `` Ctrl+` `` | 集成终端，无需切换窗口 |
| 调试 | `F5` | 断点、单步、变量监视，支持 C/C++/Python 等 |
| 智能补全 | 输入即触发 | 语言插件提供的 IntelliSense |
| 跳转定义 | `F12` | 跳到函数/变量定义处 |
| 全局搜索 | `Ctrl+Shift+F` | 全目录搜索文本，支持正则 |
| 多光标编辑 | `Alt+Click` | 同时编辑多处，批量改代码利器 |
| 重命名 | `F2` | 变量/函数批量重命名 |
| 代码格式化 | `Shift+Alt+F` | 一键格式化当前文件 |
| 快捷注释 | `Ctrl+/` | 单行/块注释切换 |
| 代码折叠 | `Ctrl+Shift+[` | 折叠代码块，长文件导航更清晰 |
| 任务运行 | `Ctrl+Shift+B` | 运行配置好的构建任务（如 gcc 编译） |
| 远程开发 | Remote-SSH / WSL | 本地编辑远程服务器代码（配合 SSH 场景） |
| 代码片段 | 输入触发 | 语言自带或自定义片段，常用结构一键生成 |

> 核心心法：**命令面板（Ctrl+Shift+P）是 VS Code 一切的入口**。记不住快捷键时，直接输命令名，比如 "format"、"toggle comment"、"show all commands"。

---

### 第五节：快捷键速查
---

| 操作 | Windows/Linux | macOS |
|------|---------------|-------|
| 命令面板 | `Ctrl+Shift+P` | `Cmd+Shift+P` |
| 快速打开文件 | `Ctrl+P` | `Cmd+P` |
| 打开设置 | `Ctrl+,` | `Cmd+,` |
| 搜索文件内容 | `Ctrl+Shift+F` | `Cmd+Shift+F` |
| 打开/关闭终端 | `` Ctrl+` `` | `` Ctrl+` `` |
| 注释/取消注释 | `Ctrl+/` | `Cmd+/` |
| 格式化代码 | `Shift+Alt+F` | `Shift+Option+F` |
| 跳转定义 | `F12` | `F12` |
| 重命名符号 | `F2` | `F2` |
| 多光标 | `Alt+Click` | `Option+Click` |
| 复制行 | `Shift+Alt+↓` | `Shift+Option+↓` |
| 删除行 | `Ctrl+Shift+K` | `Cmd+Shift+K` |
| 切换侧边栏 | `Ctrl+B` | `Cmd+B` |
| 切到编辑区终端 | `Ctrl+1` | `Cmd+1` |
| 显示悬停提示 | `Ctrl+Space` | `Ctrl+Space` |

---

### 第六节：VS Code 的替代（按语言选编辑器）
---

VS Code 是"通用工作台"，但专精某一语言时，专用 IDE 往往体验更深。选择逻辑：**多语言混写用 VS Code，单语言深耕用专用 IDE**。

| 语言 / 方向 | 推荐专用工具 | 理由 |
|-------------|-------------|------|
| C / C++ | CLion（商业）、Visual Studio（Windows）、Qt Creator | 调试与 CMake 集成更完整 |
| Python | PyCharm Professional / Community | 纯 Python 项目补全、重构、科学计算体验最佳 |
| Java | IntelliJ IDEA | 无可争议的 Java 事实标准 |
| Go | GoLand | Go 工具链原生整合 |
| Rust | RustRover / IDEA 插件 | 宏、借用检查提示最完整 |
| JavaScript/TS 前端 | WebStorm / VS Code | WebStorm 更重更全，VS Code 性价比高 |
| 终端环境 | Vim / Neovim | 无图形界面、SSH 远程场景，见 [[vim教程|vim教程]] |
| 轻量快速 | Sublime Text、Zed | 启动毫秒级，编辑大文件不卡 |

| 你的场景 | 建议 |
|----------|------|
| 本仓库跨 C/Python/汇编学习 | **VS Code 一个就够** |
| 工作主力是单一语言 | 专用 IDE + 其 Vim 插件 |
| 只有 SSH 终端 | Vim / Neovim（见 vim教程） |
| 电脑配置低 / 只需编辑 | 轻量编辑器即可 |

