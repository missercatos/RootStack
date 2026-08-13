# Vim 编辑器教程

Vim 是终端下最强大的文本编辑器。对于 C/C++ 程序员来说，在 SSH 远程服务器上写代码、快速修改配置文件、或是在 QEMU 裸机环境里没有 GUI 的时候，Vim 是唯一的选择。本教程以 **Windows 用户使用 cmd 终端** 为主线，附带 Linux/macOS 安装说明，并提供完整的 Vim 使用手册：快捷键大全和 `:` 指令大全。

---

## 一、安装 Vim

### 1.1 Windows：下载并写入 PATH

**方法一：winget（推荐，Windows 10/11 自带）**

```powershell
# 以管理员身份打开 PowerShell 或 cmd
winget install vim.vim
```

安装后重启终端即可在 cmd/PowerShell 中使用 `vim`。

**方法二：官方安装包**

1. 前往 [vim.org](https://www.vim.org/download.php) 下载 "PC: MS-DOS and MS-Windows" 的安装包（gvim90.exe 或类似）
2. 运行安装程序，**务必勾选 "Create .bat files for command line use"**（这步自动写入 PATH）
3. 若忘记勾选，手动添加环境变量：
   ```cmd
   :: 以管理员身份打开 cmd，将 Vim 安装目录加入 PATH（以默认路径为例）
   setx PATH "%PATH%;C:\Program Files (x86)\Vim\vim91" /M
   ```

**方法三：Scoop / Chocolatey**

```powershell
scoop install vim          # Scoop 用户
choco install vim            # Chocolatey 用户
```

**验证安装**

```cmd
vim --version | findstr /C:"Vi IMproved"
```

#### 1.2 Linux

```bash
# Debian/Ubuntu
sudo apt install vim

# Arch Linux
sudo pacman -S vim

# Fedora
sudo dnf install vim
```

多数 Linux 发行版已预装 `vim` 或 `vi`（Vi 兼容版）。

#### 1.3 macOS

```bash
brew install vim
```

macOS 自带 `vim`，但版本较旧，Homebrew 可获取最新版。

---

## 二、3 分钟快速入门

### 2.1 打开 Vim

```cmd
vim                :: 空白编辑器
vim hello.c        :: 打开已有文件（不存在则新建）
vim +69 hello.c    :: 打开并跳到第 69 行
vim -R readme.md   :: 只读模式打开（view 命令等效）
```

### 2.2 编辑并保存

Vim 有多个 **模式（Mode）**，新手最大的困惑都源于此。你只需求记住 **3 个核心模式**：

| 模式 | 进入方式 | 用途 | 光标形状(典型) |
|------|---------|------|---------------|
| Normal（普通模式） | `Esc` | 浏览、复制、粘贴、删除 | 方块 |
| Insert（插入模式） | `i` / `a` / `o` | 输入文字 | 竖线 |
| Command-line（命令模式） | `:` | 保存、退出、搜索替换 | — |

**第一次使用 Vim 的新手三步走**：

```vim
vim test.txt          " 1. 打开
i                     " 2. 按 i 进入 Insert 模式 → 输入任意文字
<Esc>                 " 3. 按 Esc 回到 Normal 模式
:wq                   " 4. 输入 :wq 保存并退出
```

---

## 三、模式详解

### 3.1 Normal 模式（默认）

启动 Vim 后你就在 Normal 模式。所有移动、删除、复制、粘贴快捷键都从 Normal 模式发出。

### 3.2 Insert 模式（插入文字）

从 Normal 模式进入 Insert 模式：

| 快捷键 | 效果 |
|--------|------|
| `i` | 在光标前插入 |
| `a` | 在光标后插入（append） |
| `I` | 行首插入 |
| `A` | 行尾插入 |
| `o` | 在下方新开一行并插入 |
| `O` | 在上方新开一行并插入 |
| `s` | 删除光标处字符并插入 |
| `S` / `cc` | 删除整行并插入 |
| `cw` | 删除到词尾并插入（change word）|

`Esc` 或 `Ctrl+[` 回到 Normal 模式。

### 3.3 Visual 模式（选择文字）

| 快捷键 | 效果 |
|--------|------|
| `v` | 字符级选中 |
| `V` | 行级选中 |
| `Ctrl+v` | 块选中（列编辑）|

选中后可用 `y`(复制)、`d`(删除)、`>`(缩进)、`<`(反缩进)、`=`(自动格式化) 操作。

### 3.4 Command-line 模式（执行命令）

Normal 模式下按 `:` 进入。常用 `:` 指令见后文「指令大全」。

---

## 四、快捷键大全

### 4.1 光标移动

| 快捷键 | 效果 |
|--------|------|
| `h` / `j` / `k` / `l` | 左 / 下 / 上 / 右 |
| `w` | 下一个词的词首（word） |
| `b` | 上一个词的词首（back） |
| `e` | 当前词词尾 |
| `0` | 行首 |
| `^` | 本行第一个非空白字符 |
| `$` | 行尾 |
| `gg` | 文件开头 |
| `G` | 文件末尾 |
| `:N` 或 `NG` | 跳到第 N 行（如 `:42` = 跳到第 42 行） |
| `Ctrl+f` | 向下翻屏（Forward） |
| `Ctrl+b` | 向上翻屏（Backward） |
| `Ctrl+d` | 向下翻半屏 |
| `Ctrl+u` | 向上翻半屏 |
| `H` / `M` / `L` | 屏幕顶部/中部/底部（High/Middle/Low） |
| `%` | 跳转到匹配的括号（`( ) [ ] { }`） |
| `f{char}` | 光标后查找字符（find）|
| `F{char}` | 光标前查找字符 |
| `t{char}` | 光标后查找字符，停在字符前（till） |
| `;` / `,` | 重复/反向前一次的 f/t 查找 |

### 4.2 编辑操作

| 快捷键 | 效果 |
|--------|------|
| `x` | 删除光标处字符 |
| `X` | 删除光标左边字符（退格） |
| `dd` | 删除（剪切）整行 |
| `dw` | 删除到词尾 |
| `d$` / `D` | 删除到行尾 |
| `d0` | 删除到行首 |
| `dG` | 删除到文件末尾 |
| `dgg` | 删除到文件开头 |
| `yy` / `Y` | 复制整行（yank） |
| `yw` | 复制一个词 |
| `y$` | 复制到行尾 |
| `p` | 粘贴到光标后 |
| `P` | 粘贴到光标前 |
| `u` | 撤销 |
| `Ctrl+r` | 重做（redo） |
| `r{char}` | 替换光标处字符为 {char} |
| `R` | 进入替换模式（覆盖输入） |
| `~` | 切换光标处字符大小写 |
| `>>` | 右缩进 |
| `<<` | 左缩进 |
| `==` | 自动格式化当前行 |
| `gg=G` | 全文件自动格式化 |
| `J` | 合并下一行到当前行 |

### 4.3 搜索

| 快捷键 | 效果 |
|--------|------|
| `/pattern` | 向下搜索 |
| `?pattern` | 向上搜索 |
| `n` | 下一个匹配 |
| `N` | 上一个匹配 |
| `*` | 搜索当前光标下单词（向下） |
| `#` | 搜索当前光标下单词（向上） |

### 4.4 多文件与分屏

| 快捷键 | 效果 |
|--------|------|
| `:e filename` | 编辑新文件 |
| `:split` / `:sp` | 水平分屏 |
| `:vsplit` / `:vs` | 垂直分屏 |
| `Ctrl+w h/j/k/l` | 切换分屏窗口 |
| `Ctrl+w w` | 轮流切换窗口 |
| `Ctrl+w q` | 关闭当前窗口 |
| `Ctrl+w =` | 均分窗口大小 |
| `:bn` | 下一个 buffer |
| `:bp` | 上一个 buffer |
| `:bd` | 关闭当前 buffer |
| `:ls` | 列出所有 buffer |

### 4.5 寄存器与宏

| 快捷键 | 效果 |
|--------|------|
| `"{char}y` | 复制到指定寄存器 {char} |
| `"{char}p` | 从指定寄存器 {char} 粘贴 |
| `"*y` / `"+y` | 复制到系统剪贴板 |
| `"*p` / `"+p` | 从系统剪贴板粘贴 |
| `qa` ... `q` | 录制宏：开始(`qa`) → 操作 → 结束(`q`) |
| `@a` | 执行寄存器 a 中的宏 |
| `@@` | 重复上一次执行的宏 |
| `5@a` | 执行宏 5 次 |

### 4.6 文本对象（Text Objects）

| 快捷键 | 含义 |
|--------|------|
| `ciw` | 删除当前词并插入（change inner word） |
| `ci"` | 删除双引号内的内容并插入 |
| `ci(` / `ci)` | 删除括号内的内容并插入 |
| `diw` | 删除一个词 |
| `da"` | 删除双引号及内容（a = around） |
| `yi"` | 复制引号内的内容 |
| `vi{` | 选中花括号内的内容 |

> 规则：`{operator}{i/a}{text-object}` — i = inner, a = around

### 4.7 高级编辑

| 快捷键 | 效果 |
|--------|------|
| `.` | 重复上一次修改 |
| `Ctrl+a` | 数字 +1 |
| `Ctrl+x` | 数字 -1 |
| `g~w` | 切换词的大小写 |
| `guw` | 词转为小写 |
| `gUw` | 词转为大写 |
| `gq` | 段落格式化为固定宽度 |
| `za` | 折叠/展开（编程代码块） |

---

## 五、`:` 指令大全

### 5.1 文件操作

| 指令            | 效果                   |
| ------------- | -------------------- |
| `:w`          | 保存                   |
| `:w filename` | 另存为                  |
| `:q`          | 退出                   |
| `:q!`         | 强制退出（不保存）            |
| `:wq` 或 `:x`  | 保存并退出                |
| `:e filename` | 打开文件                 |
| `:e!`         | 重新加载当前文件（放弃修改）       |
| `:r filename` | 将文件内容插入当前光标位置        |
| `:r !command` | 将 Shell 命令输出插入当前光标位置 |

### 5.2 搜索替换

| 指令 | 效果 |
|------|------|
| `:%s/old/new/g` | 全文替换 |
| `:%s/old/new/gc` | 全文替换（每次确认） |
| `:10,20s/old/new/g` | 第 10-20 行范围内替换 |
| `:s/old/new/g` | 仅当前行替换 |
| `:vimgrep /pattern/ *.c` | 在多文件中搜索 |
| `:copen` | 打开搜索结果窗口 |

### 5.3 行号与显示

| 指令 | 效果 |
|------|------|
| `:set nu` | 显示行号 |
| `:set nonu` | 隐藏行号 |
| `:set rnu` | 相对行号（光标为 0，上下以距离标注） |
| `:set list` | 显示不可见字符（Tab = ^I，行尾 = $） |
| `:set wrap` / `:set nowrap` | 启用/禁用自动换行 |
| `:set hlsearch` | 搜索高亮 |
| `:noh` | 临时关闭搜索高亮 |
| `:set paste` | 粘贴模式（禁用自动缩进） |
| `:set mouse=a` | 启用鼠标支持 |

### 5.4 缩进与 Tab

| 指令 | 效果 |
|------|------|
| `:set tabstop=4` | Tab 显示宽度 |
| `:set shiftwidth=4` | 缩进宽度 |
| `:set expandtab` | Tab 转为空格 |
| `:set noexpandtab` | 保留 Tab 制表符 |
| `:retab` | 将现有 Tab/空格按当前设置转换 |
| `:set autoindent` | 自动缩进 |

### 5.5 窗口与 Tab 页

| 指令 | 效果 |
|------|------|
| `:split` / `:sp` | 水平分屏 |
| `:vsplit` / `:vs` | 垂直分屏 |
| `:tabnew` | 新建标签页 |
| `:tabclose` | 关闭当前标签页 |
| `:tabnext` / `:tabn` | 下一个标签页 |
| `:tabprev` / `:tabp` | 上一个标签页 |
| `:tabs` | 列出所有标签页 |

### 5.6 外部命令

| 指令 | 效果 |
|------|------|
| `:!command` | 执行外部命令（如 `:!gcc %` 编译当前文件） |
| `:!` | 重复上一次外部命令 |
| `:shell` | 打开子 Shell（`exit` 返回 Vim） |
| `:terminal` | 在 Vim 内打开终端（Neovim/Vim 8+） |

### 5.7 帮助

| 指令 | 效果 |
|------|------|
| `:help` | 打开帮助主页 |
| `:help :w` | 查看 `:w` 命令的帮助 |
| `:help i_<Esc>` | 查看 Insert 模式中 Esc 的帮助 |
| `:help usr_toc` | 用户手册目录 |

### 5.8 编程相关

| 指令 | 效果 |
|------|------|
| `:make` | 运行 make 并跳转到第一个错误 |
| `:cnext` / `:cn` | 下一个编译错误 |
| `:cprev` / `:cp` | 上一个编译错误 |
| `:!gcc % -o %< && ./%<` | 编译并运行当前 C 文件 |
| `:set syntax=c` | 设置语法高亮为 C |
| `:set filetype=c` | 设置文件类型 |
| `:!python3 %` | 运行当前 Python 文件 |

---

## 六、.vimrc 基础配置

在用户主目录创建 `.vimrc`（Windows 为 `%USERPROFILE%\_vimrc`，Linux/macOS 为 `~/.vimrc`）：

```vim
" 基础设置
set number              " 显示行号
set relativenumber      " 相对行号
set tabstop=4           " Tab 宽度
set shiftwidth=4        " 缩进宽度
set expandtab           " Tab 转空格
set autoindent          " 自动缩进
set hlsearch            " 搜索高亮
set incsearch           " 增量搜索
set ignorecase          " 搜索忽略大小写
set smartcase           " 包含大写时区分大小写
set mouse=a             " 启用鼠标
set clipboard=unnamed   " 系统剪贴板

" 高亮光标行
set cursorline

" 由文件类型决定缩进
filetype plugin indent on

" 快捷键：<Leader> 默认是 \
let mapleader = " "
nnoremap <Leader>w :w<CR>       " 空格+w 保存
nnoremap <Leader>q :q<CR>       " 空格+q 退出
nnoremap <Leader>so :so %<CR>   " 空格+so 重新加载配置文件
```

---

## 七、与 C/C++ 开发的配合

Linux 下使用 Vim 开发 C/C++ 的最简配置：

```bash
# 安装插件管理器 vim-plug
curl -fLo ~/.vim/autoload/plug.vim --create-dirs \
    https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
```

`.vimrc` 中添加：

```vim
call plug#begin()
Plug 'neoclide/coc.nvim', {'branch': 'release'}   " 代码补全（LSP）
Plug 'vim-airline/vim-airline'                     " 状态栏美化
Plug 'preservim/nerdtree'                          " 文件浏览器
Plug 'junegunn/fzf.vim'                            " 模糊搜索
call plug#end()

" 安装 coc-clangd（Vim 内执行）
" :CocInstall coc-clangd
```

编译运行快捷键：

```vim
" F5 编译并运行当前 C 文件
autocmd FileType c nnoremap <F5> :w<CR>:!gcc % -o %< -Wall -Wextra -g -std=c11 && ./%<<CR>
```

> 更多终端开发环境配置参考 [[../c语言教程/1入门/01_环境配置|C 教程环境配置]] 和 [[python/1入门/01_认识Python与python_-c_一行流|Python 快速入门]]。

---

## 八、速查卡

| 分类 | 快捷键 | 效果 |
|------|--------|------|
| 模式切换 | `i` / `Esc` / `:` | 插入 / 普通 / 命令模式 |
| 移动 | `h j k l` | 左 下 上 右 |
| 移动 | `w` / `b` | 词首 / 词尾 |
| 移动 | `0` / `$` / `^` | 行首 / 行尾 / 首个非空 |
| 移动 | `gg` / `G` / `:N` | 文件头 / 文件尾 / 第 N 行 |
| 删除 | `x` / `dd` | 删字符 / 删行 |
| 复制 | `yy` / `p` | 复制行 / 粘贴 |
| 撤销 | `u` / `Ctrl+r` | 撤销 / 重做 |
| 搜索 | `/word` / `n` / `N` | 搜索 / 下一匹配 / 上一匹配 |
| 保存退出 | `:w` / `:q` / `:wq` | 保存 / 退出 / 保存并退出 |
| 替换 | `:%s/old/new/g` | 全文替换 |
| 分屏 | `:sp` / `:vs` | 水平 / 垂直分屏 |
| 窗口切换 | `Ctrl+w h j k l` | 窗口间移动 |
| 宏 | `q a` ... `q` / `@a` | 录制宏 / 执行宏 |


## 九、现代 Vim 上位替代

Vim 在 Linux 开发中广受欢迎，熟练之后操作轻快流畅，但缺点是学习曲线陡峭、配置耗时（原生 Vim 对标现代 IDE 需要自己拼装补全、语法高亮、文件树）。以下按"从易到难"给出替代方案。

### 1. IDE 内置 Vim 模式

主流 IDE 与编辑器都提供了 Vim 键位模拟插件，装上之后编辑习惯无缝迁移，同时保留 IDE 的补全、调试、重构能力：

| 宿主 | 插件 | 说明 |
|------|------|------|
| VS Code | Vim（`vscodevim.vim`） | 最接近原生 Vim 的模拟，社区最活跃 |
| IntelliJ / PyCharm / CLion | IdeaVim | JetBrains 官方支持，完美融合 IDE 快捷键 |
| Visual Studio | VsVim | 微软官方维护 |
| Chrome / Edge 浏览器 | Vimium | 浏览器内用 hjkl 操作网页（同思路） |
| Excel / 其他 | 不宜强上 | 键位冲突大于收益 |

装上插件即可获得原生 Vim 约九成的操作体验（hjkl 移动、dd/yy、宏、寄存器都可用），且**零配置**——这是最推荐的入门路径。

### 2. Neovim（nvim）

Neovim 脱胎于 Vim，解决了 Vim 二十多年积累的设计包袱：

| 优势 | 说明 |
|------|------|
| 异步架构 | 插件不再卡死界面，LSP 补全流畅 |
| Lua 配置 | 用 Lua 代替 vimscript 写配置，现代且可控 |
| 内置 LSP 客户端 | 原生支持补全、跳转、诊断（对标 IDE 核心功能） |
| 内置终端 | `:terminal` 在编辑器内开终端 |
| 社区生态 | Telescope、Treesitter、NvimTree 等已成事实标准 |

3.1 一键配置：LazyVim

原生 Neovim 仍然要自己配，但社区已经给出"装上就用"的整合包。**LazyVim** 是目前最流行的 Neovim 一键配置发行版：

- 基于 lazy.nvim 插件管理器，插件按需加载
- 开箱即用：文件树、模糊搜索、LSP 补全、Git 集成、主题
- 覆盖 Python / C/C++ / Go / Rust / 前端等主流语言
- 安装后基本不需要额外配置，快捷键以 `<leader>` 前缀组织、高度可查

3.2 作者的 ARKVim 项目

作者自身就是 LazyVim 重度用户，并基于它做了针对性定制，开源项目 **ARKVim**：

| 特性 | 说明 |
|------|------|
| 项目地址 | <https://github.com/missercatos/ARKVim> |
| 基础 | 脱胎于 LazyVim，保留其稳定插件体系 |
| 快捷编译运行 | 一键编译运行当前文件（针对 C / C++ 优化） |
| 快捷键扩展 | 追加大量高频操作快捷键，减少按键次数 |
| 多语言支持 | Python、C/C++、Java、Go、Rust、Lua、Ruby、HTML、CSS、JS 全系列插件 |
| 个性化 | 作者日常使用的主题、键位、优化调参 |

> 如果你打算长期用 Neovim，建议直接 clone 作者的配置体验一下，再按需增删：`git clone <项目地址> ~/.config/nvim`，然后打开 nvim 等待插件安装完成即可。

### 3. 其他现代替代

| 工具 | 特点 | 适合谁 |
|------|------|--------|
| Zed | Rust 写的高性能编辑器，内置 AI 与协作 | 追求速度与现代化的开发者 |
| Helix | 内置 LSP、免配置、模式编辑（与 Vim 略异） | 想换新手感的人 |
| Emacs（evil-mode） | Vim 键位 + Emacs 生态，可配置性天花板 | 愿意花时间深度定制的用户 |
| Sublime Text | 轻量、启动快，Vintage 模式模拟 Vim | 轻量编辑 + 一点 Vim 键位 |

### 4. 选择建议

| 你的情况 | 推荐 |
|----------|------|
| 刚接触 Vim，只想在 VS Code 里体验 | VS Code + Vim 插件 |
| 日常主力是 JetBrains IDE | IdeaVim |
| 想深入终端编辑器，愿意折腾配置 | Neovim + LazyVim（或直接 ARKVim） |
| 重度自定义、千层饼配置 | Emacs + evil-mode / 自研 nvim 配置 |
| 佛系，够用就好 | 原生 Vim 已足够，无需迁移 |