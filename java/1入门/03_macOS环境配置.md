# 03 macOS 环境配置

macOS 是 Java 开发的优秀平台：UNIX 底层与 Linux 服务器环境高度一致，Homebrew 让工具链管理轻松，Apple Silicon 后 JDK 原生 ARM 支持性能出色。本章覆盖 Homebrew 安装、多版本管理（java_home / jenv / SDKMAN）、zsh 环境变量配置，最后给出三平台差异总结表。

---

## 一、前置认知：macOS 的 Java 特殊性

在动手前先了解三个 macOS 独有的概念：

1. **系统自带过 Java 吗？** 现代 macOS 不预装 Java。在终端敲 `java` 会弹出安装引导——那是 Oracle 老式安装器，不要走这条路，统一用 Homebrew
2. **`/usr/bin/java` 是什么？** 它是个"存根"（stub）程序，作用是转发到你真正安装的 JVM。真正的 JDK 都住在 `/Library/Java/JavaVirtualMachines/` 目录下
3. **`java_home` 工具**：macOS 独有的 `/usr/libexec/java_home`，用于枚举和定位已装 JDK——Linux 没有对应物

与 C 对比：macOS 装 clang 走 `xcode-select --install`，装 JDK 则完全靠第三方发行版；两者都推荐 Homebrew 统一管理。

---

## 二、Homebrew 安装 JDK

### 2.1 若尚未安装 Homebrew

```bash
# 官方安装脚本(Apple Silicon 装到 /opt/homebrew,Intel 装到 /usr/local)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装后按提示把 brew 加入 PATH(zsh)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
eval "$(/opt/homebrew/bin/brew shellenv)"
brew --version
```

### 2.2 方式一：Temurin cask（推荐）

```bash
# Temurin 是 Eclipse 基金会维护的 OpenJDK 发行版,与 Windows/Linux 教程保持一致
brew install --cask temurin@21

# 验证
java -version
javac -version
```

cask 版会安装到 `/Library/Java/JavaVirtualMachines/temurin-21.jdk/`。

### 2.3 方式二：openjdk 公式

```bash
# Homebrew 自己打包的 OpenJDK
brew install openjdk@21
```

注意：公式版的特殊之处在于**不会自动注册到系统**，需要手动链接：

```bash
# 按安装完成后的提示操作(大意如下):
sudo ln -sfn /opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk \
     /Library/Java/JavaVirtualMachines/openjdk-21.jdk

# 并把二进制加入 PATH(写入 ~/.zshrc,见第四节)
export PATH="/opt/homebrew/opt/openjdk@21/bin:$PATH"
```

两种方式对比：

| 维度 | `--cask temurin` | `openjdk@21` |
|------|-----------------|--------------|
| 安装位置 | /Library/Java/...（系统级）| /opt/homebrew/opt/...（用户级）|
| 自动注册给 java_home | 是 | 需手动 symlink |
| 升级方式 | brew upgrade | brew upgrade |
| 推荐 | 追求省事 | 已深度 Homebrew 化 |

选一个即可，本教程后续以 **temurin cask** 为准。

---

## 三、多版本管理

### 3.1 /usr/libexec/java_home 工具

```bash
# 列出所有已安装的 JDK
/usr/libexec/java_home -V
# Matching Java Virtual Machines (2):
#   21.0.5 (arm64) "Eclipse Temurin 21" - .../temurin-21.jdk/Contents/Home
#   17.0.13 (arm64) "Eclipse Temurin 17" - .../temurin-17.jdk/Contents/Home

# 输出指定大版本的 HOME 路径
/usr/libexec/java_home -v 21
# /Library/Java/JavaVirtualMachines/temurin-21.jdk/Contents/Home

# 用它直接运行指定版本
$(/usr/libexec/java_home -v 17)/bin/java -version
```

注意 macOS 的目录结构：JDK 包是 `.jdk` 后缀的 bundle，真正的根目录要再进一层 `Contents/Home`。所以 JAVA_HOME 必须写到 `Contents/Home` 这一级，这是 macOS 与 Linux 配置路径时最容易踩的差异点。

### 3.2 方案一：JAVA_HOME 手动指定版本

