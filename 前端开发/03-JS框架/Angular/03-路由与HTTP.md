# 路由与HTTP：守卫、拦截器与响应式表单

> 前置：[[前端开发/03-JS框架/Angular/02-组件与服务|组件与服务]]
> 目标：掌握 routes 数组配置与懒加载，写出现代函数式守卫三件套，用 HttpInterceptor 实现 token 注入与统一错误处理，分清响应式表单与模板驱动表单。

---

## 1. 路由配置：routes 数组

### 1.1 基本装配

Angular 路由与 vue-router/react-router 高度同构：路径→组件映射表 + `<router-outlet>` 出口 + routerLink 链接。

```ts
// app.routes.ts
import { Routes } from '@angular/router';
import { HomeComponent } from './pages/home.component';
import { UserListComponent } from './pages/user-list.component';

export const routes: Routes = [
  { path: '', component: HomeComponent, title: '首页' },
  { path: 'users', component: UserListComponent, title: '用户列表' },
  { path: '**', redirectTo: '' },        // 通配兜底(必须放最后)
];

// main.ts: bootstrapApplication(AppComponent, { providers: [provideRouter(routes)] });
```

```html
<!-- 根组件模板 -->
<nav>
  <a routerLink="/" routerLinkActive="active">首页</a>
  <a routerLink="/users" routerLinkActive="active">用户</a>
</nav>
<router-outlet />   <!-- 匹配的组件渲染在此 -->
```

三大框架对照表：

| 概念 | Angular | Vue Router | React Router |
|------|---------|------------|--------------|
| 配置 | routes 数组 | createRouter({routes}) | createBrowserRouter |
| 出口 | router-outlet | router-view | Outlet |
| 链接 | routerLink + active 类 | router-link | NavLink |
| 取参 | route.paramMap / withParamMapping | useRoute().params | useParams |

### 1.2 动态段与读取

```ts
{ path: 'users/:id', component: UserDetailComponent },
```

现代推荐用 `withComponentInputBinding()` 把参数直接绑成组件 input：

```ts
provideRouter(routes, withComponentInputBinding())

@Component({ template: '<h2>用户 {{ id }}</h2>' })
export class UserDetailComponent {
  id = input.required<string>();     // 路由参数自动注入, 恒为 string
}

// 传统等价物(老项目常见): inject(ActivatedRoute).paramMap.subscribe(...)
```

注意 paramMap 是 Observable 且参数变化会再推送——同一组件在不同 id 间复用时自动响应，这与 React 里"id 进依赖数组"是同一个问题域。

### 1.3 子路由与懒加载

嵌套即 children，出口在父组件里：

```ts
{
  path: 'admin',
  component: AdminLayoutComponent,
  children: [
    { path: 'dashboard', component: DashboardComponent },
    { path: 'settings', component: SettingsComponent },
    { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  ],
},

// 懒加载两式(构建产物按路由切块):
// 组件级: { path: 'lazy', loadComponent: () => import('./lazy.component').then(m => m.LazyComponent) }
// 子路由级: { path: 'admin', loadChildren: () => import('./admin/admin.routes').then(m => m.ADMIN_ROUTES) }
```

对照 React 的 lazy+Suspense、Vue 的 () => import()——目的相同：首包瘦身。

## 2. 守卫三件套

Angular 守卫是**导航期**拦截（对比 React Router 渲染期包装组件），语义最接近后端过滤器。现代写法是普通函数返回 boolean 或 UrlTree。

### 2.1 canActivate：登录守卫

```ts
// guards/auth.guard.ts
import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);      // 函数内注入, 无类构造器
  const router = inject(Router);

  if (authService.isLoggedIn()) return true;
  return router.createUrlTree(['/login'], {
    queryParams: { from: state.url },           // 记住来源, 登录后跳回
  });
};

// 应用到路由:
// { path: 'dashboard', component: ..., canActivate: [authGuard] }
```

### 2.2 canDeactivate：未保存提示

离开页面前询问"改动还没保存，确定离开？"：

