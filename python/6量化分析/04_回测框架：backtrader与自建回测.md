# 回测框架：backtrader 与自建回测 (Backtesting)
---

## 📖 章节概述

回测是量化分析的核心——用历史数据模拟策略表现，回答"如果当时用了这个策略，会赚多少？"本章分两条线：先用 backtrader 快速搭建一个完整的移动均线交叉策略回测系统；然后用 NumPy/Pandas 从零手写一个最小回测引擎，让你看清回测的底层循环逻辑。最后讨论为什么回测的"核心循环"可能是性能瓶颈，以及何时需要用 Cython 或 C 来加速。

> **核心理念**：回测的本质是**时间序列的前向迭代**。在 C 语言中，回测就是一个 `for (i = 0; i < n; i++)` 循环，每次迭代更新持仓、计算盈亏、检查信号。backtrader 把这个循环封装成了"事件驱动"的黑箱，让你只关注策略逻辑。但理解底层循环的细节，对 C 程序员来说是必须的——你迟早会需要自建回测以追求更极致的性能。

---

### 📚 第一节：backtrader 快速上手

#### 1.1 安装与核心概念

```bash
pip install backtrader matplotlib
```

backtrader 的四大核心：

| 组件 | 作用 | C 类比 |
|------|------|--------|
| `Cerebro` | 回测引擎（大脑） | `main()` 函数 |
| `Strategy` | 交易策略 | 业务逻辑 |
| `Data Feed` | 数据源 | 数组输入 |
| `Broker` | 模拟券商（手续费、滑点） | 交易执行 |

#### 1.2 第一个 backtrader 策略：SMA 均线交叉

```bash
python -c "
import backtrader as bt
import datetime

# 1. 定义策略
class SmaCross(bt.Strategy):
    params = (
        ('fast', 10),   # 快线周期
        ('slow', 30),   # 慢线周期
    )
    
    def __init__(self):
        # 计算两条均线
        self.fast_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.fast
        )
        self.slow_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.slow
        )
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
    
    def next(self):
        # 每个 bar 调用一次
        if not self.position:  # 未持仓
            if self.crossover > 0:  # 金叉 → 买入
                self.buy()
        elif self.crossover < 0:  # 死叉 → 卖出
            self.sell()

# 2. 创建 Cerebro 引擎
cerebro = bt.Cerebro()
cerebro.addstrategy(SmaCross)

# 3. 加载数据
data = bt.feeds.YahooFinanceData(
    dataname='AAPL',
    fromdate=datetime.datetime(2023, 1, 1),
    todate=datetime.datetime(2024, 1, 1)
)
cerebro.adddata(data)

# 4. 设置初始资金
cerebro.broker.setcash(100000.0)

# 5. 运行回测
print(f'Starting Portfolio Value: {cerebro.broker.getvalue():.2f}')
cerebro.run()
print(f'Final Portfolio Value: {cerebro.broker.getvalue():.2f}')
"
```

#### 1.3 理解 `next()` 的调用过程

`next()` 在每个时间步被调用一次——这等价于 C 代码中的循环体：

```c
// C 语言等价逻辑
for (int i = slow_period; i < n; i++) {
    double fast_ma = calc_sma(close, i, fast_period);
    double slow_ma = calc_sma(close, i, slow_period);
    
    int crossover = (fast_ma > slow_ma) ? 1 : (fast_ma < slow_ma) ? -1 : 0;
    
    if (position == 0 && crossover > 0) {
        // buy
        position = 1;
        entry_price = close[i];
    } else if (position > 0 && crossover < 0) {
        // sell
        pnl += close[i] - entry_price;
        position = 0;
    }
}
```

这就是回测引擎的核心循环。backtrader 帮你做了数据对齐、订单管理、手续费计算这些繁重工作。

#### 1.4 分析回测结果

```bash
python -c "
import backtrader as bt
import backtrader.analyzers as btanalyzers

class SmaCross(bt.Strategy):
    params = (('fast', 10), ('slow', 30))
    
    def __init__(self):
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.params.fast)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.params.slow)
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
    
    def next(self):
        if not self.position:
            if self.crossover > 0:
                self.buy()
        elif self.crossover < 0:
            self.sell()

print('Strategy defined. In practice, add analyzers:')
print('  cerebro.addanalyzer(btanalyzers.SharpeRatio, _name=\"sharpe\")')
print('  cerebro.addanalyzer(btanalyzers.DrawDown, _name=\"drawdown\")')
print('  cerebro.addanalyzer(btanalyzers.Returns, _name=\"returns\")')
"
```

常用分析器：

