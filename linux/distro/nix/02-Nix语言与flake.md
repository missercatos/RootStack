# Nix 语言与 Flake

> Nix 是 NixOS 和 Nix 包管理器的配置语言，是一种纯函数式、惰性求值的领域特定语言。Flake 是 Nix 的现代实验性特性，提供标准化项目结构、锁定文件和确定性构建。本章从基础语法到实战 flake 项目全覆盖。

---

## 1. 资源链接

| 资源 | 链接 |
|------|------|
| Nix 语言参考 | https://nixos.org/manual/nix/stable/language/ |
| Nix Pills | https://nixos.org/guides/nix-pills/ |
| Flakes Wiki | https://nixos.wiki/wiki/Flakes |
| NixOS 官网 | https://nixos.org/ |
| 清华 Nix 镜像 | https://mirrors.tuna.tsinghua.edu.cn/nix/ |

---

## 2. Nix 语言基础

### 2.1 基本类型

```nix
# 整数
42

# 浮点数
3.14

# 字符串（双引号）
"hello world"
"multi\nline"

# 多行字符串（双单引号）
''
  line 1
  line 2
  ${expression}    # 反引号内插值
''

# 路径（相对于文件所在目录）
./file.txt
../parent/file.txt
/path/to/file       # 绝对路径

# 布尔值
true
false

# null
null

# 列表（空格分隔）
[ "a" "b" "c" ]
[ 1 2 3 ]

# 属性集 (attribute set)
{
  key1 = "value1";
  key2 = 42;
  nested = {
    inner = true;
  };
}

# 使用 . 访问属性
{ a.b.c = 1; }    # 等价于 { a = { b = { c = 1; }; }; }
```

### 2.2 变量与绑定

```nix
# let ... in 绑定
let
  x = 1;
  y = x + 2;
in
  y * 3
# 结果: 9

# 多重绑定
let
  a = 1;
  b = 2;
in {
  sum = a + b;
  product = a * b;
}

# rec — 递归属性集（属性间可互相引用）
rec {
  a = 1;
  b = a + 1;          # b = 2
}
```

### 2.3 函数

```nix
# 单参数函数
x: x + 1

# 多参数函数（柯里化）
x: y: x + y

# 属性集模式匹配
{ a, b }: a + b

# 带默认值
{ a ? 1, b ? 2 }: a + b

# 带省略号（接受额外参数）
{ a, b, ... }: a + b

# 带 @ 绑定整个参数
args@{ a, b, ... }: a + b + args.c

# 调用
(x: x + 1) 5           # 结果: 6
({a, b}: a + b) { a = 1; b = 2; }  # 结果: 3
```

### 2.4 with 语句

```nix
# with 将属性集的属性引入作用域
with pkgs; [ vim git htop ]
# 等价于 [ pkgs.vim pkgs.git pkgs.htop ]

# 嵌套 with
with pkgs; with lib;
[ vim git take name version ]

# with 优先级低于直接引用
let x = 1; in with { x = 2; }; x
# 结果: 1
```

### 2.5 inherit

```nix
# inherit 从外部作用域继承属性
let
  foo = "hello";
  bar = "world";
in {
  inherit foo bar;         # 等价于 foo = foo; bar = bar;
}

# inherit 从特定属性集继承
let
  pkgs = import <nixpkgs> {};
in {
  inherit (pkgs) vim git;  # 等价于 vim = pkgs.vim; git = pkgs.git;
}
```

### 2.6 if ... then ... else

```nix
# Nix 只有条件表达式，没有语句
if x > 0 then "positive" else "non-positive"

# 必须是 if-then-else（不能省略 else）
# 可以用 null 作为 else 值
if cond then value else null

# 嵌套
if x > 0 then "positive"
else if x < 0 then "negative"
else "zero"
```

### 2.7 assert 和 with

```nix
assert condition;
expression

# 示例
assert 1 + 1 == 2;
"ok"

# 在属性值中使用
{
  value = assert x > 0; x + 1;
}
```

---

## 3. 高级特性

### 3.1 导入

```nix
# import 导入 Nix 文件并求值
let
  myLib = import ./lib.nix;
in
  myLib.someFunction

# 导入 nixpkgs
let
  pkgs = import <nixpkgs> {};
in
  pkgs.hello

# 导入 nixpkgs 指定版本
let
  pkgs = import (builtins.fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/refs/tags/24.11.tar.gz";
    sha256 = "sha256:...";
  }) {};
in
  pkgs.hello
```

### 3.2 内置函数 (builtins)

