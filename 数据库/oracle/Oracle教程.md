# Oracle 教程

Oracle Database 是最老牌的企业级商业数据库，银行、电信、证券等对稳定性和事务要求极高的行业主力选型。它的架构概念比 MySQL 复杂，SQL 方言（PL/SQL）也自成一体。本文以最小可用路径带你上手。

---

## 一、核心架构概念

先建立一张概念地图，后面所有内容都围绕它展开：

| 概念 | 一句话解释 |
|------|-----------|
| 实例（Instance） | 内存结构 + 后台进程的集合，是"运行中的数据库服务" |
| 数据库（Database） | 磁盘上的物理文件集合（数据文件、控制文件、日志文件）。实例打开数据库，二者常被混称但并不等同 |
| 表空间（Tablespace） | 逻辑存储单元，一个库由多个表空间组成；表建立在某个表空间上 |
| 段（Segment） | 表空间内分配给某个对象（如表/索引）的空间 |
| 区（Extent） | 段由若干连续数据块组成的区构成 |
| 块（Block） | 最小 I/O 单位（默认 8KB），类比文件系统的扇区之上的一层 |
| SGA | System Global Area：实例级共享内存（数据缓冲、日志缓冲、共享池），所有进程共用 |
| PGA | Program Global Area：每个服务器进程私有的内存（排序区、游标区），互不可见 |

用 C 的视角类比：SGA 是进程间共享的一段 `mmap` 共享内存，PGA 相当于每个线程的线程栈。

---

## 二、安装方式

Oracle 正式版收费且安装重，学习阶段两条路：

| 方式 | 说明 |
|------|------|
| Oracle XE（Express Edition） | 官方免费版，限制 CPU/内存/容量但对学习完全够用 |
| Docker 镜像 | `container-registry.oracle.com/database/free` 或 `gvenzl/oracle-free` |

```bash
docker run -d --name oracle-free \
    -p 1521:1521 \
    -e ORACLE_PWD=Oracle123 \
    gvenzl/oracle-free
```

> XE 默认提供一个 PDB（可插拔数据库）名为 `FREEPDB`，连接时服务名填它。

---

## 三、sqlplus 连接与基本命令

sqlplus 是 Oracle 自带的命令行客户端：

```bash
# 本机登录
sqlplus system/Oracle123@localhost:1521/FREEPDB

# 以 SYSDBA 身份登录（管理操作必须）
sqlplus / as sysdba
```

交互模式常用命令：

| 命令 | 作用 |
|------|------|
| `CONNECT user/password@host:port/service` | 切换连接（可简写 `CONN`） |
| `SHOW USER` | 显示当前登录用户 |
| `DESC table_name` | 查看表结构（describe） |
| `SELECT * FROM tab;` | 列出当前用户的表 |
| `SET LINESIZE 200` | 设置行宽，防止换行错乱 |
| `SET PAGESIZE 100` | 设置每页行数 |
| `/` | 重新执行上一条 SQL |
| `EXIT` | 退出 |

注意：sqlplus 中 SQL 语句以 **分号** 结尾执行，单独一行输入 `/` 可重复上一条语句。

---

## 四、dual 表

Oracle 的 SELECT 必须带 FROM 子句，没有 MySQL 里"无表查询"的自由。为此系统内置了一张只有一行一列的哑表 `dual`：

```sql
-- 计算表达式、测试函数、查看序列值的标配写法
SELECT 1 FROM dual;
SELECT SYSDATE FROM dual;
SELECT UPPER('hello') FROM dual;

-- 结果恒为一行：
DUMMY
-----
X
```

任何只算一个值的需求都挂在 `FROM dual` 上，这是 Oracle 与其他数据库最直观的差异之一。

---

## 五、数据类型

| 类型 | 说明 | 对应 C 直觉 |
|------|------|------------|
| VARCHAR2(n) | 变长字符串，n 为最大字节或字符数（推荐 `VARCHAR2(50 CHAR)`） | `char[]` 但带长度 |
| NUMBER(p, s) | 定点数，p 总精度最大 38 位，s 小数位。整数直接 `NUMBER` | 无固定对应，类似任意精度 |
| DATE | 日期 + 时间（精确到秒） | struct tm |
| TIMESTAMP | 时间戳，默认精确到小数点后 6 位秒 | 高精度 time_t |
| CLOB | 大文本，最大 4GB+ | 长 string |
| BLOB | 二进制大对象，存图片/文件 | void* buffer |
| CHAR(n) | 定长字符串，不足补空格 | 固定长度数组 |

