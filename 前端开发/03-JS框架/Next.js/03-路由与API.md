# 路由与 API：动态路由、Route Handlers 与 Server Actions

> 前置：[[前端开发/03-JS框架/Next.js/02-SSR与SSG|SSR 与 SSG]]
> 目标：掌握动态路由与路由组等文件级路由进阶玩法，会用 Route Handler 写后端接口与中间件，理解环境变量边界，学会 Server Actions 新范式。

---

## 1. 动态路由进阶

### 1.1 [id] 文件夹

文件夹名用方括号包裹即成动态段，`app/posts/[id]/page.tsx` 匹配 `/posts/42`：

```tsx
// app/posts/[id]/page.tsx
export default async function PostPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;      // 恒为 string
  return <h1>文章 {id}</h1>;
}
```

多段组合与优先级规则：

```text
app/shop/[category]/page.tsx     → /shop/books
app/shop/[category]/[item]/page.tsx → /shop/books/abc
```

同名冲突时静态段 > 动态段 > 捕获所有段。`[...slug]`（catch-all）匹配剩余全部路径，`[[...slug]]`（optional catch-all）连空路径也吞——文档站 `/docs` 与 `/docs/a/b` 一页通吃的写法。

### 1.2 generateStaticParams：动态段的 SSG

上一章已见单层用法，补充两个工程细节：

```tsx
// 返回空数组 = 不预渲染, 全部走按需 SSR(默认行为)
export async function generateStaticParams() {
  if (process.env.FULL_SSG) {
    const posts = await db.post.findMany();
    return posts.map(p => ({ id: String(p.id) }));
  }
  return [];
}

// 多层嵌套时可为子段递归预渲染
export async function generateStaticParams() {
  return [{ category: 'books', item: 'abc' }, { category: 'games', item: 'xyz' }];
}
```

### 1.3 路由组 (group)

圆括号文件夹**不参与 URL**，纯粹用来组织结构——典型用途是让不同区域拥有不同根布局：

```text
app/
├── (site)/               # 官网区: 带营销页头尾
│   ├── layout.tsx
│   ├── page.tsx          → /
│   └── about/page.tsx    → /about
└── (admin)/              # 后台区: 独立深色布局
    ├── layout.tsx
    └── dashboard/page.tsx → /dashboard
```

两个路由组各自有 layout，URL 里却看不到 (site)/(admin) 字样。约束：同一路径只能落在一个组里，否则构建报错。

### 1.4 拦截/并行路由一句带过

parallel routes（@slot 同级槽位）与 intercepting routes（(.) 拦截同级路径）用于"模态框里打开详情""仪表盘多面板"这类高级布局，初学阶段知道有这两个约定即可，需要时查官方文档。

## 2. Route Handler：内置后端接口

### 2.1 第一个接口

`route.ts` 文件把任意路径变成 HTTP 端点（与 page.tsx 互斥）：

```ts
// app/api/hello/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({ message: 'hello' });
}

export async function POST(request: Request) {
  const body = await request.json();
  return NextResponse.json({ received: body }, { status: 201 });
}
```

导出同名函数即注册对应方法，支持 GET/POST/PUT/PATCH/DELETE/HEAD/OPTIONS 全家。

### 2.2 动态 API 路由

```ts
// app/api/posts/[id]/route.ts
import { NextResponse } from 'next/server';

const DB = new Map<number, { id: number; title: string }>([
  [1, { id: 1, title: '第一篇' }],
]);

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  const post = DB.get(Number(id));
  if (!post) return NextResponse.json({ error: 'not found' }, { status: 404 });
  return NextResponse.json(post);
}

export async function DELETE(
  _req: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  DB.delete(Number(id));
  return new Response(null, { status: 204 });
}
```

### 2.3 与 Spring 接口对照

给 Java 同学的直译表：

| Spring MVC | Route Handler |
|------------|---------------|
| `@RestController` | route.ts 本身 |
| `@GetMapping("/posts/{id}")` | `export async function GET(req, { params })` |
| `@PathVariable` | params.id |
| `@RequestBody` | `await request.json()` |
| `ResponseEntity.status(404)` | NextResponse.json(..., {status:404}) |
| Controller 方法 | 导出的函数本体 |

定位要摆正：Route Handler 的最佳角色是 **BFF（Backend for Frontend）聚合层**——聚合多个下游微服务、隐藏内部协议、注入会话信息后吐给浏览器一个"刚好够用"的响应，正如 [[java/3工程化/15_全栈开发技巧|全栈开发技巧]] 中讨论的前端专属适配层。重业务逻辑仍应住在 Java 服务里；个人项目/小工具则拿它直接当完整后端毫无问题。

### 2.4 读 Cookie/Header 与重定向

```ts
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

export async function GET() {
  const token = (await cookies()).get('session')?.value;
  if (!token) {
    return NextResponse.redirect(new URL('/login', 'http://localhost:3000'));
  }
  return NextResponse.json({ hasSession: true });
}
```

## 3. 中间件 middleware.ts

放在项目根（或 src 下），**每个请求进入路由前**先过它——适合鉴权、A/B、日志、改写：

