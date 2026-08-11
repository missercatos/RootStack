# Flask：十分钟起一个服务 (Flask Quickstart)
---

## 📖 章节概述

Flask 是 Python 生态中最轻量的 Web 微框架——核心代码仅 5 行即可运行一个 HTTP 服务。本章面向 C 程序员，快速展示 Flask 的路由、请求/响应处理、JSON API 和模板渲染，让你在十分钟内就能为 C 后端服务搭建一个 Web 前端界面。

> **核心理念**：Flask 的哲学是"微框架，全自由"。它只提供最核心的路由和请求/响应封装，不强制任何项目结构、ORM 或模板引擎。对于 C 程序员而言，这恰好契合"最小依赖、手动控制"的习惯——你可以在 Flask 路由中通过 `subprocess` 调用 C 程序、通过 `ctypes` 加载 C 共享库、或者通过管道交换数据，Flask 只负责 HTTP 层。

---

### 📚 第一节：最小 Flask 应用

一个完整的 Flask Web 服务，仅需 5 行代码：

```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

app.run()
```

保存为 `app.py`，执行 `python app.py`，浏览器打开 `http://127.0.0.1:5000` 即可看到页面。

甚至可以一行命令直接启动：

```bash
python -c "from flask import Flask; app=Flask(__name__); \
  @app.route('/'); def hello(): return 'Hello'; app.run()"
```

核心组件拆解：

| 组件 | 含义 | 对应 C 思维 |
|------|------|------------|
| `Flask(__name__)` | 创建 WSGI 应用实例 | 类似 `int main()` 入口 |
| `@app.route('/')` | 装饰器：将 URL 路径绑定到函数 | 类似注册回调函数指针 |
| `return 'Hello'` | 返回 HTTP 响应体（默认 200） | 类似 `write(socket, buf)` |
| `app.run()` | 启动内置开发服务器 | 类似 `while(1) { accept(); }` |

> Flask 内置的 Werkzeug 开发服务器**仅用于开发**，生产环境必须使用 gunicorn（见 [[05_部署：gunicorn与Docker|第 5 章 部署]]）。

---

### 📚 第二节：路由与 URL 变量

路由是 URL 到处理函数的映射。Flask 支持多种路由模式：

```python
@app.route('/')                   # 根路径
def index():
    return 'Home Page'

@app.route('/user/<name>')        # 动态变量（字符串）
def user(name):
    return f'User: {name}'

@app.route('/post/<int:post_id>') # 类型转换：int/float/path/uuid
def show_post(post_id):
    return f'Post #{post_id * 2}'  # post_id 已是 int，不是字符串

@app.route('/files/<path:filepath>') # 匹配含 / 的路径
def serve_file(filepath):
    return f'File: {filepath}'
```

类型转换器对应 C 思维：

| 转换器 | Python 类型 | C 等价思维 |
|--------|------------|-----------|
| `<string:>` (默认) | `str` | `const char *` |
| `<int:>` | `int` | `atoi()` 自动完成 |
| `<float:>` | `float` | `atof()` 自动完成 |
| `<path:>` | `str`（含 `/`） | 原始字符串 |
| `<uuid:>` | `uuid.UUID` | 128-bit UUID 解析 |

`url_for()` 函数根据函数名反向生成 URL（避免硬编码）：

```python
from flask import url_for

@app.route('/user/<name>')
def profile(name):
    return f'Profile of {name}'

# url_for('profile', name='root') → '/user/root'
```

---

### 📚 第三节：HTTP 方法与请求对象

Flask 默认只响应 GET 请求。通过 `methods` 参数指定支持的 HTTP 方法：

```python
from flask import request

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']     # POST 表单数据
        password = request.form['password']
        return f'Hello, {username}'
    return '''
        <form method="post">
            <input name="username">
            <input name="password" type="password">
            <button type="submit">Login</button>
        </form>
    '''
```

`request` 对象常用属性（类比 C 中解析 HTTP 头）：

| 属性 | 内容 | C 对照 |
|------|------|--------|
| `request.method` | `'GET'`, `'POST'` 等 | 解析 HTTP 第一行 |
| `request.args` | URL 查询参数（`?key=val`） | 解析 QUERY_STRING |
| `request.form` | POST 表单数据 | 解析 POST body |
| `request.json` | JSON 请求体 | 解析 Content-Type: application/json |
| `request.headers` | HTTP 请求头 | 逐行读取 Header 字段 |
| `request.cookies` | Cookie 字典 | 解析 Cookie 头 |
| `request.files` | 上传的文件 | 解析 multipart/form-data |

获取 URL 查询参数：

```python
@app.route('/search')
def search():
    q = request.args.get('q', '')        # 安全获取，设默认值
    page = request.args.get('page', 1, type=int)  # 自动转 int
    return f'Searching for {q}, page {page}'
```

---

### 📚 第四节：JSON API 与返回响应

对于前后端分离或 API 服务，JSON 是核心数据格式：

