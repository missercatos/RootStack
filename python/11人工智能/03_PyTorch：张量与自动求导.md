# PyTorch：张量与自动求导 (PyTorch: Tensors & Autograd)
---

## 📖 章节概述

PyTorch 是深度学习的事实标准框架。它的核心只有两个概念：**张量**（Tensor，NumPy 的 GPU 版本）和**自动求导**（Autograd，自动计算梯度）。本章从 C 程序员的视角出发，对比 `torch.Tensor` 与 `numpy.array` 及 C 数组的异同，深入理解自动求导的计算图机制，最后构建一个完整的神经网络训练循环。

> **核心理念**：深度学习训练的本质是"前向传播计算损失 → 反向传播计算梯度 → 梯度下降更新参数"的循环。PyTorch 帮你做了两件事：(1) `Tensor` 把矩阵运算搬到 GPU，比 C 手写循环快 100-1000 倍；(2) `autograd` 自动计算导数，让你不用手动推导反向传播公式。训练完成后，你导出模型给 C++ 程序做推理——推理不需要自动求导，只需要前向传播。

---

### 📚 第一节：torch.Tensor 基础

1.1 张量 vs NumPy 数组 vs C 数组
---------------------------------

```python
import torch
import numpy as np

# C 数组:        float arr[3][4];                          // 栈上的连续内存
# NumPy:         arr = np.zeros((3, 4), dtype=np.float32)  # 堆上分配，C ordered
# PyTorch:       t = torch.zeros(3, 4)                      # 可在 GPU，可跟踪梯度

t = torch.tensor([[1.0, 2.0, 3.0],
                  [4.0, 5.0, 6.0]])
print(f"shape: {t.shape}")          # (2, 3)
print(f"dtype: {t.dtype}")          # torch.float32
print(f"device: {t.device}")        # cpu
print(f"requires_grad: {t.requires_grad}")  # False
```

> **核心差异**：C 的 `float[2][3]` 在栈/堆上分配，形状是编译期常量。PyTorch Tensor 的形状是属性（可 reshape）、dtype 是属性、设备是属性（CPU vs CUDA:0）、梯度跟踪是属性。Tensor 是一个"带元数据的连续内存块指针"，类似 C++ STL 的 `std::vector`。

1.2 张量创建
-------------

```bash
python -c "
import torch
print('zeros :', torch.zeros(2, 3))
print('ones  :', torch.ones(2, 3))
print('randn :', torch.randn(2, 3))    # 标准正态分布
print('arange:', torch.arange(0, 10, 2))  # 像 C 的 for(i=0;i<10;i+=2)
print('linspace:', torch.linspace(0, 1, 5))  # 0 到 1 等分 5 个点
"
```

```bash
# 从 NumPy 转换（共享内存！）
python -c "
import torch, numpy as np
a = np.array([[1.,2.],[3.,4.]])
t = torch.from_numpy(a)
t[0,0] = 99
print('numpy array after torch change:', a)  # [[99. 2.][3. 4.]] — 共享内存！
"
```

> ⚠️ `torch.from_numpy()` 与源数组共享内存，修改 Tensor 会影响原 NumPy 数组。这与 C 中多个指针指向同一块内存类似。

1.3 张量运算与索引
--------------------

```bash
python -c "
import torch
a = torch.tensor([[1.,2.],[3.,4.]])
b = torch.tensor([[5.,6.],[7.,8.]])

print('a + b:', a + b)           # 逐元素加法
print('a @ b:', a @ b)           # 矩阵乘法
print('a * b:', a * b)           # 逐元素乘法（不是点积！）
print('a.sum():', a.sum())       # 所有元素求和
print('a.sum(dim=0):', a.sum(dim=0))  # 沿第0维（行）求和 → (2,)
print('a.sum(dim=1):', a.sum(dim=1))  # 沿第1维（列）求和 → (2,)
print('a.view(4):', a.view(4))   # reshape 为 1D（共享内存）
"
```

1.4 GPU 操作
--------------

```bash
# 检查 GPU 可用性（一行流）
python -c "
import torch
print('CUDA available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('GPU name:', torch.cuda.get_device_name(0))
    t = torch.randn(1000, 1000).cuda()
    print('GPU tensor:', t.device)
    print('Back to CPU:', t.cpu().device)
"
```

```bash
# Apple Silicon (M1/M2/M3)
python -c "
import torch
print('MPS available:', torch.backends.mps.is_available())
"
```

