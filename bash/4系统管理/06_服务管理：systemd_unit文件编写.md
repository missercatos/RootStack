# 服务管理：systemd unit 文件编写 | Service Management: systemd Unit Files

## 章节概述

> **核心理念**：systemd 是现代 Linux 的初始化系统和服务管理器，掌握 unit 文件编写是系统管理员的必备技能。理解 [Unit]、[Service]、[Install] 三个部分，就像理解 C 语言的程序结构一样重要。

---

### 第1节：unit 文件结构

#### 1.1 基本模板

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My Application Service
Documentation=https://myapp.readthedocs.io
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=myapp
Group=myapp
WorkingDirectory=/opt/myapp
ExecStart=/opt/myapp/bin/myapp --config /etc/myapp/config.yaml
ExecReload=/bin/kill -HUP $MAINPID
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=myapp
PrivateTmp=true
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=/var/lib/myapp /var/log/myapp

[Install]
WantedBy=multi-user.target
```

#### 1.2 三个部分详解

| 部分 | 用途 |
|------|------|
| `[Unit]` | 服务描述、依赖关系、启动顺序 |
| `[Service]` | 服务运行方式、权限、资源控制 |
| `[Install]` | 安装时的配置（启用/禁用行为） |

### 第2节：服务类型

#### 2.1 Type 类型

```ini
[Service]
# simple - 主进程就是服务进程（默认）
Type=simple
ExecStart=/usr/bin/myapp

# forking - 服务会 fork 后退出（传统守护进程）
Type=forking
ExecStart=/usr/sbin/nginx
PIDFile=/run/nginx.pid

# oneshot - 执行一次就退出（初始化脚本）
Type=oneshot
ExecStart=/usr/local/bin/setup.sh
RemainAfterExit=yes

# notify - 类似 simple，但支持通知 systemd 就绪
Type=notify
ExecStart=/usr/bin/myapp

# dbus - 通过 D-Bus 获取名字后就绪
Type=dbus
BusName=com.example.MyApp
```

#### 2.2 Type 选择指南

| 场景 | 推荐 Type |
|------|-----------|
| 现代应用程序 | `simple` 或 `notify` |
| 传统守护进程 | `forking` |
| 初始化脚本 | `oneshot` |
| D-Bus 服务 | `dbus` |
| 容器服务 | `simple` |

### 第3节：依赖关系

#### 3.1 After/Before

```ini
[Unit]
# After: 在这些目标启动之后启动
After=network.target mysql.target redis.target

# Before: 在这些目标之前启动
Before=nginx.target
```

#### 3.2 Wants/Requires/Requisite

```ini
[Unit]
# Wants: 弱依赖（失败不影响启动）
Wants=redis.service
Wants=postgresql.service

# Requires: 强依赖（失败则停止）
Requires=mysql.service

# Requisite: 强依赖（必须已启动，否则立即失败）
Requisite=network-online.target

# BindsTo: 绑定（依赖停止则自己也停止）
BindsTo=docker.service

# PartOf: 部分（重启/停止会传播）
PartOf=myapp.target
```

#### 3.3 依赖关系图

```
网络就绪 (network-online.target)
    │
    ├─ Wants → redis.service
    ├─ Wants → postgresql.service
    │
    └─ After → myapp.service
                │
                ├─ Requires → myapp-worker.service
                │
                └─ Wants → myapp-scheduler.service
```

### 第4节：journal 日志

#### 4.1 日志配置

```ini
[Service]
# 日志输出到 journal
StandardOutput=journal
StandardError=journal
SyslogIdentifier=myapp

# 日志输出到文件
StandardOutput=append:/var/log/myapp/stdout.log
StandardError=append:/var/log/myapp/stderr.log

# 日志级别
LogLevelMax=info
```

#### 4.2 查看日志

```bash
# 查看服务日志
sudo journalctl -u myapp.service

# 实时查看日志
sudo journalctl -u myapp.service -f

# 查看最近 100 行
sudo journalctl -u myapp.service -n 100

# 按时间范围查看
sudo journalctl -u myapp.service --since "2026-08-22 10:00"
sudo journalctl -u myapp.service --since "1 hour ago"

