# dpkg 与 deb 打包

> dpkg 是 Debian 包管理的底层工具，apt 依赖 dpkg 执行实际的包操作。本章覆盖 dpkg 命令参考、手动创建 .deb 包、维护脚本编写、debhelper 构建系统和 reprepro 本地仓库。

---

## 1. 资源链接

| 资源 | 链接 |
|------|------|
| Debian 打包指南 | https://www.debian.org/doc/debian-policy/ |
| Debian 新维护者指南 | https://www.debian.org/doc/manuals/maint-guide/ |
| Debian 官方下载 | https://www.debian.org/download |
| 清华镜像 | https://mirrors.tuna.tsinghua.edu.cn/debian/ |
| 中科大镜像 | https://mirrors.ustc.edu.cn/debian/ |
| Ubuntu 打包指南 | https://packaging.ubuntu.com/ |

---

## 2. dpkg 命令完整参考

### 2.1 包管理

```bash
# 安装 .deb 包（不处理依赖）
sudo dpkg -i package.deb

# 安装后自动修复依赖
sudo dpkg -i package.deb && sudo apt install -f

# 删除包（保留配置）
sudo dpkg -r packagename

# 完全删除（包括配置）
sudo dpkg -P packagename

# 列出所有已安装的包
dpkg -l

# 列出特定包的版本和状态
dpkg -l packagename

# 查看 .deb 包的内容（未安装）
dpkg -c package.deb
dpkg --contents package.deb

# 查看 .deb 包的信息
dpkg -I package.deb
dpkg --info package.deb
```

### 2.2 查询已安装的包

```bash
# 查看包的详细状态
dpkg -s packagename

# 列出包安装的所有文件
dpkg -L packagename

# 查找某个文件属于哪个包
dpkg -S /path/to/file

# 查找部分文件名属于哪个包
dpkg -S '*libfoo*'

# 查看系统架构
dpkg --print-architecture

# 查看可用的外部架构（如 i386 兼容）
dpkg --print-foreign-architectures

# 添加 i386 架构支持
sudo dpkg --add-architecture i386
```

### 2.3 包状态操作

```bash
# 重新配置已安装的包（运行 postinst 脚本）
sudo dpkg-reconfigure packagename

# 对未正确配置的包执行配置
sudo dpkg --configure -a

# 查看包的 conffile（配置文件）状态
dpkg --status packagename | grep -A5 "Conffiles"

# 审计：检查哪些安装的包文件被修改过
sudo dpkg --verify

# 验证特定包
sudo dpkg --verify packagename
```

### 2.4 强制操作（高级）

```bash
# 强制覆盖文件
sudo dpkg --force-overwrite -i package.deb

# 强制删除（忽略依赖）
sudo dpkg --force-depends -r packagename

# 忽略全部冲突（极度危险）
sudo dpkg --force-all -i package.deb

# 强制架构
sudo dpkg --force-architecture -i package.deb

# 查看所有强制选项
dpkg --force-help

# 解除 hold（禁止升级）标记
sudo dpkg --set-selections <<< "packagename install"

# 设置 hold 标记
sudo dpkg --set-selections <<< "packagename hold"
```

### 2.5 包列表导出与恢复

```bash
# 导出所有已安装包
dpkg --get-selections > pkg-list.txt

# 导出包及其标记（install/deinstall/purge/hold）
dpkg --get-selections "*" > full-selections.txt

# 从列表恢复（在新系统上）
sudo dpkg --set-selections < pkg-list.txt
sudo apt-get dselect-upgrade

# 只导出显式安装的包（apt 层面）
apt-mark showmanual > manual-pkgs.txt
```

---

## 3. dpkg 数据库

### 3.1 数据库结构

```bash
# dpkg 数据库位置
ls /var/lib/dpkg/

# 主要文件和目录：
# status          — 已安装包的完整状态
# available       — 可安装包的缓存
# info/           — 每个包的控制文件和脚本
#   pkgname.list    — 包的文件列表
#   pkgname.md5sums — 文件校验和
#   pkgname.postinst — 安装后脚本
#   pkgname.prerm    — 删除前脚本
# updates/        — 未完成的更新
# diversions      — 文件转移
# statoverride    — 文件所有者覆盖
```

