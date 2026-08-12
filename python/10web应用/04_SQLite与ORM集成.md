# SQLite 与 ORM 集成 (SQLite & ORM)
---

## 章节概述

Web 应用离不开数据持久化。本章从 Python 标准库 `sqlite3` 模块入手，展示纯 SQL 操作 SQLite 数据库的基础用法；然后引入 SQLAlchemy ORM，用 Python 类映射数据表，通过对象操作替代手写 SQL；最后简要介绍 Alembic 数据库迁移工具。全程对比 C 语言直接调用 SQLite C API 的写法，帮助 C 程序员快速建立 Python 数据库编程的心理模型。

> **核心理念**：SQLite 之于单机应用，就像 `/tmp/data.db` 之于临时文件——零配置、嵌入式、无服务进程。对于 C 程序员来说，SQLite 并不陌生（SQLite 本身就是用 C 写的），Python 的 `sqlite3` 模块本质上是 SQLite C API 的一个薄封装。在此基础上，SQLAlchemy ORM 进一步将"SQL 字符串"抽象为"Python 对象操作"——这类似于 C++ 中从 `sprintf(buf, "INSERT INTO ...")` 进化为 `table.insert(obj)`。

---

### 第一节：sqlite3 标准库 — 纯 SQL 操作

Python 标准库自带的 `sqlite3` 模块提供了完整的 SQLite 接口，无需安装任何额外依赖。一行命令即可体验：

```bash
python -c "
import sqlite3
conn = sqlite3.connect(':memory:')
conn.execute('CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT)')
conn.execute(\"INSERT INTO users VALUES(1, 'Alice')\")
conn.commit()
for row in conn.execute('SELECT * FROM users'):
 print(row) # (1, 'Alice')
"
```

完整的 CRUD 操作：

```python
import sqlite3

conn = sqlite3.connect('app.db')
cur = conn.cursor()

cur.execute('''
 CREATE TABLE IF NOT EXISTS tasks (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 title TEXT NOT NULL,
 done INTEGER DEFAULT 0,
 created_at TEXT DEFAULT (datetime('now'))
 )
''')

cur.execute("INSERT INTO tasks (title) VALUES (?)", ("Learning Flask",))
cur.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Read docs", 0))
conn.commit()

cur.execute("SELECT id, title, done FROM tasks WHERE done = ?", (0,))
rows = cur.fetchall()
for row in rows:
 print(f"#{row[0]} {row[1]} [{'x' if row[2] else ' '}]")

cur.execute("UPDATE tasks SET done = 1 WHERE id = ?", (1,))
cur.execute("DELETE FROM tasks WHERE id = ?", (2,))
conn.commit()

conn.close()
```

关键 API 对照 C 的 SQLite C API：

| Python `sqlite3` | C SQLite API | 作用 |
|-----------------|-------------|------|
| `sqlite3.connect()` | `sqlite3_open()` | 打开/创建数据库 |
| `conn.execute()` | `sqlite3_prepare_v2()` + `sqlite3_step()` | 编译并执行 SQL |
| `cur.fetchall()` | 循环 `sqlite3_step()` == `SQLITE_ROW` | 获取结果行 |
| `?` 占位符 | `?` 占位符 | 参数绑定（防注入） |
| `conn.commit()` | `sqlite3_exec(db, "COMMIT", ...)` | 提交事务 |
| `conn.close()` | `sqlite3_close()` | 关闭数据库 |

> Python 的 `sqlite3` 会自动开启事务（`BEGIN` 隐式执行），因此写操作后必须 `commit()`，否则数据不会持久化——这与 C 中直接用 SQLite API 的行为一致。

使用 `with` 语句自动管理事务：

```python
with sqlite3.connect('app.db') as conn:
 conn.execute("INSERT INTO tasks (title) VALUES (?)", ("Auto commit",))
 # with 块正常退出时自动 commit，异常时自动 rollback
```

行工厂实现字典式访问（避免索引位置的脆弱性）：

```python
conn.row_factory = sqlite3.Row
cur = conn.execute("SELECT * FROM tasks")
for row in cur:
 print(row['id'], row['title']) # 用列名访问
```

---

### 第二节：SQLAlchemy ORM 入门

SQLAlchemy 是 Python 中最成熟的 ORM（对象关系映射）。其核心理念：将数据库表映射为 Python 类，将行映射为类的实例，将 SQL 操作映射为方法调用。

安装：

```bash
pip install sqlalchemy
```

定义模型（类比 C 中定义 struct + 建表 DDL）：

```python
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import DeclarativeBase, Session

class Base(DeclarativeBase):
 pass

class Task(Base):
 __tablename__ = "tasks"

 id = Column(Integer, primary_key=True, autoincrement=True)
 title = Column(String(200), nullable=False)
 done = Column(Boolean, default=False)

 def __repr__(self):
 return f"<Task(id={self.id}, title='{self.title}')>"

engine = create_engine("sqlite:///app.db", echo=True)
Base.metadata.create_all(engine) # 自动建表（CREATE TABLE IF NOT EXISTS）
```

CRUD 操作——对象式写法：