```sql
CREATE TABLE employees (
    id       NUMBER PRIMARY KEY,
    name     VARCHAR2(50 CHAR) NOT NULL,
    salary   NUMBER(10, 2),
    hired_at DATE DEFAULT SYSDATE,
    resume   CLOB
);
```

---

## 六、序列 SEQUENCE

Oracle 没有自增列语法（12c 之前），主键自增靠**序列**对象：

```sql
-- 创建序列
CREATE SEQUENCE emp_seq
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;

-- 取下一个值（会推进序列）
SELECT emp_seq.NEXTVAL FROM dual;

-- 查看当前值（本会话至少取过一次后才能查）
SELECT emp_seq.CURRVAL FROM dual;

-- 典型用法：插入时生成主键
INSERT INTO employees (id, name, salary)
VALUES (emp_seq.NEXTVAL, '张三', 15000);
```

要点：

| 写法 | 说明 |
|------|------|
| `NEXTVAL` | 推进并返回新值 |
| `CURRVAL` | 返回当前会话最近一次 NEXTVAL 的值 |
| CACHE n | 预取 n 个值到内存提升性能，代价是宕机可能跳号 |
| 12c+ | 支持 `GENERATED AS IDENTITY` 列，接近 MySQL 自增体验 |

```sql
-- 12c+ 现代写法
CREATE TABLE t (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR2(50)
);
```

---

## 七、用户与权限

Oracle 权限体系围绕"角色"展开：

| 角色 | 包含能力 |
|------|---------|
| CONNECT | 最基础登录权限（CREATE SESSION） |
| RESOURCE | 开发者常用：建表、建序列、建过程等 |
| DBA | 全部系统权限，管理员专用，慎授 |

```sql
-- 用管理员创建用户（12c+ 在 CDB 中需加 c## 前缀，PDB 内不需要）
CREATE USER app_user IDENTIFIED BY AppPass123;

-- 授予开发所需角色
GRANT CONNECT, RESOURCE TO app_user;

-- 授权访问别的用户的表（跨 schema）
GRANT SELECT ON hr.employees TO app_user;

-- 收回权限
REVOKE RESOURCE FROM app_user;

-- 锁定 / 解锁账号
ALTER USER app_user ACCOUNT LOCK;
ALTER USER app_user ACCOUNT UNLOCK;
```

Oracle 中每个用户即一个 schema，`user.table` 类似 MySQL 的 `database.table`。

---

## 八、PL/SQL 基础

PL/SQL 是 Oracle 的过程化扩展，基本骨架是匿名块：

```sql
SET SERVEROUTPUT ON   -- 开启输出，否则 dbms_output 不显示

DECLARE               -- 声明区（可选）：变量、常量、游标
    v_name VARCHAR2(50) := '张三';
    v_salary NUMBER := 12000;
BEGIN                 -- 执行体（必须有）
    IF v_salary > 10000 THEN
        DBMS_OUTPUT.PUT_LINE(v_name || ' 属于高薪');
    ELSE
        DBMS_OUTPUT.PUT_LINE(v_name || ' 属于普通薪资');
    END IF;
END;
/
```

### 8.1 循环

```sql
DECLARE
    i NUMBER := 0;
BEGIN
    LOOP
        i := i + 1;
        EXIT WHEN i >= 5;         -- 退出条件
        DBMS_OUTPUT.PUT_LINE('i = ' || i);
    END LOOP;
END;
/
```

也有 `WHILE ... LOOP ... END LOOP;` 和 `FOR i IN 1..5 LOOP ... END LOOP;` 两种形式。

### 8.2 游标 CURSOR 最小示例

游标用于逐行处理查询结果，相当于结果集上的迭代器：

