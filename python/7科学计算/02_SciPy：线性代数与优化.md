# SciPy：线性代数与优化 (SciPy: Linear Algebra & Optimization)
---

## 📖 章节概述

SciPy 是 Python 科学计算工具箱中的"重型武器"。如果说 NumPy 提供了数组和基础运算，SciPy 则在上面构建了线性代数、优化、积分、插值、信号处理等专业模块。本章聚焦 `scipy.linalg` 与 `scipy.optimize` 两大核心：从求解线性方程组、计算特征值与 SVD 分解，到函数极值优化、曲线拟合和求根。我们将对比这些操作在 C 语言中需要如何调用 LAPACK/BLAS，以及 SciPy 如何用一行代码完成这些任务。

> **核心理念**：SciPy 不是"又一个新的线性代数库"，它是对久经考验的 LAPACK/BLAS Fortran 代码的高层次封装。当你在 Python 中调用 `scipy.linalg.solve(A, b)` 时，底层运行的正是那些在超级计算机上优化了几十年的 Fortran 子程序。

---

### 📚 第一节：SciPy 与 NumPy 的 linalg 对比

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
x_np = np.linalg.solve(A, b)    # [2. 3.]
x_sp = la.solve(A, b)            # [2. 3.]

# 显式的 LU 分解只有 SciPy 提供
P, L, U = la.lu(A)
print("L:\n", L)
print("U:\n", U)
print("P @ L @ U:\n", P @ L @ U)  # 还原 A
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

### 📝 小节练习

> [!question] 选择题 1
> 何时应该使用 `scipy.linalg` 而不用 `numpy.linalg`？
> - [ ] A. 任何时候都应该用 SciPy
> - [ ] B. 需要显式的 LU/QR/Cholesky 分解时
> - [ ] C. 任何时候都应该用 NumPy
> - [ ] D. 两者完全相同
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `numpy.linalg` 提供最常用的求解器（solve, eig, svd 等），`scipy.linalg` 额外提供显式分解函数以及针对特殊矩阵结构（对称、正定、带状）的优化版本。

> [!question] 判断题 1
> `scipy.linalg` 底层完全用 Python 编写。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `scipy.linalg` 是对 LAPACK/BLAS（Fortran 编写，几十年优化历史）的 Python 封装，核心计算全部在编译后的 Fortran/C 代码中执行。

---

### 📚 第二节：解线性方程组

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
print(f"解: {x}")                  # [1. 1. 2.]
print(f"验证: {A @ x}")            # 应等于 b

# 同时求解多个右侧向量
B = np.array([[4, 1],
              [11, 2],
              [8, 3]])             # 3×2 矩阵，两套 b
X = la.solve(A, B)                 # 同时求解 AX = B
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

A = np.vstack([x_data, np.ones_like(x_data)]).T   # 设计矩阵
# A 形状 (6, 2)，b 形状 (6,)

coeffs, residuals, rank, sv = la.lstsq(A, y_data)
print(f"拟合系数: y = {coeffs[0]:.3f}x + {coeffs[1]:.3f}")
# y = 2.000x + 1.067
```

> 💡 在 C 语言中，最小二乘通常需要调用 LAPACK 的 `*gels` 或 `*gelsd` 函数，需要手写工作区计算和多级指针管理。SciPy 一行直接出结果。

#### 2.3 特殊矩阵结构优化

```python
import numpy as np
import scipy.linalg as la

n = 1000
A = np.random.rand(n, n)
A = A + A.T + n * np.eye(n)   # 构造对称正定矩阵

# 一般求解器 — 不知道矩阵结构，使用 LU
x1 = la.solve(A, np.ones(n))

# Cholesky 专用于对称正定矩阵 — 速度约为 LU 的 2 倍
L = la.cholesky(A, lower=True)      # A = L @ L.T
x2 = la.cho_solve((L, True), np.ones(n))

