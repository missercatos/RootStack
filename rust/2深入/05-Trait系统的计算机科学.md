# Trait系统的计算机科学

## 原理

Rust trait 是多态的双重实现机制：

**静态分发**（monomorphization）：编译器为每个 `impl Trait for T` 生成具体代码副本。函数调用是直接跳转（`call`），可内联，零虚函数开销。代价是二进制膨胀。

**动态分发**（dyn Trait）：通过 vtable 实现。`&dyn Trait` 是 16B 胖指针（data_ptr + vtable_ptr），vtable 为每个 trait 方法存储函数指针。调用时通过 `call [vtable + offset]` 间接跳转，阻止内联。

孤儿规则的类型论背景：trait coherence 要求对于 `(Trait, Type)` 二元组，全局最多一个 impl。限制为"至少一个在本地 crate 定义"防止跨 crate 冲突。

Trait 对象的限制：非 object-safe 的 trait（返回 `Self`、含泛型方法、无 `Self: Sized` 约束的方法）不能使用动态分发，因为 vtable 无法统一表示。

---

## 语法

### Vtable 运行时示意

```rust
trait Animal { fn speak(&self); fn name(&self) -> &str; }
// vtable: [speak_ptr, name_ptr, drop_ptr, size, align]
```

### Object safety 规则

```rust
// 非 object-safe: 返回 Self
trait Clone { fn clone(&self) -> Self; } // dyn Clone 不可用

// Object-safe: Self 不在返回值位置
trait Display { fn fmt(&self, f: &mut Formatter) -> fmt::Result; }
```

### Super-trait

```rust
trait Animal: Display {} // Animal 要求 Display 已实现
```

### 标记 trait

```rust
trait Send {} // 可跨线程传递所有权
trait Sync {} // 可跨线程共享引用
trait Copy {} // 赋值时按位复制
trait Sized {} // 编译时已知大小（默认绑定）
```

### 静态 vs 动态成本

| | Static Dispatch | Dynamic Dispatch |
|--|----------------|------------------|
| 指针大小 | 8B (普通指针) | 16B (胖指针) |
| 调用开销 | 直接或内联 | 间接跳转 (vtable) |
| 二进制体积 | 大 (每个实现一份代码) | 小 (单份代码) |
| 内联优化 | 可能 | 不可能 |

---

## 实践

### 力扣问题

力扣: 力扣排序 — sort_by trait

```rust
students.sort_by(|a, b| b.total.cmp(&a.total)
 .then_with(|| a.chinese.cmp(&b.chinese))
 .then_with(|| a.id.cmp(&b.id)));
```

### AI 自检

1. `dyn Trait` 的 vtable 布局是什么样的？vtable 中包含哪些字段？
2. 为什么返回 `Self` 的 trait 方法阻止 object safety？从 vtable 偏移计算角度解释。
