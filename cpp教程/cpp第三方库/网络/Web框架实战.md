# Web 框架实战：用 C++ 写 HTTP 服务

## 原理

### C++ 在 Web 世界的定位

先说结论：C++ **不是**全栈 Web 开发的主流选择——CRUD 业务系统用 Java/Python/Go 的开发效率高一个数量级。但以下场景 C++ 有一席之地且难以替代：

1. **高性能网关/代理层**：每秒数十万 QPS 的转发、协议转换，GC 停顿都嫌多的地方；
2. **嵌入式 API 层**：路由器、工业设备、车载系统里跑一个内存占用几 MB 的 REST 接口；
3. **低延迟交易/游戏后端**：P99 尾延迟以微秒计的场景；
4. **已有 C++ 核心的服务化封装**：算法引擎、音视频处理管线，为其套一层 HTTP 皮。

选型判断口诀：**瓶颈在业务逻辑就别用 C++，瓶颈在网络与计算本身才值得**。

### 主流轻量框架对比

| 框架 | GitHub 星级（量级） | 路由风格 | 中间件 | JSON 支持 | 依赖重量 |
|------|---------------------|---------|--------|-----------|---------|
| Crow | 很高（万级） | 宏注册 `CROW_ROUTE` | 有（插件式） | 内置 json 类 | 极轻，header-only |
| cpp-httplib | 很高（万级） | 回调函数注册 | 无 | 需外接 | 极轻，单头文件 |
| oatpp | 中等 | 控制器类+宏 | 完善 | 内置 DTO 映射 | 中，自带框架感 |
| Drogon | 高 | 宏+控制器类 | 完善（过滤器） | 内置 | 较重，需编译安装 |

选择逻辑：学习与轻量场景选 Crow 或 cpp-httplib；要完整 MVC 体验上 oatpp/Drogon。本章主线是 Crow——header-only、依赖最少、API 直观，最适合理解 C++ Web 的本质。

---

## 语法

### Hello World 与路由注册

```cpp
// main.cpp —— 编译前只需 apt install libssl-dev（可选）与一个支持 C++11 的编译器
#include "crow.h"        // header-only，把 crow_all.h 放进 include 路径即可

int main() {
    crow::SimpleApp app;                       // 单线程模型的最简应用对象

    CROW_ROUTE(app, "/")([](){                // 注册 GET / 的处理 lambda
        return "Hello from C++!";
    });

    app.port(18080).multithreaded().run();    // 多 worker 线程模式启动
}
```cpp

```bash
g++ -std=c++17 main.cpp -o hello -lpthread    # header-only 库：无链接步骤
./hello
curl http://localhost:18080/
```cpp

`CROW_ROUTE` 是宏展开成路由表注册；lambda 返回值自动包成 HTTP 200 响应。整条链路没有任何魔法框架代码，就是一个事件循环 + 分发表：

```mermaid
sequenceDiagram
    participant C as 客户端
    participant L as 监听线程
    participant R as 路由表
    participant H as 处理 lambda

    C->>L: GET /user/42
    L->>R: 方法 + 路径匹配
    R->>H: /user/<int> 命中，提取参数 42
    H-->>L: 返回 JSON 字符串
    L-->>C: 200 OK + body
```asm

### URL 参数、查询串与 JSON 请求体

```cpp
// 1) 路径参数：<int> 声明类型并自动转换
CROW_ROUTE(app, "/user/<int>")([](int id){
    return crow::json::wvalue{{"id", id}};
});

// 2) 多段路径参数
CROW_ROUTE(app, "/repo/<string>/<string>")
([](const std::string& owner, const std::string& repo){
    return owner + "/" + repo;
});

// 3) 查询串：request 对象的 url_params
CROW_ROUTE(app, "/search")
([](const crow::request& req){
    auto kw = req.url_params.get("q");          // /search?q=cpp&page=2
    auto page = req.url_params.get("page");
    if (!kw) return std::string("missing q");
    return fmt_ok(kw, page ? page : "1");
});
```asm

JSON 请求体解析：

```cpp
CROW_ROUTE(app, "/echo").methods(crow::HTTPMethod::POST)([](const crow::request& req){
    auto body = crow::json::load(req.body);     // 解析失败返回 falsy
    if (!body) return crow::response(400, "invalid json");
    return crow::response{crow::json::wvalue{
        {"received", body["name"].s()},         // 读字符串字段
        {"age", body["age"].i()}                // 读整型字段
    }};
});
```asm

Crow 自带的 `crow::json` 够用于简单场景；复杂结构建议换 nlohmann-json（见实战节）。

### 中间件概念

中间件是包裹在路由处理前后的横切逻辑（鉴权、日志、CORS）。Crow 通过继承 `ILocalMiddleware` 实现：