```nix
# 常用 builtins
builtins.toString 42              # "42"
builtins.toPath "file"            # /path/file
builtins.toFile "name" "content"  # 创建文件并返回路径
builtins.readFile ./file.txt      # 读文件内容
builtins.pathExists ./file        # 检查路径是否存在
builtins.fetchurl {               # 下载 URL
  url = "https://example.com/file";
  sha256 = "...";
}
builtins.fetchTarball { url = "..."; sha256 = "..."; } # 下载 tar
builtins.fetchGit { url = "..."; ref = "main"; }       # 克隆 git
builtins.derivation { ... }       # 底层 derivation 创建
builtins.map (x: x * 2) [1 2 3]  # [2 4 6]
builtins.filter (x: x > 2) [1 2 3 4]  # [3 4]
builtins.concatLists [[1 2] [3 4]]    # [1 2 3 4]

# 完整列表
builtins.attrNames (builtins)
```

### 3.3 运算符

```nix
# 算术
1 + 2    # 3
3 - 1    # 2
4 * 5    # 20
6 / 2    # 3.0 (浮点数)

# 字符串拼接
"hello " + "world"        # "hello world"
"${x} ${y}"               # 字符串插值

# 列表拼接
[1 2] ++ [3 4]            # [1 2 3 4]

# 比较
x == y                    # 相等
x != y                    # 不等
x < y, x > y              # 大小比较

# 逻辑
!true                     # false
a && b                    # 逻辑与
a || b                    # 逻辑或
x -> y                    # 蕴涵 (implication, !x || y)

# 属性集操作
set // { key = value; }   # 合并（右边覆盖左边）
set ? key                 # 检查属性是否存在
set.key 或 set.${name}    # 选择属性
```

---

## 4. Nixpkgs 库 (lib)

### 4.1 引入 lib

```nix
{ pkgs, lib, ... }:
let
  inherit (lib) mkOption types mkEnableOption;
in { ... }
```

### 4.2 常用 lib 函数

```nix
# 字符串操作
lib.toUpper "hello"            # "HELLO"
lib.toLower "HELLO"            # "hello"
lib.hasPrefix "pre" "prefix"   # true
lib.hasSuffix "fix" "prefix"   # true
lib.removePrefix "pre" "prefix" # "fix"
lib.splitString "." "a.b.c"    # ["a" "b" "c"]
lib.concatStringsSep ":" ["a" "b"]  # "a:b"

# 列表操作
lib.unique [ 1 1 2 3 ]         # [1 2 3]
lib.findFirst (x: x > 3) 0 [1 2 4 5]  # 4
lib.take 2 [1 2 3 4]           # [1 2]
lib.drop 2 [1 2 3 4]           # [3 4]
lib.flatten [[1 2] [3 4]]      # [1 2 3 4]
lib.forEach [1 2 3] (x: x * 2)  # [2 4 6]

# 属性集操作
lib.optionalAttrs (x > 0) { positive = true; }
# 如果 x > 0 则返回 { positive = true; } 否则 {}

lib.mkIf (x > 0) { positive = true; }

lib.mkMerge [
  { a = 1; }
  { b = 2; }
]
# { a = 1; b = 2; }

# 版本字符串
lib.versionAtLeast "1.2.3" "1.2.0"  # true
lib.versionOlder "1.2.3" "2.0"      # true
```

---

## 5. Flakes

### 5.1 为什么使用 Flakes

```
传统 Nix:
  - nix-channel 管理 nixpkgs 版本（全局共享）
  - 构建结果依赖全局状态
  - 不易复现

Flakes:
  - flake.lock 锁定所有输入版本
  - 纯函数式，不依赖全局状态
  - 真正可复现
  - 标准化的项目结构
```

### 5.2 启用 Flakes

```bash
# 在 /etc/nixos/configuration.nix 中
nix.settings.experimental-features = [ "nix-command" "flakes" ];

# 或在 ~/.config/nix/nix.conf 中
# extra-experimental-features = nix-command flakes
```

### 5.3 flake.nix 结构

```nix
{
  description = "My project flake";

  # 输入（依赖的其他 flakes）
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    nixpkgs-unstable.url = "github:NixOS/nixpkgs/nixos-unstable";

    home-manager = {
      url = "github:nix-community/home-manager/release-24.11";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    # 中国镜像加速
    # nixpkgs.url = "https://mirrors.tuna.tsinghua.edu.cn/nix-channels/nixpkgs-unstable/nixexprs.tar.xz";
  };

  # 输出
  outputs = { self, nixpkgs, nixpkgs-unstable, home-manager, ... }@inputs:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs {
      inherit system;
      config = { allowUnfree = true; };
    };
    unstable = import nixpkgs-unstable {
      inherit system;
      config = { allowUnfree = true; };
    };
  in {
    # NixOS 配置
    nixosConfigurations.myhost = nixpkgs.lib.nixosSystem {
      inherit system;
      specialArgs = { inherit inputs unstable; };
      modules = [
        ./configuration.nix
        home-manager.nixosModules.home-manager
        {
          home-manager.useGlobalPkgs = true;
          home-manager.useUserPackages = true;
          home-manager.users.alice = import ./home.nix;
        }
      ];
    };

    # 开发环境
    devShells.${system}.default = pkgs.mkShell {
      buildInputs = with pkgs; [ python3 nodejs go gcc ];
      shellHook = ''
        echo "Development environment activated"
        export PYTHONPATH="."
      '';
    };

    # 包输出
    packages.${system}.default = pkgs.hello;
  };
}
```

