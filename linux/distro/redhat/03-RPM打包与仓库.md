# RPM 打包与仓库

> RPM 是 Red Hat 生态的包格式。本章是完整的 RPM 打包教程，覆盖 spec 文件编写、rpmbuild 工作流、rpmlint 质量检查、createrepo 创建本地 yum/dnf 仓库、mock 干净构建环境和 COPR 个人仓库。

---

## 1. 资源链接

| 资源 | 链接 |
|------|------|
| RPM 打包指南 | https://rpm-packaging-guide.github.io/ |
| Fedora 打包指南 | https://docs.fedoraproject.org/en-US/packaging-guidelines/ |
| COPR 构建服务 | https://copr.fedorainfracloud.org/ |
| Mock 文档 | https://github.com/rpm-software-management/mock |
| 清华镜像 | https://mirrors.tuna.tsinghua.edu.cn/centos/ |
| 中科大镜像 | https://mirrors.ustc.edu.cn/centos/ |

---

## 2. RPM 基础

### 2.1 RPM 包命名规范

```
name-version-release.architecture.rpm

例如: nginx-1.24.0-1.el9.x86_64.rpm
      |     |      |   |    |
      包名  上游版本 发布 发行版标签  架构

- name: 包名
- version: 上游版本号
- release: RPM 发布号（每次打包递增）
- architecture: x86_64, noarch, aarch64, i686
```

### 2.2 rpm 命令

```bash
# 安装
sudo rpm -ivh package.rpm        # 安装并显示进度

# 升级
sudo rpm -Uvh package.rpm

# 删除
sudo rpm -e packagename

# 查询
rpm -qa                           # 列出所有已安装的包
rpm -q packagename                # 查看是否安装了某个包
rpm -qi packagename               # 包详细信息
rpm -ql packagename               # 列出包安装的文件
rpm -qf /path/to/file             # 文件属于哪个包
rpm -qR packagename               # 列出包的依赖
rpm -q --changelog packagename    # 查看变更日志

# 验证
rpm -V packagename                # 验证包文件完整性
rpm -Va                           # 验证所有包

# 检查未安装的包
rpm -qp package.rpm               # 查询包名
rpm -qpl package.rpm              # 列出 .rpm 中的文件
rpm -qpi package.rpm              # 查看 .rpm 信息
rpm -qpR package.rpm              # 查看 .rpm 依赖

# 导入 GPG 密钥
sudo rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-*

# 从 CPIO 解压 RPM（不需要安装）
rpm2cpio package.rpm | cpio -idmv
```

---

## 3. 构建环境搭建

### 3.1 安装打包工具

```bash
# Fedora / RHEL 8+
sudo dnf install rpm-build rpmdevtools rpmlint
sudo dnf groupinstall "RPM Development Tools"

# RHEL 7 / CentOS 7
sudo yum install rpm-build rpmdevtools rpmlint
sudo yum groupinstall "Development Tools"
```

### 3.2 创建 RPM 构建目录

```bash
# 自动创建 ~/rpmbuild 目录树
rpmdev-setuptree

# 目录结构
tree ~/rpmbuild/
```

```
~/rpmbuild/
├── BUILD/          # 源码解压并编译的目录
├── BUILDROOT/      # 安装的虚拟根（fakeroot）
├── RPMS/           # 生成的二进制 RPM
│   ├── x86_64/
│   └── noarch/
├── SOURCES/        # 源码压缩包和补丁
├── SPECS/          # spec 文件
└── SRPMS/          # 源码 RPM (src.rpm)
```

---

## 4. Spec 文件编写

### 4.1 Spec 文件结构

