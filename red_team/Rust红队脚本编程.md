
## 为什么红队要用 Rust

> Rust 系统教程：[[../rust/rust目录|Rust 教程总目录]] | [[../路径F-Rust学习路径|Rust 学习路径]]

Rust 正在成为系统编程和安全工具开发的新标准。与传统脚本语言相比，Rust 在红队工作中优势明显：

- **性能**：编译为原生机器码，执行速度远超 Python，适合大规模扫描、哈希破解等计算密集型任务。
- **内存安全**：所有权系统和借用检查器在编译期杜绝了 UAF、缓冲区溢出、悬垂指针等内存漏洞。红队工具本身不该成为被攻击的目标。
- **跨平台编译**：一条命令即可交叉编译到 Windows/Linux/macOS，生成的二进制无需任何运行时依赖，丢到目标机器就能跑。
- **生态系统**：`reqwest`、`tokio`、`pnet`、`clap` 等高质量的 crate 让网络安全开发事半功倍。

Rust 被 NSA、CISA 等机构推荐为内存安全语言的首选。未来 5-10 年，安全工具的主流语言大概率是 Rust。红队队员应当尽早掌握。

> 如果你已经熟悉 Python 安全脚本，可以把 Rust 看做 Python 的「编译后无依赖版」——但更快、更安全。参考 [[补充-Python黑客脚本基础]]。


## 安全脚本开发核心概念

### Cargo 项目起步

```bash
cargo new port_scanner
cd port_scanner
# 在 Cargo.toml 的 [dependencies] 中添加依赖
# cargo build --release
# ./target/release/port_scanner
```

典型的 `Cargo.toml`：

```toml
[package]
name = "red_tools"
version = "0.1.0"
edition = "2021"

[dependencies]
reqwest = { version = "0.12", features = ["blocking"] }
tokio = { version = "1", features = ["full"] }
clap = { version = "4", features = ["derive"] }
rayon = "1.10"
```

### 基础语法速览

```rust
fn main() {
 // 不可变绑定
 let target = "192.168.1.0/24";
 // 可变绑定
 let mut open_ports = Vec::new();

 // if 是表达式
 let verdict = if open_ports.len() > 10 { "活跃" } else { "冷清" };

 // loop + match
 for port in 1..=1024 {
 match scan_port(target, port) {
 Ok(true) => open_ports.push(port),
 Ok(false) => {}
 Err(e) => eprintln!("扫描 {} 端口 {} 失败: {}", target, port, e),
 }
 }
}
```

### 所有权与借用（安全相关要点）

Rust 的所有权规则确保了内存安全，但写安全工具时要注意：

```rust
// 所有权转移：适合消息传递式的并发架构（channel）
let data = vec![1, 2, 3];
std::thread::spawn(move || {
 println!("{:?}", data); // data 的所有权移入线程
});

// 借用：多个线程只读访问用 Arc
use std::sync::Arc;
let targets = Arc::new(vec!["host1", "host2", "host3"]);
for _ in 0..3 {
 let t = Arc::clone(&targets);
 std::thread::spawn(move || {
 println!("{}", t[0]); // 只读借用
 });
}
```

红队中最常见的模式是 `Arc<Mutex<T>>` 用于共享扫描结果，以及 `mpsc::channel` 用于生产者-消费者模式。

### 错误处理

安全工具不能随便 panic。一律用 `Result` + `?` 操作符：

```rust
use std::io;

fn read_targets(path: &str) -> Result<Vec<String>, io::Error> {
 let content = std::fs::read_to_string(path)?;
 Ok(content.lines().map(String::from).collect())
}
// 调用时
match read_targets("targets.txt") {
 Ok(hosts) => println!("加载了 {} 个目标", hosts.len()),
 Err(e) => eprintln!("读取失败: {}", e),
}
```

### 常用 Crate 一览

