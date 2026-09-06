# 13 - sqlx 

## 

### Rust 

Rust  JDBC 

|  |  |  | ORM  |  |
|----|------|:--------:|:-------:|---------|
| **sqlx** |  SQL  | query!  SQL |  SQL | - |
| diesel |  ORM  | DSL  | DSL  ORM | - |
| sea-orm |  ORM sqlx |  | ActiveRecord  |  |

**diesel  SQLsea-orm  sqlx  ORM 
sqlx " SQL"**

### sqlx 

sqlx  ORM—— Model 


1. ****`PgPool`/`MySqlPool`/`SqlitePool`
2. **query/query_as ** SQL Rust 
3. ** SQL **`query!`  `cargo check` 
   `PREPARE`SQL 

 Java sqlx  "JDBC + JdbcTemplate +  SQL " 
 Hibernate/JPA ActiveRecord  ORM  sea-orm
 sqlx  Rust 

### 

```mermaid
flowchart LR
    A[cargo build] --> B{.sqlx ?}
    B -->|| C[<br/>]
    B -->|| D[ DATABASE_URL<br/> PREPARE]
    C --> E[<br/>]
    D --> E
```

`cargo sqlx prepare`  SQL / `.sqlx` 
CI —— sqlx 

---

## 

### 

```toml
[dependencies]
tokio = { version = "1", features = ["full"] }
# runtime-async-std  tls postgres/mysql/sqlite 
sqlx = { version = "0.8", features = [
    "runtime-tokio",
    "tls-rustls",
    "postgres",
    "chrono",    # 
    "migrate",   # 
] }
```

 Cargo.toml

```bash
cargo install sqlx-cli --no-default-features --features rustls,postgres
```

### PgPool / MySqlPool

 `DATABASE_URL` 12-factor 

```bash
export DATABASE_URL=postgres://user:pass@localhost:5432/mydb
export DATABASE_URL=mysql://user:pass@localhost:3306/mydb
```

```rust
use std::time::Duration;

#[tokio::main]
async fn main() -> Result<(), sqlx::Error> {
    //  N Arc  Clone
    let pool = sqlx::postgres::PgPoolOptions::new()
        .max_connections(10)                       // 
        .acquire_timeout(Duration::from_secs(3))   // 
        .connect(&std::env::var("DATABASE_URL").unwrap())
        .await?;

    // SELECT 1 
    let ok: (i32,) = sqlx::query_as("SELECT 1").fetch_one(&pool).await?;
    println!(": {}", ok.0);
    Ok(())
}
```

> MySQL  `MySqlPoolOptions` + `mysql://` API  PostgreSQL 

### query / query_as  FromRow



```rust
use sqlx::Row;

async fn demo(pool: &sqlx::PgPool) -> Result<(), sqlx::Error> {
    // 1) query + Row 
    let row = sqlx::query("SELECT id, name FROM users WHERE id = $1")
        .bind(1i64)                          // $1 
        .fetch_one(pool)
        .await?;
    let name: String = row.try_get("name")?;

    // 2) query_as + 
    let (id, name): (i64, String) =
        sqlx::query_as("SELECT id, name FROM users WHERE id = $1")
            .bind(1i64)
            .fetch_one(pool)
            .await?;
    let _ = (id, name);

    // 3) query_as +  derive FromRow 
    let user = fetch_user(pool, 1).await?;
    println!("{user:?}");
    Ok(())
}

// derive(FromRow) 
#[derive(Debug, sqlx::FromRow)]
struct User {
    id: i64,
    name: String,
    email: String,
}

async fn fetch_user(pool: &sqlx::PgPool, uid: i64) -> Result<User, sqlx::Error> {
    sqlx::query_as::<_, User>("SELECT id, name, email FROM users WHERE id = $1")
        .bind(uid)
        .fetch_one(pool)   //  RowNotFound 
        .await
}
```

fetch 

|  |  |  |
|------|---------|------|
| `fetch_one` |  | / |
| `fetch_optional` | 0  1  | `Option<T>` |
| `fetch_all` |  | `Vec<T>` |

### query! 

 SQL 

```rust
// query! SQL  schema  cargo check 
async fn get_name(pool: &sqlx::PgPool, uid: i64) -> Option<String> {
    // users name  TEXT$1  BIGINT
    sqlx::query!("SELECT name FROM users WHERE id = $1", uid)
        .fetch_optional(pool)
        .await
        .map(|row| row.name)
}

// query_as!  FromRow derive
async fn count_users(pool: &sqlx::PgPool) -> i64 {
    // PostgreSQL  COUNT  int8(i64)
    sqlx::query!("SELECT COUNT(*) AS n FROM users")
        .fetch_one(pool)
        .await
        .unwrap()
        .n
}
```



```bash
cargo sqlx prepare          #  query!  .sqlx/
git add .sqlx               # CI 
```

