# SciPy：线性代数与优化 (SciPy: Linear Algebra & Optimization)
---

## 章节概述

SciPy 是 Python 科学计算工具箱中的"重型武器"。如果说 NumPy 提供了数组和基础运算，SciPy 则在上面构建了线性代数、优化、积分、插值、信号处理等专业模块。本章聚焦 `scipy.linalg` 与 `scipy.optimize` 两大核心：从求解线性方程组、计算特征值与 SVD 分解，到函数极值优化、曲线拟合和求根。我们将对比这些操作在 C 语言中需要如何调用 LAPACK/BLAS，以及 SciPy 如何用一行代码完成这些任务。

> **核心理念**：SciPy 不是"又一个新的线性代数库"，它是对久经考验的 LAPACK/BLAS Fortran 代码的高层次封装。当你在 Python 中调用 `scipy.linalg.solve(A, b)` 时，底层运行的正是那些在超级计算机上优化了几十年的 Fortran 子程序。

---

### 第一节：SciPy 与 NumPy 的 linalg 对比

#### 1.1 两个 linalg 的区别

```python
import numpy as np
import scipy.linalg as la
```

| 特性 | `numpy.linalg` | `scipy.linalg` |
|------|---------------|----------------|
| 底层实现 | 精简版 LAPACK 子集 | 完整 LAPACK + BLAS |
| 是否总是编译进 LAPACK | 取决于 NumPy 构建配置 | 始终编译进 BLAS/LAPACK |
| 性能 | 功能少但够快 | 功能全，某些操作使用更优算法 |
| 支持矩阵类型 | 仅通用矩阵 | 支持对称、正定、带状等多种矩阵 |
| 函数数量 | ~20 个 | ~80+ 个 |

**规则：能用 `numpy.linalg` 快速验证的不要引入 SciPy；需要高级分解（如 LU/QR/Cholesky 显式分解）、特殊矩阵结构优化时用 `scipy.linalg`。**

```python
import numpy as np
import scipy.linalg as la

A = np.array([[3, 1], [1, 2]])
b = np.array([9, 8])

# 两者都能解线性方程组
x_np = np.linalg.solve(A, b) # [2. 3.]
x_sp = la.solve(A, b) # [2. 3.]

# 显式的 LU 分解只有 SciPy 提供
P, L, U = la.lu(A)
print("L:\n", L)
print("U:\n", U)
print("P @ L @ U:\n", P @ L @ U) # 还原 A
```

#### 1.2 C 程序员视角：直接调用 LAPACK

在 C 语言中，求解 `Ax = b` 需要：

```c
// 伪代码展示：C 语言调用 LAPACK 的复杂度
#include <lapacke.h>

int info, *ipiv;
ipiv = (int*)malloc(n * sizeof(int));

// dgesv 是 LAPACK 的双精度通用求解器
info = LAPACKE_dgesv(LAPACK_ROW_MAJOR, n, 1, A, lda, ipiv, b, ldb);
// 需要管理：内存分配、lda/ldb 参数、返回码检查、清理
```

SciPy 的 `la.solve(A, b)` 将这些繁琐工作完全封装，且自动选择最优的求解器（正定矩阵用 Cholesky，一般矩阵用 LU）。

---

### 第二节：解线性方程组

#### 2.1 基础求解：`la.solve`

```python
import numpy as np
import scipy.linalg as la

# 标准线性方程组 Ax = b
A = np.array([[3, 1, 0],
 [1, 4, 1],
 [0, 1, 3]])
b = np.array([4, 11, 8])

x = la.solve(A, b)
print(f"解: {x}") # [1. 1. 2.]
print(f"验证: {A @ x}") # 应等于 b

# 同时求解多个右侧向量
B = np.array([[4, 1],
 [11, 2],
 [8, 3]]) # 3×2 矩阵，两套 b
X = la.solve(A, B) # 同时求解 AX = B
print(f"多右侧解:\n{X}")
```

#### 2.2 最小二乘：`la.lstsq`

当方程数多于未知数时（超定系统），使用最小二乘法：

```python
import numpy as np
import scipy.linalg as la

# 拟合 y = ax + b，数据带噪声
x_data = np.array([0, 1, 2, 3, 4, 5])
y_data = np.array([1.1, 2.9, 5.0, 7.2, 8.9, 11.1])

A = np.vstack([x_data, np.ones_like(x_data)]).T # 设计矩阵
# A 形状 (6, 2)，b 形状 (6,)

coeffs, residuals, rank, sv = la.lstsq(A, y_data)
print(f"拟合系数: y = {coeffs[0]:.3f}x + {coeffs[1]:.3f}")
# y = 2.000x + 1.067
```

