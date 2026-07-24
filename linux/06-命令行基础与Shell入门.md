# 06 - 命令行基础与 Shell 入门

> Shell 是你与 Linux 内核对话的桥梁。无论是管理系统、编写脚本、还是处理数据，Shell 都是 Linux 用户最常打交道的界面。本章介绍 Shell 的基本概念、命令行结构、帮助系统和工作效率技巧，为你后续深入学习 Bash 编程和系统管理打下基础。

---

## 6.1 什么是 Shell

Shell（壳）是一个命令解释器，它接收你输入的命令，解释执行，并把结果返回给你。之所以叫"壳"，是因为它包裹在内核（kernel）之外，是用户与系统交互的界面。

```mermaid
graph LR
    A[用户] -->|输入命令| B[Shell<br/>bash/zsh/fish]
    B -->|解释执行| C[Linux 内核]
    C -->|返回结果| B
    B -->|显示输出| A

    style B fill:#e8f5e9,stroke:#4caf50,stroke-width:2px
    style C fill:#fff3e0
```

### 6.1.1 常见 Shell 对比

| Shell | 全名 | 特点 | 定位 |
|-------|------|------|------|
| **bash** | Bourne Again Shell | GNU 项目默认 Shell，最广泛使用的标准 | 通用、脚本之王 |
| **zsh** | Z Shell | bash 兼容 + 强大补全 + 主题（oh-my-zsh） | 交互体验最优 |
| **fish** | Friendly Interactive Shell | 开箱即用的智能补全和语法高亮 | 新手最友好 |
| **dash** | Debian Almquist Shell | 极简、快速，POSIX 严格兼容 | `/bin/sh` 链接目标 |
| **sh** | Bourne Shell | Unix 原始 Shell，POSIX 标准 | 脚本兼容性底线 |

```bash
# 查看当前使用的 Shell
echo $SHELL
# 输出: /bin/bash 或 /bin/zsh 或 /usr/bin/fish

# 查看系统中安装的所有 Shell
cat /etc/shells

# 切换 Shell（需要输入密码）
chsh -s /bin/zsh

# 临时使用不同 Shell
zsh       # 在 bash 中临时进入 zsh
exit      # 退出回到原来的 Shell
```

### 6.1.2 选择建议

| 角色 | 推荐 Shell | 理由 |
|------|------------|------|
| 通用/写脚本 | **bash** | 兼容性最好，每台 Linux 都有 |
| 日常交互使用 | **zsh** | 补全强大，oh-my-zsh 生态丰富 |
| 零配置开箱即用 | **fish** | 智能提示，无需配置 |
| 系统级 `/bin/sh` | **dash**（Debian 系） | 启动快，节省资源 |

---

## 6.2 终端、Shell、控制台的区别

这三个概念常被混用，但实际上有严格的技术区别：

| 概念 | 定义 | 类比 |
|------|------|------|
| **终端（Terminal）** | 输入输出的物理或模拟设备 | 电脑屏幕 + 键盘（硬件层面） |
| **终端模拟器（Terminal Emulator）** | 图形界面中模拟终端的软件 | GNOME Terminal、Alacritty、Kitty、Windows Terminal |
| **Shell** | 解释和执行命令的程序 | bash、zsh、fish |
| **TTY** | Teletypewriter，Linux 中的虚拟终端 | `Ctrl+Alt+F1~F6` 切换的纯文本界面 |
| **控制台（Console）** | 直接连接到计算机的物理终端 | 物理连接服务器的显示器+键盘 |

```bash
# 查看当前终端设备
tty
# 输出: /dev/pts/0 （伪终端，说明你在终端模拟器中）
# 或输出: /dev/tty1  （虚拟终端，Ctrl+Alt+F1 切换的）

# 查看所有登录的终端
who
```

**通俗总结**：
- 你打开了一个 **终端模拟器**（如 GNOME Terminal）
- 模拟器里跑着一个 **Shell**（如 bash）
- Shell 接收你的命令并交给内核执行

---

## 6.3 命令行结构

### 6.3.1 基本格式

```bash
command [选项] [参数...]
```

```bash
# 拆解举例
ls -l -a /home/alice
# │  └─┬─┘ └────┬────┘
# │   选项      参数（目标路径）
# 命令

# 等价写法
ls -la /home/alice       # 合并短选项
ls --all --format=long /home/alice   # 长选项（可读性更强）
```

