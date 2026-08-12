# SELinux 深入

> SELinux (Security-Enhanced Linux) 是 RHEL 系发行版默认的强制访问控制 (MAC) 系统，由 NSA 开发。本章深入 SELinux 架构、策略管理、排错工作流、audit2allow 策略生成和与 AppArmor 的对比。

---

## 1. 资源链接

| 资源 | 链接 |
|------|------|
| SELinux 项目 | https://selinuxproject.org/ |
| Red Hat SELinux 文档 | https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html/using_selinux/ |
| SELinux Wiki | https://selinuxproject.org/page/Main_Page |
| 清华镜像 | https://mirrors.tuna.tsinghua.edu.cn/centos/ |

---

## 2. SELinux 架构原理

### 2.1 MAC vs DAC

```
DAC (自主访问控制)：传统 Linux 权限 (rwx)
 — 文件所有者决定访问权限
 — root 可以绕过一切

MAC (强制访问控制)：SELinux
 — 系统管理员定义全局安全策略
 — root 也受策略限制
 — SELinux 在 DAC 之后检查（两层防护）

访问决策流程：
 进程 → [DAC 检查] → 通过 → [SELinux 检查] → 通过 → 允许访问
```

### 2.2 核心概念

| 概念 | 说明 | 示例 |
|------|------|------|
| **类型 (Type)** | 文件、进程的安全类型标签 | `httpd_t`, `httpd_sys_content_t` |
| **域 (Domain)** | 进程的 SELinux 上下文 | `system_u:system_r:httpd_t:s0` 中的 `httpd_t` |
| **角色 (Role)** | 用户角色 | `system_r`, `staff_r`, `user_r` |
| **用户 (User)** | SELinux 用户 | `system_u`, `unconfined_u` |
| **级别 (Level)** | MLS/MCS 安全级别 | `s0`, `s0:c0.c1023` |
| **上下文 (Context)** | 完整安全标签 | `unconfined_u:object_r:httpd_sys_content_t:s0` |
| **策略 (Policy)** | 定义所有允许规则的集合 | targeted, mls, minimum |
| **布尔值 (Boolean)** | 运行时策略开关 | `httpd_can_network_connect` |

### 2.3 SELinux 上下文格式

```
用户:角色:类型:级别

示例：
system_u:system_r:httpd_t:s0 ← httpd 进程上下文
unconfined_u:object_r:httpd_sys_content_t:s0 ← Web 文件上下文
```

### 2.4 策略类型

| 策略 | 说明 | 适用场景 |
|------|------|---------|
| `targeted` | 只限制关键服务进程 | 默认（推荐） |
| `mls` | 多级别安全 | 军事/政府机密系统 |
| `minimum` | 最小限制（类似 targeted 但更少规则） | 嵌入式/轻量 |

```bash
# 查看当前策略
sestatus | grep "Loaded policy name"
```

---

## 3. SELinux 模式

### 3.1 三种模式

| 模式 | 说明 | 日志 |
|------|------|------|
| **enforcing** | 强制执行策略，拒绝违规操作并记录 | |
| **permissive** | 不强制，但记录违规操作（调试用） | |
| **disabled** | 完全关闭 SELinux | |

```bash
# 查看当前模式
getenforce

# 查看完整状态
sestatus

# 临时切换模式（重启失效）
sudo setenforce 0 # permissive
sudo setenforce 1 # enforcing

# 永久配置
sudo vim /etc/selinux/config
```

```
SELINUX=enforcing
# SELINUX=permissive
# SELINUX=disabled ← 不推荐
SELINUXTYPE=targeted
```

### 3.2 从 disabled 启用

```bash
# 注意：从 disabled 切换到 enforcing 需要重启并重新标记文件系统！

# 1. 编辑 /etc/selinux/config: SELINUX=permissive
# 2. 重启
# 3. 检查没有错误后，改为 SELINUX=enforcing
# 4. 再次重启
```

---

## 4. 上下文管理

### 4.1 查看上下文

```bash
# 查看进程上下文
ps -eZ
ps auxZ | grep httpd

# 查看文件上下文
ls -Z /var/www/html/
ls -lZ /usr/sbin/httpd

# 查看端口上下文
sudo semanage port -l
sudo semanage port -l | grep http

# 查看用户上下文
id -Z

# 查看当前用户的 SELinux 上下文
seinfo -u
semanage user -l
```

