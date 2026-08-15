# DeepSeek Harness (dsh) 安装与使用教程
---

## 一、dsh 是什么

DeepSeek Harness（命令名 `dsh`）是 DeepSeek AI 开源的 agent harness（代理框架），核心设计理念是 **Everything is a plugin**——模型、工具、技能、会话、沙箱、存储、调度、UI 全部以插件形式存在，可以自由替换与重组。

| 特性 | 说明 |
|------|------|
| 开发者 | DeepSeek AI（开源，GitHub: deepseek-ai/deepseek-harness） |
| 底层框架 | Cordis（插件化框架，组合/生命周期/服务/事件） |
| 包名 | `@deepseek-ai/dsh`（npm） |
| 形态 | Web UI（默认 `http://127.0.0.1:3080`）+ headless CLI（一次性任务） |
| 插件分发 | 基于 npm 生态（pnpm 管理），这是它与 [[npm|npm]] 的关联点 |
| 当前状态 | 技术预览（developer preview） |

### 与 RootStack 的定位

`dsh` 是 [[AI_Agent工具使用教程|AI Agent 工具]] 体系中的落地工具之一：本地部署、工作区文件读写、命令执行、插件可编程。本章覆盖从安装到自研插件发布的完整链路。

### 核心概念速览

| 概念 | 一句话 |
|------|--------|
| profile | 一个"配置档案"：插件层的有序堆叠 + 用户覆盖层 |
| bundle | 附带配置层的 npm 包（插件组合包） |
| patch 层 | YAML 配置覆盖层，按顺序叠加 |
| 插件 | 导出 `apply(ctx)` 的 TS 模块，通过 ctx 注册能力 |
| `$DSH_HOME` | 全局状态目录（profiles、共享配置都在这里） |

---

## 二、安装

### 2.1 前置要求

| 依赖 | 要求 | 说明 |
|------|------|------|
| Node.js | LTS 版本（18/20/22） | 运行时，npm 随附 |
| npm | 随 Node.js 附带 | npx 启动 dsh 用 |
| pnpm | 需在 PATH | `dsh plugin` 命令转发给 pnpm，必须可用 |
| 网络 | 能访问 npm registry | 国内可配置镜像（见 [[npm|npm 教程]] 镜像章节） |

```bash
# 检查前置
node -v
npm -v
pnpm -v    # 没有则: npm install -g pnpm
```

### 2.2 从 npm 启动（最简方式）

```bash
npx @deepseek-ai/dsh web
```

| 要点 | 说明 |
|------|------|
| 首次运行 | npx 自动下载 `@deepseek-ai/dsh` 到缓存并执行 |
| 启动结果 | 终端打印访问地址，默认 `http://127.0.0.1:3080` |
| 固定版本 | `npx @deepseek-ai/dsh@0.x.x web` 指定版本 |
| 代理环境 | 设置 `NODE_USE_ENV_PROXY=1` 让 Node 遵循 `HTTP_PROXY`/`HTTPS_PROXY` |

```bash
# 代理环境示例
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
export NODE_USE_ENV_PROXY=1
npx @deepseek-ai/dsh web
```

### 2.3 从源码运行（开发/插件调试）

```bash
git clone https://github.com/deepseek-ai/deepseek-harness.git
cd deepseek-harness
pnpm install
pnpm run build          # 构建产物（frontend 等）
pnpm dsh web            # 源码入口，转发所有参数
```

| 场景 | 用哪种 |
|------|--------|
| 只想用 | `npx @deepseek-ai/dsh web` |
| 想开发插件 | 源码 checkout + `pnpm dsh` |
| 想改 dsh 本身 | 源码 checkout |

> 从源码运行时，`dsh` 命令在仓库根目录下以 `pnpm dsh <args...>` 形式执行；所有文档中的 `dsh ...` 命令对应改为 `pnpm dsh ...`。

### 2.4 环境变量

| 变量 | 作用 |
|------|------|
| `DSH_HOME` | 全局状态目录（默认 `~/.dsh` 或平台惯例路径），profiles 与共享 patch 都在这里 |
| `NODE_USE_ENV_PROXY=1` | 让 Node 版本遵循 `HTTP_PROXY`/`HTTPS_PROXY` |
| `HTTP_PROXY` / `HTTPS_PROXY` | 常规代理变量 |

---

## 三、Web UI 使用

### 3.1 启动与访问

```bash
npx @deepseek-ai/dsh web
# 打开 http://127.0.0.1:3080
```