### 6.3.2 选项的类型

| 类型 | 格式 | 示例 | 说明 |
|------|------|------|------|
| **短选项** | `-字母` | `-l`, `-a`, `-h` | 可以合并：`-la` = `-l -a` |
| **长选项** | `--单词` | `--all`, `--human-readable` | 可读性好，适合脚本 |
| **带参短选项** | `-字母 值` | `-n 5`, `-o output.txt` | 值紧跟或空格分隔 |
| **带参长选项** | `--单词=值` | `--lines=5`, `--output=file.txt` | 等号或空格分隔 |

```bash
# 示例：tail 命令的各种写法
tail -n 10 file.txt       # 短选项 + 参数
tail --lines=10 file.txt  # 长选项 + 参数
tail -10 file.txt         # 传统 BSD 风格（不推荐）
```

### 6.3.3 命令的类型

```bash
type ls        # alias / file / builtin / keyword
type cd        # shell builtin
type if        # shell keyword
```

| 类型 | 说明 | 示例 |
|------|------|------|
| **外部命令** | 磁盘上的可执行文件 | `ls`, `grep`, `python` |
| **内建命令** | Shell 内部实现的命令，无需外部程序 | `cd`, `echo`, `export`, `alias` |
| **别名** | 用户自定义的命令快捷方式 | `alias ll='ls -la'` |
| **关键字** | Shell 语法保留字 | `if`, `for`, `while` |
| **函数** | 用户自定义的 Shell 函数 | `myfunc() { echo hello; }` |

内建命令优先级**高于**外部命令。`type` 命令可以告诉你一个命令名实际对应什么：

```bash
type -a echo
# 输出:
# echo is a shell builtin
# echo is /usr/bin/echo
```

---

## 6.4 获取帮助

在 Linux 中，学会自己查找信息比记住所有命令更重要。

### 6.4.1 `man` — 系统手册

```bash
man ls                    # 查看 ls 的手册页
man 5 crontab             # 查看第 5 节（配置文件格式）的 crontab
man -k keyword            # 搜索含有关键词的手册页（同 apropos）
man -f ls                 # 查看 ls 的简短描述（同 whatis）
```

**手册页的节（Section）划分：**

| 节号 | 内容 | 示例 |
|------|------|------|
| 1 | 用户命令 | `man 1 ls` |
| 2 | 系统调用 | `man 2 open` |
| 3 | 库函数 | `man 3 printf` |
| 4 | 设备文件 | `man 4 tty` |
| 5 | 配置文件格式 | `man 5 crontab` |
| 6 | 游戏 | `man 6 fortune` |
| 7 | 杂项（协议、宏包） | `man 7 signal` |
| 8 | 系统管理命令 | `man 8 mount` |

```bash
# man 页面中的导航
# h = 帮助
# q = 退出
# / = 搜索（n 下一个，N 上一个）
# g = 跳到开头，G = 跳到结尾
# Space / f = 下一页，b = 上一页
```

### 6.4.2 `--help` — 快速帮助

大多数命令支持 `--help` 选项，输出简洁的使用说明：

```bash
ls --help                 # 简洁帮助
grep --help
man --help
```

### 6.4.3 `tldr` — 常用示例速查

`tldr`（Too Long; Didn't Read）提供命令的使用示例，比 man 更直观：

```bash
# 安装 tldr
# Debian/Ubuntu: sudo apt install tldr
# Fedora: sudo dnf install tldr
# Arch: sudo pacman -S tldr

tldr tar                  # 显示 tar 的常用示例
tldr find
tldr grep
```

tldr 的输出风格（示例）：

```text
  tar
  Archiving utility.

  - Create an archive from files:
    tar cf target.tar file1 file2 file3

  - Extract an archive into the current directory:
    tar xf source.tar

  - List the contents of an archive:
    tar tvf source.tar
```

### 6.4.4 `whatis` 与 `apropos`

```bash
whatis ls                 # 一行简述命令功能
whatis grep
# 输出: ls (1) - list directory contents

apropos "copy files"      # 搜索与"复制文件"相关的命令
apropos network           # 搜索网络相关命令
man -k network            # 等价于 apropos
```

### 6.4.5 `info` — GNU Info 文档

```bash
info coreutils            # GNU 项目的超文本手册
info ls
```

> 大多数情况下 `man` 和 `--help` 足够，`info` 主要是 GNU 项目使用。

