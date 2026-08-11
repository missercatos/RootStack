# 模型导出 ONNX (Exporting to ONNX)
---

## 📖 章节概述

ONNX（Open Neural Network Exchange）是从 Python 训练到 C++ 部署的桥梁。本章演示如何将 PyTorch 模型导出为 .onnx 文件，理解 ONNX 的内部结构（图、节点、张量），用 onnxruntime 在 Python 侧验证模型正确性，为下一章 C++ 部署做好准备。

> **核心理念**：ONNX 是 AI 领域的"ELF 可执行文件"。就像 C 编译器将源代码编译为可在不同平台上运行的二进制文件，`torch.onnx.export` 将 Python 模型"编译"为可在不同推理引擎（ONNX Runtime、TensorRT、OpenVINO）上运行的 .onnx 文件。C++ 程序加载 .onnx → 执行推理 → 释放资源，就像加载 `.so` 动态库。理解 ONNX 的输入/输出形状是成功部署的关键。

---

### 📚 第一节：ONNX 概述

1.1 什么是 ONNX
----------------

ONNX（Open Neural Network Exchange，开放神经网络交换格式）由 Facebook 和 Microsoft 于 2017 年推出，是一个开放的深度学习模型互操作标准。

```
你的模型导出为 .onnx 后可以运行在：

Python (训练/验证)             C++/其他语言 (部署/推理)
┌──────────────┐             ┌─────────────────────┐
│ pytorch      │──export()──▶│                     │
│ tensorflow   │             │  ONNX Runtime (CPU)  │
│ sklearn (skl2onnx)│       │  ONNX Runtime (CUDA)  │
│ jax          │             │  ONNX Runtime (DirectML)│
│ mxnet        │             │  TensorRT (NVIDIA GPU)│
└──────────────┘             │  OpenVINO (Intel)    │
                             │  TVM (Apache)        │
                             │  ONNX Runtime C API   │ ← 本章终点
                             │  ONNX Runtime C++ API  │
                             └─────────────────────┘
```

1.2 ONNX vs TorchScript vs libtorch
------------------------------------

| 方案 | 格式 | 优点 | 缺点 |
|------|------|------|------|
| ONNX | .onnx | 跨框架、广泛支持 | 部分算子不支持 |
| TorchScript | .pt | PyTorch 原生、完整支持 | 仅限 PyTorch 生态 |
| libtorch | .pt + C++ | 直接用 C++ 调 PyTorch | 部署体积大 (>500MB) |

> **推荐策略**：优先 ONNX → 如果 ONNX 不支持某些算子 → 用 TorchScript/libtorch → 如果 GPU 推理 → 从 ONNX 转 TensorRT。

---

### 📚 第二节：torch.onnx.export 实战

2.1 导出最简单的模型
---------------------

```bash
python -c "
import torch
import torch.nn as nn

# 1. 定义一个简单模型
class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(4, 3)
    def forward(self, x):
        return self.linear(x)

model = SimpleModel()
model.eval()

# 2. 创建 dummy input — 形状必须和实际输入一致
dummy_input = torch.randn(1, 4)  # batch=1, features=4

# 3. 导出 ONNX
torch.onnx.export(
    model,
    dummy_input,
    'simple_model.onnx',
    export_params=True,        # 保存模型参数（权重）
    opset_version=17,          # ONNX 算子集版本
    input_names=['input'],     # 输入节点名称
    output_names=['output'],   # 输出节点名称
    dynamic_axes={             # 动态轴：batch 维度可变
        'input': {0: 'batch'},
        'output': {0: 'batch'},
    },
)
print('Exported to simple_model.onnx')
print(f'File size: {__import__(\"os\").path.getsize(\"simple_model.onnx\")} bytes')
"
```

2.2 关键参数详解
-----------------

| 参数 | 含义 | 注意事项 |
|------|------|---------|
| `model` | 要导出的模型 | 必须先调用 `model.eval()` |
| `args` | 示例输入（tuple 或有多个参数） | 形状决定 ONNX 的参数尺寸！ |
| `f` | 输出文件名 | 后缀 `.onnx` |
| `export_params` | 是否保存权重 | 一般为 True |
| `opset_version` | ONNX 算子集版本 | 11 是稳定版，17+支持更多算子 |
| `input_names` | 输入节点名字列表 | C++ 侧用名字获取输入 |
| `output_names` | 输出节点名字列表 | C++ 侧用名字获取输出 |
| `dynamic_axes` | 可变的维度 | batch 维度经常是动态的 |

