## 目录

- [[#一、PHP代码结构|一、PHP代码结构]]
- [[#二、变量与数据类型|二、变量与数据类型]]
- [[#三、弱类型行为速览|三、弱类型行为速览]]
- [[#四、字符串与数组|四、字符串与数组]]
- [[#五、超全局变量|五、超全局变量]]
- [[#六、文件操作与会话|六、文件操作与会话]]
- [[#七、输出与编码|七、输出与编码]]
- [[#八、红队视角总结|八、红队视角总结]]

---

## 一、PHP代码结构

### 标签与文件

```php
<?php
// PHP 代码必须写在 <?php ... ?> 内
echo "Hello";
?>
```

| 标签 | 说明 |
|------|------|
| `<?php ... ?>` | 标准标签，永远可用 |
| `<? ... ?>` | 短标签，需 `short_open_tag=On`，多数默认关闭 |
| `<?= ... ?>` | 等价于 `<?php echo ... ?>`，模板输出常用 |
| `?>...` | 标签外内容原样输出（纯文本） |

```php
<?php $name = "admin"; ?>
<!-- 标签外的 HTML 会被原样输出 -->
<p>当前用户: <?= $name ?></p>
```

### 注释

```php
// 单行注释
# 单行注释（PHP 特有，但较少用）
/* 多行注释 */
```

### 大小写敏感规则（红队重点）

| 对象 | 大小写敏感性 | 说明 |
|------|-------------|------|
| 变量名 | 敏感 | `$Name` 与 `$name` 是两个变量 |
| 函数名 | 不敏感 | `SYSTEM()` 与 `system()` 等价，可用来绕过简单 WAF 大小写检测 |
| 类名/方法名 | 不敏感 | `Eval()` 与 `eval()` 等价 |
| 常量名 | 默认敏感 | 用 `define` 定义的常量区分大小写 |

```php
<?php
SYSTEM('id');   // 等价于 system('id')，WAF 常见绕过
ECHO "x";       // 等价于 echo "x"
?>
```

---

## 二、变量与数据类型

### 变量声明

```php
<?php
$name = "admin";      // 字符串
$age = 25;            // 整数
$price = 3.14;        // 浮点
$flag = true;         // 布尔
$arr = array(1, 2, 3);  // 数组（老写法）
$arr2 = [1, 2, 3];      // 数组（短语法）
$obj = new stdClass();  // 对象
$null = NULL;           // 空值
?>
```

PHP 变量以 `$` 开头，无需声明类型，运行时自动推断——与 JavaScript 的弱类型定位相似。

### 数据类型一览

| 类型 | 示例 | 判断函数 | 备注 |
|------|------|---------|------|
| 整数 int | `42` | `is_int()` | |
| 浮点 float | `3.14` | `is_float()` | `0.5` 比较有精度坑 |
| 字符串 string | `"abc"` | `is_string()` | |
| 布尔 bool | `true` | `is_bool()` | |
| 数组 array | `[1,2]` | `is_array()` | 哈希表，键可为字符串 |
| 对象 object | `new A()` | `is_object()` | |
| NULL | `NULL` | `is_null()` | `isset()` 返回 false |
| 资源 resource | `fopen()` | `is_resource()` | 文件句柄等 |

### 可变变量（红队关注）

```php
<?php
$cmd = "system";
$cmd('id');   // 可变函数调用：等价于 system('id')
?>
```

变量函数（Variable Functions）是绕过"危险函数黑名单"的常见手段：

```php
<?php
$a = $_GET['f'];     // f=system
$a($_GET['c']);      // system($_GET['c']) → RCE
?>
```

---

## 三、弱类型行为速览

PHP 是弱类型语言，比较与运算时会自动做类型转换。详细攻防见 [[02-弱类型与认证绕过|02 弱类型与认证绕过]]，这里先建立直觉：

```php
<?php
"1" == 1        // true，字符串自动转数字
"1" === 1       // false，严格比较类型
"admin" == 0    // true！非数字字符串转 0
"" == 0         // true
"1e3" == 1000   // true，科学计数法
null == false   // true
[] == false     // true（空数组）
"0e123" == "0e456"  // true，0 的幂都是 0
?>
```

> **核心记忆**：`==` 只比"值"，`===` 才比"值和类型"。所有认证绕过、`0e` 魔法哈希、`is_numeric` 绕过都从这里长出来。

---

## 四、字符串与数组

### 字符串拼接与插值

```php
<?php
$name = "admin";
echo "Hello $name";      // 双引号内变量插值
echo 'Hello $name';      // 单引号不插值，输出字面量
echo "Hello " . $name;   // 点号拼接（PHP 的 . 是字符串连接符）
?>
```

| 特性 | 双引号 | 单引号 |
|------|:------:|:------:|
| 变量插值 | 是 | 否 |
| 转义 `\n` `\t` | 是 | 仅 `\\` `\'` |
| 执行速度 | 稍慢 | 稍快（安全审计常建议单引号） |

### 常用字符串函数

| 函数 | 作用 | 攻击场景 |
|------|------|---------|
| `strlen()` | 长度 | 检测输入长度限制 |
| `str_replace()` | 替换 | 过滤 → 双写/嵌套绕过 |
| `preg_match()` | 正则匹配 | 过滤 → 大小写/编码/换行绕过 |
| `substr()` | 截取 | |
| `md5()` | 哈希 | 0e 碰撞、数组绕过 |
| `base64_encode()` | Base64 | 编码绕过 |
| `htmlspecialchars()` | HTML 转义 | XSS 防护（攻击时反推） |
| `addslashes()` | 转义引号 | SQL 注入防护（老版本） |

```php
<?php
// 经典过滤与绕过
$input = "flagflagflag";
str_replace("flag", "", $input);   // 结果 "flag"，双写绕过单次替换
preg_match("/flag/i", $input);     // 大小写、%00、换行符绕过
?>
```

### 数组

```php
<?php
$arr = ["id" => 1, "name" => "admin"];
echo $arr["name"];          // admin
echo count($arr);           // 2
in_array("admin", $arr);    // true（注意 in_array 默认弱比较！）

// 数组作为 GET 参数
// ?id[]=1&id[]=2 → $_GET['id'] = [1, 2]
?>
```

> 数组能绕过大量"字符串过滤"：`md5($_GET['id'])` 在 `id[]=x` 时报错返回 NULL，`NULL == NULL` 恒真——详见弱类型章节。

---

## 五、超全局变量

超全局变量（Superglobals）是 PHP 内置的全局数组，**任何作用域可直接使用**，是 Web 攻击的入口。

| 超全局 | 内容 | 攻击入口 |
|--------|------|---------|
| `$_GET` | URL 查询参数 `?a=b` | 参数注入、SQLi、LFI |
| `$_POST` | POST body `a=b` | 表单注入、上传 |
| `$_REQUEST` | GET+POST+Cookie 合并 | 参数污染 |
| `$_COOKIE` | Cookie 键值 | 会话伪造、Cookie 注入 |
| `$_SESSION` | 会话数据（服务端） | 反序列化、Session 文件包含 |
| `$_FILES` | 上传文件元数据 | 文件上传 |
| `$_SERVER` | 服务器/请求信息 | 头注入、路径泄露（`PHP_SELF` 反射 XSS） |
| `$_ENV` | 环境变量 | 信息泄露 |

```php
<?php
// 典型取值方式
$id    = $_GET['id'];
$user  = $_POST['user'];
$pass  = $_POST['pass'];
$sid   = $_COOKIE['PHPSESSID'];
$token = $_SERVER['HTTP_X_FORWARDED_FOR'];  // 可伪造头

// 全量打印（审计时快速看输入）
var_dump($_GET);
print_r($_SERVER);
?>
```

### 常用 $_SERVER 键

| 键 | 内容 | 风险 |
|----|------|------|
| `HTTP_USER_AGENT` | User-Agent 头 | 日志投毒（日志包含 RCE） |
| `HTTP_REFERER` | 来源页 | 日志投毒 |
| `HTTP_X_FORWARDED_FOR` | 客户端 IP（可伪造） | IP 白名单绕过 |
| `PHP_SELF` | 当前脚本路径 | 反射 XSS（URL 拼接未编码） |
| `REQUEST_URI` | 请求完整 URI | 同上 |

```php
<?php
// PHP_SELF 反射 XSS 经典案例
// 请求 /index.php/"><script>alert(1)</script>
echo "<form action=\"" . $_SERVER['PHP_SELF'] . "\">";
// PHP_SELF 直接输出 → XSS
?>
```

---

## 六、文件操作与会话

### 文件读写

```php
<?php
// 读文件
$content = file_get_contents("/etc/passwd");
$lines   = file("/etc/passwd");          // 按行读为数组
$fp      = fopen("/etc/passwd", "r");    // 流式
while (!feof($fp)) echo fgets($fp);

// 写文件
file_put_contents("/tmp/shell.php", "<?php system(\$_GET['c']);?>");
$fp = fopen("/tmp/x.txt", "w");
fwrite($fp, "data");
?>
```

| 函数 | 作用 | 攻击场景 |
|------|------|---------|
| `file_get_contents()` | 全量读取 | 任意文件读取（配合 LFI） |
| `file_put_contents()` | 全量写入 | 写 WebShell |
| `include/require` | 包含并执行 | LFI/RFI → RCE |
| `unlink()` | 删除 | 破坏性操作 |

### Session 会话

```php
<?php
session_start();          // 启动会话，生成 PHPSESSID Cookie
$_SESSION['user'] = "admin";   // 写入会话
echo session_id();        // 当前会话 ID
?>
```

| 知识点 | 说明 | 攻击场景 |
|--------|------|---------|
| `PHPSESSID` Cookie | 会话标识，服务端存文件 | 会话固定、劫持 |
| 存储路径 | Linux 默认 `/var/lib/php/sessions/` | Session 文件包含 |
| 文件名 | `sess_` + PHPSESSID | 已知文件名可包含 |
| `session.serialize_handler` | 序列化方式 | session 反序列化（见 07 章） |

```php
<?php
// 会话内容可控 + 文件包含 → RCE（详见 05 章）
// session 文件: /var/lib/php/sessions/sess_<PHPSESSID>
// 内容: user|s:5:"admin";
?>
```

---

## 七、输出与编码

### 输出函数

| 函数 | 行为 | 攻击视角 |
|------|------|---------|
| `echo` | 输出（语言结构，无返回值） | 反射 XSS 载体 |
| `print` | 输出，返回 1 | 同上 |
| `printf` | 格式化输出 | 格式化字符串问题 |
| `var_dump()` | 打印类型与值 | 审计辅助 |
| `print_r()` | 打印数组 | 审计辅助 |

### 编码与过滤函数

```php
<?php
$raw = "<script>alert(1)</script>";

echo htmlspecialchars($raw);   // &lt;script&gt; 转义尖括号 → 防 XSS
echo htmlentities($raw);       // 转义所有 HTML 实体
echo urlencode($raw);          // URL 编码
echo rawurlencode($raw);       // RFC3986 严格 URL 编码
?>
```

| 过滤函数 | 防护目标 | 攻击绕过 |
|----------|---------|---------|
| `htmlspecialchars` | XSS | 不进引号属性、`javascript:` 协议、`<svg onload>` 实体不拦截 |
| `strip_tags` | XSS/标签 | `<<script>` 双写绕过 |
| `addslashes` | SQLi | 宽字节注入（GBK `%bf%27`） |
| `intval` | 数字过滤 | `intval("1abc")=1` 只取前缀 |

---

## 八、红队视角总结

| 知识点 | 攻击价值 |
|--------|---------|
| `<?= ?>` / `<?php ?>` | 识别 PHP 站点：响应头 `X-Powered-By: PHP/7.4`、`.php` 后缀 |
| 函数大小写不敏感 | WAF 大小写绕过：`SYSTEM()`、`EvAl()` |
| 可变函数 | 危险函数黑名单绕过：`$f($_GET[c])` |
| 超全局变量 | 一切输入面：GET/POST/Cookie/头/文件 |
| 弱比较 | 认证绕过、哈希绕过（见下章） |
| `$_SERVER` 可伪造头 | IP 白名单绕过、日志投毒 |
| Session 文件路径 | 会话文件包含 RCE |
| `PHP_SELF` 反射 | XSS 入口 |

---

**返回** [[PHP基础总目录|PHP 总目录]] | [[../前端基础总目录|前端基础总目录]]