```python
# 创建会话
with Session(engine) as session:
 # Create
 task1 = Task(title="Learn Flask")
 task2 = Task(title="Read SQLAlchemy docs", done=True)
 session.add_all([task1, task2])
 session.commit() # commit 后 task.id 自动填充

 # Read
 tasks = session.query(Task).filter(Task.done == False).all()
 for t in tasks:
 print(t)

 # Read by primary key
 task = session.get(Task, 1) # SELECT ... WHERE id = 1
 print(task.title)

 # Update
 task.title = "Learn Flask and FastAPI"
 session.commit() # 自动检测变更并生成 UPDATE

 # Delete
 session.delete(task)
 session.commit()
```

SQLAlchemy 2.0 风格的 select 语法：

```python
from sqlalchemy import select

with Session(engine) as session:
 stmt = select(Task).where(Task.done == False).order_by(Task.id)
 tasks = session.scalars(stmt).all()
```

> 对比 C：在 C 中你需要手动拼接 SQL 字符串、绑定参数、遍历结果集、手动 malloc/free 结构体。ORM 中的 `session.query(Task).filter(...)` 一行替代了 C 中的 50 行。

---

### 第三节：模型关系 — 一对多、多对多

SQLAlchemy 的关系定义相当于 C 中结构体嵌套指针（或链表）：

```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
 __tablename__ = "users"

 id = Column(Integer, primary_key=True)
 name = Column(String(100))

 tasks = relationship("Task", back_populates="owner") # 一对多

class Task(Base):
 __tablename__ = "tasks"

 id = Column(Integer, primary_key=True)
 title = Column(String(200))
 user_id = Column(Integer, ForeignKey("users.id"))

 owner = relationship("User", back_populates="tasks")
```

使用关系：

```python
with Session(engine) as session:
 alice = User(name="Alice")
 alice.tasks = [
 Task(title="Write report"),
 Task(title="Review code"),
 ]
 session.add(alice)
 session.commit()

 # 通过关系访问
 user = session.query(User).filter_by(name="Alice").first()
 for task in user.tasks:
 print(task.title) # 自动执行 JOIN 查询
```

---

### 第四节：Alembic 数据库迁移

数据库 schema 会随项目演进。Alembic 是 SQLAlchemy 作者开发的迁移工具，类似 Git 管理代码版本，Alembic 管理数据库 schema 版本。

安装与初始化：

```bash
pip install alembic
alembic init migrations # 创建迁移目录
```

编辑 `alembic.ini` 中的数据库连接：

```ini
sqlalchemy.url = sqlite:///app.db
```

在 `migrations/env.py` 中设置 target_metadata：

```python
from app import Base # 导入你的模型基类
target_metadata = Base.metadata
```

迁移操作：

```bash
alembic revision --autogenerate -m "add users table" # 自动生成迁移脚本
alembic upgrade head # 应用所有迁移
alembic downgrade -1 # 回退一个版本
alembic history # 查看迁移历史
```

> 这类似于 C 项目中用 Makefile 管理编译步骤——Alembic 管理的是数据库 DDL 的"增量编译"。

---

### 第五节：与 Flask/FastAPI 集成

将 SQLAlchemy 集成到 Web 框架中：

**Flask 集成：**

```python
from flask import Flask, jsonify, request
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from models import Task, Base

app = Flask(__name__)
engine = create_engine("sqlite:///app.db")
Base.metadata.create_all(engine)

@app.route("/api/tasks")
def list_tasks():
 with Session(engine) as session:
 tasks = session.execute(select(Task)).scalars().all()
 return jsonify([{"id": t.id, "title": t.title, "done": t.done}
 for t in tasks])

@app.route("/api/tasks", methods=["POST"])
def create_task():
 data = request.json
 with Session(engine) as session:
 task = Task(title=data["title"])
 session.add(task)
 session.commit()
 return jsonify({"id": task.id, "title": task.title}), 201
```

**FastAPI 集成（使用依赖注入获得 session）：**

```python
from fastapi import FastAPI, Depends

app = FastAPI()
engine = create_engine("sqlite:///app.db")
Base.metadata.create_all(engine)

def get_session():
 with Session(engine) as session:
 yield session

@app.get("/api/tasks")
def list_tasks(session: Session = Depends(get_session)):
 tasks = session.execute(select(Task)).scalars().all()
 return tasks
```

---

### 第六节：Python sqlite3 vs C SQLite API 对比

同一个操作在 Python 和 C 中的代码量对比：

**计算表中行数：**

Python（3 行）：
```python
conn = sqlite3.connect('app.db')
count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
```

C（15 行）：
```c
sqlite3 *db;
sqlite3_stmt *stmt;
sqlite3_open("app.db", &db);
sqlite3_prepare_v2(db, "SELECT COUNT(*) FROM tasks", -1, &stmt, NULL);
sqlite3_step(stmt);
int count = sqlite3_column_int(stmt, 0);
sqlite3_finalize(stmt);
sqlite3_close(db);
```

差异总结：

