# PostgreSQL 教程

PostgreSQL 自称"世界上最先进的开源关系型数据库"，以 **BSD 类许可**（PostgreSQL License）发布，可自由用于商业产品而无需开源衍生代码——这与 MySQL 的 GPL 双授权形成鲜明对比。它对 SQL 标准的遵从度极高，JSONB、数组、CTE、窗口函数、扩展生态是其招牌能力。本章面向已学过 MySQL 基础的读者，重点讲差异与亮点。

---

## 一、多平台安装

| 平台 | 方式 | 命令 |
|------|------|------|
| Windows | 官方安装器 | 下载 EnterpriseDB 安装包图形安装 |
| macOS | Homebrew | `brew install postgresql@16` |
| Ubuntu/Debian | apt | `sudo apt install postgresql` |
| Arch Linux | pacman | `sudo pacman -S postgresql` |
| Docker | 一键运行 | 见下 |

```bash
# macOS
brew install postgresql@16
brew services start postgresql@16

# Ubuntu
sudo apt update && sudo apt install postgresql -y
sudo systemctl status postgresql

# Docker
docker run -d --name pg16 \
    -e POSTGRES_PASSWORD=123456 \
    -p 5432:5432 \
    -v pg_data:/var/lib/postgresql/data \
    postgres:16
```

> Ubuntu 安装后自动创建系统用户 `postgres`：`sudo -u postgres psql` 即可进入。

---

## 二、psql 连接与元命令

```bash
psql -U postgres -h localhost -d postgres   # -u 是普通参数，PostgreSQL 用大写 -U
psql                                        # 本机当前用户直连
```

psql 的反斜杠元命令是它的特色，效率远高于查系统表：

| 元命令 | 作用 | MySQL 等价操作 |
|--------|------|----------------|
| `\l` | 列出所有数据库 | `SHOW DATABASES;` |
| `\c dbname` | 切换数据库 | `USE dbname;` |
| `\dt` | 列出当前库的表 | `SHOW TABLES;` |
| `\d 表名` | 查看表结构（含索引、约束） | `DESC t;` + `SHOW CREATE TABLE;` |
| `\dn` | 列出所有 schema | 无直接等价 |
| `\du` | 列出用户与角色 | `SELECT user,host FROM mysql.user;` |
| `\di` | 列出索引 | `SHOW INDEX FROM t;` |
| `\x` | 切换扩展显示（竖排） | `\G` 结尾 |
| `\timing` | 显示每条 SQL 耗时 | — |
| `\q` | 退出 | `EXIT;` |

---

## 三、与 MySQL 差异对照表

这是 MySQL 用户上手 PostgreSQL 最需要的一节：

| 项目 | MySQL 写法 | PostgreSQL 写法 |
|------|-----------|-----------------|
| 自增主键 | `AUTO_INCREMENT` | `SERIAL` 或 `GENERATED ALWAYS AS IDENTITY`（标准推荐） |
| 分页 | `LIMIT 10 OFFSET 5` | 相同：`LIMIT 10 OFFSET 5` |
| 忽略大小写模糊 | `LIKE 'a%'` 无法直接忽略大小写 | `ILIKE 'a%'` 直接忽略大小写 |
| 字符串拼接 | `CONCAT(a, b)` | `a \|\| b`（也支持 CONCAT） |
| 引号规则 | 双引号可表示字符串 | 双引号 = 标识符（表名/列名），单引号才是字符串 |
| 类型强转 | `CAST(x AS INT)` | `x::int`（简洁的 :: 语法） |
| 大小写折叠 | 表名默认不区分 | 不加双引号的标识符折叠为小写；建了带引号的大写名就得永远带引号 |
| 模糊查询通配符 | `%` `_` | 相同 |
| 无符号整型 | 有 `UNSIGNED` | 没有，用 CHECK 约束模拟 |
| 引擎概念 | InnoDB/MyISAM 可选 | 无引擎概念，统一存储引擎 |

```sql
-- 差异速览示例
CREATE TABLE users (
    id     SERIAL PRIMARY KEY,                       -- 等价 AUTO_INCREMENT
    name   VARCHAR(50) NOT NULL,
    age    INT CHECK (age >= 0),                     -- 替代 UNSIGNED
    email  VARCHAR(100)
);

SELECT 'Post' || 'greSQL';            -- 字符串拼接：PostgreSQL
SELECT * FROM users WHERE name ILIKE '%li%';   -- 忽略大小写匹配
SELECT '123'::int + 1;                -- 强转：124
SELECT "Name" FROM "Users";           -- 双引号是标识符，单引号才是字符串
```

