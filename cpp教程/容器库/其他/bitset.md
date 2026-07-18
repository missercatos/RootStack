---
template <size_t N>
class bitset
---

## 底层数据结构

编译期定长的二进制位数组。每一位占 1 bit，底层通常以 `unsigned long` 数组存储，每 64 位一组进行批量位运算。长度 N 必须是编译期常量。空间仅需 N/8 字节，远优于 `bool[N]`（N 字节）和 `vector<bool>`。

## 复杂度

| 操作 | 复杂度 | 说明 |
|------|--------|------|
| b[i] | O(1) | 读写第 i 位（i=0 为最低位） |
| test(i) | O(1) | 读第 i 位，带越界检查 |
| set / reset / flip | O(n/64) | 批量操作，每 64 位一次 |
| count / any / none / all | O(n/64) | 按组统计 |
| & / \| / ^ | O(n/64) | 按位运算 |
| << / >> | O(n/64) | 移位 |
| to_string / to_ulong | O(n) | 格式转换 |

## 关键方法

| 方法 | 说明 |
|------|------|
| b[i] | 访问第 i 位（最低位 i=0），可读写 |
| b.test(i) | 测试第 i 位是否为 1，越界抛 out_of_range |
| b.set() / b.set(i, v) | 全置 1 / 第 i 位置为 v |
| b.reset() / b.reset(i) | 全置 0 / 第 i 位置 0 |
| b.flip() / b.flip(i) | 全翻转 / 第 i 位翻转 |
| b.size() | 总位数（编译期常量） |
| b.count() | 值为 1 的位数 |
| b.any() / b.none() / b.all() | 存在 1 / 全 0 / 全 1 |
| ~b / b1 & b2 / b1 \| b2 / b1 ^ b2 | 取反/与/或/异或 |
| b << n / b >> n | 左移/右移 n 位 |
| b.to_string() | 转二进制串（高位在前） |
| b.to_ulong() / b.to_ullong() | 转无符号整数 |

## 伪代码示例

```
bitset<8> bs

// 置位（最低位是第 0 位）
bs.set(0)                // bit 0 = 1
bs.set(3, 1)             // bit 3 = 1
bs[5] = 1                // bit 5 = 1
print bs                 // 00101001（高位在前）

// 统计
print bs.count()         // 3
print bs.size()          // 8

// 位运算
bs2 = bs << 1            // 左移一位
result = bs & bs2        // 按位与

// 翻转
bs.flip()                // 所有位取反

// 重置
bs.reset()               // 全部清零

// 状态压缩 DP（砝码称重）
bitset<MAX_W+1> dp
dp[0] = 1
for each weight w:
    for each count c:
        dp = dp | (dp << w)

// 可达性：dp[x] = 1 表示能称出重量 x

// 传递闭包（bitset 优化 Floyd）
bitset<N> reach[N]
for each edge u -> v:
    reach[u][v] = 1
for each k in 0..N-1:
    for each i in 0..N-1:
        if reach[i][k]:
            reach[i] = reach[i] | reach[k]
```

## 相关链接

- [[../../../数据结构/A_容器_Container]]
- [[../../../数据结构/A_容器_Container]]
- [[../序列容器/vector]]