| 维度 | Python sqlite3 | C SQLite API |
|------|---------------|-------------|
| 代码量 | 极简（3-5 行） | 冗长（10-20 行） |
| 错误处理 | 异常自动抛出 | 每个 API 检查返回码 |
| 内存管理 | GC 自动 | 手动 `sqlite3_finalize` / `sqlite3_free` |
| 性能 | 几乎相同（底层同一 C 库） | 无 Python 解释器开销 |
| 适合场景 | 快速开发、原型、工具脚本 | 嵌入式系统、性能敏感路径 |

> 实用主义原则：Web 服务层用 Python ORM 快速开发，计算密集的 C 后端内部可继续用 SQLite C API 直接读写数据库。

---

### 小节练习


> [!question] 判断题 1
> SQLAlchemy ORM 使用后，不需要再手写任何 SQL 语句。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: ORM 处理大部分常规 CRUD，但复杂查询（多表 JOIN、子查询、窗口函数）有时仍需手写 SQL。SQLAlchemy 支持 `session.execute(text("SQL"))` 执行原生 SQL。


---

## 章节测试

### 一、判断题（正确选 ，错误选 ）

> [!question] 判断题 1
> Python 的 `sqlite3` 模块是标准库的一部分，不需要 `pip install`。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `sqlite3` 是 Python 标准库模块，随 Python 解释器一起发布，无需额外安装。

> [!question] 判断题 2
> SQLAlchemy 的 `Base.metadata.create_all(engine)` 每次调用都会重建所有表（DROP + CREATE）。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `create_all()` 实际执行的是 `CREATE TABLE IF NOT EXISTS`，已存在的表不会被删除或重建。需要重建时用 `Base.metadata.drop_all()` 再 `create_all()`。

> [!question] 判断题 3
> Alembic 的 `--autogenerate` 选项会自动检测模型变化并生成迁移脚本。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `alembic revision --autogenerate -m "message"` 比较当前数据库状态与模型定义，自动生成迁移脚本。但复杂变更（如列重命名）可能需要手动调整生成的脚本。

> [!question] 判断题 4
> 在 SQLite 中，`sqlite3.connect()` 打开的数据库文件不存在时会报错。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: SQLite 的 `sqlite3_open()` 行为是：如果文件不存在就自动创建。Python 的 `sqlite3.connect()` 封装了此行为，也不会报错。

> [!question] 判断题 5
> SQLAlchemy 只能用于关系型数据库，不支持 SQLite。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: SQLAlchemy 支持所有主流关系型数据库，包括 SQLite、PostgreSQL、MySQL、Oracle 等。SQLite 通过 `sqlite:///` 前缀连接。

---


---

## 力扣练习

以下题目用于验证本章所学内容：

| 题号 | 题目 | 链接 | 涉及知识点 |
|------|------|------|-----------|
| 175 | 组合两个表 | https://leetcode.cn/problems/combine-two-tables/ | LEFT JOIN、表连接 |
| 176 | 第二高的薪水 | https://leetcode.cn/problems/second-highest-salary/ | 子查询、排序分页 |
| 178 | 分数排名 | https://leetcode.cn/problems/rank-scores/ | 窗口函数、排名 |



### 动手练习题

> [!example] 练习题 1：sqlite3 纯 SQL 命令行工具
> **难度**: 简单
>
> 写一个 Python 脚本，接受命令行参数对 SQLite 数据库进行 CRUD 操作：
> ```bash
> python db.py create "Buy milk" # INSERT
> python db.py list # SELECT all
> python db.py done 1 # UPDATE set done=1
> python db.py delete 3 # DELETE
> ```
> 使用 `argparse` 解析命令，使用 `sqlite3` 标准库操作数据库。

> [!example] 练习题 2：SQLAlchemy 模型与 Flask API
> **难度**: 简单
>
> 定义 `Book` 和 `Author` 两个 SQLAlchemy 模型（多对多关系：一本书多个作者，一个作者多本书）。提供 Flask REST API：
> - `POST /api/authors` — 创建作者
> - `POST /api/books` — 创建图书（关联已有作者）
> - `GET /api/authors/{id}/books` — 列出某作者的所有图书
>
> 使用 SQLite 存储，全部 CRUD 通过 Swagger UI 测试。

> [!example] 练习题 3：Alembic 迁移实践
> **难度**: 简单
>
> 在练习题 2 的基础上，使用 Alembic 管理数据库迁移：
> 1. 初始化 Alembic 迁移目录
> 2. 生成初始迁移（包含 Book 和 Author 表）
> 3. 新增一个 `publisher` 字段到 `Book` 模型，用 `--autogenerate` 生成增量迁移
> 4. 执行 `upgrade` 和 `downgrade`，验证迁移的向前向后兼容性

> [!example] 练习题 4：C SQLite 与 Python 对比
> **难度**: 简单
>
> 用 C 语言写一个程序，读取 SQLite 数据库中的 `tasks` 表，统计 `done=0` 的任务数量并输出。然后用 Python 的 `sqlite3` 标准库实现同样的功能。对比两者的代码行数、错误处理逻辑和开发耗时。思考：如果你的 Web 应用需要每分钟扫描数据库做聚合统计（性能关键路径），用 Python 做还是 C 做更合适？