```
# spec 文件分为多个区段

Name:           myapp
Version:        1.0.0
Release:        1%{?dist}
Summary:        A short description

License:        MIT
URL:            https://example.com/myapp
Source0:        https://example.com/releases/%{name}-%{version}.tar.gz
# Source1:        myapp.service
# Patch0:         myapp-fix.patch

BuildArch:      x86_64
# BuildArch:      noarch

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  pkgconfig(libfoo)

Requires:       libfoo >= 1.2.0
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
A longer description of the package.
It can span multiple lines.

%prep
%autosetup

%build
%configure
%make_build

%install
%make_install

%check
%make_test

%files
%license LICENSE
%doc README.md
%{_bindir}/myapp
%{_datadir}/myapp/
%config(noreplace) %{_sysconfdir}/myapp/config.yml

%changelog
* Wed Jan 15 2025 Your Name <you@example.com> - 1.0.0-1
- Initial package
```

### 4.2 完整字段参考

```bash
# 必要字段
Name:           # 包名（必须与 spec 文件名一致）
Version:        # 上游版本号（不能有短横线）
Release:        # RPM 发布号，%{?dist} 自动展开为发行版标签（如 .el9）
Summary:        # 简短描述（不超过 80 字符）
License:        # SPDX 标识符（MIT, GPLv3+, ASL 2.0 等）
URL:            # 项目主页

# 源码
Source0:        # 主源码（可以是 URL 或本地文件）
Source1: .. N:  # 额外源码或配置文件
Patch0: .. N:   # 补丁文件

# 架构
BuildArch:      # 目标架构：x86_64, noarch, aarch64 等
ExclusiveArch:  # 限制只能在特定架构构建

# 依赖
BuildRequires:  # 编译时依赖
Requires:       # 运行时依赖
Requires(pre):  # %pre 脚本前需要的依赖
Requires(post): # %post 脚本前需要的依赖

# 功能标记
Provides:       # 提供的虚拟功能
Conflicts:      # 冲突的包
Obsoletes:      # 替代的旧包

# 推荐/建议（弱依赖）
Recommends:     # 推荐安装
Suggests:       # 建议安装
Supplements:    # 补充
Enhances:       # 增强
```

### 4.3 Spec 脚本区的执行时机

| 脚本 | 执行时机 |
|------|---------|
| `%pre` | 安装前 |
| `%post` | 安装后 |
| `%preun` | 删除前 |
| `%postun` | 删除后 |
| `%pretrans` | 事务开始前 |
| `%posttrans` | 事务结束后 |
| `%triggerin` | 指定包安装时触发 |
| `%triggerun` | 指定包删除时触发 |

### 4.4 systemd service 模板

```bash
# 完整的带 systemd 服务的 spec 示例
Name: myapp
Version: 1.0.0
Release: 1%{?dist}
Summary: My application with systemd service

License: MIT
URL: https://example.com/myapp
Source0: %{url}/releases/v%{version}.tar.gz
Source1: myapp.service

BuildRequires: gcc make
BuildRequires: systemd-rpm-macros

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
My application description.

%prep
%autosetup

%build
%configure
%make_build

%install
%make_install

# 安装 systemd service 文件
mkdir -p %{buildroot}%{_unitdir}
install -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/myapp.service

# 安装 systemd sysusers 配置（如需要创建运行时用户）
# mkdir -p %{buildroot}%{_sysusersdir}
# install -m 644 %{SOURCE2} %{buildroot}%{_sysusersdir}/myapp.conf

%pre
getent group myapp >/dev/null || groupadd -r myapp
getent passwd myapp >/dev/null || useradd -r -g myapp -d %{_sharedstatedir}/myapp -s /sbin/nologin myapp

%post
%systemd_post myapp.service

%preun
%systemd_preun myapp.service

%postun
%systemd_postun_with_restart myapp.service

%files
%license LICENSE
%doc README.md
%{_bindir}/myapp
%{_unitdir}/myapp.service
%config(noreplace) %{_sysconfdir}/myapp/config.yml
%dir %{_sharedstatedir}/myapp

%changelog
* Wed Jan 15 2025 Your Name <you@example.com> - 1.0.0-1
- Initial package with systemd service
```

### 4.5 RPM 宏速查

