# npm 使用教程
---

## 一、npm 是什么

npm（Node Package Manager）是 Node.js 生态的核心包管理器，也是目前世界上最大的软件注册表。本教程面向 RootStack 读者，覆盖安装配置、基本使用、版本管理、npx、进阶用法与常见问题。

### 1.1 工具家族关系

| 工具 | 定位 | 说明 |
|------|------|------|
| Node.js | 运行时 | 执行 JavaScript 的引擎 |
| npm | 包管理器 | Node.js 自带，管理依赖 |
| npx | 包执行器 | npm 附带的临时执行工具 |
| pnpm | 替代包管理器 | 更快、磁盘更省、硬链接安装 |
| yarn | 替代包管理器 | 老牌替代，Classic/Berry 两代 |
| corepack | 版本管理器 | 管理 pnpm/yarn 的 Node 官方工具 |

### 1.2 为什么需要学 npm

| 场景 | 依赖 npm 生态 |
|------|--------------|
| 运行 JS 工具 | `npx` 临时执行（如 `npx @deepseek-ai/dsh web`） |
| 前端/Node 开发 | `npm install` 管理依赖 |
| dsh 插件管理 | `dsh plugin` 底层转发给 pnpm（见 [[dsh|dsh 教程]]） |
| 构建工具 | Vite/Webpack/esbuild 全部通过 npm 分发 |
| CI/CD | `npm ci` 是 CI 环境标准安装方式 |

> 本教程与 [[dsh|DeepSeek Harness 教程]] 互为表里：dsh 的启动（npx）、插件管理（pnpm）都是 npm 生态的活例。

---

## 二、安装与配置

### 2.1 安装 Node.js（自带 npm）

| 系统 | 方式 | 命令 / 操作 |
|------|------|-------------|
| Windows | 官方安装包 | nodejs.org 下载 .msi 安装 |
| Windows | winget | `winget install OpenJS.NodeJS.LTS` |
| macOS | Homebrew | `brew install node` |
| Linux (Debian/Ubuntu) | apt | `sudo apt install nodejs npm` |
| Linux (Arch) | pacman | `sudo pacman -S nodejs npm` |
| 任意平台 | nvm（版本管理） | `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.x/install.sh \| bash` |

```bash
node -v    # v20.x.x
npm -v     # 10.x.x
```

| 方案 | 优点 | 适合 |
|------|------|------|
| nvm | 多版本切换、无权限问题 | 开发主力，推荐 |
| 系统包管理器 | 简单 | 偶尔用 |
| 官方安装包 | 默认 PATH 配置好 | 新手 |

### 2.2 配置镜像源（国内必需）

```bash
# 查看当前源
npm config get registry

# 设置为 npmmirror（淘宝镜像）
npm config set registry https://registry.npmmirror.com

# 恢复官方源
npm config set registry https://registry.npmjs.org/
```

| 镜像 | 地址 |
|------|------|
| 官方 | `https://registry.npmjs.org/` |
| npmmirror（淘宝） | `https://registry.npmmirror.com` |
| 华为云 | `https://mirrors.huaweicloud.com/repository/npm/` |

### 2.3 .npmrc 配置文件

| 位置 | 作用域 |
|------|--------|
| `~/.npmrc` | 用户全局 |
| 项目 `.npmrc` | 仅当前项目（随仓库分发） |
| npm 内置 | 内置默认值 |

```ini
# 项目 .npmrc 示例
registry=https://registry.npmmirror.com
save-exact=true
proxy=http://127.0.0.1:7890
https-proxy=http://127.0.0.1:7890
```

### 2.4 常用 config

| 命令 | 作用 |
|------|------|
| `npm config list` | 列出全部配置 |
| `npm config set <key> <value>` | 设置 |
| `npm config delete <key>` | 删除 |
| `npm config get registry` | 查当前源 |

---

## 三、基本使用

### 3.1 初始化项目

```bash
npm init              # 交互式
npm init -y           # 全部默认
```

package.json 核心字段：

| 字段 | 作用 |
|------|------|
| `name` | 包名（发布时全局唯一） |
| `version` | 版本号（semver） |
| `description` | 描述 |
| `main` | 入口文件（CommonJS） |
| `exports` | 现代入口声明（优先于 main） |
| `scripts` | 命令脚本 |
| `dependencies` | 运行时依赖 |
| `devDependencies` | 开发时依赖 |
| `peerDependencies` | 宿主环境依赖（插件场景常见） |
| `engines` | 要求 Node 版本 |

### 3.2 安装依赖

