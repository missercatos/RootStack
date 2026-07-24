# nixpkgs 与包管理

> nixpkgs 是 Nix 生态的包仓库，包含超过 10 万个包。本章是 nixpkgs 的完整使用指南，覆盖包搜索安装、nix-shell 临时环境、编写 derivation、overlay 和 override、以及二进制缓存。

---

## 1. 资源链接

| 资源 | 链接 |
|------|------|
| Nix 包搜索 | https://search.nixos.org/packages |
| nixpkgs 仓库 | https://github.com/NixOS/nixpkgs |
| Nix 手册 | https://nixos.org/manual/nix/stable/ |
| NixOS Wiki | https://nixos.wiki/ |
| 清华 Nix 镜像 | https://mirrors.tuna.tsinghua.edu.cn/nix/ |
| 中科大 Nix 镜像 | https://mirrors.ustc.edu.cn/nix-channels/store/ |

---

## 2. nixpkgs 概述

### 2.1 nixpkgs 结构

```
nixpkgs/
├── pkgs/                    # 所有包的 derivation
│   ├── development/
│   ├── tools/
│   ├── applications/
│   ├── os-specific/
│   └── top-level/
│       └── all-packages.nix # 将所有包聚合在一起
├── lib/                     # nixpkgs 库函数
├── nixos/                   # NixOS 模块
│   └── modules/
├── pkgs/top-level/default.nix
└── flake.nix
```

### 2.2 通道 (Channels)

```bash
# 列出当前通道
nix-channel --list

# 添加通道
nix-channel --add https://nixos.org/channels/nixpkgs-unstable nixpkgs
nix-channel --add https://nixos.org/channels/nixos-24.11 nixos

# 更新通道
nix-channel --update

# 删除通道
nix-channel --remove nixpkgs

# 使用中国镜像加速
nix-channel --add https://mirrors.tuna.tsinghua.edu.cn/nix-channels/nixpkgs-unstable nixpkgs
```

---

## 3. 搜索包

### 3.1 命令行搜索

```bash
# 搜索包（需要有 channels）
nix search nixpkgs python312
nix search nixpkgs nginx

# 使用 flakes 搜索（不依赖 channels）
nix search nixpkgs python312

# 详细输出
nix search --verbose nixpkgs python

# 按名称精确搜索
nix search nixpkgs '^python312$'

# 搜索包描述中的关键字
nix search nixpkgs "web server"
```

### 3.2 Web 搜索

```
https://search.nixos.org/packages

搜索语法：
- 直接关键字：python, nginx
- 按通道： channel:nixos-24.11
- 按名称： ^python3$
```

### 3.3 查看包信息

```bash
# 使用 nix eval（flake 方式）
nix eval nixpkgs#python312.meta.description
nix eval nixpkgs#python312.meta.homepage
nix eval nixpkgs#python312.version

# 查看包的完整 meta 信息
nix eval nixpkgs#python312.meta --json | python3 -m json.tool

# 查看包的依赖
nix-store --query --tree $(nix build nixpkgs#python312 --no-link --print-out-paths)

# 或参考 derivation
nix show-derivation nixpkgs#python312
```

---

## 4. 安装包

### 4.1 nix profile（推荐 — flake 方式）

```bash
# 安装包
nix profile install nixpkgs#python312

# 安装特定版本
nix profile install nixpkgs#python312

# 列出已安装
nix profile list

# 查看 profile history
nix profile history

# 删除包
nix profile remove python312

# 按索引删除
nix profile remove 2

# 更新所有包
nix profile upgrade '.*'

# 更新特定包
nix profile upgrade python312

# 回滚
nix profile rollback

# 清除历史
nix profile wipe-history
```

### 4.2 nix-env（传统方式）

