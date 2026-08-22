# SQL Server 教程

SQL Server 是微软的商业关系型数据库，深度绑定 Windows 生态（Active Directory 认证、.NET 技术栈），同时也提供 Linux 版本和 Docker 镜像。对于有 C/C++ 基础的读者，它的 T-SQL 语法与 MySQL 有不少差异，本文聚焦这些差异点，帮助你快速上手。

---

## 一、安装

### 1.1 多平台安装方式一览

| 平台 | 方式 | 说明 |
|------|------|------|
| Windows | 安装向导（ISO / exe） | 图形化安装，可选实例、身份验证模式 |
| Linux (Debian/Ubuntu) | `apt` 仓库安装 | 官方 mssql-server 包 |
| Linux (RHEL/CentOS) | `yum/dnf` 仓库安装 | 同上 |
| Docker | `mcr.microsoft.com/mssql/server` 镜像 | 一行命令拉起，学习首选 |

### 1.2 Windows 安装向导

1. 下载 SQL Server 安装中心（Developer 版免费，功能与企业版一致）
2. 选择"全新 SQL Server 独立安装"，一路默认即可
3. 身份验证模式建议选择 **混合模式**，并设置 `sa` 密码
4. 再单独安装 SSMS（Management Studio）作为管理工具

### 1.3 Linux 安装（apt）

```bash
# Ubuntu 22.04 示例
curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg
curl -fsSL https://packages.microsoft.com/config/ubuntu/22.04/mssql-server-2022.list | sudo tee /etc/apt/sources.list.d/mssql.list

sudo apt-get update
sudo apt-get install -y mssql-server

# 设置 sa 密码并选择版本（选 Developer 即 2）
sudo /opt/mssql/bin/mssql-conf setup

# 启动服务
sudo systemctl enable --now mssql-server
```

### 1.4 Linux 安装（yum）

```bash
sudo curl -o /etc/yum.repos.d/mssql.repo \
    https://packages.microsoft.com/config/rhel/8/mssql-server-2022.repo

sudo dnf install -y mssql-server
sudo /opt/mssql/bin/mssql-conf setup
sudo systemctl enable --now mssql-server
```

### 1.5 Docker 安装（推荐学习用）

```bash
docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=YourStrong!Passw0rd" \
    -p 1433:1433 --name mssql \
    -d mcr.microsoft.com/mssql/server:2022-latest
```

> 注意：SA 密码必须包含大小写字母、数字、符号且至少 8 位，否则容器启动即失败。

---

## 二、连接工具

| 工具 | 平台 | 特点 |
|------|------|------|
| SSMS（SQL Server Management Studio） | 仅 Windows | 官方全功能图形工具，DBA 标配 |
| sqlcmd | 全平台 | 命令行客户端，脚本化操作必备 |
| Azure Data Studio | 全平台 | 跨平台图形工具，轻量现代 |
| Visual Studio / VS Code 扩展 | 全平台 | 开发调试集成 |

### 2.1 sqlcmd 基本用法

```bash
# 本机连接（Windows 默认实例）
sqlcmd -S localhost -U sa -P 'YourStrong!Passw0rd'

# 连接指定端口（Docker 场景常见）
sqlcmd -S localhost,1433 -U sa -P 'YourStrong!Passw0rd'

# 直接执行 SQL 并退出
sqlcmd -S localhost -U sa -P 'YourStrong!Passw0rd' \
    -Q "SELECT @@VERSION"
```

进入交互模式后：

```sql
-- 每条语句以 GO 结尾提交执行
SELECT name FROM sys.databases;
GO

USE master;
GO

:quit   -- 或 exit 退出
```

> sqlcmd 中 `GO` 不是 SQL 语句，而是批处理分隔符；`;` 是语句结束符。二者职责不同。

---

## 三、T-SQL 特有语法速查

从 MySQL 迁移过来的开发者最容易踩坑的地方集中在这里：

