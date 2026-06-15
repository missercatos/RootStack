# C 语言 —— struct / typedef / 宏 / 标准库
## ============================================================

## `struct` 结构体

C 的 struct 是纯数据聚合（无成员函数、无访问控制）：

```c
#include <string.h>

struct Point {
    int x;
    int y;
};

int main(void) {
    // 声明变量时必须写 struct 关键字
    struct Point p1;
    p1.x = 10; p1.y = 20;

    // 初始化
    struct Point p2 = {30, 40};

    // struct 整体赋值（逐字节复制）
    p1 = p2;  // p1.x=30, p1.y=40

    return 0;
}
```

**嵌套管 struct**：

```c
struct Rect {
    struct Point topLeft;
    struct Point bottomRight;
};

struct Rect r = {{0, 0}, {100, 200}};
r.topLeft.x = 10;
```

**自引用 struct（链表节点原型）**：

```c
struct ListNode {
    int              value;
    struct ListNode* next;   // 自引用必须用指针
};
```

> C++ 中 `struct` 关键字在声明变量时可省略（`Point p2{3,4}`），且 struct 支持成员函数、构造/析构、继承。详见 [[../4.5_struct结构体]] 和 [[../05_面向对象(一)类与对象基础]]。

## `typedef` 类型别名

`typedef` 给类型起别名。C 中主要用于简化 struct 声明：

```c
// C 风格：typedef + struct 合写
typedef struct {
    int x;
    int y;
} Point;

Point p = {1, 2};   // 无需写 struct 关键字
```

其他用途：

```c
typedef unsigned int uint;
typedef int*         IntPtr;
typedef int          IntArray[10];   // IntArray 是长度为10的int数组类型

uint   id = 100;
IntPtr p  = &id;

// 函数指针 typedef（最复杂的 typedef 形式）
typedef int (*BinOp)(int, int);      // BinOp 是指向 int(int,int) 函数的指针类型
BinOp op = add;
printf("%d\n", op(3, 5));            // 8
```

> C++ 中 `using` 替代了大部分 `typedef`（`using uint = unsigned int;`），更易读。

## `#define` 宏

预处理器在编译前执行文本替换。宏不是函数，没有类型检查。详见 [[../02_预处理器]]。

```c
#define MAX(a, b) ((a) > (b) ? (a) : (b))  // 函数式宏
#define PI 3.14159                          // 常量宏
#define ARR_SIZE 100                        // 数组大小宏

int arr[ARR_SIZE];
int m = MAX(10, 20);   // 展开为 ((10) > (20) ? (10) : (20))
```

**常见陷阱**：宏只是文本替换，不计算参数：

```c
#define SQUARE(x) x * x     // 错误！
// SQUARE(1+2) 展开为 1+2*1+2 → 1+2+2=5（而非期望的 9）
#define SQUARE(x) ((x)*(x)) // 正确

int n = 5;
#define DOUBLE(x) ((x)+(x))
DOUBLE(++n);               // 展开为 ((++n)+(++n)) → n 被加了2次！
```

> 在 C++ 中，常量用 `constexpr`，函数式宏用 `inline` 函数或模板替代。但 `#define` 在条件编译（`#ifdef DEBUG`）中仍不可或缺，C++ 教程的调试宏多处使用。

## 条件编译

```c
#ifdef DEBUG
    #define LOG(msg) printf("[DEBUG] %s\n", msg)
#else
    #define LOG(msg)
#endif

LOG("start");  // 只有在编译时 -DDEBUG 才输出
```

## C 标准库常用函数

C 标准库函数在 C++ 中同样可用（头文件用 `<c...>` 前缀）：

| 头文件 | 常用函数 | 用途 |
|:-------|:--------|:-----|
| `<stdio.h>` | `printf`, `scanf`, `fopen`, `fclose`, `fread`, `fwrite` | 输入输出 |
| `<stdlib.h>` | `malloc`, `free`, `realloc`, `atoi`, `atof`, `qsort`, `bsearch` | 内存、转换、排序 |
| `<string.h>` | `strlen`, `strcpy`, `strcmp`, `strcat`, `memcpy`, `memset`, `memcmp` | 字符串/内存操作 |
| `<math.h>` | `sqrt`, `pow`, `sin`, `cos`, `abs`, `fabs` | 数学 |
| `<ctype.h>` | `isalpha`, `isdigit`, `isspace`, `toupper`, `tolower` | 字符分类 |
| `<time.h>` | `time`, `clock`, `difftime` | 时间 |
| `<assert.h>` | `assert` | 断言 |

```c
#include <stdlib.h>
#include <string.h>

// 内存复制
int src[5] = {1, 2, 3, 4, 5};
int dst[5];
memcpy(dst, src, 5 * sizeof(int));  // 逐字节复制 20 字节

// 内存清零
int arr[100];
memset(arr, 0, sizeof(arr));        // 全部置 0

// 字符串比较
int cmp = strcmp("hello", "world");  // <0（h < w）
```

> `memcpy` 只适用于 trivially copyable 类型（如 `int`、C struct）。C++ 含虚表指针或非 trivial 成员的对象不能用 `memcpy` 复制。