### 3.2 数据库查询

```bash
# 查看包的所有维护脚本
ls /var/lib/dpkg/info/packagename.*

# 查看包安装的文件列表
cat /var/lib/dpkg/info/packagename.list

# 查看包 conffiles
cat /var/lib/dpkg/info/packagename.conffiles

# 搜索包含特定文件的包
grep -l "filename" /var/lib/dpkg/info/*.list
```

---

## 4. 创建 .deb 包基础

### 4.1 最小 deb 包结构

```
myapp-1.0.0/
├── DEBIAN/
│   └── control         # 包元数据（必需）
│   ├── preinst         # 安装前脚本（可选）
│   ├── postinst        # 安装后脚本（可选）
│   ├── prerm           # 删除前脚本（可选）
│   ├── postrm          # 删除后脚本（可选）
│   ├── conffiles       # 配置文件列表（可选）
│   └── md5sums         # 文件校验
└── usr/
    ├── bin/myapp
    ├── share/
    │   ├── doc/myapp/copyright
    │   └── applications/myapp.desktop
    └── lib/myapp/
```

### 4.2 control 文件完整字段

```
Package: myapp
Version: 1.2.3-1
Section: utils
Priority: optional
Architecture: amd64
Essential: no
Maintainer: Your Name <you@example.com>
Uploaders: Co-maintainer <co@example.com>
Homepage: https://example.com/myapp
Description: 简短描述（≤60字符）
 长描述，可以多行。
 每行开头留一个空格。
 段落间用 " ." 空行分隔。
 .
 这是第三段描述。

Depends: libc6 (>= 2.31), python3
Recommends: python3-requests
Suggests: python3-lxml
Pre-Depends: ${misc:Pre-Depends}
Conflicts: old-myapp
Provides: virtual-myapp
Replaces: old-myapp
Breaks: some-other-package (<< 2.0)
Built-Using: gcc-12 (= 12.2.0-14)
Installed-Size: 1524
```

### 4.3 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `Package` | ✓ | 包名，只能小写字母、数字、`-`、`+`、`.` |
| `Version` | ✓ | 格式：`上游版本-Debian修订版本`，如 `1.2.3-1` |
| `Architecture` | ✓ | `amd64`、`i386`、`arm64`、`all`、`any` |
| `Maintainer` | ✓ | 维护者姓名和邮箱 |
| `Description` | ✓ | 第一行是简短描述，后续段落是长描述 |
| `Depends` | | 运行时强制依赖 |
| `Pre-Depends` | | 在解包前就必须安装的依赖 |
| `Recommends` | | 推荐安装（默认会安装） |
| `Suggests` | | 建议安装（不会自动安装） |
| `Conflicts` | | 冲突的包名 |
| `Provides` | | 此包提供的虚拟包名 |
| `Replaces` | | 替换的文件来自哪个包 |
| `Breaks` | | 破坏指定版本的包 |
| `Section` | | 分类：`utils`、`net`、`devel`、`admin` 等 |
| `Priority` | | `required`、`important`、`standard`、`optional`、`extra` |
| `Essential` | | `yes` 表示系统必需，包管理器不可删除 |
| `Homepage` | | 项目主页 URL |
| `Installed-Size` | | 安装后占用磁盘空间（KB），由构建工具自动填写 |

### 4.4 构建 .deb 包

