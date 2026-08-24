# 组件与 JSX：组合的艺术

> 前置：[[前端开发/03-JS框架/React/01-React基础|React 基础]]
> 目标：掌握 children 组合模式、TS 类型化 props、样式方案选型、ref 与 Portal，搭出可复用基础组件库雏形。

---

## 1. 组合优于继承：children prop

### 1.1 React 没有"继承组件"这回事

面向对象思维的第一反应是抽基类：`BaseModal extends BasePanel`。React 明确反对这条路——**组件之间用组合（composition）而非继承（inheritance）复用代码**。逻辑复用走自定义 Hook（见 [[前端开发/03-JS框架/React/03-Hooks深入|Hooks 深入]]），结构复用走 children。

### 1.2 children：标签包裹的内容

写在组件开闭标签之间的内容，会作为 `props.children` 传进来：

```tsx
type CardProps = {
  title: string;
  children: React.ReactNode;
};

function Card({ title, children }: CardProps) {
  return (
    <div className="card">
      <header className="card-header">{title}</header>
      <div className="card-body">{children}</div>
    </div>
  );
}

// 使用方决定"里面放什么"
<Card title="用户信息">
  <UserCard name="Alice" />
  <button>编辑</button>
</Card>
```

Card 完全不知道也不关心 body 里是什么——它只提供外壳和插槽。这就是 React 版的"开闭原则"：对扩展开放（任意 children），对修改关闭（Card 自身稳定）。

Spring 类比：children 像 Spring 的模板方法反转——父组件定义骨架流程，具体内容由调用方注入，正如 `JdbcTemplate` 把 SQL 的执行骨架固定、把 SQL 本身交给你。

### 1.3 多插槽：children 之外再传组件 props

一个插槽不够用时，直接用 props 传 JSX：

```tsx
type LayoutProps = {
  header: React.ReactNode;
  sidebar: React.ReactNode;
  content: React.ReactNode;
};

function DashboardLayout({ header, sidebar, content }: LayoutProps) {
  return (
    <div className="dashboard">
      <header>{header}</header>
      <aside>{sidebar}</aside>
      <main>{content}</main>
    </div>
  );
}

<DashboardLayout
  header={<TopBar user={user} />}
  sidebar={<NavMenu items={menus} />}
  content={<Outlet />}
/>
```

这种"把组件当参数传"的写法在 Vue 里对应 slot，但 React 更彻底：JSX 就是一等公民的值。

## 2. props 类型校验：TS 是标准姿势

历史上有 PropTypes 运行时校验库，如今 **React + TypeScript 项目一律用 interface/type 声明 props**，编译期就能抓住错误：

```tsx
import { useState } from 'react';

// 基础类型 + 可选 + 默认值
type ButtonProps = {
  variant?: 'primary' | 'secondary' | 'danger';  // 字面量联合：比 enum 更轻
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
};

export function Button({
  variant = 'primary',
  size = 'md',
  disabled = false,
  onClick,
  children,
}: ButtonProps) {
  return (
    <button
      className={`btn btn-${variant} btn-${size}`}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
```

常用类型速查：

| 场景 | 写法 |
|------|------|
| 任意可渲染内容 | `React.ReactNode` |
| 组件/元素引用 | `React.ReactElement` 或 `React.JSX.Element` |
| 事件处理器 | `React.ChangeEvent<HTMLInputElement>` 等 |
| 子组件函数 | `(data: T) => React.ReactNode` |
| 扩展原生属性 | `React.ComponentProps<'button'>` |

最后一招很实用：想让组件透传所有原生 button 属性（title、aria-* 等）时不必手抄一遍：

```tsx
type SuperButtonProps = React.ComponentProps<'button'> & {
  loading?: boolean;
};

function SuperButton({ loading, ...rest }: SuperButtonProps) {
  return <button {...rest} disabled={rest.disabled || loading} />;
}
```

## 3. 样式方案四选一

