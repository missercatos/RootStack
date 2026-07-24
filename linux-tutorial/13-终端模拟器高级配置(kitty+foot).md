# 13 - 终端模拟器高级配置

> Kitty (GPU 加速) 和 Foot (极简 Wayland 原生) —— 两种顶级终端的深度玩法。

---

## 13.1 Kitty 配置

### 安装

```bash
sudo pacman -S kitty
# 或带完整功能
sudo pacman -S kitty kitty-shell-integration kitty-terminfo
```

### 配置位置

```bash
~/.config/kitty/kitty.conf          # 主配置
~/.config/kitty/current-theme.conf  # 可选的颜色方案
```

### 完整配置文件

```conf
# ===== 字体 =====
font_family      JetBrainsMono Nerd Font Mono
bold_font         auto
italic_font       auto
bold_italic_font  auto
font_size         11.0

# 调整行高
adjust_line_height -1
adjust_column_width 0

# disable_ligatures never  # 如果字体连字有问题

# ===== 光标 =====
cursor_shape      block          # block | beam | underline
cursor_blink_interval 0.5       # 0 = 不闪
cursor_stop_blinking_after 15.0  # 15秒后停止闪烁

# ===== 滚动 =====
scrollback_lines  10000
scrollback_pager  less -R
wheel_scroll_multiplier 5.0

# ===== 窗口 =====
# 启动时窗口大小
initial_window_width  900
initial_window_height 550

# 与屏幕边距
window_margin_width   8

# 内边距
window_padding_width  12

# 最大化时移除内边距
hide_window_decorations titlebar-only

# 不透明度
background_opacity    0.85

# 动态背景不透明度（焦点/失焦）
# dynamic_background_opacity yes

# ===== Tab Bar =====
tab_bar_style         powerline        # fade | powerline | hidden
tab_bar_edge          bottom
tab_bar_margin_width  0.0
tab_bar_min_tabs      1
tab_title_template    "{index}: {title}"

# active_tab_foreground   #fff
# active_tab_background   #4c566a

# ===== Shell 集成 =====
shell_integration    enabled
# 启用后可以在远程 SSH 中也用 kitty 协议

# ===== URL 检测 =====
detect_urls          yes
url_prefixes         http https file ftp gemini
open_url_with        default

# ===== 鼠标 =====
mouse_hide_wait      3.0
url_color            #87cefa
url_style            curly

# copy/paste
copy_on_select       yes
strip_trailing_spaces smart

# ===== 快捷键 =====
# 查看所有默认快捷键：
# kitty +kitten show_key_mappings

# 自定义快捷键
map ctrl+shift+c copy_to_clipboard
map ctrl+shift+v paste_from_clipboard
map ctrl+shift+n new_os_window
map ctrl+shift+t new_tab
map ctrl+shift+w close_tab
map ctrl+shift+left  previous_tab
map ctrl+shift+right next_tab
map ctrl+shift+up    move_tab_backward
map ctrl+shift+down  move_tab_forward

# Vim 风格分屏
map ctrl+shift+[ previous_window
map ctrl+shift+] next_window

# 字体缩放
map ctrl+plus  change_font_size all +0.5
map ctrl+minus change_font_size all -0.5
map ctrl+0     change_font_size all 0

# ===== 高级：远程控制 =====
# Kitty 有强大的远程控制协议

# 允许远程控制
allow_remote_control yes

# 监听 socket（本地控制用）
listen_on unix:/tmp/kitty-$$-{pid}

# ===== 高级：会话 =====
# ~/.config/kitty/kitty-startup.conf
# 或命令行启动：
# kitty --session ~/.config/kitty/session.conf
```

---

## 13.2 Kitty 会话文件

```bash
# ~/.config/kitty/session.conf
# 每次启动恢复窗口布局

new_tab Main
layout splits
cd ~/projects
launch zsh

new_tab Monitor
layout splits
launch zsh -c "btm"
launch zsh -c "journalctl -f"

new_tab Music
launch zsh -c "ncmpcpp"

# 自动设置焦点
focus Main
```

---

## 13.3 Kitty 颜色方案

```bash
# 包含几百种主题
kitty +kitten themes

# 选择并保存
kitty +kitten themes --reload-in=parent Catppuccin-Mocha

# 输出到文件
kitty +kitten themes --dump-theme Catppuccin-Mocha > ~/.config/kitty/theme.conf
```

### 手动定义颜色

