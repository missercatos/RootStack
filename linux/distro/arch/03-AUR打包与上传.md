# 14 - AUR 打包与上传完整教程

> 从零开始写 PKGBUILD，到推送 AUR，到维护更新。

---

## 14.1 AUR 工作原理

```
AUR 不存储二进制包，只存储 PKGBUILD（构建脚本）+ 辅助文件
用户本地编译安装（makepkg）

流程：
 PKGBUILD → makepkg → .pkg.tar.zst → pacman -U 安装
```

---

## 14.2 PKGBUILD 核心字段

```bash
# PKGBUILD 完整参考
# Maintainer: Your Name <email@example.com>
# Contributor: Original Author <email>

# ===== 元数据 =====
pkgname=my-app # 包名（只能小写字母数字_-+@）
pkgver=1.2.3 # 上游版本号
pkgrel=1 # Arch 包修订号（改配置不改版本时+1）
epoch= # 强制比版本号高（极少用）
pkgdesc="A short description" # 一句话描述（≤80字符）
arch=('x86_64') # 或 ('any') 如脚本/字体
url="https://github.com/user/repo" # 上游网址
license=('MIT') # SPDX 标识符
groups=() # 组名（如 'development'）
depends=('glibc' 'python') # 运行时依赖
makedepends=('git' 'go' 'cmake') # 编译依赖（安装后自动移除）
optdepends=('vim: for editing configs' # 可选依赖+说明
 'feh: for setting wallpaper')
checkdepends=('python-pytest') # 测试依赖
provides=('alternative-name') # 提供（虚拟包）
conflicts=('other-package') # 冲突
replaces=('old-package') # 替代
backup=('etc/myapp/config.yml') # 备份文件（不会被新包覆盖）
install=myapp.install # .install 脚本（pre/post install/remove/upgrade）
options=('!strip' '!debug') # 控制 makepkg 行为

# ===== 源码 =====
source=(
 # 远程文件（通过哈希验证）
 "https://example.com/releases/$pkgname-$pkgver.tar.gz"
 # Git 仓库
 "git+https://github.com/user/$pkgname.git#tag=v$pkgver"
 # 本地文件（放在 PKGBUILD 同目录）
 "myapp.desktop"
 "config.patch"
 # SVN
 # "svn+https://svn.example.com/project/trunk"
)

# 完整性校验（用 'SKIP' 表示不校验）
sha256sums=(
 'abc123def456...'
 'SKIP' # git 源用 SKIP
 'SKIP'
 'SKIP'
)

# 或用 sha512sums / b2sums / md5sums
# 推荐：sha256sums 或 sha512sums
```

---

## 14.3 完整 PKGBUILD 示例

### 示例 1：Go 项目

```bash
# Maintainer: Your Name <you@example.com>
pkgname=my-go-tool
pkgver=1.0.0
pkgrel=1
pkgdesc="A small CLI tool written in Go"
arch=('x86_64')
url="https://github.com/user/my-go-tool"
license=('MIT')
depends=('glibc')
makedepends=('git' 'go')
source=("git+${url}.git#tag=v${pkgver}")
sha256sums=('SKIP')

build() {
 cd "$pkgname"
 # 设置 Go 编译选项
 export CGO_ENABLED=0
 export GOFLAGS="-buildmode=pie -trimpath -mod=readonly -modcacherw"
 go build -ldflags="-s -w -X main.version=${pkgver}" -o "$pkgname" .
}

check() {
 cd "$pkgname"
 go test ./...
}

package() {
 cd "$pkgname"
 install -Dm755 "$pkgname" "$pkgdir/usr/bin/$pkgname"
 install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
```

### 示例 2：Rust 项目

```bash
# Maintainer: Your Name <you@example.com>
pkgname=my-rust-app
pkgver=2.0.0
pkgrel=1
pkgdesc="A Rust application"
arch=('x86_64')
url="https://github.com/user/my-rust-app"
license=('MIT' 'Apache-2.0')
depends=('gcc-libs')
makedepends=('git' 'rust' 'cargo')
source=("${pkgname}-${pkgver}.tar.gz::${url}/archive/v${pkgver}.tar.gz")
sha256sums=('SKIP')

build() {
 cd "${pkgname}-${pkgver}"
 cargo build --release --locked
}

check() {
 cd "${pkgname}-${pkgver}"
 cargo test --locked
}

package() {
 cd "${pkgname}-${pkgver}"
 install -Dm755 "target/release/${pkgname}" "$pkgdir/usr/bin/${pkgname}"

 # 安装 shell 补全
 # ./target/release/$pkgname --generate-completions bash > "$pkgname.bash"
 # install -Dm644 "$pkgname.bash" "$pkgdir/usr/share/bash-completion/completions/${pkgname}"
}
```

