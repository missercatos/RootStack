# SymPy：符号计算 (SymPy: Symbolic Math)
---

## 📖 章节概述

SymPy 是 Python 的符号数学库——它处理的是"数学表达式"本身，而非数值。求导得到的是精确的表达式而非近似值，积分是解析结果而非数值近似。本章从符号变量的创建开始，逐步展开表达式的化简、展开、微积分（求导、积分、极限）、方程求解与矩阵符号运算，并展示如何将结果输出为 LaTeX 格式。对于习惯了 C 语言中"一切皆数值"的开发者而言，SymPy 打开了一扇进入符号计算世界的大门。

> **核心理念**：符号计算与数值计算是互补的两种范式。数值计算回答"这个数是多少"（近似），符号计算回答"这个关系是什么"（精确）。在 C 语言中实现符号微积分需要手写 CAS 逻辑或调用外部 CAS 库；SymPy 将其内嵌为 Python 的原生操作，让你在同一语言中自由切换两种范式。

---

### 📚 第一节：符号变量的创建与使用

#### 1.1 初识符号变量

在 SymPy 中，`symbols` 是核心构建块——它代表数学中的"未知数"，区别于 NumPy 的"数值数组"。

```python
from sympy import symbols, pi, E, I, oo

x, y, z = symbols('x y z')
n = symbols('n', integer=True, positive=True)
a, b = symbols('a b', real=True)

# 符号表达式
expr = x**2 + 2*x*y + y**2
print(expr)           # x**2 + 2*x*y + y**2
print(type(expr))     # <class 'sympy.core.add.Add'>

# 内置数学常数
print(pi)             # pi（符号 π，无限精度）
print(pi.evalf(50))   # 3.1415926535897932384626433832795028841971693993751...

print(oo)             # 无穷大（符号）
print(E)              # 自然常数 e
print(I**2)           # -1
```

#### 1.2 符号计算 vs 数值计算

```python
import math
from sympy import symbols, sqrt, sin

x = symbols('x')

# 符号微分 — 得到精确表达式
expr = sin(x)
# diff 由第二节详述，这里只展示符号 vs 数值的本质差异

# 数值计算（C 风格思维）
import math as m
print(m.sqrt(2))       # 1.4142135623730951  — 有限精度近似

# 符号计算（SymPy 风格）
print(sqrt(2))         # sqrt(2)  — 精确的数学表达式，保持未求值状态
print(sqrt(2).evalf()) # 1.41421356237310  — 按需转换为数值
print(sqrt(8))         # 2*sqrt(2)  — 自动化简
```

> 💡 SymPy 默认将表达式保持在"精确的符号形式"，不自动转换为浮点数。需要数值结果时调用 `.evalf()` 或 `N()` 函数。这与 C 程序员习惯于"一切立即被计算"的思维有根本不同。

#### 1.3 符号函数的创建

```python
from sympy import symbols, Function, sin, cos, exp, log

# 预定义的数学函数
x = symbols('x')
print(sin(x)**2 + cos(x)**2)   # sin(x)**2 + cos(x)**2

# 自定义未定函数（unknown function）
f, g = symbols('f g', cls=Function)
print(f(x))                     # f(x)
print(f(g(x)))                  # f(g(x))

# 泛函操作：代入值
expr = x**2 + 3*x + 2
print(expr.subs(x, 1))          # 6
print(expr.subs(x, 2.0))        # 12.0000000000000

# 多变量同时替换
expr = x**2 + y**2
print(expr.subs({x: 1, y: 2}))  # 5
```

### 📝 小节练习

> [!question] 选择题 1
> `sqrt(2)` 在 SymPy 中的输出是？
> - [ ] A. `1.4142135623730951`
> - [ ] B. `sqrt(2)`
> - [ ] C. `1.414
> - [ ] D. `2.0`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: SymPy 默认保持精确的符号形式 `sqrt(2)`，不自动求值。使用 `.evalf()` 或 `float(sqrt(2))` 才转换为数值近似。

> [!question] 判断题 1
> SymPy 的符号变量 `x = symbols('x')` 等价于 Python 的普通变量 `x = 0`。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `symbols('x')` 返回的是一个 SymPy 符号对象，代表数学意义上的"未知数/变量"，可以进行符号运算。普通 Python 变量存储的是数值。

---

### 📚 第二节：表达式化简与展开

#### 2.1 基本代数操作

```python
from sympy import symbols, expand, factor, simplify, apart, together

