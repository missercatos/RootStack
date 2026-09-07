# 共享行为：Trait入门

## 学习目标

学完本章后，你将能够：
- 理解 trait 是什么：定义共享行为
- 为自己定义的类型实现 trait
- 使用 `impl Trait` 作为参数和返回值
- 使用 `#[derive]` 自动获取常见 trait
- 理解 trait 和接口的相似性

---

## 一、问题：不同类型，相同行为

你家里的各种东西都能"发出声音"，但声音不同：
- 狗叫：汪汪
- 猫叫：喵喵
- 闹钟：叮叮叮

在代码里，我们希望能写一个统一的"让某物发出声音"的功能，而不针对每种动物写一份。这就是 trait 的用武之地。

---

## 二、最简单的 trait

```rust
// 定义一个 trait：描述"能说话"这个能力
trait Speak {
    fn speak(&self);
}

// 狗：实现 Speak
struct Dog;
impl Speak for Dog {
    fn speak(&self) {
        println!("汪汪！");
    }
}

// 猫：实现 Speak
struct Cat;
impl Speak for Cat {
    fn speak(&self) {
        println!("喵喵！");
    }
}

fn main() {
    let dog = Dog;
    let cat = Cat;

    dog.speak();
    cat.speak();
}
```

输出：

```
汪汪！
喵喵！
```

### 拆解：

```rust
trait Speak {           // 1. 定义一个 trait
    fn speak(&self);    // 2. 声明一个方法签名（没有函数体）
}

impl Speak for Dog {    // 3. 为 Dog 实现这个 trait
    fn speak(&self) {   // 4. 写出具体实现
        println!("汪汪！");
    }
}
```

**trait 就像一个合同**：你签了这个合同（`impl Speak for Dog`），就必须履行合同的条款（实现 `speak` 方法）。

---

## 三、trait 作为参数

有了 trait，就可以写操作"任何能说话的东西"的函数了：

```rust
trait Speak {
    fn speak(&self);
}

struct Dog;
impl Speak for Dog {
    fn speak(&self) { println!("汪汪！"); }
}

struct Cat;
impl Speak for Cat {
    fn speak(&self) { println!("喵喵！"); }
}

// 接受 "任何实现了 Speak 的类型"
fn make_speak(animal: &impl Speak) {
    animal.speak();
}

// 另一种写法：trait bound（更常用）
fn make_speak_twice<T: Speak>(animal: &T) {
    animal.speak();
    animal.speak();
}

fn main() {
    make_speak(&Dog);
    make_speak(&Cat);
    make_speak_twice(&Dog);
}
```

`&impl Speak` 的意思是："一个实现了 Speak trait 的类型的引用"。

| 写法 | 说明 | 适用场景 |
|------|------|----------|
| `fn foo(x: &impl Speak)` | 语法糖写法 | 简单参数 |
| `fn foo<T: Speak>(x: &T)` | trait bound 写法 | 多个参数或复杂约束 |
| `fn foo<T>(x: &T) where T: Speak` | where 写法 | 约束很长时更清晰 |

三种写法等效：

```rust
// 写法1
fn func(a: &impl Speak, b: &impl Speak)

// 写法2
fn func<T: Speak>(a: &T, b: &T)

// 写法3
fn func<T>(a: &T, b: &T) where T: Speak
```

---

## 四、trait 作为返回值

```rust
trait Animal {
    fn name(&self) -> &str;
}

struct Dog;
impl Animal for Dog {
    fn name(&self) -> "狗"
}

struct Cat;
impl Animal for Cat {
    fn name(&self) -> "猫"
}

fn pet_shop(choice: i32) -> Box<dyn Animal> {
    if choice == 1 {
        Box::new(Dog)
    } else {
        Box::new(Cat)
    }
}

fn main() {
    let pet = pet_shop(1);
    println!("你的宠物是：{}", pet.name());
}
```

注意：返回 trait 时要用 `Box<dyn Trait>`，因为不同实现的大小可能不同（Dog 和 Cat 对应的结构体大小可能不一样）。至于 `Box` 和 `dyn` 的具体细节，在深入篇中会详细介绍，现在先记住这种写法即可。

---

## 五、自动派生：#[derive]

很多常见的 trait 不需要自己实现，Rust 可以自动生成：

```rust
// 自动生成 Debug, Clone, PartialEq
#[derive(Debug, Clone, PartialEq)]
struct Person {
    name: String,
    age: u32,
}

fn main() {
    let p1 = Person {
        name: String::from("小明"),
        age: 18,
    };

    let p2 = p1.clone();  // Clone 允许我们复制

    println!("{:?}", p1);          // Debug 允许打印
    println!("相等吗？{}", p1 == p2);  // PartialEq 允许比较
}
```

