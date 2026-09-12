# 10 服务端 Dart

> 前置知识：[[dart/1入门/09_异步编程|09 异步编程]]、[[dart/2深入/02_Isolate与并发|02 Isolate 与并发]]、[[dart/2深入/06_编译与产物|06 编译与产物]]
> 本章目标：理解用 Dart 写服务端的定位与边界，掌握 shelf 的 Handler/Middleware/Pipeline 模型与 dart_frog 的文件路由，能完成数据库访问、JWT 认证、WebSocket、请求校验与日志，并把服务 Docker 化或用 `dart compile exe` 单文件部署。

## 为什么用 Dart 写服务端

Dart 服务端的核心卖点有三个：**同语言全栈**（Flutter 与后端共享 DTO 与校验逻辑，接口改字段时两边一起编译报错）、**AOT 原生性能**（`dart compile exe` 产出无运行时依赖的单文件，启动毫秒级）、**模型代码复用**（把 DTO 放在共享包里，前后端直接 import）。

与主流后端技术栈对比：

| 维度 | Dart (shelf/dart_frog) | Spring Boot | FastAPI | Express |
|------|------------------------|-------------|---------|---------|
| 语言 | Dart | Java/Kotlin | Python | JS/TS |
| 性能 | AOT 原生，高 | JVM，高 | 中 | 中 |
| 启动速度 | 毫秒级 | 秒级 | 快 | 快 |
| 类型安全 | 强（空安全） | 强 | 可选 | TypeScript 可选 |
| 生态规模 | 小 | 最大 | 大 | 最大 |
| 全栈同语言 | 与 Flutter 共享模型 | 与 Android 共享 | 无 | 与 RN 部分共享 |
| 适合场景 | 中小 API、全栈 Dart 团队 | 大型企业系统 | 数据/AI 服务 | 快速原型 |

Dart 服务端**不适合**的场景也要说清楚：需要大量成熟中间件（消息队列管理台、分布式事务框架）的大型系统、招聘市场上后端 Dart 岗位稀少的团队。把它当作「Flutter 应用的自有后端」或「中小型 API」来定位最合适。

## shelf：Handler / Middleware / Pipeline

shelf 是最底层的 HTTP 库，核心概念只有三个：

- **Handler**：`FutureOr<Response> Function(Request)`，接收请求返回响应
- **Middleware**：接收 Handler 返回新 Handler，用于日志、鉴权、CORS、错误处理
- **Pipeline**：把多个 Middleware 与 Handler 串成一条处理链

```mermaid
flowchart LR
    REQ["HTTP 请求"] --> LOG["logRequests 中间件"]
    LOG --> AUTH["鉴权中间件"]
    AUTH --> ERR["错误处理中间件"]
    ERR --> ROUTER["Router Handler"]
    ROUTER --> RES["HTTP 响应"]
```

完整可运行的 REST 示例：

```dart
// bin/server.dart
import 'dart:convert';
import 'dart:io';
import 'package:shelf/shelf.dart';
import 'package:shelf/shelf_io.dart' as io;
import 'package:shelf_router/shelf_router.dart';

// 演示用内存存储，生产环境替换为数据库
final _todos = <String, Map<String, dynamic>>{};
var _nextId = 1;

Response _json(Object? body, {int status = 200}) => Response(
      status,
      body: jsonEncode(body),
      headers: {'content-type': 'application/json; charset=utf-8'},
    );

Router get router => Router()
  ..get('/health', (Request req) => _json({'status': 'ok'}))
  ..get('/todos', (Request req) => _json(_todos.values.toList()))
  ..post('/todos', (Request req) async {
    final body = jsonDecode(await req.readAsString()) as Map<String, dynamic>;
    final title = body['title'];
    if (title is! String || title.trim().isEmpty) {
      return _json({'error': 'title 不能为空'}, status: 400);
    }
    final id = '${_nextId++}';
    _todos[id] = {'id': id, 'title': title.trim(), 'done': false};
    return _json(_todos[id], status: 201);
  })
  ..get('/todos/<id>', (Request req, String id) {
    final todo = _todos[id];
    return todo == null ? _json({'error': '不存在'}, status: 404) : _json(todo);
  })
  ..delete('/todos/<id>', (Request req, String id) {
    return _todos.remove(id) == null
        ? _json({'error': '不存在'}, status: 404)
        : Response(204);
  });

/// 把未捕获异常统一转成 JSON，避免把堆栈泄漏给客户端
Middleware get jsonErrorMiddleware => (inner) => (request) async {
      try {
        return await inner(request);
      } on FormatException catch (e) {
        return _json({'error': '请求体不是合法 JSON: ${e.message}'}, status: 400);
      } catch (e, stack) {
        stderr.writeln('未捕获异常: $e\n$stack');
        return _json({'error': '服务器内部错误'}, status: 500);
      }
    };

Future<void> main() async {
  final handler = const Pipeline()
      .addMiddleware(logRequests()) // 官方日志中间件
      .addMiddleware(jsonErrorMiddleware)
      .addHandler(router.call);

  final server = await io.serve(handler, InternetAddress.anyIPv4, 8080);
  stdout.writeln('服务已启动: http://localhost:${server.port}');

  // 优雅关闭：收到信号后停止接受新请求，等待在途请求完成
  ProcessSignal.sigint.watch().listen((_) async {
    stdout.writeln('正在关闭...');
    await server.close(force: false);
    exit(0);
  });
}
```

