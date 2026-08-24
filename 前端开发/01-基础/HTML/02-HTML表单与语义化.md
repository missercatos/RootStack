# HTML 表单与语义化

上一章解决了"页面怎么写"，这一章解决两个问题：**怎么收集用户输入**（表单），以及**怎么让机器读懂你的页面**（语义化）。表单是前端与后端交互的最原始入口——你在后端写的每一个 POST 接口，几乎都对应着前端的一个 form。

---

## form 元素：表单的容器

```html
<form action="/api/register" method="post">
  <!-- 各种输入控件放这里 -->
  <button type="submit">提交</button>
</form>
```

form 的核心属性：

| 属性 | 取值 | 说明 |
|------|------|------|
| action | URL | 提交到哪里，类比接口路径 |
| method | get / post | GET 把数据拼在 URL 上，POST 放在请求体 |
| enctype | 见下 | 编码类型 |
| novalidate | 布尔属性 | 关闭浏览器原生验证 |

enctype 的三种取值（后端工程师应该眼熟）：

- `application/x-www-form-urlencoded`（默认）：类似 URL 查询串的编码
- `multipart/form-data`：**文件上传必用**，后端解析 MultipartHttpServletRequest 就是它
- `text/plain`：极少用

类比后端：一个 `<form method="post" action="/api/users">` 提交时，等价于你用 Postman 发了一个 `POST /api/users`，Content-Type 为 urlencoded，body 里是各控件的 name=value 对。**控件必须有 name 属性才会被提交**——这是新手第一大坑：没写 name，后端收到的表单就是空的。

---

## input 全家桶

input 是表单的绝对主角，靠 `type` 变换形态。HTML5 之后 type 大幅扩充：

### 文本类

```html
<!-- 单行文本：最基础 -->
<input type="text" name="nickname" placeholder="请输入昵称">

<!-- 密码：显示为圆点 -->
<input type="password" name="password">

<!-- 邮箱：手机上弹出邮箱键盘，提交时校验格式 -->
<input type="email" name="email">

<!-- 数字：只能输数字，可配 min/max/step -->
<input type="number" name="age" min="0" max="150">

<!-- 电话：手机上弹出数字键盘 -->
<input type="tel" name="phone">

<!-- URL：校验网址格式 -->
<input type="url" name="homepage">

<!-- 搜索框：部分浏览器样式略有不同 -->
<input type="search" name="keyword">
```

这些 type 不是摆设，价值有三层：移动端弹对应的虚拟键盘；浏览器内置格式校验；读屏器播报更准确的控件类型。**能用语义 type 就不要一律写 text**。

### 选择类

```html
<!-- 单选按钮：同一 name 为一组，互斥 -->
<input type="radio" id="male" name="gender" value="M">
<label for="male">男</label>
<input type="radio" id="female" name="gender" value="F">
<label for="female">女</label>

<!-- 复选框：可多选，name 建议写成数组形式便于后端接收 -->
<input type="checkbox" name="hobby" value="reading"> 阅读
<input type="checkbox" name="hobby" value="coding"> 写代码
<input type="checkbox" name="hobby" value="gaming"> 游戏

<!-- 隐藏域：不显示但会提交，常用于传 token 或状态 -->
<input type="hidden" name="csrf_token" value="abc123">
```

注意 radio 的互斥逻辑由 **name 分组**实现，两组 radio 想各自独立就取不同 name。checkbox 多选提交时，同名多个值，Spring 后端用 `@RequestParam List<String> hobby` 接收。

### 其他常用控件

```html
<!-- 文件上传：accept 限制可选文件类型 -->
<input type="file" name="avatar" accept="image/*">
<!-- multiple 属性允许多选文件 -->

<!-- 日期时间系列：替代手写日期选择器 -->
<input type="date" name="birthday">
<input type="time" name="meeting_time">
<input type="datetime-local" name="appointment">

<!-- 颜色选择器 -->
<input type="color" name="theme_color">

<!-- 范围滑块 -->
<input type="range" name="volume" min="0" max="100">
```

## button、select 与 textarea

### button 三种类型

```html
<form>
  <button type="submit">提交（默认值）</button>
  <button type="reset">重置表单</button>
  <button type="button">普通按钮：什么都不做，行为由 JS 定义</button>
</form>
```