```ts
// middleware.ts（项目根目录）
import { NextResponse, type NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token')?.value;

  // 保护 /dashboard 及其子路径
  if (request.nextUrl.pathname.startsWith('/dashboard') && !token) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('from', request.nextUrl.pathname);
    return NextResponse.redirect(loginUrl);
  }

  // 给所有响应加自定义头
  const res = NextResponse.next();
  res.headers.set('x-frame-options', 'DENY');
  return res;
}

export const config = {
  matcher: ['/dashboard/:path*', '/login'],   // 只在这些路径触发, 省资源
};
```

要点：

- 中间件运行在边缘环境，**不能使用 Node 全量 API（fs 等）**，只做轻量判断；
- matcher 白名单控制生效范围，避免每个静态资源都过一遍；
- 对比 React Router 的组件式守卫（渲染期拦截）：中间件在**请求期**拦截，未登录用户根本拿不到页面 HTML——语义上更接近 Spring Security 的过滤器链。

## 4. 环境变量与 NEXT_PUBLIC_ 边界

### 4.1 规则

`.env.local`（git 忽略）中定义变量，服务端代码直接 `process.env.X` 读取；**只有 `NEXT_PUBLIC_` 前缀的变量会被内联进客户端 bundle**：

```text
# .env.local
DATABASE_URL=postgres://localhost/dev     # 仅服务端可见
API_SECRET=sk-xxx                         # 仅服务端可见
NEXT_PUBLIC_API_BASE=https://api.ex.com   # 会打进客户端 JS!
```

```ts
// 服务端组件/route.ts/middleware 中
const db = process.env.DATABASE_URL;       // OK

// 'use client' 组件中
fetch(`${process.env.NEXT_PUBLIC_API_BASE}/posts`)   // OK
fetch(`${process.env.API_SECRET}`)                   // undefined + 安全隐患为零
```

安全铁律：**密钥永远不带 NEXT_PUBLIC_ 前缀**。前缀即公开，等于把 .env 提交进了前端源码。这与 Spring 里配置中心区分 public/private 配置、密码走 vault 是同一条纪律。

### 4.2 三套环境文件

| 文件 | 加载时机 |
|------|----------|
| `.env.development` | next dev |
| `.env.production` | next build/start |
| `.env.local` | 总是加载，覆盖上面两者（不入库） |

## 5. Server Actions：表单提交新范式

### 5.1 范式对比

以前提交表单的标准链路：客户端 onChange 收集 → fetch POST → 处理 loading/error → 手动刷新数据。Server Actions 把"客户端调用的函数"直接声明在服务端执行：

```tsx
'use server';

// app/actions.ts —— 函数体只在服务器跑, 客户端只是一个引用桩
export async function createTodo(formData: FormData) {
  const text = String(formData.get('text'));
  await db.todo.create({ data: { text } });
  revalidatePath('/');        // 让列表页缓存失效自动更新
}
```

```tsx
// app/page.tsx —— 服务端组件里的表单直接挂 action
import { createTodo } from './actions';

export default function Page() {
  return (
    <form action={createTodo}>       {/* 不写 onSubmit, 无手写 fetch */}
      <input name="text" required />
      <button type="submit">添加</button>
    </form>
  );
}
```

没有 onSubmit、没有 e.preventDefault、没有 axios、没有 useState 存表单值——HTML 原生 form action 语义 + 渐进增强（JS 未加载也能提交）。这是 App Router 最具代表性的范式转变：**从"事件驱动的 SPA 思维"部分回归"MVC 表单思维"，但保留了 React 组件模型**。Spring 类比：`<form action={createTodo}>` 就是 `<form th:action="@{/todos}" method="post">` 的 React 化身。

### 5.2 在客户端组件中调用 Action

需要交互反馈（pending 态、错误提示）时，useActionState 包装：

```tsx
'use client';

import { useActionState } from 'react';
import { createTodo } from '../actions';

type State = { error?: string };

export default function TodoForm() {
  const [state, formAction, pending] = useActionState<State, FormData>(
    async (_prev, formData) => {
      const text = String(formData.get('text') ?? '').trim();
      if (!text) return { error: '内容不能为空' };
      await save(text);                 // 内部调用服务端 action
      return {};
    },
    {},
  );

  return (
    <form action={formAction}>
      <input name="text" />
      <button disabled={pending}>{pending ? '提交中...' : '添加'}</button>
      {state.error && <p style={{ color: 'red' }}>{state.error}</p>}
    </form>
  );
}
```

三个返回值各司其职：state 上次结果、formAction 塞给 `<form action>`、pending 自动管理提交态。

## 6. 实战：留言板（API Route 版 + Server Action 版）

同一需求两种实现并排对照，体会新旧两代心智。

### 6.1 共享存储与类型

```ts
// lib/messages.ts —— 用内存 Map 模拟数据库(重启即失, 生产换 Prisma/DB)
export type Message = { id: number; author: string; content: string; at: number };

const store = new Map<number, Message>();
let seq = 0;

export function listMessages(): Message[] {
  return [...store.values()].sort((a, b) => b.at - a.at);
}

export function addMessage(author: string, content: string): Message {
  const m: Message = { id: ++seq, author, content, at: Date.now() };
  store.set(m.id, m);
  return m;
}
```