```yaml
# pubspec.yaml
name: todo_server
environment:
  sdk: ^3.4.0
dependencies:
  shelf: ^1.4.1
  shelf_router: ^1.1.4
```

```bash
dart pub get && dart run bin/server.dart
curl -X POST localhost:8080/todos -d '{"title":"写文档"}'
```

## dart_frog：文件即路由

dart_frog 在 shelf 之上提供约定式框架：目录结构就是路由表，每个文件导出一个 `onRequest` 函数。

```bash
dart pub global activate dart_frog_cli
dart_frog create my_api && cd my_api
dart_frog dev            # 热重载开发服务器
```

```text
my_api/
├── routes/
│   ├── index.dart               # GET /
│   ├── _middleware.dart         # 作用于本目录及子目录的中间件
│   ├── todos/
│   │   ├── index.dart           # GET/POST /todos
│   │   ├── [id].dart            # GET/DELETE /todos/<id>
│   │   └── _middleware.dart     # 仅作用于 /todos/*
│   └── ws.dart                  # WebSocket 端点
├── pubspec.yaml
└── server.dart                  # 生成的应用入口
```

```dart
// routes/todos/[id].dart —— 文件名即路径参数
import 'package:dart_frog/dart_frog.dart';

Future<Response> onRequest(RequestContext context, String id) async {
  switch (context.request.method) {
    case HttpMethod.get:
      final todo = await context.read<TodoRepository>().findById(id);
      return todo == null
          ? Response.json(statusCode: 404, body: {'error': '不存在'})
          : Response.json(body: todo.toJson());
    case HttpMethod.delete:
      await context.read<TodoRepository>().delete(id);
      return Response(statusCode: 204);
    default:
      return Response(statusCode: 405); // 方法不允许
  }
}
```

依赖注入用 `context.read<T>()`，在中间件里 `provide`：

```dart
// routes/_middleware.dart
import 'package:dart_frog/dart_frog.dart';

Handler middleware(Handler handler) => handler
    .use(requestLogger()) // dart_frog 内置日志
    .use(provider<TodoRepository>((_) => TodoRepositoryImpl()))
    .use(provider<DbPool>((_) => DbPool.fromEnv()));
```

环境变量用 `Platform.environment` 或 `dart_frog` 的 `.env` 支持，密钥绝不写进代码库。

## 数据库访问

Dart 官方生态没有 ORM 霸主，常见组合是 `postgres` / `mysql` 驱动 + 手写 SQL（或用 `drift` 的服务端模式做类型安全查询）。连接池是必选项：

```dart
// lib/db.dart
import 'package:postgres/postgres.dart';

Pool createPool() => Pool.withEndpoints(
      [Endpoint(
        host: 'localhost',
        port: 5432,
        database: 'app',
        username: 'app',
        password: Platform.environment['DB_PASSWORD']!,
      )],
      settings: const PoolSettings(
        maxConnectionCount: 10,        // 连接池上限
        maxConnectionAge: Duration(minutes: 30),
      ),
    );

Future<List<Map<String, dynamic>>> listTodos(Pool pool) async {
  // 永远用参数化查询，禁止字符串拼接 SQL
  final result = await pool.execute(
    Sql.named('SELECT id, title, done FROM todos ORDER BY id DESC LIMIT @limit'),
    parameters: {'limit': 50},
  );
  return result.map((row) => row.toColumnMap()).toList();
}
```