**button 在 form 内默认是 submit**——新手第二大坑：表单里放了按钮想让它触发 JS 弹窗，结果一点整个表单就提交刷新了页面。非提交按钮务必写 `type="button"`。

### select 下拉框

```html
<select name="city">
  <option value="">-- 请选择城市 --</option>
  <optgroup label="华东">
    <option value="shanghai" selected>上海</option>
    <option value="hangzhou">杭州</option>
  </optgroup>
  <optgroup label="华南">
    <option value="shenzhen">深圳</option>
  </optgroup>
</select>

<!-- multiple 属性变成多选列表 -->
<select name="tags" multiple size="4">
  <option value="java">Java</option>
  <option value="go">Go</option>
</select>
```

`selected` 是预选中项；`value` 不写则提交选项的文字内容。

### textarea 多行文本

```html
<textarea name="intro" rows="5" cols="40" placeholder="介绍一下自己"></textarea>
```

注意 textarea 是双标签，**初始内容写在标签之间而不是 value 属性里**；用户输入的首尾空白会被原样保留，后端入库前通常要 trim。

## label：最容易被忽视的无障碍关键

label 为控件提供说明文字，并通过 `for` 属性与控件的 `id` 显式关联：

```html
<label for="username">用户名</label>
<input type="text" id="username" name="username">
```

关联之后发生什么：

1. 点击文字即可聚焦输入框（点击热区扩大）
2. 屏幕阅读器朗读输入框时会报出 label 内容——视障用户全靠这个知道每个框该填什么
3. 单选/复选场景点击文字即切换选中，体验大幅提升

也可以用隐式关联（把控件包进 label）：

```html
<label>用户名 <input type="text" name="username"></label>
```

显式 `for + id` 关联更清晰、支持复杂布局，推荐作为团队规范。**没有 label 的输入框是无障碍审查的必挂项**，也是很多公司前端代码规范的红线。

fieldset 与 legend 可以给一组控件加分组外框和组标题：

```html
<fieldset>
  <legend>联系方式</legend>
  <label for="phone">电话</label>
  <input type="tel" id="phone" name="phone">
</fieldset>
```

---

## 表单验证属性

HTML5 提供了一组声明式验证属性，不用写一行 JS 就能拦截明显非法的提交：

```html
<form action="/api/register" method="post">
  <!-- required：必填，空则提交被阻止并提示 -->
  <input type="text" name="username" required
         minlength="3" maxlength="20"
         placeholder="3-20 个字符">

  <!-- pattern：正则校验，title 作为错误提示补充 -->
  <input type="text" name="phone" required
         pattern="1[3-9]\d{9}"
         title="请输入 11 位大陆手机号">

  <!-- 数值范围 -->
  <input type="number" name="age" min="18" max="65" required>

  <button type="submit">注册</button>
</form>
```

各属性速查：

| 属性 | 适用控件 | 作用 |
|------|---------|------|
| required | 几乎全部 | 必填 |
| minlength / maxlength | 文本类 | 长度限制 |
| min / max / step | number/range/date | 数值或日期范围 |
| pattern | text/search 等 | 正则匹配 |
| disabled | 全部 | 禁用（**不会提交**） |
| readonly | 文本类 | 只读但**会提交** |

两个容易踩的差异：

- `disabled` 与 `readonly` 都不可编辑，但 **disabled 的值不随表单提交**，readonly 会提交
- 浏览器原生验证只在**整表提交**那一刻触发；用 JS 接管提交（现代 SPA 都是如此）后需要自己调 `checkValidity()` 或改用 JS 校验库

类比后端：这些属性相当于 Bean Validation 注解（`@NotNull @Size @Pattern`），是"入口处的第一道闸"。但记住前端验证永远只是用户体验优化，**安全兜底必须在服务端重做**——绕过前端验证只需要 F12 删个属性。

---

## 语义化标签

### 为什么要有语义化

语义化标签 = 用"含义明确的标签"代替"无意义的 div 堆砌"。它服务于四类读者：

1. **搜索引擎爬虫**：爬虫不看渲染效果只看标签，`<article>` 里的文字权重高于 `<div>` 里的闲杂内容，这直接影响 SEO 排名
2. **屏幕阅读器**：视障用户可以按"跳到下一个地标区域"导航，前提是你的页面有 nav/main/footer 这些地标
3. **开发者自己**：半年后回看 `<aside>` 就知道是侧边栏，回看 `<div class="right-box">` 则要猜
4. **未来的设备**：智能音箱读网页、浏览器阅读模式提取正文，都依赖语义结构

