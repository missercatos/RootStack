
# pthreads (POSIX Threads)

| 属性 | 说明 |
|------|------|
| 类型 | 系统级线程库，POSIX 标准 (IEEE 1003.1c) |
| 头文件 | `<pthread.h>` |
| 链接 | `-lpthread` (Linux glibc 2.34+ 可省略) |

**核心 API**：

| 分类 | 函数 | 说明 |
|------|------|------|
| 线程管理 | `pthread_create` / `pthread_join` | 创建/等待线程 |
| | `pthread_detach` | 分离线程（结束后自动回收） |
| | `pthread_self` | 获取当前线程 ID |
| 互斥锁 | `pthread_mutex_init` / `destroy` | 初始化/销毁互斥锁 |
| | `pthread_mutex_lock` / `unlock` | 加锁/解锁 |
| | `pthread_mutex_trylock` | 尝试加锁（非阻塞） |
| 条件变量 | `pthread_cond_wait` | 等待条件（释放互斥锁并阻塞） |
| | `pthread_cond_signal` / `broadcast` | 唤醒一个/所有等待线程 |

```c
#include <pthread.h>
void *worker(void *arg) {
    int id = *(int *)arg;
    printf("Thread %d\n", id);
    return NULL;
}
int main(void) {
    pthread_t threads[4];
    int ids[] = {0, 1, 2, 3};
    for (int i = 0; i < 4; i++)
        pthread_create(&threads[i], NULL, worker, &ids[i]);
    for (int i = 0; i < 4; i++)
        pthread_join(threads[i], NULL);
    return 0;
}
```

**编译**：`gcc -pthread main.c`

> pthreads 是共享内存多核编程的基础。互斥锁确保临界区互斥访问，条件变量用于线程间通知（生产者-消费者模式）。

**跨语言参考**: [[../../../2深化/08_标准库深度|C标准库深度剖析]]