x, y = symbols('x y')

# 展开
expr = (x + y)**3
print(expand(expr))       # x**3 + 3*x**2*y + 3*x*y**2 + y**3

# 因式分解
expr2 = x**4 - 4*x**2 + 3
print(factor(expr2))      # (x - 1)*(x + 1)*(x**2 - 3)

# 指定域上的因式分解
print(factor(x**2 - 2))   # x**2 - 2  (有理数域上不可分解)

# 部分分式
expr3 = (x + 1) / (x**2 + 4*x + 3)
print(apart(expr3))       # 1/(2*(x + 3)) + 1/(2*(x + 1))

# 通分
print(together(1/x + 1/y))  # (x + y)/(x*y)

# 简化（尝试多种化简策略）
expr4 = (x**3 + x**2 - x - 1) / (x**2 + 2*x + 1)
print(simplify(expr4))    # x - 1
```

#### 2.2 三角函数化简

```python
from sympy import symbols, sin, cos, tan, trigsimp, expand_trig

x = symbols('x')

# 三角化简
expr = sin(x)**2 + cos(x)**2
print(trigsimp(expr))         # 1

expr2 = sin(2*x)
print(expand_trig(expr2))     # 2*sin(x)*cos(x)

# 双曲函数
from sympy import sinh, cosh
print(sinh(x)**2 - cosh(x)**2)  # -1??? 实际上 cosh^2 - sinh^2 = 1
# 验证
print((cosh(x)**2 - sinh(x)**2).simplify())  # 1
```

#### 2.3 假设与条件化简

```python
from sympy import symbols, sqrt, refine, Q

x = symbols('x')
print(sqrt(x**2))         # sqrt(x**2)  不自动化简（x 符号未知）

# 明确声明 x 为实数
x = symbols('x', real=True)
print(sqrt(x**2))         # |x|  (SymPy 1.x+ 下)

# 明确声明 x 为正数
x = symbols('x', positive=True)
print(sqrt(x**2))         # x  (符号为正，绝对值可去)
print(refine(sqrt(x**2), Q.positive(x)))  # x
```

> 💡 `simplify` 内部组合了多种化简算法，对于大表达式可能较慢。如果你明确知道需要哪种化简（如 `expand`, `factor`, `trigsimp`），直接调用对应函数更快且结果可预测。

### 📝 小节练习

> [!question] 选择题 1
> `expand((x + 1)*(x - 1))` 的结果是？
> - [ ] A. `x^2 - 1`
> - [ ] B. `x**2 - 1`
> - [ ] C. `(x - 1)*(x + 1)`
> - [ ] D. `1 - x**2`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `expand` 展开多项式乘积，得到 `x**2 - 1`（SymPy 使用 `**` 表示幂运算）。

> [!question] 判断题 1
> `simplify` 总能产生最短的表达式形式。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `simplify` 使用启发式算法尝试多种化简，但不保证得到"最短"或"最简"形式。对于特定类型的表达式（三角、有理函数），专用函数（`trigsimp`, `apart` 等）可能得到更好的结果。

---

### 📚 第三节：微积分符号运算

#### 3.1 求导

```python
from sympy import symbols, diff, sin, cos, exp, log, Derivative

x, y = symbols('x y')

# 一阶导数
print(diff(sin(x), x))          # cos(x)

# 高阶导数
print(diff(x**4, x, 3))         # 24*x   (三阶导数)

# 偏导数
f = x*sin(x*y) + exp(x*y)
print(diff(f, x))               # x*y*cos(x*y) + sin(x*y) + y*exp(x*y)
print(diff(f, y))               # x**2*cos(x*y) + x*exp(x*y)

# 链式求导
g = sin(x**2)
print(diff(g, x))               # 2*x*cos(x**2)

# 未求值导数
d = Derivative(sin(x), x)       # 不计算，仅表示
print(d)                         # Derivative(sin(x), x)
print(d.doit())                  # cos(x)  显式求值
```

> 你可以在终端中快速验证导数：
> ```bash
> python -c "from sympy import *; x=symbols('x'); print(diff(sin(x**2), x))"
> ```

#### 3.2 积分

```python
from sympy import symbols, integrate, Integral, oo, sin, exp, log

x, a, b = symbols('x a b')