CI  `SQLX_OFFLINE=true` 

### 

 format!  SQL——sqlx  `.bind()` 
 SQL 

```rust
// 
// let sql = format!("SELECT * FROM users WHERE name = '{}'", input); // 

//  + bindinput 
let safe = "' OR '1'='1"; // 
let rows = sqlx::query("SELECT * FROM users WHERE name = $1")
    .bind(safe) // 
    .fetch_all(pool)
    .await?;
let _ = rows;
```

 JDBC  `PreparedStatement` sqlx 

###  begin / commit / rollback

 `Transaction` 

```rust
async fn transfer_points(
    pool: &sqlx::PgPool,
    from_id: i64,
    to_id: i64,
    points: i64,
) -> Result<(), sqlx::Error> {
    // 
    let mut tx = pool.begin().await?;

    sqlx::query("UPDATE accounts SET points = points - $1 WHERE id = $2 AND points >= $1")
        .bind(points)
        .bind(from_id)
        .execute(&mut *tx)   //  &mut *tx  pool
        .await?;

    sqlx::query("UPDATE accounts SET points = points + $1 WHERE id = $2")
        .bind(points)
        .bind(to_id)
        .execute(&mut *tx)
        .await?;

    tx.commit().await?;      //  ? 
                             // Transaction  Drop 
    Ok(())
}
```

**Drop **Rust 
" commit " Java 

---

## 

### sqlx migrate

 `<>_<>.sql` 

```bash
mkdir -p migrations
sqlx migrate add create_users_table     #  migrations/20240101090000_create_users_table.sql
sqlx migrate run                        # 
sqlx migrate info                       # 
```

```sql
-- migrations/20240101090000_create_users_table.sql
CREATE TABLE IF NOT EXISTS users (
    id         BIGSERIAL PRIMARY KEY,       -- 
    name       TEXT NOT NULL,
    email      TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_users_email ON users (email); -- 
```



```rust
// sqlx 
sqlx::migrate!("./migrations").run(&pool).await?;
```

### users  CRUD 



```rust
use serde::{Deserialize, Serialize};
use sqlx::PgPool;

/// 
#[derive(Debug, Clone, sqlx::FromRow, Serialize, Deserialize)]
pub struct User {
    pub id: i64,
    pub name: String,
    pub email: String,
}

///  id
#[derive(Debug, Deserialize)]
pub struct NewUser {
    pub name: String,
    pub email: String,
}

///  id 
pub async fn insert_user(pool: &PgPool, u: NewUser) -> Result<User, sqlx::Error> {
    // INSERT ... RETURNING  PG 
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

///  id  None 
pub async fn find_user(pool: &PgPool, id: i64) -> Result<Option<User>, sqlx::Error> {
    sqlx::query_as::<_, User>("SELECT id, name, email FROM users WHERE id = $1")
        .bind(id)
        .fetch_optional(pool)
        .await
}

///  LIMIT/OFFSET
pub async fn list_users(pool: &PgPool) -> Result<Vec<User>, sqlx::Error> {
    sqlx::query_as::<_, User>(
        "SELECT id, name, email FROM users ORDER BY id LIMIT 100",
    )
    .fetch_all(pool)
    .await
}

/// 
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
    Ok(result.rows_affected()) // 0  id
}

/// 
pub async fn delete_user(pool: &PgPool, id: i64) -> Result<bool, sqlx::Error> {
    let result = sqlx::query("DELETE FROM users WHERE id = $1")
        .bind(id)
        .execute(pool)
        .await?;
    Ok(result.rows_affected() > 0)
}
```

###  axum State  Pool

axum [[rust/3/07-axum-Web|07-axum Web ]] Todo API
 HashMap  PgPool 

```rust
use std::sync::Arc;

// AppState PgPool 
#[derive(Clone)]
struct AppState {
    db: Arc<PgPool>,
}

// handler AppError
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
    sqlx::migrate!("./migrations").run(pool.as_ref()).await?; // 

    let app = axum::Router::new()
        .route("/users/{id}", axum::routing::get(get_user_handler))
        .with_state(AppState { db: pool });

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await?;
    axum::serve(listener, app).await?;
    Ok(())
}
```

 Spring Data JPAJPA  +  SQLsqlx  SQL 
—— SQL SQL

---

## 

- ****sqlx SQL/ dieselDSL  ORM/ sea-orm ORM
- ****`DATABASE_URL` + PoolOptions Clone
- ****`fetch_one/fetch_optional/fetch_all` `FromRow` 
- ****`query!`  + `cargo sqlx prepare` CI  `SQLX_OFFLINE=true`
- ****`begin` `commit` Drop 
- **** + `sqlx::migrate!` 

 users  `#[sqlx::test]` 
 [[rust/4/14-Cargo-workspace|Cargo workspace]]  repo  crate
