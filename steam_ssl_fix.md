# 自签名 CA 证书 SSL 信任问题通用解决方案

> 适用于：Steamcommunity302、Clash、mitmproxy、Charles、Fiddler 等使用自签名 CA 证书进行 HTTPS 解密的本地代理工具。

---

## 问题本质

本地代理工具对 HTTPS 流量进行中间人解密时，会使用自签名 CA 证书签发服务器证书。如果系统或应用程序未信任该 CA，就会报 SSL 证书错误。

**常见错误信息：**
```
SSL certificate problem: self-signed certificate
NET::ERR_CERT_AUTHORITY_INVALID
error:-202
certificate verify failed
```

---

## 通用诊断流程

```bash
# 1. 检查是否有本地代理监听 443 端口
ss -tlnp | grep ':443'         # Linux
lsof -i :443                   # macOS
netstat -ano | findstr ":443"  # Windows

# 2. 检查 hosts 是否被修改
cat /etc/hosts                 # Linux/macOS
type C:\Windows\System32\drivers\etc\hosts  # Windows

# 3. 导出代理的 CA 证书
echo | openssl s_client -connect 127.0.0.1:443 -servername example.com 2>/dev/null | openssl x509 -outform PEM > proxy_ca.crt

# 4. 查看证书信息
openssl x509 -in proxy_ca.crt -noout -subject -issuer -dates
```

---

## 一、Windows

### 1. 添加 CA 证书到受信任的根证书颁发机构

**GUI 操作：**
1. 双击 `.crt` 或 `.pem` 文件
2. 安装证书 → 本地计算机（需管理员）
3. 将所有证书放入下列存储 → 浏览 → **受信任的根证书颁发机构**
4. 完成

**命令行（管理员 CMD）：**
```cmd
certutil -addstore -f "Root" <CA证书文件>.crt
```

**PowerShell（管理员）：**
```powershell
Import-Certificate -FilePath "C:\path\to\ca.crt" -CertStoreLocation Cert:\LocalMachine\Root
```

### 2. 清除 SSL 缓存并重置网络

```cmd
certutil -urlcache * delete
netsh winsock reset
netsh int ip reset
ipconfig /flushdns
ipconfig /registerdns
```

完成后**重启电脑**。

### 3. Firefox 专项（独立证书库）

1. Firefox → 设置 → 隐私与安全 → 证书 → 查看证书
2. 证书颁发机构 → 导入 → 选择 CA 证书
3. 勾选「信任此 CA 来标识网站」→ 确定

### 4. Chrome/Edge

Chrome/Edge 默认使用 Windows 系统证书库，添加到系统信任后通常立即生效。如不生效，清除 SSL 状态：
- Chrome → 设置 → 隐私和安全 → 安全 → 管理证书

### 5. Steam 客户端

```cmd
:: 导入 CA 证书到系统信任库
certutil -addstore -f "Root" <CA证书文件>.crt

:: 重启 Steam
```

---

## 二、Linux

### 1. 系统级信任（所有应用生效）

**Debian / Ubuntu：**
```bash
sudo cp <CA证书>.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
sudo resolvectl flush-caches
```

**Arch Linux：**
```bash
sudo cp <CA证书>.crt /etc/ca-certificates/trust-source/anchors/
sudo update-ca-trust
```

**RHEL / CentOS / Fedora：**
```bash
sudo cp <CA证书>.pem /etc/pki/ca-trust/source/anchors/
sudo update-ca-trust extract
```

### 2. NSS 数据库修复（Firefox / Chrome / Steam 客户端）

这些应用使用 NSS 数据库管理证书，需要单独修复信任标志。

```bash
# 查看用户级 NSS 数据库中的证书
certutil -L -d sql:~/.pki/nssdb/

# 查看系统级
certutil -L -d sql:/etc/pki/nssdb/

# 如果信任标志是 C,,（仅客户端），改为 CT,C,C（信任服务器）
certutil -M -d sql:~/.pki/nssdb/ -n "<CA证书名称>" -t "CT,C,C"
```

**信任标志对照：**
| 标志 | 用途 |
|------|------|
| `C,,` | 仅客户端认证（不信任 SSL 服务器） |
| `CT,C,C` | 完全信任（SSL 服务器 + 客户端 + 邮件） |
| `CT,,` | 仅信任 SSL 服务器 |

