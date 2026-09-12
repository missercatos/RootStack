# 03 FFI 与原生交互

> 现实世界里有大量久经考验的 C/C++ 库：OpenSSL、SQLite、FFmpeg、图像编解码器、硬件厂商 SDK。Dart 不可能也不应该重写它们。`dart:ffi`（Foreign Function Interface）就是那扇门：让 Dart 直接调用动态库里的 C 函数、读写原生内存、传递结构体，甚至让 C 回调 Dart。与 JNI 相比，FFI 不需要写胶水代码，也不需要 JVM 中转；代价是**内存安全的责任重新回到程序员肩上**——这一章你会重新见到 `malloc`/`free`，也必须像 C 程序员一样对每一次分配负责。
>
> 前置知识：[[dart/1入门/03_变量与类型|03 变量与类型]]（数值宽度）、[[dart/2深入/01_泛型与类型系统|01 泛型与类型系统]]（`Pointer<T>` 是泛型类）。对照阅读：[[java/2深入/02_注解与反射|Java 注解与反射]] 中提到的 JNI 路线。

---

## 一、什么是 FFI：三条互操作路线对比

要在托管语言里调用 C，主流方案有三类：JNI（Java）、ctypes/cffi（Python）、FFI（Dart/Rust 等）。它们的核心差异在"谁来做参数转换"：

| 维度 | Java JNI | Python ctypes | Dart FFI |
|------|----------|---------------|----------|
| 是否需要写胶水代码 | 需要（C 侧实现 `JNIEXPORT` 函数） | 不需要 | 不需要 |
| 类型声明方式 | 头文件 + 手写 native 方法 | Python 侧声明 argtypes | Dart typedef 声明函数签名 |
| 调用开销 | 中（JVM 边界 + 胶水层） | 较高（动态解析） | 低（生成直接调用桩） |
| 内存管理 | JNI 局部/全局引用 | Python 对象 + 手动 free | 手动 malloc/free + GC 不介入 |
| 回调支持 | 复杂 | 支持 | `NativeCallable` |
| 适用场景 | Android 原生生态 | 脚本快速集成 | 移动/桌面/服务端通用 |

Dart FFI 的工作方式：`dart:ffi` 在编译期为每个 `lookupFunction` 生成一段**调用桩（trampoline）**，把 Dart 值按 ABI 规则放入寄存器/栈，然后跳转到目标地址。运行时开销接近一次普通函数调用，远低于 JNI 的边界成本。

---

## 二、调用流程与动态库加载

```mermaid
flowchart LR
    A["DynamicLibrary.open('libfoo.so')"] --> B["拿到库句柄"]
    B --> C["lookupFunction<Native签名, Dart签名>('foo')"]
    C --> D["生成调用桩 trampoline"]
    D --> E["Dart 调用，参数按 C ABI 传递"]
    E --> F["进入 C 函数执行"]
    F --> G["返回值按 ABI 转回 Dart 值"]
    G --> H["继续 Dart 代码"]
```

加载动态库有三种方式：

| API | 用途 | 平台 |
|-----|------|------|
| `DynamicLibrary.open(path)` | 加载指定 `.so`/`.dylib`/`.dll` | 全平台 |
| `DynamicLibrary.process()` | 取当前进程已加载的符号（如 libc） | Android/Linux/macOS/iOS |
| `DynamicLibrary.executable()` | 取可执行文件自身导出的符号 | 静态链接场景 |

```dart
import 'dart:ffi';
import 'package:ffi/ffi.dart';

typedef StrlenNative = Size Function(Pointer<Utf8>);
typedef StrlenDart = int Function(Pointer<Utf8>);

void main() {
  // 进程内查找：libc 早已加载，Linux/macOS 上可直接取符号
  final libc = DynamicLibrary.process();
  final strlen = libc.lookupFunction<StrlenNative, StrlenDart>('strlen');

  final text = '你好，FFI'.toNativeUtf8();   // Dart String -> C 字符串
  print('字节数: ${strlen(text)}');          // UTF-8 编码后的字节数
  print('回读: ${text.toDartString()}');
  malloc.free(text);                          // 谁分配谁释放
}
```

`lookupFunction` 需要两个 typedef：`Native` 版本用 FFI 原生类型描述 C 侧签名，`Dart` 版本描述调用侧的 Dart 类型。两者必须逐参数对应，ABI 不匹配不会编译报错，但会在运行时崩溃或产生垃圾值。

---

## 三、原生类型映射表

