# 文件传输：scp, rsync, ftp | File Transfer

## 章节概述

> **核心理念**：文件传输是远程协作的基础——从简单的 scp 复制到 rsync 增量同步，每个工具都有其独特的使用场景。掌握这些工具就像理解 C 语言的文件 I/O 一样重要。

---

### 第1节：scp 选项详解

#### 1.1 基础用法

```bash
# 复制文件到远程
scp file.txt user@remote:/path/to/destination/

# 从远程复制文件
scp user@remote:/path/to/file.txt /local/path/

# 复制目录（递归）
scp -r /local/directory user@remote:/path/to/destination/

# 复制多个文件
scp file1.txt file2.txt user@remote:/path/to/destination/
```

#### 1.2 高级选项

```bash
# 指定端口
scp -P 2222 file.txt user@remote:/path/

# 使用压缩
scp -C large_file.tar.gz user@remote:/path/

# 限制带宽（KB/s）
scp -l 1000 file.txt user@remote:/path/

# 保持权限和时间戳
scp -p file.txt user@remote:/path/

# 使用特定 SSH 密钥
scp -i ~/.ssh/mykey.pem file.txt user@remote:/path/

# 显示进度
scp -v file.txt user@remote:/path/
```

#### 1.3 scp 与 cp 对比

| 特性 | cp | scp |
|------|-----|-----|
| 本地复制 | 支持 | 不支持 |
| 远程复制 | 不支持 | 支持 |
| 递归复制 | `-r` | `-r` |
| 保留属性 | `-p` | `-p` |
| 压缩 | 不支持 | `-C` |
| 端口指定 | 不适用 | `-P` |

### 第2节：SSH 密钥认证

#### 2.1 生成密钥对

```bash
# 生成 RSA 密钥
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa

# 生成 Ed25519 密钥（更安全）
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519

# 生成带密码的密钥
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N "password"

# 查看公钥
cat ~/.ssh/id_rsa.pub
```

#### 2.2 部署公钥

```bash
# 使用 ssh-copy-id
ssh-copy-id -i ~/.ssh/id_rsa.pub user@remote

# 手动部署
cat ~/.ssh/id_rsa.pub | ssh user@remote "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"

# 设置正确权限
ssh user@remote "chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
```

#### 2.3 SSH 配置

```bash
# ~/.ssh/config
Host myserver
    HostName 192.168.1.100
    User admin
    Port 2222
    IdentityFile ~/.ssh/id_rsa
    ForwardAgent yes

Host bastion
    HostName bastion.example.com
    User admin
    IdentityFile ~/.ssh/id_ed25519

# 使用配置
scp file.txt myserver:/path/
ssh myserver
```

### 第3节：rsync 增量同步

#### 3.1 基础用法

```bash
# 同步目录（注意尾部斜杠）
rsync -av /source/ user@remote:/destination/

# 不带尾部斜杠（复制目录本身）
rsync -av /source user@remote:/destination/

# 从远程同步到本地
rsync -av user@remote:/source/ /local/destination/
```

#### 3.2 常用选项

```bash
# 归档模式（保留权限、时间戳等）
rsync -av source/ dest/

# 详细输出
rsync -avv source/ dest/

# 模拟运行（不实际执行）
rsync -avn source/ dest/

# 删除目标中源没有的文件
rsync -av --delete source/ dest/

# 排除特定文件
rsync -av --exclude='*.log' --exclude='.git' source/ dest/

# 包含特定文件
rsync -av --include='*.py' --exclude='*' source/ dest/

# 压缩传输
rsync -avz source/ user@remote:/dest/

# 限制带宽（KB/s）
rsync -av --bwlimit=1000 source/ dest/

# 显示进度
rsync -avP source/ dest/

# 使用 SSH 和指定端口
rsync -avz -e "ssh -p 2222" source/ user@remote:/dest/
```

#### 3.3 rsync 高级用法

```bash
# 只同步新文件（不更新已存在的）
rsync -av --ignore-existing source/ dest/

# 只更新比目标新的文件
rsync -av --update source/ dest/

# 保持硬链接
rsync -avH source/ dest/

# 保留 ACL
rsync -avA source/ dest/

# 保留扩展属性
rsync -avX source/ dest/

# 备份并保留旧文件
rsync -av --backup --suffix=.backup source/ dest/

# 使用校验和而非时间戳
rsync -avc source/ dest/

# 日志文件
rsync -av --log-file=/var/log/rsync.log source/ dest/
```

#### 3.4 rsync 过滤规则

```bash
# 创建过滤规则文件
cat > /tmp/rsync-filter.txt << 'EOF'
- .git/
- *.log
- __pycache__/
- node_modules/
+ *.py
+ *.js
- *
EOF

# 使用过滤规则
rsync -av --filter='merge /tmp/rsync-filter.txt' source/ dest/

# 内联过滤规则
rsync -av --exclude='.git' --exclude='*.log' --include='*.py' --exclude='*' source/ dest/
```

