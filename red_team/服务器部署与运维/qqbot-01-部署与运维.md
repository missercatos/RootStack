
## 整体架构

```mermaid
flowchart LR
    UserQQ[你的日用QQ] -- 发消息 --> QQServer[腾讯QQ服务器]
    QQServer -- 消息推送 --> NapCat[NapCat 协议端<br>基于 NTQQ]
    NapCat -- OneBot v11<br>WebSocket --> AstrBot[AstrBot 机器人框架<br>Python]
    AstrBot -- API调用 --> DeepSeek[DeepSeek V4 Flash<br>AI大模型]
    DeepSeek -- AI回复 --> AstrBot
    AstrBot -- 回复消息 --> NapCat
    NapCat --> QQServer
    QQServer --> UserQQ

    subgraph VPS[海外VPS - Vultr Tokyo/Singapore]
        NapCat
        AstrBot
        Nginx[Nginx 反向代理<br>HTTPS + SSL]
    end

    Admin[管理员浏览器] -- HTTPS --> Nginx
    Nginx -- proxy_pass 6185 --> AstrBot
    Nginx -- proxy_pass 6099 --> NapCat
```

**组件说明：**

| 组件 | 作用 | 端口 |
|------|------|------|
| NapCat | QQ 协议端，基于无头 NTQQ，实现 OneBot v11 标准接口 | 6099(WebUI)，3000/3001(API) |
| AstrBot | AI 机器人中枢，处理消息、调用大模型、插件系统 | 6185(WebUI)，6199(WebSocket) |
| DeepSeek | AI 大模型 API，提供对话能力 | 外部 API(api.deepseek.com) |
| Nginx | 反向代理，提供 HTTPS 加密访问 | 443(HTTPS)，80(HTTP redirect) |


## 第二章：域名与 DNS

### 购买域名

| 注册商 | 特点 |
|--------|------|
| 阿里云 | 国内方便，实名认证，¥20-50/年 |
| Namesilo | 便宜，含隐私保护，~$9/年 |
| Cloudflare | 成本价，但需已有域名转入 |

### DNS 解析设置

在阿里云 DNS 解析中添加 A 记录：

| 记录类型 | 主机记录 | 记录值 | 说明 |
|---------|---------|-------|------|
| A | `bot` | `你的VPS_IP` | 主服务域名: bot.yourdomain.com |
| A | `napcat` | `你的VPS_IP` | NapCat 管理面板子域名 |

### 验证解析

```bash
nslookup bot.yourdomain.com
dig bot.yourdomain.com +short
```

输出应为你的 VPS IP 地址。如果返回 `NXDOMAIN`，说明：
- 域名拼写错误
- DNS 记录未添加或未生效（等待 1-10 分钟）


## 第四章：Docker Compose 部署 NapCat + AstrBot

### 创建项目目录与配置文件

```bash
mkdir -p ~/astrbot && cd ~/astrbot
```

创建 `docker-compose.yml`：

```yaml
version: "3"
services:
  napcat:
    image: mlikiowa/napcat-docker:latest
    container_name: napcat
    restart: always
    environment:
      - MODE=astrbot
    ports:
      - "6099:6099"
    volumes:
      - ./data:/AstrBot/data
      - ./napcat/config:/app/napcat/config
      - ./ntqq:/app/.config/QQ
    networks:
      - astrbot_network
  astrbot:
    image: soulter/astrbot:latest
    container_name: astrbot
    restart: always
    environment:
      - TZ=Asia/Shanghai
    ports:
      - "6185:6185"
    volumes:
      - ./data:/AstrBot/data
    networks:
      - astrbot_network
networks:
  astrbot_network:
    driver: bridge
```

> 重要：NapCat 的环境变量 `MODE=astrbot` 告诉它连接 AstrBot。NapCat 和 AstrBot 必须在**同一个 Docker 网络** 内才能通信。

### 启动

```bash
docker compose up -d
```

### 检查运行状态

```bash
docker ps
```

输出应显示两个容器都在 `Up` 状态：

```
CONTAINER ID   IMAGE                           STATUS          PORTS
xxxxxxxxxxxx   mlikiowa/napcat-docker:latest   Up 5 minutes    0.0.0.0:6099->6099
xxxxxxxxxxxx   soulter/astrbot:latest          Up 5 minutes    0.0.0.0:6185->6185
```


## 第六章：配置 AstrBot

### 访问 AstrBot WebUI

浏览器打开 `http://你的VPS_IP:6185`，默认账号密码为 `astrbot` / `astrbot`，首次登录会要求修改。

### 配置 AI 模型

在 AstrBot 左侧菜单 -> 模型配置：