```bash
# ~/.zshrc 中固定使用 21:
export JAVA_HOME=$(/usr/libexec/java_home -v 21)
export PATH="$JAVA_HOME/bin:$PATH"
```

写法的好处：动态求值，不硬编码完整路径；升级小版本无需改动。

临时切换（仅当前终端）：

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
mvn -version   # 假设装了 Maven,可见它已跟随 17
```

### 3.3 方案二：jenv

jenv 只管"切换"不管"安装"，与 Homebrew 配合使用：

```bash
brew install jenv

# zsh 初始化
echo 'export PATH="$HOME/.jenv/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(jenv init -)"' >> ~/.zshrc
source ~/.zshrc

# 注册已装的 JDK(jenv enable-plugins export 才会同步 JAVA_HOME)
jenv enable-plugins export
jenv add /Library/Java/JavaVirtualMachines/temurin-21.jdk/Contents/Home
jenv add /Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home

# 三级切换
jenv global 21          # 全局默认
jenv shell 17           # 当前终端临时
cd my-project && jenv local 17   # 目录级(生成 .java-version 文件)

jenv versions           # 查看所有
```

### 3.4 方案三：SDKMAN

[[02_Linux环境配置|Linux 章]] 详细讲过的 SDKMAN 在 macOS 上原样可用：

```bash
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"

sdk list java
sdk install java 21.0.5-tem
sdk default java 21.0.5-tem
```

三种方案怎么选：

| 方案 | 安装能力 | 切换粒度 | JAVA_HOME 同步 | 推荐人群 |
|------|---------|---------|---------------|---------|
| java_home 手动 | 无（配合 brew）| 全局/临时 | 手动写 | 单版本或偶尔切换 |
| jenv | 无（配合 brew）| 全局/shell/**目录级** | 插件支持 | 多项目不同版本 |
| SDKMAN | **有（独立下载）**| 全局/shell/目录级(.sdkmanrc)| 自动 | 想三平台体验一致 |

> 与 C 对比：这类似用 mise/asdf 管理 gcc 多版本的需求场景；区别是 Java 项目对 JDK 版本的敏感度远高于 C 项目对 gcc 版本的敏感度。

---

## 四、JAVA_HOME 写入 ~/.zshrc

macOS 从 Catalina 起，默认 shell 是 **zsh**，配置文件是 `~/.zshrc`（不是老教程里的 `~/.bash_profile`）。如果你 `chsh -s /bin/bash` 改回过 bash，才用 `~/.bashrc`。

```bash
# 追加到 ~/.zshrc(cask temurin 方案)
export JAVA_HOME=$(/usr/libexec/java_home -v 21)
export PATH="$JAVA_HOME/bin:$PATH"