```conf
# ~/.config/kitty/kitty.conf
foreground #CDD6F4
background #1E1E2E

# 黑色组
color0  #45475A
color8  #585B70

# 红色组
color1  #F38BA8
color9  #F38BA8

# 绿色组
color2  #A6E3A1
color10 #A6E3A1

# 黄色组
color3  #F9E2AF
color11 #F9E2AF

# 蓝色组
color4  #89B4FA
color12 #89B4FA

# 品红组
color5  #F5C2E7
color13 #F5C2E7

# 青色组
color6  #94E2D5
color14 #94E2D5

# 白色组
color7  #BAC2DE
color15 #A6ADC8

# 光标颜色
cursor            #F5E0DC
cursor_text_color #1E1E2E

# 选择颜色
selection_foreground #1E1E2E
selection_background #F5E0DC
```

---

## 13.4 Kitty Kittens（内置工具）

```bash
# kitten = Kitty 内置的脚本/工具

# Diff（终端中对比两个文件，支持图片 diff）
kitty +kitten diff file1.txt file2.txt

# SSH（自动复制 terminfo 和 shell 集成到远程）
kitty +kitten ssh user@host

# 文件传输（类似 scp，但支持进度条和断点续传）
kitty +kitten transfer upload file.txt user@host:/path/

# Unicode 输入
kitty +kitten unicode_input

# 提示（自定义弹窗菜单，用于脚本）
kitty +kitten hints          # 选择屏幕上的 URL/文本/路径

# 面板（tiling window manager 功能）
kitty +kitten panel

# 图标选择器（emoji）
kitty +kitten emoji_picker

# 查询终端信息
kitty +kitten query_terminal

# 调试
kitty +kitten show_key_mappings
kitty +kitten debug_config
```

---

## 13.5 Kitty 图形协议

```bash
# Kitty 有自己的图形协议（比 sixel 快）
# 直接在终端中显示图片

# 显示图片
kitty +kitten icat image.png

# 设置终端背景为图片
kitty +kitten icat --place --scale-up /path/to/wallpaper.jpg

# 在终端中预览图片目录
kitty +kitten icat --print-window-size
```

---

## 13.6 Kitty 自定义 Kitten 开发

```python
#!/usr/bin/env python3
# ~/.config/kitty/my_kitten.py
"""
自定义 Kitten 示例
Kitty 通过 stdin/stdout 与控制终端通信
"""

from kittens.tui.handler import result_handler
from kitty.boss import Boss

def main(args):
    # 从 stdin 读取数据（如果是 pipe 进来的）
    import sys
    data = sys.stdin.buffer.read()
    return data

@result_handler(no_ui=True)
def handle_result(args, data, target_window_id, boss: Boss):
    if target_window_id is not None:
        w = boss.window_id_map.get(target_window_id)
        if w is not None:
            # 在目标窗口中显示结果
            # boss.call_remote_control(w, 'send-text', f'--match=id:{w.id}', 'echo Done')
            pass
```

---

## 13.7 Foot 配置

> Foot — 最快的 Wayland 原生终端模拟器。使用 `foot.ini` 配置。

### 安装

```bash
sudo pacman -S foot
# 或带主题的 foot-terminfo
```

### 配置文件位置

```bash
~/.config/foot/foot.ini            # 主配置
~/.config/foot/colors.ini          # 颜色单独文件
# 或全部放 foot.ini 中

# 默认配置参考
# /usr/share/foot/foot.ini
```

### 完整 foot.ini