### 6.2 版本 A：Route Handler + 客户端 fetch

```ts
// app/api/messages/route.ts
import { NextResponse } from 'next/server';
import { addMessage, listMessages } from '@/lib/messages';

export async function GET() {
  return NextResponse.json(listMessages());
}

export async function POST(request: Request) {
  const { author, content } = await request.json();
  if (!author?.trim() || !content?.trim()) {
    return NextResponse.json({ error: '姓名和内容必填' }, { status: 400 });
  }
  return NextResponse.json(addMessage(author.trim(), content.trim()), { status: 201 });
}
```

```tsx
'use client';

// app/guestbook-fetch/page.tsx
import { useEffect, useState } from 'react';
import type { Message } from '@/lib/messages';

export default function GuestbookFetchPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [error, setError] = useState('');
  const [pending, setPending] = useState(false);

  useEffect(() => {
    fetch('/api/messages').then(r => r.json()).then(setMessages);
  }, []);

  const submit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    setPending(true);
    setError('');
    try {
      const res = await fetch('/api/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          author: fd.get('author'),
          content: fd.get('content'),
        }),
      });
      if (!res.ok) throw new Error((await res.json()).error);
      setMessages(await fetch('/api/messages').then(r => r.json()));  // 重拉列表
      e.currentTarget.reset();
    } catch (err) {
      setError(err instanceof Error ? err.message : '提交失败');
    } finally {
      setPending(false);
    }
  };

  return (
    <>
      <form onSubmit={submit}>
        <input name="author" placeholder="你的名字" />
        <textarea name="content" placeholder="留言..." />
        <button disabled={pending}>{pending ? '发送中' : '提交'}</button>
        {error && <p style={{ color: 'red' }}>{error}</p>}
      </form>
      <ul>{messages.map(m => <li key={m.id}><b>{m.author}</b>: {m.content}</li>)}</ul>
    </>
  );
}
```

### 6.3 版本 B：Server Action

```tsx
// app/guestbook/actions.ts
'use server';

import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';
import { addMessage } from '@/lib/messages';

export async function postMessage(formData: FormData) {
  const author = String(formData.get('author') ?? '').trim();
  const content = String(formData.get('content') ?? '').trim();
  if (!author || !content) {
    throw new Error('姓名和内容必填');   // 简化演示; 严谨场景用 zod+useActionState 回传错误
  }
  addMessage(author, content);
  revalidatePath('/guestbook');         // 列表缓存失效 → 服务端重渲出新留言
}
```

```tsx
// app/guestbook/page.tsx —— 整个页面都是服务端组件!
import { listMessages } from '@/lib/messages';
import { postMessage } from './actions';

export default async function GuestbookPage() {
  const messages = listMessages();      // 直接读"数据库", 无 fetch
  return (
    <>
      <form action={postMessage}>
        <input name="author" placeholder="你的名字" />
        <textarea name="content" placeholder="留言..." />
        <button type="submit">提交</button>
      </form>
      <ul>
        {messages.map(m => (
          <li key={m.id}><b>{m.author}</b>: {m.content}</li>
        ))}
      </ul>
    </>
  );
}
```

### 6.4 两版对照结论

| 维度 | A: Route Handler | B: Server Action |
|------|------------------|------------------|
| 客户端代码 | fetch/loading/error 状态机一整套 | 零客户端 JS（基础形态） |
| 数据读取 | 再发一次 GET 重拉 | revalidate 后服务端直读 |
| 接口复用 | 可被小程序/App 复用 | 仅限本站 |
| 适用 | 公共 API、BFF 聚合 | 本站表单变更 |

决策一句话：**接口要给别人用选 Route Handler，只是自己页面提交选 Server Action**。

自检清单：

- [ ] [id] 与 [...slug] 语义分清，generateStaticParams 决定 SSG 范围
- [ ] 路由组 (group) 只组织不占 URL
- [ ] Route Handler ≈ @RestController，定位 BFF 聚合层
- [ ] middleware 是请求期拦截，matcher 控制范围，无 Node 全量 API
- [ ] NEXT_PUBLIC_ 前缀 = 进客户端包，密钥绝不加
- [ ] Server Action 替代手写 fetch，revalidate 配合刷新

---

## 小结

| 知识点 | 一句话 |
|--------|--------|
| 动态路由 | 方括号文件夹即参数段 |
| 路由组 | 圆括号共享布局不出现在 URL |
| Route Handler | route.ts 导出函数即接口，BFF 定位 |
| middleware.ts | 请求前置管道，鉴权重定向首选位置 |
| 环境变量 | NEXT_PUBLIC_ 即公开，其余仅服务端 |
| Server Actions | 表单 action 直指服务端函数，渐进增强 |

一切就绪，来一场全栈综合实战：[[前端开发/03-JS框架/Next.js/04-Next.js实战|Next.js 实战]]。