```sql
DECLARE
    CURSOR c_emp IS
        SELECT name, salary FROM employees WHERE salary > 8000;
    v_name employees.name%TYPE;      -- %TYPE 自动跟随列类型
    v_sal  employees.salary%TYPE;
BEGIN
    OPEN c_emp;
    LOOP
        FETCH c_emp INTO v_name, v_sal;
        EXIT WHEN c_emp%NOTFOUND;
        DBMS_OUTPUT.PUT_LINE(v_name || ' : ' || v_sal);
    END LOOP;
    CLOSE c_emp;
END;
/
```

更简洁的 FOR 游标自动完成 open/fetch/close：

```sql
BEGIN
    FOR r IN (SELECT name, salary FROM employees) LOOP
        DBMS_OUTPUT.PUT_LINE(r.name || ' : ' || r.salary);
    END LOOP;
END;
/
```

---

## 九、分页：ROWNUM 与 ROW_NUMBER

### 9.1 ROWNUM 经典三层写法

ROWNUM 是结果集的行号，在排序**之前**就已分配，所以直接 `WHERE ROWNUM > 10` 永远查不到数据。标准分页要套三层：

```sql
-- 第 3 页，每页 20 行
SELECT id, name, salary
FROM (
    SELECT t.*, ROWNUM rn
    FROM (
        SELECT id, name, salary
        FROM employees
        ORDER BY id
    ) t
    WHERE ROWNUM <= 60      -- 先截断前 60 行
)
WHERE rn > 40;              -- 再滤掉前 40 行
```

### 9.2 OFFSET 现代写法（12c+）

```sql
SELECT id, name, salary
FROM employees
ORDER BY id
OFFSET 40 ROWS FETCH NEXT 20 ROWS ONLY;
```

### 9.3 ROW_NUMBER() 窗口函数

```sql
SELECT * FROM (
    SELECT id, name, salary,
           ROW_NUMBER() OVER (ORDER BY salary DESC) AS rk
    FROM employees
) WHERE rk BETWEEN 41 AND 60;
```

---

## 十、数据字典

Oracle 的元数据视图分三个层级：

| 视图前缀 | 可见范围 |
|----------|---------|
| `USER_*` | 当前用户自己拥有的对象 |
| `ALL_*` | 当前用户可访问的所有对象（含被授权的他人对象） |
| `DBA_*` | 整个数据库全部对象（需要 DBA 权限） |

```sql
-- 我有哪些表
SELECT table_name FROM user_tables;

-- 我能访问哪些表
SELECT owner, table_name FROM all_tables WHERE owner = 'HR';

-- 库里所有表（需 DBA）
SELECT owner, table_name FROM dba_tables WHERE owner = 'APP_USER';

-- 其他常用
SELECT view_name FROM user_views;
SELECT sequence_name FROM user_sequences;
SELECT index_name, table_name FROM user_indexes;
```

---

## 十一、备份：expdp / impdp 提一嘴

逻辑备份用 Data Pump 工具（命令行运行，非 sqlplus 内）：

```bash
# 导出指定 schema
expdp system/Oracle123@FREEPDB schemas=app_user \
    directory=DATA_PUMP_DIR dumpfile=app.dmp logfile=exp.log

# 导入到目标库
impdp system/Oracle123@FREEPDB schemas=app_user \
    directory=DATA_PUMP_DIR dumpfile=app.dmp
```

`directory` 指向数据库中预先创建的目录对象；生产环境还有 RMAN 物理备份体系，属于进阶话题。

---

## 十二、速查卡

| 分类 | 关键点 |
|------|--------|
| 无表查询 | `SELECT expr FROM dual` |
| 字符串类型 | 一律 `VARCHAR2`，不是 VARCHAR |
| 数值 | `NUMBER(p,s)` 通吃整数与小数 |
| 主键自增 | 序列 `NEXTVAL`，或 12c+ 的 IDENTITY 列 |
| 分页 | 三层嵌套 ROWNUM，或 `OFFSET ... FETCH` |
| 元数据 | `user_tables` / `all_tables` / `dba_tables` |
| 过程化编程 | PL/SQL 匿名块 `DECLARE-BEGIN-END` |
| 登录管理 | `sqlplus / as sysdba` |
| 逻辑备份 | `expdp` / `impdp` |

---

**返回** [[../数据库目录|数据库目录]]