print(f"结果一致: {np.allclose(x1, x2)}")  # True
```

> ⚠️ 如果你的矩阵已知是对称正定的，一定要使用 `cho_solve`——它比普通 `solve` 快约一倍，且数值更稳定。

### 📝 小节练习

> [!question] 选择题 1
> 超定线性方程组（方程数多于未知数）的求解方法通常是？
> - [ ] A. 高斯消元
> - [ ] B. LU 分解
> - [ ] C. 最小二乘法
> - [ ] D. 无法求解
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: 超定系统通常无精确解，需要最小二乘解：最小化 ||Ax - b||²。SciPy 中 `la.lstsq` 或 `np.linalg.lstsq` 处理此类问题。

> [!question] 判断题 1
> `la.solve(A, b)` 内部会根据矩阵特性自动选择最优算法。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `la.solve` 使用通用的 LU 分解，**不会**自动检测矩阵特性。需要手动根据矩阵结构选择专用函数（如 `cho_solve` 用于对称正定矩阵）。

---

### 📚 第三节：特征值与奇异值分解

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
print(f"eigh 特征值: {eigvals_h}")          # 升序排列
print(f"正交性验证: \n{eigvecs_h.T @ eigvecs_h}")  # 近似单位矩阵

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
print(f"伪逆 M+ 形状: {M_plus.shape}")  # (5, 4)
```

> 💡 在 C 中调用 LAPACK 的 `*gesvd` 或 `*gesdd` 进行 SVD 需要管理几十个参数和工作区。SciPy 将其封装为单行调用，且自动选择分治算法（`gesdd`）——比传统 QR 迭代算法更快。

### 📝 小节练习

> [!question] 选择题 1
> `scipy.linalg.eigh` 相比 `scipy.linalg.eig` 的优势是？
> - [ ] A. 可用于非对称矩阵
> - [ ] B. 对于对称矩阵更快且保证实数特征值
> - [ ] C. 总能输出更精确的结果
> - [ ] D. 无需输入矩阵
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `eigh` 专门针对对称/厄米矩阵优化，利用矩阵结构使用更高效的算法，且保证输出实数特征值（升序排列）。

> [!question] 判断题 1
> SVD 分解对任何矩阵都存在，无论矩阵是否方阵。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 任何 m×n 矩阵都存在 SVD 分解：`M = U Σ V^T`。这是 SVD 相较特征值分解的关键优势——特征值分解只适用于方阵且要求对角化。

---

### 📚 第四节：函数极值优化

#### 4.1 无约束优化：`scipy.optimize.minimize`

现代科学中的优化问题远超越简单的线性方程组——函数拟合、参数优化、机器学习训练，都需要通用的数值优化器。

```python
import numpy as np
from scipy.optimize import minimize

# Rosenbrock 函数（优化界的"Hello World"）
# f(x,y) = (1-x)^2 + 100(y-x^2)^2，全局最小值在 (1,1)
def rosenbrock(x):
    return (1 - x[0])**2 + 100 * (x[1] - x[0]**2)**2

x0 = np.array([0, 0])  # 初始猜测

# Nelder-Mead（单纯形法，无梯度）
result_nm = minimize(rosenbrock, x0, method='Nelder-Mead')
print(f"Nelder-Mead: x*={result_nm.x}, f={result_nm.fun:.2e}")

# BFGS（拟牛顿法，使用数值梯度）
result_bfgs = minimize(rosenbrock, x0, method='BFGS')
print(f"BFGS:        x*={result_bfgs.x}, f={result_bfgs.fun:.2e}")

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
    {'type': 'ineq', 'fun': lambda x: x[0] + x[1] - 1},  # x+y >= 1
    {'type': 'ineq', 'fun': lambda x: x[0] + 1 - x[1]},  # y <= x+1
]
bounds = [(0, None), (None, None)]   # x>=0, y 无界

result = minimize(objective, (2, 0), constraints=constraints, bounds=bounds)
print(f"约束最优解: x*={result.x}, f={result.fun:.4f}")
```

> 💡 在 C 语言中，实现 BFGS 优化器需要数百行代码，且容易在数值稳定性上出错。SciPy 封装了成熟的 Fortran 优化器，经过数十年的测试和优化。

### 📝 小节练习

> [!question] 选择题 1
> 以下优化方法中，哪一个不需要梯度信息？
> - [ ] A. BFGS
> - [ ] B. Newton-CG
> - [ ] C. Nelder-Mead
> - [ ] D. CG
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: Nelder-Mead（单纯形法）是零阶方法，仅依赖于函数值比较而不需要导数信息。适合目标函数不平滑或梯度难以计算的场景。

> [!question] 判断题 1
> `minimize` 的 BFGS 方法如果未提供 `jac`，内部会使用解析方式推导梯度。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 如果未提供 `jac`，BFGS 使用**有限差分**近似梯度（在 `x` 附近计算函数值差商），而非解析推导。提供精确 `jac` 可显著提升收敛速度和精度。

---