```cpp
struct RequestLogger : crow::ILocalMiddleware {
    struct context {};                          // 每请求共享的上下文对象

    void before_handle(crow::request& req, crow::response& res, context&) {
        CROW_LOG_INFO << "--> " << req.method << " " << req.raw_url;
    }
    void after_handle(crow::request&, crow::response& res, context&) {
        CROW_LOG_INFO << "<-- status " << res.code;
    }
};

// 挂载到具体路由：App<RequestLogger> 声明中间件栈
crow::App<RequestLogger> app;
CROW_MIDDLEWARES(app, RequestLogger)
CROW_ROUTE(app, "/protected")([]{
    return "secret data";
});
```asm

与 Spring 的 Filter/Interceptor 概念完全对应，只是没有注解和反射，全靠模板参数静态组装——零运行时开销。

### 静态文件服务

```cpp
CROW_ROUTE(app, "/static/<string>")
([](const std::string& filename){
    auto path = std::string("assets/") + filename;

    // 安全检查：拒绝 ../ 目录穿越攻击
    if (filename.find("..") != std::string::npos) {
        return crow::response(403);
    }
    std::ifstream in(path, std::ios::binary);
    if (!in) return crow::response(404);
    std::stringstream ss; ss << in.rdbuf();
    return crow::response{ss.str()};
});
```asm

生产环境更常见的分工是：C++ 只提供 API，静态资源交给 Nginx/CDN——动静分离让 C++ 进程专注计算。

---

## 实践

实战目标：用 **Crow + nlohmann-json** 实现一套 Todo REST API（内存存储），覆盖完整 CRUD。

### 数据模型与存储层

- todo-api/
  - include/todo_store.h （内存存储：id 到 Todo 的映射）
  - src/main.cpp （全部路由）
  - crow_all.h nlohmann/json.hpp （第三方头文件）

```cpp
// include/todo_store.h —— 用 unordered_map 做内存存储（对照 [[c语言教程/3数据结构/05_哈希表|哈希表]] 原理）
#pragma once
#include <unordered_map>
#include <vector>
#include <mutex>
#include <optional>

struct Todo {
    long   id;
    std::string title;
    bool   done;
};

class TodoStore {
public:
    TodoStore() : next_id_(1) {}

    // 新建：加锁保护 next_id_ 与 map 的一致性（Web 服务必然多线程）
    long create(const std::string& title) {
        std::lock_guard<std::mutex> lk(m_);
        long id = next_id_++;
        items_[id] = Todo{id, title, false};
        return id;
    }

    std::optional<Todo> get(long id) const {
        std::lock_guard<std::mutex> lk(m_);
        auto it = items_.find(id);
        if (it == items_.end()) return std::nullopt;   // 未找到返回空可选值
        return it->second;
    }

    bool update(long id, const std::string* title, bool* done) {
        std::lock_guard<std::mutex> lk(m_);
        auto it = items_.find(id);
        if (it == items_.end()) return false;
        if (title) it->second.title = *title;          // 部分更新语义
        if (done)  it->second.done  = *done;
        return true;
    }

    bool remove(long id) {
        std::lock_guard<std::mutex> lk(m_);
        return items_.erase(id) > 0;
    }

    std::vector<Todo> all() const {
        std::lock_guard<std::mutex> lk(m_);
        std::vector<Todo> v;
        for (auto& [id, t] : items_) v.push_back(t);
        return v;
    }

private:
    mutable std::mutex m_;
    std::unordered_map<long, Todo> items_;
    long next_id_;
};
```asm

### 路由层：完整 CRUD