```ts
// guards/unsaved.guard.ts
export interface CanComponentLeave {
  canLeave: () => boolean;
}

export const unsavedGuard: CanDeactivateFn<CanComponentLeave> = component =>
  component.canLeave?.() ?? true;

// 表单组件实现接口
export class EditProfileComponent implements CanComponentLeave {
  dirty = false;
  canLeave() {
    if (!this.dirty) return true;
    return confirm('有未保存的修改，确定离开？');
  }
}

// 路由注册: { path: 'edit-profile', component: ..., canDeactivate: [unsavedGuard] }
```

### 2.3 resolve：预取数据

导航完成**之前**把数据取好，组件激活时数据已就位（对应 Next.js loader 思想）：

```ts
// guards/user.resolver.ts
export const userResolver: ResolveFn<User> = route => {
  const id = Number(route.paramMap.get('id'));
  return inject(UserService).getUser(id);
};

{ path: 'users/:id', component: UserDetailComponent, resolve: { user: userResolver } },
// 组件里直接 input.required<User>() 拿数据, 无 loading 态代码
```

三件对照表：

| 守卫 | 时机 | 典型场景 | 其他框架对应 |
|------|------|----------|--------------|
| canActivate | 进入前 | 未登录踢回登录 | Vue beforeEach / React ProtectedRoute |
| canDeactivate | 离开前 | 未保存确认 | Vue beforeRouteLeave |
| resolve | 激活前 | 预取数据 | React Router loader |

## 3. HttpClient 与拦截器

### 3.1 拦截器：token 注入 + 统一错误

拦截器是 HttpClient 的请求管道中间件——与 axios interceptors、Spring HandlerInterceptor 三方同构：

```ts
// interceptors/auth.interceptor.ts（现代 functional 写法）
import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);

  // 1) 克隆请求并附加 token(HttpRequest 不可变, 必须 clone)
  const authReq = req.clone({
    setHeaders: { Authorization: `Bearer ${auth.token}` },
  });

  // 2) 放行到下一个拦截器, 并统一处理错误
  return next(authReq).pipe(
    catchError((err) => {
      if (err.status === 401) {
        auth.logout();                          // 清登录态
        return throwError(() => new Error('登录已过期'));
      }
      return throwError(() => err);
    }),
  );
};
```

注册（standalone 方式）：`provideHttpClient(withInterceptors([authInterceptor]))` 加入 main.ts 的 providers 即可。

对照 axios 版本（[[前端开发/03-JS框架/React/06-React实战|React 实战]] 中写过）：

| 关注点 | axios | Angular interceptor |
|--------|-------|---------------------|
| 加头 | request.use(config => ...) | req.clone({setHeaders}) |
| 错误钩 | response.use 第二参 | catchError 管道 |
| 不可变性 | config 直接改 | HttpRequest 必须 clone |

错误提示的全局化：在 catchError 里调一个 NotificationService 弹 toast，所有组件的 HTTP 错误处理就归一了——这就是拦截器作为横切关注点的价值，AOP 思想再次现身。

### 3.2 类型化的 GET/POST

```ts
@Injectable({ providedIn: 'root' })
export class UserService {
  private http = inject(HttpClient);

  getUsers(page = 0) {
    return this.http.get<User[]>('/api/users', { params: { page, size: 10 } });  // 查询串自动序列化
  }

  createUser(dto: { name: string; email: string }) {
    return this.http.post<User>('/api/users', dto);   // body 自动 JSON
  }
}
```

泛型标注让响应全程带类型；订阅时 next/error 分支各司其职。竞态防护方面，切换路由时配合 takeUntilDestroyed 或 switchMap 自动取消旧订阅（细节进阶自查）。

## 4. 响应式表单 vs 模板驱动表单

Angular 内置两套表单方案，选型先讲清楚：

| 维度 | 响应式 ReactiveForms | 模板驱动 Template-driven |
|------|---------------------|--------------------------|
| 真相源 | 组件里的 FormGroup 类 | 模板里的 ngModel |
| 校验定义 | TS 代码显式声明 | HTML 属性（required 等）|
| 适用 | 复杂表单/动态字段/单元测试 | 简单两三个字段的表单 |
| 心智 | 代码优先（像后端校验） | 模板优先（像原生） |