```bash
npm install                  # 按 package.json 安装
npm install express          # 运行时依赖 (dependencies)
npm install -D typescript    # 开发依赖 (devDependencies)
npm install -g pnpm          # 全局安装
npm install --save-exact lodash   # 精确版本，不用 ^
npm install express@4         # 指定大版本
npm install git+https://github.com/user/repo.git  # 从 git 安装
npm install ./local-pkg.tgz   # 从 tarball 安装
```

| 标志 | 作用 |
|------|------|
| `-D` / `--save-dev` | devDependencies |
| `-g` / `--global` | 全局（含 CLI 工具） |
| `--save-exact` | 不写 `^`/`~`，锁死版本 |
| `--no-save` | 只装不写 package.json |
| `--force` | 强制（绕过检查，慎用） |

### 3.3 卸载与更新

```bash
npm uninstall lodash          # 移除并更新 package.json
npm uninstall -g pnpm
npm update                    # 按语义化版本规则更新
npm update --save             # 更新并写入新版本号
```

### 3.4 scripts 脚本

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "test": "vitest run",
    "start": "node server.js",
    "lint": "eslint .",
    "dsh:web": "npx @deepseek-ai/dsh web"
  }
}
```

```bash
npm run dev        # 执行 dev
npm start          # start 特例：可省略 run
npm test           # test 特例：可省略 run
npm run            # 列出所有可用脚本
```

> scripts 里的命令会自动把 `node_modules/.bin` 加入 PATH，因此直接写 `vite`/`eslint` 即可，不用全路径。

---

## 四、版本管理

### 4.1 semver 语义化版本

格式：`主版本.次版本.修订号`（`MAJOR.MINOR.PATCH`）

| 变更 | 版本位 | 例子 |
|------|--------|------|
| 不兼容 API 变更 | MAJOR +1 | 1.2.3 → 2.0.0 |
| 向后兼容新功能 | MINOR +1 | 1.2.3 → 1.3.0 |
| 向后兼容的修复 | PATCH +1 | 1.2.3 → 1.2.4 |

### 4.2 版本范围符号

| 写法 | 含义 | 例子 |
|------|------|------|
| `^1.2.3` | 允许 1.x.x（不升主版本） | 默认行为 |
| `~1.2.3` | 允许 1.2.x（不升次版本） | 保守 |
| `1.2.3` | 精确版本 | 最严格 |
| `>=1.2.0 <2.0.0` | 范围 |
| `latest` | 最新 tag |
| `1.2.x` | 任意修订 |

```text
^1.2.3   → 1.2.3 <= v < 2.0.0
~1.2.3   → 1.2.3 <= v < 1.3.0
```

### 4.3 package-lock.json 与 npm ci

| 文件/命令 | 作用 |
|-----------|------|
| `package-lock.json` | 锁死完整依赖树（含传递依赖的精确版本） |
| `npm install` | 按 lock 安装，也允许更新 |
| `npm ci` | **严格按 lock 安装**：删除 node_modules 后全新安装，CI 环境标准做法 |

```bash
# CI 中（更快、更可复现）
npm ci
```

| 场景 | 用 install | 用 ci |
|------|:---:|:---:|
| 日常开发 | 是 | |
| CI/CD | | 是 |
| 要更新依赖 | 是 | |
| 可复现构建 | | 是 |

### 4.4 检查与查询

```bash
npm outdated          # 哪些包有新版本（红/黄/绿）
npm view lodash       # 查看包信息
npm view lodash versions   # 全部历史版本
npm view lodash@4 version # 指定版本
npm ls                # 当前依赖树
npm ls --depth=0      # 只看顶层
npm audit             # 安全审计
```

### 4.5 dist-tags

| 命令 | 作用 |
|------|------|
| `npm view <pkg> dist-tags` | 查看标签（latest/beta/next） |
| `npm dist-tag add <pkg>@<ver> <tag>` | 加标签 |
| `npm dist-tag ls <pkg>` | 列出 |

```bash
npm install react@beta        # 安装 beta 通道
```

---

## 五、npx

### 5.1 用途

npx 解决"临时执行一个包"的问题：**不写入项目依赖，下载即用**。

```bash
npx @deepseek-ai/dsh web      # 直接运行 dsh（不污染项目）
npx vite --version
npx -y cowsay hello           # -y 跳过确认
```

| 行为 | 说明 |
|------|------|
| 本地已装 | 优先用 `node_modules/.bin` 里的 |
| 本地没有 | 临时下载到缓存执行 |
| `-y` | 自动确认安装提示 |
| `-p <pkg>` | 指定临时包配合命令 |

### 5.2 与全局安装的选择

| 场景 | 推荐 |
|------|------|
| 偶尔用一次的工具 | npx（如 dsh） |
| 天天用的 CLI | 全局安装（`npm i -g`）或项目 devDependency |
| 项目内固定版本工具 | devDependency + npm run |

> **dsh 的启动就是 npx 的典型用法**：`npx @deepseek-ai/dsh web` 不装进任何项目，每次按需执行。

---

## 六、进阶用法

### 6.1 workspaces（monorepo）

```json
// 根 package.json
{
  "name": "my-monorepo",
  "private": true,
  "workspaces": ["packages/*"]
}
```

```bash
npm install                    # 一次安装所有 workspace 依赖
npm run build -w @scope/pkg-a  # 只跑某个 workspace
npm install lodash -w pkg-a    # 只给某 workspace 装
```

| 收益 | 说明 |
|------|------|
| 依赖提升 | 公共依赖只装一份 |
| 交叉引用 | workspace 之间直接 link |
| 统一脚本 | 根目录统管构建 |

### 6.2 npm link（本地调试）

```bash
# 在包目录：注册全局链接
npm link

