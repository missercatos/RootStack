# Arch Linux 软件下载网络问题

> 本章系统讲解 Arch Linux 上软件下载（pacman/yay/pikaur/makepkg 等）遇到网络问题的原理、排查思路和解决方法。以 Clash 为例演示代理配置，最后以 Q&A 形式覆盖其他疑难场景。

---

## 1. 为什么 Arch Linux 下载软件会出问题

### 1.1 DNS 解析失败

`pacman -Sy` 报错 `Could not resolve host: mirrors.xxx.com`，本质是 DNS 查询被污染或超时。

**原理**：你的电脑需要先从 DNS 服务器拿到 mirror 的 IP 地址，才能发起 HTTP 下载。如果 DNS 被劫持（返回假 IP）或查询超时（服务器无响应），下载就无法开始。

```bash
# 验证 DNS 是否正常
nslookup mirrors.aliyun.com
dig mirrors.aliyun.com

# 如果返回不到 IP，说明 DNS 有问题
```

### 1.2 连接被重置 / Connection refused

`pacman -Sy` 报错 `error: failed retrieving file ... Connection reset by peer` 或 `Connection refused`。

**原理**：TCP 连接在建立阶段（三次握手）或数据传输阶段被中间设备（防火墙、运营商、GFW）主动中断。常见原因：
- Mirror IP 被封锁
- 运营商 QoS 限速
- GFW 干扰（针对特定域名/IP）

### 1.3 连接超时

`pacman -Sy` 报错 `error: timed out` 或 `Could not connect to ...`。

**原理**：TCP SYN 包发出去但没有收到 SYN-ACK 回包。可能原因：
- Mirror 服务器宕机或负载过高
- 本地网络路由不通
- 防火墙规则阻止出站

### 1.4 下载速度极慢

能连上但速度只有几 KB/s。

**原因**：
- Mirror 在海外，物理距离远导致 RTT 高
- 运营商对国际带宽限速
- Mirror 本身带宽不足（非高峰期也慢）
- TCP 拥塞控制算法在高延迟链路上表现差

### 1.5 SSL/TLS 证书错误

`pacman -Sy` 报错 `SSL certificate problem: unable to get local issuer certificate`。

**原理**：
- 系统时间不正确（证书验证失败）
- CA 证书包过旧
- 中间人攻击（不常见但需排除）

---

## 2. 解决方案总览

| 问题 | 首选方案 | 备选方案 |
|------|---------|---------|
| DNS 解析失败 | 换公共 DNS（`/etc/resolv.conf`） | 使用 DoH/DoT |
| 连接被重置 | 代理（Clash/v2ray） | 换 mirror |
| 连接超时 | 代理 或 换 mirror | 检查防火墙 |
| 速度极慢 | 换国内 mirror | 代理加速 |
| SSL 证书错误 | `timedatectl set-ntp true` | 更新 ca-certificates |

### 2.1 换 Mirror（最简单的方案）

编辑 `/etc/pacman.d/mirrorlist`，将国内 mirror 放到最前面：

```bash
# 备份
sudo cp /etc/pacman.d/mirrorlist /etc/pacman.d/mirrorlist.bak

# 使用 reflector 自动选最快的 mirror
sudo pacman -S reflector
sudo reflector --country China --age 12 --protocol https --sort rate --save /etc/pacman.d/mirrorlist
```

或者手动编辑，把清华/阿里/中科大等放到第一行：

```
## China
Server = https://mirrors.tuna.tsinghua.edu.cn/archlinux/$repo/os/$arch
Server = https://mirrors.aliyun.com/archlinux/$repo/os/$arch
Server = https://mirrors.ustc.edu.cn/archlinux/$repo/os/$arch
```

### 2.2 换 DNS

```bash
# 临时换
sudo vim /etc/resolv.conf
# 加入：
nameserver 223.5.5.5
nameserver 8.8.8.8

# 永久换（使用 systemd-resolved）
sudo systemctl enable --now systemd-resolved
sudo vim /etc/systemd/resolved.conf
# 加入：
[Resolve]
DNS=223.5.5.5 8.8.8.8
DNSOverTLS=yes
```

### 2.3 使用代理（根本解决国际线路问题）

当 mirror 在海外、或需要访问 GitHub（yay/AUR）时，代理是唯一可靠方案。下一节详细讲解。

---

## 3. 以 Clash 为例配置代理

### 3.1 Clash 的三个端口

| 端口 | 类型 | 用途 |
|------|------|------|
| 7890 | HTTP 代理 | 给 curl/wget/git/yay/pacman 用 |
| 7891 | SOCKS5 代理 | 给 Telegram 等支持 SOCKS5 的软件用 |
| 9090 | API 控制面板 | Clash Dashboard 管理界面 |