| 可派生 trait | 作用 |
|-------------|------|
| `Debug` | 用 `{:?}` 打印调试信息 |
| `Clone` | 用 `.clone()` 复制 |
| `Copy` | 赋值时自动复制（浅层，只有小类型） |
| `PartialEq` | 用 `==` 和 `!=` 比较 |
| `Eq` | 完整的等价比较（配合 PartialEq） |
| `PartialOrd` | 用 `<`, `>` 等排序比较 |
| `Ord` | 完整的排序 |
| `Hash` | 用于 HashMap 的键 |
| `Default` | 提供默认值 `Default::default()` |

---

## 六、trait 的默认实现

trait 中的方法可以给出默认实现，这样实现方可以选择使用默认或覆盖：

```rust
trait Greet {
    // 带默认实现
    fn greet(&self) {
        println!("你好！");
    }

    // 无默认实现，必须自己写
    fn name(&self) -> &str;
}

struct Friend {
    name: String,
}

impl Greet for Friend {
    fn name(&self) -> &str {
        &self.name
    }
    // greet 使用默认实现，不需要写
}

struct Boss {
    name: String,
}

impl Greet for Boss {
    fn name(&self) -> &str {
        &self.name
    }

    // 覆盖默认实现
    fn greet(&self) {
        println!("{} 说：工作完成了吗？", self.name);
    }
}

fn main() {
    let f = Friend { name: String::from("小明") };
    let b = Boss { name: String::from("老板") };

    f.greet();  // "你好！"
    b.greet();  // "老板 说：工作完成了吗？"
}
```

---

## 七、trait 约束组合

```rust
use std::fmt::Display;

// 要求 T 同时实现 PartialOrd 和 Display
fn max_and_print<T: PartialOrd + Display>(a: T, b: T) {
    if a > b {
        println!("最大：{}", a);
    } else {
        println!("最大：{}", b);
    }
}

fn main() {
    max_and_print(10, 20);
    max_and_print(3.14, 2.71);
    // max_and_print("hello", "world"); // 也可以！
}
```

`T: PartialOrd + Display` = "T 必须同时实现 PartialOrd 和 Display"。

---

## 八、孤儿规则

你不能为不是你写的类型，不是你写的 trait 做实现。这就是"孤儿规则"。

```rust
// 假设你想让 i32 实现你自己定义的 Speak trait
trait Speak {
    fn speak(&self);
}

impl Speak for i32 {  // 合法！trait 是你写的
    fn speak(&self) {
        println!("数字：{}", self);
    }
}

// 但是：
// impl Display for Vec<i32> { ... }
// 非法！Display 和 Vec 都不是你定义的
```

这条规则防止不同库互相冲突。

---

## 九、综合示例：可排序的物品

```rust
use std::cmp::Ordering;

#[derive(Debug)]
struct Book {
    title: String,
    pages: u32,
}

// 实现 PartialEq：定义什么是"相等"
impl PartialEq for Book {
    fn eq(&self, other: &Self) -> bool {
        self.pages == other.pages
    }
}

impl Eq for Book {}

// 实现 PartialOrd：定义怎么比较
impl PartialOrd for Book {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        self.pages.partial_cmp(&other.pages)
    }
}

impl Ord for Book {
    fn cmp(&self, other: &Self) -> Ordering {
        self.pages.cmp(&other.pages)
    }
}

fn main() {
    let mut books = vec![
        Book { title: String::from("Rust入门"), pages: 300 },
        Book { title: String::from("Python入门"), pages: 200 },
        Book { title: String::from("C入门"), pages: 400 },
    ];

    books.sort();  // 按页数排序

    for book in &books {
        println!("{}（{}页）", book.title, book.pages);
    }
}
```

---

## 本章小结

trait 让你定义"共享行为"：

- `trait Name { fn method(&self); }` 定义行为规范
- `impl Trait for Type { ... }` 为类型实现行为
- `&impl Trait` 作为参数，接受任何实现了该 trait 的类型
- `#[derive(Trait)]` 自动生成常见 trait 的实现
- trait 可以有默认实现，类型可以选择覆盖
- `T: A + B` 组合多个 trait 约束
- 孤儿规则：trait 或类型必须有一个是你自己定义的

trait 是 Rust 中实现"多态"的核心机制。接下来学习生命周期 — 帮助编译器理解引用的寿命。

[[13-引用有效期：生命周期入门]]

---

## 章节考查

