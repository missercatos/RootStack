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

下一章把查询能力拉满：[[03-查询进阶|查询进阶]]

---
**返回** [[../数据库目录|数据库目录]]