---

## 6.5 Tab 补全

Tab 补全是命令行最高效的技巧之一。按 `Tab` 键让 Shell 自动补全：

```bash
# 补全命令名
syst<Tab>           → systemctl
firef<Tab>          → firefox

# 补全文件名和路径
cat /etc/hos<Tab>   → cat /etc/hosts
ls /usr/shar<Tab>   → ls /usr/share/

# 补全变量名
echo $HO<Tab>       → echo $HOME

# 按两次 Tab 查看所有可能补全项
ls /etc/<Tab><Tab>  → 列出 /etc 下所有文件和目录
```

zsh 和 fish 的 Tab 补全比 bash 更强，支持模糊匹配和历史补全。在 bash 中可以通过安装 `bash-completion` 包增强补全能力：

```bash
# Debian/Ubuntu
sudo apt install bash-completion

# Fedora
sudo dnf install bash-completion

# Arch Linux
sudo pacman -S bash-completion
```

---

## 6.6 命令历史

### 6.6.1 基本操作

```bash
history                        # 查看命令历史列表
history 20                     # 查看最近 20 条历史
!42                            # 重新执行历史中第 42 条命令
!!                             # 重新执行上一条命令
!$                             # 引用上一条命令的最后一个参数
!*                             # 引用上一条命令的所有参数
!ls                            # 执行最近一条以 ls 开头的命令
```

### 6.6.2 历史搜索

```bash
Ctrl+r                         # 反向搜索历史（最常用！）
# 输入关键词后，继续按 Ctrl+r 查找更早的匹配
# 按 Ctrl+s 正向搜索（如果终端未占用 Ctrl+s）
# 按 Enter 执行，按 Esc 或 Ctrl+g 取消

# 在 zsh 和 fish 中，直接输入前缀再按 ↑ 即可过滤历史
```

### 6.6.3 历史相关环境变量

```bash
echo $HISTSIZE          # 内存中保存的历史条数（默认 1000）
echo $HISTFILESIZE      # 历史文件中保存的条数（默认 2000）
echo $HISTFILE          # 历史文件路径（默认 ~/.bash_history）
echo $HISTCONTROL       # 历史控制选项

# HISTCONTROL 常用值：
# ignorespace    — 以空格开头的命令不记录
# ignoredups     — 连续重复的命令只记录一次
# ignoreboth     — 以上两者的组合（推荐）
# erasedups      — 删除所有重复记录
```

```bash
# ~/.bashrc 推荐设置
export HISTSIZE=10000
export HISTFILESIZE=20000
export HISTCONTROL=ignoreboth:erasedups
export HISTTIMEFORMAT="%F %T "   # 显示时间戳
shopt -s histappend              # 追加而非覆盖历史文件
```

---

## 6.7 命令行快捷键

高效的命令行操作离不开快捷键。以下是最常用的 bash 快捷键（大多与 Emacs 风格一致）。

### 6.7.1 进程控制

| 快捷键 | 功能 | 说明 |
|--------|------|------|
| `Ctrl+C` | 中断当前前台进程 | 发送 SIGINT 信号 |
| `Ctrl+D` | 发送 EOF（End Of File） | 在空行相当于退出 Shell（logout） |
| `Ctrl+Z` | 暂停当前前台进程 | 发送 SIGTSTP，通过 `fg` 恢复 |
| `Ctrl+S` | 暂停屏幕输出 | 按 `Ctrl+Q` 恢复 |
| `Ctrl+Q` | 恢复屏幕输出 | |
| `Ctrl+\` | 强制退出（SIGQUIT） | 比 Ctrl+C 更强，会生成 core dump |

### 6.7.2 光标移动

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+A` | 跳到行首 |
| `Ctrl+E` | 跳到行尾 |
| `Ctrl+B` | 光标左移一个字符（同左方向键） |
| `Ctrl+F` | 光标右移一个字符（同右方向键） |
| `Alt+B` | 光标左移一个单词 |
| `Alt+F` | 光标右移一个单词 |