> **总分100分**：概念考查40分 + 判断正误20分 + 代码分析15分 + 编程大题15分 + 填空题5分 + 代码补全5分

### 一、概念考查（每题4分，共40分）

**1. trait 在 Rust 中的作用是？**
- A. 存储数据
- B. 定义共享的行为接口
- C. 分配内存
- D. 编译加速

<details><summary>点击查看答案</summary>

**B**。trait 定义了类型必须实现的行为（方法签名），是一种"能力声明"机制。

</details>

**2. `impl Trait for Type` 是什么意思？**
- A. 创建一个新类型
- B. 为 Type 实现 Trait 定义的方法
- C. 导入一个 trait
- D. 声明一个变量

<details><summary>点击查看答案</summary>

**B**。`impl Trait for Type` 表示"为 Type 类型实现 Trait 所约定的功能"。

</details>

**3. `#[derive(Debug)]` 做了什么？**
- A. 创建一个新变量
- B. 自动生成 Debug trait 的实现
- C. 删除 Debug trait
- D. 打印调试信息

<details><summary>点击查看答案</summary>

**B**。`derive` 是编译器自动生成 trait 实现的机制，省去手动编写的重复代码。

</details>

**4. `fn foo(x: &impl Speak)` 中的 `&impl Speak` 的含义是？**
- A. 只有 Speak 类型能传入
- B. 任何实现 Speak trait 的类型都可以传入
- C. x 是 Speak trait 本身
- D. x 必须是一个引用

<details><summary>点击查看答案</summary>

**B**。`&impl Speak` 表示接受"实现了 Speak trait 的任意类型的引用"。

</details>

**5. 孤儿规则（Orphan Rule）规定？**
- A. trait 不能有默认实现
- B. 实现 trait 时，trait 或类型必须至少有一个是本地定义的
- C. trait 只能在 main 中实现
- D. 每个 trait 只能被实现一次

<details><summary>点击查看答案</summary>

**B**。孤儿规则是为了确保 trait 实现的"一致性"：如果你不拥有 trait，也不拥有类型，就不能实现它。

</details>

**6. trait 方法的默认实现是怎样的？**
- A. 不能被覆盖
- B. 在 trait 中写函数体，实现方可以选择使用或覆盖
- C. 所有方法必须有默认实现
- D. 默认实现不存在

<details><summary>点击查看答案</summary>

**B**。trait 方法可以在 trait 定义中给出默认函数体，实现者可以选择覆盖或不覆盖。

</details>

**7. `T: Display + Clone` 意味着？**
- A. T 要么实现 Display，要么实现 Clone
- B. T 必须同时实现 Display 和 Clone
- C. T 不能实现 Display 和 Clone
- D. Display 比 Clone 更重要

<details><summary>点击查看答案</summary>

**B**。`+` 表示"并且"，T 必须同时满足两个约束。

</details>

**8. 以下哪个不能 `#[derive]`？**
- A. Debug
- B. Clone
- C. PartialEq
- D. 任何自定义 trait

<details><summary>点击查看答案</summary>

**D**（当前理解层面）。`derive` 只能用于编译器内置支持的特殊 trait，自定义 trait 需要手动 implement。

</details>

**9. `PartialOrd` trait 的作用是？**
- A. 比较是否相等
- B. 排序比较（大于、小于）
- C. 打印
- D. 复制

<details><summary>点击查看答案</summary>

**B**。`PartialOrd` 提供 `<`、`>`、`<=`、`>=` 比较功能。

</details>

**10. `Box<dyn Trait>` 用于什么场景？**
- A. 加速代码
- B. 在返回值中使用 trait 类型（动态分发）
- C. 替换所有引用
- D. 创建数组

<details><summary>点击查看答案</summary>

**B**。`Box<dyn Trait>` 允许在运行时确定具体类型，用于存储、返回所需的不确定大小的 trait 对象。

</details>

### 二、判断正误（每题2分，共20分）

**1. trait 可以有字段定义。**
<details><summary>点击查看答案</summary>

**错误**。trait 只能定义方法（包括默认实现），不能定义字段。

</details>

**2. 一个类型可以实现多个 trait。**
<details><summary>点击查看答案</summary>

**正确**。一个类型可以 `impl TraitA for Type { ... }` 和 `impl TraitB for Type { ... }`。

</details>

**3. `impl Trait` 语法和 `T: Trait` 语法在参数列表中完全等价。**
<details><summary>点击查看答案</summary>

**近似正确**，但有细微差别（多个参数时约束是否要求同一类型等）。在入门层面可以认为它们表达相同的意思。

