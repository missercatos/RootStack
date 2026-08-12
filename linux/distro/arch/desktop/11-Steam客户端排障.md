# 11 - Steam 客户端排障

> Steam Linux 客户端的内嵌浏览器（CEF/steamwebhelper）运行在 pressure-vessel 容器内，与宿主系统的信任链隔离。本专题以"商店页空白 + `net_error -202`"为例，完整演示从日志定位、容器结构分析到注入修复的全过程，并附带一键修复脚本。

---

## 11.1 症状识别

### 现象

- Steam 商店 / 社区页面空白或加载失败
- 内嵌浏览器无报错弹窗，但页面内容缺失

### 日志定位

CEF 错误记录在客户端日志中：

```bash
# CEF 日志（net_error -202 = SSL 握手失败）
grep "net_error -202" ~/.local/share/Steam/logs/cef_log.txt | tail

# 输出示例
# [102223:102240:0801/160144.140422:ERROR:ssl_client_socket_impl.cc(878)]
# handshake failed; returned -1, SSL error code 1, net_error -202
```

```
# -202 的含义（Chromium 网络栈错误码）
net::ERR_CERT_AUTHORITY_INVALID = -202
# 服务器证书不受信任（签发 CA 不在客户端的信任库中）
```

配合网络连接确认目标确实在握手而非连接失败：

```bash
# 检查是否有到目标站点的连接建立
ss -tnp | grep ":443"
```

## 11.2 根因分析

### 11.2.1 客户端结构

Steam Linux 客户端由三部分构成：

```
steam (主进程)
 └── steamwebhelper（CEF 内嵌浏览器，运行在 pressure-vessel 容器内）
 └── NSS（证书校验）→ libnssckbi.so（信任根库）
```

容器由 `srt-bwrap` 创建，其根文件系统来自运行时镜像：

```
~/.local/share/Steam/steamrt64/pv-runtime/steam-runtime-steamrt/
├── steamrt3c_platform_3c.0.<版本>.246540/ # 运行时镜像（多个版本并存）
│ ├── files/ # 镜像文件树（修改需写这里）
│ │ ├── bin → tmp/usr/bin # 扁平化布局，对应容器内 /usr/*
│ │ ├── lib → tmp/usr/lib
│ │ ├── etc → tmp/usr/etc
│ │ └── ...
│ ├── usr-mtree.txt.gz # 容器 /etc 内容清单（决定哪些文件进容器）
│ └── files/var/ # 会话挂载点
│ └── tmp-XXXXXXXX/usr/ # 每次容器启动重建（硬链接副本）
└── var/tmp-*/usr/ # 当前会话实际挂载到容器 /usr
```

关键机制：

- 每次启动 `steamwebhelper`（或 Steam 会话），`var/tmp-*/` 由镜像 `files/` **硬链接复制**生成
- 容器内 `/usr` 挂载自 `var/tmp-<ID>/usr`，`/etc` 挂载自 `var/tmp-<ID>/usr/etc`
- 镜像 `files/` 中的修改会随 tmp 重建持续生效；**只改 tmp 的修改会在重建时丢失**
- `usr-mtree.txt.gz` 决定容器 `/etc` 下出现哪些文件（不含的文件即使存在于镜像也不挂载）

### 11.2.2 信任链差异（问题的真正根源）

Chromium/CEF 用 NSS 校验证书，默认加载 `libnssckbi.so`（内置信任根模块）。两个系统对该库的处理完全不同：

| | Arch Linux 宿主 | Steam 运行时容器 |
|---|---|---|
| `libnssckbi.so` 身份 | 符号链接 → `/usr/lib/pkcs11/p11-kit-trust.so` | 真实的静态内置根库 |
| 信任来源 | p11-kit 实时合并 `/etc/ca-certificates/trust-source/` 全部 CA | 仅编译期内置的公共根证书 |
| 用户安装的 CA（如 Steamcommunity302） | 自动生效 | 永远缺失 |

```bash
# 宿主侧验证：libnssckbi.so 是 p11-kit-trust 的链接
ls -la /usr/lib/libnssckbi.so
# /usr/lib/libnssckbi.so -> pkcs11/p11-kit-trust.so

# 宿主侧验证：系统信任库中能看到目标 CA
trust list | grep -A1 "Steamcommunity302"
# 类型: 证书
# 信任: anchor
```

```bash
# 容器侧验证（需要找到 webhelper 的 PID）
WH=$(pgrep -f "steamwebhelper -nocrashdialog" | head -1)
grep " /usr " /proc/$WH/mountinfo | head -1
# .../var/tmp-6Y38S3/usr /usr ro,nosuid,nodev ... - btrfs ...

# 容器内 nssckbi 是真实文件（约 537KB 内置根），而非 p11-kit 链接
ls -la /proc/$WH/root/usr/lib/x86_64-linux-gnu/nss/libnssckbi.so
```

结论：**容器内缺少用户安装的系统 CA**。对于 S302 自签 CA，必须把"宿主 Arch 的 p11-kit 信任机制"复刻进容器。

