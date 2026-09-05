# SymPy：符号计算 (SymPy: Symbolic Math)
---

## 章节概述

SymPy 是 Python 的符号数学库——它处理的是"数学表达式"本身，而非数值。求导得到的是精确的表达式而非近似值，积分是解析结果而非数值近似。本章从符号变量的创建开始，逐步展开表达式的化简、展开、微积分（求导、积分、极限）、方程求解与矩阵符号运算，并展示如何将结果输出为 LaTeX 格式。对于习惯了 C 语言中"一切皆数值"的开发者而言，SymPy 打开了一扇进入符号计算世界的大门。

> **核心理念**：符号计算与数值计算是互补的两种范式。数值计算回答"这个数是多少"（近似），符号计算回答"这个关系是什么"（精确）。在 C 语言中实现符号微积分需要手写 CAS 逻辑或调用外部 CAS 库；SymPy 将其内嵌为 Python 的原生操作，让你在同一语言中自由切换两种范式。

---

### 第一节：符号变量的创建与使用

#### 1.1 初识符号变量

在 SymPy 中，`symbols` 是核心构建块——它代表数学中的"未知数"，区别于 NumPy 的"数值数组"。

```python
from sympy import symbols, pi, E, I, oo

x, y, z = symbols('x y z')
n = symbols('n', integer=True, positive=True)
a, b = symbols('a b', real=True)

# 符号表达式
expr = x**2 + 2*x*y + y**2
print(expr) # x**2 + 2*x*y + y**2
print(type(expr)) # <class 'sympy.core.add.Add'>

# 内置数学常数
print(pi) # pi（符号 π，无限精度）
print(pi.evalf(50)) # 3.1415926535897932384626433832795028841971693993751...

print(oo) # 无穷大（符号）
print(E) # 自然常数 e
print(I**2) # -1
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
print(m.sqrt(2)) # 1.4142135623730951 — 有限精度近似

# 符号计算（SymPy 风格）
print(sqrt(2)) # sqrt(2) — 精确的数学表达式，保持未求值状态
print(sqrt(2).evalf()) # 1.41421356237310 — 按需转换为数值
print(sqrt(8)) # 2*sqrt(2) — 自动化简
```

> SymPy 默认将表达式保持在"精确的符号形式"，不自动转换为浮点数。需要数值结果时调用 `.evalf()` 或 `N()` 函数。这与 C 程序员习惯于"一切立即被计算"的思维有根本不同。

#### 1.3 符号函数的创建

```python
from sympy import symbols, Function, sin, cos, exp, log

# 预定义的数学函数
x = symbols('x')
print(sin(x)**2 + cos(x)**2) # sin(x)**2 + cos(x)**2

# 自定义未定函数（unknown function）
f, g = symbols('f g', cls=Function)
print(f(x)) # f(x)
print(f(g(x))) # f(g(x))

# 泛函操作：代入值
expr = x**2 + 3*x + 2
print(expr.subs(x, 1)) # 6
print(expr.subs(x, 2.0)) # 12.0000000000000

# 多变量同时替换
expr = x**2 + y**2
print(expr.subs({x: 1, y: 2})) # 5
```

---

### 第二节：表达式化简与展开

#### 2.1 基本代数操作

```python
from sympy import symbols, expand, factor, simplify, apart, together

x, y = symbols('x y')

# 展开
expr = (x + y)**3
print(expand(expr)) # x**3 + 3*x**2*y + 3*x*y**2 + y**3

# 因式分解
expr2 = x**4 - 4*x**2 + 3
print(factor(expr2)) # (x - 1)*(x + 1)*(x**2 - 3)

# 指定域上的因式分解
print(factor(x**2 - 2)) # x**2 - 2 (有理数域上不可分解)

# 部分分式
expr3 = (x + 1) / (x**2 + 4*x + 3)
print(apart(expr3)) # 1/(2*(x + 3)) + 1/(2*(x + 1))

# 通分
print(together(1/x + 1/y)) # (x + y)/(x*y)

# 简化（尝试多种化简策略）
expr4 = (x**3 + x**2 - x - 1) / (x**2 + 2*x + 1)
print(simplify(expr4)) # x - 1
```

#### 2.2 三角函数化简

```python
from sympy import symbols, sin, cos, tan, trigsimp, expand_trig

x = symbols('x')

# 三角化简
expr = sin(x)**2 + cos(x)**2
print(trigsimp(expr)) # 1

expr2 = sin(2*x)
print(expand_trig(expr2)) # 2*sin(x)*cos(x)

# 双曲函数
from sympy import sinh, cosh
print(sinh(x)**2 - cosh(x)**2) # -1??? 实际上 cosh^2 - sinh^2 = 1
# 验证
print((cosh(x)**2 - sinh(x)**2).simplify()) # 1
```

#### 2.3 假设与条件化简

```python
from sympy import symbols, sqrt, refine, Q

x = symbols('x')
print(sqrt(x**2)) # sqrt(x**2) 不自动化简（x 符号未知）

# 明确声明 x 为实数
x = symbols('x', real=True)
print(sqrt(x**2)) # |x| (SymPy 1.x+ 下)

# 明确声明 x 为正数
x = symbols('x', positive=True)
print(sqrt(x**2)) # x (符号为正，绝对值可去)
print(refine(sqrt(x**2), Q.positive(x))) # x
```