### 6.7.3 文本编辑

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+W` | 删除光标前一个单词 |
| `Alt+D` | 删除光标后一个单词 |
| `Ctrl+U` | 删除从行首到光标的内容 |
| `Ctrl+K` | 删除从光标到行尾的内容 |
| `Ctrl+Y` | 粘贴上一次删除的内容（yank） |
| `Ctrl+T` | 交换光标前两个字符的位置 |
| `Alt+T` | 交换光标前两个单词的位置 |
| `Ctrl+L` | 清屏（等同于 `clear` 命令） |

### 6.7.4 记忆技巧表

| 字母 | 含义 | 举例 |
|------|------|------|
| **A** | **A**nfang（德语：开始）/ **A**head | `Ctrl+A` 跳到行首 |
| **E** | **E**nd | `Ctrl+E` 跳到行尾 |
| **B** | **B**ackward | `Ctrl+B` 光标后退 |
| **F** | **F**orward | `Ctrl+F` 光标前进 |
| **W** | **W**ord | `Ctrl+W` 删除单词 |
| **K** | **K**ill | `Ctrl+K` 删除到行尾 |
| **Y** | **Y**ank | `Ctrl+Y` 粘贴 |
| **L** | C**l**ear | `Ctrl+L` 清屏 |

---

## 6.8 环境变量（基础）

环境变量是 Shell 中的一个核心概念，在此只介绍基础用法，详细内容见 [[16-Bash编程基础]]。

### 6.8.1 查看环境变量

```bash
env                  # 查看所有环境变量
printenv             # 同上
echo $HOME           # 查看特定变量
echo $PATH           # 查看命令搜索路径
echo $USER           # 当前用户名
echo $SHELL          # 当前 Shell
echo $PWD            # 当前工作目录
```

### 6.8.2 最重要的环境变量：`$PATH`

`$PATH` 定义了当你在命令行输入一个命令时，Shell 去哪些目录搜索可执行文件：

```bash
echo $PATH
# 典型输出: /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# 各目录按顺序搜索，找到第一个匹配就执行
# 查看命令实际位置
which ls             # /usr/bin/ls
which python         # /usr/bin/python
```

### 6.8.3 设置与导出变量

```bash
# 设置变量（仅在当前 Shell 中有效）
MYVAR="hello"
echo $MYVAR

# 导出变量（对子进程也生效）
export MYVAR="hello"
export EDITOR="vim"
export LANG="zh_CN.UTF-8"

# 临时在命令执行时设置（只在这次命令中生效）
LANG=C ls --help          # 以英文显示帮助
EDITOR=nano crontab -e    # 用 nano 编辑 cron
```

### 6.8.4 永久设置

在 `~/.bashrc` 或 `~/.zshrc` 中添加：

```bash
export EDITOR="vim"
export PATH="$HOME/.local/bin:$PATH"
export LANG="zh_CN.UTF-8"
```

---

## 6.9 别名（Alias）

别名允许你用简短的名称代替长命令。

### 6.9.1 创建别名

```bash
# 查看所有别名
alias

# 创建别名
alias ll='ls -la'
alias la='ls -A'
alias l='ls -CF'
alias grep='grep --color=auto'
alias rm='rm -i'              # 删除前确认
alias cp='cp -i'
alias mv='mv -i'
alias ..='cd ..'
alias ...='cd ../..'

# 删除别名
unalias ll
```

### 6.9.2 忽略别名

```bash
# 使用命令的完整路径
/usr/bin/ls

# 在命令前加反斜杠
\ls
\rm dangerous_file.txt

# 使用 command 内建命令
command ls
```

### 6.9.3 常用别名推荐

```bash
# 系统操作
alias update='sudo apt update && sudo apt upgrade'    # Debian 系列
alias update='sudo dnf upgrade --refresh'              # Fedora
alias update='sudo pacman -Syu'                        # Arch Linux

# 文件操作
alias df='df -h'
alias du='du -h'
alias free='free -h'

# 网络
alias myip='curl ifconfig.me'
alias ports='ss -tulanp'

# Git（如已安装）
alias g='git'
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
```

### 6.9.4 永久保存别名

在 `~/.bashrc` 或 `~/.bash_aliases` 中添加（后者需要 source）：

```bash
# ~/.bashrc
if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

# ~/.bash_aliases
alias ll='ls -la'
alias update='sudo pacman -Syu'
```

---

## 6.10 Shell 配置文件加载顺序

理解配置文件何时被加载，对于管理环境变量和别名至关重要。

### 6.10.1 登录 Shell vs 非登录 Shell

| Shell 类型 | 触发场景 | 加载的文件（bash） |
|------------|----------|---------------------|
| **登录 Shell** | SSH 登录、`Ctrl+Alt+F1~F6`、`su -` | `~/.bash_profile` → `~/.bashrc` |
| **交互式非登录 Shell** | 打开新的终端模拟器窗口 | `~/.bashrc` |
| **非交互式 Shell** | 执行脚本（`bash script.sh`） | `$BASH_ENV`（如果有设置） |

```bash
# 典型配置策略：
# ~/.bash_profile （登录时加载，调用 .bashrc）
if [ -f ~/.bashrc ]; then
    . ~/.bashrc