# 在消费项目：链接进来
npm link your-package-name

# 取消
npm unlink your-package-name
```

> 开发 dsh 插件时可配合使用：本地改插件源码，消费端实时生效（或直接 `dsh plugin add ./插件目录`，见 [[dsh|dsh 教程]]）。

### 6.3 打包与发布

```bash
npm pack                     # 打 tarball（预览发布内容）
npm pack --dry-run           # 预览不打包

npm login                    # 登录（一次）
npm publish                  # 发布
npm publish --access public  # 公有包（默认私有需付费）
npm publish --tag beta       # 指定 tag
```

```text
发布前检查:
1. name 全局唯一（npm view 你的包名 确认不存在）
2. files 字段控制发布内容（默认排除 .git/node_modules）
3. version 必须高于已发布版本
4. 有 README.md 显示在 npm 页面
```

### 6.4 npm audit 安全审计

```bash
npm audit                  # 列出漏洞
npm audit fix              # 自动修复（升级兼容版本）
npm audit fix --force      # 强制升级主版本（可能破坏兼容）
npm audit --production     # 只看运行时依赖
```

### 6.5 overrides（强制版本）

```json
{
  "overrides": {
    "lodash": "4.17.21",
    "react": "$react"       // 跟随顶层 react 版本
  }
}
```

> 用于：修传递依赖漏洞、统一多个子依赖的版本。谨慎使用——覆盖可能破坏依赖契约。

### 6.6 其他实用

```bash
npm dedupe              # 去重相同版本
npm prune               # 移除 package.json 外的多余包
npm shrinkwrap          # 生成强锁文件
npm ci --ignore-scripts # CI 跳过构建脚本（加快）
npm config get prefix   # 全局安装目录
```

---

## 七、常见问题与解决方案

### 7.1 权限错误 EACCES

```text
Error: EACCES: permission denied, mkdir '/usr/lib/node_modules/xxx'
```

| 方案 | 命令 |
|------|------|
| 推荐：改全局目录到用户区 | `npm config set prefix ~/.npm-global` + PATH 加 `~/.npm-global/bin` |
| nvm 管理 Node | 换 nvm 后全局安装无需 sudo |
| Windows | 不要用管理员安装，改用 nvm-windows |

### 7.2 镜像源相关问题

| 现象 | 原因 | 解决 |
|------|------|------|
| 404 Not Found | 包不存在或版本号写错 | `npm view <包> versions` 确认 |
| 404（镜像同步延迟） | 新包未同步 | 换官方源 `npm i --registry=https://registry.npmjs.org/` |
| 403 Forbidden | 私有包未登录/无权限 | 检查 npm login、包 scope |
| ETIMEDOUT | 网络 | 换镜像/开代理 |

### 7.3 ERESOLVE 依赖冲突

```text
npm error code ERESOLVE
npm error Could not resolve dependency
```

| 方案 | 说明 |
|------|------|
| `--legacy-peer-deps` | 忽略 peer 依赖冲突（老项目常见） |
| `--force` | 强制安装（慎用） |
| 手动升级冲突包 | 根因修复 |
| 用 overrides | 统一冲突包版本 |

```bash
npm install --legacy-peer-deps
```

### 7.4 node-gyp 编译失败（原生模块）

