# 03 - defineTool 工具开发

> 工具(Tool)是模型与外部世界之间的手。dsh 里定义一个工具只需要调用一次 `defineTool`——但字段背后的设计意图值得逐个讲透:哪些字段是写给模型看的,哪些是写给框架看的,哪些是写给人看的。本章以官方风格的 greet 工具起步,最终实战一个完整可用的 git-log-reader 工具并在 UI 里验证。

前置阅读：[[deepseek-harness/3实战开发/02-第一个插件完整流程|第一个插件]]
相关章节：[[deepseek-harness/2架构/06-LLM适配器与StreamChunk|LLM 适配器]]

---

## 1. defineTool 全字段精讲

`defineTool` 来自 `@deepseek-ai/dsh-tools`,它接收一个对象,返回一个符合工具规范的描述符:

```typescript
import { defineTool } from '@deepseek-ai/dsh-tools'

// 一个工具描述符的骨架:五个核心字段各司其职
export const myTool = defineTool({
  name: 'tool_name',            // 给模型的调用标识
  description: '...',           // 给模型的说明书
  parameters: { /* ... */ },    // 参数 schema,自动校验
  output: { /* ... */ },        // 返回值:canonical + render 两层
  execute: async (args) => { }, // 真正干活的函数
})
```

### 1.1 name:给模型的调用标识

- 命名空间内唯一,模型通过它点名调用;
- 惯例用 snake_case,如 `read_file`、`git_log`;
- 名字要能"自解释":模型在没有任何额外提示的情况下,要能从名字猜出工具用途的一半以上。

### 1.2 description:给模型的说明书

这是**最容易被低估的字段**。description 不是文档,是 prompt 的一部分——它的措辞直接决定模型调不调、何时调、怎么调。

对比同一工具的两种 description:

```text
差:"读取文件。"                          → 模型不知道何时该用它、和 read 有何区别
好:"读取指定路径的文本文件内容并返回字符串。
    仅支持 UTF-8 编码,单次上限 1MB。
    当用户要求查看代码或配置文件内容时使用;
    二进制文件请改用 inspect_binary。"   → 边界清晰,还能引导模型正确分流
```

写 description 的三条军规：

1. **说清楚做什么**(动词开头，一句话)；
2. **说清楚边界**(不支持什么、什么情况不该用)；
3. **给出分流指引**(相近场景应该用哪个别的工具)。

### 1.3 parameters:参数 schema,自动推断与校验

parameters 是一个按参数名组织的 schema 对象,每个参数声明三件事:

```typescript
parameters: {
  // 键名即参数名:模型生成 JSON 时会以此为键
  target: {
    type: 'string',          // 类型:参与 JSON Schema 约束
    required: true,          // 是否必填:缺失时框架直接拒绝执行
    description: '目标对象的说明', // 又是给模型看的:教它怎么填这个值
  },
}
```

框架基于这份 schema 做两件事：**推断**——把 schema 转成模型侧的函数签名，让模型知道该传什么；**校验**——execute 执行前检查模型生成的 args，缺必填项或类型不对直接拦截，不会让你的代码收到脏数据。

每个参数的 `description` 同样重要:它是模型填写该参数的唯一依据,要写成"填空题的题干",例如"要读取的文件的绝对路径,必须是宿主机上的真实路径"。

### 1.4 output:canonical 与 render 的两层分离

这是 dsh 工具设计里最有味道的一点。output 被拆成两个职责：

```typescript
output: {
  // 第一层:schema —— canonical(规范)返回值
  // 描述 execute 返回数据的结构,是给"程序"消费的:
  // 后续链路里的其他工具、日志系统、测试断言都依赖这层数据
  schema: {
    greeting: { type: 'string' },
  },
  // 第二层:render —— 展示层
  // 把 canonical 数据渲染成 UI 可显示的内容块,
  // 是给"人"消费的:同样的数据可以渲染成纯文本、表格甚至图片
  render: (result) => ({
    type: 'text',
    text: result.greeting,
  }),
}
```

为什么必须分层？三个理由：

