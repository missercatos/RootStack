# 21 - SSH 远程管理

> SSH（Secure Shell）是 Linux 系统管理的基石协议。它提供了加密的远程登录、命令执行、文件传输和端口转发能力。无论是管理云服务器、维护本地服务还是搭建隧道穿透内网，SSH 都是不可或缺的核心技能。本章从 SSH 协议原理讲起，深入客户端配置、密钥认证、端口转发、sshd 服务端配置及安全加固等实战内容。

---

## 21.1 SSH 概述

### 什么是 SSH

SSH 协议通过不安全的网络建立安全的加密通道。它取代了传统的 telnet、rlogin、rsh 等明文协议：

```
┌──────────┐ 加密通道 ┌──────────┐
│ SSH │ ════════════════════════ │ SSH │
│ Client │ 端口: 22 │ Server │
└──────────┘ └──────────┘
 │ │
 ├── 远程命令执行 │
 ├── SFTP 文件传输 │
 ├── 端口转发 / 隧道 │
 └── X11 转发 │
```

| 组件 | 说明 |
|------|------|
| OpenSSH | Linux 上最流行的 SSH 实现 |
| ssh | 客户端程序 |
| sshd | 服务端守护进程 |
| ssh-keygen | 密钥生成工具 |
| ssh-copy-id | 公钥分发工具 |
| ssh-agent | 密钥代理（缓存解密后的私钥） |

### 安装 OpenSSH

不同发行版的安装方式：

```bash
# Debian / Ubuntu
sudo apt install openssh-client openssh-server

# RHEL / Fedora
sudo dnf install openssh-clients openssh-server

# openSUSE
sudo zypper install openssh

# Arch
sudo pacman -S openssh
```

> 几乎所有 Linux 发行版都预装了 OpenSSH 客户端。服务器端可能需要额外安装。

---

## 21.2 SSH 客户端基础

### 基本连接

```bash
# 最简方式：使用当前用户名连接
ssh 192.168.1.100

# 指定用户名
ssh user@192.168.1.100

# 指定端口（默认 22）
ssh -p 2222 user@192.168.1.100

# 指定私钥
ssh -i ~/.ssh/my_key user@192.168.1.100

# 详细输出（调试用）
ssh -v user@192.168.1.100
ssh -vv user@192.168.1.100 # 更详细
ssh -vvv user@192.168.1.100 # 最详细

# 仅执行一条命令
ssh user@server "uptime"
ssh user@server "sudo systemctl restart nginx"

# 执行本地脚本
ssh user@server 'bash -s' < local_script.sh
```

### 首次连接与 known_hosts

首次连接时 SSH 会提示确认主机指纹：

```
The authenticity of host '192.168.1.100' can't be established.
ED25519 key fingerprint is SHA256:xxxxxxxxxxxxxxx.
Are you sure you want to continue connecting (yes/no)?
```

确认后，主机公钥会保存到 `~/.ssh/known_hosts`：

```bash
# 查看已知主机
cat ~/.ssh/known_hosts

# 移除某台主机的记录
ssh-keygen -R 192.168.1.100
ssh-keygen -R "[192.168.1.100]:2222" # 带端口
```

---

## 21.3 密钥认证

密钥认证比密码认证更安全，也是自动化脚本的基础。

### 生成密钥对

```bash
# 推荐：Ed25519（现代、安全、短密钥）
ssh-keygen -t ed25519 -C "your_email@example.com"

# 传统：RSA 4096（兼容性好）
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# ECDSA（备选）
ssh-keygen -t ecdsa -b 521 -C "your_email@example.com"

# 输出文件（默认）：
# ~/.ssh/id_ed25519 私钥（绝不要分享！）
# ~/.ssh/id_ed25519.pub 公钥（放到服务器上）
```

交互式提示：

```
Enter file in which to save the key: # 回车使用默认路径
Enter passphrase: # 设置私钥密码（推荐）
Enter same passphrase again:
```

### 分发公钥到服务器

```bash
# 方法一：ssh-copy-id（最方便）
ssh-copy-id user@192.168.1.100
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@192.168.1.100

# 方法二：手动复制
cat ~/.ssh/id_ed25519.pub | ssh user@server "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"

# 方法三：scp
scp ~/.ssh/id_ed25519.pub user@server:~/
ssh user@server "cat ~/id_ed25519.pub >> ~/.ssh/authorized_keys && rm ~/id_ed25519.pub"
```

### 权限设置（服务器端）

SSH 对权限检查非常严格，权限不对会拒绝认证：