2.3 动态轴详解
---------------

```python
# dynamic_axes 使 batch 维度可变
dynamic_axes = {
    'input':  {0: 'batch_size'},   # 输入的第 0 维可变
    'output': {0: 'batch_size'},   # 输出的第 0 维可变
}

# 导出的模型可以接受任意 batch size：
# batch=1: (1, 4) ✅
# batch=32: (32, 4) ✅
# batch=None: 错误 — 没有标记为动态的维度必须匹配 dummy_input
```

> **C++ 部署关键**：如果不设置 `dynamic_axes`，导出后 batch 维度被固定为 `dummy_input` 的大小。C++ 程序必须传入相同 batch 大小的输入。设置动态轴后，batch 大小可变，更灵活。

2.4 导出 CNN（图像模型）
-------------------------

```bash
python -c "
import torch, torch.nn as nn

class CNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(3, 16, 3, padding=1)
        self.fc = nn.Linear(16, 10)
    def forward(self, x):
        x = self.conv(x)           # (B,3,H,W) → (B,16,H,W)
        x = x.mean(dim=[2, 3])     # 全局平均池化 → (B,16)
        return self.fc(x)          # → (B,10)

model = CNN().eval()
dummy_input = torch.randn(1, 3, 224, 224)

torch.onnx.export(
    model, dummy_input, 'cnn_model.onnx',
    input_names=['image'],
    output_names=['class_logits'],
    dynamic_axes={'image': {0: 'batch', 2: 'height', 3: 'width'}},
    opset_version=17,
)
print('CNN exported!')
# C++ 侧: 可以传入 (N, 3, H, W) 任意大小的图像
"
```

---

### 📚 第三节：理解 ONNX 模型结构

3.1 ONNX 模型的内部表示
------------------------

ONNX 模型是一个 protobuf 格式文件，内部结构如下：

```
ModelProto
├── graph
│   ├── input  (ValueInfoProto — 模型输入)
│   │   └── name, type, shape
│   ├── output (ValueInfoProto — 模型输出)
│   │   └── name, type, shape
│   ├── initializer (TensorProto — 权重参数)
│   │   └── 每个权重的名称、类型、原始数据
│   └── node (NodeProto × N — 计算节点)
│       └── op_type, inputs[], outputs[], attributes
└── opset_import
    └── domain, version
```

每个 `node` 代表一个算子（如 Conv, Relu, Gemm, Softmax），`initializer` 存储权重。

3.2 用 Python 检查 ONNX 模型
------------------------------

```bash
python -c "
import onnx

model = onnx.load('simple_model.onnx')

# 输入信息
print('=== Inputs ===')
for inp in model.graph.input:
    print(f'  Name: {inp.name}')
    shape = [d.dim_value if d.dim_value else 'dynamic' for d in inp.type.tensor_type.shape.dim]
    print(f'  Shape: {shape}')

# 输出信息
print('=== Outputs ===')
for out in model.graph.output:
    print(f'  Name: {out.name}')

# 算子列表
print('=== Nodes ===')
for node in model.graph.node:
    print(f'  Op: {node.op_type}, Inputs: {list(node.input)}, Outputs: {list(node.output)}')

# 权重/参数
print(f'\\n=== Initializers ({len(model.graph.initializer)}) ===')
for init in model.graph.initializer:
    print(f'  {init.name}: shape={list(init.dims)}')

# 验证模型合法性
onnx.checker.check_model(model)
print('\\n✓ Model is valid!')
"
```

输出示例：
```
=== Inputs ===
  Name: input
  Shape: ['dynamic', 4]

=== Outputs ===
  Name: output

=== Nodes ===
  Op: Gemm, Inputs: ['input', 'linear.weight', 'linear.bias'], Outputs: ['output']

=== Initializers (2) ===
  linear.weight: shape=[3, 4]
  linear.bias: shape=[3]

✓ Model is valid!
```