```cpp
// src/main.cpp
#include "crow.h"
#include <nlohmann/json.hpp>
#include "todo_store.h"

using nlohmann::json;

static json to_json(const Todo& t) {                 // 领域对象转 JSON
    return json{{"id", t.id}, {"title", t.title}, {"done", t.done}};
}

int main() {
    crow::SimpleApp app;
    static TodoStore store;

    // ---- POST /todos 创建 ----
    CROW_ROUTE(app, "/todos").methods("POST"_method)
    ([](const crow::request& req) {
        try {
            auto j = json::parse(req.body);          // 解析失败抛异常
            long id = store.create(j.at("title").get<std::string>());
            crow::response res(201, to_json(store.get(id).value()).dump());
            res.set_header("Content-Type", "application/json");
            return res;
        } catch (...) {
            return crow::response(400, "{\"error\":\"invalid body\"}");
        }
    });

    // ---- GET /todos 列表 ----
    CROW_ROUTE(app, "/todos")([] {
        json arr = json::array();
        for (auto& t : store.all()) arr.push_back(to_json(t));
        crow::response res(arr.dump());
        res.set_header("Content-Type", "application/json");
        return res;
    });

    // ---- GET /todos/<id> 单查 ----
    CROW_ROUTE(app, "/todos/<long>")([](long id) {
        auto t = store.get(id);
        if (!t) return crow::response(404, "{\"error\":\"not found\"}");
        return crow::response(to_json(t.value()).dump());
    });

    // ---- PUT /todos/<id> 更新 ----
    CROW_ROUTE(app, "/todos/<long>").methods("PUT"_method)
    ([](const crow::request& req, long id) {
        try {
            auto j = json::parse(req.body);
            std::string title = j.value("title", "");       // 可选字段兜底
            bool done = j.value("done", false);
            bool ok = store.update(id,
                        j.contains("title") ? &title : nullptr,
                        j.contains("done") ? &done : nullptr);
            return ok ? crow::response(200) : crow::response(404);
        } catch (...) {
            return crow::response(400);
        }
    });

    // ---- DELETE /todos/<id> 删除 ----
    CROW_ROUTE(app, "/todos/<long>").methods("DELETE"_method)
    ([](long id) {
        return store.remove(id) ? crow::response(204)
                                : crow::response(404);
    });

    app.port(18080).multithreaded().run();
}
```cpp

验证一轮完整生命周期：

```bash
curl -X POST localhost:18080/todos -d '{"title":"buy milk"}'
curl localhost:18080/todos
curl -X PUT localhost:18080/todos/1 -d '{"done":true}'
curl -X DELETE localhost:18080/todos/1
```cpp

### cpp-httplib 极简对照版

同一个"列表查询"接口在 cpp-httplib 里长这样，感受一下更原始的风格：

```cpp
#include <httplib.h>

int main() {
    httplib::Server svr;
    svr.Get("/todos", [](const httplib::Request& req, httplib::Response& res) {
        res.set_content("[{\"id\":1,\"title\":\"buy milk\",\"done\":false}]",
                        "application/json");
    });
    svr.listen("0.0.0.0", 18081);      // 没有 JSON 类型、没有路径参数语法，
}                                       // 一切都要手写：解析、序列化、状态码
```cpp

cpp-httplib 定位是"嵌入式 HTTP 能力"（常被塞进桌面软件做本地回环接口），当 Web 框架用会缺路由参数、中间件这些基础设施——这也反衬出 Crow 的甜点位。

### ab/wrk 压测思路

```bash
ab -n 100000 -c 200 http://localhost:18080/todos     # 总数10万 并发200
wrk -t8 -c256 -d30s http://localhost:18080/todos     # 8线程 256连接 持续30秒
```cpp

关注三个数字而非单一 QPS：

| 指标 | 含义 | 经验参考 |
|------|------|---------|
| Requests/sec | 吞吐 | Crow 单机可达十万级（简单路由） |
| Latency P99 | 尾延迟 | C++ 优势所在，通常远低于带 GC 运行时 |
| Non-2xx rate | 错误率 | 高并发下非零说明连接队列/线程池配置有问题 |

压测纪律：先确认服务端日志级别关到 warn（同步刷盘日志是吞吐杀手）；客户端机与服务端分开部署，避免自测自。

### 开发效率对比总结

与 [[java/3工程化/07_Spring MVC|Spring MVC]] 和 Python Flask 对比同一 CRUD 任务：

| 维度 | Spring MVC | Flask | Crow |
|------|-----------|-------|------|
| 起步代码量 | 注解+启动类，中等 | 极少 | 少但要管编译 |
| 生态（ORM/鉴权/文档） | 极其成熟 | 成熟 | 稀缺，多为手搓 |
| 内存占用/GC 停顿 | JVM 数百 MB 起 | 低但有解释器开销 | 几 MB，零停顿 |
| P99 尾延迟 | 毫秒级 | 十毫秒级 | 微秒级可达 |
| 团队维护门槛 | 低 | 低 | 高 |

何时值得用 C++ 写 Web：**性能是产品核心竞争力**（网关、交易、实时引擎）或**运行环境苛刻**（嵌入式设备）。纯业务 CRUD 选它属于用牛刀切菜还容易伤手。

---

## 小结

- C++ Web 的定位不是替代 Spring/Flask，而是守住高性能网关、嵌入式 API、低延迟服务三块阵地；
- Crow 以 header-only 之身提供路由参数、查询串、JSON、中间件全套基础能力，编译即部署；
- REST CRUD 的骨架在任何语言里都一样：存储层加锁保护共享状态，路由层负责解析与状态码；
- 压测看 P99 与错误率而非裸 QPS，动静分离让 C++ 进程只干计算活；
- 技术选型的本质是拿开发效率换运行时性能，想清楚再下场。
