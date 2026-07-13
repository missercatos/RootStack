# OpenMP

编译器层面的并行编程模型，使用 `#pragma omp` 指令标注并行区域。最轻量级的上手方式——只需在 for 循环前加一行 pragma 即可获得多核加速。编译器（GCC/Clang/MSVC）内置支持，无需额外库。

## 核心组件

| 指令 | 说明 |
|------|------|
| #pragma omp parallel | 创建并行线程组 |
| #pragma omp parallel for | 并行化 for 循环 |
| #pragma omp parallel reduction | 并行归约（求和、求积等） |
| #pragma omp critical | 临界区互斥 |
| #pragma omp atomic | 原子操作 |
| #pragma omp barrier | 线程同步屏障 |
| omp_get_thread_num() | 获取当前线程编号 |
| omp_set_num_threads() | 设置线程数量 |

## 何时使用

- 简单循环并行化
- 科学计算和数值模拟
- 快速原型中的并行化
- 不想引入任何第三方依赖的最轻量方案
- 适合"先跑起来再优化"的快速迭代

## 关键特性

零依赖(编译器内置)、pragma 指令式、简单直观、数据并行首选

## 相关链接

- [[TBB|Intel TBB]] — 高层次并行框架
- [[taskflow|taskflow]] — 任务图并行
- [[../../c语言教程/库大全/第三方库/相关文件|C 第三方库]]
- [[../索引|库索引]]
- (搜索: OpenMP C++)
