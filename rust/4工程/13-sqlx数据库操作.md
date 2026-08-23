# 13 - sqlx 数据库操作

## 原理

### Rust 数据库生态地图

Rust 没有类似 JDBC 的官方统一规范，数据库访问分三个流派：

| 库 | 定位 | 编译期校验 | ORM 程度 | 学习曲线 |
|----|------|:--------:|:-------:|---------|
| **sqlx** | 异步原生 SQL 工具箱 | 有（query! 宏校验 SQL） | 无，纯 SQL | 低-中 |
| diesel | 同步 ORM 老牌方案 | 有（DSL 类型安全） | 高（DSL 即 ORM） | 中-高 |
| sea-orm | 异步 ORM（基于 sqlx） | 无（运行时为主） | 高（ActiveRecord 风格） | 中 |

三者关系一句话：**diesel 用类型系统重造了 SQL，sea-orm 给 sqlx 穿上 ORM 外衣，
sqlx 本身坚持"写原生 SQL"**。

### sqlx 的定位

sqlx 不是传统 ORM——没有 Model 类、没有自动建表、没有关联加载。
它提供三样东西：

1. **异步连接池**：`PgPool`/`MySqlPool`/`SqlitePool`，开箱即用；
2. **query/query_as 宏**：手写 SQL，结果自动映射到 Rust 结构体；
3. **编译期 SQL 校验**：`query!` 宏在 `cargo check` 时真的连库执行
   `PREPARE`，SQL 写错、列名写错、类型不匹配直接编译失败。

对照 Java 世界：sqlx 大致是 "JDBC + JdbcTemplate + 编译期 SQL 检查" 的合体，
而不是 Hibernate/JPA。想要 ActiveRecord 式 ORM 的体验可看 sea-orm，
但理解 sqlx 是理解 Rust 数据访问的必修课。

### 编译期校验的工作原理

```mermaid
flowchart LR
    A[cargo build] --> B{.sqlx 缓存目录存在?}
    B -->|存在| C[离线比对缓存元数据<br/>无需真实数据库]
    B -->|不存在| D[读取 DATABASE_URL<br/>连接数据库 PREPARE]
    C --> E[校验通过则编译<br/>失败则编译报错]
    D --> E
```

`cargo sqlx prepare` 会把每条宏内 SQL 的元数据（列名/类型）序列化到 `.sqlx` 目录并随代码入库。
CI 和其他开发者拿到仓库后无需真库即可编译——这是 sqlx 工程化的关键设计。

---

## 语法

### 安装与依赖

```toml
[dependencies]
tokio = { version = "1", features = ["full"] }
# runtime-async-std 与 tls 选型按目标平台调整；postgres/mysql/sqlite 按需开启
sqlx = { version = "0.8", features = [
    "runtime-tokio",
    "tls-rustls",
    "postgres",
    "chrono",    # 时间类型支持
    "migrate",   # 迁移工具支持
] }
```

命令行工具独立安装（不进 Cargo.toml）：

```bash
cargo install sqlx-cli --no-default-features --features rustls,postgres
```

### 建立连接：PgPool / MySqlPool

连接串通过 `DATABASE_URL` 环境变量传入（12-factor 应用惯例）：

```bash
export DATABASE_URL=postgres://user:pass@localhost:5432/mydb
export DATABASE_URL=mysql://user:pass@localhost:3306/mydb
```

```rust
use std::time::Duration;

#[tokio::main]
async fn main() -> Result<(), sqlx::Error> {
    // 从环境变量读连接串创建池；池内部管理 N 条连接，Arc 包装可随意 Clone
    let pool = sqlx::postgres::PgPoolOptions::new()
        .max_connections(10)                       // 最大并发连接数
        .acquire_timeout(Duration::from_secs(3))   // 拿不到连接的最长等待
        .connect(&std::env::var("DATABASE_URL").unwrap())
        .await?;

    // SELECT 1 探活，验证连通性
    let ok: (i32,) = sqlx::query_as("SELECT 1").fetch_one(&pool).await?;
    println!("数据库连通: {}", ok.0);
    Ok(())
}
```