---

## 四、数据类型亮点

### 4.1 JSONB（二进制 JSON）

JSONB 存储解析后的 JSON，支持索引与丰富的操作符：

```sql
CREATE TABLE events (
    id    SERIAL PRIMARY KEY,
    data  JSONB NOT NULL
);

INSERT INTO events (data) VALUES
    ('{"type": "click", "user": {"id": 1}, "tags": ["web", "vip"]}');

-- 操作符
SELECT data->>'type'              FROM events;   -- ->> 取文本值："click"
SELECT data->'user'->>'id'        FROM events;   -- 链式取嵌套字段："1"
SELECT data @> '{"type": "click"}' FROM events;  -- @> 包含判断，可用 GIN 索引加速
SELECT data ? 'tags'               FROM events;  -- ? 是否含该键
```

| 操作符 | 含义 |
|--------|------|
| `->` | 取 JSON 对象/数组元素（返回 jsonb） |
| `->>` | 取值并转为文本 |
| `@>` | 左侧包含右侧 JSON |
| `?` | 是否包含指定顶层键 |

### 4.2 数组类型

MySQL 没有的原生能力：

```sql
CREATE TABLE posts (
    id    SERIAL PRIMARY KEY,
    title VARCHAR(200),
    tags  TEXT[] DEFAULT '{}'      -- 文本数组
);

INSERT INTO posts (title, tags) VALUES ('hello', ARRAY['db', 'tutorial']);

SELECT * FROM posts WHERE 'db' = ANY(tags);       -- 数组包含某元素
SELECT * FROM posts WHERE tags && ARRAY['db'];    -- 数组有交集
SELECT tags[1] FROM posts;                        -- 下标从 1 开始！
```

### 4.3 其他实用类型

| 类型 | 说明 |
|------|------|
| `UUID` | 原生 UUID 存储，配合 `gen_random_uuid()` 作分布式主键 |
| `INET` / `CIDR` | IP 地址类型，支持网段比较 `WHERE ip << '10.0.0.0/8'` |
| `NUMERIC` | 任意精度精确小数（同 MySQL DECIMAL） |
| `INTERVAL` | 时间区间可直接加减运算 |
| 枚举 `CREATE TYPE` | 自定义枚举类型 |

---

## 五、CTE 公用表表达式

WITH 子句把复杂查询拆成命名步骤，可读性远超嵌套子查询：

```sql
-- 各部门平均工资，再筛高于全公司平均的部门
WITH dept_avg AS (
    SELECT dept_id, AVG(salary) AS avg_sal
    FROM employees
    GROUP BY dept_id
),
company_avg AS (
    SELECT AVG(salary) AS avg_sal FROM employees
)
SELECT d.dept_id, d.avg_sal
FROM dept_avg d, company_avg c
WHERE d.avg_sal > c.avg_sal;
```

CTE 还支持在同一语句内更新/删除并返回结果：

```sql
WITH removed AS (
    DELETE FROM logs WHERE created_at < NOW() - INTERVAL '90 days'
    RETURNING id          -- 返回被删的行
)
SELECT COUNT(*) FROM removed;
```

### 5.1 递归 CTE

处理树形/层级数据的利器，MySQL 8 之前完全没有的能力：

```sql
CREATE TABLE org (
    id       INT PRIMARY KEY,
    name     VARCHAR(50),
    boss_id  INT REFERENCES org(id)
);

INSERT INTO org VALUES (1,'CEO',NULL),(2,'张总监',1),(3,'李经理',2),(4,'王工',3),(5,'赵工',3);

-- 从 CEO 向下展开整棵组织树
WITH RECURSIVE tree AS (
    SELECT id, name, boss_id, 1 AS depth
    FROM org WHERE boss_id IS NULL          -- 递归起点
    UNION ALL
    SELECT o.id, o.name, o.boss_id, t.depth + 1
    FROM org o JOIN tree t ON o.boss_id = t.id   -- 递归步骤
)
SELECT * FROM tree ORDER BY depth;

-- 经典应用：1 到 100 数字序列
WITH RECURSIVE nums(n) AS (
    SELECT 1
    UNION ALL
    SELECT n + 1 FROM nums WHERE n < 100
)
SELECT SUM(n) FROM nums;
```