### 4.2 修改文件上下文

```bash
# chcon — 临时修改上下文（重置会丢失）
sudo chcon -t httpd_sys_content_t /var/www/html/index.html
sudo chcon -R -t httpd_sys_content_t /var/www/mysite/
sudo chcon -R --reference /var/www/html /var/www/mysite

# restorecon — 恢复到默认上下文
sudo restorecon -v /var/www/html/index.html
sudo restorecon -Rv /var/www/mysite/

# 永久默认上下文规则
sudo semanage fcontext -a -t httpd_sys_content_t "/var/www/mysite(/.*)?"
sudo restorecon -Rv /var/www/mysite/

# 列出所有 fcontext 规则
sudo semanage fcontext -l
sudo semanage fcontext -l | grep httpd

# 删除自定义规则
sudo semanage fcontext -d -t httpd_sys_content_t "/var/www/mysite(/.*)?"
```

### 4.3 端口上下文

```bash
# 列出端口类型
sudo semanage port -l

# 添加端口到指定类型（如让 SSH 监听 2222）
sudo semanage port -a -t ssh_port_t -p tcp 2222

# 修改端口类型
sudo semanage port -m -t http_port_t -p tcp 8080

# 删除端口
sudo semanage port -d -t ssh_port_t -p tcp 2222
```

### 4.4 网络相关上下文

```bash
# 允许服务使用特定端口
sudo semanage port -a -t http_port_t -p tcp 8084

# 查看布尔值
sudo semanage boolean -l | grep httpd
```

---

## 5. SELinux 布尔值

### 5.1 查看和设置布尔值

```bash
# 列出所有布尔值
getsebool -a

# 列出特定服务的布尔值
getsebool -a | grep httpd
getsebool -a | grep nis
getsebool -a | grep virt

# 查看布尔值详情
semanage boolean -l | grep httpd_can_network_connect

# 临时设置
sudo setsebool httpd_can_network_connect on

# 永久设置
sudo setsebool -P httpd_can_network_connect on

# 重置为默认
sudo setsebool httpd_can_network_connect off
```

### 5.2 常用布尔值

| 布尔值 | 作用 |
|--------|------|
| `httpd_can_network_connect` | 允许 httpd 连接网络（反向代理必须） |
| `httpd_can_sendmail` | 允许 httpd 发送邮件 |
| `httpd_enable_cgi` | 允许 httpd CGI 脚本 |
| `named_write_master_zones` | 允许 named 更新主区域文件 |
| `nfs_export_all_ro` | 允许 NFS 导出只读 |
| `nfs_export_all_rw` | 允许 NFS 导出读写 |
| `samba_enable_home_dirs` | 允许 Samba 共享家目录 |
| `virt_use_nfs` | 允许 KVM 使用 NFS 存储 |
| `ssh_sysadm_login` | 允许 root SSH 登录（enforcing 下） |
| `use_nfs_home_dirs` | 允许 NFS 挂载家目录 |
| `selinuxuser_execmod` | 允许在用户家目录执行可写文件 |
| `domain_kernel_load_modules` | 允许内核模块加载 |

---

## 6. SELinux 排错工作流

### 6.1 标准排错步骤

```
1. 确认问题 → 日志显示 "SELinux is preventing..."
2. 查看审计日志 → ausearch -m avc -ts recent
3. 分析 AVC 拒绝 → sealert -a /var/log/audit/audit.log
4. 找到解决方案 → audit2allow 或 manual fix
5. 临时测试 → setenforce 0 确认问题
6. 永久修复 → semanage, setsebool, 或自定义策略
```

### 6.2 查看 SELinux 拒绝

```bash
# AVC (Access Vector Cache) 拒绝记录
sudo ausearch -m avc -ts today
sudo ausearch -m avc -ts recent
sudo ausearch -m avc -ts today | grep denied

# 查看 audit 日志
sudo tail -f /var/log/audit/audit.log | grep AVC

# 使用 sealert 分析（推荐）
sudo sealert -a /var/log/audit/audit.log

# 查看特定应用的拒绝
sudo ausearch -m avc -ts today -c httpd
sudo ausearch -m avc -ts recent | grep httpd_t
```