> MySQL 用 `MySqlPoolOptions` + `mysql://` 连接串，API 完全同构，下文以 PostgreSQL 为准。

### query / query_as 与 FromRow

三种取数姿势，从裸到类型化：

```rust
use sqlx::Row;

async fn demo(pool: &sqlx::PgPool) -> Result<(), sqlx::Error> {
    // 1) query + Row 手动取列：灵活但啰嗦，适合动态列场景
    let row = sqlx::query("SELECT id, name FROM users WHERE id = $1")
        .bind(1i64)                          // 参数绑定，$1 占位
        .fetch_one(pool)
        .await?;
    let name: String = row.try_get("name")?;

    // 2) query_as + 元组：轻量场景不想定义结构体时
    let (id, name): (i64, String) =
        sqlx::query_as("SELECT id, name FROM users WHERE id = $1")
            .bind(1i64)
            .fetch_one(pool)
            .await?;
    let _ = (id, name);

    // 3) query_as + 结构体：主力写法，结构体 derive FromRow 自动映射列名
    let user = fetch_user(pool, 1).await?;
    println!("{user:?}");
    Ok(())
}

// 字段名与数据库列名一一对应；derive(FromRow) 生成列到字段的映射代码
#[derive(Debug, sqlx::FromRow)]
struct User {
    id: i64,
    name: String,
    email: String,
}

async fn fetch_user(pool: &sqlx::PgPool, uid: i64) -> Result<User, sqlx::Error> {
    sqlx::query_as::<_, User>("SELECT id, name, email FROM users WHERE id = $1")
        .bind(uid)
        .fetch_one(pool)   // 无记录返回 RowNotFound 错误
        .await
}
```

fetch 家族速查：

| 方法 | 行数语义 | 返回 |
|------|---------|------|
| `fetch_one` | 恰好一行 | 无行/多行报错 |
| `fetch_optional` | 0 或 1 行 | `Option<T>`，查询可能无结果时必用 |
| `fetch_all` | 多行 | `Vec<T>` |

### query! 宏与编译期校验

把上面的字符串 SQL 换成宏，错误提前到编译期：

```rust
// query! 直接返回匿名结构体；SQL 与 schema 不匹配时 cargo check 直接失败
async fn get_name(pool: &sqlx::PgPool, uid: i64) -> Option<String> {
    // 宏会检查：users 表存在、name 列存在且为 TEXT、$1 类型匹配 BIGINT
    sqlx::query!("SELECT name FROM users WHERE id = $1", uid)
        .fetch_optional(pool)
        .await
        .map(|row| row.name)
}

// query_as! 映射到指定结构体（不需要 FromRow derive）
async fn count_users(pool: &sqlx::PgPool) -> i64 {
    // 注意：PostgreSQL 的 COUNT 返回 int8(i64)，宏会精确推断
    sqlx::query!("SELECT COUNT(*) AS n FROM users")
        .fetch_one(pool)
        .await
        .unwrap()
        .n
}
```

生成离线缓存（一次性，需本地有库）：

```bash
cargo sqlx prepare          # 扫描所有 query! 宏，写入 .sqlx/
git add .sqlx               # 提交进仓库，CI 无需连库
```

CI 中设置 `SQLX_OFFLINE=true` 强制走缓存，杜绝环境差异导致的意外联网。

### 参数绑定防注入

永远不要用 format! 拼 SQL——sqlx 的 `.bind()` 走预编译参数通道，
值只作为数据传输，不可能被解析成 SQL 片段：