| C 类型 | FFI 类型 | Dart 侧类型 | 宽度/说明 |
|--------|----------|-------------|-----------|
| `int8_t` | `Int8` | `int` | 1 字节 |
| `int16_t` | `Int16` | `int` | 2 字节 |
| `int32_t` | `Int32` | `int` | 4 字节 |
| `int64_t` | `Int64` | `int` | 8 字节 |
| `uint8_t` | `Uint8` | `int` | 0~255 |
| `float` | `Float` | `double` | 4 字节 |
| `double` | `Double` | `double` | 8 字节 |
| `bool`（C99） | `Bool` | `bool` | 1 字节 |
| `char *`（UTF-8） | `Pointer<Utf8>` | `String`（需转换） | 空字符结尾 |
| `void *` | `Pointer<Void>` | `Pointer<Void>` | 无类型指针 |
| `T *` | `Pointer<T>` | `Pointer<T>` | 指向 T 的指针 |
| `size_t` | `Size` | `int` | 平台字长 |
| `intptr_t` | `IntPtr` | `int` | 可存指针的整数 |
| `struct T` | `final class T extends Struct` | 类实例（按值） | 见第五节 |
| 函数指针 | `Pointer<NativeFunction<T>>` | `Pointer<NativeFunction<T>>` | 见第七节 |

注意 Dart 的 `int` 是 64 位，而 C 的 `int` 通常是 32 位——签名里必须写 `Int32` 而不是 `Int64`，否则栈帧错位。

---

## 四、Pointer 与内存读写

FFI 指针是真正的原生地址，但**不能做指针算术**，取而代之的是 `elementAt`、`cast`、`ref`、`value`：

```dart
import 'dart:ffi';
import 'package:ffi/ffi.dart';

void main() {
  // calloc 清零分配；malloc 不保证清零
  final buffer = calloc<Int32>(4);   // 4 个 int32

  for (var i = 0; i < 4; i++) {
    buffer[i] = (i + 1) * 10;        // operator[] 按元素下标读写
  }
  print(buffer[0]);                  // 10
  print(buffer.elementAt(3).value);  // 40，等价写法

  // 重新解释类型：把同一块内存当作字节数组读
  final bytes = buffer.cast<Uint8>();
  print(bytes[0]);                   // 10（小端序下第一个 int32 的最低字节）
  print('地址: 0x${buffer.address.toRadixString(16)}');

  calloc.free(buffer);               // 释放，用错 allocator 会出问题
}
```

内存 API 速查：

| API | 行为 | 对应 C |
|-----|------|--------|
| `malloc<T>(n)` | 分配 `n * sizeOf<T>()` 字节，不初始化 | `malloc` |
| `calloc<T>(n)` | 分配并全部置零 | `calloc` |
| `malloc.free(p)` / `calloc.free(p)` | 释放 | `free` |
| `p.ref` | 解引用得到 T 的值（`Pointer<Int32>.ref` 是 `int`） | `*p` |
| `p.value` / `p.value = v` | 读写指向的值 | `*p` |
| `p[i]` | 第 i 个元素（T 为原生类型时） | `p[i]` |
| `p.cast<U>()` | 改变指向类型，不移动地址 | `(U *)p` |
| `sizeOf<T>()` | 取类型字节数 | `sizeof(T)` |
| `nullptr` | 空指针 | `NULL` |

---

## 五、Struct 与 Union

C 结构体在 Dart 侧用继承 `Struct` 的类表示，字段用 `external` + 类型注解声明。结构体可以按值传参、按值返回：

```dart
import 'dart:ffi';

final class Point extends Struct {
  @Double()
  external double x;

  @Double()
  external double y;
}

// @Packed(n) 取消对齐填充，必须与 C 侧一致
@Packed(1)
final class Packet extends Struct {
  @Uint8()
  external int tag;
  @Uint32()
  external int payload;        // 无填充时偏移为 1
}

void main() {
  print(sizeOf<Point>());      // 16
  print(sizeOf<Packet>());     // 5（默认对齐下是 8）
}
```

字段类型规则：结构体字段只能用原生类型、`Pointer<T>` 或其他 `Struct`/`Union`；嵌套数组用 `@Array(n)`，如 `@Array(4) external Array<Double> values;` 对应 `double values[4]`。`Union` 与 `Struct` 声明方式相同，区别是所有字段共享同一段内存，大小等于最大字段。**结构体定义必须与 C 侧逐字节一致**（字段顺序、类型、对齐），否则读写会错位。

---

## 六、C 字符串与 Dart String 的转换

Dart `String` 是 UTF-16 且不可变；C 字符串是 UTF-8 字节序列加 `\0` 结尾。`package:ffi` 提供转换函数：

```dart
import 'package:ffi/ffi.dart';

void main() {
  // Dart -> C：分配内存并写入 UTF-8 字节（含结尾 \0）
  final cStr = 'Hello, 世界'.toNativeUtf8();
  print(cStr.address);              // Pointer<Utf8>

  // C -> Dart：读取到 \0 为止并解码
  final dartStr = cStr.toDartString();
  print(dartStr);                   // Hello, 世界
  malloc.free(cStr);                // 转换分配的内存必须手动释放
}
```