```ini
# ===== 主配置 =====
[main]

# 字体
font=JetBrainsMono Nerd Font:size=11
# 斜体/粗体系
font-bold=JetBrainsMono Nerd Font:size=11:weight=bold
font-italic=JetBrainsMono Nerd Font:size=11:slant=italic

# 行高/字间距调整
line-height=16
letter-spacing=0

# DPI 感知
dpi-aware=yes

# 内边距
pad=12x12 center

# 初始窗口大小（字符数）
initial-window-size-chars=100x30
initial-window-size-pixels=800x600

# 窗口标题
title=foot

# 锁行（固定行数，不可超出）
# locked-title=no

# ===== 滚动 =====
[scrollback]
lines=10000
# 滚动乘数
multiplier=3

# 滚动指示器（屏幕右上角小点）
indicator-position=relative
indicator-format=percentage    # percentage | fraction | line

# ===== 光标 =====
[cursor]
style=block            # block | beam | underline
blink=yes
beam-thickness=1.5

# 光标颜色
color=1E1E2E F5E0DC   # 前景 背景
# 闪烁速率 (ms)
blink-rate=500

# ===== 鼠标 =====
[mouse]
hide-when-typing=yes
alternate-scroll-mode=yes

# ===== 触摸 =====
[touch]
long-press-delay=400

# ===== 颜色 =====
[colors]
# 前景/背景
foreground=CDD6F4
background=1E1E2E

# 光标
cursors=1E1E2E      # 文字
cursor=1E1E2E       # 文字
cursor=text F5E0DC  # 光标块

# 选择
selection-foreground=1E1E2E
selection-background=F5E0DC

# ANSI 颜色
regular0=45475A   # 黑色
regular1=F38BA8   # 红色
regular2=A6E3A1   # 绿色
regular3=F9E2AF   # 黄色
regular4=89B4FA   # 蓝色
regular5=F5C2E7   # 品红
regular6=94E2D5   # 青色
regular7=BAC2DE   # 白色

bright0=585B70
bright1=F38BA8
bright2=A6E3A1
bright3=F9E2AF
bright4=89B4FA
bright5=F5C2E7
bright6=94E2D5
bright7=A6ADC8

# 256 色调色板
[colors]
0=1E1E2E
1=F38BA8
# ... 可以继续定义到 255

# ===== 快捷键 =====
[key-bindings]
# 语法：action=keycombo

# 剪贴板
clipboard-copy=Control+Shift+c XF86Copy
clipboard-paste=Control+Shift+v XF86Paste

# 搜索
search-start=Control+Shift+r

# 字体缩放
font-increase=Control+plus Control+equal Control+KP_Add
font-decrease=Control+minus Control+KP_Subtract
font-reset=Control+0 Control+KP_0

# 滚动
scrollback-up-page=Shift+Page_Up
scrollback-down-page=Shift+Page_Down

# 复制到剪贴板 + 保留选区
# primary-paste=Shift+Insert

# URL 模式
show-urls-launch=Control+Shift+u
show-urls-copy=Control+Shift+i

# 打开新窗口
spawn-terminal=Control+Shift+n

# ===== URL 处理 =====
[url]
# 检测 URL
launch=xdg-open ${url}

# URL 协议
protocols=http, https, ftp, ftps, file, gemini, gopher
# 字符集
# osc8-close=]

# 标签/标记（高亮显示）
label-letters=sadfjklewcmpgh

# ===== 服务器模式 =====
[server]
# Foot 可以用服务器模式节省内存
# 一个 foot 进程管理多个窗口
# 启动方式：
#   foot -s         # 启动服务器
#   footclient      # 连接服务器建新窗口
#   foot --server   # 同上
```

---

## 13.8 Foot 服务器模式

```bash
# 1. 启动服务器（登录时自动启动）
foot --server &

# 2. 使用客户端创建窗口（比新进程快得多）
footclient                    # 新窗口
footclient -H                 # 新窗口在当前目录
footclient --title="Htop" htop  # 运行指定命令

# 3. 在 Sway/Hyprland/Niri 绑定键
# 推荐绑 footclient 而不是 foot
bindsym $mod+Return exec footclient
```

---

## 13.9 Kitty vs Foot 对比

| | Kitty | Foot |
|------|-------|------|
| 渲染 | GPU (OpenGL) | GPU (OpenGL) |
| 协议 | xdg-shell | xdg-shell |
| 服务器模式 | --single-instance | --server + footclient |
| 图形/图片 | 自定义图形协议 | sixel (可选) |
| Tabs/分屏 | 内置 | 依赖 tmux/窗口管理器 |
| 远程控制 | 丰富的 RC 协议 | 通过 pipe/socket |
| 速度 | 非常快 | 更快 |
| 内存 | 较高 | 极低 |
| 字体连字 | 支持 | 不支持（设计原则） |
| 用键盘选文本 | Kitten hints | URL 模式 |
| 配置文件 | kitty.conf (键值对) | foot.ini (INI风格) |
| 主题 | kitten themes | 手动/工具导入 |
```

---

## 13.10 高级：终端键盘协议

```bash
# Kitty Keyboard Protocol — 终端可以区分更多按键组合

# 在终端应用中启用（如 neovim/helix）
# Kitty:
# 默认已启用，可以检测 Ctrl+Shift+Enter、Ctrl+I vs Tab 等

# Foot:
# 同样支持，不需额外配置

# 验证终端是否支持：
printf '\e[?u'
# 如果返回 CSI ? 1 u，表示已进入增强模式

# 传统终端只能区分 33 种组合键
# 新协议可以区分所有修饰键组合
```

---

## 13.11 终端色彩管道

```bash
# 管道生成器，任意应用输出 24位真彩色
# 利用终端能力做高级显示