```python
from flask import jsonify, make_response

@app.route('/api/v1/data')
def get_data():
    return jsonify({
        'status': 'ok',
        'data': [1, 2, 3],
        'count': 3
    })
    # 自动设置 Content-Type: application/json

@app.route('/api/v1/compute')
def compute():
    # 典型场景：Flask 接收请求 → 调用 C 后端 → 返回结果
    result = {'sum': 100, 'product': 200}
    resp = make_response(jsonify(result))
    resp.headers['X-Custom-Header'] = 'value'
    resp.status_code = 201           # 自定义状态码
    return resp
```

错误响应：

```python
from flask import abort

@app.route('/api/v1/data/<int:id>')
def get_item(id):
    if id < 0:
        abort(400, description='Invalid ID: must be non-negative')
    return jsonify({'id': id, 'name': f'item_{id}'})
```

---

### 📚 第五节：模板与静态文件（简述）

Flask 使用 Jinja2 模板引擎渲染 HTML。目录约定：

```
project/
├── app.py
├── templates/          ← 模板文件（Flask 自动查找）
│   └── index.html
└── static/             ← 静态文件（CSS/JS/图片）
    └── style.css
```

模板渲染：

```python
from flask import render_template

@app.route('/hello/<name>')
def hello(name):
    return render_template('index.html', name=name, items=[1, 2, 3])
```

```html
<!-- templates/index.html -->
<h1>Hello, {{ name }}!</h1>
<ul>
{% for item in items %}
    <li>{{ item }}</li>
{% endfor %}
</ul>
```

静态文件自动挂载在 `/static/` 路径下，HTML 中用 `url_for('static', filename='style.css')` 引用。模板的详细用法见 [[03_模板与静态资源|第 3 章 模板与静态资源]]。

---

### 📚 第六节：包装 C 后端为 Web 服务

Flask 最适宜作为 C 后端的 HTTP 前端。三种互操作模式：

**模式一：subprocess 调用 C 程序**

```python
import subprocess, json

@app.route('/api/c-run')
def c_run():
    result = subprocess.run(
        ['./bin/my_c_program', '--input', '42'],
        capture_output=True, text=True, timeout=5
    )
    return jsonify({
        'exit_code': result.returncode,
        'stdout': result.stdout,
        'stderr': result.stderr
    })
```

**模式二：ctypes 调用 C 共享库**

```python
import ctypes

lib = ctypes.CDLL('./lib/libcompute.so')
lib.compute_sum.argtypes = [ctypes.c_int, ctypes.c_int]
lib.compute_sum.restype = ctypes.c_int

@app.route('/api/sum/<int:a>/<int:b>')
def api_sum(a, b):
    result = lib.compute_sum(a, b)
    return jsonify({'sum': result})
```

**模式三：管道/共享内存/消息队列**

```python
# 打开命名管道与 C 后台进程通信
@app.route('/api/pipe-query')
def pipe_query():
    with open('/tmp/c_backend.pipe', 'w') as f:
        f.write('QUERY\n')
    with open('/tmp/c_backend_resp.pipe', 'r') as f:
        result = f.read()
    return jsonify({'result': result.strip()})
```

> ctypes 的完整用法见 [[../2精通/05_ctypes：在Python中调用C库|精通 05 ctypes]]，进程间通信见 [[../2精通/08_subprocess与进程管道：C与Python数据交换|精通 08 进程管道]]。

---

### 📝 小节练习

> [!question] 选择题 1
> Flask 装饰器 `@app.route('/user/<int:id>')` 中的 `<int:id>` 表示什么？
> - [ ] A. 只匹配字符串类型
> - [ ] B. 匹配整数并自动转换为 Python int
> - [ ] C. 必须传入 32 位有符号整数
> - [ ] D. 匹配正则表达式
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `<int:>` 转换器自动将 URL 中的数字字符串转换为 Python `int` 类型，省去手动调用 `int()` 的步骤。

> [!question] 判断题 1
> Flask 内置的开发服务器可以直接用于生产环境。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: Flask 的 `app.run()` 启动的是 Werkzeug 开发服务器，单线程、无进程管理、无安全加固，仅适合开发测试。生产环境必须使用 gunicorn 等 WSGI 服务器。

> [!question] 选择题 2
> 获取 URL `http://host/search?q=flask&page=2` 中 `page` 参数的推荐方式是？
> - [ ] A. `request.args[1]`
> - [ ] B. `request.form.get('page')`
> - [ ] C. `request.args.get('page', 1, type=int)`
> - [ ] D. `request.query.page`
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: `request.args` 存储查询参数。`.get()` 方法安全获取（不存在返回默认值），`type=int` 自动类型转换。

---

## 📋 章节测试

### 一、判断题（正确选 ✅，错误选 ❌）

