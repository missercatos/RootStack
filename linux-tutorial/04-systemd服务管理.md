# 04 - systemd 服务管理

> systemd 是 Linux 的初始化系统和服务管理器，Arch Linux 从 2012 年起使用。

---

## 4.1 systemctl 基本操作

```bash
# 启动/停止/重启
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl restart nginx
sudo systemctl reload nginx          # 重载配置（不停服务）

# 启用/禁用（开机自启）
sudo systemctl enable nginx
sudo systemctl disable nginx
sudo systemctl enable --now nginx    # 启用并立即启动
sudo systemctl disable --now nginx   # 禁用并立即停止

# 查看状态
systemctl status nginx
systemctl is-active nginx
systemctl is-enabled nginx
systemctl is-failed nginx

# 列出服务
systemctl list-units --type=service
systemctl list-units --type=service --state=running
systemctl list-units --type=service --state=failed
systemctl list-unit-files --type=service
```

---

## 4.2 Unit 类型

| 类型 | 后缀 | 说明 |
|------|------|------|
| service | `.service` | 系统服务 |
| socket | `.socket` | IPC 套接字 |
| target | `.target` | 运行级别分组（替代 SysV runlevel） |
| timer | `.timer` | 定时任务 |
| mount | `.mount` | 挂载点 |
| device | `.device` | 设备文件 |
| slice | `.slice` | 资源分组 |

### 常用 target

```bash
# 查看当前 target
systemctl get-default

# 设置默认 target
sudo systemctl set-default multi-user.target    # 命令行模式
sudo systemctl set-default graphical.target     # 图形界面

# 切换 target
sudo systemctl isolate multi-user.target
sudo systemctl isolate rescue.target            # 救援模式
sudo systemctl isolate emergency.target         # 紧急模式

# target 对应关系
# graphical.target    → 图形界面（类似 runlevel 5）
# multi-user.target   → 多用户命令行（类似 runlevel 3）
# rescue.target       → 单用户恢复
# emergency.target    → 最简环境
```

---

## 4.3 编写 .service 文件

### 系统服务 `/etc/systemd/system/`

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My Application
After=network.target              # 在网络就绪后启动
Requires=postgresql.service       # 强硬依赖（postgresql 失败此服务也失败）
Wants=redis.service               # 软依赖（redis 失败不影响）

[Service]
Type=simple                       # 默认，主进程即服务
User=myapp
Group=myapp
WorkingDirectory=/opt/myapp
ExecStart=/usr/bin/python /opt/myapp/server.py
ExecStop=/bin/kill -s SIGTERM $MAINPID
ExecReload=/bin/kill -s SIGHUP $MAINPID
Restart=on-failure                # 仅在异常退出时重启
RestartSec=5                      # 重启间隔

# 安全加固
NoNewPrivileges=yes
PrivateTmp=true
ProtectHome=true
ProtectSystem=strict

[Install]
WantedBy=multi-user.target
```

### Type 参数说明

| Type | 说明 |
|------|------|
| `simple` | 默认，fork 后立即认为已启动 |
| `forking` | 子进程 fork 后父进程退出，用 PIDFile 定位 |
| `oneshot` | 执行完退出，配合 `RemainAfterExit=yes` |
| `notify` | 服务主动发送信号告知就绪 |
| `idle` | 等所有作业完成后才启动 |

### 重载服务

```bash
sudo systemctl daemon-reload        # 重新读取 unit 文件
sudo systemctl enable myapp.service
sudo systemctl start myapp.service
```

---

## 4.4 用户级 systemd 服务

```bash
# 服务文件位置
~/.config/systemd/user/myapp.service

# 用户级命令（不加 sudo，加 --user）
systemctl --user daemon-reload
systemctl --user enable --now myapp.service
systemctl --user status myapp.service

# 允许用户在未登录时运行服务（执行一次即可）
sudo loginctl enable-linger alice
```

---

## 4.5 journalctl 日志查看

```bash
# 基本查看
journalctl                              # 所有日志
journalctl -b                           # 本次启动以来的日志
journalctl -b -1                        # 上一次启动的日志
journalctl -k                           # 内核日志

# 按服务筛选
journalctl -u nginx
journalctl -u nginx --since "2025-01-01"
journalctl -u nginx --since "1 hour ago"
journalctl -u nginx -f                  # 实时跟踪（类似 tail -f）

# 格式化输出
journalctl -u nginx -o json-pretty      # JSON 格式
journalctl -u nginx -o short-full       # 完整时间戳

# 磁盘管理
journalctl --disk-usage                 # 查看占用
sudo journalctl --vacuum-time=2weeks    # 清理旧日志
sudo journalctl --vacuum-size=500M      # 限制大小

