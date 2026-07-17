
# OpenMP

| 属性 | 说明 |
|------|------|
| 类型 | 编译器支持的共享内存并行编程 |
| 头文件 | `<omp.h>` |
| 编译标志 | `gcc -fopenmp` |

**核心概念**：OpenMP 通过 `#pragma` 指令在 C 代码中标注可并行的循环和区域，编译器自动生成多线程代码。相比 pthreads，OpenMP 是**声明式**而非**命令式**的——告诉编译器"哪些可以并行"，而非"如何创建线程"。

**核心指令**：

```c
/* 并行化 for 循环 */
#pragma omp parallel for
for (int i = 0; i < N; i++)
    result[i] = heavy_compute(data[i]);

/* 并行区域 */
#pragma omp parallel
{
    int tid = omp_get_thread_num();
    printf("Thread %d\n", tid);
}

/* 归约操作 */
int sum = 0;
#pragma omp parallel for reduction(+:sum)
for (int i = 0; i < N; i++)
    sum += array[i];

/* 临界区 */
#pragma omp critical
{
    shared_counter++;
}
```

**核心 API**：

| 函数 | 说明 |
|------|------|
| `omp_get_thread_num` | 获取当前线程编号 |
| `omp_get_num_threads` | 获取总线程数 |
| `omp_set_num_threads` | 设置线程数 |
| `omp_get_wtime` | 获取挂钟时间（秒） |

> OpenMP 最适合**数据并行**——对数组、矩阵做相同操作的循环。对于需要复杂同步模式的并发任务，pthreads 提供更精细的控制。

**跨语言参考**: [[../../../2深化/08_标准库深度|C标准库深度剖析]]