# 不定积分
print(integrate(sin(x), x))     # -cos(x)
print(integrate(log(x), x))     # x*log(x) - x

# 定积分
print(integrate(sin(x), (x, 0, pi)))      # 2
print(integrate(exp(-x**2), (x, 0, oo)))  # sqrt(pi)/2

# 带参数的积分
print(integrate(exp(-a*x), (x, 0, oo)))   # Piecewise((1/a, Abs(arg(a)) < pi/2), ...)

# 未求值积分 — 当 SymPy 找不到解析形式时
print(integrate(sin(sin(x)), x))          # Integral(sin(sin(x)), x)
```

#### 3.3 极限

```python
from sympy import symbols, limit, oo, sin

x, n = symbols('x n')

# 基本极限
print(limit(sin(x)/x, x, 0))        # 1

# 无穷极限
print(limit((1 + 1/n)**n, n, oo))   # E  (欧拉数)

# 单侧极限
print(limit(1/x, x, 0, dir='+'))    # oo  (正无穷)
print(limit(1/x, x, 0, dir='-'))    # -oo (负无穷)

# 级数展开
from sympy import series
print(series(exp(x), x, 0, 6))      # 1 + x + x**2/2 + x**3/6 + x**4/24 + x**5/120 + O(x**6)
```

> 💡 如果你的积分未符号化地解出（如 `sin(sin(x))`），表明该积分可能没有初等函数形式的解析表达式。此时应该切换到 [[04_数值模拟：微分方程求解|数值模拟]] 进行数值积分。

### 📝 小节练习

> [!question] 选择题 1
> `integrate(f(x), x)` 返回 `Integral(f(x), x)`，这意味着？
> - [ ] A. 积分结果为零
> - [ ] B. SymPy 找不到该积分的解析表达式
> - [ ] C. 语法错误
> - [ ] D. 需要先求导
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 当 SymPy 无法找到积分的闭式（解析）表达时，返回未求值的 `Integral` 对象。这不是错误，而是表示"我算不出来解析形式"。

> [!question] 判断题 1
> `diff` 函数无法计算混合偏导数。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `diff(f, x, y)` 或 `diff(f, x, 2, y, 1)` 可以计算混合偏导数（先对 x 求 2 次，再对 y 求 1 次）。

---

### 📚 第四节：方程求解与矩阵符号运算

#### 4.1 方程求解

```python
from sympy import symbols, Eq, solve, solveset, nonlinsolve

x, y = symbols('x y')

# 单个方程
sol = solve(x**2 - 5*x + 6, x)
print(sol)                    # [2, 3]

# 使用 Eq 显式表示等式
eq = Eq(x**2 + y**2, 1)
sol = solve(eq, x)            # 解出 x 用 y 表示
print(sol)                    # [-sqrt(1 - y**2), sqrt(1 - y**2)]

# 方程组
sol_xy = solve([x**2 + y**2 - 25, x - y - 1], [x, y])
print(sol_xy)                 # [(-3, -4), (4, 3)]

# 非线性方程组
sol = nonlinsolve([x + y - 3, x*y - 2], [x, y])
print(sol)                    # {(1, 2), (2, 1)}
```

#### 4.2 矩阵符号运算

```python
from sympy import symbols, Matrix, eye, zeros, ones, det, trace

# 符号矩阵
M = Matrix([[1, x],
            [y, 1]])
print(M)
# Matrix([[1, x],
#         [y, 1]])

# 矩阵行列式
print(det(M))                 # 1 - x*y

# 矩阵运算
A = Matrix([[1, 2],
            [3, 4]])
B = Matrix([[5, 6],
            [7, 8]])

print(A + B)                  # Matrix([[6, 8], [10, 12]])
print(A * B)                  # 矩阵乘法
print(A.inv())                # 符号逆矩阵

# 特征值
lambda_sym = symbols('lambda')
M = Matrix([[1, 2],
            [2, 1]])
print(M.eigenvals())          # {3: 1, -1: 1}
print(M.eigenvects())         # 完整的特征向量分解

# 符号矩阵求解 AX = B
X = A.solve(Matrix([5, 11]))
print(X)                      # Matrix([[1], [2]])
```

#### 4.3 LaTeX 输出

```python
from sympy import symbols, latex, sin, Integral, oo, Matrix

x, a = symbols('x a')

