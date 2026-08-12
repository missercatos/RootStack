---
title: "C++ 功能库 — random"
---

## 概述

C++ `<random>` 库将随机数生成器与概率分布解耦——生成器(engine)产生均匀分布的伪随机比特，分布(distribution)将其映射到目标概率分布。这解决了 C 中 `rand() % N` 的偏差问题和分布单一问题。

推荐工作流：用 `random_device` 取真随机种子 → 初始化 `mt19937` 生成器 → 用分布对象产生目标分布的值。

## 核心组件

### 生成器

| 组件 | 说明 |
|------|------|
| `random_device` | 硬件熵源，真随机（或接近真随机），仅用于种子 |
| `mt19937` | 梅森旋转，周期 2^19937-1，标准选择 |
| `mt19937_64` | 64 位版本 |
| `minstd_rand` | 最小标准线性同余，体积小但周期短 |
| `default_random_engine` | 平台默认生成器 |

### 分布

| 分布 | 说明 |
|------|------|
| `uniform_int_distribution` | 均匀整数分布 [a, b]（闭区间） |
| `uniform_real_distribution` | 均匀实数分布 [a, b)（左闭右开） |
| `normal_distribution` | 正态(高斯)分布，指定均值与标准差 |
| `bernoulli_distribution` | 伯努利分布（true/false），指定 true 概率 |
| `discrete_distribution` | 离散分布，指定各值的权重 |
| `exponential_distribution` | 指数分布 |
| `poisson_distribution` | 泊松分布 |

## 典型用法

### 基本工作流

```
FUNCTION demo_random:
 rd = RANDOM_DEVICE() // 真随机源
 gen = MT19937(rd()) // 用真随机数做种子

 dice = UNIFORM_INT_DIST(1, 6) // [1, 6] 均匀分布
 FOR i = 1 TO 5:
 PRINT dice(gen) // 每次调用产生新随机数
 END FOR
```

### 各种分布

```
FUNCTION demo_distributions:
 gen = MT19937(RANDOM_DEVICE()())

 uni_real = UNIFORM_REAL_DIST(0.0, 1.0)
 PRINT uni_real(gen) // 0.0 ~ 1.0 均匀浮点

 normal = NORMAL_DIST(70.0, 10.0) // 均值70，标准差10
 PRINT normal(gen) // 接近正态分布值

 coin = BERNOULLI_DIST(0.7) // 70% 概率为 true
 PRINT coin(gen)

 choices = DISCRETE_DIST({1, 3, 6}) // 权重 1:3:6
 PRINT choices(gen) // 索引 2 概率最高
```

### 洗牌

```
FUNCTION demo_shuffle:
 v = [1, 2, 3, 4, 5, 6]
 gen = MT19937(RANDOM_DEVICE()())
 SHUFFLE(v, gen) // 随机打乱
 PRINT v // e.g. [3, 1, 5, 2, 6, 4]
```

### 随机项目选择

```
FUNCTION demo_sample:
 src = [10, 20, 30, 40, 50]
 dst = ARRAY OF SIZE(3)
 gen = MT19937(RANDOM_DEVICE()())
 SAMPLE(src, dst, 3, gen) // 不重复抽样 3 个
```

---

- **时间与种子**: [[chrono|chrono]] — 用 `steady_clock::now()` 做种子
- **数值类型**: [[numeric|numeric]] — `numeric_limits`、`complex`
- **C 对照**: `rand()`/`srand()`（`<stdlib.h>`），存在偏差
- **返回目录**: 