```bash
# Level 1：最原始方式（dpkg-deb 手动打包）

# 1. 创建目录结构
mkdir -p myapp-1.0.0/DEBIAN
mkdir -p myapp-1.0.0/usr/bin
mkdir -p myapp-1.0.0/usr/share/doc/myapp

# 2. 编写 control 文件
cat > myapp-1.0.0/DEBIAN/control << 'EOF'
Package: myapp
Version: 1.0.0-1
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Your Name <you@example.com>
Description: My first deb package
 This is a simple example of creating a deb package manually.
EOF

# 3. 放入文件
cp myapp_script.sh myapp-1.0.0/usr/bin/myapp
chmod 755 myapp-1.0.0/usr/bin/myapp

cat > myapp-1.0.0/usr/share/doc/myapp/copyright << 'EOF'
Copyright (c) 2025 Your Name
Licensed under MIT License.
EOF

# 4. 打包
dpkg-deb --build myapp-1.0.0/
# 生成 myapp-1.0.0.deb

# 5. 命名规范（可选改名）
mv myapp-1.0.0.deb myapp_1.0.0-1_amd64.deb

# 6. 检查包质量
lintian myapp_1.0.0-1_amd64.deb

# 7. 查看包内容
dpkg -c myapp_1.0.0-1_amd64.deb
dpkg -I myapp_1.0.0-1_amd64.deb
```

---

## 5. 维护脚本（Maintainer Scripts）

### 5.1 四个脚本及其调用时机

| 脚本 | 调用时机 | 参数 |
|------|---------|------|
| `preinst` | 包文件解压前 | `install` 或 `upgrade 旧版本` |
| `postinst` | 包文件解压后 | `configure 最新版本` |
| `prerm` | 包文件删除前 | `remove` 或 `upgrade 新版本` 或 `deconfigure` |
| `postrm` | 包文件删除后 | `remove` 或 `purge` 或 `upgrade 新版本` |

### 5.2 postinst 示例

```bash
#!/bin/bash
# DEBIAN/postinst
set -e

case "$1" in
    configure)
        # 创建系统用户
        if ! getent passwd myapp >/dev/null; then
            adduser --system --group --home /var/lib/myapp --no-create-home myapp
        fi

        # 设置目录权限
        chown -R myapp:myapp /var/lib/myapp
        chmod 755 /var/lib/myapp

        # 启动服务
        if [ -x /bin/systemctl ]; then
            systemctl daemon-reload
            systemctl enable myapp.service
            systemctl start myapp.service || true
        fi

        echo "myapp 安装完成。"
        ;;

    abort-upgrade|abort-remove|abort-deconfigure)
        ;;

    *)
        echo "postinst called with unknown argument \`$1'" >&2
        exit 1
        ;;
esac

exit 0
```

### 5.3 prerm 示例

```bash
#!/bin/bash
# DEBIAN/prerm
set -e

case "$1" in
    remove|upgrade|deconfigure)
        # 停止服务
        if [ -x /bin/systemctl ]; then
            systemctl stop myapp.service || true
            systemctl disable myapp.service || true
        fi
        ;;

    failed-upgrade)
        ;;

    *)
        echo "prerm called with unknown argument \`$1'" >&2
        exit 1
        ;;
esac

exit 0
```

### 5.4 postrm 示例

```bash
#!/bin/bash
# DEBIAN/postrm
set -e

case "$1" in
    purge)
        # 删除系统用户和数据（仅 purge 时）
        if getent passwd myapp >/dev/null; then
            userdel myapp
        fi
        rm -rf /var/lib/myapp
        ;;

    remove|upgrade|failed-upgrade|abort-install|abort-upgrade|disappear)
        ;;

    *)
        echo "postrm called with unknown argument \`$1'" >&2
        exit 1
        ;;
esac

exit 0
```

### 5.5 conffiles

```
# DEBIAN/conffiles
# 列出被标记为配置文件的文件路径
# dpkg 不会覆盖这些文件，而会将新版本保存为 .dpkg-new
/etc/myapp/config.yml
/etc/myapp/settings.ini
/etc/logrotate.d/myapp
```

---

## 6. debhelper 构建系统

### 6.1 dh_make 初始化

```bash
# 安装打包工具
sudo apt install dh-make devscripts build-essential fakeroot lintian

# 准备源码
tar -czf myapp-1.0.0.tar.gz myapp-1.0.0/

cd myapp-1.0.0/
export DEBEMAIL="you@example.com"
export DEBFULLNAME="Your Name"

# 初始化 Debian 打包目录
dh_make -f ../myapp-1.0.0.tar.gz

# 选择包类型（s: single binary, m: multiple binary, l: library...）
# 通常选择 s
```

