# React Router：SPA 的导航系统

> 前置：[[前端开发/03-JS框架/React/03-Hooks深入|Hooks 深入]]
> 目标：掌握 react-router v6/v7 数据路由范式、嵌套布局、动态段、守卫与懒加载，完成三页面 SPA。

---

## 1. SPA 路由的本质

单页应用只有一个 HTML，"换页"其实是 JS 监听 URL 变化、切换渲染的组件树，浏览器不发起新文档请求。路由库干两件事：

1. **监听** URL（history API：pushState/replaceState/popstate）；
2. **匹配** URL → 决定渲染哪个组件树。

三大框架路由同构性极高：Vue Router、React Router、Angular Router 都是"路径模式 + 组件映射 + 嵌套出口 + 导航拦截"，学会一个迁移零成本。

react-router 现状：v6 是主流稳定版，v7 在 v6 API 之上平滑演进（数据能力增强），本章以 v6/v7 通用的写法为准。

## 2. 两种创建方式

### 2.1 传统式 BrowserRouter

老项目最常见的写法——组件式声明：

```tsx
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';

export default function App() {
  return (
    <BrowserRouter>
      <nav>
        <Link to="/">首页</Link>
        <Link to="/users">用户</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/users" element={<UserList />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}
```

直观易懂，但数据加载要自己在组件里写 useEffect。

### 2.2 数据路由 createBrowserRouter（推荐）

v6.4 引入的新范式，把"路由配置"从 JSX 搬到**纯对象数组**，并解锁 loader/action 数据能力：

```tsx
const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    errorElement: <ErrorPage />,          // 渲染错误兜底
    children: [
      { index: true, element: <Home /> },
      { path: 'users', element: <UserList /> },
    ],
  },
]);

// 挂载: <RouterProvider router={router} />
```

两者对照：

| 维度 | BrowserRouter | createBrowserRouter |
|------|---------------|---------------------|
| 形态 | JSX 组件声明 | 配置对象数组 |
| 数据加载 | 组件内 useEffect 自理 | 内置 loader（本章从简，详见 Next.js 对比） |
| 错误处理 | 各组件自求多福 | errorElement 一处兜底 |
| 适用 | 老项目/极简场景 | 新项目默认 |

本教程统一使用 `createBrowserRouter`。它与 Spring MVC 的 `@RequestMapping` 注册表心智一致：一张路径→处理器的总表。

## 3. 嵌套路由与 Layout：Outlet

真实应用的页面共享同一个外壳（顶栏+侧边栏+内容区）。父路由的 element 里放 `<Outlet />` 作为子路由的渲染出口：

```tsx
import { Outlet, NavLink } from 'react-router-dom';

function RootLayout() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <NavLink to="/" end>首页</NavLink>          {/* end: 精确匹配才高亮 */}
        <NavLink to="/users">用户</NavLink>
        <NavLink to="/about">关于</NavLink>
      </aside>
      <main className="content">
        <Outlet />                                  {/* 子路由渲染在这里 */}
      </main>
    </div>
  );
}
```

路由表对应嵌套：

```tsx
const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      { index: true, element: <Home /> },           // 索引路由 = 精确匹配 "/"

      { path: 'users', element: <UserList /> },
      { path: 'about', element: <About /> },
    ],
  },
]);
```

要点：

- **索引路由** `index: true`：父路径被精确访问时默认渲染的孩子；
- 子路由 path 不带前导斜杠（相对路径），`path: 'users'` 实际是 `/users`；
- 没有 element 只有 children 的父路由称为布局路由（纯包裹不占 URL）。

Vue 用户对照：与 vue-router 的嵌套 children + `<router-view>` 完全同构；`<NavLink>` 高亮即 `router-link-active`。

## 4. 动态段与 useParams

路径中以冒号声明的参数段：

```tsx
// 路由注册
{ path: 'users/:id', element: <UserDetail /> }

// 组件内取参: 注意返回值永远是字符串！
import { useParams } from 'react-router-dom';

function UserDetail() {
  const { id } = useParams<{ id: string }>();
  const [user, setUser] = useState<User | null>(null);
  useEffect(() => {
    fetch(`/api/users/${id}`)
      .then(r => r.json())
      .then(setUser);
  }, [id]);                                     // id 变化时重新拉取

  if (!user) return <p>加载中...</p>;
  return <h1>{user.name}</h1>;
}
```

三个易错点：

- `useParams` 返回值**全是 string**，做数字比较前先 Number()；
- id 出现在依赖数组里：同一组件在不同参数间复用（`/users/1` → `/users/2`），React 保留组件实例，必须自己响应参数变化；
- 可选段写法 `path: 'files/:file?'`（v6.5+/v7）。

## 5. 编程式导航 useNavigate

链接点击用 `<Link>`，代码逻辑触发的跳转（登录成功后、删除后返回等）用 `useNavigate`：