> 在 C 语言中，最小二乘通常需要调用 LAPACK 的 `*gels` 或 `*gelsd` 函数，需要手写工作区计算和多级指针管理。SciPy 一行直接出结果。

#### 2.3 特殊矩阵结构优化

```python
import numpy as np
import scipy.linalg as la

n = 1000
A = np.random.rand(n, n)
A = A + A.T + n * np.eye(n) # 构造对称正定矩阵

# 一般求解器 — 不知道矩阵结构，使用 LU
x1 = la.solve(A, np.ones(n))

# Cholesky 专用于对称正定矩阵 — 速度约为 LU 的 2 倍
L = la.cholesky(A, lower=True) # A = L @ L.T
x2 = la.cho_solve((L, True), np.ones(n))

print(f"结果一致: {np.allclose(x1, x2)}") # True
```

> 如果你的矩阵已知是对称正定的，一定要使用 `cho_solve`——它比普通 `solve` 快约一倍，且数值更稳定。

---

### 第三节：特征值与奇异值分解

#### 3.1 特征值分解

```python
import numpy as np
import scipy.linalg as la

A = np.array([[4, -1, 1],
 [-1, 3, -2],
 [1, -2, 3]])

# 标准特征值分解
eigvals, eigvecs = la.eig(A)
print(f"特征值: {eigvals}")

# 对于对称/厄米矩阵，使用 eigh 更快且保证实数输出
eigvals_h, eigvecs_h = la.eigh(A)
print(f"eigh 特征值: {eigvals_h}") # 升序排列
print(f"正交性验证: \n{eigvecs_h.T @ eigvecs_h}") # 近似单位矩阵

# 验证: A @ v = λ @ v
for i in range(len(eigvals_h)):
 residual = A @ eigvecs_h[:, i] - eigvals_h[i] * eigvecs_h[:, i]
 print(f"特征向量 {i} 残差范数: {np.linalg.norm(residual):.2e}")
```

#### 3.2 奇异值分解（SVD）

SVD 是数值线性代数的"瑞士军刀"——矩阵伪逆、低秩近似、PCA、数据压缩都依赖它：

```python
import numpy as np
import scipy.linalg as la

M = np.array([[1, 0, 0, 0, 2],
 [0, 0, 3, 0, 0],
 [0, 0, 0, 0, 0],
 [0, 4, 0, 0, 0]])

U, s, Vt = la.svd(M, full_matrices=False)
print(f"奇异值: {s}")
print(f"U 形状: {U.shape}, Vt 形状: {Vt.shape}")

# 低秩近似（只保留最大的前 k 个奇异值）
k = 2
approx = U[:, :k] @ np.diag(s[:k]) @ Vt[:k, :]
error = np.linalg.norm(M - approx) / np.linalg.norm(M)
print(f"秩-{k} 近似的相对误差: {error:.5f}")

# 通过 SVD 计算伪逆
M_plus = la.pinv(M)
print(f"伪逆 M+ 形状: {M_plus.shape}") # (5, 4)
```

> 在 C 中调用 LAPACK 的 `*gesvd` 或 `*gesdd` 进行 SVD 需要管理几十个参数和工作区。SciPy 将其封装为单行调用，且自动选择分治算法（`gesdd`）——比传统 QR 迭代算法更快。

---

### 第四节：函数极值优化

#### 4.1 无约束优化：`scipy.optimize.minimize`

现代科学中的优化问题远超越简单的线性方程组——函数拟合、参数优化、机器学习训练，都需要通用的数值优化器。

```python
import numpy as np
from scipy.optimize import minimize

# Rosenbrock 函数（优化界的"Hello World"）
# f(x,y) = (1-x)^2 + 100(y-x^2)^2，全局最小值在 (1,1)
def rosenbrock(x):
 return (1 - x[0])**2 + 100 * (x[1] - x[0]**2)**2

x0 = np.array([0, 0]) # 初始猜测

# Nelder-Mead（单纯形法，无梯度）
result_nm = minimize(rosenbrock, x0, method='Nelder-Mead')
print(f"Nelder-Mead: x*={result_nm.x}, f={result_nm.fun:.2e}")

# BFGS（拟牛顿法，使用数值梯度）
result_bfgs = minimize(rosenbrock, x0, method='BFGS')
print(f"BFGS: x*={result_bfgs.x}, f={result_bfgs.fun:.2e}")

# 提供解析梯度
def rosenbrock_grad(x):
 return np.array([
 -2*(1 - x[0]) - 400*x[0]*(x[1] - x[0]**2),
 200*(x[1] - x[0]**2)
 ])

result_bfgs_exact = minimize(
 rosenbrock, x0, method='BFGS', jac=rosenbrock_grad
)
print(f"BFGS(精确梯度): x*={result_bfgs_exact.x}, f={result_bfgs_exact.fun:.2e}")
print(f"迭代次数: {result_bfgs_exact.nit}")
```

