# 共享行为：Trait入门

## 原理

### Trait 是 Rust 实现多态的核心机制

编译期多态通过泛型 + trait bound（静态分发）实现，等同于单态化后的具体函数调用。运行时多态通过 `&dyn Trait` / `Box<dyn Trait>`（动态分发）实现，在对象中包含两个指针：data pointer + vtable pointer（胖指针，16 字节），vtable 包含所有 trait 方法的函数指针。

```text
静态分发 (impl Trait / <T: Trait>):
┌─────────────────────────────────────────┐
│ 编译时: 单态化为具体类型                  │
│ fn speak_dog(dog: &Dog) { dog.speak(); }│
│ fn speak_cat(cat: &Cat) { cat.speak(); }│
│ 运行时: 直接调用，零开销                  │
└─────────────────────────────────────────┘

动态分发 (dyn Trait):
┌─────────────────────────────────────────┐
│ 运行时: 胖指针 (16 字节)                 │
│                                           │
│ &dyn Speak = [data_ptr, vtable_ptr]       │
│                ↓          ↓               │
│            Dog 实例    ┌─────────────┐    │
│                        │ drop: ...   │    │
│                        │ speak: ...  │    │
│                        │ introduce: …│    │
│                        └─────────────┘    │
│ 调用: (vtable.speak)(data_ptr)            │
└─────────────────────────────────────────┘
```

### 静态分发 vs 动态分发

| 特性 | 静态分发 | 动态分发 |
|------|----------|----------|
| 运行时开销 | 零 | vtable 跳转 |
| 内联优化 | 可能 | 不可能 |
| 二进制体积 | 大（膨胀） | 小（单份） |
| 异构集合 | 不可能 | `Vec<Box<dyn Trait>>` |
| 编译错误 | 清晰 | 模糊 |
| 类型信息 | 编译时完全已知 | 仅知道 trait |

### 孤儿规则（Orphan Rule）

为类型实现 trait 时，至少 trait 或类型之一必须在当前 crate 中定义。这保证 trait 实现的全局一致性，防止多个 crate 冲突。

```text
Orphan Rule 规则:
- impl Trait for Type
- 必须满足: Trait 在当前 crate 定义 OR Type 在当前 crate 定义

允许:
✅ impl MyTrait for i32       (MyTrait 是我的)
✅ impl Display for MyStruct  (MyStruct 是我的)

禁止:
❌ impl Display for Vec<i32>  (都不是我的)
❌ impl Hash for i32          (Hash 和 i32 都不是我的)
```

### derive 宏行为

`#[derive]` 是过程宏，在编译时自动生成 trait 实现代码，省去样板代码。

```rust
#[derive(Debug, Clone, PartialEq)]
struct Point { x: f64, y: f64 }

// 编译器自动生成 (概念性):
// impl Debug for Point {
//     fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
//         f.debug_struct("Point")
//          .field("x", &self.x)
//          .field("y", &self.y)
//          .finish()
//     }
// }
// impl Clone for Point { ... } // 按位复制
// impl PartialEq for Point { ... } // 逐字段比较
```

### Display / Debug / Clone / Copy 深入

```text
Display vs Debug:
  Display: 面向用户的输出 ({})
    - 需要手动 impl
    - 用于错误信息、用户界面

  Debug: 面向开发者的输出 ({:?})
    - 可以 derive
    - 用于调试、日志

Clone vs Copy:
  Clone: 显式深拷贝 (.clone())
    - 可能昂贵（堆数据、递归结构）
    - 需要显式调用

  Copy: 隐式按位复制 (赋值时自动)
    - 只适用于栈上小数据
    - 要求类型实现了 Clone
    - 所有字段也必须是 Copy
    - 实现 Copy 后 clone() 变为按位复制

  哪些类型可以 Copy:
    ✅ i32, f64, bool, char
    ✅ 所有字段都是 Copy 的元组/结构体
    ❌ String, Vec, Box (包含堆指针)
    ❌ 引用 (可以 Copy，但不是"数据的 Copy")
```

---

## 语法

### 定义与实现

```rust
trait Speak {
    fn speak(&self); // 必须实现（无默认实现）
    fn introduce(&self) -> String { // 默认实现
        format!("I can speak!")
    }
}

struct Dog;
impl Speak for Dog {
    fn speak(&self) { println!("Woof!"); }
    // introduce() 使用默认实现
}

struct Cat;
impl Speak for Cat {
    fn speak(&self) { println!("Meow!"); }
    fn introduce(&self) -> String {
        format!("I am a cat!")
    }
}
```

### Trait 作为参数

```rust
// impl Trait 语法糖
fn say(animal: &impl Speak) { animal.speak(); }

// 完整 trait bound 语法（等价）
fn say<T: Speak>(animal: &T) { animal.speak(); }

// 两个参数需要同一类型
fn say_both<T: Speak>(a: &T, b: &T) {
    a.speak();
    b.speak();
}

// impl Trait 允许不同实现类型
fn say_both_impl(a: &impl Speak, b: &impl Speak) {
    a.speak();
    b.speak();
}
```

### Trait 作为返回值

```rust
fn create() -> Box<dyn Speak> {
    Box::new(Dog)
}

// impl Trait 返回（所有路径必须返回同一类型）
fn create_dog() -> impl Speak {
    Dog
    // 不能在不同分支返回不同类型
}
```