```bash
# 搜索
nix-env -qaP python

# 安装
nix-env -iA nixpkgs.python312

# 安装特定通道的包
nix-env -f '<nixpkgs>' -iA python312

# 查看已安装
nix-env -q

# 删除
nix-env -e python312

# 升级
nix-env -u
nix-env -u python312

# 查看代际
nix-env --list-generations

# 回滚
nix-env --rollback

# 切换到特定代际
nix-env -G 5
```

---

## 5. nix-shell 与 nix develop

### 5.1 nix-shell（传统方式）

```bash
# 临时使用包
nix-shell -p python312 nodejs gcc

# 从 shell.nix 创建环境
nix-shell shell.nix

# 纯环境（不继承用户环境变量）
nix-shell --pure -p python312
```

```nix
# shell.nix 示例
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python312
    python312Packages.pip
    python312Packages.virtualenv

    nodejs_22
    nodePackages.pnpm

    go
    gcc
    cmake

    postgresql_16
  ];

  shellHook = ''
    export PS1="[dev] $PS1"
    echo "Dev shell ready. Python: $(python --version), Node: $(node --version)"
  '';

  PROJECT_NAME = "my-web-app";
}
```

### 5.2 nix develop（flake 方式）

```bash
# 从 flake 的 devShell 进入
nix develop

# 从远程仓库进入
nix develop github:nix-community/nix-templates#python

# 进入特定 shell
nix develop .#frontend

# 直接运行命令
nix develop --command python
```

---

## 6. 构建包

### 6.1 nix-build（传统）

```bash
# 构建包但不安装
nix-build '<nixpkgs>' -A python312

# 构建并查看结果（创建 result 符号链接）
nix-build -E 'with import <nixpkgs> {}; python312'

# 构建表达式文件
nix-build my-expression.nix

# 进入构建环境调试
nix-shell '<nixpkgs>' -A python312
```

### 6.2 nix build（flake 方式）

```bash
# 构建当前 flake 的默认包
nix build

# 构建当前 flake 的特定包
nix build .#myPackage

# 构建 nixpkgs 中的包
nix build nixpkgs#python312

# 构建但不创建 result 链接
nix build --no-link nixpkgs#python312

# 打印输出路径
nix build --print-out-paths --no-link nixpkgs#python312

# 构建并查看日志
nix build -L nixpkgs#python312
```

---

## 7. 编写 Derivation

### 7.1 使用 stdenv.mkDerivation

```nix
# myapp.nix — 一个完整的包定义
{ lib
, stdenv
, fetchFromGitHub
, cmake
, pkg-config
, openssl
, zlib
}:

stdenv.mkDerivation rec {
  pname = "myapp";
  version = "1.0.0";

  src = fetchFromGitHub {
    owner = "user";
    repo = "myapp";
    rev = "v${version}";
    sha256 = "sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=";
  };

  nativeBuildInputs = [
    cmake
    pkg-config
  ];

  buildInputs = [
    openssl
    zlib
  ];

  cmakeFlags = [
    "-DBUILD_TESTS=OFF"
  ];

  meta = with lib; {
    description = "My application description";
    homepage = "https://example.com/myapp";
    license = licenses.mit;
    platforms = platforms.linux;
    maintainers = with maintainers; [ yourname ];
  };
}
```

### 7.2 各语言模板