| 转换方向 | API | 内存归属 |
|----------|-----|----------|
| Dart -> C | `str.toNativeUtf8(allocator: malloc)` | 调用方负责 `free` |
| C -> Dart | `ptr.toDartString()` | 返回新 String，原内存仍归 C 方 |
| 字节 -> Dart | `Utf8.decode(bytes)` | 无分配 |
| Dart -> 字节 | `utf8.encode(str)`（`dart:convert`） | 普通 Dart 对象 |

用 `toDartString()` 读到的是**副本**；C 侧之后修改内存不会影响已生成的 Dart 字符串，反之亦然。

---

## 七、回调：让 C 调用 Dart

把 Dart 函数变成 C 可调用的函数指针，需要 `NativeCallable`（Dart 3.1+）。以 libc 的 `qsort` 为例：

```dart
import 'dart:ffi';
import 'package:ffi/ffi.dart';

typedef CompareNative = Int32 Function(Pointer<Void>, Pointer<Void>);
typedef CompareDart = int Function(Pointer<Void>, Pointer<Void>);
typedef QsortNative = Void Function(Pointer<Int32>, Size, Size,
    Pointer<NativeFunction<CompareNative>>);
typedef QsortDart = void Function(Pointer<Int32>, int, int,
    Pointer<NativeFunction<CompareNative>>);

// 回调函数必须是顶层或静态函数，签名与 Native typedef 对应
int compareInts(Pointer<Void> a, Pointer<Void> b) {
  final va = a.cast<Int32>().value;
  final vb = b.cast<Int32>().value;
  return va.compareTo(vb);
}

void main() {
  final libc = DynamicLibrary.process();
  final qsort = libc.lookupFunction<QsortNative, QsortDart>('qsort');

  // isolateLocal：回调在当前 Isolate 执行；返回 int 需给异常返回值
  final callable = NativeCallable<CompareNative>.isolateLocal(
    compareInts,
    exceptionalReturn: 0,
  );

  final data = calloc<Int32>(5);
  for (var i = 0; i < 5; i++) {
    data[i] = [42, 7, 19, 3, 88][i];
  }
  qsort(data, 5, sizeOf<Int32>(), callable.nativeFunction);
  print([for (var i = 0; i < 5; i++) data[i]]);   // [3, 7, 19, 42, 88]

  callable.close();   // 必须关闭，否则泄漏调用桩
  calloc.free(data);
}
```

注意：回调可能在 C 的任意时刻触发，**绝不能让它抛出未捕获异常**（会直接终止进程），因此 `exceptionalReturn` 必须提供。`NativeCallable.listener` 变体用于把回调转发到其他 Isolate，代价是只能返回 `void`。

---

## 八、完整示例：调用自定义 C 库

先写一个 C 库 `native/vector_math.c`：

```c
#include <stdint.h>
#include <math.h>

typedef struct {
    double x;
    double y;
} Vec2;

double vec2_length(Vec2 v) {
    return sqrt(v.x * v.x + v.y * v.y);
}

int32_t sum_array(const int32_t *data, int32_t length) {
    int32_t total = 0;
    for (int32_t i = 0; i < length; i++) {
        total += data[i];
    }
    return total;
}
```

编译成动态库：

```bash
# Linux
gcc -shared -fPIC -O2 -o native/libvector_math.so native/vector_math.c -lm
# macOS（注意库名与后缀不同）
gcc -dynamiclib -O2 -o native/libvector_math.dylib native/vector_math.c -lm
# Windows (MinGW)
gcc -shared -O2 -o native/vector_math.dll native/vector_math.c -lm
```

Dart 侧声明并调用：

```dart
import 'dart:ffi';
import 'dart:io';
import 'package:ffi/ffi.dart';

final class Vec2 extends Struct {
  @Double()
  external double x;

  @Double()
  external double y;
}

typedef Vec2LengthNative = Double Function(Vec2);
typedef Vec2LengthDart = double Function(Vec2);
typedef SumArrayNative = Int32 Function(Pointer<Int32>, Int32);
typedef SumArrayDart = int Function(Pointer<Int32>, int);

void main() {
  final path = Platform.isMacOS
      ? 'native/libvector_math.dylib'
      : 'native/libvector_math.so';
  final lib = DynamicLibrary.open(path);

  final vec2Length =
      lib.lookupFunction<Vec2LengthNative, Vec2LengthDart>('vec2_length');
  final sumArray =
      lib.lookupFunction<SumArrayNative, SumArrayDart>('sum_array');

  // 按值传结构体：calloc 分配，ref 读写字段
  final v = calloc<Vec2>()
    ..ref.x = 3
    ..ref.y = 4;
  print('长度: ${vec2Length(v.ref)}');   // 5.0
  calloc.free(v);

  // 指针参数：分配数组并填充
  final data = calloc<Int32>(4);
  for (var i = 0; i < 4; i++) {
    data[i] = (i + 1) * 10;
  }
  print('求和: ${sumArray(data, 4)}');    // 100
  calloc.free(data);
}
```