### 3.2 配置模型

打开 **设置 → 模型**：

| 步骤 | 操作 |
|------|------|
| 1 | 输入 DeepSeek API 密钥并保存 |
| 2 | 模型路由立即可用，无需重启服务器 |
| 3 | 其他提供方或自定义 OpenAI 兼容端点：见官方模型配置指南 |

### 3.3 选择工作区

| 步骤 | 操作 |
|------|------|
| 1 | 点击 **选择工作区** |
| 2 | 添加启动 `dsh` 时所在的项目目录 |
| 3 | 选中该目录（选中前会话输入框不可用） |

> `dsh` 进程以**调用目录**为默认文件系统位置；工作区是 agent 可以读写文件的根目录。

### 3.4 运行任务

在会话输入框发送任务，例如：

```text
Summarize this repository and identify its main packages.
```

| 能力 | 说明 |
|------|------|
| 文件操作 | 读写工作区文件 |
| 命令执行 | 在工作区运行命令 |
| 委派 | 拆分子任务 |
| 计划 | 维护任务计划 |
| 审批 | 超出当前权限策略的操作会先询问你 |

---

## 四、Profile 与 CLI 模式

### 4.1 Profile 概念

Profile 是 `dsh` 的"配置档案"：**有序的插件 bundle 层 + 用户自己的覆盖层**。web 与 headless 是出厂内置的两个 profile。

### 4.2 命令语法

| 命令 | 用途 |
|------|------|
| `dsh --profile <名>` | 启动指定 profile |
| `dsh --profile headless "job"` | 跑一次持久会话，打印最终答案后退出 |
| `dsh web` | `--profile web` 的别名 |
| `dsh plugin --profile <名> <pnpm参数...>` | 管理该 profile 的插件（转发给 pnpm） |
| `dsh --profile <名> --dump-config` | 只打印各层合并后的配置，不启动 |

```bash
# headless 一次性任务
dsh --profile headless "分析 /tmp/x.log 中的错误模式"

# 查看某 profile 的合并配置（验证插件层是否生效）
dsh --profile demo --dump-config
```

### 4.3 Profile 目录结构

Profile 位于 `$DSH_HOME/profiles/<名>/`：

| 文件 | 作用 |
|------|------|
| `package.json` | 树外插件依赖（pnpm 管理）+ profile manifest |
| `dsh.profile`（package.json 内） | manifest，含有序的 `bundles` 列表 |
| `cordis.patch.yml` | 用户自己的 patch 层（每个 bundle 层之后应用） |
| `pnpm-workspace.yaml` | pnpm 授权配置（如 `allowBuilds`） |

```json
{
  "name": "dsh-profile-demo",
  "private": true,
  "dependencies": {
    "dsh-hello-plugin": "link:/path/to/hello-plugin"
  },
  "dsh": {
    "profile": {
      "bundles": [
        "@deepseek-ai/dsh-base",
        "dsh-hello-plugin"
      ]
    }
  }
}
```

### 4.4 出厂 bundle

| bundle | 用途 |
|--------|------|
| `@deepseek-ai/dsh-base` | 基础能力（默认第一个 bundle） |
| `@deepseek-ai/dsh-web-app` | Web UI（web profile = base + web-app） |
| `@deepseek-ai/dsh-headless` | headless（headless profile = base + headless） |

> 首次使用 `web`/`headless` 会自动从模板初始化；其他名字的 profile 首次使用时以 `@deepseek-ai/dsh-base` 为基础创建。

---

## 五、插件安装与卸载

### 5.1 命令总览

`dsh plugin --profile <名> <args...>` 在 profile 目录内**转发给 pnpm**，因此 pnpm 的所有子命令都可用：

| 命令 | 作用 |
|------|------|
| `dsh plugin --profile demo add <包>` | 安装插件（自动入 bundle 层） |
| `dsh plugin --profile demo remove <包>` | 卸载（同时移除依赖与对应层） |
| `dsh plugin --profile demo update` | 更新 |
| `dsh plugin --profile demo why <包>` | 查依赖来源 |
| `dsh plugin --profile demo list` | 列出已装包 |

```bash
# 从 GitHub 安装
dsh plugin --profile tui add github:deepseek-harness/turtle-ui
dsh plugin --profile tui remove turtle-ui
dsh --profile tui
```

### 5.2 四种安装来源