### 6.2 debian/ 目录结构

```
myapp-1.0.0/
├── src/                    # 上游源码
└── debian/
    ├── changelog           # 变更日志
    ├── control             # 包元数据
    ├── rules               # 构建规则（Makefile）
    ├── copyright           # 版权信息
    ├── compat              # debhelper 兼容性级别
    ├── install             # 文件安装映射
    ├── dirs                # 需要创建的目录
    ├── links               # 符号链接
    ├── postinst            # 安装后脚本
    ├── prerm               # 删除前脚本
    ├── postrm              # 删除后脚本
    ├── conffiles           # 配置文件
    ├── watch               # 监控上游新版本
    └── source/
        └── format          # 源码格式（"3.0 (quilt)"）
```

### 6.3 debian/rules

```makefile
#!/usr/bin/make -f

# 使用 dh 简化的最小 rules：
%:
	dh $@

# 覆盖特定步骤：
override_dh_auto_configure:
	./configure --prefix=/usr --sysconfdir=/etc

override_dh_auto_build:
	$(MAKE)

override_dh_auto_test:
	$(MAKE) test

override_dh_auto_install:
	$(MAKE) install DESTDIR=$$(pwd)/debian/myapp

override_dh_compress:
	dh_compress -X.yml

override_dh_usrlocal:
	# 禁止安装到 /usr/local
```

### 6.4 debian/install

```
# 格式：<源码路径> <目标路径>
src/myapp          usr/bin/
src/config.yml     etc/myapp/
src/systemd/myapp.service    lib/systemd/system/
```

### 6.5 构建包

```bash
# 使用 debuild 构建（推荐）
debuild -us -uc
# -us  不签名源码包
# -uc  不签名 .changes 文件

# 或使用 dpkg-buildpackage
dpkg-buildpackage -us -uc -ui

# 或使用 pbuilder/cowbuilder（干净 chroot 环境）
sudo apt install pbuilder
sudo pbuilder create
sudo pbuilder build ../myapp_1.0.0-1.dsc

# 检查包
lintian ../myapp_1.0.0-1_amd64.changes
```

### 6.6 debian/changelog 格式

```
myapp (1.0.0-1) unstable; urgency=medium

  * Initial release. (Closes: #123456)
  * Added systemd service file.
  * Fixed segmentation fault on amd64.

 -- Your Name <you@example.com>  Wed, 15 Jan 2025 10:00:00 +0800
```

生成 changelog 条目：

```bash
dch -i             # 交互式添加新条目
dch -r ""          # 标记为 release
dch --bpo           # 标记为 backports 版本
```

---

## 7. dh 命令速查

| 命令 | 作用 |
|------|------|
| `dh_auto_configure` | 自动检测并运行配置 |
| `dh_auto_build` | 自动检测并编译 |
| `dh_auto_test` | 自动检测并测试 |
| `dh_auto_install` | 安装到 debian/tmp/ |
| `dh_install` | 根据 .install 文件复制文件 |
| `dh_installdocs` | 安装文档 |
| `dh_installman` | 安装 man 手册 |
| `dh_installinit` | 安装 init/systemd 脚本 |
| `dh_installsystemd` | 安装并启用 systemd 服务 |
| `dh_installchangelogs` | 安装 changelog |
| `dh_link` | 创建符号链接 |
| `dh_strip` | 剥离调试符号 |
| `dh_compress` | 压缩文档 |
| `dh_fixperms` | 修正文件权限 |
| `dh_makeshlibs` | 生成共享库依赖信息 |
| `dh_shlibdeps` | 计算共享库依赖 |
| `dh_gencontrol` | 生成 control 文件 |
| `dh_md5sums` | 生成 md5sums |
| `dh_builddeb` | 打包 .deb |

---

## 8. reprepro —— 本地 APT 仓库

