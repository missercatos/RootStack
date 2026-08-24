# Angular 基础：大而全的企业级框架

> 前置：[[前端开发/01-基础/JavaScript/06-ES6+特性|ES6+ 特性]]、TypeScript 基础
> 目标：认识 Angular 定位与心智差异，会用 CLI 与组件三件套，掌握四向数据绑定、内置指令与管道，跑通第一个产品列表。

---

## 1. Angular 定位

### 1.1 全家桶哲学

Angular 是 Google 维护的全功能框架：**路由、HTTP 客户端、表单、依赖注入全部官方内置**，不靠社区拼装。配套还有：TypeScript 强制使用、CLI 深度集成（生成/测试/构建一条龙）、每半年一个大版本的严格升级节奏。

| 能力 | Vue/React 的做法 | Angular 的做法 |
|------|------------------|----------------|
| 路由 | vue-router / react-router（官方或半官方） | @angular/router 内置 |
| HTTP | fetch / axios 自选 | HttpClient 服务内置 |
| DI | 无（Context/Zustand 补位） | 平台级 DI 内置 |
| 表单 | 手写或第三方库 | 响应式/模板驱动两套内置 |
| 语言 | JS/TS 自由 | TS 强制 |

一句话定位：**企业级大项目首选之一**——规范统一、工具链完备、长期支持版本明确，适合多人多年度维护的系统。

### 1.2 与 Vue/React 的心智差异

小而灵活派（Vue/React）给你零件自己组装；大而全派（Angular）给整车并规定开法：

- **一切皆类 + 装饰器**：组件是带 `@Component` 的 TS 类，服务是 `@Injectable` 类——Java 后端看 Angular 会强烈既视感；
- **约定强**：命名、目录结构、模块划分都有官方推荐，团队间代码风格趋同；
- 学习曲线前陡后缓：概念多（DI/RxJS/生命周期），但一旦建立心智，产出极其稳定。

注意区分：本教程讲的是现代 Angular（2+，当前主流），与早已 EOL 的 AngularJS（1.x）是完全不同的框架，后者仅作快速参考见 [[前端开发/03-JS框架/AngularJS/01-AngularJS快速参考|AngularJS 快速参考]]。

### 1.3 给 Java 同学的翻译表

| Java/Spring 世界 | Angular 世界 |
|------------------|--------------|
| @Service/@Component 注解 | @Component/@Injectable 装饰器 |
| Spring IoC 容器 | Angular DI 注入器 |
| application.yml | environment.ts / angular.json |
| Maven/Gradle | Angular CLI (ng) |
| Spring MVC Controller | 组件 + 服务 |
| 强类型编译检查 | tsc 编译期检查 |

这份表会在 [[前端开发/03-JS框架/Angular/02-组件与服务|下一章]] DI 部分全面兑现。

## 2. CLI：Angular 的 Maven

```bash
npm i -g @angular/cli

ng new product-app          # 创建项目(交互选择: 样式方案/SSR)
cd product-app
ng serve                    # 开发服务器, http://localhost:4200, 热更新
```

常用命令速查（`ng generate` 简写 `ng g`）：

```bash
ng g component product-list     # 生成组件四件套
ng g service product            # 生成服务
ng g module admin --routing     # 生成模块
ng build                        # 生产构建 → dist/
ng test                         # 单元测试(Karma/Jasmine)
```

生成器不只是省打字：它保证全团队的文件结构与命名完全一致——这是"全家桶"纪律性的第一体现。

## 3. 组件三件套

### 3.1 结构解剖

每个组件由装饰器配置 + TS 类 + 模板 + 样式构成：

```ts
import { Component } from '@angular/core';

@Component({
  selector: 'app-hello',           // 使用时的标签名 <app-hello>
  template: `
    <h2>你好，{{ name }}</h2>
    <button (click)="toggle()">切换</button>
  `,
  styles: [`h2 { color: #2563eb; }`],
})
export class HelloComponent {
  name = 'Angular';

  toggle() {
    this.name = this.name === 'Angular' ? '世界' : 'Angular';
  }
}
```

三件套拆解：

| 部分 | 说明 |
|------|------|
| @Component 装饰器 | 元数据：selector/template/styles |
| TS 类 | 数据成员与方法——模板的逻辑载体 |
| template | HTML + Angular 模板语法（内联或 templateUrl 外链文件） |

对比 React：React 组件是函数；Angular 组件是类，模板独立于逻辑。对比 Vue：单文件组件的 template/script/style 三段在 Angular 里被拆成模板字符串（或独立 html 文件）+ ts 文件。

### 3.2 模板语法总览

```html
<!-- 插值 -->
<p>{{ title }}</p>

<!-- 属性绑定 [] : 组件数据 → 视图 -->
<img [src]="user.avatar" [alt]="user.name">
<button [disabled]="loading">提交</button>