### 3.2 启动 Clash

```bash
cd ~/clash && ./clash -d ~/clash &
```

验证是否启动：

```bash
ss -tlnp | grep 7890
# 应看到 clash 进程监听 7890
```

### 3.3 让 pacman 走代理

pacman 不读环境变量的 `http_proxy`，需要在 `/etc/pacman.conf` 中配置：

```bash
sudo vim /etc/pacman.conf
```

在文件末尾加入：

```ini
XferCommand = /usr/bin/curl -x http://127.0.0.1:7890 -o %o %u
```

这样 pacman 下载时会自动走 7890 代理端口。

> 注意：`XferCommand` 会覆盖 pacman 默认的下载方式。如果代理不通，所有下载都会失败。临时恢复：注释掉这行即可。

### 3.4 让 yay/AUR 走代理

yay 底层调用 makepkg → curl，需要设置环境变量：

```bash
export https_proxy=http://127.0.0.1:7890
export http_proxy=http://127.0.0.1:7890
yay -S <包名>
```

永久生效，写入 `~/.bashrc`：

```bash
export https_proxy=http://127.0.0.1:7890
export http_proxy=http://127.0.0.1:7890
export all_proxy=socks5://127.0.0.1:7891
export no_proxy=localhost,127.0.0.1,::1
```

### 3.5 让 git 走代理

```bash
# 只对 GitHub
git config --global http.https://github.com.proxy http://127.0.0.1:7890

# 全局
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890
```

### 3.6 验证代理是否工作

```bash
# 测试 Google
curl -x http://127.0.0.1:7890 https://www.google.com -I
# 应返回 HTTP/2 200

# 测试 GitHub
curl -x http://127.0.0.1:7890 https://github.com -I

# 查看出口 IP（应为代理节点的 IP）
curl -x http://127.0.0.1:7890 https://ipinfo.io/ip
```

### 3.7 Clash 开机自启

```bash
mkdir -p ~/.config/systemd/user

cat > ~/.config/systemd/user/clash.service << 'EOF'
[Unit]
Description=Clash Proxy Service
After=network.target

[Service]
Type=simple
ExecStart=/home/%u/clash/clash -d /home/%u/clash
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

systemctl --user enable clash.service
systemctl --user start clash.service
sudo loginctl enable-linger $(whoami)
```

### 3.8 Clash 规则配置

在 `~/clash/config.yaml` 的 `rules` 段，可以配置哪些流量走代理、哪些直连：

```yaml
rules:
  # 国外走代理
  - DOMAIN-SUFFIX,github.com,Proxy
  - DOMAIN-SUFFIX,google.com,Proxy
  - DOMAIN-SUFFIX,archlinux.org,Proxy

  # 国内直连
  - DOMAIN-SUFFIX,baidu.com,DIRECT
  - DOMAIN-SUFFIX,bilibili.com,DIRECT

  # 兜底
  - MATCH,Proxy
```

---

## 4. 安全注意事项

- **信任代理服务商**：你的流量经过他们的服务器，HTTPS 请求只能看到域名，看不到具体内容
- **DNS 泄露**：确保 DNS 也走代理（Clash 配置 dns 段）
- **WebRTC 泄露**：Firefox 中 `about:config` → `media.peerconnection.enabled` → `false`

---

## 5. 其他一些问题

以下为零碎、不好系统归类的问题，以 Q&A 形式覆盖。

### Q: "SSL certificate problem" 怎么办？

```bash
sudo timedatectl set-ntp true
# 或换个节点
```

### Q: Clash 能用但浏览器不能？

- Mullvad Browser：确认 Clash 已启动
- Firefox：手动设置代理 127.0.0.1:7890
- Chrome：用 `--proxy-server=http://127.0.0.1:7890` 参数启动

### Q: 多个代理软件冲突？

同一时间只能有一个代理软件监听 7890 端口。

```bash
ss -tlnp | grep 7890
# 停止其他代理后再启动 Clash
```

### Q: 代理设置了但 git clone 还是慢？

```bash
env | grep proxy
git config --global --get http.proxy
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890
```

### Q: 怎么查看当前哪些端口被占用了？

```bash
ss -tlnp
# 输出示例：
# LISTEN  0  128  127.0.0.1:7890  users:(("clash",pid=1234,fd=6))
# LISTEN  0  128  127.0.0.1:7891  users:(("clash",pid=1234,fd=7))
# LISTEN  0  128  127.0.0.1:9090  users:(("clash",pid=1234,fd=8))
# LISTEN  0  128  0.0.0.0:22      users:(("sshd",pid=567,fd=3))
```