```bash
# 在服务器上执行
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chmod 644 ~/.ssh/id_*.pub # 公钥可读
chmod 600 ~/.ssh/id_* # 私钥仅自己读写
```

| 文件 | 权限 | 说明 |
|------|------|------|
| `~/.ssh/` | 700 | 仅自己可进入 |
| `~/.ssh/authorized_keys` | 600 | 仅自己可读写 |
| `~/.ssh/id_ed25519` | 600 | 私钥 |
| `~/.ssh/id_ed25519.pub` | 644 | 公钥 |
| `~/.ssh/config` | 600 | 客户端配置 |
| `~/.ssh/known_hosts` | 644 | 已知主机列表 |

---

## 21.4 SSH 客户端配置文件

`~/.ssh/config` 可以简化连接，支持主机别名、代理跳转、密钥指定等。

```ssh-config
# ~/.ssh/config

# === 基本格式 ===
Host myserver
 HostName 192.168.1.100
 Port 2222
 User alice
 IdentityFile ~/.ssh/id_ed25519

# === 通用默认值 ===
Host *
 ServerAliveInterval 60
 ServerAliveCountMax 3
 TCPKeepAlive yes
 Compression yes
 ForwardAgent no
 ForwardX11 no

# === 跳板机 / 代理跳转 ===
Host production
 HostName 10.0.1.50
 User deploy
 ProxyJump jump-host

Host jump-host
 HostName jump.example.com
 User admin
 IdentityFile ~/.ssh/bastion_key

# === 多级跳转 ===
Host deep-server
 HostName 10.0.2.100
 User root
 ProxyJump admin@gateway:22,root@internal:22

# === 不同的密钥 ===
Host github.com
 HostName github.com
 User git
 IdentityFile ~/.ssh/github_key
 IdentitiesOnly yes

Host gitlab.com
 HostName gitlab.com
 User git
 IdentityFile ~/.ssh/gitlab_key
 IdentitiesOnly yes

# === 按网段匹配 ===
Host 10.0.*
 User admin
 IdentityFile ~/.ssh/internal_key
 StrictHostKeyChecking no # 开发环境可放宽
 UserKnownHostsFile /dev/null

# === IPv6 连接 ===
Host ipv6-server
 HostName 2001:db8::1
 User alice
 AddressFamily inet6
```

配置生效后即可简化为：

```bash
ssh myserver # 等同于 ssh -p 2222 -i ~/.ssh/id_ed25519 alice@192.168.1.100
ssh production # 自动通过跳板机
```

---

## 21.5 端口转发（SSH 隧道）

SSH 端口转发可以在加密通道内传输任意 TCP 流量。这是 SSH 最强大但常被忽视的功能之一。

### 本地端口转发（-L）

将本地端口转发到远程目标。访问本地端口 = 访问远程目标：

```bash
# 语法：ssh -L 本地端口:目标主机:目标端口 user@ssh_server

# 示例：将本地 8080 转发到远端服务器的 80
ssh -L 8080:localhost:80 user@server
# 现在访问 http://localhost:8080 等同于访问 server 的 80 端口

# 示例：通过跳板机访问内网数据库
ssh -L 5432:10.0.1.100:5432 user@jump.example.com
# 本地 psql -h localhost -p 5432 连接到内网 PostgreSQL

# 多端口转发
ssh -L 8080:localhost:80 -L 8443:localhost:443 user@server
```

```
┌──────────┐ 加密隧道 ┌──────────┐ 普通连接 ┌──────────┐
│ 本地 │ ═══════════════════ │ SSH │ ──────────-> │ 目标 │
│ :8080 │ │ Server │ │ :80 │
│ 访问本地 │ │ │ │ (内部服务) │
└──────────┘ └──────────┘ └──────────┘
```

### 远程端口转发（-R）

将远程端口转发到本地。让远程主机能访问本地的服务：

```bash
# 语法：ssh -R 远程端口:目标主机:目标端口 user@ssh_server

# 示例：让远程服务器能访问本机 3000 端口
ssh -R 9000:localhost:3000 user@server
# 在 server 上访问 localhost:9000 等同于访问本机 3000 端口

# 示例：将内网服务暴露到公网 VPS
ssh -R 0.0.0.0:80:localhost:3000 user@public_vps
# 公网 VPS 的 80 端口流量转发到内网本机的 3000
```

> 注意：`GatewayPorts yes` 需在 sshd_config 中设置才能绑定到 0.0.0.0。

### 动态端口转发（-D）