### 示例 3：Python 应用

```bash
# Maintainer: Your Name <you@example.com>
pkgname=python-myapp
_pyname=myapp
pkgver=1.5.0
pkgrel=1
pkgdesc="Python CLI tool"
arch=('any')
url="https://github.com/user/myapp"
license=('MIT')
depends=('python' 'python-click' 'python-rich' 'python-requests')
makedepends=('python-build' 'python-installer' 'python-setuptools' 'python-wheel')
source=("${pkgname}-${pkgver}.tar.gz::${url}/archive/v${pkgver}.tar.gz")
sha256sums=('SKIP')

build() {
 cd "${pkgname}-${pkgver}"
 python -m build --wheel --no-isolation
}

package() {
 cd "${pkgname}-${pkgver}"
 python -m installer --destdir="$pkgdir" dist/*.whl
}
```

### 示例 4：从 GitHub Release 安装二进制

```bash
# Maintainer: Your Name <you@example.com>
pkgname=myapp-bin
pkgver=3.2.1
pkgrel=1
pkgdesc="Pre-built binary application"
arch=('x86_64')
url="https://github.com/user/myapp"
license=('MIT')
# 因为下载预编译二进制，没有运行时依赖的话可以不写
depends=('glibc')
# 冲突检查
conflicts=("${pkgname%-bin}") # 与源码版冲突
provides=("${pkgname%-bin}=${pkgver}")

source=("${pkgname%-bin}-${pkgver}.tar.gz::${url}/releases/download/v${pkgver}/${pkgname%-bin}-linux-amd64.tar.gz")
sha256sums=('SKIP')

package() {
 cd "${pkgname%-bin}-${pkgver}"
 install -Dm755 "${pkgname%-bin}" "$pkgdir/usr/bin/${pkgname%-bin}"
 install -Dm644 LICENSE "$pkgdir/usr/share/licenses/${pkgname%-bin}/LICENSE"
}
```

---

## 14.4 install 脚本（钩子）

```bash
# myapp.install
# 用于安装前后/更新前后/卸载前后执行操作

pre_install() {
 # 安装前执行（如备份旧配置、创建系统用户）
 echo "即将安装 ${1%%-*}-${1#*-}..."
}

post_install() {
 # 安装后执行
 # 更新 gtk 图标缓存
 if command -v gtk-update-icon-cache &>/dev/null; then
 gtk-update-icon-cache -q -t -f usr/share/icons/hicolor
 fi
 # 更新 desktop 数据库
 if command -v update-desktop-database &>/dev/null; then
 update-desktop-database -q
 fi
 # 更新字体
 if command -v fc-cache &>/dev/null; then
 fc-cache -f
 fi
 # 创建系统用户
 if ! getent passwd myapp >/dev/null; then
 useradd -r -d /var/lib/myapp -s /usr/bin/nologin myapp
 fi
 echo "安装完成！配置示例在 /usr/share/doc/myapp/"
}

pre_upgrade() {
 # 更新前执行
 echo "正在从 ${2%%-*}-${2#*-} 升级到 ${1%%-*}-${1#*-}..."
}

post_upgrade() {
 post_install "$1"
 echo "升级完成"
}

pre_remove() {
 # 卸载前
 echo "即将卸载..."
}

post_remove() {
 # 卸载后清理
 # 移除系统用户
 if getent passwd myapp >/dev/null; then
 userdel myapp
 fi
}
```

---

## 14.5 本地测试与构建

```bash
# 创建 PKGBUILD 后的工作流

# 1. 生成 .SRCINFO（AUR 元数据文件）
makepkg --printsrcinfo > .SRCINFO

# 2. 安装依赖
makepkg -s

# 3. 构建（不安装）
makepkg

# 4. 构建 + 安装 + 处理依赖
makepkg -si

# 5. 构建 + 安装 + 跳过依赖（确信依赖已满足时）
makepkg -i

# 6. 清理（删除 src/ 和 pkg/）
makepkg -c

# 7. 检查包完整性
namcap PKGBUILD # 检查 PKGBUILD 规范
namcap *.pkg.tar.zst # 检查包质量

# 8. 在干净 chroot 中测试（最严格）
# 安装 devtools
sudo pacman -S devtools
# 创建 chroot
mkarchroot $HOME/chroot/root base-devel
# 在 chroot 中构建
makechrootpkg -c -r $HOME/chroot
```

---

## 14.6 .SRCINFO 文件

```bash
# .SRCINFO 是 AUR 的元数据索引（不是给人写的，由 makepkg 生成）

# 生成
makepkg --printsrcinfo > .SRCINFO

# 内容示例：
pkgbase = myapp
 pkgdesc = A short description
 pkgver = 1.2.3
 pkgrel = 1
 url = https://github.com/user/myapp
 arch = x86_64
 license = MIT
 depends = glibc
 depends = python
 makedepends = git
 makedepends = cargo
 source = git+https://github.com/user/myapp.git#tag=v1.2.3
 sha256sums = SKIP

pkgname = myapp
```