## 11.3 修复方案

### 思路

把容器内的 `libnssckbi.so` 内容替换为宿主的 `p11-kit-trust.so`（Arch 的标准做法），并让 302 的 CA 文件进入容器 `/etc`：

1. 替换镜像 `files/lib/x86_64-linux-gnu/nss/libnssckbi.so` → 宿主 `p11-kit-trust.so` 的内容
2. 将 `steamcommunityCA.crt` 放入镜像 `files/etc/ca-certificates/trust-source/anchors/`
3. 在 `usr-mtree.txt.gz` 中登记该 CA（否则不会挂载进容器）
4. 重启 `steamwebhelper` 触发容器重建

### 前置依赖检查

p11-kit-trust.so 需要宿主 libp11-kit 与其依赖，容器需满足这些依赖：

```bash
# 检查 p11-kit-trust.so 的未定义符号（除 glibc 外依赖哪些库）
nm -D /usr/lib/pkcs11/p11-kit-trust.so | grep " U " | awk '{print $2}' | sort -u | head

# 容器内需有对应库（本例只需 libtasn1，容器自带 6.6.0 满足）
ls /proc/$WH/root/usr/lib/x86_64-linux-gnu/libtasn1.so* /proc/$WH/root/usr/lib/x86_64-linux-gnu/libp11-kit.so*
```

### 手动注入步骤

```bash
# 0. 定位镜像目录（取最新版本）
IMGDIR="$HOME/.local/share/Steam/steamrt64/pv-runtime/steam-runtime-steamrt/"\
"steamrt3c_platform_3c.0.20260618.246540"
FILES="$IMGDIR/files"

# 1. 备份原始文件
cp "$FILES/lib/x86_64-linux-gnu/nss/libnssckbi.so" /tmp/libnssckbi.so.bak
cp "$IMGDIR/usr-mtree.txt.gz" /tmp/usr-mtree.bak.gz

# 2. 用宿主 p11-kit-trust.so 的内容覆盖容器 libnssckbi.so
cp /usr/lib/pkcs11/p11-kit-trust.so \
 "$FILES/lib/x86_64-linux-gnu/nss/libnssckbi.so"

# 3. 放置 CA 到镜像 trust-source 目录
mkdir -p "$FILES/etc/ca-certificates/trust-source/anchors"
cp /etc/ca-certificates/trust-source/anchors/steamcommunityCA.crt \
 "$FILES/etc/ca-certificates/trust-source/anchors/"

# 4. 在 mtree 中登记（目录 + 文件条目，格式参考同目录既有条目）
# 解压 → 在 ./etc/ca-certificates/update.d 之后插入：
# ./etc/ca-certificates/trust-source type=dir
# ./etc/ca-certificates/trust-source/anchors type=dir
# ./etc/ca-certificates/trust-source/anchors/steamcommunityCA.crt \
# type=file mode=644 time=<unix时间>.0 size=1302 sha256=<哈希>
# 重新压缩为 usr-mtree.txt.gz

# 5. 重启 webhelper（触发容器重建；不要重启 Steam 主进程！）
pkill -f steamwebhelper
```

> [!note] 为什么只重启 webhelper
> 容器重建只读取镜像 + mtree，不重新校验文件大小。若重启整个 Steam，`BVerifyInstalledFiles` 会按 depotcache manifest 的**文件大小**校验并还原镜像（见 11.4），注入即失效。

### 验证

```bash
# 1. 新 webhelper 的容器内应看到替换后的库与 CA
WH=$(pgrep -f "steamwebhelper -nocrashdialog" | head -1)
ls -la /proc/$WH/root/usr/lib/x86_64-linux-gnu/nss/libnssckbi.so
# 大小应为 248648（宿主 p11-kit-trust.so），而非原始 537176
ls /proc/$WH/root/etc/ca-certificates/trust-source/anchors/

# 2. CEF 日志不再出现新的 -202
grep -c "net_error -202" ~/.local/share/Steam/logs/cef_log.txt # 记下当前值
sleep 120
grep -c "net_error -202" ~/.local/share/Steam/logs/cef_log.txt # 不应增长

# 3. webhelper 与 S302 保持活动连接
ss -tnp | grep "127.0.0.1:443"
```

## 11.4 关键陷阱与边界

### BVerifyInstalledFiles 会还原镜像

Steam 主进程每次启动会校验运行时镜像文件**大小**（与 depotcache manifest 对比），不一致则还原：

```bash
# bootstrap_log.txt 中的还原证据
grep -i "verify\|restor" ~/.local/share/Steam/logs/bootstrap_log.txt

# 典型还原：ca-certificates.crt 被改回 216591 字节
# BVerifyInstalledFiles: Verifying file sizes only: '...ca-certificates.crt'
```

影响：

- **本会话内**（Steam 主进程持续运行）：注入稳定，webhelper 重启不还原
- **跨会话**（完全退出 Steam 再启动）：`libnssckbi.so` 与 `usr-mtree.txt.gz` 会被还原为原始大小，需重新注入