</details>

**4. `#[derive(Clone)]` 对所有类型都有效。**
<details><summary>点击查看答案</summary>

**错误**。如果结构体包含不支持 Clone 的字段，derive(Clone) 会失败。

</details>

**5. trait 方法不能有返回值。**
<details><summary>点击查看答案</summary>

**错误**。trait 方法可以定义任何返回类型，包括泛型返回类型。

</details>

**6. `&impl Trait` 不能用作函数返回类型。**
<details><summary>点击查看答案</summary>

**实际上在新版 Rust 中 `-> impl Trait` 可以用作返回类型**，但和 `-> &impl Trait` 有所不同。命题说"不能"是不准确的。在较新 Rust 版本中可以使用。

</details>

**7. 所有实现了 `PartialEq` 的类型都可以用 `==` 比较。**
<details><summary>点击查看答案</summary>

**正确**。`PartialEq` trait 定义了 `eq` 和 `ne` 方法，`==` 和 `!=` 是它们的语法糖。

</details>

**8. trait 中带有默认实现的方法可以不用在 `impl` 块中重写。**
<details><summary>点击查看答案</summary>

**正确**。默认提供了实现，实现者不必再写。除非想覆盖它。

</details>

**9. 可以为自己写的 trait 给他人的类型做实现。**
<details><summary>点击查看答案</summary>

**正确**。孤儿规则允许：只要 trait 或类型中有一个是你自己定义的就可以。

</details>

**10. `Box<dyn Animal>` 在编译时就确定了具体类型。**
<details><summary>点击查看答案</summary>

**错误**。`dyn` 表示动态分发，具体类型在运行时确定。

</details>

### 三、代码分析（每题3分，共15分）

**1. 下面代码的输出是什么？**

```rust
trait Sound {
    fn make(&self) -> &str;
}

struct Bell;
impl Sound for Bell {
    fn make(&self) -> &str {
        "叮咚"
    }
}

struct Drum;
impl Sound for Drum {
    fn make(&self) -> &str {
        "咚咚"
    }
}

fn play(s: &impl Sound) {
    println!("{}", s.make());
}

fn main() {
    play(&Bell);
    play(&Drum);
}
```

- A. 叮咚 咚咚
- B. 编译错误
- C. 咚咚 叮咚
- D. 只有 叮咚

<details><summary>点击查看答案</summary>

**A**。`play(&Bell)` 打印"叮咚"，`play(&Drum)` 打印"咚咚"。

</details>

**2. 下面代码的输出是什么？**

```rust
#[derive(Debug, Clone)]
struct Item {
    name: String,
    price: u32,
}

fn main() {
    let i1 = Item { name: String::from("笔"), price: 5 };
    let i2 = i1.clone();
    println!("{:?}", i1);
}
```

- A. 编译错误（i1 被移动了）
- B. Item { name: "笔", price: 5 }
- C. clone 失败
- D. 打印 i2 的内容

<details><summary>点击查看答案</summary>

**B**。`i1.clone()` 创建了独立副本，`i1` 仍可使用。打印输出 i1 的 Debug 格式。

</details>

**3. 下面代码能否编译通过？**

```rust
trait Printable {
    fn print(&self);
}

impl Printable for i32 {
    fn print(&self) {
        println!("数字：{}", self);
    }
}

fn main() {
    42.print();
}
```

- A. 能，输出"数字：42"
- B. 不能，i32 不能有方法
- C. 不能，孤儿规则不允许
- D. 能，但输出"42"

<details><summary>点击查看答案</summary>

**A**。trait 是我们自己写的，i32 是标准库的 — 符合孤儿规则（至少一个是本地的）。

</details>

**4. 下面代码的输出是什么？**

```rust
trait Describable {
    fn describe(&self) -> String;
}

impl Describable for i32 {
    fn describe(&self) -> String {
        format!("整数：{}", self)
    }
}

fn print_info(x: &impl Describable, y: &impl Describable) {
    println!("{} 与 {}", x.describe(), y.describe());
}

fn main() {
    let a = 10;
    let b = 20;
    print_info(&a, &b);
}
```

- A. 编译错误
- B. 整数：10 与 整数：20
- C. 10 与 20
- D. 没有输出

<details><summary>点击查看答案</summary>

**B**。`a` 和 `b` 都是 i32，都实现了 Describable，输出对应的描述。

</details>

**5. 下面代码有什么问题？**

