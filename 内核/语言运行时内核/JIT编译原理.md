
# JIT 编译原理

> Just-In-Time 编译——让解释型语言跑出接近编译型语言的性能。

## 概念

JIT (Just-In-Time) 编译是在程序运行时将字节码（或源码）编译为机器码的技术。与 AOT (Ahead-Of-Time) 编译不同，JIT 拥有运行时信息（类型反馈、执行频率、分支概率），可以做"投机优化"（Speculative Optimization），在很多场景下甚至超过 AOT 编译的性能（如 Java 长服务进程）。

## 核心分类

| 类型 | 触发条件 | 优点 | 缺点 | 代表 |
|------|---------|------|------|------|
| Method JIT | 检测到某个方法调用频率超过阈值 | 编译单元清晰, 优化范围大 | 冷函数编译浪费 | HotSpot C1/C2 |
| Tracing JIT | 检测到某个循环路径热度高 | 只编译热路径, 开销低 | 边角情况需要 guard | TraceMonkey, LuaJIT |
| Baseline JIT | 所有代码首次执行时 JIT | 没有解释器开销 | 编译压力大 | SpiderMonkey Baseline |

## Method JIT vs Tracing JIT

```
// Method JIT (HotSpot):
//   编译整个方法体, 不管冷热分支, 覆盖所有 case
function compute(a, b, op):
    IF op == 1:  return a + b        // 热路径
    IF op == 2:  return a - b        // 冷路径
    IF op == 3:  return a * b        // 冷路径
    IF op == 4:  return a / b        // 冷路径
    // ^ 全部编译为机器码

// Tracing JIT (LuaJIT):
//   只追踪实际执行的热路径, 编译为一条直线代码
//   op == 1 路径: a + b 的机器码
//   路径入口有 guard 检查 op == 1
//   如果 op != 1, guard 失败 → 跳回解释器
```

## 内联缓存 (Inline Caching)

```
// 无优化: 每次方法调用都走虚表查找
obj.toString()  // Mask: load obj.klass → load klass.vtable[toString_slot] → call

// 内联缓存 (IC):
// 缓存最近一次的类型和对应的函数指针
if (obj.klass == cached_klass) {
    call cached_toString_impl;   // 快速路径
} else {
    // 慢速路径: 查找 vtable, 更新缓存
    cached_klass = obj.klass;
    cached_toString_impl = lookup(obj.klass, "toString");
    call cached_toString_impl;
}

// 多态内联缓存 (PIC): 缓存 3-4 个常见类型的函数指针
// Megamorphic: 超过阈值则退回 vtable 查找
```

## 投机优化 (Speculative Optimization)

```
// 基于运行时 profile 的投机优化

// 场景: 函数总是接收 int 参数
function add(a, b) { return a + b; }

// TurboFan 生成以下伪机器码:
//   ...
//   CHECK a IS Smi          ← guard
//   CHECK b IS Smi          ← guard
//   temp = a + b            ← 已优化为单条 CPU 加法指令
//   CHECK overflow          ← guard
//   RETURN temp
//   ...
//   DEOPTIMIZE:             ← 任一个 guard 失败即跳转
//       保存状态
//       丢弃编译的机器码
//       从 Ignition 字节码继续执行

// 去优化 (Deoptimization):
//   1. 记录 recompile 信息 (哪类 guard 失败, 常见类型是什么)
//   2. 下次编译时根据新的类型反馈生成新的机器码
//   3. 这就是为什么 V8 可能对一个函数生成多个版本
```

## 分层编译阶梯

```
性能
  ^
  |                                Level 4: C2 / TurboFan
  |                                  深度优化机器码
  |                                    - 内联展开
  |                                    - 逃逸分析
  |                                    - 循环展开
  |                                    - SIMD 向量化
  |                                    - 分支预测
  |
  |                      Level 3: C1 full profile / Ignition + feedback
  |                        收集所有类型反馈
  |
  |           Level 2: C1 limited profile
  |             收集部分类型反馈
  |
  |  Level 1: C1 quick / Ignition
  |    无反馈, 快速编译
  |
  |  Level 0: 纯解释
  +----------------------------------------------------------> 时间
```

## PGO (Profile-Guided Optimization)

AOT 编译器也可以利用 PGO 模拟 JIT 的效果:
```
1. 在程序带有 profiling 选项的情况下运行 → 生成 .profdata
2. 重新编译, 编译器读取 .profdata
3. 编译器根据 profile 信息做代码布局 (热路径放一起)、内联决策
```

JIT 拥有运行时实时 profile, 但占用内存和 CPU 资源; PGO 不占运行时资源, 但需要离线采集, 无法应对部署后的行为变化。

---

## 交叉链接

- [[../../c语言教程/2深化/06_编译链接与ELF|编译链接与 ELF]] -- AOT 编译的完整流程
- [[../../cpp教程/cpp深化教程/07_面向对象(三)多态与虚函数|C++ 虚函数]] -- vtable 机制 vs 内联缓存
- [[CPython|CPython 运行时]] -- 为什么 CPython 不 JIT (PyPy 做 JIT)
- [[V8|V8 引擎]] -- Ignition + TurboFan 的完整 JIT 流水线
- [[JVM|JVM 运行时]] -- C1/C2 分层编译
- [[../系统内核/05_中断与系统调用|中断与系统调用]] -- JIT 代码的异常处理 vs 内核中断