| 宏 | 展开值 |
|----|--------|
| `%{_bindir}` | `/usr/bin` |
| `%{_sbindir}` | `/usr/sbin` |
| `%{_libexecdir}` | `/usr/libexec` |
| `%{_datadir}` | `/usr/share` |
| `%{_sysconfdir}` | `/etc` |
| `%{_localstatedir}` | `/var` |
| `%{_sharedstatedir}` | `/var/lib` |
| `%{_unitdir}` | `/usr/lib/systemd/system` |
| `%{_tmpfilesdir}` | `/usr/lib/tmpfiles.d` |
| `%{_sysusersdir}` | `/usr/lib/sysusers.d` |
| `%{_mandir}` | `/usr/share/man` |
| `%{_includedir}` | `/usr/include` |
| `%{_libdir}` | `/usr/lib64` (64位) |
| `%buildroot` | 构建虚拟根（~rpms/BUILDROOT） |
| `%{?dist}` | 发行版标签（.el9 或 .fc40） |
| `%{name}` | 包名 |
| `%{version}` | 版本号 |
| `%{release}` | 发布号 |
| `%{_arch}` | 构建架构 |

查看所有宏：

```bash
rpm --showrc
rpm --eval '%{_bindir}'
```

---

## 5. rpmbuild 构建流程

### 5.1 准备源码

```bash
# 下载源码放到 SOURCES 目录
cp myapp-1.0.0.tar.gz ~/rpmbuild/SOURCES/

# 或直接在 spec 中用 URL，然后：
spectool -g -R myapp.spec         # 下载所有 Source
```

### 5.2 构建

```bash
# 方式 1：从 spec 文件构建（推荐）
rpmbuild -ba myapp.spec           # 构建二进制 + 源码 RPM
rpmbuild -bb myapp.spec           # 只构建二进制 RPM
rpmbuild -bs myapp.spec           # 只构建源码 RPM

# 方式 2：从源码 RPM 构建
rpmbuild --rebuild myapp-1.0.0-1.fc40.src.rpm

# 构建选项
rpmbuild -ba --clean myapp.spec   # 构建后清理 BUILD 目录
rpmbuild -ba --target x86_64 myapp.spec
rpmbuild -ba --define "_topdir /custom/path" myapp.spec

# 跳过构建阶段（调试用）
rpmbuild -bp myapp.spec           # 只 %prep
rpmbuild -bc myapp.spec           # 到 %build
rpmbuild -bi myapp.spec           # 到 %install
rpmbuild -bl myapp.spec           # 检查 %files 列表
```

### 5.3 快速检查流程

```bash
# 1. 语法检查
rpmlint myapp.spec

# 2. 下载源码
spectool -g -R myapp.spec

# 3. 安装构建依赖
sudo dnf builddep myapp.spec

# 4. 构建
rpmbuild -ba myapp.spec

# 5. 检查生成的包
rpmlint ~/rpmbuild/RPMS/x86_64/myapp-*.rpm

# 6. 安装测试
sudo dnf install ~/rpmbuild/RPMS/x86_64/myapp-*.rpm
```

---

## 6. rpmlint 质量检查

```bash
# 安装
sudo dnf install rpmlint

# 检查 spec 文件
rpmlint myapp.spec

# 检查生成的 RPM
rpmlint ~/rpmbuild/RPMS/x86_64/myapp-*.rpm

# 检查源码 RPM
rpmlint ~/rpmbuild/SRPMS/myapp-*.src.rpm

# 详细模式
rpmlint -i myapp.spec             # 带解释
rpmlint -v myapp.spec             # 详细输出

# 常见 rpmlint 错误修复：
# - "no-changelogname-tag" → 添加 %changelog
# - "no-description-tag" → 添加 %description
# - "no-license-tag" → 添加 License 字段
# - "unstripped-binary-or-object" → 编译时加 %{optflags}
```

---

## 7. createrepo —— 创建 YUM/DNF 仓库

### 7.1 创建本地仓库