> GPU 注意事项：CPU 和 GPU Tensor 不能直接运算，`cuda_tensor + cpu_tensor` 会报错。需要用 `.cpu()` 或 `.cuda()` 统一设备。在 C 中类比：不能把 GPU 显存地址和 CPU 内存地址传给同一个 `memcpy`。

---

### 📚 第二节：Autograd — 自动求导

2.1 为什么要自动求导
--------------------

假设你有一个函数 `loss = (wx - y)^2`，参数为 `w`。在 C 中你需要手动推导并编码梯度：

```c
// C: 手动求导
float loss = (w * x - y) * (w * x - y);  // loss = (wx - y)²
float dloss_dw = 2 * (w * x - y) * x;    // 手动推导 ∂loss/∂w
w -= lr * dloss_dw;                      // 梯度下降
```

对于有上百万参数的深度神经网络，手动推导梯度是不可能的。PyTorch 的 autograd 自动完成此工作：

```python
# PyTorch: 自动求导
import torch
w = torch.tensor([2.0], requires_grad=True)
x = torch.tensor([3.0])
y_true = torch.tensor([10.0])

loss = (w * x - y_true).pow(2).mean()  # 前向传播
loss.backward()                          # 自动计算所有 requires_grad=True 的梯度
print(f"loss: {loss.item():.4f}")        # 16.0000
print(f"∂loss/∂w: {w.grad.item():.4f}")  # -24.0000 → 2*(6-10)*3 = -24
```

2.2 计算图（Computational Graph）
----------------------------------

每次 Tensor 运算，PyTorch 都在后台构建一个有向无环图（DAG）：

```
w (requires_grad=True) ─┐
                         ├─→ mul(w, x) ─→ sub(mul, y) ─→ pow(sub, 2) ─→ mean() = loss
x                      ─┘         │
y ─────────────────────────────────┘

backward() 沿着这条图反向传播：
loss.grad = 1.0
  → mean 反向: 1.0 / N
    → pow 反向: 2 * (wx - y)
      → sub 反向: 1 (对 wx), -1 (对 y)
        → mul 反向: x (对 w), w (对 x)
          → w.grad = x * 2 * (wx - y) * 1.0 / N
```

每次 `.backward()` 后，计算图被释放（PyTorch 默认行为）。这节省了内存，但意味着不能 `backward()` 两次。如果需要保留，使用 `loss.backward(retain_graph=True)`。

2.3 梯度下降完整循环
--------------------

```python
import torch

# 数据
X = torch.tensor([[1.0], [2.0], [3.0], [4.0]])
Y = torch.tensor([[3.0], [5.0], [7.0], [9.0]])  # Y = 2X + 1

# 参数
w = torch.randn(1, requires_grad=True)
b = torch.randn(1, requires_grad=True)

lr = 0.01
for epoch in range(500):
    # 前向传播
    y_pred = X * w + b              # 计算图开始构建
    loss = ((y_pred - Y) ** 2).mean()

    # 反向传播
    loss.backward()

    # 梯度下降（with torch.no_grad() 防止这些操作进入计算图）
    with torch.no_grad():
        w -= lr * w.grad
        b -= lr * b.grad
        w.grad.zero_()               # 清零梯度，否则会累加
        b.grad.zero_()

    if epoch % 100 == 0:
        print(f"Epoch {epoch:3d}: loss={loss.item():.6f}, w={w.item():.3f}, b={b.item():.3f}")
```

> **C 程序员的关键理解**：`with torch.no_grad():` 关闭自动求导，相当于告诉 PyTorch"下面这段代码只是推理/参数更新，不需要记录到计算图中"。梯度累积（`w.grad += new_grad`）是 PyTorch 的默认行为，所以每次更新后必须 `.zero_()`。这对于习惯手动管理内存的 C 程序员是常见的错误点。

---

### 📚 第三节：nn.Module — 构建神经网络

3.1 把线性回归包装为 Module
----------------------------

```python
import torch
import torch.nn as nn

class LinearRegressor(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(1, 1)    # 输入 1 维，输出 1 维 → y = wx + b

    def forward(self, x):
        return self.linear(x)

model = LinearRegressor()
print(model)
# LinearRegressor(
#   (linear): Linear(in_features=1, out_features=1, bias=True)
# )
```

> `nn.Linear` 内部就是 `W @ x + b`，`W` 和 `b` 自动注册为模型参数（`requires_grad=True`）。你不需要手动创建和追踪它们。