```tsx
import { useNavigate } from 'react-router-dom';

function LoginPage() {
  const navigate = useNavigate();
  const handleLogin = async () => {
    const ok = await doLogin();
    if (ok) navigate('/dashboard', { replace: true });   // 登录后 replace，防后退回登录页
  };
  return <button onClick={handleLogin}>登录</button>;
}
```

| 场景 | 写法 |
|------|------|
| 正常跳转 | `navigate('/path')` |
| 替换当前记录（登录后/重定向） | `navigate('/path', { replace: true })` |
| 后退/前进 | `navigate(-1)` / `navigate(1)`（数字=history.go） |
| 跳转并传 state（刷新即丢） | `navigate('/detail', { state: { from: 'list' } })`，目标页用 `useLocation().state` 读取 |

## 6. searchParams：URL 查询参数读写

分页、筛选这类应可分享、可收藏、可后退的状态，标准存放位置是查询串。useSearchParams 提供类似 useState 的读写体验：

```tsx
import { useSearchParams } from 'react-router-dom';

function UserList() {
  const [searchParams, setSearchParams] = useSearchParams();
  const page = Number(searchParams.get('page')) || 1;
  const keyword = searchParams.get('kw') ?? '';

  return (
    <>
      <input
        value={keyword}
        onChange={e => setSearchParams({ kw: e.target.value, page: '1' })}
        placeholder="搜索"
      />
      <p>第 {page} 页</p>
      {/* 翻页: setSearchParams(prev => { prev.set('page', ...); return prev; }) */}
      <button onClick={() =>
        setSearchParams(prev => {
          prev.set('page', String(Math.max(1, page - 1)));
          return prev;
        })
      }>上一页</button>
    </>
  );
}
```

设计意义：筛选状态进 URL 之后，复制链接给同事看到的就是同样的列表状态——URL 即应用状态的可分享快照。这也是 [[前端开发/03-JS框架/Next.js/01-Next.js基础|Next.js]] 中 searchParams 成为服务端可用数据的伏笔。

## 7. 导航守卫：ProtectedRoute 包装模式

React Router 没有内置全局守卫钩子（对比 Vue Router 的 beforeEach / Angular 的 canActivate），官方推荐的思路是**包装组件**：在渲染层面拦截。

```tsx
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from './auth';     // 自定义 Hook：读 token/登录态（下一章实现）

// 方式一：包一层组件
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { token } = useAuth();
  const location = useLocation();

  if (!token) {
    // 未登录 → 重定向登录页，并记住来源以便登录后跳回
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  return children;
}

// 方式二：配合 Outlet 做"布局级"守卫
function AuthLayout() {
  const { token } = useAuth();
  return token ? <Outlet /> : <Navigate to="/login" replace />;
}
```

```tsx
{
  path: '/',
  element: <AuthLayout />,            // 整个子树都受保护
  children: [
    { path: 'dashboard', element: <Dashboard /> },
    { path: 'settings', element: <Settings /> },
  ],
},
```

对照表：

| 框架 | 拦截时机 | 写法 |
|------|----------|------|
| Vue Router | 全局 beforeEach 钩子 | `router.beforeEach((to) => ...)` |
| Angular | 路由激活接口 | `canActivate: [authGuard]` |
| React Router | 无全局钩子 | 受保护包装组件 / 布局守卫 |

React 社区刻意保持"一切皆组件"的一致性：守卫就是条件渲染。代价是拦截发生在渲染期而非导航期，语义上等价，习惯即可。

## 8. 懒加载：React.lazy + Suspense

路由级代码分割是性能优化的第一刀：首屏只打包当前页代码，其余按需加载。

```tsx
import { lazy, Suspense } from 'react';

// 不再 import UserList，改为惰性引入 → 构建时拆成独立 chunk
const UserList = lazy(() => import('./pages/UserList'));
const About = lazy(() => import('./pages/About'));

<Suspense fallback={<p>页面加载中...</p>}>
  <Routes>
    <Route path="/users" element={<UserList />} />
    <Route path="/about" element={<About />} />
  </Routes>
</Suspense>
```

要点：

- `lazy(() => import('./x'))` 接收动态 import，返回可懒加载组件，加载期间 Suspense 显示 fallback，必须成对出现；
- 只对**路由级/重组件**使用，小组件拆出去反而多一次网络往返；
- 数据路由下更优雅：直接在路由配置里用 `lazy: () => import(...)` 字段，loader 与组件一起懒加载。

## 9. 实战：三页面 SPA（首页/用户列表/用户详情)

### 9.1 项目结构

```text
src/
├── main.tsx              # 创建 router 并挂载
├── api.ts                # mock 数据源
├── layouts/RootLayout.tsx
├── pages/
│   ├── Home.tsx
│   ├── UserList.tsx
│   ├── UserDetail.tsx
│   └── NotFound.tsx
```