> `impl Trait` 返回要求所有路径返回同一具体类型。返回不同类型需 `Box<dyn Trait>`。

### derive 自动实现

```rust
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
struct User { name: String, id: u32 }
```

| derive trait | 提供功能 | 使用场景 |
|-------------|----------|----------|
| `Debug` | `{:?}` 打印 | 调试、日志 |
| `Clone` | `.clone()` 深拷贝 | 需要复制时 |
| `Copy` | 赋值时自动按位复制 | 栈上小数据 |
| `PartialEq` / `Eq` | `==` `!=` 比较 | 相等性判断 |
| `PartialOrd` / `Ord` | `>` `<` 排序比较 | 排序、比较 |
| `Hash` | HashMap 键 | 需要哈希时 |
| `Default` | `Default::default()` | 提供默认值 |

### 孤儿规则

```rust
trait MyTrait { } // 我的 crate 定义的 trait
impl MyTrait for i32 { } // 合法：trait 是我的

// impl Display for Vec<i32> { } // 非法：trait 和类型都不是我的

// 绕过孤儿规则: Newtype 模式
struct MyVec(Vec<i32>);
impl std::fmt::Display for MyVec {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        write!(f, "{:?}", self.0)
    }
}
// MyVec 是我的类型，所以合法
```

### 组合约束

```rust
fn dump<T: Display + Debug>(x: &T) {
    println!("Display: {}", x);
    println!("Debug: {:?}", x);
}

fn print_info(x: &(impl Area + Perimeter)) {
    println!("面积: {}, 周长: {}", x.area(), x.perimeter());
}

// where 子句（更清晰）
fn complex_function<T, U>(t: &T, u: &U) -> String
where
    T: Display + Debug,
    U: Clone + Into<String>,
{
    format!("{}-{}", t, u.clone().into())
}
```

### trait 对象的大小限制

```rust
// dyn Trait 是 sized 的（固定大小的胖指针）
let obj: Box<dyn Speak> = Box::new(Dog);  // Box 8 字节 (指针)
let ref_obj: &dyn Speak = &Dog;           // & 16 字节 (胖指针: data + vtable)

// 返回 impl Trait 不是 fat pointer
fn create() -> impl Speak { Dog }  // 编译时类型已知
```

---

## 常见陷阱与最佳实践

### 陷阱 1：返回不同类型的 impl Trait

```rust
// ❌ 编译失败
fn create(switch: bool) -> impl Speak {
    if switch { Dog } else { Cat }
    // 编译器: 两个分支返回不同类型
}

// ✅ 使用 dyn Trait
fn create(switch: bool) -> Box<dyn Speak> {
    if switch { Box::new(Dog) } else { Box::new(Cat) }
}
```

### 陷阱 2：Copy 和 Clone 混淆

```rust
// Copy 类型赋值不消耗所有权
let x: i32 = 5;
let y = x;  // x 仍然可用
println!("{} {}", x, y);  // ✅

// Clone 类型需要显式调用
let s1 = String::from("hello");
let s2 = s1.clone();  // 显式克隆
// println!("{}", s1);  // ✅ s1 仍然可用

// ❌ 但这样会移动 s1
let s3 = s1;
// println!("{}", s1);  // 编译错误: s1 已移动
```

### 最佳实践

1. 优先用 `impl Trait` 作为参数，简单且约束清晰
2. 需要异构集合时用 `Box<dyn Trait>`
3. 库代码避免依赖孤儿规则，提供 trait 而非具体类型
4. `derive` 前检查字段是否支持（如 `Copy` 要求所有字段 Copy）

---

## 实践

### 力扣问题

力扣: 力扣排序题 — trait + derive

```rust
#[derive(Debug, Clone, PartialEq)]
struct Student { id: u32, grade: u32 }

impl Eq for Student {}

impl PartialOrd for Student {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        self.grade.partial_cmp(&other.grade)
    }
}

impl Ord for Student {
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        self.grade.cmp(&other.grade)
    }
}
```

力扣: 力扣多态题 — trait 对象

```rust
trait Shape {
    fn area(&self) -> f64;
    fn name(&self) -> &str;
}

struct Circle { radius: f64 }
impl Shape for Circle {
    fn area(&self) -> f64 { std::f64::consts::PI * self.radius.powi(2) }
    fn name(&self) -> &str { "Circle" }
}

struct Rectangle { width: f64, height: f64 }
impl Shape for Rectangle {
    fn area(&self) -> f64 { self.width * self.height }
    fn name(&self) -> &str { "Rectangle" }
}

fn total_area(shapes: &[Box<dyn Shape>]) -> f64 {
    shapes.iter().map(|s| s.area()).sum()
}
```

### AI 自检

1. `impl Trait`（静态分发）与 `dyn Trait`（动态分发）的 vtable 布局有何不同？
2. 孤儿规则为何必要？多 crate 环境下的 trait 实现冲突如何避免？
3. `Copy` 类型的赋值和 `Clone` 类型的 `.clone()` 在二进制层面有什么区别？
4. `Box<dyn Trait>` 和 `&dyn Trait` 的大小分别是什么？