3.2 用 Optimizer 替代手动梯度更新
----------------------------------

```python
import torch
import torch.nn as nn
import torch.optim as optim

X = torch.tensor([[1.0], [2.0], [3.0], [4.0]])
Y = torch.tensor([[3.0], [5.0], [7.0], [9.0]])

model = nn.Linear(1, 1)                        # 等价于 y = wx + b
criterion = nn.MSELoss()                       # 均方误差损失
optimizer = optim.SGD(model.parameters(), lr=0.01)  # 随机梯度下降

for epoch in range(500):
    optimizer.zero_grad()          # 清零梯度（替代 w.grad.zero_()）
    y_pred = model(X)             # 前向传播
    loss = criterion(y_pred, Y)   # 计算损失
    loss.backward()               # 反向传播
    optimizer.step()              # 更新所有参数（替代手动 w -= lr * w.grad）

print(f"w={model.weight.item():.3f}, b={model.bias.item():.3f}")
```

3.3 多层神经网络
-----------------

```python
import torch
import torch.nn as nn

class MLP(nn.Module):
    def __init__(self, in_features, hidden, out_features):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_features, hidden),
            nn.ReLU(),                            # ReLU(x) = max(0, x)
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, out_features),
        )

    def forward(self, x):
        return self.net(x)

model = MLP(in_features=4, hidden=64, out_features=3)
print(f"Parameters: {sum(p.numel() for p in model.parameters())}")

# 模拟输入
x = torch.randn(8, 4)           # batch_size=8, features=4
out = model(x)
print(f"Input: {x.shape} → Output: {out.shape}")  # (8, 4) → (8, 3)
```

3.4 激活函数速查
-----------------

| 激活函数 | 公式 | 用途 |
|---------|------|------|
| ReLU | `max(0, x)` | 隐藏层默认选择 |
| Sigmoid | `1/(1+e^(-x))` | 二分类输出层 |
| Softmax | `e^x_i / Σe^x_j` | 多分类输出层 |
| Tanh | `(e^x - e^(-x))/(e^x + e^(-x))` | RNN / LSTM |
| GELU | `x * Φ(x)` | Transformer（BERT, GPT） |

---

### 📚 第四节：完整训练循环

4.1 分类任务完整示例
--------------------

```python
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# 1. 数据准备
X, y = load_iris(return_X_y=True)
X = StandardScaler().fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)
X_train = torch.tensor(X_train, dtype=torch.float32)
X_test = torch.tensor(X_test, dtype=torch.float32)
y_train = torch.tensor(y_train, dtype=torch.long)
y_test = torch.tensor(y_test, dtype=torch.long)

# 2. 模型定义
class IrisClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(4, 16),
            nn.ReLU(),
            nn.Linear(16, 3),
        )

    def forward(self, x):
        return self.net(x)

model = IrisClassifier()
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

# 3. 训练循环
for epoch in range(200):
    model.train()
    optimizer.zero_grad()
    logits = model(X_train)
    loss = criterion(logits, y_train)
    loss.backward()
    optimizer.step()

    if epoch % 50 == 0:
        model.eval()
        with torch.no_grad():
            preds = model(X_test).argmax(dim=1)
            acc = (preds == y_test).float().mean()
        print(f"Epoch {epoch:3d}: loss={loss.item():.4f}, test_acc={acc:.3f}")

# 4. 最终评估
model.eval()
with torch.no_grad():
    preds = model(X_test).argmax(dim=1)
    acc = (preds == y_test).float().mean()
    print(f"\nFinal test accuracy: {acc:.3f}")
```

4.2 训练循环的标准模板
----------------------

```python
# PyTorch 训练循环固定模板（伪代码）
for epoch in range(epochs):
    # === 训练阶段 ===
    model.train()
    for X_batch, y_batch in train_loader:
        optimizer.zero_grad()        # 清零梯度
        output = model(X_batch)      # 前向传播
        loss = criterion(output, y_batch)  # 计算损失
        loss.backward()              # 反向传播
        optimizer.step()             # 更新参数

    # === 验证阶段 ===
    model.eval()
    with torch.no_grad():            # 验证不需要梯度
        for X_batch, y_batch in val_loader:
            output = model(X_batch)
            # 计算验证指标（accuracy 等）

# === 保存模型 ===
torch.save(model.state_dict(), "model.pth")
```