### 8.1 安装与初始化

```bash
sudo apt install reprepro

# 创建仓库目录
sudo mkdir -p /srv/repo/debian
cd /srv/repo/debian

# 创建 conf/distributions
sudo mkdir -p conf
sudo tee conf/distributions << 'EOF'
Origin: My Organization
Label: Custom Debian Repository
Codename: bookworm
Architectures: amd64 i386 arm64 source
Components: main
Description: Custom package repository for Debian Bookworm
SignWith: yes
DebIndices: Packages Release . .gz .bz2
UDebIndices: Packages . .gz .bz2
DscIndices: Sources Release . .gz .bz2
EOF
```

### 8.2 添加包到仓库

```bash
# 添加单个 .deb
reprepro -b /srv/repo/debian includedeb bookworm myapp_1.0.0-1_amd64.deb

# 添加源码包
reprepro -b /srv/repo/debian includedsc bookworm myapp_1.0.0-1.dsc

# 删除包
reprepro -b /srv/repo/debian remove bookworm myapp

# 列出仓库中的包
reprepro -b /srv/repo/debian list bookworm

# 查看包信息
reprepro -b /srv/repo/debian listfilter bookworm 'Package (==myapp)'
```

### 8.3 导出仓库密钥

```bash
# 导出 GPG 公钥
gpg --export --armor "My Repo Key" > /srv/repo/debian/repo-key.asc

# 客户端导入
sudo cp repo-key.asc /etc/apt/trusted.gpg.d/my-repo.asc
# 或
sudo apt-key add repo-key.asc
```

### 8.4 HTTP 服务

```bash
# nginx 配置
sudo tee /etc/nginx/sites-available/repo << 'EOF'
server {
    listen 80;
    server_name repo.example.com;
    root /srv/repo/debian;

    location / {
        autoindex on;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/repo /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### 8.5 客户端配置

```bash
# 添加 deb 源
echo "deb [signed-by=/etc/apt/trusted.gpg.d/my-repo.asc] https://repo.example.com/ bookworm main" | \
    sudo tee /etc/apt/sources.list.d/myrepo.list

sudo apt update
sudo apt install myapp
```

---

## 9. 常用开发工具

```bash
# lintian — Debian 包质量检查
sudo apt install lintian
lintian myapp_1.0.0-1_amd64.deb
lintian -i myapp_1.0.0-1_amd64.deb          # 带详细说明
lintian -EviIL +pedantic myapp_1.0.0-1_amd64.deb  # 最严格

# piuparts — 安装/升级/删除测试
sudo apt install piuparts
sudo piuparts myapp_1.0.0-1_amd64.deb

# pbuilder — 干净 chroot 构建
sudo apt install pbuilder
sudo pbuilder create --distribution bookworm
sudo pbuilder build myapp_1.0.0-1.dsc

# sbuild — 更专业的构建环境（Debian 开发者使用）
sudo apt install sbuild schroot
sudo sbuild-createchroot bookworm /srv/chroot/bookworm http://deb.debian.org/debian
sbuild -d bookworm myapp_1.0.0-1.dsc

# devscripts — 打包辅助脚本集
sudo apt install devscripts
dch -i                    # 编辑 changelog
uscan                     # 扫描上游新版本
debuild                   # 构建包
dget                      # 下载源码包
what-patch                # 分析补丁
```

---

## 10. 相关资源

- Debian 打包新维护者指南: https://www.debian.org/doc/manuals/maint-guide/
- Debian 政策手册: https://www.debian.org/doc/debian-policy/
- debhelper 手册: `man debhelper`
- dh 命令参考: `man dh`
- dpkg 手册: `man dpkg`
- Ubuntu 打包指南: https://packaging.ubuntu.com/
- [[../debian/01-apt包管理|APT 包管理]]
- [[../debian/02-Debian安装与服务器配置|Debian 安装与服务器配置]]
- [[../arch/03-AUR打包与上传|AUR 打包（PKGBUILD）]]
- [[../redhat/03-RPM打包与仓库|RPM 打包]]