`pubspec.yaml` 中需要依赖 `ffi`：

```yaml
dependencies:
  ffi: ^2.1.0
```

---

## 九、Native Assets：下一代打包机制

传统 FFI 要求你手动编译动态库、处理各平台路径、打包时把库塞进产物，CI 配置繁琐。**Native Assets** 是 Dart 正在推进的新机制：在包内写 `hook/build.dart`，构建时由 SDK 自动调用本地工具链编译 C 源码，并保证产物随应用一起打包、在运行时能找到。

```dart
// hook/build.dart（实验性 API，随 SDK 版本可能调整）
import 'package:native_toolchain_c/native_toolchain_c.dart';

Future<void> main(List<String> args) async {
  await CBuilder.library(
    name: 'vector_math',
    assetName: 'vector_math_bindings_generated.dart',
    sources: ['src/vector_math.c'],
  ).run(args);
}
```

当前状态：Native Assets 仍属实验特性，需要较新的 SDK 与 `--enable-experiment=native-assets`；稳定项目仍建议先用传统动态库 + 打包脚本。

---

## 十、内存所有权与泄漏防范

FFI 内存不被 Dart GC 管理，所有权必须显式约定：

| 内存来源 | 谁释放 | 释放方式 |
|----------|--------|----------|
| Dart 侧 `malloc`/`calloc` | Dart | `allocator.free(ptr)` |
| `toNativeUtf8` 分配 | Dart | `malloc.free(ptr)` |
| C 函数返回的 `char*` | 看文档（通常是调用方） | 一般用 C 提供的 `free_xxx` 函数 |
| C 函数内部静态缓冲 | 不释放 | 生命周期由库管理，注意线程安全 |
| `callable.nativeFunction` | Dart | `callable.close()` |

防范清单：每次分配用 `try/finally` 包住释放；把指针封装进 Dart 类并在 `dispose()` 中释放；用 `NativeFinalizer` 在 Dart 对象被 GC 时兜底释放原生资源；在 CI 里跑 AddressSanitizer 编译的 C 库做泄漏检测。

---

## 十一、常见坑

**坑 1：库路径找不到。** `DynamicLibrary.open('libfoo.so')` 在 Linux 上按 `LD_LIBRARY_PATH` 与系统路径搜索，相对路径是相对于**进程工作目录**而非源码目录。发布时把库放进平台约定位置（Android `jniLibs`、macOS Framework、Windows exe 同目录）。

**坑 2：ABI 不匹配。** 把 `int` 声明成 `Int64`、漏写 `Pointer`、结构体对齐不一致，都会导致参数错位或崩溃。对照头文件逐字段核对，必要时用 `sizeOf` 与 C 的 `sizeof` 打印比对。

**坑 3：把 GC 对象的地址传给 C。** Dart 对象会被 GC 移动，`address` 随时失效。需要长期持有内存时必须 `malloc`/`calloc` 分配原生内存，把数据拷进去再传。

**坑 4：回调抛异常。** 回调穿透 C 栈帧的异常无法被 Dart 捕获，直接崩溃。回调内必须 `try/catch` 兜底并返回 `exceptionalReturn`。

**坑 5：忘记 `callable.close()` 与 `malloc.free()`。** 这两类泄漏不会立刻显形，长跑服务里会累积成 OOM 或调用桩耗尽。

---

## 本章小结

| 知识点 | 一句话 |
|--------|--------|
| FFI 定位 | 无需胶水代码直接调 C，开销接近普通调用 |
| 加载方式 | `open` 指定库、`process` 取进程符号、`executable` 取自身 |
| 函数签名 | `Native` typedef 描述 C 侧，`Dart` typedef 描述调用侧 |
| 类型映射 | `Int32` 对 `int32_t`，宽度必须与 C 一致 |
| 指针操作 | `ref`/`value`/`[]`/`cast`/`elementAt`，无指针算术 |
| 结构体 | 继承 `Struct`，`external` 字段，逐字节对齐 C 定义 |
| 字符串 | `toNativeUtf8` 与 `toDartString`，转换内存手动释放 |
| 回调 | `NativeCallable` + 异常返回值，用完 `close` |
| 所有权 | Dart 分配 Dart 释放，C 分配按库文档释放 |
| 泄漏防范 | try/finally、dispose、NativeFinalizer、ASan |

---

## 练习

| 题号 | 题目 | 链接 | 知识点 |
|------|------|------|--------|
| 509 | 斐波那契数 | https://leetcode.cn/problems/fibonacci-number/ | 原生调用、递归 |

- 返回目录：[[dart/dart目录|Dart 教程目录]]