```nix
# Go
{ stdenv, lib, buildGoModule, fetchFromGitHub }:
buildGoModule rec {
  pname = "my-go-app";
  version = "1.0.0";

  src = fetchFromGitHub {
    owner = "user";
    repo = pname;
    rev = "v${version}";
    sha256 = "sha256-...=";
  };

  vendorHash = "sha256-...=";  # 或 vendorHash = ""; 首次构建

  meta = with lib; {
    description = "Go application";
    license = licenses.mit;
  };
}

# Rust
{ stdenv, lib, rustPlatform, fetchFromGitHub, pkg-config, openssl }:
rustPlatform.buildRustPackage rec {
  pname = "my-rust-app";
  version = "1.0.0";

  src = fetchFromGitHub {
    owner = "user";
    repo = pname;
    rev = "v${version}";
    sha256 = "sha256-...=";
  };

  cargoHash = "sha256-...=";

  nativeBuildInputs = [ pkg-config ];
  buildInputs = [ openssl ];

  meta = with lib; {
    description = "Rust application";
    license = licenses.mit;
  };
}

# Python
{ lib, python3Packages, fetchFromGitHub }:
python3Packages.buildPythonApplication rec {
  pname = "my-python-app";
  version = "1.0.0";

  src = fetchFromGitHub {
    owner = "user";
    repo = pname;
    rev = "v${version}";
    sha256 = "sha256-...=";
  };

  propagatedBuildInputs = with python3Packages; [
    requests
    click
  ];

  nativeCheckInputs = with python3Packages; [
    pytest
  ];

  meta = with lib; {
    description = "Python application";
    license = licenses.mit;
  };
}

# Node.js
{ lib, buildNpmPackage, fetchFromGitHub }:
buildNpmPackage rec {
  pname = "my-js-app";
  version = "1.0.0";

  src = fetchFromGitHub {
    owner = "user";
    repo = pname;
    rev = "v${version}";
    sha256 = "sha256-...=";
  };

  npmDepsHash = "sha256-...=";

  # Makefile 或自定义 build 阶段
  postInstall = ''
    ln -s $out/lib/node_modules/my-js-app/bin/cli.js $out/bin/my-js-app
  '';

  meta = with lib; {
    description = "JavaScript application";
    license = licenses.mit;
  };
}
```

### 7.3 使用 derivation

```bash
# 将 nix 文件放在某个路径，通过 callPackage 调用
nix build --impure --expr 'with import <nixpkgs> {}; callPackage ./myapp.nix {}'

# 或在 flake 中导出
{
  outputs = { self, nixpkgs }: {
    packages.x86_64-linux.myapp = import ./myapp.nix {
      inherit (nixpkgs.legacyPackages.x86_64-linux)
        lib stdenv fetchFromGitHub cmake pkg-config openssl zlib;
    };
  };
}
```

---

## 8. Overlay 与 Override

### 8.1 Override 基础

```nix
# override — 修改 derivation 的参数
let
  pkgs = import <nixpkgs> {};
  myNginx = pkgs.nginx.override {
    # 修改 nginx 的参数
    modules = [ pkgs.nginxModules.rtmp ];
  };
in myNginx

# overrideAttrs — 修改 derivation 的属性
let
  pkgs = import <nixpkgs> {};
  customVim = pkgs.vim.overrideAttrs (oldAttrs: {
    version = "custom-version";
    src = fetchFromGitHub { ... };
    patches = oldAttrs.patches ++ [ ./my-fix.patch ];
  });
in customVim
```

### 8.2 Overlays

```nix
# Overlay 是一种全局修改 nixpkgs 的机制
# 可以添加新包、修改现有包

# ~/.config/nixpkgs/overlays/custom.nix
self: super: {

  # 添加新包
  myCustomApp = self.callPackage ./myapp.nix {};

  # 覆盖已有包
  vim = super.vim.overrideAttrs (oldAttrs: rec {
    version = "custom-${oldAttrs.version}";
    src = self.fetchFromGitHub {
      owner = "vim";
      repo = "vim";
      rev = "v9.1.0000";
      sha256 = "sha256-...=";
    };
  });

  # 覆盖 Python 包
  python312 = super.python312.override {
    packageOverrides = pySelf: pySuper: {
      numpy = pySuper.numpy.overridePythonAttrs (oldAttrs: {
        # 修改 numpy
      });
    };
  };
}
```

### 8.3 使用 Overlays