复杂度超过"登录框"就用响应式——它是企业项目的默认答案，也是 Java 同学最有安全感的写法：校验规则集中在代码里可测试，正如 Bean Validation 注解背后的约束体系。

### 4.1 ReactiveFormsModule 快速上手

```ts
import { Component, inject } from '@angular/core';
import { FormBuilder, Validators, ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'app-signup',
  standalone: true,
  imports: [ReactiveFormsModule],
  template: `
    <form [formGroup]="form" (ngSubmit)="submit()">
      <input formControlName="username" placeholder="用户名" />
      @if (form.controls.username.invalid && form.controls.username.touched) {
        <p class="err">用户名至少 3 个字符</p>
      }
      <input formControlName="email" type="email" placeholder="邮箱" />
      @if (form.controls.email.errors?.['email']) {
        <p class="err">邮箱格式不正确</p>
      }
      <button [disabled]="form.invalid">提交</button>
    </form>
  `,
})
export class SignupComponent {
  private fb = inject(FormBuilder);

  form = this.fb.nonNullable.group({
    username: ['', [Validators.required, Validators.minLength(3)]],
    email: ['', [Validators.required, Validators.email]],
    role: ['user'],
  });

  submit() {
    console.log(this.form.getRawValue());   // {username, email, role} 强类型
  }
}
```

要点：

- **FormBuilder.group 声明结构**：字段名 → [初始值， 校验器数组]；
- **状态四件套**：valid/invalid、touched（碰过没）、dirty（改过没）、errors（错误明细）；
- **getRawValue() 返回强类型值对象**——表单数据从此不是散落的 DOM 读值；
- 动态增删字段用 FormArray；跨字段联动用 valueChanges 流（RxJS 再立功）。

对照 Spring MVC 后端：前端 Validators ≈ Bean Validation 注解，form.invalid 禁用按钮 ≈ 服务端 BindingResult 拒绝非法提交——只是把校验前移到了浏览器，两端契约仍需后端兜底。

## 5. 实战：登录 + 守卫 + CRUD 页面接 mock API

### 5.1 结构

```text
src/app/
├── auth.service.ts          # 登录态(signal + localStorage)
├── auth.guard.ts            # 登录守卫
├── pages/login.component.ts
├── pages/todo-crud.component.ts
└── app.routes.ts
```

### 5.2 AuthService

```ts
import { Injectable, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class AuthService {
  readonly token = signal<string | null>(localStorage.getItem('token'));

  isLoggedIn() { return this.token() !== null; }

  async login(username: string, password: string): Promise<void> {
    // mock: 用户名非空即成功; 真实场景换成 http.post('/api/login')
    await new Promise(r => setTimeout(r, 300));
    if (!username.trim()) throw new Error('用户名不能为空');
    const t = btoa(`${username}:${Date.now()}`);
    localStorage.setItem('token', t);
    this.token.set(t);
  }

  logout(reason?: string) {
    localStorage.removeItem('token');
    this.token.set(null);
    if (reason) alert(reason);
  }
}
```

signal 存登录态：读它的模板自动随登出刷新（signals 简介 [[前端开发/03-JS框架/Angular/04-Angular实战|下章展开]]）。

### 5.3 登录页（响应式表单）

```ts
import { Component, inject } from '@angular/core';
import { FormBuilder, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule],
  template: `
    <form [formGroup]="form" (ngSubmit)="submit()" style="max-width:320px;margin:60px auto">
      <h2>登录</h2>
      <input formControlName="username" placeholder="用户名" />
      <input formControlName="password" type="password" placeholder="密码" />
      @if (error) { <p style="color:red">{{ error }}</p> }
      <button [disabled]="form.invalid || busy">{{ busy ? '登录中...' : '登录' }}</button>
    </form>
  `,
})
export class LoginComponent {
  private fb = inject(FormBuilder);
  private auth = inject(AuthService);
  private router = inject(Router);

  form = this.fb.nonNullable.group({
    username: ['', Validators.required],
    password: ['', Validators.required],
  });
  error = '';
  busy = false;

  async submit() {
    this.busy = true;
    try {
      const { username, password } = this.form.getRawValue();
      await this.auth.login(username, password);
      void this.router.navigateByUrl(history.state.from ?? '/');   // 跳回来源页或首页
    } catch (e) {
      this.error = e instanceof Error ? e.message : '登录失败';
    } finally {
      this.busy = false;
    }
  }
}
```