注意：`nn.Linear` 在 PyTorch 中被转换为 ONNX 的 `Gemm` 算子（General Matrix Multiply：Y = αA×B + βC）。这是 ONNX 算子层面的"翻译"。

3.3 netron — 可视化 ONNX 模型
------------------------------

```bash
# 安装 netron
pip install netron

# 在浏览器中可视化
python -c "import netron; netron.start('simple_model.onnx')"

# 或者用命令行导出图片
# netron 是交互式工具，无法直接出图，但可以在浏览器中查看每个节点的结构
```

> netron 让你像反汇编工具（objdump）一样检查模型内部结构。每个节点的输入/输出张量形状、权重值、算子属性都能看到。这对于调试 ONNX 导出问题非常有用。

---

### 📚 第四节：用 onnxruntime 验证导出

4.1 Python 端验证
------------------

导出 ONNX 后最重要的一步是验证：Python 原始模型 和 ONNX Runtime 推理的结果必须一致。

```python
import torch
import torch.nn as nn
import numpy as np
import onnxruntime as ort

# 1. 重新加载刚导出的模型
class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(4, 3)

model = SimpleModel()
model.eval()

# 2. 创建 ONNX Runtime session
session = ort.InferenceSession('simple_model.onnx')

# 3. 准备输入
x = torch.randn(2, 4)  # batch=2

# 4. PyTorch 推理
with torch.no_grad():
    pytorch_out = model(x).numpy()

# 5. ONNX Runtime 推理
#    注意：ONNX Runtime 输入是 numpy 数组，键名必须匹配 input_names
onnx_out = session.run(
    None,                    # None = 获取所有输出
    {'input': x.numpy()},   # {'输入节点名': numpy 数组}
)[0]                        # run() 返回 list of outputs

# 6. 对比结果
diff = np.abs(pytorch_out - onnx_out).max()
print(f"PyTorch  output: {pytorch_out[0]}")
print(f"ONNX RT  output: {onnx_out[0]}")
print(f"Max difference: {diff:.10f}")
assert diff < 1e-5, f"Output mismatch! diff={diff}"
print("✓ PyTorch and ONNX Runtime outputs match!")
```

4.2 常见的 ONNX 导出问题
--------------------------

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 输出不一致 | 使用了不支持的 Python 控制流 | `if/for` 可能无法正确 trace |
| 导出失败 | 算子不支持（如自定义 CUDA kernel） | 用 `torch.onnx.is_in_onnx_export()` 提供 fallback |
| 动态形状错误 | 未设置 `dynamic_axes` | 为可变维度设置动态轴 |
| `eval()` 忘调用 | Dropout/BatchNorm 行为不同 | 始终在导出前调用 `model.eval()` |

4.3 处理动态控制流
--------------------

```python
import torch
import torch.nn as nn

class DynamicModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear_a = nn.Linear(10, 10)
        self.linear_b = nn.Linear(10, 10)

    def forward(self, x, use_branch_b=False):
        if use_branch_b:
            return self.linear_b(x)
        else:
            return self.linear_a(x)

model = DynamicModel().eval()

# 方案1：分别导出两个分支
# torch.onnx.export(model, (x, False), 'model_branch_a.onnx', ...)
# torch.onnx.export(model, (x, True), 'model_branch_b.onnx', ...)

# 方案2：用 torch.cond（PyTorch 2.0+）
def forward(self, x, use_branch_b):
    return torch.cond(use_branch_b, lambda: self.linear_b(x), lambda: self.linear_a(x))
```

> PyTorch 的 ONNX 导出使用 **Tracing**（跟踪）模式：给定一个示例输入，实际执行一次前向传播，记录所有执行的操作，然后序列化为 ONNX。这类似于 C 代码的单路径执行记录——if/else 的分支、for 循环的迭代次数都被"固化"在导出的图中。

---

### 📚 第五节：高级导出场景

5.1 导出带 BatchNorm 的模型
-----------------------------

```python
# ⚠️ 关键：先 eval()，再导出！
model.eval()

# 或者将 BatchNorm 折叠到前面的卷积中（减少推理计算）
torch.onnx.export(
    model, dummy_input, 'model.onnx',
    do_constant_folding=True,  # 默认 True：常量折叠优化
    training=torch.onnx.TrainingMode.EVAL,  # 确保是 EVAL 模式
)
```