```rust
trait Action {
    fn act(&self);
}

struct Robot;
impl Action for Robot {
    fn act(&self) { println!("机械动作"); }
}

struct Human;
impl Action for Human {
    fn act(&self) { println!("人类动作"); }
}

fn factory(kind: bool) -> impl Action {
    if kind {
        Robot
    } else {
        Human
    }
}
```

- A. 没有错误
- B. 不能用 `impl Action` 作为返回类型
- C. `impl Action` 返回时必须所有分支返回相同类型
- D. act 方法不能有默认实现

<details><summary>点击查看答案</summary>

**C**。`impl Trait` 作为返回类型时，所有代码路径必须返回同一具体类型。这里 Robot 和 Human 是不同的类型。应该用 `Box<dyn Action>`。

</details>

### 四、编程大题（15分）

**题目：** 设计一个"形状面积计算"系统：
1. 定义 trait `Area`：方法 `fn area(&self) -> f64`
2. 定义 trait `Perimeter`：方法 `fn perimeter(&self) -> f64`
3. 实现结构体 Circle（半径）和 Rectangle（宽高）
4. 两者都实现 Area 和 Perimeter
5. 实现一个函数 `print_info(shape: &(impl Area + Perimeter))` 打印面积和周长
6. 在 main 中测试

<details><summary>点击查看答案</summary>

```rust
use std::f64::consts::PI;

trait Area {
    fn area(&self) -> f64;
}

trait Perimeter {
    fn perimeter(&self) -> f64;
}

struct Circle {
    radius: f64,
}

impl Area for Circle {
    fn area(&self) -> f64 {
        PI * self.radius * self.radius
    }
}

impl Perimeter for Circle {
    fn perimeter(&self) -> f64 {
        2.0 * PI * self.radius
    }
}

struct Rectangle {
    width: f64,
    height: f64,
}

impl Area for Rectangle {
    fn area(&self) -> f64 {
        self.width * self.height
    }
}

impl Perimeter for Rectangle {
    fn perimeter(&self) -> f64 {
        2.0 * (self.width + self.height)
    }
}

fn print_info(shape: &(impl Area + Perimeter)) {
    println!("面积：{:.2}，周长：{:.2}", shape.area(), shape.perimeter());
}

fn main() {
    let c = Circle { radius: 5.0 };
    let r = Rectangle { width: 4.0, height: 6.0 };

    println!("圆形：");
    print_info(&c);

    println!("矩形：");
    print_info(&r);
}
```

**评分标准**：
- Area trait（2分）
- Perimeter trait（2分）
- Circle 和 impl（3分）
- Rectangle 和 impl（3分）
- print_info 函数（3分）
- main 测试（2分）

</details>

### 五、填空题（每题1分，共5分）

**1. 定义 trait 用关键字 `______`。**

<details><summary>点击查看答案</summary>

**trait**。`trait Name { fn method(&self); }`。

</details>

**2. 为类型实现 trait：`______ TraitName ______ TypeName { ... }`。**

<details><summary>点击查看答案</summary>

**impl** 和 **for**。`impl TraitName for TypeName { ... }`。

</details>

**3. `#[derive(______)]` 可以让结构体支持 `{:?}` 打印。**

<details><summary>点击查看答案</summary>

**Debug**。`derive(Debug)` 生成 `fmt::Debug` 的实现。

</details>

**4. `fn foo(x: &______ Trait)` 接受任何实现了 Trait 的类型的引用。**

<details><summary>点击查看答案</summary>

**impl**。`&impl Trait` 是 trait bound 的语法糖。

</details>

**5. `______` 规则：实现 trait 时，trait 或类型至少一个必须是本地定义的。**

<details><summary>点击查看答案</summary>

**孤儿（Orphan）**。孤儿规则保证了 trait 实现的一致性（coherence）。

</details>

### 六、代码补全（共5分）

**1. 补全 trait 定义（2分）**

```rust
______ Summary {
    fn summarize(&self) -> String;
}
```

<details><summary>点击查看答案</summary>

```rust
trait Summary {
```

</details>

**2. 补全 trait 实现（2分）**

```rust
struct Article {
    title: String,
}

______ Summary ______ Article {
    fn summarize(&self) -> String {
        format!("文章：{}", self.title)
    }
}
```

<details><summary>点击查看答案</summary>

```rust
impl Summary for Article {
```

</details>

**3. 补全 derive 用法（1分）**

```rust
#[______(Debug, Clone)]
struct Point {
    x: i32,
    y: i32,
}
```

<details><summary>点击查看答案</summary>

```rust
#[derive(Debug, Clone)]
```

</details>

---

> **计分：概念40 + 判断20 + 代码分析15 + 编程15 + 填空5 + 补全5 = 总分100分**
