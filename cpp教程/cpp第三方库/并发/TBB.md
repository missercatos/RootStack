# Intel TBB

"Threading Building Blocks" — Intel 开发的高层并行框架，是 oneAPI 的组成部分。提供并行算法（parallel_for、parallel_reduce、parallel_sort 等）、并发容器、任务调度器和内存分配器。C++17 并行算法部分受 TBB 启发。

## 核心组件

| 组件 | 说明 |
|------|------|
| tbb::parallel_for | 数据并行循环 |
| tbb::parallel_reduce | 并行归约 |
| tbb::parallel_sort | 并行排序 |
| tbb::concurrent_hash_map | 线程安全哈希表 |
| tbb::concurrent_queue | 无锁并发队列 |
| tbb::flow::graph | 数据流图并行 |
| tbb::scalable_allocator | 多线程优化的内存分配器 |

## 何时使用

- 计算密集型应用的并行化
- 数值计算和图像处理的并行加速
- Intel CPU 上有额外优化
- 不想手动管理线程的高层并行

## 关键特性

并行算法、并发容器、任务调度、可扩展内存分配器

## 相关链接

- [[OpenMP|OpenMP]] — 编译器级并行
- [[taskflow|taskflow]] — 任务图并行
- 
- (搜索: Intel oneTBB)