# 单个表达式
print(latex(x**2 + sin(x)))
# x^{2} + \sin{\left(x \right)}

# 定积分
int_expr = Integral(sin(x**2), (x, 0, oo))
print(latex(int_expr))
# \int\limits_{0}^{\infty} \sin{\left(x^{2} \right)}\, dx

# 矩阵
M = Matrix([[1, x], [a, x**2]])
print(latex(M))
# \left[\begin{matrix}1 & x\\a & x^{2}\end{matrix}\right]
```

> 💡 LaTeX 输出使得 SymPy 可以直接嵌入科学论文写作工作流——推导在 Python 中完成，结果直接粘贴为 LaTeX 公式。

### 📝 小节练习

> [!question] 选择题 1
> `solve([x + y - 5, x - y - 1], [x, y])` 的结果是什么？
> - [ ] A. `(2, 3)`
> - [ ] B. `[(3, 2)]`
> - [ ] C. `{x: 3, y: 2}` （字典形式）
> - [ ] D. 报错
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: 当 `solve` 的第二个参数是符号列表时，返回字典列表 `[{x: 3, y: 2}]` 或元组列表。具体格式取决于 SymPy 版本和方程的形式。

> [!question] 判断题 1
> SymPy 的矩阵符号运算可以处理包含符号变量的矩阵。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 这是 SymPy 的核心功能之一——矩阵元素可以是符号，行列式、特征值、逆矩阵等都以符号表达式形式给出。

---

## 📋 章节测试

### 一、判断题（正确选✅，错误选❌）

> [!question] 判断题 1
> SymPy 中 `sqrt(2)` 自动等价于 `1.4142...`。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: SymPy 保持符号精确形式 `sqrt(2)`不出数值，需要 `.evalf()` 才转为浮点。

> [!question] 判断题 2
> `symbols('x')` 创建的 `x` 既可以用于符号计算，也可以替代 NumPy 数组作为数值计算。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: SymPy 符号对象与 NumPy 数组是完全不同的类型，不能在 NumPy 的向量化操作中直接使用，也不存储数值。

> [!question] 判断题 3
> `diff(f(x), x)` 返回的是数值导数（如有限差分近似）。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `diff` 返回精确的符号导数（解析形式），而非数值近似。数值导数需要使用 `scipy.misc.derivative` 或手动有限差分。

> [!question] 判断题 4
> `integrate(exp(-x**2), x)` 总能返回初等函数形式的表达式。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `exp(-x^2)` 的不定积分不能用初等函数表达。SymPy 会返回 `sqrt(pi)*erf(x)/2`（使用特殊函数 erf 表达），或对于无法表达的返回 `Integral` 对象。

> [!question] 判断题 5
> SymPy 的 `Matrix` 支持求逆、特征值和行列式的**符号**计算。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: SymPy 矩阵的元素可以是符号，`A.inv()` 返回的是符号逆矩阵表达式，`A.eigenvals()` 返回符号特征值。

> [!question] 判断题 6
> `latex` 函数只能输出单个表达式，不能输出矩阵。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `latex` 支持矩阵、积分、求和等复杂结构，输出对应的 LaTeX 排版代码。

> [!question] 判断题 7
> 在 C 语言中实现符号微积分，通常需要集成外部 CAS 库（如 GiNaC、SymEngine）或自己手写模式匹配引擎。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: C 语言没有内置的符号计算能力。实现符号化简/微分/积分需要大量的模式匹配和表达式树操作代码，工业级方案通常依赖外部 CAS 库。

---

### 二、选择题（单项选择题）

> [!question] 选择题 1
> SymPy 中表示"无穷大"的符号是？
> - [ ] A. `sympy.inf`
> - [ ] B. `sympy.oo`（两个小写 o）
> - [ ] C. `sympy.infinity`
> - [ ] D. `sympy.NaN`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: SymPy 使用 `oo`（两个小写字母 o）表示正无穷，`-oo` 表示负无穷。类似 `sin(1/x)` 在 `x -> 0` 时的极限不存在。

> [!question] 选择题 2
> 以下哪个函数用于展开三角函数的倍角公式？
> - [ ] A. `trigsimp`
> - [ ] B. `expand_trig`
> - [ ] C. `simplify`
> - [ ] D. `expand`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `expand_trig` 将 `sin(2x)` 展开为 `2*sin(x)*cos(x)`。`trigsimp` 做相反的化简：将 `sin(x)**2 + cos(x)**2` 化简为 1。

> [!question] 选择题 3
> 以下哪项不是 SymPy 的内置功能？
> - [ ] A. 符号微分
> - [ ] B. 符号积分
> - [ ] C. 数值偏微分方程求解
> - [ ] D. 矩阵符号逆运算
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: SymPy 处理符号（解析）数学，不包括数值 PDE 求解。数值 PDE 求解需要使用 SciPy、FEniCS 或其他数值计算库。参见 [[04_数值模拟：微分方程求解|数值模拟章节]]。

> [!question] 选择题 4
> `print(latex(Integral(x**2, (x, 0, 1))))` 输出中一定出现下面哪个 LaTeX 命令？
> - [ ] A. `\sum`
> - [ ] B. `\int`
> - [ ] C. `\frac`
> - [ ] D. `\alpha`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `Integral` 对象转为 LaTeX 时出现 `\int`（积分符号）。`\frac` 只在分式表达式中出现，`\sum` 只在求和中出现。

> [!question] 选择题 5
> `solve(x**2 == 4, x)` 的正确写法是？
> - [ ] A. `solve(x**2 == 4, x)`
> - [ ] B. `solve(Eq(x**2, 4), x)`
> - [ ] C. `solve(x**2 - 4, x)`
> - [ ] D. B 和 C 都对
>
> > [!success]- 点击查看答案
> > 正确答案: D
> > **解析**: `solve` 可以接受两种形式：隐式 `f(x) = 0`（传入 `x**2 - 4`）或显式等式 `Eq` 对象（传入 `Eq(x**2, 4)`）。A 中的 `==` 在 SymPy 上下文中不是结构相等而是 Python 的布尔比较。

> [!question] 选择题 6
> 以下哪个 SymPy 函数可以计算函数的泰勒级数展开？
> - [ ] A. `taylor`
> - [ ] B. `expand`
> - [ ] C. `series`
> - [ ] D. `limit`
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: `series(expr, x, x0, n)` 计算 `expr` 在 `x = x0` 处的 n 阶级数展开。末项为 `O(x**n)` 表示截断误差。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：梯度与 Hessian 矩阵的计算
> **难度**: ⭐⭐
>
> 定义多元函数 `f(x,y,z) = x^3 + y^2*z + sin(x*y) + exp(z)`。使用 SymPy 计算：（1）梯度向量（三个偏导数）；（2）Hessian 矩阵（所有二阶偏导数）。使用 `latex()` 输出梯度向量和 Hessian 矩阵的 LaTeX 代码。验证 `hessian(f, [x,y,z])` 函数与手动逐个求二阶偏导的结果一致。

> [!example] 练习题 2：常微分方程解析解
> **难度**: ⭐⭐
>
> 使用 `sympy.dsolve` 求解常微分方程 `y''(x) + 4*y'(x) + 3*y(x) = 0`，分别给定初始条件 `y(0)=1` 和 `y'(0)=0`。绘制解析解的图像（用 `lambdify` 将 SymPy 表达式转为 NumPy 可调用函数后绘图）。

> [!example] 练习题 3：电路网络分析
> **难度**: ⭐⭐⭐
>
> RLC 串联电路：使用 SymPy 符号推导从时域到 s 域（Laplace 变换）的转移函数 `H(s) = V_out(s)/V_in(s)`。使用 `sympy.inverse_laplace_transform` 求冲激响应。将结果与手动推导对比。

> [!example] 练习题 4：机器人运动学
> **难度**: ⭐⭐⭐
>
> 一个 2 连杆平面机械臂：定义符号变量 `theta1, theta2, l1, l2`（关节角和杆长）。使用 SymPy 矩阵推导正运动学——末端执行器 (x, y) 关于关节角和杆长的符号表达式。计算雅可比矩阵 `J = ∂(x,y)/∂(θ1,θ2)` 的行列式的零点——这些是机械臂的奇异位形。

> [!example] 练习题 5：三重积分的解析计算
> **难度**: ⭐⭐
>
> 使用 SymPy 的 `integrate` 计算球体 `x^2 + y^2 + z^2 <= R^2` 的体积（三重积分）。按 `dz dy dx` 的顺序积分，使用符号假设 `symbols('R', positive=True)`。将结果与已知公式 `V = 4/3 * π * R^3` 比较。