```bash
# 安装 createrepo_c（C 语言重写，更快）
sudo dnf install createrepo_c

# 准备 RPM 文件目录
mkdir -p /srv/repo/custom/x86_64
cp ~/rpmbuild/RPMS/x86_64/*.rpm /srv/repo/custom/x86_64/

# 创建仓库元数据
createrepo_c /srv/repo/custom/

# 更新仓库（添加新包后）
createrepo_c --update /srv/repo/custom/

# 生成校验和
createrepo_c --checksum sha256 /srv/repo/custom/

# 包含 deltarpm（增量更新）
createrepo_c --deltas /srv/repo/custom/

# 指定仓库基本 URL（用于 mirrorlist 生成）
createrepo_c --baseurl https://repo.example.com/custom/ /srv/repo/custom/
```

### 7.2 签名仓库

```bash
# 生成 GPG 密钥
gpg --full-generate-key

# 签名每个 RPM
rpm --addsign /srv/repo/custom/x86_64/*.rpm
# 或使用 rpmsign
rpmsign --addsign /srv/repo/custom/x86_64/*.rpm

# 导出公钥
gpg --export --armor "My Repo Key" > /srv/repo/custom/RPM-GPG-KEY-custom

# 签名仓库元数据
gpg --detach-sign --armor /srv/repo/custom/repodata/repomd.xml

# 客户端导入
sudo rpm --import https://repo.example.com/custom/RPM-GPG-KEY-custom
```

### 7.3 HTTP 仓库服务

```bash
# nginx 配置
sudo dnf install nginx

sudo tee /etc/nginx/conf.d/repo.conf << 'EOF'
server {
    listen 80;
    server_name repo.example.com;

    location /custom/ {
        alias /srv/repo/custom/;
        autoindex on;
    }
}
EOF

sudo systemctl enable --now nginx
sudo firewall-cmd --add-service=http --permanent && sudo firewall-cmd --reload
```

### 7.4 客户端 .repo 配置

```ini
# /etc/yum.repos.d/custom.repo
[custom-repo]
name=Custom Repository
baseurl=https://repo.example.com/custom/
enabled=1
gpgcheck=1
gpgkey=https://repo.example.com/custom/RPM-GPG-KEY-custom
```

```bash
sudo dnf makecache
sudo dnf install myapp
```

---

## 8. Mock —— 干净 chroot 构建环境

### 8.1 安装与初始化

```bash
# 安装 mock
sudo dnf install mock

# 将用户加入 mock 组
sudo usermod -aG mock $USER
# 注销重新登录使组生效

# 查看可用的 chroot 配置
ls /etc/mock/

# rocky+epel-9-x86_64.cfg
# fedora-40-x86_64.cfg
# alma+epel-9-x86_64.cfg
```

### 8.2 使用 Mock 构建

```bash
# 从 SRPM 构建
mock -r rocky+epel-9-x86_64 ~/rpmbuild/SRPMS/myapp-1.0.0-1.el9.src.rpm

# 从 spec 构建（自动生成 SRPM）
mock -r rocky+epel-9-x86_64 --buildsrpm --spec myapp.spec --sources ~/rpmbuild/SOURCES/
mock -r rocky+epel-9-x86_64 --rebuild /var/lib/mock/rocky+epel-9-x86_64/result/*.src.rpm

# 一条命令完成
mock -r rocky+epel-9-x86_64 myapp.spec

# 输出目录
ls /var/lib/mock/rocky+epel-9-x86_64/result/

# 指定输出目录
mock -r rocky+epel-9-x86_64 --resultdir=~/rpms myapp.spec
```

### 8.3 Mock 链式构建

```bash
# 如果包 A 依赖包 B，先构建 B
mock -r rocky+epel-9-x86_64 depB.spec

# 然后链式构建 A（自动使用刚构建的 B）
mock -r rocky+epel-9-x86_64 --chain packageA/

# 支持多包和依赖解析
mock -r rocky+epel-9-x86_64 --chain pkgA/ pkgB/ pkgC/
```

### 8.4 进入 Mock Shell 调试

```bash
# 初始化 chroot 但不构建
mock -r rocky+epel-9-x86_64 --init

# 进入 chroot shell
mock -r rocky+epel-9-x86_64 --shell

# 在 chroot 中安装额外包
mock -r rocky+epel-9-x86_64 --install vim strace

# 重建 chroot（清理后重新初始化）
mock -r rocky+epel-9-x86_64 --clean
mock -r rocky+epel-9-x86_64 --scrub all
```