# 使生效并验证
source ~/.zshrc
echo $JAVA_HOME
# /Library/Java/JavaVirtualMachines/temurin-21.jdk/Contents/Home
which java
# /Library/Java/JavaVirtualMachines/temurin-21.jdk/Contents/Home/bin/java
```

若用的是 openjdk 公式方案，则改为：

```bash
export JAVA_HOME="/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"
```

zsh 相关排障提示：

| 现象 | 原因 | 解决 |
|------|------|------|
| source 后新终端又失效 | 写进了 .bash_profile 而 shell 是 zsh | 移到 ~/.zshrc |
| PATH 里出现重复条目 | 多处重复 export | 无害但可精简，`echo $PATH | tr ':' '\n'` 查看 |
| IDEA 里能跑、终端不能跑 | IDE 用自己的 JDK 设置 | 以终端环境为准排查 |

> 对比 Linux：机制完全一样，只是文件名不同（zshrc vs bashrc）且多了 java_home 这个定位工具。

---

## 五、Xcode Command Line Tools 与 Java 的关系

```bash
xcode-select --install   # 若已装会提示
```

CLT 提供 clang、git、make 等 UNIX 开发基础件。它与 Java 的交集：

1. **部分构建工具间接依赖**：某些原生依赖编译（如 JDBC 驱动中的 native 组件、JNI 项目）会调用 clang/make
2. **git 是 brew/jenv/SDKMAN 安装脚本的依赖**：没有 git，一些安装流程会失败
3. **不需要完整 Xcode**：几个 GB 的 Xcode.app 对 Java 开发毫无必要，几百 MB 的 CLT 足够

结论：装好 CLT 作为系统底座即可，不必为 Java 特意做更多。

---

## 六、Apple Silicon (ARM) 注意事项

M1/M2/M3/M4 芯片的 mac 上有三类二进制：

| 架构类型 | 性能 | 说明 |
|---------|------|------|
| aarch64（ARM 原生）| 最优 | Temurin/Zulu/Oracle JDK 均提供 |
| x86_64 + Rosetta 转译 | 打七折左右 | 兼容用途 |
| universal（双架构合一）| 各取所需 | 部分发行版提供 |

实践要点：

1. **确认下载的是 aarch64 版本**。Adoptium 网站会自动识别；brew 也按当前架构自动选择 formula
2. **验证是否原生运行**：

```bash
java -version
# 输出中看这一行: OpenJDK 64-Bit Server VM Temurin-21.0.5+11 (mix mode, emulated?) 
# 更直接的方式:
file $(which java)
# .../bin/java: Mach-O 64-bit executable arm64   <- arm64 即原生
```

3. **公司遗留的 x86 应用怎么办**：Rosetta 2 可以转译运行（首次触发时系统会提示安装），性能可用但别作为开发主力
4. **Docker 场景**：容器内默认拉取 arm64 镜像；需要 x86 镜像时加 `--platform linux/amd64`（走 QEMU，慢），工程化篇部署时会再提

Apple Silicon 上原生 OpenJDK 的启动速度与吞吐表现优秀，日常 Java 开发体验不输同价位 x86 机器，IDEA 也已有原生 ARM 版本。

---

## 七、验证与第一个程序

```bash
mkdir -p ~/code/java-lab && cd ~/code/java-lab
```

创建 `Hello.java`：

```java
public class Hello {
    public static void main(String[] args) {
        System.out.println("Hello, RootStack!");
        // 打印环境信息,顺便验证架构是否原生
        System.out.println("JVM version : " + System.getProperty("java.version"));
        System.out.println("VM arch     : " + System.getProperty("os.arch"));
        System.out.println("OS name     : " + System.getProperty("os.name"));
    }
}
```

编译运行：

```bash
javac Hello.java    # 编译,生成 Hello.class
java Hello          # 运行
```

预期输出：

```text
Hello, RootStack!
JVM version : 21.0.5
VM arch     : aarch64
OS name     : Mac OS X
```

`os.arch` 显示 `aarch64` 说明是 ARM 原生 JVM；若是 `x86_64` 且你的芯片是 M 系列，说明误装了 Intel 版，回第六节检查。

顺手感受字节码的跨平台承诺：把这份 `Hello.class` 直接 scp 到任意 Linux 服务器上执行 `java Hello`——不需要重新编译，照样输出。这就是 [[00_Java是什么|第一章]] 讲的字节码机制。

---

## 八、常见问题排查

| 现象 | 原因 | 解决 |
|------|------|------|
| 敲 `java` 弹出系统安装框 | 未通过 brew 安装或 PATH 未生效 | 按第二节重装；检查 ~/.zshrc |
| `No Java runtime present, requesting install.` | stub 找不到已注册 JDK | cask 方案重装；或手动 symlink openjdk 公式包 |
| `Unable to locate a Java Runtime to invoke` 同上 | JAVA_HOME 指向不存在路径 | `echo $JAVA_HOME` 核对，末尾要有 `Contents/Home` |
| javac 存在但版本不对 | 多个 JDK 在 PATH 竞争 | `which -a java javac` 逐个查，调整 PATH 顺序 |
| brew upgrade 后版本跳变 | cask 自动升级到新大版本 | 锁定：`brew pin temurin@21`（cask 支持 pin 子命令视 brew 版本而定）|
| 中文乱码 | 终端编码问题（少见，macOS 默认 UTF-8）| 终端设置-描述文件-高级里确认字符编码 UTF-8 |

macOS 相对 Windows 少了 GBK 编码坑，相对 Linux 少了防火墙坑（应用首次监听端口时图形化弹窗授权即可），整体是最省心的开发环境。

---

## 九、三平台差异总结对照表

| 维度 | Windows | Linux | macOS |
|------|---------|-------|-------|
| 推荐安装 | winget / Temurin MSI | SDKMAN / apt/dnf/pacman | brew cask temurin |
| 默认 shell | PowerShell / cmd | bash | **zsh** |
| 环境变量文件 | 系统属性 GUI / setx | ~/.bashrc | ~/.zshrc |
| 环境变量语法 | `setx VAR "value"` | `export VAR=value` | `export VAR=value` |
| JAVA_HOME 典型值 | `C:\Program Files\Eclipse Adoptium\jdk-21...` | `~/.sdkman/candidates/java/current` | `.../temurin-21.jdk/Contents/Home` |
| 多版本管理 | WSL+SDKMAN / jabba | SDKMAN / alternatives | java_home / jenv / SDKMAN |
| PATH 分隔符 | `;`（分号）| **`:`（冒号）** | **`:`（冒号）** |
| 文件路径分隔符 | `\` 反斜杠 | `/` 正斜杠 | `/` 正斜杠 |
| 默认源码编码 | GBK（需 `-encoding utf-8`）| UTF-8 | UTF-8 |
| 防火墙放行 | Windows Defender 弹窗 | firewalld/ufw 命令 | 图形弹窗授权 |
| 系统级 Java 定位工具 | where java | update-alternatives / archlinux-java | /usr/libexec/java_home -V |

两个高频踩坑点单独强调：

1. **PATH 分隔符**：Windows 用分号，Unix 系用冒号。在 Windows 的 Git Bash 里配 PATH 却用了分号，是跨平台新人的经典事故
2. **编码**：只有 Windows 需要 `-encoding utf-8` 补丁；写跨平台构建脚本时应始终显式声明编码

---

## 十、环境自检脚本

把本章所有验证动作收进一个可重复执行的脚本，存为 `check-java.sh`：

```bash
#!/bin/bash
# check-java.sh —— macOS Java 环境自检
pass=0; fail=0