5.2 导出 Transformer / BERT
----------------------------

```python
from transformers import AutoModel, AutoTokenizer

model = AutoModel.from_pretrained('bert-base-uncased').eval()
tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')

# BERT 有两个输入: input_ids 和 attention_mask
text = "Hello, world!"
inputs = tokenizer(text, return_tensors='pt')

export_args = (inputs['input_ids'], inputs['attention_mask'])

torch.onnx.export(
    model,
    export_args,
    'bert.onnx',
    input_names=['input_ids', 'attention_mask'],
    output_names=['last_hidden', 'pooler_output'],
    dynamic_axes={
        'input_ids':       {0: 'batch', 1: 'seq_length'},
        'attention_mask':  {0: 'batch', 1: 'seq_length'},
        'last_hidden':     {0: 'batch', 1: 'seq_length'},
        'pooler_output':   {0: 'batch'},
    },
    opset_version=17,
)
```

5.3 简化 ONNX 模型（onnxsim）
------------------------------

```bash
pip install onnxsim

# 简化 ONNX 图：移除冗余节点、折叠常量
python -c "
import onnx
from onnxsim import simplify
model = onnx.load('bert.onnx')
simplified, check = simplify(model)
assert check, 'Simplification failed'
onnx.save(simplified, 'bert_simplified.onnx')
print('Simplified!')
"
```

> `onnxsim` 对于大型模型非常实用，可以减少 10-30% 的模型大小和推理时间。

---

### 📝 小节练习

> [!question] 选择题 1
> `torch.onnx.export` 的 `dummy_input` 参数作用是什么？
> - [ ] A. 设置模型的随机种子
> - [ ] B. 提供示例输入以追踪计算图
> - [ ] C. 验证模型的准确率
> - [ ] D. 设置 batch size 为 1
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `dummy_input` 是示例输入，PyTorch 用它实际执行一次前向传播，记录所有执行的操作以生成 ONNX 计算图。dummy_input 的形状同时确定了 ONNX 模型的输入形状。

> [!question] 选择题 2
> ONNX Runtime 的 `session.run()` 接受的输入格式是什么？
> - [ ] A. PyTorch Tensor
> - [ ] B. Python list
> - [ ] C. 字典 `{'input_name': numpy_array}`
> - [ ] D. JSON 字符串
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: ONNX Runtime Python API 的 `run()` 方法接受一个 dict，键是模型输入节点名（与 `input_names` 匹配），值是 numpy 数组。

> [!question] 判断题 1
> ONNX 模型文件使用 JSON 格式存储。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: ONNX 使用 protobuf 格式存储。protobuf 是一种紧凑的二进制序列化格式，比 JSON 小且快。

---

## 📋 章节测试

### 一、判断题（正确选 ✅，错误选 ❌）

> [!question] 判断题 1
> ONNX 只支持 PyTorch 导出的模型。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: ONNX 是跨框架的开放标准。TensorFlow（tf2onnx）、sklearn（skl2onnx）、JAX、MXNet 等都可以导出 ONNX 模型。

> [!question] 判断题 2
> `opset_version` 越大越好，始终使用最新版本。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 新 opset 可能不被旧版 ONNX Runtime 支持。应选择与目标部署环境兼容的 opset。opset_version=11 是兼容性最好的选择，17 是较新的推荐值。

> [!question] 判断题 3
> `dynamic_axes` 使导出的 ONNX 模型可以接受不同大小的输入。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `dynamic_axes` 标记哪些维度是动态的（如 batch、序列长度、图像尺寸）。标记为动态的维度在推理时可以传入不同大小。

> [!question] 判断题 4
> 导出 ONNX 前必须调用 `model.eval()`。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `model.eval()` 将 Dropout 和 BatchNorm 切换到推理模式。如果在 `model.train()` 状态下导出，推理结果会出错（Dropout 随机丢弃，BatchNorm 使用 running mean 等错误行为）。

> [!question] 判断题 5
> ONNX Runtime 的 C API 需要依赖 Python 运行时。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: ONNX Runtime 的核心是纯 C/C++ 实现的，C API 没有任何 Python 依赖。Python 只在训练和导出阶段使用，部署阶段不需要。