| 功能 | MySQL 写法 | SQL Server (T-SQL) 写法 |
|------|-----------|------------------------|
| 取前 N 行 | `SELECT * FROM t LIMIT 10` | `SELECT TOP 10 * FROM t` |
| 自增主键 | `AUTO_INCREMENT` | `IDENTITY(1,1)` |
| 当前时间 | `NOW()` | `GETDATE()` |
| 判空替换 | `IFNULL(a, b)` | `ISNULL(a, b)` |
| 标识符引用 | 反引号 `` `name` `` | 方括号 `[name]` |
| 定义变量 | 少见 | `DECLARE @x INT; SET @x = 1;` |
| 打印输出 | 无对应 | `PRINT 'hello'` |
| 字符串连接 | `CONCAT()` / `||` | `+` 或 `CONCAT()` |
| 字符串长度 | `LENGTH()` | `LEN()` |

### 3.1 TOP 与分页基础

```sql
-- 前 5 行
SELECT TOP 5 * FROM employees ORDER BY salary DESC;

-- 前 20%（按比例）
SELECT TOP 20 PERCENT * FROM employees;

-- TOP ... WITH TIES：并列名次一并返回
SELECT TOP 5 WITH TIES * FROM employees ORDER BY salary DESC;
```

### 3.2 IDENTITY 自增列

```sql
CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,  -- 从 1 开始，每次 +1
    name NVARCHAR(50) NOT NULL,
    created DATETIME2 DEFAULT GETDATE()
);

-- 插入时不能给 IDENTITY 列赋值
INSERT INTO users (name) VALUES (N'张三');

-- 查询最近生成的自增值（类比 MySQL 的 LAST_INSERT_ID()）
SELECT @@IDENTITY;
SELECT SCOPE_IDENTITY();   -- 推荐：只取当前作用域的值
```

### 3.3 方括号标识符

当表名或列名与保留字冲突、或含空格/特殊字符时用方括号包裹：

```sql
SELECT [order], [user name] FROM [my table];
```

等价于标准 SQL 的双引号 `"order"`。方括号是 T-SQL 的方言写法。

### 3.4 变量与 PRINT

```sql
DECLARE @count INT;
DECLARE @name NVARCHAR(50);

SET @count = 100;
SET @name = N'SQL Server';

PRINT N'当前用户数：' + CAST(@count AS NVARCHAR(10));
SELECT @name AS db_name;

-- DECLARE + SET 可以合并为一条（SQL Server 2008+）
DECLARE @x INT = 42;
```

> `N''` 前缀表示 Unicode 字符串，存中文必须加，否则可能变成问号。

---

## 四、系统数据库

安装完成后自带 4 个系统库，各有分工：

| 系统库 | 作用 |
|--------|------|
| master | 存放所有数据库的元数据（登录账号、链接服务器、系统配置）。损坏则整个实例无法启动 |
| model | 新建数据库的模板。新库的所有初始设置都复制自它 |
| msdb | SQL Server Agent 的后台数据：定时任务、备份历史、作业调度 |
| tempdb | 临时表、排序中间结果、版本存储。重启即清空，性能调优重点对象 |

```sql
SELECT name, database_id, create_date FROM sys.databases;
```

---

## 五、系统视图与元数据查询

### 5.1 目录视图（sys.*）

```sql
-- 查看所有数据库
SELECT name FROM sys.databases;

-- 查看当前库所有表
SELECT name, create_date FROM sys.tables WHERE type = 'U';

-- 查看某张表的列信息
SELECT name, type_name(system_type_id) AS data_type, max_length
FROM sys.columns
WHERE object_id = OBJECT_ID('dbo.users');
```

### 5.2 INFORMATION_SCHEMA（跨平台标准）

```sql
-- 与 MySQL 兼容的写法，可移植性更好
SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE';

SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'users';
```

日常排查优先记这两套：`sys.*` 功能全但绑定 SQL Server；`INFORMATION_SCHEMA.*` 在 MySQL/PostgreSQL 里也通用。

---

## 六、存储过程入门

存储过程是预编译存放在数据库中的 SQL 集合，类似"数据库里的函数"。适合封装复杂业务、减少网络往返。

```sql
CREATE PROCEDURE dbo.usp_get_employees_by_salary
    @minSalary DECIMAL(10,2),          -- 输入参数
    @maxSalary DECIMAL(10,2),
    @count INT OUTPUT                  -- 输出参数
AS
BEGIN
    SET NOCOUNT ON;                    -- 不返回受影响行数消息

    SELECT id, name, salary
    FROM employees
    WHERE salary BETWEEN @minSalary AND @maxSalary
    ORDER BY salary DESC;

    SELECT @count = COUNT(*)
    FROM employees
    WHERE salary BETWEEN @minSalary AND @maxSalary;
END;
GO
```