| 方法 | 需要梯度 | 适用场景 |
|------|---------|---------|
| `Nelder-Mead` | 否 | 噪声目标函数，低维（< 20） |
| `BFGS` | 否（数值近似）/是 | 光滑函数，中维 |
| `CG` | 是 | 大规模优化 |
| `Newton-CG` | 是（还需要 Hessian） | 高精度的中规模问题 |
| `L-BFGS-B` | 否 | 有边界约束的大规模问题 |

#### 4.2 带约束优化

```python
import numpy as np
from scipy.optimize import minimize

# 目标：min f(x,y) = (x-1)^2 + (y-2.5)^2
# 约束：x + y >= 1, y <= x + 1, x >= 0
def objective(x):
 return (x[0] - 1)**2 + (x[1] - 2.5)**2

constraints = [
 {'type': 'ineq', 'fun': lambda x: x[0] + x[1] - 1}, # x+y >= 1
 {'type': 'ineq', 'fun': lambda x: x[0] + 1 - x[1]}, # y <= x+1
]
bounds = [(0, None), (None, None)] # x>=0, y 无界

result = minimize(objective, (2, 0), constraints=constraints, bounds=bounds)
print(f"约束最优解: x*={result.x}, f={result.fun:.4f}")
```

> 在 C 语言中，实现 BFGS 优化器需要数百行代码，且容易在数值稳定性上出错。SciPy 封装了成熟的 Fortran 优化器，经过数十年的测试和优化。

---

### 第五节：曲线拟合与求根

#### 5.1 非线性最小二乘曲线拟合

```python
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# 真实模型：y = a * exp(-b * x) + c
def model(x, a, b, c):
 return a * np.exp(-b * x) + c

# 生成含噪声的观测数据
np.random.seed(42)
x_data = np.linspace(0, 4, 50)
y_true = model(x_data, 2.5, 1.3, 0.5)
y_data = y_true + 0.2 * np.random.normal(size=len(x_data))

# 一键拟合
popt, pcov = curve_fit(model, x_data, y_data, p0=[1, 1, 0])
print(f"拟合参数: a={popt[0]:.3f}, b={popt[1]:.3f}, c={popt[2]:.3f}")
# 真实值: a=2.5 b=1.3 c=0.5

# 参数的不确定性（标准差）
perr = np.sqrt(np.diag(pcov))
print(f"参数标准差: a={perr[0]:.3f}, b={perr[1]:.3f}, c={perr[2]:.3f}")
```

> `curve_fit` 的本质是使用 Levenberg-Marquardt 算法求解非线性最小二乘问题。若想用一行命令在终端快速测试：
> ```bash
> python -c "from scipy.optimize import curve_fit; import numpy as np; x=np.linspace(0,4,50); y=2.5*np.exp(-1.3*x)+0.5+0.2*np.random.randn(50); popt,_=curve_fit(lambda x,a,b,c:a*np.exp(-b*x)+c,x,y); print(popt)"
> ```

#### 5.2 方程求根

```python
import numpy as np
from scipy.optimize import root_scalar, root

# 标量求根：f(x) = 0
def f(x):
 return x**3 - x - 2

# Brent 方法（默认，稳健且快速）
sol = root_scalar(f, bracket=[1, 2], method='brentq')
print(f"根: x = {sol.root:.10f}, 迭代: {sol.iterations}")

# 向量求根：方程组 f(x) = 0
def system(vars):
 x, y = vars
 return [x**2 + y**2 - 4,
 x * y - 1]

sol_sys = root(system, [1.0, 1.0]) # 初始猜测
print(f"方程组的根: x={sol_sys.x[0]:.6f}, y={sol_sys.x[1]:.6f}")
print(f"验证 f(root) = {system(sol_sys.x)}")
```

> 优化与求根技术的更多数学背景，参见 [[../../数学/|数学专题]]。

---

## 力扣练习

以下题目用于验证本章所学内容：

| 题号 | 题目 | 链接 | 涉及知识点 |
|------|------|------|-----------|
| 50 | Pow(x, n) | https://leetcode.cn/problems/powx-n/ | 快速幂、数值计算 |
| 69 | x 的平方根 | https://leetcode.cn/problems/sqrtx/ | 数值方法、二分/牛顿迭代 |
| 367 | 有效的完全平方数 | https://leetcode.cn/problems/valid-perfect-square/ | 数值判断、二分 |