| Crate | 用途 | 红队场景 |
|-------|------|----------|
| `reqwest` | HTTP 客户端 | 爆破、目录扫描、信息收集 |
| `tokio` | 异步运行时 | 高并发扫描、网络请求 |
| `rayon` | 数据并行 | 多线程端口扫描、哈希计算 |
| `clap` | CLI 参数解析 | 所有工具的命令行接口 |
| `serde` / `serde_json` | 序列化 | 处理 API 响应、配置文件 |
| `pnet` | 原始套接字 | 包构造、嗅探、SYN 扫描 |
| `trust-dns-resolver` | DNS 解析 | 子域名枚举 |
| `rustls` | TLS 库 | HTTPS 请求（替代 OpenSSL） |
| `base64` | Base64 编解码 | 载荷编码 |
| `rand` | 随机数 | 生成随机 UA、延迟等 |


## Rust vs Python：何时用哪个

| 维度 | Rust | Python |
|------|------|--------|
| **执行速度** | 极快（原生） | 慢（解释执行） |
| **内存占用** | 极低 | 较高 |
| **开发速度** | 较慢（编译、生命周期标注） | 极快 |
| **部署** | 单文件二进制，零依赖 | 需解释器 + pip 包 |
| **并发模型** | tokio（真异步）、rayon（数据并行） | asyncio（GIL 限制） |
| **网络库** | reqwest、pnet | requests、scapy |
| **学习曲线** | 陡峭 | 平缓 |
| **适合场景** | 持久化工具、高并发扫描、载荷生成、OPSEC 敏感任务 | 快速原型、一次性脚本、后渗透利用 |

**实战建议**：

- 先用 Python 快速验证思路（10 分钟搞定），确认可行后用 Rust 重写为生产版本。
- 需要丢到目标机器长期运行的工具（C2 agent、持久化、keylogger）优先 Rust。
- 临时的一次性任务、与 Metasploit/CobaltStrike 交互的脚本，Python 仍是首选。
- Rust 的二进制体积可以通过 `strip` / `UPX` / `opt-level = "z"` + `lto = true` 控制在数百 KB 以内，非常适合做小体积 payload。
- 参考 [[补充-Python黑客脚本基础]] 对比两边的实现方式。


## 扩展资源

### 书籍

- **The Rust Book**（官方免费）：https://doc.rust-lang.org/book/ — 必读圣经。
- **Rust By Example**：https://doc.rust-lang.org/stable/rust-by-example/ — 实战练习。
- **Black Hat Rust**（付费）：https://kerkour.com/black-hat-rust — 唯一专注于攻击性安全的 Rust 书籍，涵盖扫描器、C2、shellcode 注入、勒索软件等。
- **Rust for Rustaceans**：进阶 idiom 和设计模式。

### 开源安全工具参考

| 项目 | GitHub | 说明 |
|------|--------|------|
| RustScan | https://github.com/RustScan/RustScan | 极速端口扫描器 |
| feroxbuster | https://github.com/epi052/feroxbuster | Rust 写的目录爆破器 |
| xh | https://github.com/ducaale/xh | 类似 httpie 的 HTTP 客户端 |
| sniffglue | https://github.com/kpcyrd/sniffglue | 安全嗅探器 |
| mqtt2psql | https://github.com/kpcyrd/mqtt2psql | Arch Linux 安全研究员的 Rust 工具集 |
| kerberoast | https://github.com/n4r1b/kerberoast-rs | Kerberoasting 工具 |

### 在线资源

- **Rust Playground**：https://play.rust-lang.org/ — 在线写 Rust 无需安装。
- **crates.io**：https://crates.io/ — Rust 官方包仓库。
- **docs.rs**：https://docs.rs/ — 所有 crate 的自动生成文档。
- **Rust Security 周报**：https://rustsec.org/ — Rust 生态安全漏洞公告。

---

> 下一篇推荐阅读：`红队队员完整学习手册` (已归档) — 将所有技能串联成完整攻击链。