| 方案 | 写法 | 隔离性 | 动态样式 | 适用 |
|------|------|--------|----------|------|
| 普通 CSS | 全局 .css 文件 | 无，类名冲突靠约定 | 类名拼接 | 小项目/原型 |
| CSS Modules | `*.module.css` | 编译期哈希类名，天然隔离 | 类名条件拼接 | 中型项目默认选择 |
| inline style | style 对象 | 最强 | JS 表达式直出 | 动态量（宽度/颜色） |
| Tailwind | class 工具类原子 | 类名即样式 | 条件表达式拼类 | 快速迭代+设计系统约束 |

### 3.1 四种写法对照

```tsx
// 1. 普通 CSS：import './App.css' 后直接用 className="list"
// 风险：全局作用域，两个组件都定义 .list 会互相覆盖

// 2. CSS Modules：文件必须叫 xxx.module.css
import styles from './UserList.module.css';
<li className={styles.item} />

// 3. inline style
<div style={{ maxWidth: 600, backgroundColor: active ? '#e6f7ff' : '#fff' }} />

// 4. Tailwind（Vite 项目需先安装配置）
<button className="rounded-lg bg-blue-500 px-4 py-2 text-white hover:bg-blue-600 disabled:opacity-50" />
```

### 3.2 选型建议

- 入门学习期用 **CSS Modules**，零心智负担且不踩全局冲突；
- **动态数值**（进度条宽度、图表颜色）inline style 最顺手；
- 团队协作、组件库风格统一推荐 **Tailwind**，配合 clsx 管理条件类名：

```tsx
import clsx from 'clsx';
<span className={clsx('tag', active && 'tag-active', size === 'lg' && 'tag-lg')} />
```

本教程后续示例统一使用 CSS Modules + 关键处 inline style 的混合策略。

## 4. 受控 vs 非受控表单

上一章讲了受控组件（value 由 state 驱动），另一条路线是**非受控**：DOM 自己管自己的值，需要时用 ref 读一次：

```tsx
import { useRef } from 'react';

function SearchForm() {
  const keywordRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log(keywordRef.current?.value);   // 只在提交时读取
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* defaultValue 只设定初始值，之后 DOM 接管 */}
      <input ref={keywordRef} defaultValue="" placeholder="搜索..." />
      <button>搜索</button>
    </form>
  );
}
```

决策表：

| 维度 | 受控 | 非受控 |
|------|------|--------|
| 数据源 | React state | DOM 内部状态 |
| 实时校验/联动 | 天然支持 | 要监听原生事件，别扭 |
| 提交时取值 | 直接读 state | 读 ref |
| 代码量 | 每字段两行绑定 | 几乎零绑定 |
| 典型场景 | 登录注册、搜索联动 | 单文件上传 input、简单一次性表单 |

经验法则：**默认受控；只有"提交才关心值"或接第三方非 React 库时用非受控**。复杂表单想省样板代码，上 react-hook-form（底层就是非受控 + 精准订阅）。

## 5. refs 操作 DOM

### 5.1 useRef 三行入门

```tsx
const inputRef = useRef<HTMLInputElement>(null);

<input ref={inputRef} />
inputRef.current?.focus();     // current 就是真实 DOM 节点
```

`useRef(null)` 返回 `{ current: null }` 的可变盒子，把 JSX 的 ref 属性挂上去后，React 会在挂载时把 DOM 节点塞进 `.current`。

### 5.2 何时才需要：聚焦/滚动/测量

React 的哲学是声明式——绝大多数交互不该碰 DOM。ref 的正当用途清单：

1. **聚焦/失焦**：弹窗打开自动聚焦第一个输入框；
2. **滚动定位**：聊天窗口滚到底部、锚点跳转；
3. **测量**：拿到元素宽高做浮层定位（配合 getBoundingClientRect）;
4. **对接第三方命令式库**：地图、编辑器、播放器的初始化容器。

```tsx
function ChatWindow() {
  const bottomRef = useRef<HTMLDivElement>(null);
  const [msgs, setMsgs] = useState<string[]>([]);

  // 收到新消息后滚动到底部——这是 state 无法表达的操作
  const receive = (m: string) => {
    setMsgs(prev => [...prev, m]);
    requestAnimationFrame(() => bottomRef.current?.scrollIntoView({ behavior: 'smooth' }));
  };

  return (
    <div>
      {msgs.map((m, i) => <p key={i}>{m}</p>)}
      <div ref={bottomRef} />
      <button onClick={() => receive(`msg ${Date.now()}`)}>模拟新消息</button>
    </div>
  );
}
```