### 排查过程备忘（后续遇到类似问题可参考）

- 容器内 NSS 用户库路径是用户级（`$XDG_DATA_HOME/pki/nssdb`、`$HOME/.pki/nssdb`），往容器 `/etc/pki/nssdb` 注入无效
- 环境变量方案（`SSL_CERT_FILE`、`PRESSURE_VESSEL_FILESYSTEMS_RO` 等）对 CEF 的 NSS 路径不生效
- 容器内已注入后仍报 -202 时，检查 mtree 是否登记了 CA 文件（mtree 缺失 = 文件不进容器 = p11-kit 读不到锚点）

---

## 11.5 一键修复脚本

```bash
#!/usr/bin/env bash
# steam-s302-trust-fix.sh — 修复 Steam CEF 不信任 Steamcommunity302 CA（net_error -202）
# 用法: ./steam-s302-trust-fix.sh
# 依赖: 宿主已安装 S302（/etc/ca-certificates/trust-source/anchors/steamcommunityCA.crt 存在）
set -euo pipefail

CA_SRC=/etc/ca-certificates/trust-source/anchors/steamcommunityCA.crt
TRUST_SRC=/usr/lib/pkcs11/p11-kit-trust.so
RT_DIR="$HOME/.local/share/Steam/steamrt64/pv-runtime/steam-runtime-steamrt"

# 0. 前置检查
[ -f "$CA_SRC" ] || { echo "缺少 $CA_SRC：请先安装 Steamcommunity302 并导入证书"; exit 1; }
[ -f "$TRUST_SRC" ] || { echo "宿主缺少 p11-kit-trust.so（Arch 未装 p11-kit？）"; exit 1; }
pgrep -x steam >/dev/null || { echo "Steam 未运行。请先启动 Steam（本脚本需要它在运行）。"; exit 1; }

# 1. 定位最新的运行时镜像
IMG=$(ls -dt "$RT_DIR"/steamrt3c_platform_3c.* | head -1)
FILES="$IMG/files"
[ -f "$FILES/lib/x86_64-linux-gnu/nss/libnssckbi.so" ] || { echo "未找到镜像目录：$IMG"; exit 1; }

# 2. 替换 libnssckbi.so（先备份）
BAK="$IMG/libnssckbi.so.bak.$(date +%s)"
cp "$FILES/lib/x86_64-linux-gnu/nss/libnssckbi.so" "$BAK"
echo "已备份原始 nssckbi -> $BAK"
cp "$TRUST_SRC" "$FILES/lib/x86_64-linux-gnu/nss/libnssckbi.so"

# 3. 放置 CA
mkdir -p "$FILES/etc/ca-certificates/trust-source/anchors"
cp "$CA_SRC" "$FILES/etc/ca-certificates/trust-source/anchors/"

# 4. 登记 mtree（不存在对应条目时才插入）
mkdir -p /tmp/steamfix.$$
zcat "$IMG/usr-mtree.txt.gz" > /tmp/steamfix.$$/mtree
if ! grep -q "trust-source/anchors/steamcommunityCA.crt" /tmp/steamfix.$$/mtree; then
 SIZE=$(stat -c %s "$CA_SRC")
 TIME=$(stat -c %Y "$CA_SRC")
 SHA=$(sha256sum "$CA_SRC" | awk '{print $1}')
 awk -v t="$TIME" -v s="$SIZE" -v h="$SHA" \
 '1; /^\.\/etc\/ca-certificates\/update.d type=dir$/ {
 print "./etc/ca-certificates/trust-source type=dir";
 print "./etc/ca-certificates/trust-source/anchors type=dir";
 printf "./etc/ca-certificates/trust-source/anchors/steamcommunityCA.crt type=file mode=644 time=%d.0 size=%d sha256=%s\n", t, s, h }' \
 /tmp/steamfix.$$/mtree | gzip > "$IMG/usr-mtree.txt.gz"
 echo "mtree 已更新"
else
 echo "mtree 已包含 CA 条目，跳过"
fi
rm -rf /tmp/steamfix.$$

# 5. 重启 webhelper（保留 Steam 主进程）
echo "重启 steamwebhelper..."
pkill -f steamwebhelper || true
sleep 15

# 6. 验证
WH=$(pgrep -f "steamwebhelper -nocrashdialog" | head -1 || true)
if [ -n "$WH" ]; then
 echo "webhelper PID=$WH"
 ls -l "/proc/$WH/root/etc/ca-certificates/trust-source/anchors/steamcommunityCA.crt"
else
 echo "警告：webhelper 未在 15 秒内重启，请手动检查"
fi
echo "完成。商店页若仍空白，请检查 cef_log.txt 中是否还有 net_error -202。"
```

> [!warning] 跨会话失效
> 完全重启 Steam 后镜像会被 `BVerifyInstalledFiles` 还原，-202 可能复发，此时重新运行本脚本即可（约 1 分钟）。
