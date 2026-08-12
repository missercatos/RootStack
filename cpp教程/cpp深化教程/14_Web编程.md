# Web 编程

## 原理

### TCP/IP 四层模型

```
应用层 ← HTTP, HTTPS, FTP, DNS
传输层 ← TCP (可靠), UDP (不可靠), 端口号标识应用
网络层 ← IP (路由转发), ICMP, ARP
数据链路层 ← Ethernet, Wi-Fi, MAC 地址标识设备
物理层 ← 传输介质（双绞线/光纤/电磁波）
```

数据发送时自上而下封装——每层添加自己的头部。接收时自下而上解封装。

### TCP 三次握手

```
Client → Server: SYN (seq=x) "我要连接"
Server → Client: SYN+ACK (seq=y, ack=x+1) "我收到了，可以连接"
Client → Server: ACK (ack=y+1) "我收到了你的确认"
```

为什么是三次而不是两次？假设只有两次握手——Client 发送 SYN 后因网络延迟被重传，旧 SYN 稍后才到 Server。Server 分配资源建立连接，但 Client 已经不需要这个连接了。三次握手让 Client 可以不回复 ACK，Server 就知道该连接请求是无效的。

### TCP 四次挥手

```
Client → Server: FIN "我不发数据了"
Server → Client: ACK "收到"
Server → Client: FIN "我也不发了"（可能间隔一段时间，期间 Server 仍可发数据）
Client → Server: ACK "收到"
（Client 进入 TIME_WAIT，等待 2MSL 约 1-4 分钟）
```

TIME_WAIT 的作用：确保最后的 ACK 被对方收到；让旧连接的迟到报文在网络中消亡。这也是 `SO_REUSEADDR` 存在的原因——允许服务器重启时立即绑定端口。

### Socket 的本质

Socket 是一个特殊的文件描述符。`socket()` 调用时内核创建的数据结构包含：发送缓冲区、接收缓冲区、TCP 控制块（状态机、序列号、窗口大小）、等待队列。可以用 `close()` 关闭（像关闭文件一样），可以用 `fcntl()` 设置非阻塞，可以用 `select/poll/epoll` 进行多路复用。

默认缓冲区大小：约 212992 字节（可通过 `SO_RCVBUF`/`SO_SNDBUF` 调整）。

### epoll 多路复用

同时处理成千上万个连接时，为每个连接创建线程不现实。epoll 允许一个线程高效监控大量文件描述符：

1. `epoll_create1()` — 创建 epoll 实例，内核分配 eventpoll 结构体（含红黑树 + 就绪链表）
2. `epoll_ctl()` — 注册/修改/删除要监控的 fd
3. `epoll_wait()` — 等待事件，只返回就绪的 fd（O(1) 的是活跃连接，与总 fd 数无关）

epoll 的两种触发模式：
- **水平触发（LT，默认）**：只要 fd 状态可读/写，持续通知——与 select/poll 行为一致
- **边缘触发（ET）**：只有状态变化时通知一次——性能更高但编程更复杂，必须配合非阻塞 I/O

### 阻塞 vs 非阻塞 I/O

- **阻塞模式（默认）**：recv() 没有数据时进程进入睡眠状态（TASK_INTERRUPTIBLE）；send() 缓冲区满时同样睡眠
- **非阻塞模式**：通过 `fcntl(sock, F_SETFL, flags | O_NONBLOCK)` 设置——数据未就绪时立即返回 -1，errno = EAGAIN/EWOULDBLOCK

### HTTP 协议格式

```
请求行：GET /path HTTP/1.1\r\n
请求头：Host: www.example.com\r\n
 Content-Type: application/json\r\n
 Content-Length: 27\r\n
空行： \r\n
请求体：{"key": "value"}
```

常见状态码：200 OK, 201 Created, 301 永久移动, 400 Bad Request, 403 Forbidden, 404 Not Found, 500 Internal Server Error。

### 字节序

网络字节序采用大端序（big-endian）。x86/ARM 主机通常用小端序。Socket API 中需要转换：
- `htons()`/`htonl()` — 主机序→网络序（16/32 位）
- `ntohs()`/`ntohl()` — 网络序→主机序

---

## 语法

### Socket API（POSIX）

```cpp
int sock = socket(AF_INET, SOCK_STREAM, 0); // TCP
// AF_INET: IPv4; SOCK_STREAM: TCP; SOCK_DGRAM: UDP

struct sockaddr_in addr;
addr.sin_family = AF_INET;
addr.sin_port = htons(8080);
inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);

connect(sock, (struct sockaddr*)&addr, sizeof(addr));
send(sock, data, len, 0);
recv(sock, buffer, sizeof(buffer), 0);
close(sock);
```

### 服务器端

```cpp
int server = socket(AF_INET, SOCK_STREAM, 0);
bind(server, (struct sockaddr*)&addr, sizeof(addr));
listen(server, backlog);
int client = accept(server, (struct sockaddr*)&client_addr, &len);
// 对 client 进行 send/recv 操作
```

### setsockopt 常用选项

```cpp
int opt = 1;
setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)); // 端口重用
setsockopt(sock, IPPROTO_TCP, TCP_NODELAY, &opt, sizeof(opt)); // 禁用 Nagle
```

### getaddrinfo 协议无关解析

```cpp
struct addrinfo hints = {};
hints.ai_family = AF_UNSPEC; // IPv4 + IPv6
hints.ai_socktype = SOCK_STREAM;
struct addrinfo* result;
getaddrinfo("example.com", "80", &hints, &result);
// 遍历 result 链表，依次尝试 connect
freeaddrinfo(result);
```

### RAII Socket 封装

```cpp
class Socket {
 int fd;
public:
 Socket(int domain, int type) : fd(socket(domain, type, 0)) {}
 ~Socket() { if (fd >= 0) close(fd); }
 Socket(Socket&& other) noexcept : fd(other.fd) { other.fd = -1; }
 Socket(const Socket&) = delete;
};
```

---

## 实践

**力扣题目**：无专属练习题。网络编程在算法竞赛中不使用，但在工程中至关重要。建议实践：1) 用 epoll 写一个单线程的 echo 服务器，支持 10000+ 并发连接；2) 用 HTTP 请求从公开 API 拉取 JSON 数据，用字符串流解析响应。

**AI 自检**：要求 AI 解释 epoll 水平触发和边缘触发的区别，给出带有 `EPOLLET` 的边缘触发版本的 `recv` 循环代码。

**建议先阅读**：[[13_多线程]] — 网络服务器的并发连接处理；[[11_文件与流]] — 缓冲区模型与阻塞的本质；[[10_异常处理]] — 网络错误的异常处理。