# 查看内核日志
sudo journalctl -k

# 按优先级过滤
sudo journalctl -u myapp.service -p err

# 输出为文件
sudo journalctl -u myapp.service --since today > today.log
```

### 第5节：systemctl 操作

#### 5.1 基本操作

```bash
# 启动服务
sudo systemctl start myapp.service

# 停止服务
sudo systemctl stop myapp.service

# 重启服务
sudo systemctl restart myapp.service

# 重新加载配置
sudo systemctl reload myapp.service

# 查看状态
sudo systemctl status myapp.service

# 启用开机自启
sudo systemctl enable myapp.service

# 禁用开机自启
sudo systemctl disable myapp.service

# 查看是否启用
sudo systemctl is-enabled myapp.service

# 查看是否运行
sudo systemctl is-active myapp.service
```

#### 5.2 高级操作

```bash
# 查看服务的依赖关系
sudo systemctl list-dependencies myapp.service

# 查看服务的反向依赖
sudo systemctl list-dependencies --reverse myapp.service

# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 重载失败的服务
sudo systemctl reset-failed myapp.service

# 杀死服务的所有进程
sudo systemctl kill myapp.service

# 查看服务的属性
sudo systemctl show myapp.service

# 设置服务属性
sudo systemctl set-property myapp.service CPUQuota=50%
```

#### 5.3 Target 管理

```bash
# 查看所有 target
sudo systemctl list-units --type=target

# 切换到 multi-user.target（命令行模式）
sudo systemctl isolate multi-user.target

# 切换到 graphical.target（图形界面模式）
sudo systemctl isolate graphical.target

# 设置默认 target
sudo systemctl set-default multi-user.target

# 查看默认 target
systemctl get-default
```

### 第6节：完整示例

#### 6.1 Web 应用服务

```ini
# /etc/systemd/system/webapp.service
[Unit]
Description=Web Application
Documentation=https://webapp.readthedocs.io
After=network-online.target
Wants=network-online.target
Requires=postgresql.service redis.service

[Service]
Type=simple
User=webapp
Group=webapp
WorkingDirectory=/opt/webapp

Environment=NODE_ENV=production
Environment=PORT=8080
Environment=DATABASE_URL=postgresql://localhost:5432/webapp
Environment=REDIS_URL=redis://localhost:6379

ExecStart=/usr/bin/node server.js
ExecReload=/bin/kill -HUP $MAINPID

Restart=on-failure
RestartSec=10
StartLimitBurst=3
StartLimitIntervalSec=60

StandardOutput=journal
StandardError=journal
SyslogIdentifier=webapp

# 安全加固
PrivateTmp=true
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/webapp /var/log/webapp
CapabilityBoundingSet=
SystemCallFilter=@system-service
SystemCallArchitectures=native

# 资源限制
LimitNOFILE=65536
LimitNPROC=4096
MemoryMax=2G
CPUQuota=200%

[Install]
WantedBy=multi-user.target
```

#### 6.2 定时任务服务

```ini
# /etc/systemd/system/cleanup.service
[Unit]
Description=System Cleanup Service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/cleanup.sh

# /etc/systemd/system/cleanup.timer
[Unit]
Description=Run cleanup daily

[Timer]
OnCalendar=daily
Persistent=true
RandomizedDelaySec=1800

[Install]
WantedBy=timers.target
```

#### 6.3 Docker 容器服务

```ini
# /etc/systemd/system/mycontainer.service
[Unit]
Description=My Docker Container
After=docker.service
Requires=docker.service

[Service]
Type=simple
Restart=on-failure
RestartSec=30

ExecStartPre=-/usr/bin/docker stop mycontainer
ExecStartPre=-/usr/bin/docker rm mycontainer
ExecStart=/usr/bin/docker run --name mycontainer \
    --network host \
    -v /data/mycontainer:/data \
    -e TZ=Asia/Shanghai \
    myapp:latest

ExecStop=/usr/bin/docker stop mycontainer

StandardOutput=journal
StandardError=journal
SyslogIdentifier=mycontainer

[Install]
WantedBy=multi-user.target
```