```rust
// 危险写法（仅示意，切勿使用）：用户输入直接拼接
// let sql = format!("SELECT * FROM users WHERE name = '{}'", input); // 注入风险！

// 正确写法：占位符 + bind，input 无论包含什么字符都只是字符串值
let safe = "' OR '1'='1"; // 经典注入载荷
let rows = sqlx::query("SELECT * FROM users WHERE name = $1")
    .bind(safe) // 作为整体参数传入，等价于查找名为这个奇怪串的用户
    .fetch_all(pool)
    .await?;
let _ = rows;
```

对应 JDBC 的 `PreparedStatement`，但 sqlx 在编译期还能额外校验参数类型。

### 事务 begin / commit / rollback

事务的核心是 `Transaction` 类型接管连接，提交或回滚后归还：

```rust
async fn transfer_points(
    pool: &sqlx::PgPool,
    from_id: i64,
    to_id: i64,
    points: i64,
) -> Result<(), sqlx::Error> {
    // 开启事务：从池中取出一条连接并标记事务开始
    let mut tx = pool.begin().await?;

    sqlx::query("UPDATE accounts SET points = points - $1 WHERE id = $2 AND points >= $1")
        .bind(points)
        .bind(from_id)
        .execute(&mut *tx)   // 注意传 &mut *tx 而不是 pool
        .await?;

    sqlx::query("UPDATE accounts SET points = points + $1 WHERE id = $2")
        .bind(points)
        .bind(to_id)
        .execute(&mut *tx)
        .await?;

    tx.commit().await?;      // 显式提交；若中途 ? 出错提前返回，
                             // Transaction 被 Drop 时自动回滚
    Ok(())
}
```

记忆点：**Drop 即回滚**。Rust 所有权保证事务对象离开作用域必然回滚，
不存在"忘记 commit 导致悬挂事务"这类 Java 里常见的泄漏。

---

## 实践

### 迁移管理：sqlx migrate

迁移文件按 `<版本号>_<描述>.sql` 命名，版本号用时间戳保证全局有序：

```bash
mkdir -p migrations
sqlx migrate add create_users_table     # 生成 migrations/20240101090000_create_users_table.sql
sqlx migrate run                        # 执行未应用的迁移
sqlx migrate info                       # 查看迁移状态
```

```sql
-- migrations/20240101090000_create_users_table.sql
CREATE TABLE IF NOT EXISTS users (
    id         BIGSERIAL PRIMARY KEY,       -- 自增主键
    name       TEXT NOT NULL,
    email      TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_users_email ON users (email); -- 邮箱查询索引
```

程序启动时也可以代码内执行迁移，保证部署即就绪：

```rust
// 幂等：sqlx 记录已应用版本，重复调用只跑新增迁移
sqlx::migrate!("./migrations").run(&pool).await?;
```

### users 表完整 CRUD 示例

一个可直接嵌入服务的仓储模块，覆盖增删改查全流程：