---

## 六、窗口函数示例

语法与 MySQL 相同（`OVER (PARTITION BY ... ORDER BY ...)`），但 PostgreSQL 支持更早、更完整：

```sql
SELECT name, dept_id, salary,
       ROW_NUMBER() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rn,
       RANK()       OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rk,
       SUM(salary)  OVER (ORDER BY hire_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total,
       LAG(salary)  OVER (ORDER BY hire_date) AS prev_sal
FROM employees;
```

---

## 七、扩展生态

PostgreSQL 的杀手锏之一是扩展机制，一条语句加载新能力：

```sql
-- PostGIS：业界最强 GIS 地理空间引擎
CREATE EXTENSION postgis;
SELECT ST_Distance(a.geom, b.geom);   -- 计算两点距离

-- pg_trgm：三元组模糊搜索，加速 LIKE '%xx%'
CREATE EXTENSION pg_trgm;
CREATE INDEX idx_name_trgm ON users USING gin (name gin_trgm_ops);

-- uuid-ossp / pgcrypto：UUID 与加密函数
CREATE EXTENSION IF NOT EXISTS pgcrypto;
SELECT gen_random_uuid();
```

常用扩展速览：

| 扩展 | 用途 |
|------|------|
| postgis | 地理空间数据全套 |
| pg_trgm | 模糊文本搜索 |
| pgcrypto | 加密/哈希函数 |
| pg_stat_statements | SQL 性能统计 |
| TimescaleDB | 时序数据库能力 |

---

## 八、备份：pg_dump 与 pg_restore

```bash
# 备份单个库（纯 SQL 文本格式）
pg_dump -U postgres shop > shop.sql

# 自定义压缩格式（恢复更快、可选只恢复部分对象）
pg_dump -U postgres -Fc shop > shop.dump

# 全实例所有库
pg_dumpall -U postgres > all.sql

# 仅导出结构
pg_dump -U postgres -s shop > shop_schema.sql

# 恢复文本格式
psql -U postgres -d shop_new -f shop.sql

# 恢复自定义格式（pg_restore）
pg_restore -U postgres -d shop_new shop.dump
```

| 对比项 | mysqldump | pg_dump |
|--------|-----------|---------|
| 默认输出 | SQL 文本 | SQL 文本 |
| 二进制备份格式 | 无 | `-Fc` 自定义压缩格式 |
| 在线一致性 | 需 `--single-transaction` | 天然 MVCC 快照，无需锁库 |

---

## 九、用户与权限

PostgreSQL 只有"角色"一个概念，带 LOGIN 属性的角色即用户：

```sql
-- 创建登录用户
CREATE ROLE appuser WITH LOGIN PASSWORD 'Str0ng!Pass';

-- 创建角色（组）
CREATE ROLE readers;

-- 给角色赋权
GRANT CONNECT ON DATABASE shop TO readers;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readers;

-- 用户加入角色
GRANT readers TO appuser;

-- 授权未来新建的表也自动可见（否则新表要重新 GRANT）
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readers;

-- 查看权限
\du

-- 收权与删除
REVOKE readers FROM appuser;
DROP ROLE appuser;
```

与 MySQL 的显著差异：权限按 database → schema → table 三层组织，`public` 是默认 schema；跨库访问需通过 `dblink`/FDW 扩展而非同一连接直接切换。

---

## 十、本章小结

| 主题 | 要点 |
|------|------|
| 许可与定位 | BSD 类许可随意商用，SQL 标准遵从度高，功能最全的开源关系库 |
| 元命令 | \l \c \dt \d \du 提效神器 |
| 关键差异 | SERIAL 自增、ILIKE、`\|\|` 拼接、双引号=标识符、`::` 强转 |
| 数据类型 | JSONB 四大操作符、原生数组、UUID、INET |
| 层级查询 | WITH RECURSIVE 递归 CTE 处理树形结构 |
| 生态 | CREATE EXTENSION 加载 PostGIS/pg_trgm 等 |
| 运维 | pg_dump -Fc + pg_restore，MVCC 快照不锁库 |

---
**返回** [[../数据库目录|数据库目录]]