4.3 模型保存与加载
-------------------

```python
# 保存（推荐：只保存参数，不保存结构）
torch.save(model.state_dict(), "iris_model.pth")

# 加载
model = IrisClassifier()
model.load_state_dict(torch.load("iris_model.pth"))
model.eval()

# 保存整个模型（不推荐：序列化不稳定）
torch.save(model, "iris_full.pth")
```

> **对比 C 操作**：`torch.save(model.state_dict(), "iris_model.pth")` 等价于把每个参数的数组值写入二进制文件。C++ 侧用 libtorch 同样可以加载 `.pth` 文件。

---

### 📝 小节练习

> [!question] 选择题 1
> PyTorch 中 `requires_grad=True` 的作用是？
> - [ ] A. 使张量可以运行在 GPU 上
> - [ ] B. 使张量的梯度被自动计算和记录
> - [ ] C. 加速张量的矩阵运算
> - [ ] D. 使张量变为不可变
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `requires_grad=True` 告诉 PyTorch 这个张量需要梯度。在 `backward()` 时，autograd 引擎会自动计算并填充 `.grad` 属性。

> [!question] 选择题 2
> `optimizer.zero_grad()` 为什么必须在每个 batch 之前调用？
> - [ ] A. 释放 GPU 显存
> - [ ] B. 重置随机种子
> - [ ] C. 清零梯度，防止梯度累加
> - [ ] D. 这是一种可选的优化技巧
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: PyTorch 默认在每次 `backward()` 时梯度是**累加**的（`grad += new_grad`）。如果不清零，梯度会包含之前 batch 的梯度。这在某些场景（如梯度累积）是有意为之的。

> [!question] 判断题 1
> `torch.from_numpy(arr)` 返回的张量与 `arr` 共享内存，修改其中一个会影响另一个。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `torch.from_numpy()` 创建的 Tensor 与 NumPy 数组共享同一块内存（条件：CPU、相同 dtype）。如果需要独立拷贝，使用 `torch.tensor(arr)`。

---

## 📋 章节测试

### 一、判断题（正确选 ✅，错误选 ❌）

> [!question] 判断题 1
> PyTorch 的张量只能运行在 CPU 上。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: PyTorch 支持 CPU、CUDA (NVIDIA GPU)、MPS (Apple Silicon)、ROCm (AMD GPU)、XPU (Intel) 等多种后端。用 `.to('cuda')`、`.to('mps')` 切换设备。

> [!question] 判断题 2
> `model.eval()` 会永久修改模型，使其无法继续训练。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `model.eval()` 只是设置模式标志（影响 Dropout 和 BatchNorm 等层的行为），调用 `model.train()` 即可恢复训练模式。

> [!question] 判断题 3
> `torch.no_grad()` 的作用是关闭自动求导以节省显存并加速推理。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 在 `with torch.no_grad()` 块中，所有 Tensor 操作不会构建计算图，不会分配梯度缓存。推理时使用此模式更高效。

> [!question] 判断题 4
> `nn.Linear(4, 3)` 包含的参数量是 12 个。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `nn.Linear(4, 3)` 包含权重矩阵 `W` (4×3 = 12) 和偏置向量 `b` (3)，共 15 个参数。当 `bias=False` 时才是 12 个。

> [!question] 判断题 5
> `optimizer.step()` 内部调用的是 `param -= lr * param.grad` 的逻辑。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: SGD 优化器的 `step()` 本质就是 `param -= lr * grad`。Adam、RMSprop 等更复杂的优化器有额外的动量计算，但基本原理相同。

> [!question] 判断题 6
> `loss.backward()` 被调用多次（不使用 `retain_graph`）时，计算图会被自动重建。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 默认情况下 `backward()` 之后计算图被释放，再次调用会报错。需要 `loss.backward(retain_graph=True)` 保留计算图。或者重新执行前向传播构建新图。

### 二、选择题（单项选择题）

> [!question] 选择题 1
> `a @ b` 在 PyTorch 中代表什么操作？
> - [ ] A. 逐元素乘法
> - [ ] B. 矩阵乘法
> - [ ] C. 张量加法
> - [ ] D. 外积
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `@` 运算符执行矩阵乘法（等同 `torch.matmul(a, b)`）。逐元素乘法用 `*`（等同 `torch.mul(a, b)`）。