### 第4节：sftp 批量操作

#### 4.1 交互式 sftp

```bash
# 连接 sftp 服务器
sftp user@remote

# 常用命令
# ls      - 列出远程目录
# lls     - 列出本地目录
# cd      - 切换远程目录
# lcd     - 切换本地目录
# get     - 下载文件
# put     - 上传文件
# mkdir   - 创建远程目录
# rm      - 删除远程文件
# exit    - 退出
```

#### 4.2 批量 sftp 操作

```bash
# 从文件执行 sftp 命令
cat > /tmp/sftp-commands.txt << 'EOF'
cd /remote/path
mkdir new_directory
put local_file.txt
get remote_file.txt
chmod 755 remote_file.txt
EOF

sftp -b /tmp/sftp-commands.txt user@remote

# 使用 here document
sftp user@remote << 'EOF'
cd /remote/path
put *.txt
get *.log
EOF
```

#### 4.3 sftp 与 scp 对比

| 特性 | scp | sftp |
|------|-----|------|
| 单次传输 | 更简单 | 需要命令 |
| 批量操作 | 需要循环 | 原生支持 |
| 交互式 | 不支持 | 支持 |
| 断点续传 | 不支持 | 部分支持 |
| 目录浏览 | 不支持 | 支持 |
| 文件管理 | 不支持 | 支持 |

### 第5节：断点续传

#### 5.1 wget 断点续传

```bash
# 断点续传下载
wget -c https://example.com/large-file.zip

# 后台下载并断点续传
wget -bc https://example.com/large-file.zip

# 查看后台任务
cat wget-log
```

#### 5.2 curl 断点续传

```bash
# 断点续传
curl -C - -O https://example.com/large-file.zip

# 续传并限制速度
curl -C - --limit-rate 100K -O https://example.com/large-file.zip
```

#### 5.3 rsync 天然支持断点续传

```bash
# rsync 本身就是增量同步，天然支持断点续传
rsync -avP user@remote:/large-file.zip ./

# 使用 --partial 保留部分传输的文件
rsync -av --partial user@remote:/large-file.zip ./
```

### 第6节：综合实战

#### 6.1 自动备份脚本

```bash
#!/bin/bash
# 自动备份脚本

# 配置
REMOTE_USER="backup"
REMOTE_HOST="backup-server.example.com"
REMOTE_DIR="/backups"
LOCAL_DIR="/data"
BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="/var/log/backup.log"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# 执行备份
log "Starting backup: $BACKUP_NAME"

rsync -avz --delete \
    -e "ssh -i ~/.ssh/backup_key" \
    --exclude='*.tmp' \
    --exclude='.cache' \
    "$LOCAL_DIR/" \
    "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/$BACKUP_NAME/" \
    2>&1 | tee -a "$LOG_FILE"

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    log "Backup completed successfully"
    
    # 创建符号链接
    ssh -i ~/.ssh/backup_key "$REMOTE_USER@$REMOTE_HOST" \
        "ln -sfn $REMOTE_DIR/$BACKUP_NAME $REMOTE_DIR/latest"
else
    log "Backup failed"
    exit 1
fi
```

#### 6.2 网站同步脚本

```bash
#!/bin/bash
# 网站同步脚本（开发到生产）

SOURCE="./public/"
DEST="user@production:/var/www/html/"

echo "=== Syncing website ==="

rsync -avz --progress \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='.env' \
    --delete \
    "$SOURCE" "$DEST"

echo "=== Sync complete ==="
```

#### 6.3 增量备份到 S3

```bash
#!/bin/bash
# 使用 s3cmd 增量备份到 S3

LOCAL_DIR="/data"
S3_BUCKET="s3://my-backup-bucket"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
STATE_FILE="/var/lib/backup-state"

# 使用 rsync 风格的增量备份
aws s3 sync "$LOCAL_DIR" "$S3_BUCKET/$TIMESTAMP/" \
    --exclude "*.tmp" \
    --exclude "*.log"

# 更新最新符号链接
aws s3 cp "$S3_BUCKET/$TIMESTAMP/" "$S3_BUCKET/latest/" --recursive

# 清理 30 天前的备份
aws s3 ls "$S3_BUCKET/" | \
    awk '{print $2}' | \
    grep -E '^[0-9]{8}_[0-9]{6}/$' | \
    while read dir; do
        dir_date=$(echo "$dir" | cut -d_ -f1)
        if [[ $(date -d "$dir_date" +%s) -lt $(date -d "30 days ago" +%s) ]]; then
            echo "Deleting old backup: $dir"
            aws s3 rm "$S3_BUCKET/$dir" --recursive
        fi
    done
```
