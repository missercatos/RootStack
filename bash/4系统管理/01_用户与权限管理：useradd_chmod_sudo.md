# 用户与权限管理：useradd, chmod, sudo | User & Permission Management

## 章节概述

> **核心理念**：Linux 是多用户操作系统，用户和权限管理是系统安全的基石。理解 UID/GID、文件权限、sudo 机制和 ACL，就像理解 C 语言的访问控制——谁能读、谁能写、谁能执行，都必须精确控制。

---

### 第1节：用户管理命令

#### 1.1 useradd 创建用户

```bash
# 创建用户（默认设置）
sudo useradd username

# 创建用户并设置主目录
sudo useradd -m -s /bin/bash username

# 创建用户并指定 UID 和组
sudo useradd -m -u 1500 -g developers -s /bin/bash username

# 创建系统用户（无主目录，UID < 1000）
sudo useradd -r -s /usr/sbin/nologin serviceuser

# 设置密码
sudo passwd username
```

| 选项 | 说明 |
|------|------|
| `-m` | 创建主目录 |
| `-s` | 指定 shell |
| `-u` | 指定 UID |
| `-g` | 指定主组 |
| `-G` | 指定附加组 |
| `-e` | 账户过期日期 |
| `-c` | 用户注释 |
| `-r` | 创建系统用户 |

#### 1.2 usermod 修改用户

```bash
# 将用户添加到附加组
sudo usermod -aG sudo username

# 修改用户 shell
sudo usermod -s /bin/zsh username

# 锁定用户账户
sudo usermod -L username

# 解锁用户账户
sudo usermod -U username

# 修改用户名
sudo usermod -l newname oldname

# 设置账户过期
sudo usermod -e 2026-12-31 username
```

#### 1.3 userdel 删除用户

```bash
# 删除用户（保留主目录）
sudo userdel username

# 删除用户及其主目录
sudo userdel -r username

# 强制删除（即使用户在线）
sudo userdel -rf username
```

### 第2节：文件权限管理

#### 2.1 chmod 权限修改

```bash
# 符号模式
chmod u+x script.sh      # 所有者添加执行权限
chmod g-w file.txt       # 组用户移除写权限
chmod o=r file.txt       # 其他用户只读
chmod a+r file.txt       # 所有用户添加读权限

# 数字模式（八进制）
chmod 755 script.sh      # rwxr-xr-x
chmod 644 file.txt       # rw-r--r--
chmod 700 private.sh     # rwx------
chmod 600 secret.key     # rw-------

# 递归修改
chmod -R 755 /var/www/
```

| 权限 | 数字 | 说明 |
|------|------|------|
| `r` | 4 | 读取 |
| `w` | 2 | 写入 |
| `x` | 1 | 执行 |
| `-` | 0 | 无权限 |

#### 2.2 chown 所有权修改

```bash
# 修改所有者
sudo chown username file.txt

# 修改所有者和组
sudo chown username:groupname file.txt

# 递归修改
sudo chown -R www-data:www-data /var/www/

# 仅修改组
sudo chgrop groupname file.txt
```

### 第3节：sudo 配置

#### 3.1 /etc/sudoers 文件

```bash
# 编辑 sudoers 文件（必须使用 visudo）
sudo visudo

# 授予用户 sudo 权限
username ALL=(ALL:ALL) ALL

# 授予用户免密码 sudo
username ALL=(ALL) NOPASSWD: ALL

# 授予用户特定命令的 sudo 权限
username ALL=(ALL) /usr/bin/systemctl restart nginx, /usr/bin/tail -f /var/log/syslog

# 授予组 sudo 权限
%sudo ALL=(ALL:ALL) ALL

# 授予用户执行特定命令（不需要密码）
username ALL=(root) NOPASSWD: /usr/bin/apt-get update, /usr/bin/apt-get upgrade
```

#### 3.2 sudo 安全实践

```bash
# 查看用户 sudo 历史
sudo grep sudo /var/log/auth.log

# 查看当前用户的 sudo 权限
sudo -l

# 测试 sudo 配置
sudo -v

# 查看 sudo 日志
sudo journalctl _COMM=sudo
```

### 第4节：ACL（访问控制列表）

#### 4.1 ACL 基本操作

```bash
# 查看文件 ACL
getfacl file.txt

# 设置 ACL（给用户）
setfacl -m u:username:rwx file.txt

# 设置 ACL（给组）
setfacl -m g:groupname:rx file.txt

# 设置默认 ACL（对新文件生效）
setfacl -d -m g:groupname:rwx directory/

# 移除 ACL
setfacl -x u:username file.txt

# 移除所有 ACL
setfacl -b file.txt
```

#### 4.2 ACL 权限掩码

```bash
# ACL 掩码限制最大权限
getfacl file.txt
# 输出示例:
# user::rwx
# user:username:rwx    # 有效权限
# group::r-x
# mask::r-x            # 掩码（最大权限）
# other::r--

# 修改掩码
setfacl -m m::rwx file.txt
```

### 第5节：UID/GID 理解

#### 5.1 查看 UID/GID

```bash
# 查看当前用户信息
id
# 输出: uid=1000(username) gid=1000(username) groups=1000(username),27(sudo)

# 查看特定用户
id username

# 查看 UID 范围
cat /etc/login.defs | grep -E "^UID_|^GID_"

# UID 范围说明:
# 0:        root
# 1-999:    系统用户
# 1000+:    普通用户
```

#### 5.2 /etc/passwd 和 /etc/shadow

```bash
# /etc/passwd 格式
cat /etc/passwd
# username:x:1000:1000:Comment:/home/username:/bin/bash
# 字段: 用户名:密码占位:UID:GID:注释:主目录:Shell

# /etc/shadow（密码哈希，需要 root 权限）
sudo cat /etc/shadow
# username:$6$xxxx:19845:0:99999:7:::

# /etc/group
cat /etc/group
# groupname:x:GID:user1,user2,user3
```

### 第6节：批量用户管理

#### 6.1 批量创建用户

```bash
#!/bin/bash
# 从文件批量创建用户
while IFS=: read -r username fullname; do
    sudo useradd -m -c "$fullname" -s /bin/bash "$username"
    echo "$username:$(openssl rand -base64 12)" | sudo chpasswd
    echo "Created user: $username"
done < users.txt

# users.txt 格式:
# john:John Doe
# jane:Jane Smith
```

#### 6.2 用户信息收集

```bash
# 列出所有普通用户
awk -F: '$3 >= 1000 && $3 < 65534 {print $1, $3, $6, $7}' /etc/passwd

# 列出登录过的用户
lastlog | grep -v "Never logged in"

# 列出当前登录用户
who

# 列出所有组
getent group | awk -F: '$3 >= 1000 {print $1, $3}'
```