---

## 14.7 上传到 AUR

### 首次上传

```bash
# 1. 注册 AUR 账户（https://aur.archlinux.org/register）

# 2. 生成 SSH 密钥对
ssh-keygen -t ed25519 -C "aur-upload"

# 3. 添加公钥到 AUR 账户设置页
cat ~/.ssh/aur.pub # 复制到 AUR Settings → SSH Keys

# 4. 配置 SSH
# ~/.ssh/config
Host aur.archlinux.org
 IdentityFile ~/.ssh/aur
 User aur
 HostName aur.archlinux.org

# 5. 测试连接
ssh aur@aur.archlinux.org help
# 或
ssh aur@aur.archlinux.org

# 6. 克隆 AUR Git 仓库（首次）
git clone ssh://aur@aur.archlinux.org/myapp.git

# 7. 放入文件
cd myapp
cp ../PKGBUILD ../.SRCINFO ./ # .SRCINFO 必须存在！
# 如果有辅助文件
cp ../myapp.desktop ../myapp.install ./

# 8. 提交并推送
git add PKGBUILD .SRCINFO
git commit -m "Initial release v1.2.3"
git push origin master
```

### 更新

```bash
# 更新 AUR 包的标准流程

cd myapp-aur

# 1. 拉取最新（防止冲突）
git pull

# 2. 编辑 PKGBUILD（改 pkgver/pkgrel/sha256sums）
vim PKGBUILD

# 3. 更新 checksum
updpkgsums

# 4. 重新生成 .SRCINFO
makepkg --printsrcinfo > .SRCINFO

# 5. 本地构建测试
makepkg -si

# 6. 提交（带版本号）
git add PKGBUILD .SRCINFO
git commit -m "upgpkg: myapp 1.3.0"

# 7. 推送
git push origin master

# 8. （可选）如果在 chroot 测试过，加上签名
# gpg --detach-sign PKGBUILD
# 或依赖 namcap 检查
```

### 优雅降级/废弃

```bash
# 如果包不再维护
touch pkgbase-deleted
git add pkgbase-deleted
git rm PKGBUILD .SRCINFO
git commit -m "Delete: abandoned, upstream dead"
git push
```

---

## 14.8 AUR 提交规范

```bash
# 提交消息格式（AUR 约定）
"upgpkg: pkgname newversion" # 版本更新
"upgpkg: pkgname newversion-rel" # 非版本更新（改pkgrel、依赖、配置）
"Initial release v1.0.0" # 首次提交
"Delete: reason" # 删除

# 版本格式
pkgver-pkgrel → 1.2.3-1
epoch:pkgver-pkgrel → 1:2.0.0-1
```

---

## 14.9 AUR 常见辅助工具

```bash
# aurpublish — 简化 AUR Git 操作
paru -S aurpublish
aurpublish -p myapp

# aurutils — 本地 AUR 仓库管理
paru -S aurutils

# aurvote — 给包投票（CLI）
paru -S aurvote
aurvote -v myapp # 投票
aurvote -u # 对所有已安装 AUR 包投票

# nvchecker — 自动检查上游版本更新
paru -S nvchecker
# .nvchecker.toml
[myapp]
source = "github"
github = "user/myapp"
```

---

## 14.10 AUR 最佳实践

```bash
# DO
# - 官方仓库没有的包才放 AUR
# - 用 SHA256 校验非 git 源
# - 测试 PKGBUILD 能正常构建
# - pkgver 匹配上游版本号
# - 及时更新/响应评论

# DON'T
# - 放二进制文件到 AUR（应标记为 *-bin）
# - 放有版权争议的内容
# - pkgver 自己编版本号
# - 留 SKIP 校验下载的压缩包
# - 在 PKGBUILD 里用 sudo
# - 安装到 /usr/local（应用 /usr）
```

---

## 14.11 自动构建与 CI

```bash
# GitHub Actions 自动测试 PKGBUILD
# .github/workflows/aur-test.yml

name: AUR Build Test
on: [push, pull_request]

jobs:
 build:
 runs-on: ubuntu-latest
 container: archlinux:latest
 steps:
 - uses: actions/checkout@v3
 - name: Install build tools
 run: |
 pacman -Syu --noconfirm base-devel git namcap
 useradd -m builder
 echo "builder ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
 - name: Build package
 run: |
 sudo -u builder makepkg -s --noconfirm
 - name: Check package
 run: |
 namcap *.pkg.tar.zst
```

---

## 14.12 AUR Webhook 与监控

