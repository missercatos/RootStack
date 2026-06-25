# STL 容器速通 — bitset (位集)

bitset 是固定长度的二进制位数组，每一位只占 1 bit。它在编译期确定长度，支持完整的位运算（与、或、异或、取反、移位）以及一批方便的成员函数，是做状态压缩、集合运算、筛法标记和可达性 DP 的利器。由于每 64 位一组批量处理，许多操作的复杂度是 O(n/64)，比逐位处理快得多。

## 一、优缺点

| 优点 | 缺点 |
|------|------|
| 每位仅占 1 bit，比 bool 数组省约 8 倍内存 | 长度是模板参数，必须编译期确定 |
| 位运算批量处理，复杂度 O(n/64) | 不支持运行时动态改变大小 |
| 接口丰富（set/reset/flip/count 等） | 不支持算术运算（加减乘除） |
| 可直接 cout 输出二进制串 | 没有迭代器，不能用范围 for 遍历 |

## 二、适用场景

| 场景 | 说明 |
|------|------|
| 状态压缩 DP | 用位表示物品选取状态 |
| 集合运算 | 并集、交集、子集判定，O(n/64) |
| 筛法 / 标记 | 比 `vector<bool>` 更高效，每 bit 存一个标记 |
| 可达性 / 背包 DP | `dp |= dp << k` 一次完成转移 |
| 图的矩阵运算 | 邻接矩阵压缩、传递闭包（Floyd 优化为 O(n^3/64)） |

## 三、成员函数总览

| 函数 | 说明 |
|------|------|
| `b[i]` | 访问第 i 位（可读写，i=0 为最低位） |
| `b.test(i)` | 测试第 i 位是否为 1（越界抛 out_of_range） |
| `b.set()` / `b.set(i, v)` | 全部置 1 / 第 i 位置为 v |
| `b.reset()` / `b.reset(i)` | 全部置 0 / 第 i 位置 0 |
| `b.flip()` / `b.flip(i)` | 全部翻转 / 第 i 位翻转 |
| `b.size()` | 总位数（编译期固定） |
| `b.count()` | 值为 1 的位的个数 |
| `b.any()` / `b.none()` / `b.all()` | 是否存在 1 / 是否全 0 / 是否全 1 |
| `~b`、`b1 & b2`、`b1 \| b2`、`b1 ^ b2` | 取反、与、或、异或 |
| `b << n` / `b >> n` | 左移 / 右移 n 位 |
| `b.to_string()` | 转为 string（高位在前） |
| `b.to_ulong()` / `b.to_ullong()` | 转为 unsigned long / unsigned long long |
| `b._Find_first()` / `b._Find_next(i)` | 第一个 1 / i 之后第一个 1（GCC 扩展，非标准） |

## 四、动手实践（渐进操作）

下面按"创建 → 统计 → 置位 → 访问 → 修改 → 复位 → 位运算与移位 → 遍历 → 转换 → 清空"的顺序逐步练习。每一步只给提示与陷阱，请你对照"成员函数总览"自己把代码敲出来。

### 步骤 1：创建

> [!tip] 自己动手
> 函数：包含头文件 `<bitset>`；常见构造有默认全 0 的 `bitset<8> b`、用整数初始化的 `bitset<8>(42)`、用字符串初始化的 `bitset<8>(string("1100"))`。
> 陷阱：模板参数 N 必须是编译期常量，`int n; cin>>n; bitset<n>` 是非法的；需要运行时长度请改用 `vector<bool>` 或 `boost::dynamic_bitset`。字符串初始化是低位对齐到右端。

### 步骤 2：统计（size / count / any / none / all）

> [!tip] 自己动手
> 函数：`size()` 取总位数，`count()` 取 1 的个数，`any()` 判断是否存在 1，`none()` 判断是否全 0，`all()` 判断是否全 1。
> 陷阱：bitset 没有 `empty()`，"是否为空（全 0）"要用 `none()`；`size()` 是编译期固定的总位数，不随置位变化。