类比后端：语义化之于 HTML，就像 RESTful 风格之于 API 设计——用 `GET /orders/42` 还是 `GET /api?action=getOrder&id=42` 都能工作，但前者让任何人都看得懂。**语义是写给所有消费方（包括人）的契约**。

### 页面骨架五件套与内容三件套

```html
<body>
  <!-- header：页头，logo/站名/主导航所在，可多个（如每篇文章自己的 header） -->
  <header>
    <h1>我的博客</h1>
    <nav><!-- nav：导航区块，内部惯例是 ul li a --></nav>
  </header>

  <!-- main：主内容区，全页唯一 -->
  <main>
    <!-- article：独立成篇的内容，脱离上下文也能看懂 -->
    <article>
      <h2>文章标题</h2>
      <section><!-- section：主题分组，通常带标题 --></section>
    </article>

    <!-- aside：与主线弱相关的内容：侧栏、广告、相关阅读 -->
    <aside>侧边栏</aside>
  </main>

  <!-- footer：页脚，版权/备案/联系方式 -->
  <footer>&copy; 2026</footer>
</body>
```

选用决策一句话版：

| 标签 | 用不用的一句话判断 |
|------|------------------|
| header / footer | 页面级或区块级的头尾 |
| nav | 是不是"主要导航链接集合"（页脚一堆杂链接不算） |
| main | 主内容，**全页仅一个** |
| article | 这块内容拿去 RSS 里单独发布还成立吗？成立就用 |
| section | 有主题且通常带标题的分组；纯排版需求用 div |
| aside | 拿掉不影响理解主内容的附加信息 |
| div | 以上都不合适时的最后手段 |

article 和 section 的区分是最常见的困惑：article 强调**独立性**（一篇博文、一条评论、一个商品卡），section 强调**章节性**（文章里"安装""配置"两节）。实在分不清时的经验法则：优先 article 或 div，section 别硬凑。

### 回顾 div 滥用问题

反面教材：

```html
<div class="top"><div class="menu">...</div></div>
<div class="content"><div class="post">...</div></div>
<div class="bottom">...</div>
```

正面改造：

```html
<header><nav>...</nav></header>
<main><article>...</article></main>
<footer>...</footer>
```

功能完全一样，但后者爬虫能识别出导航区和正文区，读屏器能跳转地标，代码量还更少。

---

## meta 标签详解

meta 写在 head 里，声明页面的元信息。三类最重要的：

### 字符集与兼容

```html
<meta charset="UTF-8">
<!-- 必须 head 内第一个出现，否则浏览器可能已按错误编码开始解析 -->

<!-- IE 兼容指令（历史项目常见，新项目可不写） -->
<meta http-equiv="X-UA-Compatible" content="IE=edge">
```

### viewport：移动适配的第一行代码

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

没有这行，手机浏览器会假设页面宽 980px 再整体缩小——你的响应式布局完全失效。逐参数解读：

| 参数 | 含义 |
|------|------|
| width=device-width | 视口宽度等于设备物理宽度 |
| initial-scale=1.0 | 初始缩放 1:1 |
| maximum-scale / user-scalable | 禁缩放——**不建议设**，无障碍红线 |

响应式设计详见 [[前端开发/01-基础/CSS/06-CSS实战：响应式设计|CSS 实战：响应式设计]]。

### SEO 三件套

```html
<meta name="description" content="张三的技术博客，专注 Java 后端与前端工程化">
<meta name="keywords" content="Java, 前端, 全栈"><!-- 主流搜索引擎已忽略 keywords -->
<title>张三的技术博客</title>

<!-- 社交分享卡片（分享到微信/Twitter 时展示） -->
<meta property="og:title" content="文章标题">
<meta property="og:description" content="文章摘要">
<meta property="og:image" content="https://example.com/cover.jpg">
```

description 虽然不直接参与排名计算，但它是搜索结果里标题下方那段摘要——直接影响用户点不点你。

---

## 实战：带验证的注册表单

综合本章知识，写一个完整的注册表单页面。保存为 `register.html` 直接打开即可体验原生验证。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="RootStack 社区账号注册页">
  <title>注册 · RootStack 社区</title>
