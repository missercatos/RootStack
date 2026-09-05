# Django：全栈 Web 框架 (Django: Full-Stack Web Framework)

---

## 章节概述

Django 是 Python 最流行的全栈 Web 框架，自带 ORM、模板引擎、Admin 后台、认证系统、表单处理等全套组件。与 Flask 的"微框架"哲学不同，Django 采用"batteries included"策略——开箱即用，适合快速开发内容驱动型网站（CMS、电商、社交平台）。

> **C 程序员视角**：Django 之于 Web，就像 Qt 之于 GUI——框架替你处理了大量底层细节（HTTP 协议、数据库连接池、CSRF 防护、SQL 注入防护），你只需关注业务逻辑。

---

## 1. 安装与项目创建

```bash
# 安装 Django
pip install django

# 创建项目
django-admin startproject mysite
cd mysite

# 项目结构
mysite/
├── manage.py          # 管理脚本（类似 Makefile）
├── mysite/
│   ├── __init__.py
│   ├── settings.py    # 全局配置
│   ├── urls.py        # URL 路由
│   ├── asgi.py        # ASGI 入口
│   └── wsgi.py        # WSGI 入口
```

```bash
# 启动开发服务器
python manage.py runserver
# 默认 http://127.0.0.1:8000/

# 创建应用（app）
python manage.py startapp blog
```

---

## 2. MTV 架构

Django 使用 MTV（Model-Template-View）模式：

```
请求 → URL 路由 → View（逻辑） → Model（数据） → Template（渲染）
```

| 组件 | 职责 | 类比 C |
|------|------|--------|
| Model | 数据库表映射 | struct + SQL |
| Template | HTML 模板渲染 | printf 格式化输出 |
| View | 请求处理逻辑 | main() 中的请求分发 |
| URL | URL → View 映射 | switch-case 路由 |

---

## 3. Model：ORM 数据库操作

```python
# blog/models.py
from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
```

```bash
# 生成迁移文件
python manage.py makemigrations

# 执行迁移（创建表）
python manage.py migrate

# 创建超级用户（Admin 登录用）
python manage.py createsuperuser
```

```python
# Django Shell 操作数据（python manage.py shell）
from blog.models import Post

# 创建
Post.objects.create(title="Hello", content="World")

# 查询
Post.objects.filter(published=True)
Post.objects.get(id=1)

# 更新
post = Post.objects.get(id=1)
post.published = True
post.save()

# 删除
post.delete()
```

---

## 4. View：请求处理

```python
# blog/views.py
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from .models import Post

# 函数视图
def post_list(request):
    posts = Post.objects.filter(published=True)
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

# API 视图（返回 JSON）
def post_api(request):
    posts = list(Post.objects.values('id', 'title', 'content'))
    return JsonResponse({'posts': posts})
```

---

## 5. URL 路由

```python
# mysite/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls')),
]
```

```python
# blog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('api/posts/', views.post_api, name='post_api'),
]
```

---

## 6. Template 模板

```html
<!-- blog/templates/blog/post_list.html -->
<!DOCTYPE html>
<html>
<head><title>博客</title></head>
<body>
    <h1>文章列表</h1>
    {% for post in posts %}
    <article>
        <h2><a href="{% url 'post_detail' post.pk %}">{{ post.title }}</a></h2>
        <p>{{ post.content|truncatewords:30 }}</p>
        <time>{{ post.created_at|date:"Y-m-d" }}</time>
    </article>
    {% endfor %}
</body>
</html>
```

---

## 7. Admin 后台

```python
# blog/admin.py
from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'published')
    list_filter = ('published', 'created_at')
    search_fields = ('title', 'content')
```

访问 `http://127.0.0.1:8000/admin/` 即可管理所有数据。

---

## 8. 表单与 CSRF

```python
# blog/forms.py
from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'published']
```

```html
<!-- 模板中使用表单 -->
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">发布</button>
</form>
```

Django 自动处理 CSRF token，无需手动管理——这是相比 Flask 的安全优势。

---

## 9. Django REST Framework（DRF）

```bash
pip install djangorestframework
```

```python
# blog/serializers.py
from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
```

```python
# blog/views.py
from rest_framework import viewsets
from .models import Post
from .serializers import PostSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
```

DRF 自动生成 RESTful API，包含序列化、分页、过滤、权限控制。

---

## 10. 与 C 程序集成

```python
# 通过 subprocess 调用 C 程序
import subprocess

def run_c_program(request):
    result = subprocess.run(
        ['./my_c_program', arg1, arg2],
        capture_output=True, text=True
    )
    return JsonResponse({'output': result.stdout})
```

```python
# 通过 ctypes 调用 C 共享库
import ctypes

lib = ctypes.CDLL('./libmylib.so')
lib.process_data.argtypes = [ctypes.c_char_p]
lib.process_data.restype = ctypes.c_int

def process(request):
    result = lib.process_data(b"input data")
    return JsonResponse({'result': result})
```

---

## 11. 部署

```bash
# 生产环境
pip install gunicorn

# 启动
gunicorn mysite.wsgi:application --bind 0.0.0.0:8000

# Nginx 反向代理配置
# location / { proxy_pass http://127.0.0.1:8000; }
```

```bash
# Docker 部署
# Dockerfile
FROM python:3.12
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["gunicorn", "mysite.wsgi:application", "--bind", "0.0.0.0:8000"]
```

---

## 12. Django vs Flask vs FastAPI

| 特性 | Django | Flask | FastAPI |
|------|--------|-------|---------|
| 定位 | 全栈框架 | 微框架 | 异步 API 框架 |
| ORM | 内置 | 需 SQLAlchemy | 需 SQLAlchemy |
| Admin | 内置 | 无 | 无 |
| 认证 | 内置 | 需扩展 | 需扩展 |
| 模板 | 内置 Jinja2 | Jinja2 | 无 |
| 异步 | 3.1+ 支持 | 需扩展 | 原生 |
| 学习曲线 | 陡峭 | 平缓 | 中等 |
| 适用场景 | CMS/电商/API | 小型服务/原型 | 高性能 API |

> **选择建议**：内容驱动型网站（博客/CMS/电商）选 Django；小型微服务选 Flask；高性能异步 API 选 FastAPI。

---

## 速查卡片

| 需求 | 命令 |
|------|------|
| 创建项目 | `django-admin startproject mysite` |
| 创建应用 | `python manage.py startapp blog` |
| 迁移数据库 | `python manage.py makemigrations && python manage.py migrate` |
| 启动服务器 | `python manage.py runserver` |
| Django Shell | `python manage.py shell` |
| 创建管理员 | `python manage.py createsuperuser` |
| 收集静态文件 | `python manage.py collectstatic` |