| 理由 | 说明 |
| --- | --- |
| 一份数据多个受众 | 模型读 canonical;UI 读 render;两者需求天然不同 |
| 渲染可替换 | 同一工具在终端渲染成文本,在 web 渲染成组件,数据层不动 |
| 测试只测 canonical | execute 的返回结构稳定,schema 即契约,测试不必解析渲染产物 |

一句话:**schema 管"是什么",render 管"怎么显示"**。改 UI 样式不动 schema,改返回结构不炸 UI。

### 1.5 execute:异步执行体

```typescript
// execute 接收已通过校验的 args,可以是 async 函数
// 它抛出的异常会被框架捕获并转成工具级错误返回给模型,
// 因此不需要在内部吞掉所有异常
execute: async (args) => {
  return { greeting: `hello ${args.target}` }
}
```

---

## 2. 完整示例一:greet 工具(照录官方风格)

这是最典型的入门工具,结构与官方示例一致:

```typescript
// greet-tool.ts —— 最小完整工具
import { defineTool } from '@deepseek-ai/dsh-tools'

export const greet = defineTool({
  // 调用标识:模型侧看到的名字
  name: 'greet',

  // 给模型的说明书:做什么 + 何时用
  description: '向指定的人打招呼,返回一句问候语。当用户明确要求问候某人时使用。',

  // 参数声明:一个必填的 string
  parameters: {
    name: {
      type: 'string',
      required: true,
      description: '被问候者的名字,例如 "Alice"',
    },
  },

  // 返回值两层:schema 定义 canonical 结构,render 决定展示
  output: {
    schema: {
      greeting: { type: 'string' },
    },
    render: (result) => ({
      type: 'text',
      text: result.greeting,
    }),
  },

  // 异步执行体:args 已经过校验,name 必为 string
  execute: async ({ name }) => {
    return { greeting: `Hello, ${name}!` }
  },
})
```

把它挂进插件只需在 apply 里注册:

```typescript
import type Context from '@deepseek-ai/cordis'
import { greet } from './greet-tool'

export function apply(ctx: Context) {
  // 将工具注册进 context,模型即可发现并调用
  ctx.register(greet)
}
```

---

## 3. 完整示例二:带文件读取的工具

真实工具要面对错误。约定:**把可预期的失败作为正常返回值的一部分(schema 里就有 error 字段),而不是抛异常**——这样模型能读到错误信息并自行决定重试还是换路。

```typescript
// read-text-file.ts —— 带工作区约束与错误约定的文件读取工具
import { defineTool } from '@deepseek-ai/dsh-tools'
import { readFile } from 'node:fs/promises'
import { isAbsolute, resolve } from 'node:path'

// 允许读取的根目录:工具只能触碰这个目录内的文件(工作区约束)
const WORKSPACE_ROOT = resolve(process.cwd(), 'workspace')

export const readTextFile = defineTool({
  name: 'read_text_file',
  description:
    '读取工作区内指定文本文件并返回内容。' +
    '仅允许访问 workspace 目录下的相对路径文件;' +
    '二进制文件与大文件请勿使用本工具。',
  parameters: {
    path: {
      type: 'string',
      required: true,
      description: '相对于 workspace 的文件路径,例如 "notes/todo.md"',
    },
  },
  output: {
    schema: {
      ok: { type: 'boolean' },
      content: { type: 'string' },
      error: { type: 'string' },
    },
    render: (result) =>
      // 展示层根据成败渲染不同内容
      result.ok
        ? { type: 'text', text: result.content }
        : { type: 'text', text: `读取失败:${result.error}` },
  },
  execute: async ({ path }) => {
    // 第一步:拼出绝对路径并做越界检查
    const abs = resolve(WORKSPACE_ROOT, path)
    if (!abs.startsWith(WORKSPACE_ROOT)) {
      // 越界不是异常,是约定的错误返回
      return { ok: false, content: '', error: '路径越出工作区范围' }
    }
    try {
      // 第二步:正常读取
      const content = await readFile(abs, 'utf-8')
      return { ok: true, content, error: '' }
    } catch (e) {
      // 第三步:把系统错误翻译成模型可理解的短语
      return { ok: false, content: '', error: `文件不存在或不可读:${path}` }
    }
  },
})
```

要点回顾:工作区约束在 execute 入口处做路径归一化后前缀校验,防住 `../` 穿越;错误走返回值不走异常,让模型拿到决策依据。