```bash
# 获取包的评论通知
# https://aur.archlinux.org/rss/?p=myapp

# 监控下游依赖（依赖你包的其他包）
# 在 AUR 页面查看 "Required by"

# 监控上游更新
# https://release-monitoring.org/
```

---

## 14.13 本章测验

> [!example] 自测题目

> [!question]- 选择题 1：AUR 存储的是什么内容？
> - A. 预编译的二进制包
> - B. PKGBUILD 构建脚本和辅助文件
> - C. 源码压缩包
> - D. Docker 镜像
>
> > [!success]- 点击查看答案
> > **B**
> > AUR 不存储二进制包，只存储 PKGBUILD（构建脚本）和辅助文件，用户在本地通过 makepkg 编译安装。

> [!question]- 选择题 2：PKGBUILD 中 pkgrel 字段的用途是什么？
> - A. 指定包的上游版本号
> - B. 指定包的 Arch 修订号（改配置不改版本时递增）
> - C. 强制比其他版本号高
> - D. 指定最小依赖版本
>
> > [!success]- 点击查看答案
> > **B**
> > pkgrel 是 Arch 包修订号，当 PKGBUILD 改了配置/依赖但上游版本号不变时递增。epoch 才是强制比版本号高的字段。

> [!question]- 选择题 3：生成 .SRCINFO 文件的正确命令是？
> - A. makepkg --srcinfo
> - B. makepkg --printsrcinfo > .SRCINFO
> - C. updpkgsums --srcinfo
> - D. pacman -Si > .SRCINFO
>
> > [!success]- 点击查看答案
> > **B**
> > 使用 `makepkg --printsrcinfo > .SRCINFO` 生成 AUR 所需的元数据索引文件。

> [!question]- 判断题 4：上传 AUR 包时，.SRCINFO 文件不是必需的
> - A. 正确
> - B. 错误
>
> > [!success]- 点击查看答案
> > **B. 错误**
> > .SRCINFO 是 AUR 的元数据索引文件，必须随 PKGBUILD 一起提交，否则 AUR 无法正确索引你的包。

> [!question]- 选择题 5：在干净 chroot 环境中测试构建的命令是什么？
> - A. makepkg --clean
> - B. makechrootpkg -c -r $HOME/chroot
> - C. makepkg --chroot
> - D. pacman -S --chroot
>
> > [!success]- 点击查看答案
> > **B**
> > 使用 devtools 包提供的 `makechrootpkg -c -r $HOME/chroot` 在干净的 chroot 环境中构建，这是最严格的测试方式。

> [!question]- 选择题 6：AUR 更新包时的标准提交消息格式是？
> - A. "Update to version X.Y.Z"
> - B. "upgpkg: pkgname newversion"
> - C. "bump: pkgname X.Y.Z"
> - D. "release: vX.Y.Z"
>
> > [!success]- 点击查看答案
> > **B**
> > AUR 约定的提交消息格式为 `"upgpkg: pkgname newversion"`，如 `"upgpkg: myapp 1.3.0"`。

> [!question]- 判断题 7：PKGBUILD 中可以使用 sudo 命令来安装文件到系统目录
> - A. 正确
> - B. 错误
>
> > [!success]- 点击查看答案
> > **B. 错误**
> > 绝对不能在 PKGBUILD 里使用 sudo。package() 函数应将文件安装到 $pkgdir 前缀下，由 pacman 统一管理安装。

> [!question]- 选择题 8：PKGBUILD 中 makedepends 和 depends 的区别是什么？
> - A. 没有区别，两者等价
> - B. makedepends 是编译时依赖（安装后自动移除），depends 是运行时依赖
> - C. makedepends 是可选依赖，depends 是强制依赖
> - D. makedepends 用于测试，depends 用于运行
>
> > [!success]- 点击查看答案
> > **B**
> > makedepends 指定编译时需要的依赖（如 git、cmake），安装后会自动移除。depends 是运行时依赖，包安装后一直保留。

> [!question]- 选择题 9：namcap 工具的用途是什么？
> - A. 生成 PKGBUILD 模板
> - B. 检查 PKGBUILD 规范和包质量
> - C. 自动更新包版本号
> - D. 管理 AUR 账户
>
> > [!success]- 点击查看答案
> > **B**
> > namcap 用于检查 PKGBUILD 规范（如缺失依赖、不规范写法）和编译后的包质量（如多余文件、权限问题）。

> [!question]- 判断题 10：预编译二进制包上传 AUR 时应使用 *-bin 后缀命名
> - A. 正确
> - B. 错误
>
> > [!success]- 点击查看答案
> > **A. 正确**
> > 按 AUR 惯例，下载预编译二进制而非从源码编译的包应以 -bin 后缀命名（如 myapp-bin），并用 conflicts 和 provides 与源码版互斥。