### 5.4 flake.lock

```bash
# flake.lock 是自动生成的依赖锁定文件
# 记录了所有 inputs 的精确版本（git commit + hash）

# 更新锁定文件
nix flake update

# 更新特定 input
nix flake update nixpkgs

# 查看 input 的当前锁定版本
nix flake metadata
```

### 5.5 Flake 常用命令

```bash
# 初始化 flake
nix flake init
nix flake init -t github:nix-community/nix-templates#python

# 更新锁定
nix flake update
nix flake lock

# 查看元数据
nix flake metadata

# 构建
nix build
nix build .#packageName

# 运行
nix run
nix run .#appName

# 开发 shell
nix develop
nix develop .#devShellName

# 检查 flake
nix flake check

# 显示输出
nix flake show
```

---

## 6. Home Manager

### 6.1 什么是 Home Manager

```
Home Manager 是 Nix 生态的声明式用户环境管理工具
类似于 NixOS 管理系统级配置，Home Manager 管理用户级配置：
  - 用户安装的包
  - 配置文件（.bashrc, .gitconfig, .config/*）
  - systemd 用户服务
  - 桌面环境配置
```

### 6.2 安装

```nix
# 作为 NixOS 模块（在 flake 中）
{
  inputs.home-manager.url = "github:nix-community/home-manager/release-24.11";
  inputs.home-manager.inputs.nixpkgs.follows = "nixpkgs";

  outputs = { nixpkgs, home-manager, ... }:
  {
    nixosConfigurations.myhost = nixpkgs.lib.nixosSystem {
      modules = [
        home-manager.nixosModules.home-manager
        {
          home-manager.useGlobalPkgs = true;
          home-manager.useUserPackages = true;
          home-manager.users.alice = ./home.nix;
        }
      ];
    };
  };
}
```

```bash
# 独立安装（非 NixOS 发行版）
nix run home-manager/master -- init --switch

# 激活配置
home-manager switch
```

### 6.3 home.nix 示例

```nix
{ config, pkgs, ... }:

{
  home.username = "alice";
  home.homeDirectory = "/home/alice";
  home.stateVersion = "24.11";

  # 用户级包
  home.packages = with pkgs; [
    firefox
    vscode
    htop
    neofetch
    ripgrep
    fd
    bat
    eza
  ];

  # 不要在 ~/.bashrc 中手动配置，而是在这里
  programs.bash = {
    enable = true;
    shellAliases = {
      ll = "ls -la";
      g = "git";
    };
    initExtra = ''
      export EDITOR=vim
    '';
  };

  programs.git = {
    enable = true;
    userName = "Alice";
    userEmail = "alice@example.com";
    extraConfig = {
      init.defaultBranch = "main";
    };
  };

  programs.starship.enable = true;
  programs.tmux.enable = true;

  # 管理文件
  home.file.".Xresources".text = ''
    XTerm*background: black
    XTerm*foreground: white
  '';

  # systemd 用户服务
  services.syncthing.enable = true;
}
```

---

## 7. 开发 Shell (devShell)

### 7.1 创建 devShell

```nix
# flake.nix 中的 devShells 输出
{
  outputs = { nixpkgs, ... }:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; };
  in {
    devShells.${system}.default = pkgs.mkShell {
      name = "my-project-dev";

      buildInputs = with pkgs; [
        python312
        nodejs_22
        go
      ];

      shellHook = ''
        echo "Development environment ready"
        export PROJECT_ROOT=$(pwd)
      '';

      # 环境变量
      MY_VAR = "hello";
    };
  };
}
```

### 7.2 使用 devShell

```bash
# 进入开发 shell
nix develop

# 进入特定 shell
nix develop .#python

# 从任意 flake 进入
nix develop github:user/repo

# 退出（Ctrl+D 或 exit）
```

---

## 8. 相关资源

- Nix 语言手册: https://nixos.org/manual/nix/stable/language/
- Nix Pills: https://nixos.org/guides/nix-pills/
- Flakes Wiki: https://nixos.wiki/wiki/Flakes
- Home Manager 手册: https://nix-community.github.io/home-manager/
- NixOS 选项搜索: https://search.nixos.org/options
- [[../nix/01-NixOS安装与声明式配置|NixOS 安装与声明式配置]]
- [[../nix/03-nixpkgs与包管理|nixpkgs 与包管理]]