| 方案 | 类型安全 | 适合 |
|------|----------|------|
| postgres / mysql 驱动 | 手写 SQL，运行时映射 | 需要精确控制 SQL |
| drift（服务端模式） | 编译期检查 | 想要 ORM 的团队 |
| 直接 `Sql.named` + 手写模型 | 靠测试保证 | 小项目 |

## 认证与 JWT

服务端认证的常见做法是登录成功后签发 JWT，后续请求带 `Authorization: Bearer <token>`：

```dart
import 'dart:io';
import 'package:dart_jsonwebtoken/dart_jsonwebtoken.dart';
import 'package:shelf/shelf.dart';

SecretKey get _secret => SecretKey(Platform.environment['JWT_SECRET']!);

/// 登录成功后签发 2 小时有效的 token
String signToken(String userId) => JWT(
      {'sub': userId, 'role': 'user'},
      issuer: 'rootstack',
    ).sign(_secret, expiresIn: const Duration(hours: 2));

/// 鉴权中间件：校验失败一律返回 401，不泄漏具体原因
Middleware authMiddleware() => (inner) => (request) async {
      final header = request.headers['authorization'] ?? '';
      if (!header.startsWith('Bearer ')) {
        return Response(401, body: '{"error":"未登录"}');
      }
      try {
        final payload = JWT.verify(header.substring(7), _secret);
        // 把用户信息注入请求上下文，供后续 Handler 读取
        return inner(request.change(context: {'userId': payload.payload['sub']}));
      } on JWTException {
        return Response(401, body: '{"error":"登录已过期"}');
      }
    };
```

密码存储用 `bcrypt` 或 `argon2` 包做加盐哈希，绝不存明文或单轮 MD5。

## WebSocket 实时通信

`shelf_web_socket` 把 WebSocket 升级交给一个 Handler：

```dart
import 'package:shelf_web_socket/shelf_web_socket.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

// 维护所有在线连接，实现简易广播
final _clients = <WebSocketChannel>{};

Handler get wsHandler => webSocketHandler((WebSocketChannel socket, _) {
      _clients.add(socket);
      socket.stream.listen(
        (message) {
          for (final client in _clients) {
            client.sink.add('广播: $message'); // 转发给所有客户端
          }
        },
        onDone: () => _clients.remove(socket), // 断开时清理
        onError: (_) => _clients.remove(socket),
      );
    });

// 注册到 Router：router.get('/ws', wsHandler);
```

生产环境要做心跳检测（定时 ping）清理死连接，并按房间/主题分组广播，而不是全量广播。

## 请求校验、错误处理与日志

- 校验放进入口：类型、长度、枚举值全部检查，失败返回 400 与字段级错误信息
- 业务异常定义自己的 `AppException`，中间件统一映射为 HTTP 状态码
- 日志用结构化 JSON（`package:logging` + 自定义 Formatter），包含请求 ID、耗时、状态码，便于接入 ELK
- 不要把 `stackTrace` 返回给客户端，只在服务端日志记录

```dart
class AppException implements Exception {
  final int status;
  final String message;
  AppException(this.status, this.message);
}

Middleware errorMapper() => (inner) => (request) async {
      try {
        return await inner(request);
      } on AppException catch (e) {
        return Response(e.status,
            body: '{"error":"${e.message}"}',
            headers: {'content-type': 'application/json'});
      }
    };
```

## Docker 化与单文件部署

`dart compile exe` 产出的是自包含原生可执行文件，镜像可以做到很小：

```dockerfile
# 构建阶段：安装依赖并 AOT 编译
FROM dart:stable AS build
WORKDIR /app
COPY pubspec.* ./
RUN dart pub get
COPY . .
RUN dart pub get --offline && dart compile exe bin/server.dart -o bin/server

# 运行阶段：scratch 镜像，只包含可执行文件与根证书
FROM scratch
COPY --from=build /runtime/ /
COPY --from=build /app/bin/server /app/bin/
EXPOSE 8080
CMD ["/app/bin/server"]
```

```bash
docker build -t todo-server .
docker run -p 8080:8080 -e JWT_SECRET=xxx -e DB_PASSWORD=yyy todo-server

# 不用容器时直接分发单文件
dart compile exe bin/server.dart -o build/todo-server
./build/todo-server
```

镜像体积通常只有几十 MB，远小于 JVM 服务的几百 MB；冷启动毫秒级，适合 Serverless 与快速扩缩容。

