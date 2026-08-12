# 共享行为：Trait入门

## 原理

Trait 是 Rust 实现多态的核心机制。编译期多态通过泛型 + trait bound（静态分发）实现，等同于单态化后的具体函数调用。运行时多态通过 `&dyn Trait` / `Box<dyn Trait>`（动态分发）实现，在对象中包含两个指针：data pointer + vtable pointer（胖指针，16 字节），vtable 包含所有 trait 方法的函数指针。

静态分发（`impl Trait` / `<T: Trait>`）优点：无虚函数开销，内联优化可能，速度快。缺点：代码膨胀。

动态分发（`dyn Trait`）优点：单份机器码，可存储异构类型。缺点：指针跳转开销，阻止内联。

孤儿规则（Orphan Rule）：为类型实现 trait 时，至少 trait 或类型之一必须在当前 crate 中定义。这保证 trait 实现的全局一致性，防止多个 crate 冲突。

`#[derive]` 是过程宏，在编译时自动生成 trait 实现代码，省去样板代码。

---

## 语法

### 定义与实现

```rust
trait Speak {
 fn speak(&self); // 必须实现
 fn introduce(&self) -> String { // 默认实现
 format!("I can speak!")
 }
}

struct Dog;
impl Speak for Dog {
 fn speak(&self) { println!("Woof!"); }
}
```

### Trait 作为参数

```rust
fn say(animal: &impl Speak) { animal.speak(); }

fn say_twice<T: Speak>(animal: &T) {
 animal.speak();
 animal.speak();
}
```

### Trait 作为返回值

```rust
fn create() -> Box<dyn Speak> {
 Box::new(Dog)
}
```

> `impl Trait` 返回要求所有路径返回同一具体类型。返回不同类型需 `Box<dyn Trait>`。

### derive 自动实现

```rust
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
struct User { name: String, id: u32 }
```

| derive trait | 提供功能 |
|-------------|----------|
| `Debug` | `{:?}` 打印 |
| `Clone` | `.clone()` 深拷贝 |
| `Copy` | 赋值时自动按位复制 |
| `PartialEq` / `Eq` | `==` `!=` 比较 |
| `PartialOrd` / `Ord` | `>` `<` 排序比较 |
| `Hash` | HashMap 键 |
| `Default` | `Default::default()` |

### 孤儿规则

```rust
trait MyTrait { } // 我的 trait
impl MyTrait for i32 { } // 合法：trait 是我的

// impl Display for Vec<i32> { } // 非法：trait 和类型都不是我的
```

### 组合约束

```rust
fn dump<T: Display + Debug>(x: &T) { }
fn print_info(x: &(impl Area + Perimeter)) { }
```

---

## 实践

### 力扣问题

力扣: 力扣排序题 — trait + derive

```rust
#[derive(Debug)]
struct Student { id: u32, grade: u32 }
// 实现 PartialOrd 后使用 sort
```

### AI 自检

1. `impl Trait`（静态分发）与 `dyn Trait`（动态分发）的 vtable 布局有何不同？
2. 孤儿规则为何必要？多 crate 环境下的 trait 实现冲突如何避免？