反例警示：不要用 ref 改 DOM 文案/样式来"绕过重渲"——那等于回到 jQuery，state 与视图从此不同步，bug 温床。判断标准：**这个操作能用 state 表达吗？能就别用 ref。**

### 5.3 forwardRef 转发一提

ref 不是普通 prop，封装组件想把内部 input 的 ref 暴露给外部要用 `React.forwardRef` 包一层（React 19 起可直接当 prop 传递），老代码里见到认识即可。

## 6. Portal：渲染到组件树之外

### 6.1 问题：模态框被父级样式劫持

模态框如果渲染在组件树原位置，会被任何设置了 `overflow: hidden`、`transform`、`z-index` 层叠上下文的祖先影响，导致遮罩盖不全、弹层错位。

### 6.2 createPortal

Portal 让组件**逻辑上仍在原树中**（context、事件冒泡照常），但 **DOM 物理上挂在指定节点下**：

```tsx
import { createPortal } from 'react-dom';

type ModalProps = {
  open: boolean;
  onClose: () => void;
  children: React.ReactNode;
};

export default function Modal({ open, onClose, children }: ModalProps) {
  if (!open) return null;
  return createPortal(
    <div className="modal-mask" onClick={onClose}>
      <div className="modal-box" onClick={e => e.stopPropagation()}>
        {children}
      </div>
    </div>,
    document.body,          // 挂到 body，逃逸一切祖先样式
  );
}
```

注意细节：点击遮罩关闭，但 `stopPropagation` 挡住内容区冒泡——虽然 DOM 在 body 下，**合成事件的冒泡仍沿 React 树进行**，这正是 Portal "形离神不离"的体现。

Vue 用户对照：与 Vue3 的 Teleport `<Teleport to="body">` 一模一样，连名字都神似。

## 7. 错误边界概念

任何一个子组件运行时报错，默认会把整棵 React 树卸载成白屏。**错误边界（Error Boundary）**是捕获子树渲染错误的隔离舱。

坏消息：class 组件时代它只能用 class 写（`static getDerivedStateFromError` + `componentDidCatch`）。好消息：实际项目几乎不手写，直接用现成的 `react-error-boundary` 包：

```tsx
import { ErrorBoundary } from 'react-error-boundary';

<ErrorBoundary
  fallback={<div>该模块崩溃了，<button onClick={() => location.reload()}>刷新</button></div>}
  onError={(err) => console.error('上报监控', err)}
>
  <RiskyChartWidget />
</ErrorBoundary>
```

要点：

- 只捕获**渲染期/生命周期**错误，事件回调、异步任务里的错误捕获不到（那些本来就该 try/catch）；
- 边界按需布置：每个独立功能模块包一层，局部崩不影响全局；
- Next.js 有内置约定式替代品 `error.tsx`（见 [[前端开发/03-JS框架/Next.js/01-Next.js基础|Next.js 基础]]）。

## 8. 实战：可复用基础组件库雏形

目标：搭出 Button / Input / Card 三个组件 + 一个演示页，体会"props 设计即 API 设计"。

### 8.1 目录结构

```text
src/
├── components/
│   ├── Button.tsx
│   ├── Button.module.css
│   ├── Input.tsx
│   ├── Card.tsx
│   └── index.ts        # 统一出口
├── App.tsx
└── main.tsx
```

### 8.2 Button.tsx

```tsx
import type { ReactNode } from 'react';
import styles from './Button.module.css';

type Props = {
  variant?: 'primary' | 'ghost' | 'danger';
  block?: boolean;
  onClick?: () => void;
  children: ReactNode;
};

export function Button({ variant = 'primary', block, onClick, children }: Props) {
  const cls = [styles.btn, styles[variant], block ? styles.block : ''].join(' ');
  return (
    <button className={cls} onClick={onClick}>{children}</button>
  );
}
```