创建 SOCKS5 代理，将 SSH 服务器作为代理出口：

```bash
# 创建 SOCKS5 代理
ssh -D 1080 user@server

# 在浏览器中设置 SOCKS5 代理为 localhost:1080
# 或在终端中使用
export ALL_PROXY=socks5://127.0.0.1:1080
curl https://httpbin.org/ip

# Firefox 使用 SOCKS5（自动配置）
# 设置 → 网络设置 → SOCKS 主机: 127.0.0.1 端口: 1080
```

```
┌──────────┐ SOCKS5 ┌──────────┐ 普通连接 ┌──────────┐
│ 本地 │ ═══════════=> │ SSH │ ──────────> │ Internet│
│ 浏览器 │ │ Server │ │ │
│ curl │ │ │ │ │
└──────────┘ └──────────┘ └──────────┘
```

### 后台保持隧道

```bash
# -f: 后台运行, -N: 不执行命令, -T: 不分配终端
ssh -fNT -L 8080:localhost:80 user@server

# 配合 autossh 自动重连
autossh -M 0 -fNT -L 8080:localhost:80 user@server
```

---

## 21.6 SCP 与 rsync over SSH

### SCP（安全拷贝）

```bash
# 本地 → 远程
scp file.txt user@server:/path/
scp -r mydir user@server:/path/ # 递归目录

# 远程 → 本地
scp user@server:/remote/file.txt ./local/

# 远程 → 远程
scp user@host1:/file.txt user@host2:/dest/

# 指定端口
scp -P 2222 file.txt user@server:/path/

# 压缩传输
scp -C large_file.bin user@server:/path/

# 保留属性
scp -p file.txt user@server:/path/ # 小写 p 保留时间戳
```

> SCP 协议已逐渐被更安全的 SFTP 协议替代。现代 scp 命令实际使用 SFTP 协议。

### SFTP（SSH 文件传输协议）

```bash
# 交互式 SFTP 客户端
sftp user@server

sftp> ls
sftp> cd /var/www
sftp> get file.txt # 下载
sftp> put file.txt # 上传
sftp> get -r mydir/ # 递归下载
sftp> rm file.txt
sftp> mkdir dirname
sftp> bye
```

### rsync over SSH

rsync 是更强大的文件同步工具，支持增量传输、断点续传：

```bash
# 基本用法
rsync -avz ./local_dir/ user@server:/remote_dir/

# 常用参数
rsync -avzP /src/ user@server:/dst/ # P=进度+断点续传
rsync -avz --delete /src/ user@server:/dst/ # 镜像同步
rsync -avz --exclude='node_modules' --exclude='.cache' /src/ server:/dst/

# 通过自定义端口
rsync -avz -e "ssh -p 2222" /src/ user@server:/dst/

# 通过跳板机
rsync -avz -e "ssh -J jump" /src/ target:/dst/

# 生成备份快照（硬链接去重）
rsync -avz --link-dest=/backup/latest/ /src/ /backup/$(date +%Y%m%d)/
```

| 特性 | scp | rsync |
|------|-----|-------|
| 增量传输 | 否 | 是 |
| 断点续传 | 否 | 是 |
| 压缩 | 支持 | 支持（更好） |
| 符号链接处理 | 简单 | 丰富选项 |
| 文件过滤 | 否 | 支持 exclude/include |
| 适用场景 | 少量文件快速复制 | 大量文件、备份、同步 |

---

## 21.7 SSHD 服务端配置

### 配置文件结构

主配置文件 `/etc/ssh/sshd_config`：

```bash
# 备份原配置
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak

# 验证配置语法
sudo sshd -t

# 查看当前生效的配置
sudo sshd -T
```

### 关键安全设置