```nix
# NixOS configuration.nix 中全局启用
nixpkgs.overlays = [
  (import ./overlays/custom.nix)
];

# 在 flake 中
{
  nixpkgs.overlays = [ self.overlays.default ];
}

# 在 shell.nix 中
let
  pkgs = import <nixpkgs> {
    overlays = [
      (import ./overlays/custom.nix)
    ];
  };
in pkgs.myCustomApp
```

### 8.4 常见 Overlay 用例

```nix
self: super: {

  # 使用最新版本替代
  neovim = super.neovim-unwrapped;

  # 应用补丁
  fzf = super.fzf.overrideAttrs (old: {
    patches = (old.patches or []) ++ [ ./fzf-fix.patch ];
  });

  # 从不同源构建
  gimp = super.gimp.overrideAttrs (old: rec {
    version = "2.99.18";
    src = self.fetchurl {
      url = "https://download.gimp.org/gimp/v2.99/gimp-${version}.tar.xz";
      sha256 = "sha256-...=";
    };
  });

  # 启用额外特性
  gitFull = super.gitFull.override {
    sendEmailSupport = true;
    svnSupport = true;
    guiSupport = true;
  };
}
```

---

## 9. 二进制缓存 (Binary Cache / Substituter)

### 9.1 概念

```
Nix 的构建可以两种方式获得结果：
1. 本地编译（无缓存时）
2. 从二进制缓存下载（有预编译结果时）

二进制缓存在 Nix 术语中叫 substituter
默认缓存：https://cache.nixos.org
```

### 9.2 配置缓存

```nix
# /etc/nixos/configuration.nix 或 ~/.config/nix/nix.conf
nix.settings.substituters = [
  "https://mirrors.tuna.tsinghua.edu.cn/nix-channels/store"
  "https://cache.nixos.org"
  "https://my-org.cachix.org"
];

nix.settings.trusted-public-keys = [
  "cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY="
  "my-org.cachix.org-1:..."
];
```

### 9.3 Cachix 个人缓存

```bash
# 安装 cachix
nix-env -iA cachix -f https://cachix.org/api/v1/install

# 使用别人的缓存
cachix use username-cache

# 创建自己的缓存并推送构建结果
cachix create my-cache
nix build .#myPackage
cachix push my-cache result

# 或使用 GitHub Actions 自动推送
# actions/cachix-build
```

### 9.4 验证缓存生效

```bash
# 构建时看到 "copying path ... from 'https://...'" 说明缓存命中
nix build -L nixpkgs#python312

# 查看哪些包可以从缓存获得
nix path-info --recursive /nix/store/*-python3-*

# 查看缓存的路径
nix-store --query --substituters
```

---

## 10. 垃圾回收与空间管理

```bash
# 查看 store 大小
du -sh /nix/store/

# 查看 root（哪些 derivation 支撑了存活路径）
nix-store --gc --print-roots

# 删除未被引用的路径
nix-collect-garbage

# 彻底删除（包括旧 profile）
nix-collect-garbage -d

# 删除 30 天前的旧代际
sudo nix-collect-garbage --delete-older-than 30d

# 优化 store（硬链接重复文件，节省空间）
nix-store --optimise

# 查看未被 GC root 引用但仍存活的原因
nix-store --query --roots /nix/store/*-my-package-*

# 空间统计
nix path-info --recursive --size /run/current-system | sort -t' ' -nk2 | tail
```

---

## 11. 相关资源

- Nix 包搜索: https://search.nixos.org/packages
- nixpkgs 仓库: https://github.com/NixOS/nixpkgs
- Nix 手册: https://nixos.org/manual/nix/stable/
- Cachix: https://www.cachix.org/
- 清华大学 Nix 镜像: https://mirrors.tuna.tsinghua.edu.cn/nix/
- [[../nix/01-NixOS安装与声明式配置|NixOS 安装与声明式配置]]
- [[../nix/02-Nix语言与flake|Nix 语言与 Flake]]
- [[../arch/02-pacman包管理高级|pacman 包管理]]
- [[../debian/01-apt包管理|APT 包管理]]