## 性能与 Isolate

Dart 服务端默认只用一个 Isolate（一个 CPU 核）。压榨多核有两种方式：

- **共享端口多 Isolate**：每个 Isolate 都 `HttpServer.bind(..., shared: true)` 绑定同一端口，内核负责分发连接
- **CPU 密集任务放 `Isolate.run`**：图片处理、加解密、大 JSON 解析不要阻塞事件循环

```dart
// 用满 CPU 核数启动多个服务实例
Future<void> main() async {
  final cores = Platform.numberOfProcessors;
  for (var i = 0; i < cores; i++) {
    await Isolate.spawn(_startServer, null);
  }
}

Future<void> _startServer(void _) async {
  final server = await HttpServer.bind(InternetAddress.anyIPv4, 8080, shared: true);
  // ...绑定 shelf handler 并监听
}
```

大多数 Web API 是 IO 密集型，单 Isolate 的异步模型已能支撑可观吞吐；先压测再优化，不要过早多 Isolate。

## 常见坑

1. **连接池泄漏**：事务忘记 commit/rollback、异常路径没归还连接，压力上来后池耗尽，表现为请求全部超时。用 `try/finally` 保证归还。
2. **时区混乱**：数据库存 UTC，API 返回 UTC 并带 `Z`，客户端负责本地化。服务端混用本地时间会在跨时区时出错。
3. **不做优雅关闭**：直接 `kill -9` 会丢掉在途请求。监听 SIGTERM/SIGINT，先 `server.close(force: false)` 再关闭连接池。
4. **CPU 任务阻塞事件循环**：在大 JSON 解析或图片处理期间，所有请求都被卡住。放 `Isolate.run`。
5. **密钥进代码库**：JWT_SECRET、数据库密码一律走环境变量，`.env` 加入 `.gitignore`。
6. **SQL 字符串拼接**：哪怕参数来自内部也要用 `Sql.named`，注入漏洞往往从「这里应该安全」开始。
7. **错误堆栈返回客户端**：泄漏文件路径与依赖版本，是常见的信息泄露渠道。

## 本章小结

- Dart 服务端的定位是「全栈同语言 + AOT 高性能」，适合中小 API 与 Flutter 应用的自有后端，不适合需要庞大中间件生态的大型系统
- shelf 的核心是 Handler、Middleware、Pipeline 三件套，Router 负责路径分发
- dart_frog 用文件即路由与 `context.read` 依赖注入，把 shelf 的样板代码降到最低
- 数据库访问优先参数化查询与连接池；drift 服务端模式可提供编译期类型安全
- 认证用 JWT + 密码哈希，鉴权逻辑放中间件；WebSocket 用于实时推送并注意心跳与分组
- 校验、错误映射、结构化日志是服务端的三条基本纪律
- `dart compile exe` 单文件部署，Docker 用多阶段构建 + scratch 镜像，体积小、启动快
- 单 Isolate 适合 IO 密集型服务，多核用共享端口多 Isolate 或 `Isolate.run` 处理 CPU 任务

---

- 返回目录：[[dart/dart目录|Dart 教程目录]]

---

## 练习

1. **dart_frog CRUD API（验收：curl 能完成增删改查）**
   用 `dart_frog create` 创建项目，实现 `/todos` 的列表、创建、查询、删除四个端点；创建时校验 `title` 非空且不超过 100 字，错误返回 400 与 JSON 错误信息；用内存存储即可，但 Repository 要通过 `provider` 注入。

2. **JWT 认证（验收：无 token 返回 401，正确 token 返回数据）**
   增加 `/login` 端点（用户名密码从环境变量读取），签发 JWT；给 `/todos` 加上鉴权中间件；用 curl 分别验证无 token、伪造 token、正确 token 三种情况的状态码。

3. **容器化与优雅关闭（验收：`docker run` 后接口可访问，Ctrl+C 无请求丢失）**
   编写多阶段 Dockerfile，构建并运行镜像；给服务加上 SIGTERM 处理，用 `docker stop` 验证进程能在收到信号后完成在途请求再退出（日志中打印关闭过程）。

4. **WebSocket 广播（验收：两个客户端能互相收到消息）**
   增加 `/ws` 端点，客户端连接后发送的消息广播给所有连接；用 `websocat` 或两个浏览器标签验证，并实现断开时从客户端集合移除，避免内存泄漏。