| 来源 | 写法 | 说明 |
|------|------|------|
| npm 包 | `add your-package` | 预构建代码，即装即用 |
| GitHub | `add github:user/repo` | 拉源码，需要 `prepare` 脚本构建 |
| 本地目录 | `add ./hello-plugin` | 相对路径锚定调用目录（`file:`/`link:` 同理） |
| tarball | `add ./hello-plugin-0.1.0.tgz` | `pnpm pack` 产物，无需构建授权 |

> 相对路径（`.`、`../plugin` 及 `file:`/`link:` 形式）以**调用目录**为锚点：在插件 checkout 目录里执行 `add .` 安装的是该 checkout，而不是 profile。

### 5.3 Git 安装的 allowBuilds 授权

从 Git 安装时拉取的是**源码**，构建依赖包的 `prepare` 脚本；pnpm ≥10 默认拒绝运行 git 依赖的 `prepare`，首次 `add` 会失败：

```text
失败信息会打印:
1. pnpm 的 allowBuilds 提示
2. dsh 的指引: 把打印的包键复制进该 profile 的 pnpm-workspace.yaml
```

```yaml
# $DSH_HOME/profiles/<名>/pnpm-workspace.yaml
allowBuilds:
  dsh-hello-plugin: true
```

| 分发方式 | 是否需要用户授权 | 说明 |
|----------|:---:|------|
| npm 发布 | 否 | 发布时已构建好 `lib/` |
| tarball | 否 | `pnpm pack` 产物 |
| GitHub 源码 | 是 | `prepare` + `allowBuilds: true` |

### 5.4 层（bundle）自动 reconcile

每次 `dsh plugin` 成功执行后，`dsh.profile.bundles` 会与已安装状态自动对齐：

| 情况 | 结果 |
|------|------|
| 依赖声明了 `"dsh": {"bundle": {...}}` | 加入层堆叠（update 获得声明也自动激活） |
| 依赖没有 bundle 声明 | 作为普通依赖安装，打一条一次性警告，不激活层 |
| 依赖被移除 | 对应层离开堆叠 |

---

## 六、自己制作插件

### 6.1 第一个插件

插件 = 导出 `apply` 函数的 TypeScript 模块。框架加载时调用 `apply`，传入 `ctx`（上下文对象），你通过 `ctx` 注册能力。

```bash
mkdir -p scratch-plugin/src
```

```ts
// scratch-plugin/src/my-plugin.ts
import type { Context } from '@deepseek-ai/cordis'

export const name = 'hello-plugin'

export function apply(ctx: Context) {
  // 依赖的服务就绪后这里才会执行
  console.log('[hello-plugin] plugin loaded!')
}
```

```yaml
# scratch-plugin/cordis.yml —— 本地插件的 Web 覆盖层
- insert:
    - id: hello
      name: '/absolute/path/to/deepseek-harness/scratch-plugin/src/my-plugin.ts'
```

> 插件路径必须是**绝对路径**。patch 文件只贡献配置，不改变 loader 解析模块时的 profile 目录。

```bash
# 从源码 checkout 根目录启动（加载本地插件）
pnpm dsh web --patch ./scratch-plugin/cordis.yml
# 打开 http://127.0.0.1:3080，终端应打印 [hello-plugin] plugin loaded!
```

### 6.2 插件的三种形态

| 形态 | 适用 |
|------|------|
| 函数形式（`export function apply(ctx)`） | 大多数情况，最简 |
| 对象形式（`export default { name, inject, apply }`） | 结构化声明 |
| 类形式（`class extends Service`） | 需要向其他插件提供服务时 |

```ts
// 对象形式
export default {
  name: 'my-plugin',
  inject: ['tools'],
  apply(ctx: Context) {
    // ...
  },
}
```

```ts
// 类形式（提供服务）
import { Service, type Context } from '@deepseek-ai/cordis'

export default class MyService extends Service {
  static inject = ['tools']
  constructor(ctx: Context) {
    super(ctx, 'myService')
  }
}
```

### 6.3 生命周期与自动清理

通过 `ctx` 注册的一切（事件监听、工具、定时器）在插件卸载时**自动清理**，无需手动 removeListener。

需要手动清理的资源（如网络连接）用 `ctx.effect()`：

```ts
export function apply(ctx: Context) {
  ctx.effect(() => {
    const timer = setInterval(() => {
      console.log('heartbeat')
    }, 5000)
    return () => clearInterval(timer)   // 卸载时执行
  })
}
```

### 6.4 声明服务依赖（inject）