1. 清空已有配置重新添加，或编辑现有 `deepseek` 提供商
2. 提供商类型：OpenAI API Compatible
3. API 地址：`https://api.deepseek.com/v1`
4. API Key：在 [platform.deepseek.com](https://platform.deepseek.com) 注册获取
5. 模型名：`deepseek-chat` (映射到 DeepSeek V4 Flash)

```json
{
  "type": "openai_chat_completion",
  "api_base": "https://api.deepseek.com/v1",
  "key": ["你的API_KEY"],
  "model": "deepseek-chat"
}
```

### 配置 NapCat 连接适配器

AstrBot 默认可能配置了 `qq_official` 适配器(QQ 官方机器人)。需要改为 `aiocqhttp` 适配器以对接 NapCat。

编辑 `~/astrbot/data/cmd_config.json`，找到 `"platform"` 字段，替换为：

```json
"platform": [
  {
    "type": "aiocqhttp",
    "id": "napcat",
    "enable": true,
    "ws_reverse_host": "0.0.0.0",
    "ws_reverse_port": 6199,
    "token": ""
  }
],
```

然后重启 AstrBot：

```bash
docker restart astrbot
```

### 验证连接

```bash
docker logs astrbot | grep -i "aiocqhttp\|OneBot\|适配器已连接"
```

成功输出：

```
aiocqhttp(OneBot v11) 适配器已连接。
```

### 添加管理员白名单

在 AstrBot WebUI -> 配置 -> 其他配置 -> 管理员 ID，填入你的日用 QQ 号（发给机器人消息的那个号）。


## 第八章：常见排错大全

### 容器相关

#### 1. NapCat 报 ECONNREFUSED

```
[error] 反向WebSocket (ws://astrbot:6199/ws) 连接错误 Error: connect ECONNREFUSED
```

**原因**：AstrBot 没有在监听 6199 端口。可能 astrbot 容器未运行，或配置不正确。

**排查**：
```bash
docker ps | grep astrbot                    # AstrBot 是否在运行
docker exec astrbot ss -tlnp 2>/dev/null | grep 6199  # 是否监听 6199
docker logs astrbot | grep -i "aiocqhttp\|OneBot"     # 适配器是否启动
```

**解决**：检查 `cmd_config.json` 中 `platform` 配置的字段名是否正确。注意 `ws_reverse_host` 和 `ws_reverse_port`，不是 `ws_host` 和 `ws_port`。

```mermaid
flowchart TD
    A[NapCat 报 ECONNREFUSED] --> B{AstrBot 容器在运行吗?}
    B -- 否 --> C[docker compose up -d 启动 AstrBot]
    B -- 是 --> D{平台适配器配置正确吗?}
    D -- 否 --> E[检查 cmd_config.json<br>platform 字段为 aiocqhttp<br>端口 6199]
    D -- 是 --> F[检查两个容器是否同一网络]
    F --> G[docker network inspect astrbot_network]
```

#### 2. JSONDecodeError

```
json.decoder.JSONDecodeError: Expecting ',' delimiter: line 268 column 3
```

**原因**：`cmd_config.json` 中缺少逗号或格式错误。常见于手动编辑 JSON 时在数组或对象之间漏了逗号。

**排查**：
```bash
python3 -c "import json; json.load(open('/root/astrbot/data/cmd_config.json')); print('OK')"
```

如果报错，说明 JSON 格式有问题。

**解决**：用 Python 脚本修复（安全，不会破坏格式）：

```bash
python3 -c "
import json
cfg = json.load(open('/root/astrbot/data/cmd_config.json'))
# 修改你的配置
cfg['platform'] = [{'type': 'aiocqhttp', 'id': 'napcat', 'enable': True, 'ws_reverse_host': '0.0.0.0', 'ws_reverse_port': 6199, 'token': ''}]
json.dump(cfg, open('/root/astrbot/data/cmd_config.json','w'), indent=2)
print('Done')
"
```

> 通用原则：**修改 JSON 文件前先备份** `cp file.json file.json.bak`。始终用程序化方式修改而非 sed/手动编辑。

#### 3. NapCat 需要重新扫码

删除容器重建后需要重新扫码登录 QQ。

```bash
docker logs napcat 2>&1 | grep -i "qr\|二维码\|url"
```

打开二维码 URL 或用手机 QQ 扫码。

### SSL 证书相关

#### 4. 证书验证超时

```
Verification error details: ... Timeout during connect (likely firewall problem)
```

**原因**：Let's Encrypt 无法访问 VPS 的 80 端口。防火墙(云厂商安全组或 ufw)阻挡了入站 80 端口。

**排查**：
```bash
ufw status              # 检查系统防火墙
ss -tlnp | grep 80      # 检查 Nginx 是否监听 80
```

**解决**：开放 `ufw allow 80/tcp`，同时检查 Vultr/DigitalOcean 控制台的防火墙策略。

#### 5. NXDOMAIN 域名不存在

```
server can't find bot.yourdomain.com: NXDOMAIN
```

**排查**：
- 确认域名拼写正确（`.com` vs `.top` vs `.top.com`）
- 确认 DNS A 记录已添加
- 等待 DNS 缓存刷新（1-10 分钟）

#### 6. nginx 指令错误

```
unknown directive "sl_certificate"
```

**原因**：`ssl_certificate` 写成了 `sl_certificate`（漏了字母 s）。

**解决**：检查 Nginx 配置文件中的指令拼写。

### 机器人不回复

#### 7. 消息发送了但无回复

排查链路：
```mermaid
flowchart TD
    A[机器人不回复] --> B{NapCat 收到消息吗?}
    B -- 否 --> C[查看 NapCat 日志<br>检查 QQ 是否在线]
    B -- 是 --> D{AstrBot 收到消息吗?}
    D -- 否 --> E[检查 WebSocket 连接<br>docker logs astrbot]
    D -- 是 --> F{LLM API 调用成功吗?}
    F -- 否 --> G[检查 API Key 和余额<br>检查网络连通性]
    F -- 是 --> H{白名单配置?}
    H -- 不在白名单 --> I[在 WebUI 添加管理员 QQ 号]
```

- 查看 NapCat 是否在线：`docker logs napcat | grep "接收"`
- 查看 AstrBot 日志：`docker logs astrbot --tail 20`
- 检查 WebUI 白名单配置


## 第九章：通用服务器部署技巧

这些技巧不仅适用于 QQ 机器人，适用于**任何服务器端业务**的部署和运维。

### 日志优先原则

任何问题，第一步永远是看日志：

| 场景 | 命令 |
|------|------|
| Docker 容器问题 | `docker logs 容器名 --tail 50` |
| Nginx 问题 | `tail -f /var/log/nginx/error.log` |
| 系统问题 | `journalctl -xe` |
| SSH 登录问题 | `tail -f /var/log/auth.log` |

### 防火墙三层模型

```mermaid
flowchart LR
    A[互联网] --> B[第一层: 云厂商安全组<br>Vultr/AWS/阿里云]
    B --> C[第二层: 系统防火墙<br>ufw / iptables / nftables]
    C --> D[第三层: 应用层鉴权<br>Token / 密码 / IP白名单]
    D --> E[服务]
```

排查连通性问题时，从外到内逐层检查：
1. 先试从外网能 ping 通 IP 吗？
2. 端口能从外网访问吗？(`nc -zv 你的IP 端口`)
3. 云厂商防火墙放行了吗？
4. 系统防火墙放行了吗？
5. 应用本身在监听吗？(`ss -tlnp`)

### Docker 核心原则

- **容器隔离**：每个服务一个容器，不混装
- **网络互通**：需要通信的容器必须在同一 Docker 网络
- **数据持久化**：用 `volumes` 挂载配置文件和数据目录，容器删除后数据不丢
- **重启策略**：`restart: always` 保证崩溃后自动恢复
- **资源限制**：生产环境应限制 CPU 和内存 (`deploy.resources.limits`)

### Nginx 反向代理模板

Nginx 配置可复用于**任何需要 HTTPS 的 Web 服务**，只需改动 `server_name` 和 `proxy_pass`：

```nginx
server {
    listen 443 ssl;
    server_name 你的域名;

    ssl_certificate /path/to/fullchain.cer;
    ssl_certificate_key /path/to/private.key;

    location / {
        proxy_pass http://127.0.0.1:你的本地端口;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

server {
    listen 80;
    server_name 你的域名;
    return 301 https://$server_name$request_uri;
}
```

### JSON 配置安全操作

以 `cmd_config.json` 为例，操作 JSON 配置时应：

1. **备份**：`cp file.json file.json.bak`
2. **验证**：`python3 -c "import json; json.load(open('file.json')); print('valid')"`
3. **修改**：用 Python 脚本或 WebUI 修改，而非 sed
4. **重启应用**使配置生效

### 安全底线清单

| 项目 | 操作 |
|------|------|
| 修改默认密码 | 所有管理面板的第一个操作 |
| 最小端口暴露 | 只开 22/80/443，关闭其他 |
| SSH 密钥认证 | 禁用密码登录，改用密钥 |
| 容器非 root | 避免容器以 root 运行 |
| 定期更新 | `apt update && apt upgrade -y` |
| 监控告警 | 简单可用性监控 |
| SSL 自动化 | acme.sh 自动续期证书 |

---

## 相关知识点

- [[服务器部署与运维总目录]] -- 本目录索引
- [[qqbot-02-红队视角]] -- 面向攻击者的分析
- [[qqbot-03-安全加固]] -- 面向防御者的加固方案
- [[../archstrike-recon教学/01-高级子域名与资产发现]] -- 子域名及服务发现技术
- [[../archstrike-web教学/01-Web基础与HTTP协议]] -- HTTP/HTTPS 协议详解
- [[../archstrike-proxy教学/01-代理与隐蔽通信]] -- 代理隧道技术
- [[../网安基础知识/01-计算机网络基础]] -- 网络基础