<!-- 事件绑定 () : 视图 → 组件逻辑 -->
<button (click)="save()">保存</button>
<input (input)="onInput($event)">

<!-- 双向绑定 [()] = [] + () 语法糖 -->
<input [(ngModel)]="draft">

<!-- 结构指令 * 前缀: 操作 DOM 结构 -->
<p *ngIf="error; else loading">出错了</p>
<li *ngFor="let item of items; index as i">{{ i }}. {{ item }}</li>
```

## 4. 数据绑定四向

把上面散点收拢成一张体系表——Angular 官方话术叫"四种绑定方向"：

| 方向 | 语法 | 流向 | 示例 |
|------|------|------|------|
| 插值 | `{{ expr }}` | 组件 → 视图 | `<h1>{{title}}</h1>` |
| 属性绑定 | `[prop]="expr"` | 组件 → 视图 | `[src]="imgUrl"` |
| 事件绑定 | `(event)="handler"` | 视图 → 组件 | `(click)="submit()"` |
| 双向绑定 | `[(ngModel)]="prop"` | 双向 | `<input [(ngModel)]="name">` |

双向绑定是属性绑定 + 事件绑定的糖：`[(ngModel)]="name"` 等价于 `[ngModel]="name" (ngModelChange)="name=$event"`。需要引入 FormsModule 才能用 ngModel：

```ts
import { FormsModule } from '@angular/forms';

@Component({
  imports: [FormsModule],        // standalone 组件的导入方式
  template: `<input [(ngModel)]="draft" placeholder="输入试试">
             <p>{{ draft }}</p>`,
})
export class EchoComponent {
  draft = '';
}
```

与 React 对照：Angular 的 `[]` 即 props 下发、`()` 即回调上报，`[()]` 则相当于受控组件的 value+onChange 合体。与 Vue 对照几乎逐字相同：`[]`≈`:prop`，`()`≈`@event`，`[(ngModel)]`≈`v-model`。

## 5. 指令入门

指令分两类：**结构指令**（增删 DOM 元素，带 * 号）与**属性指令**（改变元素外观/行为）。

### 5.1 结构指令

```html
<!-- *ngIf: 条件渲染, 可带 else 分支 -->
<div *ngIf="user; else anonymous">欢迎 {{ user.name }}</div>
<ng-template #anonymous><a href="/login">请登录</a></ng-template>

<!-- *ngFor: 列表渲染, trackBy 优化 diff -->
<li *ngFor="let p of products; let i = index" [key]="p.id">
  {{ i + 1 }}. {{ p.name }}
</li>

<!-- *ngSwitch 系列 -->
<span [ngSwitch]="status">
  <em *ngCase="'paid'">已支付</em>
  <em *ngCase="'shipped'">已发货</em>
  <em *ngDefault>处理中</em>
</span>
```

*ngFor 必须给稳定标识辅助变更检测（新版本推荐 `track p.id` 写法），对应 React key 与 Vue :key 的角色。

### 5.2 属性指令

```html
<!-- ngClass: 动态类名集合 -->
<div [ngClass]="{ active: isSelected, disabled: !enabled }">

<!-- ngStyle: 动态样式 -->
<div [ngStyle]="{ color: level > 3 ? 'red' : 'green', fontSize.px: 14 }">