> [!question] 判断题 6
> `onnx.checker.check_model()` 可以验证 ONNX 模型输出的数值精确度。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `check_model()` 只检查 ONNX 图的结构合法性（节点连接、类型匹配、opset 兼容等），不检查输出的数值正确性。验证数值需要对比 PyTorch 模型和 ONNX Runtime 的输出（如本章 4.1 所示）。

### 二、选择题（单项选择题）

> [!question] 选择题 1
> 导出 ONNX 时 PyTorch 的 `nn.Linear` 通常会转换成什么 ONNX 算子？
> - [ ] A. MatMul
> - [ ] B. Conv
> - [ ] C. Gemm
> - [ ] D. Add
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: `nn.Linear` 的计算是 `y = x @ W^T + b`，对应 ONNX 的 Gemm 算子（General Matrix multiply：αAB + βC）。

> [!question] 选择题 2
> `onnxsim` 工具的主要作用是？
> - [ ] A. 可视化 ONNX 模型结构
> - [ ] B. 转换 ONNX 为 JSON 格式
> - [ ] C. 简化 ONNX 图，移除冗余节点
> - [ ] D. 训练 ONNX 模型
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: onnxsim (onnx-simplifier) 是 ONNX 图的简化工具，执行常量折叠、移除冗余节点和未使用的 initializer，减小模型体积并加速推理。

> [!question] 选择题 3
> PyTorch ONNX 导出的默认模式是？
> - [ ] A. Scripting（脚本模式）
> - [ ] B. Tracing（跟踪模式）
> - [ ] C. Eager（即时模式）
> - [ ] D. Compile（编译模式）
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `torch.onnx.export` 默认使用 Tracing 模式：传入 dummy input 实际运行前向传播一次，记录所有执行的操作生成静态计算图。Scripting 模式（通过 `torch.jit.script`）可以处理控制流但需要显式设置。

> [!question] 选择题 4
> 以下哪个工具用于交互式可视化 ONNX 模型结构？
> - [ ] A. onnxruntime
> - [ ] B. netron
> - [ ] C. onnxsim
> - [ ] D. tensorboard
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: netron 是一个交互式 ONNX 模型可视化工具，可在浏览器中查看模型的计算图、节点属性、权重和张量形状。

> [!question] 选择题 5
> ONNX 模型中 `initializer` 存储的是什么？
> - [ ] A. 输入数据
> - [ ] B. 模型结构（算子）
> - [ ] C. 权重的初始训练数据
> - [ ] D. 训练好的模型权重参数值
>
> > [!success]- 点击查看答案
> > 正确答案: D
> > **解析**: `initializer` 是已训练好的模型权重参数（如卷积核、线性层的 W 和 b）。这些值在导出时被冻结写入 .onnx 文件，推理时不可改变。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：导出并验证自己的 CNN
> **难度**: ⭐⭐
>
> 1. 用第四章的 MNIST CNN 模型，把它保存到 `mnist_cnn.pth`
> 2. 导出为 `mnist_cnn.onnx`（注意输入形状是 `(1, 1, 28, 28)`）
> 3. 用 onnxruntime 验证：传入一张真实 MNIST 图像，对比 PyTorch 输出和 ONNX Runtime 输出
> 4. 设置 `dynamic_axes` 使 batch 维度可变
> 5. 分别在 batch=1 和 batch=16 上测试推理成功

> [!example] 练习题 2：分析 ONNX 图
> **难度**: ⭐⭐
>
> 1. 导出 ResNet-18 到 `resnet18.onnx`（用 `torchvision.models.resnet18`）
> 2. 用 `onnx.load()` 加载并打印所有节点类型（`node.op_type`）
> 3. 统计每种算子的出现次数
> 4. 计算模型文件大小
> 5. 用 netron 打开模型，观察计算图的结构层次

> [!example] 练习题 3：ONNX 模型简化
> **难度**: ⭐⭐
>
> 1. 导出 ResNet-18 到 ONNX
> 2. 记录原始文件大小和推理时间（100 次推理取平均）
> 3. 用 onnxsim 简化模型
> 4. 记录简化后的文件大小和推理时间
> 5. 用 onnxruntime 验证简化前后的输出完全一致（max difference < 1e-5）
>
> 观察简化带来了多少文件体积缩减和速度提升。