> [!question] 选择题 2
> 计算图（Computational Graph）是什么类型的数据结构？
> - [ ] A. 链表
> - [ ] B. 平衡二叉树
> - [ ] C. 有向无环图（DAG）
> - [ ] D. 哈希表
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: PyTorch 在每次运算时构建一个有向无环图（DAG），叶子节点是输入张量/参数，根节点是损失函数。`backward()` 在 DAG 上执行反向拓扑序遍历求梯度。

> [!question] 选择题 3
> 以下哪种保存 PyTorch 模型的方式是推荐的？
> - [ ] A. `torch.save(model, "model.pth")`
> - [ ] B. `torch.save(model.state_dict(), "model.pth")`
> - [ ] C. `pickle.dump(model, "model.pkl")`
> - [ ] D. `model.write("model.pth")`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `state_dict()` 只保存模型参数（权重和偏置的有序字典），不保存模型结构，是推荐的轻量级方式。保存整个模型对象（选项 A）存在序列化兼容性问题。

> [!question] 选择题 4
> `dim=0` 在 `tensor.sum(dim=0)` 中代表什么？
> - [ ] A. 沿列方向（垂直）求和
> - [ ] B. 沿行方向（水平）求和
> - [ ] C. 对所有元素求和
> - [ ] D. 沿深度方向求和
>
> > [!success]- 点击查看答案
> > 正确答案: A
> > **解析**: `dim=0` 沿着第 0 维（`shape[0]`，即行方向）求和，结果是压缩了行维度。例如 `(3,4).sum(dim=0)` → `(4,)`。

> [!question] 选择题 5
> 以下哪个不是 PyTorch 的优化器？
> - [ ] A. `optim.Adam`
> - [ ] B. `optim.SGD`
> - [ ] C. `optim.AdamW`
> - [ ] D. `optim.GradientBoosting`
>
> > [!success]- 点击查看答案
> > 正确答案: D
> > **解析**: PyTorch 的 `torch.optim` 模块提供 SGD、Adam、AdamW、RMSprop、Adagrad 等梯度下降优化器。GradientBoosting 是集成学习方法（如 XGBoost），不是 PyTorch 优化器。

> [!question] 选择题 6
> `nn.CrossEntropyLoss()` 等价于哪两个操作的组合？
> - [ ] A. `nn.ReLU` + `nn.MSELoss`
> - [ ] B. `nn.LogSoftmax` + `nn.NLLLoss`
> - [ ] C. `nn.Sigmoid` + `nn.BCELoss`
> - [ ] D. `nn.Tanh` + `nn.L1Loss`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `CrossEntropyLoss` 内部先对 logits 做 LogSoftmax，再计算负对数似然损失（NLLLoss）。因此输入不需要提前做 softmax。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：从零实现线性回归
> **难度**: ⭐⭐
>
> 不使用 `nn.Linear` 和 `nn.MSELoss`，纯手动实现线性回归：
> 1. 手动创建 `w` 和 `b` 张量（`requires_grad=True`）
> 2. 手动计算 `y_pred = X @ w + b`
> 3. 手动计算 MSE loss = `((y_pred - y) ** 2).mean()`
> 4. 手动 `loss.backward()` + `w -= lr * w.grad`
> 5. 用 `torch.randn(100, 3)` 生成随机数据，目标 `y = X.sum(dim=1)`
>
> 完成后与 `nn.Linear` 版本对比结果。

> [!example] 练习题 2：MNIST 数字分类
> **难度**: ⭐⭐⭐
>
> 用 PyTorch 训练一个两层 MLP（784 → 128 → 10）在 MNIST 手写数字数据集上：
> ```python
> from torchvision import datasets, transforms
> train_data = datasets.MNIST('data/', train=True, download=True,
>                              transform=transforms.ToTensor())
> ```
> 1. 创建 DataLoader，batch_size=64
> 2. 训练 5 个 epoch
> 3. 在测试集上报告准确率（目标 > 95%）
> 4. 保存模型参数到 `mnist_mlp.pth`

> [!example] 练习题 3：对比 GPU vs CPU
> **难度**: ⭐⭐
>
> 如果有 GPU，用 `time.perf_counter()` 对比大矩阵乘法 `(10000, 10000) @ (10000, 10000)` 在 CPU 和 CUDA 上的时间。观察 GPU 的加速比。
>
> 如果没有 GPU，用 `torch.randn(5000, 5000)` 手动计时 100 次矩阵乘法，观察 `torch.no_grad()` 和普通模式的性能差异。
