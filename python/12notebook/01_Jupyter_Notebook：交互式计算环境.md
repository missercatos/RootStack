# Jupyter Notebook：交互式计算环境 (Jupyter Notebook: Interactive Computing)

---

## 章节概述

Jupyter Notebook 是数据科学和科学计算的标准工具——在浏览器中编写代码、运行结果、插入文档、绘制图表，全部在一个 `.ipynb` 文件中完成。对于 C 程序员来说，Jupyter 就是一个"交互式 REPL + 可视化 + 文档"的三合一环境。

> **核心价值**：C 程序的开发循环是 edit → compile → run → debug。Jupyter 的开发循环是 write cell → shift+enter → see result → iterate——快得多。

---

## 1. 安装与启动

```bash
# 安装完整版（含常用科学计算库）
pip install jupyterlab numpy pandas matplotlib

# 启动 JupyterLab（推荐）
jupyter lab
# 浏览器自动打开 http://127.0.0.1:8888/

# 启动经典 Notebook
jupyter notebook
```

```bash
# 远程服务器部署（常用场景）
jupyter lab --ip 0.0.0.0 --port 8888 --no-browser --allow-root
# 用 SSH 隧道访问：ssh -L 8888:localhost:8888 user@server
```

---

## 2. 基本操作

### 单元格类型

| 类型 | 快捷键 | 用途 |
|------|--------|------|
| Code | `Y` | 执行 Python 代码 |
| Markdown | `M` | 写文档、公式、说明 |
| Raw | `R` | 原始文本（不渲染） |

### 常用快捷键

| 快捷键 | 功能 |
|--------|------|
| `Shift+Enter` | 运行当前单元格并跳到下一格 |
| `Ctrl+Enter` | 运行当前单元格并保持选中 |
| `A` | 在上方插入新单元格 |
| `B` | 在下方插入新单元格 |
| `DD` | 删除当前单元格 |
| `Z` | 撤销删除 |
| `L` | 显示行号 |
| `Ctrl+Shift+-` | 在光标处分割单元格 |
| `Esc` → `M` | 切换到 Markdown |
| `Esc` → `Y` | 切换到 Code |

---

## 3. 魔法命令

```python
# 行魔法（% 前缀）
%timeit sum(range(1000))           # 计时
%matplotlib inline                 # 内联显示图表
%who                               # 列出所有变量
%load script.py                    # 加载外部脚本到单元格
%pip install pandas                # 在 Notebook 中安装包

# 均魔法（%% 前缀，作用于整个单元格）
%%timeit
result = [i**2 for i in range(10000)]

%%bash
ls -la
echo "Hello from bash"
```

---

## 4. 数据分析工作流

```python
import pandas as pd
import matplotlib.pyplot as plt

# 读取数据
df = pd.read_csv('data.csv')

# 快速探索
df.head()           # 前5行
df.info()           # 列类型和非空数
df.describe()       # 统计摘要

# 数据清洗
df = df.dropna()                          # 删除缺失值
df['date'] = pd.to_datetime(df['date'])   # 转换日期
df = df[df['value'] > 0]                  # 过滤

# 分析
summary = df.groupby('category')['value'].agg(['mean', 'std', 'count'])

# 可视化
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
df.plot(x='date', y='value', ax=axes[0], title='时序图')
summary['mean'].plot(kind='bar', ax=axes[1], title='分类均值')
plt.tight_layout()
plt.show()
```

---

## 5. 与 C 程序集成

```python
# 在 Notebook 中编译和运行 C 代码
%%bash
cat > test.c << 'EOF'
#include <stdio.h>
int main() {
    int sum = 0;
    for (int i = 0; i < 1000; i++) sum += i;
    printf("Sum = %d\n", sum);
    return 0;
}
EOF
gcc -o test test.c && ./test
```

```python
# 使用 ctypes 调用 C 共享库
import ctypes
lib = ctypes.CDLL('./libmylib.so')
result = lib.add(10, 20)
print(f"C 函数返回: {result}")
```

```python
# 使用 Cython 加速（在 Notebook 中）
%load_ext Cython
```

```cython
%%cython
def fib(int n):
    cdef int a = 0, b = 1, i
    for i in range(n):
        a, b = b, a + b
    return a
```

---

## 6. 导出与分享

```bash
# 导出为不同格式
jupyter nbconvert --to html notebook.ipynb
jupyter nbconvert --to pdf notebook.ipynb
jupyter nbconvert --to script notebook.ipynb   # 纯 Python 脚本
jupyter nbconvert --to markdown notebook.ipynb

# 命令行执行整个 notebook（自动化测试）
jupyter nbconvert --execute --to notebook notebook.ipynb
```

---

## 7. Jupyter 与其他工具

| 工具 | 特点 | 适用 |
|------|------|------|
| JupyterLab | 下一代 Notebook，多标签 | 日常开发 |
| Jupyter Notebook | 经典版本 | 兼容性好 |
| Google Colab | 免费 GPU，云端运行 | 深度学习 |
| VS Code + Jupyter | VS Code 内集成 | 已用 VS Code 的人 |
| Observable | JS 版 Notebook | Web 可视化 |

---

## 速查卡片

| 需求 | 命令 |
|------|------|
| 安装 | `pip install jupyterlab` |
| 启动 | `jupyter lab` |
| 运行单元格 | `Shift+Enter` |
| 新建单元格 | `A`（上）/ `B`（下） |
| 删除单元格 | `DD` |
| 转为 Markdown | `M` |
| 转为 Code | `Y` |
| 导出 HTML | `jupyter nbconvert --to html file.ipynb` |
| 导出脚本 | `jupyter nbconvert --to script file.ipynb` |