# 示例：用 chafa 在终端显示图片（支持 kitty/kitty + sixel/foot）
chafa --format symbols image.jpg
chafa --symbols block image.png    # 方块风格
chafa --colors 256 image.png       # 256色
chafa --size 80x40 image.png       # 指定尺寸
```

---

## 13.12 本章测验

> [!example] 📝 自测题目

> [!question]- 选择题 1：Kitty 终端使用什么技术进行渲染？
> - A. CPU 软件渲染
> - B. Vulkan
> - C. GPU (OpenGL)
> - D. DirectX
>
> > [!success]- 点击查看答案
> > **C**
> > Kitty 使用 GPU 加速渲染（OpenGL），这是它性能优秀的主要原因之一。

> [!question]- 选择题 2：Foot 终端的服务器模式有什么优势？
> - A. 支持远程连接
> - B. 多个窗口共享一个进程，节省内存且创建窗口更快
> - C. 可以跨机器同步终端状态
> - D. 提供 Web 界面访问
>
> > [!success]- 点击查看答案
> > **B**
> > Foot 的服务器模式（foot --server + footclient）让多个窗口共享一个进程，大幅节省内存，创建新窗口比新进程快得多。

> [!question]- 判断题 3：Foot 终端支持字体连字（ligatures）功能
> - A. ✓ 正确
> - B. ✗ 错误
>
> > [!success]- 点击查看答案
> > **B. ✗ 错误**
> > Foot 不支持字体连字，这是其设计原则之一（追求极简和性能）。Kitty 支持字体连字。

> [!question]- 选择题 4：Kitty 中查看/选择主题的命令是什么？
> - A. kitty --themes
> - B. kitty +kitten themes
> - C. kitty colorscheme list
> - D. kitty config --theme
>
> > [!success]- 点击查看答案
> > **B**
> > 使用 `kitty +kitten themes` 可以浏览和选择数百种内置主题，并实时预览。

> [!question]- 选择题 5：Kitty 中允许远程控制需要在配置中设置什么？
> - A. remote_control = true
> - B. allow_remote_control yes
> - C. enable_rc = on
> - D. ipc_mode = enabled
>
> > [!success]- 点击查看答案
> > **B**
> > 在 kitty.conf 中设置 `allow_remote_control yes` 即可启用 Kitty 强大的远程控制协议。

> [!question]- 判断题 6：Kitty Keyboard Protocol 可以让终端区分 Ctrl+I 和 Tab 键
> - A. ✓ 正确
> - B. ✗ 错误
>
> > [!success]- 点击查看答案
> > **A. ✓ 正确**
> > 传统终端只能区分约 33 种组合键，Kitty Keyboard Protocol 可以区分所有修饰键组合，包括 Ctrl+I vs Tab、Ctrl+Shift+Enter 等。

> [!question]- 选择题 7：Foot 配置文件使用什么格式？
> - A. TOML
> - B. YAML
> - C. INI
> - D. 键值对（类似 kitty.conf）
>
> > [!success]- 点击查看答案
> > **C**
> > Foot 使用 INI 风格的配置文件（foot.ini），用 [section] 分隔不同配置区域。

> [!question]- 选择题 8：Kitty 中在终端直接显示图片的命令是什么？
> - A. kitty show image.png
> - B. kitty +kitten icat image.png
> - C. kitty display image.png
> - D. kitty --image image.png
>
> > [!success]- 点击查看答案
> > **B**
> > 使用 `kitty +kitten icat image.png` 可以利用 Kitty 自有的图形协议在终端中直接显示图片。

> [!question]- 判断题 9：Kitty 和 Foot 都支持 Kitty Keyboard Protocol
> - A. ✓ 正确
> - B. ✗ 错误
>
> > [!success]- 点击查看答案
> > **A. ✓ 正确**
> > Kitty 和 Foot 都支持 Kitty Keyboard Protocol（终端键盘协议），不需要额外配置即可在支持的应用（如 neovim/helix）中使用。

> [!question]- 选择题 10：Kitty 的 tab_bar_style 设置为 powerline 时效果是？
> - A. 隐藏标签栏
> - B. 标签栏使用 Powerline 风格箭头分隔符
> - C. 标签之间使用淡入淡出过渡
> - D. 标签栏固定在顶部
>
> > [!success]- 点击查看答案
> > **B**
> > tab_bar_style = powerline 使标签栏使用类似 Powerline 的箭头形状分隔符。其他选项有 fade（淡入淡出）和 hidden（隐藏）。