```ini
# /etc/ssh/sshd_config（推荐的安全配置）

# === 端口 ===
Port 22 # 可改为非标准端口减少扫描噪

# === 监听 ===
ListenAddress 0.0.0.0 # 限制监听特定 IP
# ListenAddress 192.168.1.100

# === 用户认证 ===
PermitRootLogin no # 禁止 root 直接登录
PubkeyAuthentication yes # 启用密钥认证
PasswordAuthentication no # 禁用密码认证（密钥认证就绪后）
ChallengeResponseAuthentication no # 禁用挑战响应
UsePAM yes # 使用 PAM 认证

# === 限制登录 ===
AllowUsers alice bob # 白名单（推荐）
AllowGroups sshusers # 按组白名单
# DenyUsers baduser # 黑名单
# DenyGroups badgroup

# === 登录限制 ===
MaxAuthTries 3 # 最大认证尝试次数
MaxSessions 10 # 单连接最大会话数
LoginGraceTime 30 # 登录超时（秒）

# === 密钥认证 ===
AuthorizedKeysFile .ssh/authorized_keys
HostKey /etc/ssh/ssh_host_ed25519_key

# === 保活 ===
ClientAliveInterval 300 # 每 5 分钟发一次保活包
ClientAliveCountMax 2 # 连续 2 次无响应则断开

# === 转发控制 ===
X11Forwarding no # 禁用 X11 转发
AllowAgentForwarding no # 禁用 agent 转发（多用户场景）
AllowTcpForwarding yes # 端口转发（按需）
GatewayPorts no # 禁止远程端口转发绑定 0.0.0.0

# === SFTP 隔离 ===
# Subsystem sftp internal-sftp # 使用内部 SFTP
# Match Group sftponly # 限制 SFTP 用户
# ChrootDirectory /srv/sftp
# ForceCommand internal-sftp
# X11Forwarding no
# AllowTcpForwarding no

# === 加密算法（现代安全级别）===
KexAlgorithms curve25519-sha256,curve25519-sha256@libssh.org,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com
MACs hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com

# === 日志 ===
SyslogFacility AUTH
LogLevel VERBOSE # 记录指纹方便审计
```

### 配置变更后

```bash
# 验证配置
sudo sshd -t

# 重载配置（不中断现有连接）
sudo systemctl reload sshd
# 或
sudo kill -HUP $(pidof sshd)
```

### 查看当前连接

```bash
# 查看 SSHD 连接
sudo ss -tnp | grep :22
sudo lsof -i :22

# 查看当前登录用户
w
who

# 踢出特定会话
sudo pkill -u username sshd
```

---

## 21.8 SSH Agent 转发

ssh-agent 缓存解密后的私钥，避免反复输入密码短语。

### 本地使用

```bash
# 启动 agent（大多数桌面环境已自动启动）
eval $(ssh-agent)

# 添加密钥
ssh-add ~/.ssh/id_ed25519
ssh-add -l # 列出已加载的密钥
ssh-add -L # 列出已加载的公钥
ssh-add -d ~/.ssh/id_ed25519 # 删除指定密钥
ssh-add -D # 删除所有密钥

# 设置密钥有效期
ssh-add -t 3600 ~/.ssh/id_ed25519 # 1 小时后自动移除
```

### Agent 转发（谨慎使用）

Agent 转发允许在服务器上使用本地的密钥认证：

```bash
# 方式一：命令行
ssh -A user@server

# 方式二：配置文件
Host server
 ForwardAgent yes
```

> **安全警告**：Agent 转发存在安全风险。如果有 root 权限的恶意用户登录了同一台跳板机，可以利用你的 agent socket 进行认证。生产环境建议使用 ProxyJump 或 `ssh -J` 代替 agent 转发。

### 安全的替代方案：ProxyJump

```bash
# 不使用 agent 转发，用 ProxyJump 替代
ssh -J user@jump-host user@target-host

# ~/.ssh/config 配置
Host target
 ProxyJump jump-host
```

---

## 21.9 tmux / screen 持久化会话

通过 SSH 运行长时间任务时，断开连接会导致进程终止。终端复用器解决了这个问题。详见 [[55-终端常用工具大全]]。

### tmux 快速入门

```bash
# 安装
# Debian/Ubuntu: sudo apt install tmux
# RHEL/Fedora: sudo dnf install tmux
# Arch: sudo pacman -S tmux

# 基本操作
tmux # 创建新会话
tmux new -s mywork # 命名会话
tmux ls # 列出所有会话
tmux attach -t mywork # 重新连接会话

# 常用快捷键（默认前缀 Ctrl+b）：
# Ctrl+b % 水平分割窗口
# Ctrl+b " 垂直分割窗口
# Ctrl+b 方向键 切换窗格
# Ctrl+b d 脱离会话（detach）
# Ctrl+b c 创建新窗口
# Ctrl+b [ 进入滚动模式
# Ctrl+b x 关闭当前窗格
```

### screen 快速入门

```bash
# 安装
# Debian/Ubuntu: sudo apt install screen
# RHEL/Fedora: sudo dnf install screen

screen -S mywork # 创建命名会话
screen -ls # 列出会话
screen -r mywork # 重新连接
screen -d mywork # 强制分离

# 快捷键（默认前缀 Ctrl+a）：
# Ctrl+a c 创建新窗口
# Ctrl+a d 脱离会话
# Ctrl+a " 窗口列表
# Ctrl+a ' 切换窗口
```