### 6.3 理解 AVC 拒绝消息

```
type=AVC msg=audit(1705312345.678:1234): avc: denied { read } for \
 pid=12345 comm="httpd" name="index.html" dev="sda1" ino=56789 \
 scontext=system_u:system_r:httpd_t:s0 \
 tcontext=unconfined_u:object_r:user_home_t:s0 \
 tclass=file

解读：
- 进程 httpd (httpd_t 域) 试图读取文件 index.html (user_home_t 类型)
- httpd_t 没有读取 user_home_t 的权限
```

### 6.4 临时测试（permissive 域）

```bash
# 只将特定域设为 permissive（不关闭全局 SELinux）
sudo semanage permissive -a httpd_t

# 查看所有 permissive 域
sudo semanage permissive -l

# 取消 permissive
sudo semanage permissive -d httpd_t

# permissive 域的好处：
# - 只让它记录的违规操作，但仍允许执行
# - 收集 audit 日志用于 audit2allow 分析
# - 不影响其他域的安全策略
```

---

## 7. audit2allow —— 策略生成

### 7.1 基本使用

```bash
# 从审计日志生成允许规则
sudo audit2allow -a

# 生成可编译的 Type Enforcement 文件
sudo audit2allow -a -M mypolicy

# 这会生成两个文件：
# mypolicy.te — Type Enforcement (策略源文件)
# mypolicy.pp — 编译好的策略模块

# 安装策略模块
sudo semodule -i mypolicy.pp

# 查看更详细的分析
sudo audit2allow -a -w # 解释为什么拒绝
sudo audit2allow -a -v # 详细输出
```

### 7.2 完整工作流

```bash
# 1. 先将目标域设为 permissive
sudo semanage permissive -a httpd_t

# 2. 重试导致问题的操作（触发 AVC 拒绝）
# ...

# 3. 从审计日志生成策略
sudo ausearch -m avc -ts recent | audit2allow -M custom_httpd

# 4. 查看生成的策略
cat custom_httpd.te
```

```
# custom_httpd.te
module custom_httpd 1.0;

require {
 type httpd_t;
 type user_home_t;
 class file { read open getattr };
}

#============= httpd_t ==============
allow httpd_t user_home_t:file { read open getattr };
```

```bash
# 5. review 生成的规则（确保合理，不要直接允许过于宽泛的权限）
vim custom_httpd.te

# 6. 编译并安装
sudo semodule -i custom_httpd.pp

# 7. 恢复域为 enforcing
sudo semanage permissive -d httpd_t
```

### 7.3 audit2allow 安全审查

```bash
# 不要盲目用 audit2allow 生成策略！
# 应审查每个生成的规则：
#
# - 是否真的需要这个权限？
# - 能否用布尔值替代？
# - 能否用文件上下文替代？
# - allow 的权限是否过于宽泛？
#
# 更好的方式是：
# 1. 用布尔值：setsebool -P httpd_enable_homedirs on
# 2. 用上下文：semanage fcontext + restorecon
# 3. 最后手段：自定义策略模块
```

---

## 8. 策略管理

### 8.1 semodule 命令

```bash
# 列出已安装的策略模块
sudo semodule -l
sudo semodule --list-modules=full

# 安装策略模块
sudo semodule -i mypolicy.pp

# 删除策略模块
sudo semodule -r mypolicy

# 启用/禁用模块
sudo semodule -e mypolicy # 启用
sudo semodule -d mypolicy # 禁用

# 升级/替换模块
sudo semodule -u mypolicy.pp

# 查看模块详情
sudo semodule --list-modules=full | grep mypolicy
```

### 8.2 semanage 完整用法

```bash
# 管理端口类型
semanage port -l
semanage port -a -t http_port_t -p tcp 8080
semanage port -d -t http_port_t -p tcp 8080

# 管理文件上下文
semanage fcontext -l
semanage fcontext -a -t httpd_sys_content_t "/web(/.*)?"
semanage fcontext -d -t httpd_sys_content_t "/web(/.*)?"

# 管理布尔值
semanage boolean -l

# 管理 permissive 域
semanage permissive -a httpd_t
semanage permissive -d httpd_t

# 管理 SELinux 用户
semanage user -l

# 管理 SELinux 登录
semanage login -l

# 管理网络接口
semanage interface -l

# 管理节点
semanage node -l
```