<!-- ngModel: 前面已见, 也是属性指令家族 -->
```

对照小结：`*ngIf/*ngFor` ≈ v-if/v-for ≈ JSX 条件/map；`[ngClass]` ≈ v-bind:class ≈ clsx。

> 版本注记：Angular 17 引入控制流新语法 `@if (cond) {} @else {}`、`@for (p of products; track p.id) {}`，逐步替代 *ngIf/*ngFor。老项目两者并存，新项目可优先新语法；本教程以经典指令为主线便于对照学习。

## 6. pipe 管道

### 6.1 内置管道

管道是模板里的显示变换器：`{{ 表达式 | 管道:参数 }}`。

```html
<p>{{ birthday | date:'yyyy-MM-dd' }}</p>          <!-- 2026-08-24 -->
<p>{{ price | currency:'CNY':'symbol' }}</p>       <!-- ¥1,299.00 -->
<p>{{ longText | slice:0:50 }}...</p>
<p>{{ name | uppercase | slice:0:10 }}</p>         <!-- 管道可串联 -->
<p>{{ userCount$ | async }}</p>                    <!-- async 管道自动订阅 Observable -->
```

常用内置管道：date/currency/decimal/percent/json/slice/lowercase/uppercase/titlecase/async/keyvalue。

### 6.2 自定义管道

需求：手机号脱敏 `138****5678`。

```bash
ng g pipe mask-phone
```

```ts
// mask-phone.pipe.ts
import { Pipe, PipeTransform } from '@angular/core';

@Pipe({ name: 'maskPhone' })
export class MaskPhonePipe implements PipeTransform {
  transform(value: string, visible = 3): string {
    if (!value || value.length <= visible * 2) return value ?? '';
    const head = value.slice(0, visible);
    const tail = value.slice(-visible);
    return `${head}${'*'.repeat(value.length - visible * 2)}${tail}`;
  }
}
```

```html
<p>{{ '13812345678' | maskPhone }}</p>       <!-- 138*******678 -->
<p>{{ cardNo | maskPhone:4 }}</p>            <!-- 参数化: 前4后4保留 -->
```

要点：实现 `PipeTransform` 接口的 transform 方法；管道应当纯（同输入同输出）。对照 React：没有直接对等物，等价于一个格式化函数调用 `{ maskPhone(user.phone) }`；对照 Vue：自定义 filter 的现代继任者。async 管道先记住名字，[[前端开发/03-JS框架/Angular/02-组件与服务|RxJS 章节]] 再展开。

## 7. 实战：产品列表

目标：ng 新项目里做一个带搜索过滤与状态高亮的产品列表，串起本章全部知识点。

```bash
ng new product-app --style=css --skip-git
cd product-app
ng serve
```

### 7.1 数据模型与根组件

```ts
// src/app/product.ts
export interface Product {
  id: number;
  name: string;
  price: number;
  stock: number;
}
```

```ts
// src/app/app.component.ts
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Product } from './product';

@Component({
  selector: 'app-root',
  standalone: true,                          // 现代 standalone 组件(17+ 推荐)
  imports: [CommonModule, FormsModule],
  template: `
    <main class="wrap">
      <h1>产品列表</h1>

      <input [(ngModel)]="keyword" placeholder="搜索产品名..." />

      <table>
        <thead>
          <tr><th>#</th><th>名称</th><th>价格</th><th>库存</th><th>状态</th></tr>
        </thead>
        <tbody>
          <tr *ngFor="let p of filtered(); let i = index"
              [ngClass]="{ low: p.stock < 10 }">
            <td>{{ i + 1 }}</td>
            <td>{{ p.name }}</td>
            <td>{{ p.price | currency:'CNY':'symbol':'1.2-2' }}</td>
            <td>{{ p.stock }}</td>
            <td>{{ p.stock > 0 ? '有货' : '缺货' }}</td>
          </tr>
        </tbody>
      </table>

      <p *ngIf="filtered().length === 0">没有匹配的产品</p>
      <p>共 {{ products.length }} 件，总价 {{ totalValue() | currency:'CNY' }}</p>
    </main>
  `,
  styles: [`
    .wrap { max-width: 640px; margin: 40px auto; font-family: system-ui; }
    table { width: 100%; border-collapse: collapse; margin-top: 12px; }
    th, td { border-bottom: 1px solid #eee; padding: 8px; text-align: left; }
    .low { background: #fff7ed; }
    input { padding: 6px 10px; width: 240px; }
  `],
})
export class AppComponent {
  keyword = '';

  products: Product[] = [
    { id: 1, name: '机械键盘', price: 399, stock: 25 },
    { id: 2, name: '无线鼠标', price: 129, stock: 8 },
    { id: 3, name: '显示器支架', price: 199, stock: 0 },
    { id: 4, name: 'USB-C 扩展坞', price: 249, stock: 42 },
  ];

  filtered(): Product[] {
    return this.products.filter(p =>
      p.name.toLowerCase().includes(this.keyword.trim().toLowerCase()),
    );
  }

  totalValue(): number {
    return this.products.reduce((sum, p) => sum + p.price, 0);
  }
}
```

standalone 组件无需 NgModule 注册，imports 数组直接声明依赖模块——这是 Angular 17+ 的推荐姿势（演进脉络下章细说）。

### 7.2 知识点覆盖自检

- [ ] @Component 装饰器的 selector/template/styles 三件套
- [ ] 插值、[]、()、[()] 四种绑定都在模板中出现
- [ ] *ngIf 空态提示、*ngFor 列表渲染、[ngClass] 条件样式
- [ ] date/currency 类管道格式化金额
- [ ] [(ngModel)] 搜索框驱动 filtered() 重算

运行 `ng serve` 后修改任意 stock 数字，观察低库存行高亮与总价联动——数据变化自动反映视图，这就是 Angular 变更检测的日常体感。

---

## 小结

| 知识点 | 一句话 |
|--------|--------|
| 定位 | Google 全家桶，TS 强制，企业级首选之一 |
| 心智差异 | 大而全 vs 小而灵活，Java 后端最易迁移 |
| CLI | ng new/serve/generate，Maven 式工程保障 |
| 组件三件套 | 装饰器元数据 + TS 类 + 模板样式 |
| 四向绑定 | 插值/[]/( )/[()]，v-model 的近亲 |
| 指令 | 结构指令动 DOM 树，属性指令改外观 |
| pipe | 模板显示变换器，date/currency/async |

组件怎么通信、服务怎么注入？见 [[前端开发/03-JS框架/Angular/02-组件与服务|组件与服务]]。