# /etc/systemd/journald.conf 配置持久化
# Storage=persistent
```

---

## 4.6 分析启动耗时

```bash
systemd-analyze                        # 总启动时间
systemd-analyze blame                  # 各服务耗时排行
systemd-analyze critical-chain         # 关键链分析
systemd-analyze plot > boot.svg        # 生成 SVG 图表
```

---

## 4.7 常见考题

1. 怎么让 nginx 开机自启？ → `systemctl enable nginx`
2. daemon-reload 什么时候用？ → 修改了 `.service` 文件后
3. `Wants` 和 `Requires` 区别？ → Wants 弱依赖，失败不影响；Requires 强依赖，失败则停
4. `.service` 文件放哪？ → 系统级 `/etc/systemd/system/`，用户级 `~/.config/systemd/user/`
5. 怎么看 nginx 实时日志？ → `journalctl -u nginx -f`

---

## 4.8 本章测验

> [!example] 📝 自测题目

> [!question]- 选择题 1：修改 `.service` 文件后，需要执行什么命令使其生效？
> - A. `systemctl restart`
> - B. `systemctl daemon-reload`
> - C. `systemctl reload`
> - D. `systemctl refresh`
>
> > [!success]- 点击查看答案
> > **B**
> > `daemon-reload` 让 systemd 重新读取所有 unit 文件，识别配置变更

> [!question]- 选择题 2：`systemctl enable --now nginx` 等价于？
> - A. `enable` + `restart`
> - B. `enable` + `start`
> - C. `start` + `reload`
> - D. `enable` + `reload`
>
> > [!success]- 点击查看答案
> > **B**
> > `--now` 在 enable 的同时立即启动服务，等价于先 enable 再 start

> [!question]- 判断题 3：`Wants=redis.service` 表示 redis 失败时当前服务也会停止
> - A. ✓ 正确
> - B. ✗ 错误
>
> > [!success]- 点击查看答案
> > **B. ✗ 错误**
> > `Wants` 是弱依赖，被依赖的服务失败不影响当前服务；`Requires` 才是强依赖

> [!question]- 选择题 4：`multi-user.target` 对应传统 SysV 的哪个运行级别？
> - A. runlevel 1
> - B. runlevel 3
> - C. runlevel 5
> - D. runlevel 0
>
> > [!success]- 点击查看答案
> > **B**
> > multi-user.target 对应多用户命令行模式（runlevel 3），graphical.target 对应 runlevel 5

> [!question]- 选择题 5：查看 nginx 服务实时日志的命令是？
> - A. `tail -f /var/log/nginx`
> - B. `journalctl -u nginx -f`
> - C. `systemctl log nginx`
> - D. `dmesg -u nginx`
>
> > [!success]- 点击查看答案
> > **B**
> > `journalctl -u` 按 unit 筛选日志，`-f` 实时跟踪新输出

> [!question]- 判断题 6：用户级 systemd 服务需要使用 `sudo` 来管理
> - A. ✓ 正确
> - B. ✗ 错误
>
> > [!success]- 点击查看答案
> > **B. ✗ 错误**
> > 用户级服务使用 `systemctl --user` 管理，不需要 sudo

> [!question]- 选择题 7：Service 段中 `Type=oneshot` 适用于什么场景？
> - A. 持续运行的守护进程
> - B. 执行完就退出的一次性任务
> - C. 需要 fork 子进程的服务
> - D. 监听套接字的服务
>
> > [!success]- 点击查看答案
> > **B**
> > `oneshot` 适用于执行完即退出的任务，常配合 `RemainAfterExit=yes` 使用

> [!question]- 选择题 8：`systemd-analyze blame` 的作用是？
> - A. 查看当前运行的服务
> - B. 列出各服务的启动耗时排行
> - C. 分析服务依赖关系
> - D. 查看失败的服务
>
> > [!success]- 点击查看答案
> > **B**
> > `blame` 按启动耗时从多到少排列所有已启动的 unit

> [!question]- 判断题 9：`loginctl enable-linger alice` 允许 alice 的用户服务在未登录时运行
> - A. ✓ 正确
> - B. ✗ 错误
>
> > [!success]- 点击查看答案
> > **A. ✓ 正确**
> > enable-linger 使用户的 systemd 实例在开机时启动，即使用户未登录也能运行用户级服务

> [!question]- 选择题 10：清理两周前的 journal 日志应使用？
> - A. `journalctl --vacuum-time=2weeks`
> - B. `journalctl --clean=2w`
> - C. `journalctl --delete-old 14d`
> - D. `rm /var/log/journal/*`
>
> > [!success]- 点击查看答案
> > **A**
> > `--vacuum-time` 删除指定时间之前的日志，是 journald 的标准清理方式