</head>
<body>
  <main>
    <h1>创建账号</h1>

    <!-- novalidate 未设置 => 使用浏览器原生验证 -->
    <form action="/api/register" method="post">

      <fieldset>
        <legend>基本信息</legend>

        <!-- 用户名：必填 + 长度限制 + 正则限定字符 -->
        <p>
          <label for="username">用户名（3-16 位字母数字下划线）</label><br>
          <input type="text" id="username" name="username"
                 required minlength="3" maxlength="16"
                 pattern="\w+"
                 title="只能包含字母、数字、下划线"
                 autocomplete="username">
        </p>

        <!-- 邮箱：type=email 自带格式校验 -->
        <p>
          <label for="email">邮箱</label><br>
          <input type="email" id="email" name="email"
                 required placeholder="you@example.com"
                 autocomplete="email">
        </p>

        <!-- 密码：minlength 保证最低强度下限 -->
        <p>
          <label for="password">密码（至少 8 位）</label><br>
          <input type="password" id="password" name="password"
                 required minlength="8"
                 autocomplete="new-password">
        </p>
      </fieldset>

      <fieldset>
        <legend>更多资料</legend>

        <!-- 性别：radio 同名互斥，label 显式关联 -->
        <p>性别：
          <input type="radio" id="g-m" name="gender" value="M">
          <label for="g-m">男</label>
          <input type="radio" id="g-f" name="gender" value="F">
          <label for="g-f">女</label>
          <input type="radio" id="g-o" name="gender" value="O" checked>
          <label for="g-o">保密</label>
        </p>

        <!-- 城市：下拉选择 -->
        <p>
          <label for="city">所在城市</label>
          <select id="city" name="city">
            <option value="">-- 请选择 --</option>
            <option value="beijing">北京</option>
            <option value="shanghai">上海</option>
            <option value="shenzhen">深圳</option>
            <option value="other">其他</option>
          </select>
        </p>

        <!-- 技能多选：checkbox 同名数组提交 -->
        <p>技术方向：
          <input type="checkbox" id="t-be" name="stack" value="backend">
          <label for="t-be">后端</label>
          <input type="checkbox" id="t-fe" name="stack" value="frontend">
          <label for="t-fe">前端</label>
          <input type="checkbox" id="t-ops" name="stack" value="ops">
          <label for="t-ops">运维</label>
        </p>

        <!-- 个人简介：textarea，非必填 -->
        <p>
          <label for="bio">个人简介（100 字以内）</label><br>
          <textarea id="bio" name="bio" rows="4" maxlength="100"
                    placeholder="介绍一下你自己"></textarea>
        </p>
      </fieldset>

      <p>
        <!-- 协议勾选：required 让未勾选无法提交 -->
        <input type="checkbox" id="agree" name="agree" required>
        <label for="agree">我已阅读并同意<a href="#">《社区协议》</a></label>
      </p>

      <p>
        <!-- 提交按钮：触发原生验证 -->
        <button type="submit">注 册</button>
        <!-- 普通按钮：清空表单但不依赖 reset 的默认行为 -->
        <button type="reset">重 填</button>
      </p>

      <!-- 隐藏域：携带来源标记供后端统计 -->
      <input type="hidden" name="source" value="web-register-page">
    </form>
  </main>
</body>
</html>
```

设计决策讲解：

1. **fieldset/legend 分组**："基本信息"与"更多资料"两区视觉上自动出现分组框，语义上告诉辅助技术这是一组相关字段
2. **每个输入都有 label 且用 for/id 显式关联**：点击文字即聚焦；读屏器完整可用
3. **验证分层**：required/minlength/pattern/type 四种手段各司其职，零 JS 实现拦截；但后端仍需全套校验（永远如此）
4. **autocomplete 合理取值**：浏览器可帮用户自动填充，注册转化率细节
5. **隐藏域传 source**：典型的表单携带上下文手法
6. **radio 默认选中保密项**：敏感信息给用户留退路，产品思维体现在属性选择上

试玩建议：把 username 留空提交、填一个不合格手机号、不勾协议分别提交，观察浏览器原生提示气泡——这就是声明式验证的效果。

下一章我们看 HTML5 还带来了哪些能力：[[前端开发/01-基础/HTML/03-HTML5新特性|HTML5 新特性]]。