Button.module.css：

```css
.btn {
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
}
.primary { background: #2563eb; color: #fff; }
.ghost   { background: transparent; color: #2563eb; }
.danger  { background: #dc2626; color: #fff; }
.block   { display: block; width: 100%; margin-top: 8px; }
```

### 8.3 Input.tsx（受控）

```tsx
type Props = {
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  error?: string;
};

export function Input({ value, onChange, placeholder, error }: Props) {
  return (
    <div>
      <input
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        style={{ borderColor: error ? '#dc2626' : undefined }}
      />
      {error && <p style={{ color: '#dc2626', fontSize: 12 }}>{error}</p>}
    </div>
  );
}
```

注意 onChange 的签名收敛为 `(v: string) => void`——组件库把事件对象消化掉，只暴露业务关心的值，调用方体验更干净。

### 8.4 Card.tsx（children 组合）

```tsx
import type { ReactNode } from 'react';

type Props = {
  title?: string;
  extra?: ReactNode;
  footer?: ReactNode;
  children: ReactNode;
};

export function Card({ title, extra, footer, children }: Props) {
  return (
    <section style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: 16 }}>
      {(title || extra) && (
        <header style={{ display: 'flex', justifyContent: 'space-between' }}>
          <h3>{title}</h3>
          {extra}
        </header>
      )}
      <div>{children}</div>
      {footer && <footer style={{ borderTop: '1px solid #eee', marginTop: 12 }}>{footer}</footer>}
    </section>
  );
}
```

### 8.5 统一出口与演示页

components/index.ts：

```ts
export { Button } from './Button';
export { Input } from './Input';
export { Card } from './Card';
```

App.tsx：

```tsx
import { useState } from 'react';
import { Button, Input, Card } from './components';
import Modal from './Modal';

export default function App() {
  const [name, setName] = useState('');
  const err = name.length > 0 && name.length < 3 ? '至少 3 个字符' : undefined;

  return (
    <main style={{ maxWidth: 480, margin: '40px auto' }}>
      <Card
        title="创建账号"
        extra={<Button variant="ghost" onClick={() => setName('')}>清空</Button>}
        footer={<Button block disabled={!name || !!err}>提交</Button>}
      >
        <Input value={name} onChange={setName} placeholder="用户名" error={err} />
        {name && <p>你好，{name}</p>}
      </Card>
      <ModalDemo />
    </main>
  );
}

// Portal 实际演练：弹窗挂 body，逻辑仍在组件树内
function ModalDemo() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <Button variant="danger" onClick={() => setOpen(true)}>打开弹窗</Button>
      <Modal open={open} onClose={() => setOpen(false)}>
        <h3>确认删除吗？</h3>
        <Button variant="ghost" onClick={() => setOpen(false)}>取消</Button>
        <Button variant="danger" onClick={() => setOpen(false)}>删除</Button>
      </Modal>
    </>
  );
}
```

自检清单：

- [ ] 能解释为什么 React 不用继承复用组件
- [ ] children / 多插槽各自解决什么问题
- [ ] 新项目 props 校验用 TS 而不是 PropTypes
- [ ] 四种样式方案知道取舍，CSS Modules 是默认项
- [ ] ref 只用于聚焦/滚动/测量等命令式操作
- [ ] Modal 用 Portal 挂 body，且理解事件仍沿 React 树冒泡

---

## 小结

| 知识点 | 一句话 |
|--------|--------|
| 组合模式 | children 即插槽，结构复用靠组合不靠继承 |
| props 类型 | TS interface 是标准姿势，ComponentProps 透传原生属性 |
| 样式 | CSS Modules 隔离默认之选，动态数值用 inline |
| 受控 vs 非受控 | 默认受控，提交才取值的简单表单可用非受控 |
| useRef | current 盒子装 DOM，聚焦/滚动/测量三件事 |
| Portal | DOM 出走、逻辑留守，模态框标配 |
| Error Boundary | 子树错误隔离舱，用现成库不手写 |

下一章深入 Hooks 的规则与时序坑：[[前端开发/03-JS框架/React/03-Hooks深入|Hooks 深入]]。