查看特定端口：

```bash
ss -tlnp | grep 7890
ss -tlnp | grep -E '789[0-9]|909[0-9]'
```

### Q: 不同 VPN/代理工具的默认端口？

| 工具 | HTTP 代理 | SOCKS5 代理 | 管理面板 |
|------|-----------|-------------|---------|
| Clash | 7890 | 7891 | 9090 |
| v2ray | 10808 | 1080 | - |
| sing-box | 10808 | 1080 | - |
| Trojan | 10808 | 1080 | - |
| Shadowsocks | - | 1080 | - |

### Q: 怎么判断当前系统用的是哪个代理工具？

```bash
ps aux | grep -E 'clash|v2ray|sing-box|trojan|ss-local|sslocal'
ss -tlnp | grep 7890
# 输出中的进程名就是当前代理工具
```

### Q: 怎么找到代理工具的配置文件？

| 工具 | 默认配置路径 |
|------|-------------|
| Clash | ~/clash/config.yaml |
| Clash Meta | ~/.config/clash-meta/config.yaml |
| v2ray | ~/.config/v2ray/config.json |
| sing-box | ~/.config/sing-box/config.json |
| Trojan | ~/.config/trojan/config.json |
| Shadowsocks | ~/.config/shadowsocks/config.json |

通用查找：

```bash
find ~ -name "config.yaml" -o -name "config.json" 2>/dev/null | head -20
```

### Q: 我不知道代理的端口号，怎么找出来？

```bash
# 查看配置文件
cat ~/clash/config.yaml | grep -E 'port:|socks-port:|external-controller:'

# 查看所有监听端口
ss -tlnp | grep -v "127.0.0.53" | grep -v "sshd"

# 查看环境变量
env | grep -i proxy

# 用 lsof 查看
sudo lsof -i -P -n | grep LISTEN | grep -E '789[0-9]|1080|9090'
```

### Q: 除了 Clash 还有什么代理工具？

| 工具 | 特点 | 适用 |
|------|------|------|
| Clash | 规则丰富、节点管理好 | 日常使用 |
| Clash Meta | Clash 的增强版 | 需要更多功能 |
| v2ray | 功能全面 | 高级用户 |
| sing-box | 现代化、性能好 | 新项目 |
| Trojan | 隐蔽性好 | 特殊环境 |

```bash
yay -S clash-meta
# 或
yay -S sing-box
```

---

## 5.5 新版：日常用机「默认直连 + 需要时才加速」模式

> 这一批问题是针对"普通日用浏览器/软件走默认网络，只有 Clash 运行时才加速"这一套用法的新增问答，接着上面继续往下排。

### Q: 现在想只让"当前这一个终端"走代理、其它不受影响，用什么指令？

当前默认 shell 是 fish，直接在终端里输入：

```fish
proxyon        # 默认 127.0.0.1:7890（HTTP+SOCKS5 同一混合端口）
proxyon 7891   # 或指定其它端口
proxyoff       # 关闭当前终端代理，恢复默认网络
proxycheck     # 查看当前终端代理状态
```

bash/zsh 里用标准 export：

```bash
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
export all_proxy=socks5://127.0.0.1:7890
# 只对"当前这个终端"生效，关闭终端即失效
unset http_proxy https_proxy all_proxy   # 取消
```

**关键点**：`export` 只影响当前 shell 及其启动的子进程，不影响其它终端、不影响从应用菜单打开的 GUI 程序。

### Q: 想只让"某一个软件/某一条命令"走代理、其它不动？

用 `env` 前缀，只对这一次命令生效：

```bash
# 只让这一条 git clone 走 clash
env https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890 \
    git clone https://github.com/xxx/xxx

# 只让 yay 这一次走代理
env https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890 yay -S 软件名

# 命令行程序通用写法(HTTP代理)
env ALL_PROXY=socks5://127.0.0.1:7890 curl https://www.google.com
```

给 GUI 程序（浏览器等）单独走代理则要看它自己的参数：

```bash
google-chrome-stable --proxy-server="http://127.0.0.1:7890"
# Firefox 不走命令行代理，需在 设置→网络设置 里手动填
```

### Q: 终端能不能做到"Clash 开着就自动加速，Clash 关了就正常上网"？

可以，fish 里已内置自动检测（config.fish 里的 `__proxy_auto`，每次按回车前自动执行一次）：

- 检测到本机有 `127.0.0.1:7890` 端口在监听 → 自动 export 终端代理变量；
- 没检测到 → 自动 unset，走默认网络。