### 5.4 CRUD 页 + mock API

public/api/todos.json 提供初始数据；真实写入用内存模拟（重点看链路而非存储）：

```ts
// pages/todo-crud.component.ts
import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

interface Todo { id: number; text: string; done: boolean }

@Component({
  selector: 'app-todo-crud',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div style="max-width:480px;margin:30px auto">
      <input [(ngModel)]="draft" placeholder="新待办" />
      <button (click)="add()">添加</button>
      <ul>
        @for (t of todos; track t.id) {
          <li>
            <input type="checkbox" [checked]="t.done" (change)="toggle(t)" />
            {{ t.text }}
            <button (click)="remove(t.id)">删</button>
          </li>
        }
      </ul>
    </div>
  `,
})
export class TodoCrudComponent implements OnInit {
  private http = inject(HttpClient);
  todos: Todo[] = [];
  draft = '';

  ngOnInit() {
    this.http.get<Todo[]>('api/todos.json').subscribe(list => (this.todos = list));
  }

  add() {
    const text = this.draft.trim();
    if (!text) return;
    this.todos = [{ id: Date.now(), text, done: false }, ...this.todos];
    this.draft = '';
    // 真实后端: this.http.post('/api/todos', {text}).subscribe(...)
  }

  toggle(t: Todo) {
    t.done = !t.done;
    // 真实后端: this.http.patch(`/api/todos/${t.id}`, {done: t.done}).subscribe(...)
  }

  remove(id: number) {
    this.todos = this.todos.filter(t => t.id !== id);
    // 真实后端: this.http.delete(`/api/todos/${id}`).subscribe(...)
  }
}
```

### 5.5 路由与守卫装配

```ts
// app.routes.ts
import { Routes } from '@angular/router';
import { authGuard } from './auth.guard';
import { LoginComponent } from './pages/login.component';
import { TodoCrudComponent } from './pages/todo-crud.component';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  {
    path: '',
    canActivate: [authGuard],                 // 整个受保护区
    children: [
      { path: '', component: TodoCrudComponent, title: '待办管理' },
    ],
  },
  { path: '**', redirectTo: '' },
];
```

```ts
// main.ts 全家桶注册
bootstrapApplication(AppComponent, {
  providers: [
    provideRouter(routes, withComponentInputBinding()),
    provideHttpClient(withInterceptors([authInterceptor])),
  ],
});
```
验收清单：

- [ ] 未登录直接访问 `/` 被 authGuard 踢到 `/login?from=/`，登录成功跳回来源页；
- [ ] 手动清掉 localStorage 再点页面内导航被拦（每次导航都过守卫）；
- [ ] CRUD 操作正常且 mock 数据来自 HTTP（Network 可见 json 请求）；
- [ ] 把任意接口地址改成 404 观察 error 分支表现。

自检清单：

- [ ] routes 数组/routerLink/outlet 三要素与另外两家同构
- [ ] loadComponent/loadChildren 懒加载两式；守卫三件时机背得出
- [ ] 拦截器必须 clone 请求，catchError 收口错误
- [ ] 复杂表单默认 ReactiveForms，getRawValue 强类型

---

## 小结

| 知识点 | 一句话 |
|--------|--------|
| 路由配置 | routes 数组 + outlet + routerLink |
| 懒加载 | loadComponent/loadChildren 切块 |
| 守卫 | canActivate/canDeactivate/resolve 导航期拦截 |
| 拦截器 | token 注入与错误收口的横切层 |
| 响应式表单 | FormBuilder 声明结构，校验在代码可测试 |
| 选型 | 简单单字段模板驱动，其余一律 ReactiveForms |

综合演练收官：[[前端开发/03-JS框架/Angular/04-Angular实战|Angular 实战]]。