---

## 9. SELinux 常见问题与解决

### 9.1 Web 服务器问题

```bash
# 问题：Apache/Nginx 无法读取非标准目录的文件
ls -lZ /var/www/custom/
# 类型是 default_t，不是 httpd_sys_content_t

# 解决：
sudo semanage fcontext -a -t httpd_sys_content_t "/var/www/custom(/.*)?"
sudo restorecon -Rv /var/www/custom/

# 问题：Apache 作为反向代理需要连接后端
sudo setsebool -P httpd_can_network_connect on

# 问题：PHP/Python 需要执行写操作
sudo setsebool -P httpd_unified on
sudo chcon -t httpd_sys_rw_content_t /var/www/app/data/
```

### 9.2 数据库问题

```bash
# 问题：MariaDB/MySQL 自定义数据目录
ls -lZ /data/mysql/
# 类型不是 mysqld_db_t

# 解决：
sudo semanage fcontext -a -t mysqld_db_t "/data/mysql(/.*)?"
sudo restorecon -Rv /data/mysql/

# MySQL 允许网络连接（主从复制）
sudo setsebool -P mysqld_disable_trans on
```

### 9.3 SSH 问题

```bash
# 问题：更改 SSH 端口后无法连接
# 解决：
sudo semanage port -a -t ssh_port_t -p tcp 2222

# 问题：使用非标准位置存放 authorized_keys
sudo semanage fcontext -a -t ssh_home_t "/home/%{USER}/.ssh/authorized_keys"
```

### 9.4 容器问题

```bash
# 问题：容器文件类型不对
# 容器文件应标记为 container_file_t
sudo semanage fcontext -a -t container_file_t "/var/lib/containers(/.*)?"
sudo restorecon -Rv /var/lib/containers/

# 允许容器使用 NFS
sudo setsebool -P virt_use_nfs on
```

### 9.5 文件重定位问题

```bash
# 问题：使用 mv 移动文件保留了原上下文
# 解决：cp 保留上下文，mv 不保留
# 用 cp 替换 mv 移动带 SELinux 上下文的文件
cp /source/file /dest/
# 而非 mv /source/file /dest/

# 如果已经移动，手动修复
sudo restorecon -v /dest/file
```

---

## 10. SELinux vs AppArmor

| 特性 | SELinux | AppArmor |
|------|---------|----------|
| 控制粒度 | 基于类型/域（细粒度） | 基于路径（粗粒度） |
| 默认策略 | 全部拒绝，显式允许 | 基于配置文件白名单 |
| 配置文件 | 编译后的二进制策略 | 文本文件 |
| 用户友好 | 较复杂 | 较简单 |
| 主要使用者 | RHEL/CentOS/Fedora | Debian/Ubuntu/openSUSE |
| 强制访问控制 | (MAC) | (MAC) |
| 多级安全 (MLS) | | |
| 网络标签 | | 有限 |
| RBAC | | |
| 学习模式 | permissive | complain |

```bash
# AppArmor 快速参考 (Debian/Ubuntu 默认)
sudo aa-status # 查看状态
sudo aa-enforce /etc/apparmor.d/usr.bin.nginx # 强制
sudo aa-complain /etc/apparmor.d/usr.bin.nginx # 学习（类似 permissive）
sudo aa-genprof /usr/sbin/nginx # 生成策略

# vs SELinux
getenforce # 查看模式
sudo setenforce 0 # permissive
semanage permissive -a httpd_t # 域级 permissive
```

---

## 11. 相关资源

- SELinux Wiki: https://selinuxproject.org/
- SELinux Project: https://github.com/SELinuxProject
- Red Hat SELinux 指南: https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html/using_selinux/
- setroubleshoot: https://github.com/fedora-selinux/setroubleshoot
- [[../redhat/02-RHEL-CentOS安装与配置|RHEL 安装与配置]]
- [[../redhat/05-firewalld与nmcli|firewalld 与 nmcli]]
- [[../debian/02-Debian安装与服务器配置|Debian 安装（含 AppArmor）]]
