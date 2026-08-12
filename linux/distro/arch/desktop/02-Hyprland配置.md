# 11 - Hyprland 配置详解

> [Hyprland](https://hyprland.org/) — C++ 写的动态平铺 Wayland 合成器，动画极强，可定制性最高。

---

## 11.1 安装

```bash
sudo pacman -S hyprland
# 或带工具链
sudo pacman -S hyprland hyprpaper hyprlock hypridle hyprpicker xdg-desktop-portal-hyprland
```

---

## 11.2 配置文件结构

```bash
~/.config/hypr/hyprland.conf # 主配置（可 include 其他文件）

# 常用拆分方式
~/.config/hypr/hyprland.conf → source = ~/.config/hypr/binds.conf
 source = ~/.config/hypr/rules.conf
 source = ~/.config/hypr/decorations.conf

# 变量定义在所有 include 之前
```

---

## 11.3 核心变量系统

```conf
# ===== 变量定义 =====
$mainMod = SUPER # Super = Win 键
$term = kitty
$fileManager = thunar
$menu = fuzzel # 或 rofi / wofi / anyrun
$browser = firefox

# 颜色变量
$rosewater = rgb(f5e0dc)
$flamingo = rgb(f2cdcd)
$mauve = rgb(DDB6F2)
$pink = rgb(F5C2E7)
$maroon = rgb(E8A2AF)
$red = rgb(F28FAD)
$peach = rgb(F8BD96)
$yellow = rgb(FAE3B0)
$green = rgb(ABE9B3)
$teal = rgb(B5E8E0)
$blue = rgb(96CDFB)
$sky = rgb(89DCEB)
$base = rgb(1E1E2E)
$mantle = rgb(181825)
$crust = rgb(11111B)
$text = rgb(CDD6F4)
$subtext0 = rgb(A6ADC8)
$surface0 = rgb(313244)

# 尺寸变量
$gapSize = 8
$borderSize = 2
$rounding = 12
```

---

## 11.4 显示器配置

```conf
# ===== 显示器 =====
monitor=eDP-1,1920x1080@144,0x0,1.5
# 分辨率@刷新率 位置 缩放

# 多显示器
monitor=DP-1,2560x1440@165,1920x0,1
monitor=eDP-1,1920x1080@60,0x0,1

# 禁用内置屏幕
# monitor=eDP-1,disable

# VRR (可变刷新率)
monitor=DP-1,2560x1440@165,0x0,1,bitdepth,10,vrr,2
# vrr: 0=关闭 1=始终 2=仅全屏

# 工作区分配到显示器
workspace=1,monitor:eDP-1
workspace=2,monitor:eDP-1
workspace=3,monitor:DP-1
workspace=4,monitor:DP-1
workspace=5,monitor:eDP-1
workspace=6,monitor:DP-1

# ===== 环境变量 =====
env = XCURSOR_SIZE,24
env = XCURSOR_THEME,Bibata-Modern-Classic
env = LIBVA_DRIVER_NAME,nvidia # 如果用 NVIDIA
env = GBM_BACKEND,nvidia-drm
env = __GLX_VENDOR_LIBRARY_NAME,nvidia
env = WLR_NO_HARDWARE_CURSORS,1
env = QT_QPA_PLATFORM,wayland
env = SDL_VIDEODRIVER,wayland
```

---

## 11.5 输入配置

```conf
# ===== 键盘 =====
input {
 kb_layout = us,ru
 kb_variant =
 kb_model =
 kb_options = grp:alt_shift_toggle,caps:escape
 kb_rules =

 repeat_rate = 40 # 字符重复率
 repeat_delay = 250 # 重复前延迟(ms)

 numlock_by_default = false

 # 单独给特定键盘设布局
 kb_file = /path/to/xkb # 自定义 XKB 文件
}

# 多键盘区分
device:epic-mouse-v1 {
 sensitivity = -0.5
}
device:royal-kludge-rk61 {
 repeat_rate = 30
}

# ===== 鼠标/触摸板 =====
input {
 follow_mouse = 1 # 焦点跟随鼠标 (0/1)

 touchpad {
 natural_scroll = yes
 tap-to-click = yes
 drag_lock = yes
 disable_while_typing = yes
 }

 sensitivity = 0 # -1.0 ~ 1.0
 accel_profile = flat # adaptive, flat
}

# 手势
gestures {
 workspace_swipe = true
 workspace_swipe_fingers = 3
 workspace_swipe_distance = 400
 workspace_swipe_cancel_ratio = 0.2
 workspace_swipe_create_new = true
 workspace_swipe_min_speed_to_force = 30
}
```

---

## 11.6 通用设置

```conf
general {
 gaps_in = $gapSize # 窗口内间距
 gaps_out = 12 # 窗口外间距
 border_size = $borderSize
 col.active_border = $mauve $pink 45deg # 渐变色！
 col.inactive_border = $surface0

 cursor_inactive_timeout = 3 # 秒，隐藏光标

 layout = dwindle # dwindle | master

 # 多列时不自动调整分割方向
 no_cursor_warps = false

 # 工作区数量（静默创建）
 # allow_workspace_count = 10
}
```

---

## 11.7 装饰

```conf
decoration {
 rounding = $rounding

 # Blur
 blur {
 enabled = true
 size = 4
 passes = 2 # 渲染次数（性能换质量）
 noise = 0.01 # 噪点纹理（减少伪影）
 contrast = 1.3
 brightness = 0.9
 new_optimizations = on # 性能优化
 xray = false # 透窗 debug
 }

 # 阴影
 drop_shadow = yes
 shadow_range = 15
 shadow_render_power = 2
 shadow_offset = 3 3
 col.shadow = rgba(1a1a1aee)
 col.shadow_inactive = rgba(1a1a1a88)

 # 窗口调暗（非焦点窗口）
 dim_inactive = false
 dim_strength = 0.1

 # 圆角 Shader（高级）
 # screen_shader = ~/.config/hypr/shaders/rounded.glsl
}
```

---

## 11.8 动画

```conf
# Hyprland 动画极其强大——使用 Bezier 曲线和弹簧物理

animations {
 enabled = yes

 # ===== 贝塞尔曲线 =====
 # 语法：bezier = 名字,x1,y1,x2,y2
 bezier = wind, 0.05, 0.9, 0.1, 1.05
 bezier = winIn, 0.1, 1.1, 0.1, 1.1
 bezier = winOut, 0.3, -0.3, 0, 1
 bezier = linear, 0, 0, 1, 1
 bezier = popin, 0.1, 1.1, 0.1, 1.0
 bezier = overshot, 0.05, 0.9, 0.1, 1.1

 # ===== 窗口动画 =====
 animation = windows, 1, 4, wind, popin 70%
 # 样式 时间 曲线

 # 打开窗口
 animation = windowsIn, 1, 4, winIn, slide

 # 关闭窗口
 animation = windowsOut, 1, 3, winOut, popin 80%

 # 窗口移动
 animation = windowsMove, 1, 3, wind, slide

 # ===== 淡入淡出 =====
 animation = fadeIn, 1, 3, default
 animation = fadeOut, 1, 3, default
 animation = fadeSwitch, 1, 2, default
 animation = fadeShadow, 1, 3, default
 animation = fadeDim, 1, 3, default

 # ===== 工作区切换 =====
 animation = workspaces, 1, 4, wind, slidevert
 # slidevert = 上下滑动
 # slide = 左右滑动（dwindle 默认）

 # ===== 特殊工作区（scratchpad 等）=====
 animation = specialWorkspace, 1, 4, overshot, slidevert
}
```

### 动画样式全表

| 动画样式 | 效果 |
|----------|------|
| `default` | 仅透明度/大小（无滑动） |
| `popin` | 从中心弹出 |
| `popin 80%` | 弹出到 80% 后弹回 100% |
| `slide` | 从屏幕边滑入 |
| `slidevert` | 垂直滑入 |
| `slidefade` | 滑入+淡入 |
| `slidefadevert` | 竖滑+淡入 |

---

## 11.9 绑定键

```conf
# ===== 绑定键 =====
bind = $mainMod, RETURN, exec, $term
bind = $mainMod, Q, killactive,
bind = $mainMod, F, fullscreen, 0 # 0=非最大化, 1=最大化, 2=全屏
bind = $mainMod SHIFT, F, fullscreen, 1
bind = $mainMod, V, togglefloating,
bind = $mainMod, P, pseudo, # pseudo tiling (dwindle)
bind = $mainMod SHIFT, Space, togglesplit, # 切换分割方向

# ===== 启动器 =====
bind = $mainMod, D, exec, $menu
bind = $mainMod, Space, exec, anyrun
bind = $mainMod, B, exec, $browser

# ===== 焦点切换 =====
bind = $mainMod, H, movefocus, l
bind = $mainMod, L, movefocus, r
bind = $mainMod, K, movefocus, u
bind = $mainMod, J, movefocus, d

# ===== 移动窗口 =====
bind = $mainMod SHIFT, H, movewindow, l
bind = $mainMod SHIFT, L, movewindow, r
bind = $mainMod SHIFT, K, movewindow, u
bind = $mainMod SHIFT, J, movewindow, d

# ===== 调整窗口大小(用鼠标拖动) =====
# 按住 mod + 右键拖动
bindm = $mainMod, mouse:272, movewindow
bindm = $mainMod, mouse:273, resizewindow

# ===== 调整分割比例 =====
bind = $mainMod, right, resizeactive, 50 0
bind = $mainMod, left, resizeactive, -50 0
bind = $mainMod, up, resizeactive, 0 -50
bind = $mainMod, down, resizeactive, 0 50

# ===== 工作区 =====
bind = $mainMod, 1, workspace, 1
bind = $mainMod, 2, workspace, 2
bind = $mainMod, 3, workspace, 3
bind = $mainMod, 4, workspace, 4
bind = $mainMod, 5, workspace, 5
bind = $mainMod, 6, workspace, 6
bind = $mainMod, 7, workspace, 7
bind = $mainMod, 8, workspace, 8
bind = $mainMod, 9, workspace, 9
bind = $mainMod, 0, workspace, 10

# 移动活动窗口到工作区（并跟随）
bind = $mainMod SHIFT, 1, movetoworkspacesilent, 1
bind = $mainMod SHIFT, 2, movetoworkspacesilent, 2
# ...etc

# 工作区导航（循环滚动）
bind = $mainMod, bracketleft, workspace, e-1
bind = $mainMod, bracketright, workspace, e+1
bind = $mainMod SHIFT, bracketleft, movetoworkspace, e-1
bind = $mainMod SHIFT, bracketright, movetoworkspace, e+1

# 前后工作区（全局历史）
bind = $mainMod, TAB, workspace, previous

# ===== 特殊工作区(Scratchpad) =====
bind = $mainMod, S, togglespecialworkspace, magic
bind = $mainMod SHIFT, S, movetoworkspace, special:magic

# ===== 鼠标工作区 =====
bind = $mainMod ALT, H, movecurrentworkspacetomonitor, l
bind = $mainMod ALT, L, movecurrentworkspacetomonitor, r

# ===== 截图 =====
bind = , Print, exec, grimblast copy area
bind = SHIFT, Print, exec, grimblast copy active
bind = $mainMod, Print, exec, grimblast copy output
bind = $mainMod SHIFT, Print, exec, grimblast save area

# ===== 系统 =====
bind = $mainMod SHIFT, E, exit,
bind = $mainMod SHIFT, C, exec, systemctl poweroff
bind = $mainMod SHIFT, R, exec, systemctl reboot
bind = $mainMod, L, exec, hyprlock

# ===== 多媒体 =====
bind = , XF86AudioRaiseVolume, exec, wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%+
bind = , XF86AudioLowerVolume, exec, wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-
bind = , XF86AudioMute, exec, wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle
bind = , XF86AudioMicMute, exec, wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle
bind = , XF86MonBrightnessUp, exec, brightnessctl set 5%+
bind = , XF86MonBrightnessDown, exec, brightnessctl set 5%-

# ===== 子映射(Submap) - 多键组合 =====
# 按下 Mod+R 进入 resize 模式，按方向键完成操作后退出
bind = $mainMod, R, submap, resize
submap = resize
bind = , right, resizeactive, 30 0
bind = , left, resizeactive, -30 0
bind = , up, resizeactive, 0 -30
bind = , down, resizeactive, 0 30
bind = , right, submap, resize # 继续留在此模式
bind = , escape, submap, reset # 退出 submap
bind = , return, submap, reset
submap = reset
```

---

## 11.10 窗口规则

```conf
# ===== 窗口规则 =====
windowrulev2 = tile, class:^(.*)$ # 默认所有平铺

# 浮动窗口
windowrulev2 = float, class:^(pavucontrol)$
windowrulev2 = float, class:^(org.pwmt.zathura)$
windowrulev2 = float, class:^(mpv)$
windowrulev2 = float, class:^(blueberry.py)$
windowrulev2 = float, title:^(Picture-in-Picture)$
windowrulev2 = float, title:^(Firefox — Sharing Indicator)$

# 固定位置和大小
windowrulev2 = size 800 600, class:^(mpv)$
windowrulev2 = center, class:^(mpv)$

# 全屏
windowrulev2 = fullscreen, class:^(gamescope)$

# 钉在屏幕上（在所有工作区都显示）
windowrulev2 = pin, class:^(conky)$
windowrulev2 = pin, title:^(.* - Discord)$

# 禁止平铺的窗口
windowrulev2 = noanim, class:^(firefox)$, title:^(Firefox — Sharing Indicator)$
windowrulev2 = nofocus, class:^$
windowrulev2 = noborder, class:^(firefox)$, title:^(.* — Sharing Indicator)$
windowrulev2 = noblur, class:^(firefox)$, title:^(.* — Sharing Indicator)$
windowrulev2 = noshadow, class:^(firefox)$, title:^(.* — Sharing Indicator)$
windowrulev2 = noinitialfocus, class:^(chromium)$

# 透明度
windowrulev2 = opacity 0.8 override 0.8, class:^(kitty)$ # 静态
windowrulev2 = opacity 0.9 0.7, class:^(foot)$ # 活动/非活动

# 圆角
windowrulev2 = rounding 0, class:^(firefox)$, title:^(.*Sharing Indicator)$

# 工作区分配
windowrulev2 = workspace 1 silent, class:^(firefox)$
windowrulev2 = workspace 2 silent, class:^(Alacritty)$
windowrulev2 = workspace 3 silent, class:^(code-oss)$

# 设置非活动窗口变暗
windowrulev2 = dimaround, class:^(gimp)$

# 保持宽高比
windowrulev2 = keepaspectratio, class:^(mpv)$
windowrulev2 = maxsize 1920 1080, class:^(.*)$

# 特殊工作区（scratchpad）
windowrulev2 = workspace special:magic silent, class:^(scratchpad)$
```

---

## 11.11 分层规则(Layer Rules)

```conf
# 控制 layer-shell 组件（waybar、通知等）
layerrule = blur, waybar
layerrule = blur, notifications
layerrule = ignorezero, notifications # 忽略透明区域
layerrule = ignorealpha 0.5, rofi
layerrule = dimaround, rofi

# 动画控制
layerrule = animation slide top, rofi # 从顶部滑入
layerrule = animation slide bottom, notifications
layerrule = noanim, waybar
```

---

## 11.12 hyprctl —— 运行时控制

```bash
# hyprctl 是 Hyprland 的命令行控制接口

# 工作区操作
hyprctl dispatch workspace 3
hyprctl dispatch movetoworkspace 5
hyprctl dispatch togglespecialworkspace magic

# 窗口操作
hyprctl dispatch killactive
hyprctl dispatch togglefloating
hyprctl dispatch fullscreen 1
hyprctl dispatch resizeactive 50 0
hyprctl dispatch moveactive -200 0

# 获取信息
hyprctl activewindow # 当前窗口信息(JSON)
hyprctl clients # 所有窗口
hyprctl monitors # 显示器信息
hyprctl workspaces # 工作区
hyprctl layers # Layer shell
hyprctl version # 版本信息

# 批量操作
hyprctl --batch "dispatch workspace 1; dispatch exec kitty"

# 监控事件
hyprctl events # 实时事件流
# 输出：activewindow>>kitty
# workspace>>2

# 设置属性
hyprctl setprop class:kitty alpha 0.8
hyprctl setprop address:0x5555... nomaxsize 0

# 切换配置变量
hyprctl keyword general:gaps_out 20
hyprctl keyword decoration:rounding 0

# 动画管理
hyprctl animations # 列出动画配置
```

---

## 11.13 编写 Hyprland 插件

```conf
# ~/.config/hypr/hyprland.conf
plugin = ~/.local/lib/hyprland/myplugin.so
```

### 插件模板 (C++)

```cpp
// myplugin.cpp — Hyprland 插件 API
#include <hyprland/src/plugins/PluginAPI.hpp>

// 注册插件
APICALL EXPORT std::string PLUGIN_API_VERSION() {
 return HYPRLAND_API_VERSION;
}

// 初始化
APICALL EXPORT PLUGIN_DESCRIPTION_INFO PLUGIN_INIT(HANDLE handle) {
 PHANDLE = handle;

 // 注册回调
 HyprlandAPI::registerCallbackDynamic(
 PHANDLE, "preRender",
 [&](void* self, SCallbackInfo& info, std::any data) {
 // 每帧渲染前执行
 }
 );

 HyprlandAPI::addConfigValue(PHANDLE, "plugin:myplugin:enable",
 Hyprlang::INT{1});

 return {"myplugin", "My Hyprland Plugin", "Me", "1.0"};
}

APICALL EXPORT void PLUGIN_EXIT() {
 // 清理
}
```

---

## 11.14 Hyprland 生态系统

```bash
# 核心工具
hyprpaper # 壁纸守护进程
hyprlock # 锁屏（GPU 加速、毛玻璃效果）
hypridle # 空闲管理
hyprpicker # 屏幕取色器
hyprcursor # 自定义光标主题格式
hyprgraphics # 图形测试工具

# hyprlock 配置 ~/.config/hypr/hyprlock.conf
# hypridle 配置 ~/.config/hypr/hypridle.conf

# 社区工具
hyprshot # 截图
hyprnome # 工作区切换器
hyprland-autoname-workspaces # 自动命名
```

---

## 11.15 本章测验

> [!example] 自测题目

> [!question]- 选择题 1：Hyprland 默认的平铺布局算法是什么？
> - A. master
> - B. dwindle
> - C. spiral
> - D. grid
>
> > [!success]- 点击查看答案
> > **B**
> > Hyprland 默认使用 dwindle 布局算法（螺旋二分），也可在 general 中切换为 master 布局。

> [!question]- 选择题 2：Hyprland 中设置窗口边框渐变色的正确语法是？
> - A. col.active_border = gradient($mauve, $pink, 45deg)
> - B. col.active_border = $mauve $pink 45deg
> - C. col.active_border = linear-gradient(45deg, $mauve, $pink)
> - D. col.active_border = [$mauve, $pink] angle=45
>
> > [!success]- 点击查看答案
> > **B**
> > Hyprland 中渐变色边框语法为直接列出颜色加角度：`col.active_border = $mauve $pink 45deg`。

> [!question]- 选择题 3：Hyprland 中 VRR (可变刷新率) 设置 vrr=2 表示什么？
> - A. VRR 关闭
> - B. VRR 始终开启
> - C. 仅全屏时开启 VRR
> - D. 仅游戏时开启 VRR
>
> > [!success]- 点击查看答案
> > **C**
> > vrr=0 关闭，vrr=1 始终开启，vrr=2 仅全屏时开启可变刷新率。

> [!question]- 判断题 4：Hyprland 的 submap 功能类似 Vim 的模式切换，可以创建多键组合操作
> - A. 正确
> - B. 错误
>
> > [!success]- 点击查看答案
> > **A. 正确**
> > submap 允许进入一个子键映射模式（如 resize 模式），在该模式下按键有不同含义，类似 Vim 的模式切换。用 `submap = reset` 退出。

> [!question]- 选择题 5：hyprctl 批量执行多个操作的正确语法是？
> - A. hyprctl dispatch workspace 1 && hyprctl dispatch exec kitty
> - B. hyprctl --batch "dispatch workspace 1; dispatch exec kitty"
> - C. hyprctl multi "workspace 1" "exec kitty"
> - D. hyprctl dispatch workspace 1 exec kitty
>
> > [!success]- 点击查看答案
> > **B**
> > hyprctl 使用 `--batch` 参数加分号分隔命令来批量执行多个操作。

> [!question]- 选择题 6：Hyprland 窗口规则中 `windowrulev2 = pin` 的效果是什么？
> - A. 固定窗口大小不可调整
> - B. 锁定窗口位置不可移动
> - C. 窗口在所有工作区都显示
> - D. 窗口置顶不可被覆盖
>
> > [!success]- 点击查看答案
> > **C**
> > pin 规则使窗口"钉"在屏幕上，即在所有工作区都可见（类似 sticky window）。

> [!question]- 判断题 7：Hyprland 的动画系统中，popin 80% 表示窗口从中心弹出到 80% 后回弹到 100%
> - A. 正确
> - B. 错误
>
> > [!success]- 点击查看答案
> > **A. 正确**
> > popin 动画样式表示从中心弹出，后面加百分比如 `popin 80%` 表示弹出到 80% 后回弹到 100%，产生弹性效果。

> [!question]- 选择题 8：Hyprland Layer Rules 中 `ignorezero` 的作用是？
> - A. 忽略 Z 坐标为 0 的层
> - B. 忽略透明区域（alpha=0 的像素不参与模糊）
> - C. 忽略宽度为 0 的边框
> - D. 忽略第 0 号工作区
>
> > [!success]- 点击查看答案
> > **B**
> > ignorezero 使透明区域（alpha=0 的像素）不参与模糊计算，常用于通知等有透明区域的层。

> [!question]- 判断题 9：bindm 是 Hyprland 中专门用于鼠标绑定的指令，m 代表 mouse
> - A. 正确
> - B. 错误
>
> > [!success]- 点击查看答案
> > **A. 正确**
> > bindm 用于绑定鼠标操作，如 `bindm = $mainMod, mouse:272, movewindow` 表示按住 Mod+左键拖动移动窗口。

> [!question]- 选择题 10：Hyprland 插件系统使用什么语言开发？
> - A. Lua
> - B. Python
> - C. C++
> - D. Rust
>
> > [!success]- 点击查看答案
> > **C**
> > Hyprland 插件使用 C++ 开发，通过 `PLUGIN_API_VERSION`、`PLUGIN_INIT`、`PLUGIN_EXIT` 等 API 与合成器交互。