插件需要使用其他服务（`tools`、`llm` 等）时声明 `inject`，框架保证依赖就绪后才加载：

```ts
export const name = 'my-tool-plugin'
export const inject = ['tools']

export function apply(ctx: Context) {
  ctx.tools.register(/* ... */)
}
```

### 6.5 开发一个 Tool

工具注册 DSL 来自 `@deepseek-ai/dsh-tools`：

```ts
import type { Context } from '@deepseek-ai/cordis'
import { defineTool } from '@deepseek-ai/dsh-tools'

export const name = 'greet-tool'
export const inject = ['tools']

export function apply(ctx: Context) {
  ctx.tools.register(defineTool({
    name: 'greet',
    description: 'Greet someone by name.',
    parameters: {
      name: { type: 'string', required: true, description: 'The name to greet' },
    },
    output: {
      schema: { type: 'string' },
      render: (_args, value) => [{ type: 'text', text: value }],
    },
    async execute(args) {
      return `Hello, ${args.name}!`
    },
  }))
}
```

| 字段 | 作用 |
|------|------|
| `name` / `description` | 给模型的工具元信息 |
| `parameters` | 参数 schema，自动推断并校验 `args` |
| `output.schema` | 返回值 schema（canonical value） |
| `output.render` | 把返回值转成模型可见内容 |
| `execute` | 实际执行逻辑 |

```bash
# 重启开发命令（若未在运行）
pnpm dsh web --patch ./scratch-plugin/cordis.yml
# 在 UI 里问: Use the greet tool to greet Ada.
# 模型调用 greet 并收到 Hello, Ada!
```

### 6.6 插件配置

插件可以接受用户配置（config 系统）：在插件中声明配置 schema，用户通过 patch 层注入值。配置合并遵循层顺序（见 7.3），适合把 API key、开关、参数外置。

---

## 七、打包与安装插件

### 7.1 Bundle 是什么

Bundle = **附带一个配置层的 npm 包**。区别于普通依赖包：它在 manifest 里声明 patch 层，安装后自动加入 profile 的层堆叠。

```json
// hello-plugin/package.json
{
  "name": "dsh-hello-plugin",
  "version": "0.1.0",
  "dependencies": {
    "@deepseek-ai/cordis": "^2.0.0"
  },
  "dsh": {
    "bundle": {
      "patch": "./cordis.patch.yml"
    }
  }
}
```

| 包类型 | 是否激活层 | 用途 |
|--------|:---:|------|
| 声明 `dsh.bundle` | 是 | 插件本体，用户启用 |
| 无 `dsh.bundle` | 否（警告） | 仅供插件 import 的库 |

### 7.2 安装本地 checkout 并验证

```bash
# 在包含 hello-plugin 的目录中
dsh plugin --profile demo add ./hello-plugin

# 验证层（不启动）
dsh --profile demo --dump-config   # 输出中应有 "# == dsh-hello-plugin" 层

# 启动
dsh --profile demo
```

```bash
# 卸载：同时移除依赖和对应层
dsh plugin --profile demo remove dsh-hello-plugin
```

### 7.3 层顺序（决定配置合并结果）

```text
1. dsh.profile.bundles 里的各 bundle patch（按列表顺序，先是 @deepseek-ai/dsh-base，再按加入顺序）
2. profile 自己的 cordis.patch.yml
3. $DSH_HOME/cordis.patch.yml（机器本地偏好，各 profile 共享）
4. 每个 --patch <路径> overlay（按 argv 顺序）
```

> 后面的层覆盖前面的层。改配置时先想清楚"这个值应该放哪一层"：项目配置放 bundle/profile，机器偏好放 `$DSH_HOME`，临时调试放 `--patch`。

---

## 八、提交与发布插件

### 8.1 三种分发方式对比

| 方式 | 命令 | 用户侧安装 | 构建责任 |
|------|------|-----------|---------|
| 发布 npm | `pnpm publish` | `dsh plugin add your-package` | 作者（发布时构建好 `lib/`） |
| tarball | `pnpm pack` | `dsh plugin add ./xxx.tgz` | 作者 |
| GitHub 安装 | 打 tag | `dsh plugin add github:you/repo` | 用户（prepare + allowBuilds） |

### 8.2 发布到 npm（推荐）

```bash
# 1. 构建
pnpm run build    # 产出 lib/

# 2. 登录
npm login

# 3. 发布（lib/ 随包发布）
pnpm publish
```

### 8.3 GitHub 源码分发的 prepare 脚本