api.ts（先用本地 mock，后续章节替换真请求）：

```ts
export type User = { id: number; name: string; email: string };

const USERS: User[] = [
  { id: 1, name: 'Alice', email: 'alice@example.com' },
  { id: 2, name: 'Bob', email: 'bob@example.com' },
  { id: 3, name: 'Carol', email: 'carol@example.com' },
];

export function fetchUsers(): Promise<User[]> {
  return new Promise(resolve => setTimeout(() => resolve(USERS), 300));
}

export function fetchUser(id: number): Promise<User | undefined> {
  return new Promise(resolve =>
    setTimeout(() => resolve(USERS.find(u => u.id === id)), 300));
}
```

### 9.2 main.tsx 路由装配

```tsx
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import RootLayout from './layouts/RootLayout';
import Home from './pages/Home';
import UserList from './pages/UserList';
import UserDetail from './pages/UserDetail';
import NotFound from './pages/NotFound';

const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      { index: true, element: <Home /> },
      { path: 'users', element: <UserList /> },
      { path: 'users/:id', element: <UserDetail /> },
      { path: '*', element: <NotFound /> },
    ],
  },
]);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
);
```

### 9.3 RootLayout.tsx

```tsx
import { NavLink, Outlet } from 'react-router-dom';

export default function RootLayout() {
  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <nav style={{ width: 160, borderRight: '1px solid #eee', padding: 16 }}>
        <p><NavLink to="/" end>首页</NavLink></p>
        <p><NavLink to="/users">用户列表</NavLink></p>
      </nav>
      <main style={{ flex: 1, padding: 24 }}>
        <Outlet />
      </main>
    </div>
  );
}
```

### 9.4 三个页面

Home 与 NotFound 都是几行的小组件，合并展示：

```tsx
// pages/Home.tsx
import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div>
      <h1>欢迎来到用户中心</h1>
      <p>去逛逛<Link to="/users">用户列表</Link>吧。</p>
    </div>
  );
}

// pages/NotFound.tsx
import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <div>
      <h1>404</h1>
      <Link to="/">回到首页</Link>
    </div>
  );
}
```

UserList.tsx（列表 + 竞态防护）：

```tsx
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchUsers, type User } from '../api';

export default function UserList() {
  const [users, setUsers] = useState<User[] | null>(null);

  useEffect(() => {
    let ignore = false;
    fetchUsers().then(data => { if (!ignore) setUsers(data); });
    return () => { ignore = true; };
  }, []);

  if (!users) return <p>加载中...</p>;

  return (
    <ul>
      {users.map(u => (
        <li key={u.id}>
          {/* 详情页跳转：模板字符串拼动态路径 */}
          <Link to={`/users/${u.id}`}>{u.name}</Link> — {u.email}
        </li>
      ))}
    </ul>
  );
}
```

UserDetail.tsx（动态段 + 参数变化重拉）：

```tsx
import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchUser, type User } from '../api';

export default function UserDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    let ignore = false;
    setUser(null);
    fetchUser(Number(id)).then(data => { if (!ignore) setUser(data ?? null); });
    return () => { ignore = true; };
  }, [id]);

  if (!user) return <p>加载中...</p>;

  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
      <button onClick={() => navigate('/users')}>返回列表</button>
    </div>
  );
}
```

运行 `npm run dev`，验证清单：

- [ ] 侧边栏切换三页，外壳不闪（只有 Outlet 区域重渲）
- [ ] 直接刷新 `/users/2` 能正确显示（dev server 已配 history fallback）
- [ ] 手输 `/xxx` 落到 404
- [ ] 列表→详情→返回，列表滚动位置与状态保留（组件未被销毁的场景自行体会）

自检清单：

- [ ] createBrowserRouter 配置式路由优于 JSX 声明式的点说得出两条
- [ ] Outlet/索引路由/嵌套 path 相对规则清楚
- [ ] useParams 返回 string，id 进依赖数组
- [ ] replace 的适用时机（登录后）
- [ ] 守卫 = 包装组件条件渲染，能写出 AuthLayout
- [ ] lazy+Suspense 成对使用，只拆路由级大块

---

## 小结

| 知识点 | 一句话 |
|--------|--------|
| 数据路由 | createBrowserRouter + RouterProvider，配置即路由 |
| 嵌套 | 父 element 放 Outlet，index 路由是默认孩子 |
| 动态段 | :id 声明，useParams 取出恒为 string |
| 编程导航 | useNavigate，replace 防"后退到登录页" |
| searchParams | 分页筛选拉进 URL，可分享可后退 |
| 守卫 | 无全局钩子，ProtectedRoute/AuthLayout 条件渲染 |
| 懒加载 | lazy+Suspense，只拆路由级 |

单页内的状态跨页面共享怎么办？见 [[前端开发/03-JS框架/React/05-状态管理|状态管理]]。