### 8.5 自定义 Mock 配置

```bash
# 复制默认配置到自定义
cp /etc/mock/rocky+epel-9-x86_64.cfg ~/.config/mock/custom-9-x86_64.cfg

# 编辑：添加自定义仓库、修改包列表等
vim ~/.config/mock/custom-9-x86_64.cfg
```

```
# ~/.config/mock/custom-9-x86_64.cfg
config_opts['root'] = 'custom-9-x86_64'
config_opts['target_arch'] = 'x86_64'
config_opts['legal_host_arches'] = ('x86_64',)
config_opts['chroot_setup_cmd'] = 'install @buildsys-build'

# 添加自定义仓库
config_opts['yum.conf'] += """
[custom-repo]
name=Custom
baseurl=https://repo.example.com/custom/$releasever/$basearch/
enabled=1
gpgcheck=0
"""
```

```bash
# 使用自定义配置
mock -r ~/.config/mock/custom-9-x86_64.cfg myapp.spec
```

---

## 9. COPR —— 个人公共仓库

### 9.1 使用 COPR Web 界面

```
1. 访问 https://copr.fedorainfracloud.org/
2. 登录 (FAS 账号)
3. Create New Project
   - Name: my-tools
   - Description: My personal tools
   - Chroots: fedora-40-x86_64, epel-9-x86_64
   - Create

4. 在 Packages 标签 → New Package
   - Package name: myapp
   - Type: Git (提供 git URL + spec 路径)
   - 或 Upload SRPM
5. Build

构建完成后，其他人可以通过 dnf 使用：
sudo dnf copr enable username/my-tools
sudo dnf install myapp
```

### 9.2 COPR CLI 工具

```bash
# 安装
sudo dnf install copr-cli

# 配置 API 令牌（在 COPR Web → Settings → API 生成）
# 写入 ~/.config/copr

# 创建项目
copr-cli create my-tools --description "My tools" \
    --chroot fedora-40-x86_64 --chroot epel-9-x86_64

# 从 SRPM 构建
copr-cli build my-tools ~/rpmbuild/SRPMS/myapp-1.0.0-1.fc40.src.rpm

# 从 Git 构建
copr-cli buildscm --clone-url https://github.com/user/repo.git \
    --spec spec/myapp.spec --method make_srpm my-tools

# 从 PyPI 自动生成 spec 并构建
copr-cli buildpypi my-tools --pythonversions 3 --packagename myapp

# 列出项目
copr-cli list

# 删除包
copr-cli delete-package my-tools --name myapp
```

---

## 10. 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `error: Failed build dependencies` | 缺少 BuildRequires | `sudo dnf builddep myapp.spec` |
| `error: Installed (but unpackaged) file(s) found` | %files 列表不完整 | 添加遗漏的文件或使用 %exclude |
| `error: File listed twice` | 文件被多次列出 | 检查 %files 是否有重复 |
| mock 构建网络不通 | 默认使用代理 | 编辑 mock 配置添加 `use_host_resolv = True` |
| RPM 签名错误 | GPG 密钥未导入 | `rpm --import KEY` |
| debuginfo 包过大 | 调试符号未剥离 | 设置 `%global debug_package %{nil}` |

---

## 11. 相关资源

- RPM 打包指南: https://rpm-packaging-guide.github.io/
- Fedora 打包规范: https://docs.fedoraproject.org/en-US/packaging-guidelines/
- Mock 文档: https://rpm-software-management.github.io/mock/
- COPR: https://copr.fedorainfracloud.org/
- [[../redhat/01-dnf-yum包管理|DNF/YUM 包管理]]
- [[../redhat/02-RHEL-CentOS安装与配置|RHEL 安装与配置]]
- [[../debian/03-dpkg与deb打包|Debian deb 打包]]
- [[../arch/03-AUR打包与上传|AUR PKGBUILD 打包]]
