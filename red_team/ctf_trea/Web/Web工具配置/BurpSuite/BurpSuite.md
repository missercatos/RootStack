## BurpSuite -- 工具配置

> Burp Suite 是 Web 安全测试的核心工具，用于拦截、修改和重放 HTTP 请求。本知识库默认终端习惯，但理解 Burp 的基础配置是必要技能。

### 安装与启动

```bash
# Arch Linux / ArchStrike
sudo pacman -S burpsuite

# 或通过 yay 安装社区版
yay -S burpsuite

# 启动（终端）
burpsuite
```

### 核心配置

**1. 代理设置（Proxy → Options）**

Burp 默认监听 `127.0.0.1:8080`。配置浏览器代理指向该地址。

浏览器代理设置：
- Firefox：设置 → 网络设置 → 手动代理 → HTTP 代理 `127.0.0.1` 端口 `8080`
- Chrome：安装 Proxy SwitchyOmega 插件更方便

**2. 拦截开关**

Proxy → Intercept 标签 → "Intercept is on/off" 按钮控制拦截

**3. 证书安装（HTTPS 抓包必须）**

访问 `http://burpsuite` 下载 CA 证书 → 浏览器导入为受信任的根证书

### 常用模块

| 模块 | 用途 | 快捷键/入口 |
|------|------|-----------|
| Proxy | 拦截和查看所有请求/响应 | HTTP history |
| Repeater | 手动修改请求并重发，观察响应 | Ctrl+R 发送到 Repeater |
| Intruder | 批量爆破参数（字典攻击） | Ctrl+I 发送到 Intruder |
| Decoder | 编码解码（URL/base64/hex） | 右键 → Send to Decoder |
| Scanner | 自动漏洞扫描（Pro 版） | Dashboard |

### 终端替代对照表

由于本知识库默认终端习惯，大部分 Burp 操作都有终端替代品：

| Burp 功能 | 终端替代 |
|----------|---------|
| 看请求/响应 | `curl -s -D - URL` |
| 修改请求头 | `curl -H "Key: Value" URL` |
| 修改请求方法 | `curl -X POST URL` |
| 带 Cookie | `curl -b "admin=1" URL` |
| 参数爆破 | `while read pw; do curl -u "$u:$pw" URL; done < pw.txt` |
| URL 解码 | `python3 -c "from urllib.parse import unquote; print(unquote('...'))"` |
| base64 编解码 | `echo -n "xxx" \| base64` / `echo "xxx" \| base64 -d` |

### 关联教程

- [[../Chrome/Chrome|Chrome 配置]] -- 浏览器配合 Burp 的完整配置
- [[../../Web前置技能/HTTP协议/HTTP协议|HTTP 协议总览]] -- HTTP 协议基础
- [[../../../../archstrike-web教学/01-Web基础与HTTP协议|01-Web基础与HTTP协议]] -- ArchStrike Web 安全实战
- [[../../使用习惯|使用习惯]] -- 终端习惯与图形化习惯说明