| 分析器 | 指标 | 含义 |
|--------|------|------|
| `SharpeRatio` | 夏普比率 | 风险调整后收益 |
| `DrawDown` | 最大回撤 | 从高点到低点的最大跌幅 |
| `Returns` | 总收益率 | 策略总收益 |
| `TradeAnalyzer` | 交易统计 | 胜率、盈亏比 |
| `SQN` | 系统质量指数 | 综合评分 |
| `VWR` | 可变权重收益 | 多种收益指标 |

---

### 📚 第二节：自建回测引擎 —— 理解底层循环

#### 2.1 为什么自建回测

backtrader 功能强大但有其局限：
- 事件驱动架构有开销，大数据集上慢
- 不支持向量化回测（一次计算所有信号）
- 定制复杂逻辑时框架成为约束

对于 C 程序员，自建回测让你完全掌控循环逻辑和内存布局——正是性能优化的起点。

#### 2.2 向量化回测核心

```bash
python -c "
import numpy as np
import pandas as pd

# 生成模拟数据
np.random.seed(42)
n = 1000
close = 100 + np.cumsum(np.random.randn(n) * 2)
dates = pd.date_range('2024-01-01', periods=n, freq='B')
df = pd.DataFrame({'close': close, 'date': dates})

# 策略：10/30 均线交叉
df['fast_sma'] = df['close'].rolling(10).mean()
df['slow_sma'] = df['close'].rolling(30).mean()

# 信号：1=持多, 0=空仓
df['signal'] = 0
df.loc[df['fast_sma'] > df['slow_sma'], 'signal'] = 1
df.loc[df['fast_sma'] < df['slow_sma'], 'signal'] = 0

# 日收益率
df['return'] = df['close'].pct_change()
# 策略收益：只有持仓时才获得收益
df['strategy_return'] = df['signal'].shift(1) * df['return']

# 累计收益
df['cum_return'] = (1 + df['strategy_return'].fillna(0)).cumprod()
df['buy_hold_return'] = (1 + df['return'].fillna(0)).cumprod()

print(f'Strategy final: {df[\"cum_return\"].iloc[-1]:.4f}')
print(f'Buy & Hold:   {df[\"buy_hold_return\"].iloc[-1]:.4f}')
print(f'Sharpe: {df[\"strategy_return\"].mean() / df[\"strategy_return\"].std() * np.sqrt(252):.3f}')
"
```

#### 2.3 事件驱动回测核心（纯 NumPy）

```bash
python -c "
import numpy as np

def simple_backtest(close, fast_window=10, slow_window=30, 
                    initial_capital=100000.0, commission=0.0003):
    n = len(close)
    
    # 预计算均线（用 np.convolve 或 rolling mean）
    fast_sma = np.array([np.mean(close[max(0, i-fast_window+1):i+1]) 
                         for i in range(n)])
    slow_sma = np.array([np.mean(close[max(0, i-slow_window+1):i+1]) 
                         for i in range(n)])
    
    position = 0      # 当前持仓股数
    cash = initial_capital
    equity = np.zeros(n)
    trades = []
    
    for i in range(slow_window, n):
        signal = 0
        if fast_sma[i] > slow_sma[i] and fast_sma[i-1] <= slow_sma[i-1]:
            signal = 1   # 金叉
        elif fast_sma[i] < slow_sma[i] and fast_sma[i-1] >= slow_sma[i-1]:
            signal = -1  # 死叉
        
        if signal == 1 and position == 0:
            # 全仓买入
            position = cash * (1 - commission) / close[i]
            cash = 0
            trades.append(('BUY', i, close[i]))
        elif signal == -1 and position > 0:
            # 全仓卖出
            cash = position * close[i] * (1 - commission)
            position = 0
            trades.append(('SELL', i, close[i]))
        
        equity[i] = cash + position * close[i]
    
    return equity, trades

# 测试
np.random.seed(1)
close = 100 + np.cumsum(np.random.randn(500) * 2)
close = np.maximum(close, 10)

equity, trades = simple_backtest(close)
print(f'Final equity: {equity[-1]:.2f}')
print(f'Trades: {len(trades)}')
print(f'Max drawdown (rough): {(1 - np.min(equity) / np.max(np.maximum.accumulate(equity))):.2%}')
"
```

#### 2.4 性能考察：Python 循环的开销

上面的回测使用了 Python 的 `for` 循环，在 10 万行数据上可能需要数秒。对于高频回测或多参数寻优，这是不可接受的：