### 3. Firefox 专项（独立 NSS 数据库）

```bash
# 找到 Firefox 证书数据库目录
FIREFOX_NSS=$(find ~/.mozilla/firefox -name "cert9.db" -exec dirname {} \; 2>/dev/null | head -1)

# 导入 CA 证书
certutil -A -d "sql:$FIREFOX_NSS" -n "<CA证书名称>" -t "CT,C,C" -i <CA证书>.crt
```

### 4. Steam 客户端专项

```bash
# 1. 找到 Steam 运行时 CA 证书目录
STEAM_CERT=$(find ~/.local/share/Steam -path "*/etc/ssl/certs" -type d 2>/dev/null | head -1)

# 2. 复制 CA 证书
sudo cp <CA证书>.crt "$STEAM_CERT/"

# 3. 追加到 ca-certificates.crt
sudo cat <CA证书>.crt >> "$STEAM_CERT/ca-certificates.crt"

# 4. 修复用户 NSS 信任标志
certutil -M -d sql:~/.pki/nssdb/ -n "<CA证书名称>" -t "CT,C,C"

# 5. 重启 Steam
```

### 5. 验证

```bash
# 测试 SSL 连接
curl -v https://目标域名/

# 验证证书链
openssl verify -CAfile <CA证书>.crt <服务器证书>.pem
```

---

## 三、macOS

### 1. 添加到系统钥匙串

**命令行：**
```bash
# 导入到系统钥匙串（需管理员密码）
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain <CA证书>.crt

# 或导入到用户登录钥匙串
security add-trusted-cert -r trustRoot -k ~/Library/Keychains/login.keychain-db <CA证书>.crt
```

**GUI 操作：**
1. 双击 `.crt` 文件 → 钥匙串访问自动打开
2. 找到导入的证书 → 右键 → 显示简介
3. 展开「信任」→「使用此证书时」→ 始终信任
4. 关闭窗口 → 输入密码确认

### 2. Chrome / Safari

macOS 的 Chrome 和 Safari 默认使用系统钥匙串，导入系统钥匙串后通常立即生效。

如 Chrome 不生效：
```bash
# 重置 SSL 状态
defaults delete com.google.Chrome.SSLState
# 重启 Chrome
```

### 3. Firefox 专项

```bash
FIREFOX_NSS=$(find ~/Library/Application\ Support/Firefox/Profiles -name "cert9.db" -exec dirname {} \; 2>/dev/null | head -1)

certutil -A -d "sql:$FIREFOX_NSS" -n "<CA证书名称>" -t "CT,C,C" -i <CA证书>.crt
```

### 4. 清除 DNS 缓存

```bash
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
```

---

## 四、排查清单

| 检查项 | Linux | macOS | Windows |
|--------|-------|-------|---------|
| 系统时间 | `timedatectl status` | 系统设置 → 日期与时间 | 设置 → 时间和语言 |
| hosts 文件 | `/etc/hosts` | `/etc/hosts` | `C:\Windows\System32\drivers\etc\hosts` |
| 443 端口监听 | `ss -tlnp \| grep :443` | `lsof -i :443` | `netstat -ano \| findstr :443` |
| 系统 CA 证书 | 见发行版命令 | `security find-certificate` | `certutil -store root` |
| NSS 数据库 | `certutil -L -d sql:~/.pki/nssdb/` | 同左 | 不适用 |
| DNS 缓存 | `resolvectl flush-caches` | `sudo dscacheutil -flushcache` | `ipconfig /flushdns` |

---

## 五、注意事项

1. **安全警告：** 信任自签名 CA = 允许该 CA 解密你的所有 HTTPS 流量。仅在可信的本地代理工具中使用。
2. **证书更新：** 代理工具更新/重新安装后可能重新生成 CA 证书，需要重新导入。
3. **多浏览器：** Firefox 始终使用独立证书库，无论哪个平台都需要单独处理。
4. **企业网络：** 如果是公司网络问题，联系 IT 部门获取正确的根证书，不要自行信任不明来源的 CA。
5. **Steam 客户端：** Linux 上 Steam 使用 CEF（Chromium Embedded Framework），依赖 NSS 数据库，必须同时修复系统信任库和 NSS 信任标志。
