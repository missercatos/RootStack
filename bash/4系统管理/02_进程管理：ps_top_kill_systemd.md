# 进程管理：ps, top, kill, systemd | Process Management

## 章节概述

> **核心理念**：进程是程序执行的实例，管理进程就是管理系统资源。理解进程状态、信号机制、调度优先级和 systemd 服务管理，是 Linux 系统管理员的核心技能。

---

### 第1节：ps 命令详解

#### 1.1 ps aux

```bash
# 查看所有进程（BSD 风格）
ps aux

# 输出格式:
# USER  PID %CPU %MEM  VSZ  RSS TTY STAT START TIME COMMAND
# root    1  0.0  0.1 1696  520 ?   Ss   Aug20 0:03 /sbin/init
```

| 字段 | 说明 |
|------|------|
| `USER` | 进程所有者 |
| `PID` | 进程 ID |
| `%CPU` | CPU 使用率 |
| `%MEM` | 内存使用率 |
| `VSZ` | 虚拟内存大小（KB） |
| `RSS` | 实际内存大小（KB） |
| `STAT` | 进程状态 |
| `COMMAND` | 命令名称 |

#### 1.2 进程状态说明

| 状态 | 说明 |
|------|------|
| `R` | 运行中（Running） |
| `S` | 可中断睡眠（Sleeping） |
| `D` | 不可中断睡眠（等待 I/O） |
| `T` | 已停止（Stopped） |
| `Z` | 僵尸进程（Zombie） |
| `s` | 会话领导者（Session leader） |
| `+` | 前台进程组 |
| `<` | 高优先级 |
| `N` | 低优先级 |

#### 1.3 ps 高级用法

```bash
# 查看特定用户的进程
ps -u username

# 按 CPU 使用排序
ps aux --sort=-%cpu | head -20

# 按内存使用排序
ps aux --sort=-%mem | head -20

# 查看进程树
ps auxf
pstree -p

# 查看特定进程的线程
ps -Lf <PID>

# 查看进程的父进程
ps -o pid,ppid,comm -p <PID>
```

### 第2节：top/htop

#### 2.1 top 命令

```bash
# 启动 top
top

# 常用快捷键
# 1     - 显示每个 CPU 的使用情况
# M     - 按内存排序
# P     - 按 CPU 排序
# k     - 杀死进程
# h     - 显示帮助
# q     - 退出

# 非交互式运行（脚本中使用）
top -bn1 | head -20
```

#### 2.2 htop 增强版

```bash
# 安装 htop
sudo apt install htop    # Debian/Ubuntu
sudo yum install htop    # CentOS/RHEL

# 启动 htop
htop

# 按 F2 配置显示
# 按 F5 树形视图
# 按 F6 排序
# 按 F9 发送信号
```

### 第3节：kill/killall

#### 3.1 信号列表

| 信号 | 编号 | 说明 |
|------|------|------|
| `SIGHUP` | 1 | 挂起，重新加载配置 |
| `SIGINT` | 2 | 中断（Ctrl+C） |
| `SIGQUIT` | 3 | 退出，生成 core dump |
| `SIGKILL` | 9 | 强制终止（不可捕获） |
| `SIGTERM` | 15 | 终止（默认信号） |
| `SIGUSR1` | 10 | 用户自定义信号 1 |
| `SIGUSR2` | 12 | 用户自定义信号 2 |
| `SIGSTOP` | 19 | 暂停进程（不可捕获） |
| `SIGCONT` | 18 | 继续运行 |

#### 3.2 kill 命令使用

```bash
# 终止进程（默认 SIGTERM）
kill <PID>

# 强制终止（SIGKILL）
kill -9 <PID>
kill -SIGKILL <PID>

# 发送 SIGHUP（重新加载配置）
kill -HUP <PID>
kill -1 <PID>

# 发送自定义信号
kill -USR1 <PID>
```

#### 3.3 killall 和 pkill

```bash
# 终止所有同名进程
killall nginx
killall -9 nginx

# 按模式匹配终止
pkill -f "python3 app.py"
pkill -u username

# 查看进程是否运行
pgrep nginx
pgrep -l nginx  # 显示进程名
```

### 第4节：nice/renice

#### 4.1 调整优先级

```bash
# 以低优先级运行命令
nice -n 10 ./heavy_task.sh

# 以最高优先级运行
nice -n -20 ./critical_task.sh

# 修改运行中进程的优先级
renice -n 10 -p <PID>

# 修改用户所有进程的优先级
renice -n 10 -u username
```

| nice 值 | 说明 |
|---------|------|
| -20 ~ -1 | 高优先级（仅 root） |
| 0 | 默认优先级 |
| 1 ~ 19 | 低优先级 |

### 第5节：systemd 基本命令

#### 5.1 服务管理

```bash
# 启动服务
sudo systemctl start nginx

# 停止服务
sudo systemctl stop nginx

# 重启服务
sudo systemctl restart nginx

# 重新加载配置
sudo systemctl reload nginx

# 查看服务状态
sudo systemctl status nginx

# 设置开机自启
sudo systemctl enable nginx

# 禁用开机自启
sudo systemctl disable nginx

# 查看所有运行中的服务
systemctl list-units --type=service --state=running

# 查看所有已安装的服务
systemctl list-unit-files --type=service
```

#### 5.2 进程状态查看

```bash
# 查看进程的 systemd 状态
systemctl status <PID>

# 查看进程的 cgroup 信息
systemctl status <PID> | grep cgroup

# 查看进程的资源使用
systemd-cgtop

# 查看失败的服务
systemctl --failed
```

### 第6节：进程调试与监控

#### 6.1 /proc 文件系统

```bash
# 查看进程的命令行
cat /proc/<PID>/cmdline | tr '\0' ' '

# 查看进程的环境变量
cat /proc/<PID>/environ | tr '\0' '\n'

# 查看进程打开的文件
ls -la /proc/<PID>/fd

# 查看进程的内存映射
cat /proc/<PID>/maps

# 查看进程的资源限制
cat /proc/<PID>/limits
```

#### 6.2 strace 跟踪

```bash
# 跟踪系统调用
strace -p <PID>

# 跟踪特定系统调用
strace -e trace=open,read,write -p <PID>

# 跟踪并统计
strace -c -p <PID>

# 跟踪子进程
strace -f ./command
```

#### 6.3 lsof 查看打开的文件

```bash
# 查看进程打开的所有文件
lsof -p <PID>

# 查看端口被哪个进程占用
lsof -i :80
lsof -i :443

# 查看用户打开的文件
lsof -u username

# 查看特定文件被谁打开
lsof /var/log/syslog
```