fi

# ~/.bashrc （每次打开终端都加载）
# 在这里放置别名、环境变量、自定义函数
```

### 6.10.2 修改配置后生效

```bash
source ~/.bashrc       # 重新加载配置（无需重新登录）
. ~/.bashrc            # 同上，使用 . 命令
exec bash              # 用新的 bash 替换当前进程
```

---

## 6.11 命令链与重定向基础

虽然详细内容在 [[16-Bash编程基础]] 中展开，但以下基础概念需先了解：

### 6.11.1 命令连接符

| 符号 | 含义 | 示例 |
|------|------|------|
| `;` | 顺序执行（不管前一条是否成功） | `cmd1; cmd2` |
| `&&` | 前一条成功才执行下一条 | `mkdir dir && cd dir` |
| `\|\|` | 前一条失败才执行下一条 | `cmd1 \|\| echo "失败"` |
| `\|` | 管道——前一条的 stdout 传给下一条的 stdin | `ls \| grep txt` |

### 6.11.2 重定向基础

| 符号 | 含义 | 示例 |
|------|------|------|
| `>` | stdout 重定向到文件（覆盖） | `echo "hi" > file.txt` |
| `>>` | stdout 重定向到文件（追加） | `echo "hi" >> file.txt` |
| `2>` | stderr 重定向到文件 | `cmd 2> error.log` |
| `&>` | stdout 和 stderr 都重定向 | `cmd &> all.log` |
| `<` | 从文件读取 stdin | `wc -l < file.txt` |
| `/dev/null` | 丢弃输出 | `cmd > /dev/null 2>&1` |

---

## 6.12 实践练习

### 6.12.1 新手每日练习

```bash
# Day 1：基础导航
pwd && ls && cd / && ls && cd ~

# Day 2：理解命令结构
man ls && whatis ls && type ls

# Day 3：历史操作
history && ls && !! && !$

# Day 4：Tab 补全
# 尝试用 Tab 补全尽可能长的路径

# Day 5：快捷键
# 不用方向键，只用 Ctrl+A/E/B/F 移动光标
# 用 Ctrl+R 搜索历史

# Day 6：别名
alias && echo 'alias today="date"' >> ~/.bashrc && source ~/.bashrc

# Day 7：环境变量
env | sort && echo $PATH && which bash
```

### 6.12.2 探索式学习

```bash
# 遇到陌生命令，三步法学习：
# 1. 快速查看用途
whatis command_name

# 2. 查看常用示例
tldr command_name

# 3. 深入查看完整手册
man command_name
```

---

## 6.13 常见问题

| 问题 | 解决方案 |
|------|----------|
| 命令名输错了，提示 "command not found" | 检查拼写，用 `Ctrl+R` 搜索历史 |
| 改了 `.bashrc` 不生效 | `source ~/.bashrc` 重新加载 |
| 环境变量在子 Shell 中不见了 | 必须用 `export` 导出 |
| 别名在 `sudo` 中无效 | `sudo` 使用 root 的 Shell 配置；用 `sudo -E` 保留当前环境 |
| 终端显示乱码 | 检查 `echo $LANG`，设置为 `export LANG=zh_CN.UTF-8` |
| 清屏后想找回之前的输出 | 无法找回（Ctrl+L 只是视觉清屏） |

---

## 6.14 相关链接

- [[01-Linux概述与历史]] — 了解 Linux 的来龙去脉
- [[04-文件与目录管理]] — 用命令行管理文件
- [[05-文本编辑器(Vim+Nano)]] — 学习终端编辑器
- [[16-Bash编程基础]] — 深入 Shell 编程
- [[53-终端常用工具大全]] — 提升终端效率的工具集合
- [[03-FHS文件系统层次标准]] — 理解系统目录结构

> **学习建议**：每个 Linux 初学者都应该先读完这 6 个基础章节（01-06），建立完整的命令行世界观。之后的章节可以按需阅读，逐步深入特定领域。