### SSH + tmux 最佳实践

```bash
# 一键连接并创建/重连会话
ssh user@server -t 'tmux new -A -s work'

# 在 ~/.ssh/config 中配置
Host myserver
 HostName 192.168.1.100
 User alice
 RequestTTY yes
 RemoteCommand tmux new -A -s work
```

---

## 21.10 SSH 安全最佳实践

### 检查清单

```bash
# 1. 检查密钥配置
ssh-keygen -l -f ~/.ssh/id_ed25519 # 查看密钥指纹
sudo cat /var/log/auth.log | grep "Failed password"

# 2. 检查 sshd 配置
sudo sshd -t
sudo sshd -T | grep -E "(permitroot|passwordauth|pubkeyauth)"

# 3. 查看当前安全级别
ssh -o PreferredAuthentications=publickey user@server 2>&1
```

### 额外安全措施

| 措施 | 命令/配置 | 说明 |
|------|----------|------|
| 禁用短密钥 | `HostKeyAlgorithms +ssh-ed25519` | 拒绝 RSA < 2048 |
| 禁用弱算法 | `Ciphers` 只保留现代加密 | 去掉 3des-cbc 等 |
| 双因素认证 | 配合 `pam_google_authenticator.so` | PAM 层的 2FA |
| 登录通知 | `pam_exec` 调用脚本 | 新登录通知管理员 |
| 端口敲门 | `knockd` 服务 | 隐藏 SSH 端口 |
| 限速 | iptables `-m recent` | 限制尝试频率 |

### SSH 证书认证（进阶）

比传统公钥认证更易管理的方案：

```bash
# 生成 CA 密钥
ssh-keygen -t ed25519 -f ~/ssh_ca

# 签发用户证书（有效期 24 小时）
ssh-keygen -s ~/ssh_ca -I user_id -n alice -V +24h ~/.ssh/id_ed25519.pub

# 在服务器上信任 CA（/etc/ssh/sshd_config）
TrustedUserCAKeys /etc/ssh/trusted_ca.pub

# 撤销证书
ssh-keygen -k -f /etc/ssh/revoked_keys ~/ssh_ca -u user_id.id_revoke
```

证书认证的优势：无需在每个服务器上配置 authorized_keys，集中管理证书的签发和吊销。

---

## 21.11 常见问题排查

```bash
# SSH 连接超时
ssh -v user@server # 查看调试输出
ping server_ip # 检查网络连通性
sudo ss -tlnp | grep 22 # 确认 sshd 监听

# 权限问题
ls -la ~/.ssh/ # 检查客户端权限
# 服务端日志
sudo journalctl -u sshd -f # systemd 系统
sudo tail -f /var/log/auth.log # Debian/Ubuntu
sudo tail -f /var/log/secure # RHEL/Fedora

# 密钥被拒绝
ssh -vvv user@server 2>&1 | grep -i "permission\|auth\|key"
ssh-keygen -y -f ~/.ssh/id_ed25519 # 从私钥提取公钥验证

# 加密算法不兼容
ssh -Q cipher # 列出支持的加密算法
ssh -Q mac # 列出支持的 MAC 算法
ssh -Q kex # 列出支持的密钥交换算法

# 主机密钥变更警告
# WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!
# 可能是正当的（服务器重装）也可能是 MITM 攻击
ssh-keygen -R hostname # 删除旧记录
# 联系管理员确认新的主机指纹
```

---

## 21.12 参考资源与关联章节

| 资源 | 说明 |
|------|------|
| `man ssh` | SSH 客户端手册 |
| `man sshd_config` | SSHD 配置选项 |
| `man ssh_config` | 客户端配置选项 |
| OpenSSH 官方 | https://www.openssh.com/ |

相关章节：
- [[24-防火墙与安全]] — 防火墙配置，SSH 端口访问控制
- [[28-系统安全加固与审计]] — 系统级安全加固，fail2ban 配置
- [[55-终端常用工具大全]] — tmux、screen 等终端工具详解
- [[13-网络配置基础]] — 网络基础知识

---

> **小结**：SSH 是 Linux 远程管理的核心协议。掌握密钥认证、config 配置、端口转发和 sshd 安全加固是每个系统管理员的基本功。生产环境中务必遵循最小权限原则：禁用密码登录、禁止 root 直连、限制可登录用户、使用 ed25519 密钥、定期审计 authorized_keys。