所以：不开 Clash 时 git/AUR/脚本都能正常连国内；`clash` 一开，新敲的命令自动就走代理了。用 `proxycheck` 可随时查看当前是"自动/手动/默认网络"哪种模式。

如果开了自动还想锁死某端口，用 `proxyon <端口>`（会置为手动模式，自动检测不再覆盖）；`proxyoff` 退回自动。

### Q: 现在 `clash` 命令怎么用？为什么以前一输入就显示"已在运行"？

现在把 `clash` 做成了一个管理命令，默认就是启动：

```bash
clash             # 启动(后台)，等价 clash start
clash status      # 查看运行状态、监听端口
clash restart     # 重启
clash stop        # 停止
```

以前的 bug：脚本里用 `pgrep -x clash` 判断是否在运行，而脚本自己文件名也叫 `clash`，于是"自己查到自己"，永远显示已在运行。新版改成**查 9090 API 是否健康 + PID 文件**，不再自误判。

### Q: 为什么以前 Clash 明明开着、端口也设了，浏览器/Steam 还是没加速？

两个常见坑，现已修：

1. **加载了错误的配置**：直接 `cd ~/clash && ./clash`（不带 `-d`）会去读 `~/.config/clash/config.yaml`（一个只有 `mixed-port: 7890`、没有任何节点/规则的残缺文件），当然不加速。现在统一用 `clash` 命令，它强制 `-d ~/clash` 加载真正的 `~/clash/config.yaml`（含节点和规则）。
2. **端口协议对不上**：旧配置里 HTTP 是 7890、SOCKS5 是 7891，两码事。很多软件按"SOCKS5 填 7890"去填，就连不上。现在改成单一 **mixed-port 7890**，同一个端口同时支持 HTTP 和 SOCKS5，任何软件填 `127.0.0.1:7890` 都能通。

### Q: 现在的浏览器/软件网络策略到底是怎么分工的？

| 对象 | 行为 | 说明 |
|------|------|------|
| Chrome / Firefox | 默认直连，不绑任何端口 | 日用浏览器，出问题也从应用菜单启动 |
| 终端里的 git/yay/脚本 | Clash 开→自动加速；关→默认网络 | fish 自动检测，见上文 |
| Mullvad Browser | 自动绑定 `127.0.0.1:7890` | 启动脚本自动写入 profile 的 SOCKS5 代理 |
| Steam | 想加速就用专门命令启动，平时直接开 | 见下一条 |

### Q: Steam 想走 Clash 加速，终端输入什么？

不要改 Steam 本身，启动时手动带代理即可（需先 `clash` 开着）：

```bash
# 方式一：项目自带的加速启动脚本
steamd

# 方式二：或手动等效命令(直接在终端跑)
env http_proxy=http://127.0.0.1:7890 https_proxy=http://127.0.0.1:7890 steam
```

直接点桌面图标开 Steam 就是默认网络、不加速；想要加速每次在终端跑上面任一条即可。

### Q: 怎么确认现在 clash 真在加速（而不是白开）？

```bash
clash status                     # 应显示 7890 在监听
curl -x http://127.0.0.1:7890 -s -m 8 https://www.google.com -o /dev/null -w "%{http_code}\n"   # 期望 200
curl -x socks5://127.0.0.1:7890 -s -m 8 https://www.google.com -o /dev/null -w "%{http_code}\n" # 期望 200
# 出口 IP(应为代理节点所在地区)
curl -x http://127.0.0.1:7890 -s https://ipinfo.io/ip
```

---

## 6. 速查卡片

### 常用命令

| 需求 | 命令 |
|------|------|
| 启动 Clash | `cd ~/clash && ./clash -d ~/clash &` |
| 停止 Clash | `pkill clash` |
| 检查端口 | `ss -tlnp \| grep 7890` |
| 设置代理 | `export https_proxy=http://127.0.0.1:7890` |
| 取消代理 | `unset https_proxy http_proxy all_proxy` |
| 测试代理 | `curl -x http://127.0.0.1:7890 https://google.com -I` |
| 查看出口 IP | `curl -x http://127.0.0.1:7890 https://ipinfo.io/ip` |
| git 代理 | `git config --global http.proxy http://127.0.0.1:7890` |
| 取消 git 代理 | `git config --global --unset http.proxy` |
| 更新订阅 | `curl -o ~/clash/config.yaml "订阅链接"` |
| Dashboard | 浏览器访问 `http://127.0.0.1:9090` |

### 端口速查

| 端口 | 用途 | 配置位置 |
|------|------|---------|
| 7890 | HTTP 代理 | config.yaml → port |
| 7891 | SOCKS5 代理 | config.yaml → socks-port |
| 9090 | Dashboard API | config.yaml → external-controller |