Git 安装拉的是源码，作者必须提供自包含的 `prepare` 脚本（pnpm 在 git 安装后运行它构建发布入口）：

| 要求 | 说明 |
|------|------|
| 自包含 | 不能假设开发环境上下文（如 monorepo checkout） |
| 示例 | turtle-ui：`prepare` 用专用 tsdown 配置直接转译 `src/`，不依赖项目引用、不做类型检查 |
| 用户侧 | pnpm ≥10 需 `allowBuilds: true`（见 5.3） |

```json
// package.json
{
  "scripts": {
    "prepare": "tsdown src/index.ts --format esm --out-dir lib"
  }
}
```

### 8.4 提交到社区

| 渠道 | 用途 |
|------|------|
| GitHub Discussions | 提交反馈、bug 报告、功能建议 |
| `dsh-plugin` topic | 给插件仓库加该 topic（GitHub Topics）提高发现度 |
| Discord | 加入 DeepSeek Harness 社区交流 |

```text
提交清单:
1. 仓库 README 写明安装方式（dsh plugin add 你的包名）
2. package.json 声明 dsh.bundle（patch 层）
3. 提供构建（npm 发布/tarball 预构建 或 prepare 脚本）
4. 仓库加 dsh-plugin topic
5. Discussions 发帖介绍
```

---

## 九、常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `npx` 每次下载慢 | 无缓存/网络慢 | 配置 npm 镜像（见 [[npm|npm 教程]]）；`npx @deepseek-ai/dsh@<版本>` 固定版本复用缓存 |
| 端口 3080 被占用 | 其他进程占用 | 改端口或先 `lsof -i :3080` 查占用 |
| 启动报模块解析错误（源码运行） | 缺少构建产物 | 先 `pnpm run build`（文档明确要求先构建再运行） |
| 浏览器 UI 是旧代码 | 存在陈旧 bundle | 源码模式下重建：`pnpm run build`（launcher 不检查新鲜度） |
| git 安装失败并提示 allowBuilds | pnpm ≥10 拒绝 prepare | 复制打印的包键到 profile 的 `pnpm-workspace.yaml` |
| 代理不生效 | Node 未遵循环境代理 | `NODE_USE_ENV_PROXY=1` 后重试 |
| `dsh plugin` 报 pnpm 不存在 | pnpm 不在 PATH | `npm install -g pnpm` |
| 首次 `add` 失败（新 profile） | profile 未初始化 | `dsh plugin --profile <名> add <包>` 会自动初始化（base 模板） |
| 包装了但没层 | manifest 无 `dsh.bundle` | 只作为普通依赖，需在 package.json 声明 bundle |
| Windows 下路径问题 | 绝对路径/分隔符 | patch 中插件路径用绝对路径，注意反斜杠转义 |

---

## 十、速查表

### 命令速查

| 命令 | 作用 |
|------|------|
| `npx @deepseek-ai/dsh web` | 启动 Web UI（推荐日常用） |
| `npx @deepseek-ai/dsh@<v> web` | 固定版本启动 |
| `dsh --profile headless "job"` | 一次性任务 |
| `dsh --profile <名>` | 启动指定 profile |
| `dsh --profile <名> --dump-config` | 查看合并配置 |
| `dsh plugin --profile <名> add <包>` | 安装插件（npm/github/./tgz） |
| `dsh plugin --profile <名> remove <包>` | 卸载插件 |
| `dsh plugin --profile <名> update` | 更新插件 |
| `pnpm dsh web --patch ./x/cordis.yml` | 源码模式 + 本地插件 |

### 目录速查

| 路径 | 内容 |
|------|------|
| `$DSH_HOME/profiles/<名>/package.json` | profile manifest + 插件依赖 |
| `$DSH_HOME/profiles/<名>/cordis.patch.yml` | profile 层配置 |
| `$DSH_HOME/profiles/<名>/pnpm-workspace.yaml` | allowBuilds 等授权 |
| `$DSH_HOME/cordis.patch.yml` | 机器级共享配置 |

### 关联

- [[npm|npm 教程]] — dsh 的启动（npx）与插件管理（pnpm）都基于 npm 生态
- [[vim教程|Vim 教程]] — 终端编辑插件源码
- [[VSCODE的配置与使用|VS Code 配置]] — 编辑 TS 插件的图形界面选择
- [[AI_Agent工具使用教程|AI Agent 工具]] — RootStack 的 AI 工具体系