```rust
use serde::{Deserialize, Serialize};
use sqlx::PgPool;

/// 数据库实体：同时承担请求体和响应体角色（小项目够用）
#[derive(Debug, Clone, sqlx::FromRow, Serialize, Deserialize)]
pub struct User {
    pub id: i64,
    pub name: String,
    pub email: String,
}

/// 创建用户的入参：不含 id（由数据库生成）
#[derive(Debug, Deserialize)]
pub struct NewUser {
    pub name: String,
    pub email: String,
}

/// 新建用户，返回带自增 id 的完整实体
pub async fn insert_user(pool: &PgPool, u: NewUser) -> Result<User, sqlx::Error> {
    // INSERT ... RETURNING 是 PG 特色：插入同时拿回生成的列，免二次查询
    let user = sqlx::query_as::<_, User>(
        "INSERT INTO users (name, email) VALUES ($1, $2)
         RETURNING id, name, email",
    )
    .bind(u.name)
    .bind(u.email)
    .fetch_one(pool)
    .await?;
    Ok(user)
}

/// 按 id 查询；查不到返回 None 而非报错
pub async fn find_user(pool: &PgPool, id: i64) -> Result<Option<User>, sqlx::Error> {
    sqlx::query_as::<_, User>("SELECT id, name, email FROM users WHERE id = $1")
        .bind(id)
        .fetch_optional(pool)
        .await
}

/// 全量列表（生产中应加分页 LIMIT/OFFSET）
pub async fn list_users(pool: &PgPool) -> Result<Vec<User>, sqlx::Error> {
    sqlx::query_as::<_, User>(
        "SELECT id, name, email FROM users ORDER BY id LIMIT 100",
    )
    .fetch_all(pool)
    .await
}

/// 更新邮箱；返回受影响行数用于判断目标是否存在
pub async fn update_email(
    pool: &PgPool,
    id: i64,
    email: &str,
) -> Result<u64, sqlx::Error> {
    let result = sqlx::query("UPDATE users SET email = $1 WHERE id = $2")
        .bind(email)
        .bind(id)
        .execute(pool)
        .await?;
    Ok(result.rows_affected()) // 0 表示没找到该 id
}

/// 删除用户
pub async fn delete_user(pool: &PgPool, id: i64) -> Result<bool, sqlx::Error> {
    let result = sqlx::query("DELETE FROM users WHERE id = $1")
        .bind(id)
        .execute(pool)
        .await?;
    Ok(result.rows_affected() > 0)
}
```

### 与 axum 集成：State 注入 Pool

axum 章（[[rust/3实践/07-axum-Web服务开发|07-axum Web 服务开发]]）的 Todo API
把 HashMap 换成 PgPool 即完成持久化升级：

```rust
use std::sync::Arc;

// AppState 只持有一个池；PgPool 内部自带并发控制，无需再套锁
#[derive(Clone)]
struct AppState {
    db: Arc<PgPool>,
}

// handler：复用上面的仓储函数，错误统一转 AppError
async fn get_user_handler(
    State(state): State<AppState>,
    Path(id): Path<i64>,
) -> Result<Json<User>, StatusCode> {
    match crate::repo::find_user(&state.db, id).await {
        Ok(Some(user)) => Ok(Json(user)),
        Ok(None) => Err(StatusCode::NOT_FOUND),
        Err(e) => {
            tracing::error!("db error: {e}");
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let pool = Arc::new(
        sqlx::postgres::PgPoolOptions::new()
            .max_connections(10)
            .connect(&std::env::var("DATABASE_URL").unwrap())
            .await?,
    );
    sqlx::migrate!("./migrations").run(pool.as_ref()).await?; // 启动即迁移

    let app = axum::Router::new()
        .route("/users/{id}", axum::routing::get(get_user_handler))
        .with_state(AppState { db: pool });

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await?;
    axum::serve(listener, app).await?;
    Ok(())
}
```

对照 Spring Data JPA：JPA 用接口 + 方法名推导 SQL，sqlx 让你亲手写 SQL 但换来
编译期校验和零反射开销——一个是隐藏 SQL，一个是验证 SQL，哲学截然相反。

---

## 小结

- **生态选型**：sqlx（原生 SQL）/ diesel（DSL 型 ORM）/ sea-orm（异步 ORM），按团队口味取舍；
- **连接**：`DATABASE_URL` + PoolOptions，池可 Clone、自带并发管理；
- **取数**：`fetch_one/fetch_optional/fetch_all` 三兄弟，`FromRow` 自动映射；
- **编译期校验**：`query!` 宏 + `cargo sqlx prepare` 离线缓存，CI 设 `SQLX_OFFLINE=true`；
- **事务**：`begin` 取连接、`commit` 提交、Drop 自动回滚；
- **迁移**：时间戳命名 + `sqlx::migrate!` 启动时幂等执行。

下一步建议：给本章 users 服务补上集成测试（用 `#[sqlx::test]` 自动起临时库），
并接入 [[rust/4工程/14-Cargo-workspace多包管理|Cargo workspace]] 把 repo 层拆成独立 crate。