check() {
    if eval "$2" >/dev/null 2>&1; then
        echo "[OK]   $1"; pass=$((pass+1))
    else
        echo "[FAIL] $1"; fail=$((fail+1))
    fi
}

check "brew 已安装"            "command -v brew"
check "java 可用"              "java -version"
check "javac 可用"             "javac -version"
check "JAVA_HOME 已设置"       "[ -n \"\$JAVA_HOME\" ]"
check "JAVA_HOME 指向有效目录"  "[ -d \"\$JAVA_HOME\" ]"
check "版本为 21"              "java -version 2>&1 | grep -q '\"21'"
check "ARM 原生(仅 M 系列)"     "[ \"\$(uname -m)\" != arm64 ] || java -XshowSettings:properties -version 2>&1 | grep -q 'os.arch = aarch64'"

echo "-------------------------"
echo "通过 $pass 项, 失败 $fail 项"
[ $fail -eq 0 ] && echo "环境就绪, 可以开始下一章" || echo "请回到对应小节排错"
```

使用：

```bash
chmod +x check-java.sh
./check-java.sh
```

这个脚本本身也是 shell 练习素材；[[02_Linux环境配置|Linux 章]] 的读者可以原样搬用（去掉 java_home 相关项即可）。

---

## 十一、本章小结

- macOS 不预装 Java，统一用 Homebrew：首选 `brew install --cask temurin@21`
- JDK 安装在 `/Library/Java/JavaVirtualMachines/*.jdk/Contents/Home`，JAVA_HOME 要指到 Contents/Home 层
- 多版本三方案：`/usr/libexec/java_home -v` 手动、jenv 目录级切换、SDKMAN 三平台统一体验
- 配置写入 ~/.zshrc（默认 shell 是 zsh）
- Apple Silicon 选 aarch64 原生包，`file $(which java)` 可验证
- 三平台差异核心记两点：PATH 分隔符 `;` vs `:`；Windows 有 GBK 编码坑而 Unix 系没有

## LeetCode 巩固

环境就绪，热身题依然是 [两数之和](https://leetcode.cn/problems/two-sum/)。macOS 用户可以在 IDEA 或终端里各跑一遍代码找找手感。

下一章我们比较各家编辑器与 IDE，之后就能正式进入代码世界——从 [[05_第一个程序与jshell|第一个程序与 jshell]] 开始。