```bash
python -c "
import numpy as np
import time

n = 200_000
close = 100 + np.cumsum(np.random.randn(n) * 2)

def backtest_python_loop(close):
    n = len(close)
    fast_sma = np.zeros(n)
    slow_sma = np.zeros(n)
    # 计算均线
    for i in range(9, n):
        fast_sma[i] = np.mean(close[i-9:i+1])
    for i in range(29, n):
        slow_sma[i] = np.mean(close[i-29:i+1])
    
    equity = np.zeros(n)
    cash = 100000.0
    position = 0.0
    for i in range(30, n):
        # 信号判断 + 交易逻辑
        if fast_sma[i] > slow_sma[i] and position == 0:
            position = cash / close[i]
            cash = 0
        elif fast_sma[i] < slow_sma[i] and position > 0:
            cash = position * close[i]
            position = 0
        equity[i] = cash + position * close[i]
    return equity

t0 = time.time()
equity = backtest_python_loop(close)
t1 = time.time()
print(f'Python loop on {n} bars: {t1 - t0:.3f}s')
print(f'That is {(t1 - t0) * 1000 / n:.3f} ms per bar')
print()
print('For 1M bars or parameter optimization, this becomes infeasible.')
print('→ Cython or C acceleration needed (see Chapter 06)')
"
```

---

### 📚 第三节：回测中的常见陷阱

#### 3.1 前视偏差（Look-ahead Bias）

**错误**：在时刻 t 使用了 t+1 才能知道的数据。

```python
# 错误示例：用全序列的最大值做归一化
normalized = close / close.max()  # 用了未来的价格

# 正确：用滚动窗口
normalized = close / close.rolling(252).max()  # 只用过去一年数据
```

#### 3.2 幸存者偏差（Survivorship Bias）

使用当前存在的股票列表做历史回测，忽略了那些已经退市的股票。应使用历史成分股数据。

#### 3.3 交易成本

手续费、滑点、涨跌停限制、流动性——这些在真实交易中是存在的，回测时必须建模：

```python
# 简化版交易成本
def apply_cost(price, volume, commission_rate=0.0003, slippage=0.001):
    # 手续费 + 滑点（买入时价格打高，卖出时打低）
    impact = price * (1 + slippage) if volume > 0 else price * (1 - slippage)
    fee = abs(price * volume * commission_rate)
    return impact, fee
```

---

### 📝 小节练习

> [!question] 选择题 1
> backtrader 中 `Strategy.next()` 方法在什么时候被调用？
> - [ ] A. 策略初始化时调用一次
> - [ ] B. 每个交易信号产生时调用
> - [ ] C. 数据的每一行（每个 bar）上调用一次
> - [ ] D. 回测结束时调用
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: `next()` 是回测主循环的"循环体"——数据的每一个时间步都会调用一次。它等价于 C 中的 `for` 循环体。`__init__` 是初始化，`next` 是迭代，`stop` 是收尾。

> [!question] 判断题 1
> 向量化回测总是比事件驱动回测快。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 向量化回测对简单策略确实更快（因为用 NumPy 批量操作），但对于有状态依赖的复杂策略（如需要跟踪持仓成本、止损、仓位管理等），事件驱动回测更自然，且不一定会更慢。

---

## 📋 章节测试

### 一、判断题

> [!question] 判断题 1
> backtrader 的 Cerebro 是回测的核心引擎，负责协调数据、策略、券商和分析器。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: Cerebro（西班牙语"大脑"）是 backtrader 的中心调度器。它负责数据加载、策略注册、订单路由、分析器管理和最终结果汇总。

> [!question] 判断题 2
> 在回测中使用全序列归一化（除以全序列最大值）不会引入前视偏差。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 这是典型的前视偏差。在 t 时刻，你不能知道整个序列的最大值（它可能出现在未来）。应使用滚动窗口（只在 t 及之前的数据内归一化）。

> [!question] 判断题 3
> backtrader 默认会自动考虑交易手续费。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: backtrader 默认手续费率为 0。需要显式设置：`cerebro.broker.setcommission(commission=0.001)` 来模拟真实的交易成本。

> [!question] 判断题 4
> 回测中的"幸存者偏差"是指回测数据缺少历史退市股票的问题。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 幸存者偏差是量化回测中最隐蔽的陷阱之一。如果只用当前还在上市的股票做历史回测，会系统性高估策略表现——因为"活下来"的股票本身就是表现较好的。

> [!question] 判断题 5
> NumPy 的 `np.mean` 可以直接替代 Pandas 的 rolling mean，没有性能差异。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: Pandas 的 `.rolling().mean()` 底层使用 Cython 实现的滚动窗口算法，复杂度 O(n)。用 `np.mean` 在 for 循环中手动计算每个窗口复杂度是 O(n*window)。对大数据差异可达数十倍。

> [!question] 判断题 6
> 自建回测引擎的最大优势是可以完全控制内存布局和循环逻辑以追求极致性能。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 成熟的回测框架为了通用性牺牲了性能。自建引擎可以根据策略特点定制数据结构和计算流程，特别是在用 Cython/C 重写核心循环后，可以达到数百万 bar/s 的处理速度。

