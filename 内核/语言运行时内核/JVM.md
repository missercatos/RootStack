
# JVM -- Java 虚拟机内核

> Java 的"操作系统"——类加载器、字节码解释器、分层编译、高级 GC、JNI 桥接。

## 概念

HotSpot JVM 是 Java 平台的旗舰实现，用 C++ 编写。JVM 不仅仅是一个解释器——它是一整套运行时环境：从 class 文件验证到类加载，从解释执行到 C1/C2 JIT 编译，从分代 GC 到 JNI 本地调用。JVM 是"托管运行时"的典范，也是 Rust/Go 运行时设计的参考对象。

## 核心组件

| 组件 | 职责 | 关键机制 |
|------|------|---------|
| 类加载器 | 查找、加载、链接 class 文件 | 双亲委派模型 |
| 字节码解释器 | 执行 class 文件中的字节码指令 | 栈帧模型 |
| C1 编译器 | 快速 JIT (Client Compiler), 低延迟 | 线性扫描寄存器分配 |
| C2 编译器 | 优化 JIT (Server Compiler), 高峰值性能 | 图着色寄存器分配 |
| 对象模型 | Mark Word + Klass pointer + 字段 + 对齐 | 对象头 |
| G1GC / ZGC | 分代 + 并发 + 低停顿 GC | 分区、染色指针 |
| JNI | Java 调用 C/C++ 代码的桥梁 | native 方法调用 |

## 类加载器层次

```
Bootstrap ClassLoader (加载核心库)
 ^ rt.jar / modules 中的 java.lang.*, java.util.*
 |
Extension ClassLoader (JDK 8 及之前, 加载 jre/lib/ext)
 ^
 |
Application ClassLoader (加载 classpath 中的用户类)
```

双亲委派模型: 每个类加载器收到加载请求时，先委托给父加载器，父加载器找不到才自己加载。这保证了核心类不会被用户代码篡改。

## 对象头布局 (64-bit JVM)

```
+------------------------+------------------------+------------------------+------------------------+
| Mark Word (64-bit) | Klass Pointer (32-bit | Instance Fields... | Padding |
| | with compressed oops) | | (to 8-byte alignment) |
+------------------------+------------------------+------------------------+------------------------+
| bits [0:1] = lock flag |
| 01: unlocked / biased |
| 00: lightweight locked |
| 10: heavyweight locked |
| 11: GC mark |
| bits [25:31] = identity hashcode (on demand) |
| bits [32:62] = age (GC 分代年龄) |
```

## C1 → C2 分层编译

```
mermaid
graph TD
 L0["Level 0: 解释执行<br/>纯字节码解释器"]
 L1["Level 1: C1 无 profile<br/>简单 C1 编译, 无收集数据"]
 L2["Level 2: C1 有限 profile<br/>快速编译, 收集部分类型数据"]
 L3["Level 3: C1 完整 profile<br/>完整编译, 收集所有调用/分支数据"]
 L4["Level 4: C2 编译<br/>基于 profile 的深度优化"]

 L0 --> L3
 L0 --> L2
 L2 --> L3
 L3 --> L4
 L4 --> L0

 style L0 fill:#f9f,stroke:#333
 style L4 fill:#9f9,stroke:#333
```

## G1GC 概览

| 阶段 | 描述 | 是否并发 |
|------|------|---------|
| 初始标记 (Initial Mark) | 标记 GC Roots 直接可达对象 | STW (短) |
| 并发标记 (Concurrent Mark) | 从 roots 出发并发追踪引用图 | 并发 |
| 最终标记 (Remark) | 处理并发标记期间的修改 | STW (短) |
| 清除 (Cleanup) | 计算区域存活度, 挑选回收区域 | STW (短) |
| 复制 (Evacuation) | 将存活对象复制到新区域, 回收旧区域 | STW (并行) |

## JNI 桥接

```
Java (JavaVM)
 |
 | System.loadLibrary("native")
 | native int compute(int a, int b);
 | |
 | JNIEXPORT jint JNICALL Java_com_example_Main_compute
 | (JNIEnv *env, jobject obj, jint a, jint b) {
 | return a + b;
 | }
 |
C/C++ (libnative.so / native.dll)
```

JNI 调用开销: ~10-40ns (直接调用) 或 ~200ns+ (需要类型转换)。JNI 临界区会阻止 GC 移动正在使用的对象。

---