---

## 4. 参数 schema 类型一览

parameters 支持的类型集合:

| 类型 | 写法示例 | 校验行为 | 适用场景 |
| --- | --- | --- | --- |
| string | `{ type: 'string', required: true }` | 非字符串拒绝 | 路径、名称、任意文本 |
| number | `{ type: 'number' }` | 非数值拒绝 | 数量、阈值、超时 |
| boolean | `{ type: 'boolean' }` | 非布尔拒绝 | 开关型选项 |
| array | `{ type: 'array', items: { type: 'string' } }` | 元素类型逐一校验 | 列表输入,如多个路径 |
| object | `{ type: 'object', properties: { ... } }` | 嵌套字段递归校验 | 结构化配置 |
| enum | `{ type: 'string', enum: ['a', 'b'] }` | 取值必须在枚举内 | 固定选项,如模式选择 |

选型建议:**能用 enum 就不用自由 string**——枚举让模型零猜测,也让校验更硬。

---

## 5. output.render 多模态返回

render 不止能返回文本块。返回内容块的 type 可以携带图片等模态:

```typescript
// render 返回多模态内容块的示例
render: (result) => ({
  blocks: [
    // 文本块:常规信息
    { type: 'text', text: `共 ${result.total} 条提交:` },
    // 图片块:例如工具生成了图表文件
    { type: 'image', url: result.chartUrl },
  ],
})
```

设计上依然遵循第 1.4 节的两层分离:图片地址属于 canonical 数据(schema 里是 string 类型的 url 字段),是否以图片形式展示由 render 决定——终端环境可以只打印 URL,web 环境可以内联渲染。

---

## 6. 工具间组合与 PTC 模式

单个工具解决单点问题;当模型把多个工具的输出作为下一步输入串联使用时,就进入了 PTC(Protocol/Tool Composition)模式。dsh 对此没有特殊 API——**canonical 层的结构化返回就是为组合而生的**:A 工具返回的 schema 化数据可以被模型原样填进 B 工具的参数。协议层面的机制详见 [[deepseek-harness/2架构/06-LLM适配器与StreamChunk|LLM 适配器]],本章不展开。

---

## 7. 实战:git-log-reader 工具全流程

现在综合运用全部知识,写一个在生产里有真实价值的工具:在指定仓库执行 `git log` 并格式化返回。

### 7.1 工具实现

创建 `scratch-plugin/src/git-log-reader.ts`:

```typescript
// git-log-reader.ts —— 在指定仓库读取提交历史的工具
import { defineTool } from '@deepseek-ai/dsh-tools'
import { execFile } from 'node:child_process'
import { promisify } from 'node:util'

// promisify 化的 execFile:参数数组传参,避免 shell 注入
const execFileAsync = promisify(execFile)

export const gitLogReader = defineTool({
  name: 'git_log_reader',

  description:
    '读取指定 Git 仓库的最近提交历史并格式化返回。' +
    '当用户询问某个仓库的提交记录、改动历史或最近更新时使用;' +
    '需要查看具体代码差异时应改用 diff 类工具。',

  parameters: {
    repoPath: {
      type: 'string',
      required: true,
      description: 'Git 仓库的绝对路径,例如 "/home/a/projects/demo"',
    },
    maxCount: {
      type: 'number',
      required: false,
      description: '最多返回的提交条数,默认 10,上限 100',
    },
  },

  output: {
    schema: {
      ok: { type: 'boolean' },
      formatted: { type: 'string' },
      total: { type: 'number' },
      error: { type: 'string' },
    },
    render: (result) => ({
      type: 'text',
      text: result.ok ? result.formatted : `git log 失败:${result.error}`,
    }),
  },

  execute: async ({ repoPath, maxCount }) => {
    // 防御性钳制:模型可能传入离谱数字,这里统一收口
    const limit = Math.min(Math.max(maxCount ?? 10, 1), 100)

    try {
      // 用 execFile + 参数数组调用 git,
      // --pretty 定制输出格式:短哈希 | 作者 | 相对时间 | 标题
      const { stdout } = await execFileAsync(
        'git',
        [
          '-C', repoPath,              // -C 指定仓库目录,免 cd
          'log',
          `--max-count=${limit}`,
          '--pretty=format:%h | %an | %ar | %s',
        ],
        // 超时保护:卡住的 git 命令不应拖死整个会话
        { timeout: 10_000 },
      )

      // 统计条数并拼接表头
      const lines = stdout.split('\n').filter(Boolean)
      return {
        ok: true,
        formatted: `最近 ${lines.length} 条提交:\n${stdout}`,
        total: lines.length,
        error: '',
      }
    } catch (e) {
      // 常见失败:路径不存在 / 不是 git 仓库 / 无提交
      return {
        ok: false,
        formatted: '',
        total: 0,
        error: '目录不存在、不是 git 仓库或没有提交历史',
      }
    }
  },
})
```