调用方式：

```sql
-- 普通 EXEC 调用
EXEC dbo.usp_get_employees_by_salary @minSalary = 5000, @maxSalary = 20000;

-- 接收 OUTPUT 参数
DECLARE @n INT;
EXEC dbo.usp_get_employees_by_salary
    @minSalary = 5000,
    @maxSalary = 20000,
    @count = @n OUTPUT;
PRINT N'符合条件人数：' + CAST(@n AS NVARCHAR(10));

-- 删除存储过程
DROP PROCEDURE dbo.usp_get_employees_by_salary;
```

命名惯例：前缀 `usp_`（user stored procedure），避免与系统过程 `sp_` 混淆——`sp_` 前缀会触发额外的查找开销。

---

## 七、分页：OFFSET FETCH

SQL Server 2012 起支持标准分页语法，**必须配合 ORDER BY** 使用：

```sql
-- 第 3 页，每页 20 条（跳过前 40 行取 20 行）
SELECT id, name, salary
FROM employees
ORDER BY id
OFFSET 40 ROWS FETCH NEXT 20 ROWS ONLY;
```

老版本的经典写法是 `ROW_NUMBER()` 窗口函数模拟：

```sql
WITH paged AS (
    SELECT id, name, salary,
           ROW_NUMBER() OVER (ORDER BY id) AS rn
    FROM employees
)
SELECT id, name, salary FROM paged
WHERE rn BETWEEN 41 AND 60;
```

对比记忆：

| 数据库 | 分页写法 |
|--------|---------|
| MySQL | `LIMIT 40, 20` |
| PostgreSQL | `LIMIT 20 OFFSET 40` |
| SQL Server | `OFFSET 40 ROWS FETCH NEXT 20 ROWS ONLY` |

---

## 八、备份与恢复

### 8.1 BACKUP DATABASE

```sql
-- 完整备份
BACKUP DATABASE mydb
TO DISK = 'D:\backup\mydb.bak'
WITH INIT, COMPRESSION;

-- 差异备份（只备份自上次完整备份后的变化）
BACKUP DATABASE mydb
TO DISK = 'D:\backup\mydb_diff.bak'
WITH DIFFERENTIAL;

-- 日志备份（要求恢复模式为 FULL）
BACKUP LOG mydb TO DISK = 'D:\backup\mydb.trn';
```

Linux 下路径形如 `/var/opt/mssql/backup/mydb.bak`。

### 8.2 RESTORE DATABASE

```sql
-- 从完整备份恢复
RESTORE DATABASE mydb
FROM DISK = 'D:\backup\mydb.bak'
WITH RECOVERY;      -- 恢复后立即可用

-- 先恢复完整备份，再追加差异备份
RESTORE DATABASE mydb
FROM DISK = 'D:\backup\mydb.bak'
WITH NORECOVERY;    -- 保持恢复中状态，等待后续日志

RESTORE DATABASE mydb
FROM DISK = 'D:\backup\mydb_diff.bak'
WITH RECOVERY;
```

命令行下也可以直接用 sqlcmd 执行上述语句完成定时备份脚本。

---

## 九、速查卡

| 分类 | 关键点 |
|------|--------|
| 取前 N 行 | `TOP N`（不是 LIMIT） |
| 自增 | `IDENTITY(1,1)`，取值用 `SCOPE_IDENTITY()` |
| 当前时间 | `GETDATE()` |
| 判空 | `ISNULL(col, default)` |
| 标识符 | 方括号 `[order]` |
| 中文常量 | 加 `N` 前缀：`N'中文'` |
| 元数据 | `sys.tables` / `INFORMATION_SCHEMA.TABLES` |
| 分页 | `ORDER BY ... OFFSET n ROWS FETCH NEXT m ROWS ONLY` |
| 备份恢复 | `BACKUP DATABASE ... TO DISK` / `RESTORE DATABASE ... FROM DISK` |
| 批处理 | sqlcmd 中以 `GO` 分隔提交 |

---

**返回** [[../数据库目录|数据库目录]]