```text
gyp ERR! stack Error: Can't find Python executable "python"
```

| 平台 | 解决 |
|------|------|
| Windows | 装 Visual Studio Build Tools + Python，或 `npm install -g windows-build-tools`（旧） |
| Windows 新方案 | `npm install --global node-gyp` + VS2022 勾选 C++ 工作负载 |
| Linux | `sudo apt install build-essential python3` |
| macOS | `xcode-select --install` |

### 7.5 代理设置

```bash
npm config set proxy http://127.0.0.1:7890
npm config set https-proxy http://127.0.0.1:7890

# 或临时
npm install --proxy http://127.0.0.1:7890
```

| 场景 | 说明 |
|------|------|
| npm 走代理 | 上面 config 即可 |
| Node 运行时走代理 | 需设置 `NODE_USE_ENV_PROXY=1`（dsh 场景见 [[dsh|dsh 教程]]） |

### 7.6 缓存与清理

```bash
npm cache verify          # 验证缓存
npm cache clean --force   # 清缓存（最后手段）
npx clear-npx-cache       # 清 npx 缓存（dsh 更新后仍跑旧版时）
```

### 7.7 lockfile 冲突

```text
npm error In the "package-lock.json" file, an object for the package "xxx" ...
```

```bash
# 删除后重新生成（确认后执行）
rm package-lock.json && npm install
# 或
git checkout package-lock.json && npm ci
```

### 7.8 幽灵依赖与 pnpm 视角

| 概念 | 说明 |
|------|------|
| 幽灵依赖 | 代码直接 import 了未声明的传递依赖（npm 提升导致"碰巧能用"） |
| 严格模式 | pnpm 默认隔离 node_modules，幽灵依赖直接报错 |
| 解决 | 把用到的包显式写进 package.json |

> dsh 插件管理使用 pnpm，因此**插件必须显式声明全部依赖**，不能依赖提升——这是 dsh 插件开发与 npm 教程最直接的结合点。

### 7.9 其他高频问题

| 问题 | 解决 |
|------|------|
| `Cannot find module 'xxx'` | `npm install` 或检查 node_modules 是否被删 |
| `ENOENT: no such file or directory` | 路径问题：确认 package.json 位置、脚本路径 |
| `npm ERR! Missing script: "dev"` | scripts 里没有该命令，`npm run` 查看 |
| 全局命令找不到 | PATH 未含 `npm config get prefix`/bin |
| engine 版本不符 | `npm install --engine-strict=false` 或升级 Node |

---

## 八、与 dsh 的结合

| dsh 环节 | npm 生态工具 | 对应 npm 知识点 |
|----------|-------------|----------------|
| 启动 | `npx @deepseek-ai/dsh web` | npx 临时执行（第五章） |
| 插件安装 | `dsh plugin --profile x add <pkg>` | pnpm（npm 生态家族） |
| 插件发布 | `pnpm publish` / `npm pack` | 发布与打包（第六章） |
| git 安装 | prepare 脚本 + allowBuilds | scripts 生命周期（第三章） |
| 幽灵依赖 | pnpm 严格模式 | 显式声明依赖（第七章 7.8） |

> 完整流程见 [[dsh|DeepSeek Harness 教程]]：从安装、profile、插件开发到发布。

---

## 九、速查表

| 命令 | 作用 |
|------|------|
| `npm init -y` | 初始化项目 |
| `npm install <pkg>` | 安装（运行时依赖） |
| `npm install -D <pkg>` | 安装（开发依赖） |
| `npm install -g <pkg>` | 全局安装 |
| `npm uninstall <pkg>` | 卸载 |
| `npm update` | 更新 |
| `npm ci` | 按 lockfile 全新安装（CI） |
| `npm run <script>` | 执行脚本 |
| `npm run` | 列出脚本 |
| `npm outdated` | 查看可更新 |
| `npm audit [fix]` | 安全审计/修复 |
| `npm view <pkg> versions` | 查询版本 |
| `npm ls --depth=0` | 顶层依赖树 |
| `npx <pkg>` | 临时执行 |
| `npm link` | 本地调试链接 |
| `npm pack` | 打包 tarball |
| `npm publish` | 发布 |
| `npm config set registry <url>` | 换源 |

### 关联

- [[dsh|DeepSeek Harness 教程]] — npm 生态的落地案例（npx 启动 + pnpm 插件管理）
- [[vim教程|Vim 教程]] — 终端编辑 package.json
- [[VSCODE的配置与使用|VS Code 配置]] — 编辑 TS/JS 依赖代码