> `simplify` 内部组合了多种化简算法，对于大表达式可能较慢。如果你明确知道需要哪种化简（如 `expand`, `factor`, `trigsimp`），直接调用对应函数更快且结果可预测。

---

### 第三节：微积分符号运算

#### 3.1 求导

```python
from sympy import symbols, diff, sin, cos, exp, log, Derivative

x, y = symbols('x y')

# 一阶导数
print(diff(sin(x), x)) # cos(x)

# 高阶导数
print(diff(x**4, x, 3)) # 24*x (三阶导数)

# 偏导数
f = x*sin(x*y) + exp(x*y)
print(diff(f, x)) # x*y*cos(x*y) + sin(x*y) + y*exp(x*y)
print(diff(f, y)) # x**2*cos(x*y) + x*exp(x*y)

# 链式求导
g = sin(x**2)
print(diff(g, x)) # 2*x*cos(x**2)

# 未求值导数
d = Derivative(sin(x), x) # 不计算，仅表示
print(d) # Derivative(sin(x), x)
print(d.doit()) # cos(x) 显式求值
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
print(integrate(sin(x), x)) # -cos(x)
print(integrate(log(x), x)) # x*log(x) - x

# 定积分
print(integrate(sin(x), (x, 0, pi))) # 2
print(integrate(exp(-x**2), (x, 0, oo))) # sqrt(pi)/2

# 带参数的积分
print(integrate(exp(-a*x), (x, 0, oo))) # Piecewise((1/a, Abs(arg(a)) < pi/2), ...)

# 未求值积分 — 当 SymPy 找不到解析形式时
print(integrate(sin(sin(x)), x)) # Integral(sin(sin(x)), x)
```

#### 3.3 极限

```python
from sympy import symbols, limit, oo, sin

x, n = symbols('x n')

# 基本极限
print(limit(sin(x)/x, x, 0)) # 1

# 无穷极限
print(limit((1 + 1/n)**n, n, oo)) # E (欧拉数)

# 单侧极限
print(limit(1/x, x, 0, dir='+')) # oo (正无穷)
print(limit(1/x, x, 0, dir='-')) # -oo (负无穷)

# 级数展开
from sympy import series
print(series(exp(x), x, 0, 6)) # 1 + x + x**2/2 + x**3/6 + x**4/24 + x**5/120 + O(x**6)
```

> 如果你的积分未符号化地解出（如 `sin(sin(x))`），表明该积分可能没有初等函数形式的解析表达式。此时应该切换到 [[04_数值模拟：微分方程求解|数值模拟]] 进行数值积分。

---

### 第四节：方程求解与矩阵符号运算

#### 4.1 方程求解

```python
from sympy import symbols, Eq, solve, solveset, nonlinsolve

x, y = symbols('x y')

# 单个方程
sol = solve(x**2 - 5*x + 6, x)
print(sol) # [2, 3]

# 使用 Eq 显式表示等式
eq = Eq(x**2 + y**2, 1)
sol = solve(eq, x) # 解出 x 用 y 表示
print(sol) # [-sqrt(1 - y**2), sqrt(1 - y**2)]

# 方程组
sol_xy = solve([x**2 + y**2 - 25, x - y - 1], [x, y])
print(sol_xy) # [(-3, -4), (4, 3)]

# 非线性方程组
sol = nonlinsolve([x + y - 3, x*y - 2], [x, y])
print(sol) # {(1, 2), (2, 1)}
```

#### 4.2 矩阵符号运算

```python
from sympy import symbols, Matrix, eye, zeros, ones, det, trace

# 符号矩阵
M = Matrix([[1, x],
 [y, 1]])
print(M)
# Matrix([[1, x],
# [y, 1]])

# 矩阵行列式
print(det(M)) # 1 - x*y

# 矩阵运算
A = Matrix([[1, 2],
 [3, 4]])
B = Matrix([[5, 6],
 [7, 8]])

print(A + B) # Matrix([[6, 8], [10, 12]])
print(A * B) # 矩阵乘法
print(A.inv()) # 符号逆矩阵

# 特征值
lambda_sym = symbols('lambda')
M = Matrix([[1, 2],
 [2, 1]])
print(M.eigenvals()) # {3: 1, -1: 1}
print(M.eigenvects()) # 完整的特征向量分解

# 符号矩阵求解 AX = B
X = A.solve(Matrix([5, 11]))
print(X) # Matrix([[1], [2]])
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

> LaTeX 输出使得 SymPy 可以直接嵌入科学论文写作工作流——推导在 Python 中完成，结果直接粘贴为 LaTeX 公式。

---

## 力扣练习

以下题目用于验证本章所学内容：

| 题号 | 题目 | 链接 | 涉及知识点 |
|------|------|------|-----------|
| 50 | Pow(x, n) | https://leetcode.cn/problems/powx-n/ | 幂运算、数学推导 |
| 69 | x 的平方根 | https://leetcode.cn/problems/sqrtx/ | 数学公式、迭代方法 |