### 步骤 3：置位（插入）

> [!tip] 自己动手
> 函数：`set()` 把全部位置 1；`set(i)` 把第 i 位置 1；`set(i, v)` 把第 i 位置为 v；也可直接 `b[i] = 1`。
> 陷阱：bitset 长度固定，没有"插入新元素"的概念，所谓"插入"就是把某位置 1；`set(i)` 越界会抛异常，`b[i]` 越界则是未定义行为。

### 步骤 4：访问

> [!tip] 自己动手
> 函数：`b[i]` 直接读第 i 位（最快），`b.test(i)` 读第 i 位且带越界检查。
> 陷阱：`b[0]` 是最低位（最右），不是最高位；`test(i)` 越界抛 `out_of_range`，`b[i]` 越界是未定义行为，注意二者取舍。

### 步骤 5：修改

> [!tip] 自己动手
> 函数：`flip()` 翻转全部位，`flip(i)` 翻转第 i 位；`set(i, v)` 把第 i 位改成指定值；`b[i] = v` 也能改。
> 陷阱：flip 是按位取反，不是清零；想把某位改成确定值用 `set(i,v)` 比先判断再 flip 更稳妥。

### 步骤 6：复位（删除）

> [!tip] 自己动手
> 函数：`reset(i)` 把第 i 位置 0（相当于"删除"该标记），`reset()` 把全部位置 0。
> 陷阱：bitset 不能真正删除某一位使长度变短，"删除"只能理解为把该位清 0；越界的 `reset(i)` 会抛异常。

### 步骤 7：位运算与移位

> [!tip] 自己动手
> 函数：`~b` 取反；`b1 & b2`、`b1 | b2`、`b1 ^ b2` 做交并对称差；`b << n`、`b >> n` 移位。
> 陷阱：参与 `&` `|` `^` 的两个 bitset 长度（模板参数 N）必须相同，否则无法编译；左移时高位溢出会被丢弃。

### 步骤 8：遍历

> [!tip] 自己动手
> 函数：bitset 没有迭代器，用下标循环 `for (i=0; i<b.size(); i++)` 配合 `b[i]` 即可遍历；只想找出所有为 1 的位时，GCC 下可用 `_Find_first()` 配合 `_Find_next(i)` 跳着遍历，更快。
> 陷阱：不能用范围 for（`for (auto x : b)` 不合法）；`_Find_first` / `_Find_next` 是 GCC 扩展，非标准，跨编译器时需谨慎。

### 步骤 9：转换

> [!tip] 自己动手
> 函数：`to_string()` 转二进制字符串（高位在前），`to_ulong()` / `to_ullong()` 转无符号整数。
> 陷阱：若 bitset 的值超出目标整型的范围，`to_ulong()` / `to_ullong()` 会抛 `overflow_error`，转换大 bitset 前要确认值在范围内。

### 步骤 10：清空

> [!tip] 自己动手
> 函数：`reset()` 不带参数即把所有位清 0，等价于清空。
> 陷阱：bitset 的"清空"只是全部置 0，长度（size）不会变；它本来就没有 `clear()` 这种成员。

## 五、经典实战

### 选数（洛谷 P1036，用 bitset 表示子集）

```cpp
#include <iostream>
#include <bitset>
using namespace std;

int a[21], n, k, ans;

bool isPrime(int x) {
    if (x < 2) return false;
    for (int i = 2; i * i <= x; i++)
        if (x % i == 0) return false;
    return true;
}

int main() {
    cin >> n >> k;
    for (int i = 0; i < n; i++) cin >> a[i];
    for (int mask = 0; mask < (1 << n); mask++) {
        bitset<21> b(mask);
        if (b.count() != k) continue;   // 恰好选 k 个
        int sum = 0;
        for (int i = 0; i < n; i++)
            if (b[i]) sum += a[i];
        if (isPrime(sum)) ans++;
    }
    cout << ans << endl;
    return 0;
}
```