### 7.2 注册插件

创建 `scratch-plugin/src/git-log-plugin.ts`:

```typescript
// git-log-plugin.ts —— 注册工具的载体插件
import type Context from '@deepseek-ai/cordis'
import { gitLogReader } from './git-log-reader'

export const name = 'git-log-plugin'

export function apply(ctx: Context) {
  ctx.on('ready', () => console.log('[git-log-plugin] 工具注册中'))
  // 注册即暴露给模型
  ctx.register(gitLogReader)
}
```

### 7.3 patch 文件

更新 `scratch-plugin/cordis.yml`(注意仍是绝对路径):

```yaml
insert:
  - id: git-log-plugin
    name: '/home/a/RootStack/deepseek-harness/scratch-plugin/src/git-log-plugin.ts'
```

### 7.4 启动与 UI 验证流程

```bash
# 启动(记得 build 过一次仓库,见第一章)
pnpm dsh web --patch ./scratch-plugin/cordis.yml
```

验证清单,按序执行:

1. **终端确认**：出现 `[git-log-plugin] 工具注册中`,说明插件加载成功；
2. **打开 web UI**,进入对话界面；
3. **发一条触发消息**,例如:"帮我看下 /home/a/RootStack 这个仓库最近的提交";
4. **观察调用链**:模型应发起对 `git_log_reader` 的调用,参数 `repoPath` 为你给的路径;
5. **核对渲染结果**:UI 中应以文本块形式展示格式化的提交列表(`哈希 | 作者 | 时间 | 标题`);
6. **反向验证**:问一个无关问题,确认模型**不会**滥用这个工具——description 的分流指引("diff 类工具")在此发挥作用。

如果第 4 步模型没调用工具，优先怀疑两件事：你的提问没命中 description 描述的场景，或者 description 写得太含糊。回到 1.2 节的三条军规改措辞。

---

## 8. 工具命名与描述的最佳实践表

| 维度 | 最佳实践 | 反例 |
| --- | --- | --- |
| 命名 | 动词_名词,snake_case:`read_file` | `doIt`、`FileReader2` |
| 粒度 | 一个工具一件事,宁多勿杂 | `do_everything` 万能工具 |
| description 开头 | 动词句:"读取…"、"执行…" | "这是一个用来…" |
| 边界声明 | 明确"不支持/不要用于" | 只说能干什么 |
| 分流指引 | 指出相邻场景用哪个工具 | 让模型自己猜 |
| 参数 description | 写成填空题题干,含格式示例 | 只写一个词 |
| 必填策略 | 真正必需的才 required,其余给默认值 | 全部 required 逼模型编参数 |
| 枚举优先 | 固定选项用 enum,不用自由文本 | 用 string 再在运行时报错 |

---

## 9. 本章小结

- `defineTool` 五字段三分工:name/description/parameters 给模型,output.schema 给程序,output.render 给人,execute 干活;
- description 是 prompt 的一部分,措辞决定调用质量;
- canonical 与 render 两层分离,换来"一份数据、多种展示、独立测试";
- 可预期错误走返回值约定,不走异常,让模型保有决策权;
- 实战完成了 git-log-reader 并在 UI 走通验证闭环。

工具的参数目前还写死在代码里(repoPath 默认逻辑、maxCount 上限)。下一章把它们外置成可配置项:[[deepseek-harness/3实战开发/04-Config与Schemastery|Config 与 Schemastery]]。