> [!question] 判断题 1
> Flask 是一个全栈 Web 框架，内置 ORM 和表单验证。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: Flask 是"微框架"，核心仅包含路由、请求/响应、模板渲染。ORM（如 SQLAlchemy）、表单验证（如 WTForms）、用户认证等需要通过扩展添加。Django 才是内置 ORM 的全栈框架。

> [!question] 判断题 2
> `app = Flask(__name__)` 中的 `__name__` 用于让 Flask 确定模板和静态文件的根目录。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: Flask 通过 `__name__` 获取当前模块的路径，从而定位 `templates/` 和 `static/` 目录的位置。

> [!question] 判断题 3
> `jsonify()` 返回的是普通字符串，需要手动设置 Content-Type。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `jsonify()` 返回一个 `Response` 对象，已自动设置 `Content-Type: application/json`。

> [!question] 判断题 4
> Flask 的路由装饰器可以在同一个函数上使用多次，绑定多个 URL。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 可以对同一个函数叠加多个 `@app.route()` 装饰器，一个函数响应多个 URL。

> [!question] 判断题 5
> `url_for('static', filename='style.css')` 会生成 `/static/style.css` 这样的路径。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `url_for('static', filename='...')` 生成静态文件的完整 URL 路径，默认为 `/static/` 前缀。

---

### 二、选择题（单项选择题）

> [!question] 选择题 1
> Flask 启动开发服务器时，默认监听的主机和端口是？
> - [ ] A. 0.0.0.0:8080
> - [ ] B. 127.0.0.1:5000
> - [ ] C. 0.0.0.0:80
> - [ ] D. 127.0.0.1:3000
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `app.run()` 默认监听 `127.0.0.1:5000`。可通过 `app.run(host='0.0.0.0', port=8080)` 修改。

> [!question] 选择题 2
> 在 Flask 路由函数中，如果访问了不存在的 `request.form['key']`，会抛出什么异常？
> - [ ] A. `TypeError`
> - [ ] B. `ValueError`
> - [ ] C. `KeyError`
> - [ ] D. `SyntaxError`
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: 与字典行为一致，直接索引不存在的键抛出 `KeyError`。推荐使用 `request.form.get('key', default)` 安全获取。

> [!question] 选择题 3
> 以下哪个 URL 能匹配路由 `@app.route('/post/<int:post_id>')`？
> - [ ] A. `/post/hello`
> - [ ] B. `/post/3.14`
> - [ ] C. `/post/42`
> - [ ] D. `/post/`
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: `<int:post_id>` 只匹配整数。`/post/42` 匹配成功，`post_id` 为 Python `int` 类型的 42。

> [!question] 选择题 4
> 以下关于 `request.args` 的说法正确的是？
> - [ ] A. 存储 POST 请求的表单数据
> - [ ] B. 存储 URL 查询参数（`?key=val`）
> - [ ] C. 存储 JSON 请求体
> - [ ] D. 存储请求头
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `request.args` 是一个 `ImmutableMultiDict`，存储 URL 查询字符串中的参数。POST 表单用 `request.form`，JSON 用 `request.json`。

> [!question] 选择题 5
> 使用 `abort(404)` 的效果是？
> - [ ] A. 杀死 Flask 进程
> - [ ] B. 返回 HTTP 404 错误响应并终止当前请求
> - [ ] C. 抛出 Python 异常但继续处理请求
> - [ ] D. 重定向到 `/404` 页面
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `abort(code)` 抛出 `HTTPException`，由 Flask 框架捕获后返回对应的 HTTP 错误响应。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：最小 Web 服务
> **难度**: ⭐
>
> 写一个 5 行的 Flask 应用，访问根路径 `/` 返回 `"Hello, C Programmer!"`。用浏览器验证后，尝试用 `curl http://127.0.0.1:5000` 查看原始 HTTP 响应。

> [!example] 练习题 2：JSON API 端点
> **难度**: ⭐⭐
>
> 实现一个 `/api/v1/fib/<int:n>` 端点，返回前 n 个斐波那契数的 JSON 数组。要求：
> - n ≤ 100，超出返回 400 错误
> - 返回格式 `{"status": "ok", "data": [0, 1, 1, 2, ...]}`
> - 用 `curl` 和浏览器分别测试

> [!example] 练习题 3：C 后端封装
> **难度**: ⭐⭐⭐
>
> 写一个 C 程序 `compute.c`，接受命令行参数 `<op> <a> <b>`，输出计算结果到 stdout：
> ```c
> // int main(int argc, char **argv) → 解析 argv[1]/[2]/[3] → printf("%d\n", result)
> ```
> 编译后，在 Flask 路由中通过 `subprocess.run` 调用该程序，将结果封装为 JSON API 返回。

> [!example] 练习题 4：多路由表单
> **难度**: ⭐⭐
>
> 实现两个路由：
> - `GET /form` — 显示 HTML 表单（含姓名、年龄两个字段）
> - `POST /form` — 接收表单数据，显示提交结果页面
>
> 使用 `render_template` 渲染 HTML 模板，模板中展示表单数据。