### 📚 第五节：曲线拟合与求根

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
# 真实值:  a=2.5  b=1.3  c=0.5

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

sol_sys = root(system, [1.0, 1.0])   # 初始猜测
print(f"方程组的根: x={sol_sys.x[0]:.6f}, y={sol_sys.x[1]:.6f}")
print(f"验证 f(root) = {system(sol_sys.x)}")
```

> 🔗 优化与求根技术的更多数学背景，参见 [[../../数学/|数学专题]]。

### 📝 小节练习

> [!question] 选择题 1
> `curve_fit` 内部使用的优化算法是？
> - [ ] A. 梯度下降
> - [ ] B. Levenberg-Marquardt
> - [ ] C. 单纯形法
> - [ ] D. 贝叶斯推断
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `curve_fit` 使用 Levenberg-Marquardt 算法求解非线性最小二乘问题，结合了高斯-牛顿法和梯度下降法的优点。

> [!question] 判断题 1
> `root_scalar(f, bracket=[a, b])` 要求 `f(a)` 和 `f(b)` 同号。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 括号法（如 brentq）要求 `f(a)` 和 `f(b)` **异号**（即区间内必有根）。若同号，无法保证区间内存在根，算法会报错。

---

## 📋 章节测试

### 一、判断题（正确选✅，错误选❌）

> [!question] 判断题 1
> `scipy.linalg` 和 `numpy.linalg` 底层都调用 LAPACK/BLAS。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 两者都是 LAPACK/BLAS 的封装。区别在于 SciPy 封装了更完整的 LAPACK 接口，而 NumPy 仅捆绑了精简子集。

> [!question] 判断题 2
> `la.solve(A, b)` 可以同时处理多个右侧向量 `b`。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 当 `b` 是一个二维数组时（每列代表一套右侧向量），`la.solve` 同时求解所有方程组——这比循环调用高效得多，因为 LU 分解只需计算一次。

> [!question] 判断题 3
> Cholesky 分解适用于任何方阵。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: Cholesky 分解仅适用于**对称正定矩阵**。对于一般方阵，应使用 LU 分解（`la.lu`）或直接使用 `la.solve`。

> [!question] 判断题 4
> SVD 分解中 `U` 和 `Vt` 不一定是正交矩阵。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: SVD 分解中 `U` 和 `V` 始终是正交矩阵（酉矩阵），其列向量构成标准正交基。这是 SVD 的定义性质。

> [!question] 判断题 5
> `curve_fit` 返回的 `pcov` 矩阵的对角线元素是各参数方差的估计值。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `pcov` 是参数的协方差矩阵，对角线元素为各参数方差的估计，`np.sqrt(np.diag(pcov))` 即为参数的标准差（1σ 不确定度）。

> [!question] 判断题 6
> `minimize` 的 `Nelder-Mead` 方法可以保证找到全局最小值。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: Nelder-Mead 和所有局部优化方法一样，只能找到**局部最小值**。对于非凸函数，结果依赖于初始猜测。全局优化需要使用 `scipy.optimize.differential_evolution` 或 `basinhopping`。

> [!question] 判断题 7
> 在 C 语言中直接调用 LAPACK 比在 Python 中通过 SciPy 调用更快。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 速度相同——两者底层执行的都是相同的 LAPACK Fortran 代码。SciPy 的 Python 调用开销微乎其微（仅仅是一次 FFI 函数调用），对于矩阵运算而言可忽略。

---

### 二、选择题（单项选择题）

> [!question] 选择题 1
> 以下可以在终端中一键运行 SciPy 优化的正确命令是？
> - [ ] A. `python -c "solve([[1,2],[3,4]],[1,2])"`
> - [ ] B. `python -c "from scipy.optimize import minimize; print(minimize(lambda x:(x-3)**2,0).x)"`
> - [ ] C. `scipy optimize min (x-3)^2`
> - [ ] D. `python -m scipy.optimize`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: B 使用 `python -c` 内联运行完整的 Python 代码，正确导入并调用 `minimize`。

> [!question] 选择题 2
> `la.lstsq` 返回的四个值分别是？
> - [ ] A. 系数、残差平方和、矩阵的秩、奇异值
> - [ ] B. 解向量、误差、迭代次数、状态码
> - [ ] C. 系数、协方差矩阵、残差、梯度
> - [ ] D. 只有一个返回值
>
> > [!success]- 点击查看答案
> > 正确答案: A
> > **解析**: `la.lstsq` 返回 `(x, residuals, rank, s)` —— 系数矩阵、残差二范数平方和、系数矩阵的数值秩、奇异值数组。

> [!question] 选择题 3
> 以下优化场景最适合使用 `curve_fit` 的是？
> - [ ] A. 找到函数的最小值
> - [ ] B. 拟合实验数据的模型参数
> - [ ] C. 求解微分方程组
> - [ ] D. 矩阵对角化
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `curve_fit` 专用于在已知函数模型框架下对观测数据进行非线性参数拟合（非线性最小二乘），返回参数最优估计值和协方差矩阵。

> [!question] 选择题 4
> 以下关于 `la.svd(M, full_matrices=False)` 的说法，正确的是？
> - [ ] A. `U` 的列数等于 `M` 的行数
> - [ ] B. `U` 的列数等于 `min(M.shape)`
> - [ ] C. `s` 的长度等于 `M.shape[0]`
> - [ ] D. `Vt` 的形状始终为方阵
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `full_matrices=False` 返回经济型 SVD：`U` 的列数和 `Vt` 的行数都等于 `k = min(m, n)`（奇异值的数量），`s` 的长度也为 `k`。

> [!question] 选择题 5
> `root(func, x0)` 与 `root_scalar(f, ...)` 的区别是？
> - [ ] A. 没区别
> - [ ] B. `root` 用于方程组（多维），`root_scalar` 用于单变量方程
> - [ ] C. `root` 不使用梯度，`root_scalar` 使用
> - [ ] D. `root` 只在 SciPy 1.0+ 可用
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `root` 求解方程组（向量值函数的零点），`root_scalar` 求解标量单变量方程 `f(x)=0`。

> [!question] 选择题 6
> LAPACK 中 `dgesv` 函数的 `d` 前缀代表？
> - [ ] A. dynamic（动态分配）
> - [ ] B. double precision（双精度浮点）
> - [ ] C. diagonal（对角化）
> - [ ] D. decomposition（分解）
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: LAPACK 命名规则：`s`=单精度, `d`=双精度, `c`=复单精度, `z`=复双精度。`dgesv` = double precision **ge**neral matrix **s**ol**v**er。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：C 与 SciPy 求解器性能对比
> **难度**: ⭐⭐
>
> 生成随机的 500×500 矩阵 A 和 500×10 的 B。分别使用 `numpy.linalg.solve` 和 `scipy.linalg.solve` 求解 `AX = B`，计时并报告性能差异。进一步，当 A 是对称正定矩阵时，对比 `cho_solve` 与普通 `solve` 的加速比。

> [!example] 练习题 2：图像 SVD 压缩
> **难度**: ⭐⭐
>
> 将一张灰度图片加载为 NumPy 矩阵，使用 `scipy.linalg.svd` 进行 SVD 分解。截断不同的奇异值数量 k（如 5, 20, 50, 100），重建图像并计算压缩率（存储 U_k, s_k, Vt_k 的元素数与原始元素数之比）和重建误差（Frobenius 范数相对误差）。

> [!example] 练习题 3：化学反应动力学参数拟合
> **难度**: ⭐⭐⭐
>
> 一级反应动力学方程：`C(t) = C0 * exp(-k * t)`。生成带噪声的观测数据 `(t_i, C_i)`，使用 `curve_fit` 拟合 `C0` 和 `k`。对比：（1）手动用 `minimize` 定义损失函数进行优化；（2）直接用 `curve_fit`。提取参数不确定度 `pcov`，绘制 95% 置信带。

> [!example] 练习题 4：热力学平衡求解
> **难度**: ⭐⭐⭐
>
> 求解二元体系的汽液平衡方程组：
> ```
> P = x1*γ1*P1_sat + x2*γ2*P2_sat
> y1*P = x1*γ1*P1_sat
> ```
> 给定总压 P，使用 `scipy.optimize.root` 求解液相组成 x1 和气相组成 y1。尝试不同的初始猜测值，观察算法是否能收敛到正确的物理根。

> [!example] 练习题 5：投资组合优化
> **难度**: ⭐⭐
>
> 给定 5 只股票的收益率协方差矩阵（构造一个半正定矩阵），使用 `scipy.optimize.minimize` 求解最小方差投资组合权重。约束条件：所有权重之和为 1（`constraints`），每个权重大于等于 0（`bounds`）。对比不同预期收益率目标下的有效前沿。提示：使用 SLSQP 方法处理约束优化。