### 砝码称重（洛谷 P2347，bitset 优化可达性 DP）

```cpp
#include <iostream>
#include <bitset>
using namespace std;

int cnt[7];
int w[7] = {0, 1, 2, 3, 5, 10, 20};

int main() {
    for (int i = 1; i <= 6; i++) cin >> cnt[i];
    bitset<1001> dp;
    dp[0] = 1;
    for (int i = 1; i <= 6; i++)
        for (int j = 0; j < cnt[i]; j++)
            dp |= dp << w[i];           // 一次转移所有可达重量
    cout << "Total=" << dp.count() - 1 << endl; // 减掉重量 0
    return 0;
}
```

### 货币系统（洛谷 P5020）

```cpp
#include <iostream>
#include <algorithm>
#include <bitset>
using namespace std;

int a[105];

int main() {
    int T;
    cin >> T;
    while (T--) {
        int n;
        cin >> n;
        for (int i = 0; i < n; i++) cin >> a[i];
        sort(a, a + n);                 // 升序处理
        bitset<25001> dp;
        dp[0] = 1;
        int ans = 0;
        for (int i = 0; i < n; i++) {
            if (!dp[a[i]]) ans++;       // 不能被更小面额凑出，必须保留
            dp |= dp << a[i];           // 更新所有可凑出的金额
        }
        cout << ans << endl;
    }
    return 0;
}
```

## 六、推荐练习题目

| 题号 | 平台 | 题目 | 核心考察 | 难度 |
|------|------|------|---------|------|
| P1036 | 洛谷 | 选数 | bitset 表示子集 + 枚举 | 普及- |
| P2347 | 洛谷 | 砝码称重 | bitset 优化可达性 DP | 普及/提高- |
| P5020 | 洛谷 | 货币系统 | bitset 优化完全背包 | 提高+/省选- |
| 78 | 力扣 | 子集 | 状态枚举 / 位表示 | 中等 |
| P1466 | 洛谷 | 集合 Subset Sums | bitset 优化子集和 DP | 普及/提高- |
| 191 | 力扣 | 位 1 的个数 | popcount / count() | 简单 |
| 268 | 力扣 | 丢失的数字 | 位运算 / 状态标记 | 简单 |

## 七、自己动手

> [!question] 练习题 1
> 给定 n 种砝码（每种可用多次）和目标重量 W，判断能否恰好称出 W，能输出 YES 否则 NO。
>
> 提示：用 `bitset<W+1>` 当 dp，初始 `dp[0]=1`；对每种砝码 w 反复 `dp |= dp << w`（可用次数有限则按次数循环），最后看 `dp[W]` 是否为 1。
> 陷阱：bitset 长度是编译期常量，要按题目上界开足够大；判断结果用 `dp[W]` 或 `dp.test(W)`，别忘了越界风险。

> [!question] 练习题 2
> 给定 n 个集合（元素取值在 [0, 999]），多次查询两个集合交集的大小。
>
> 提示：每个集合用 `bitset<1000>` 表示，元素 x 出现就 `b[x]=1`；查询时把两个 bitset 做 `&`，再用 `count()` 取交集大小。
> 陷阱：参与 `&` 的两个 bitset 模板参数必须相同；元素下标不要越过 999，否则越界。

> [!question] 练习题 3
> 求 n 个顶点有向图的传递闭包，输出最终可达矩阵中 1 的总数。
>
> 提示：每个顶点的可达集合用一行 `bitset<n上界>` 表示；按 Floyd 思路枚举中转点 k，对每个能到 k 的顶点 i 执行 `reach[i] |= reach[k]`。
> 陷阱：要把 k 放在最外层循环（与普通 Floyd 一致），否则结果不完整；最后统计总数用每行 `count()` 累加。

## 八、知识网络

- 上一容器：[[容器类/12_unordered_map_multimap]] | 返回：[[目录]]
- 相关：[[算法技巧/暴力枚举]] | [[算法技巧/下标技巧]]
