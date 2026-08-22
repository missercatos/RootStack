# 定时任务：crontab, anacron, systemd-timer | Scheduled Tasks

## 章节概述

> **核心理念**：定时任务是系统自动化的基石——从定期备份、日志轮转到系统维护，都依赖于精确的调度机制。理解 crontab、anacron 和 systemd timer，就像理解 C 语言的事件循环一样重要。

---

### 第1节：crontab 语法

#### 1.1 基本语法

```
# crontab 格式:
# ┌───────────── 分钟 (0-59)
# │ ┌───────────── 小时 (0-23)
# │ │ ┌───────────── 日 (1-31)
# │ │ │ ┌───────────── 月 (1-12)
# │ │ │ │ ┌───────────── 星期 (0-7, 0和7都是周日)
# │ │ │ │ │
# * * * * * command

# 示例:
0 2 * * * /path/to/backup.sh          # 每天凌晨 2 点
30 8 * * 1-5 /path/to/weekday.sh      # 工作日 8:30
0 */4 * * * /path/to/every4hours.sh    # 每 4 小时
0 0 1 * * /path/to/monthly.sh          # 每月 1 号
0 22 * * 5 /path/to/friday.sh          # 每周五 22:00
```

#### 1.2 crontab 操作

```bash
# 编辑当前用户的 crontab
crontab -e

# 查看当前用户的 crontab
crontab -l

# 查看所有用户的 crontab
sudo ls -la /var/spool/cron/crontabs/

# 删除当前用户的 crontab
crontab -r

# 从文件导入 crontab
crontab backup.crontab

# 特定用户的 crontab
sudo crontab -u username -e
```

#### 1.3 crontab 特殊字符串

| 字符 | 说明 | 等价 |
|------|------|------|
| `@reboot` | 系统启动时运行 | - |
| `@yearly` | 每年运行 | `0 0 1 1 *` |
| `@monthly` | 每月运行 | `0 0 1 * *` |
| `@weekly` | 每周运行 | `0 0 * * 0` |
| `@daily` | 每天运行 | `0 0 * * *` |
| `@hourly` | 每小时运行 | `0 * * * *` |

#### 1.4 crontab 最佳实践

```bash
# 1. 设置环境变量
PATH=/usr/local/bin:/usr/bin:/bin
MAILTO=user@example.com
SHELL=/bin/bash

# 2. 使用完整路径
0 2 * * * /usr/bin/python3 /home/user/script.py

# 3. 重定向输出
0 2 * * * /path/to/script.sh >> /var/log/script.log 2>&1

# 4. 使用锁防止重复执行
0 * * * * flock -n /tmp/script.lock /path/to/script.sh
```

### 第2节：anacron

#### 2.1 anacron 概念

anacron 适用于非 24/7 运行的系统（如笔记本电脑），它会在系统启动时检查错过的任务。

```bash
# /etc/anacrontab 格式:
# period  delay  job-identifier  command
1         5      daily-backup    /usr/local/bin/backup.sh
7         10     weekly-cleanup  /usr/local/bin/cleanup.sh
```

| 字段 | 说明 |
|------|------|
| `period` | 执行间隔（天） |
| `delay` | 启动后延迟（分钟） |
| `job-identifier` | 任务标识 |
| `command` | 要执行的命令 |

#### 2.2 anacron 使用

```bash
# 手动触发 anacron
sudo anacron -f

# 查看 anacron 状态
sudo anacron -n

# 编辑 anacron 配置
sudo vim /etc/anacrontab

# 查看 anacron 日志
grep anacron /var/log/syslog
```

### 第3节：systemd timer

#### 3.1 创建 systemd timer

```bash
# /etc/systemd/system/mytask.timer
[Unit]
Description=Run mytask daily

[Timer]
OnCalendar=daily
Persistent=true
RandomizedDelaySec=1800

[Install]
WantedBy=timers.target
```

#### 3.2 创建对应的服务

```bash
# /etc/systemd/system/mytask.service
[Unit]
Description=My daily task
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/mytask.sh
User=root
StandardOutput=journal
StandardError=journal
```

#### 3.3 timer 定时选项

| 选项 | 说明 |
|------|------|
| `OnCalendar` | 按日历时间触发 |
| `OnBootSec` | 启动后延迟 |
| `OnUnitActiveSec` | 上次执行后间隔 |
| `Persistent` | 错过的任务在启动后补执行 |
| `RandomizedDelaySec` | 随机延迟 |
| `AccuracySec` | 时间精度 |

#### 3.4 systemd timer 操作

```bash
# 启用 timer
sudo systemctl enable mytask.timer
sudo systemctl start mytask.timer

# 查看 timer 状态
sudo systemctl list-timers
sudo systemctl list-timers --all

# 查看 timer 详情
sudo systemctl status mytask.timer
sudo systemctl cat mytask.timer

# 查看执行历史
sudo journalctl -u mytask.service

# 手动触发
sudo systemctl start mytask.service
```

### 第4节：at/batch

#### 4.1 at 一次性任务

```bash
# 在指定时间执行任务
echo "/path/to/script.sh" | at 2:00 AM
echo "/path/to/script.sh" | at 10:00 PM tomorrow
echo "/path/to/script.sh" | at noon + 3 days

# 交互式创建
at now + 1 hour
# 输入命令，Ctrl+D 结束

# 查看任务队列
atq

# 删除任务
atrm <job_id>
```

#### 4.2 batch 批处理

```bash
# 在系统负载低时执行
echo "/path/to/heavy_task.sh" | batch

# 查看 batch 队列
atq -b
```

### 第5节：日志查看

#### 5.1 cron 日志

```bash
# 查看 cron 日志
grep CRON /var/log/syslog
grep CRON /var/log/cron

# 查看特定用户的 cron 日志
grep CRON | grep username

# 使用 journalctl 查看
sudo journalctl -u cron
sudo journalctl -u crond
```

#### 5.2 systemd timer 日志

```bash
# 查看特定服务的日志
sudo journalctl -u mytask.service

# 查看最近的日志
sudo journalctl -u mytask.service -n 50

# 实时查看日志
sudo journalctl -u mytask.service -f

# 按时间范围查看
sudo journalctl -u mytask.service --since "2026-08-22" --until "2026-08-23"
```

### 第6节：定时任务对比

| 特性 | crontab | anacron | systemd timer |
|------|---------|---------|---------------|
| 适用场景 | 服务器 | 笔记本/桌面 | 现代系统 |
| 最小间隔 | 1 分钟 | 1 天 | 微秒级 |
| 错过任务 | 不补执行 | 启动后补执行 | 可配置 |
| 依赖管理 | 无 | 无 | 支持 |
| 日志集成 | syslog | syslog | journal |
| 资源控制 | 无 | 无 | 支持 |
| 并发控制 | 需手动 | 需手动 | 内置 |
| 配置文件 | /etc/crontab | /etc/anacrontab | .timer + .service |