---

### 二、选择题

> [!question] 选择题 1
> backtrader 中添加数据源使用的方法是？
> - [ ] A. `cerebro.adddata()`
> - [ ] B. `cerebro.feed()`
> - [ ] C. `strategy.adddata()`
> - [ ] D. `broker.adddata()`
>
> > [!success]- 点击查看答案
> > 正确答案: A
> > **解析**: 使用 `cerebro.adddata(feed)` 将数据源添加到 Cerebro 引擎。数据被注册后，所有策略都可以通过 `self.datas[0]` 或 `self.data0` 访问（多数据源时按添加顺序访问）。

> [!question] 选择题 2
> Moving Average Crossover 策略中，"死叉"是指？
> - [ ] A. 快线向下穿过慢线
> - [ ] B. 快线向上穿过慢线
> - [ ] C. 价格向下穿过均线
> - [ ] D. 均线走平无交叉
>
> > [!success]- 点击查看答案
> > 正确答案: A
> > **解析**: 金叉 = 快线从下方向上穿透慢线（买入信号），死叉 = 快线从上方向下穿透慢线（卖出信号）。

> [!question] 选择题 3
> 以下哪个指标最常用于衡量策略的风险调整后收益？
> - [ ] A. 总收益率
> - [ ] B. 最大回撤
> - [ ] C. 夏普比率
> - [ ] D. 胜率
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: 夏普比率 = (年化收益率 - 无风险利率) / 年化波动率，统一度量了收益与风险。总收益率只看收益不管风险，最大回撤只看风险，胜率只看交易不看出场盈亏大小。

> [!question] 选择题 4
> Python 的 for 循环在回测中成为瓶颈时，首选的优化手段是？
> - [ ] A. 使用 PyPy 解释器
> - [ ] B. 使用更多 Python 线程
> - [ ] C. 用 Cython/C 重写核心循环
> - [ ] D. 使用 async 异步编程
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: 回测的瓶颈是纯数值计算（均线、信号判断、盈亏累计），Python 循环的数值计算比 C 慢 50-100 倍。用 Cython 加类型声明或直接用 C 写核心循环是最有效的优化手段。线程因 GIL 无效，PyPy 改善有限，async 对 CPU 密集型无用。

> [!question] 选择题 5
> backtrader 中，`self.position` 在策略代码里表示什么？
> - [ ] A. 当前持仓数量（浮点数/整数）
> - [ ] B. 当前持仓市值
> - [ ] C. 当前持仓盈亏
> - [ ] D. 可用资金
>
> > [!success]- 点击查看答案
> > 正确答案: A
> > **解析**: `self.position` 是一个 Position 对象，`if not self.position` 检测是否有持仓。`.size` 属性返回持仓数量，`.price` 返回均价。`bool(self.position)` 在持仓时为 True。

> [!question] 选择题 6
> 自建回测引擎中，以下哪种方式计算累计收益率最高效？
> - [ ] A. for 循环逐个乘
> - [ ] B. `np.cumprod(1 + returns)`
> - [ ] C. `pd.Series(returns).cumprod()`
> - [ ] D. 递归调用
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `np.cumprod(1 + returns)` 调用了 NumPy 的 C 实现，一次完成所有累积乘积计算。Pandas 的 `cumprod()` 底层也是调 NumPy。for 循环逐个乘是最慢的。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：SMA 参数网格搜索
> **难度**: ⭐⭐
>
> 使用 backtrader 对 SmaCross 策略做参数优化：快线周期从 5 到 50（步长 5），慢线周期从 20 到 200（步长 20）。对每组参数运行回测，记录夏普比率和最大回撤，绘制参数 vs 表现的热力图。使用 `cerebro.optstrategy()` 方法。

> [!example] 练习题 2：从零实现向量化回测
> **难度**: ⭐⭐⭐
>
> 不依赖 backtrader，用 Pandas/NumPy 实现一个完整的向量化回测系统，包含：
> 1. 信号计算（可以是任意自定义规则）
> 2. 每日持仓更新
> 3. 交易成本（手续费 0.03% + 滑点 0.1%）
> 4. 累计收益曲线计算
> 5. 夏普比率和最大回撤计算
>
> 用生成的随机数据测试你的引擎。

> [!example] 练习题 3：回测结果对比
> **难度**: ⭐⭐⭐
>
> 用同一份数据、同一个策略（SMA 交叉），分别用 backtrader 和自建引擎执行回测。对比两者的：总收益率、年化波动率、夏普比率、最大回撤。找出结果差异的原因（手续费处理、信号延迟、收盘价 vs 次日开盘价等）。
