# 类与继承：从 struct 到 class (OOP: From C struct to Python class)
---

## 章节概述

C 语言中没有类——只有 `struct` 和函数指针。想用 C 实现"对象"？你需要用 `struct` 装数据 + 函数指针表模拟虚函数 + 手动传递 `this` 指针。C++ 用 `class` 封装了这一切，Python 则进一步简化到极致。本章展示 Python 类的最小语法（`__init__`、`self`、`__str__`），对比三种语言实现同一功能所需的代码量，让你掌握"用 Python 写工具类"而不是"设计大型继承体系"的技能。

> **核心理念**：Python 的类和 C 的 `struct` 是本质相同的——它们都是"把数据和操作数据的方法打包在一起"。区别在于 Python 帮你管理了虚函数表（vtable）、自动传递 `this`（`self`），以及提供了魔法方法（magic methods）让自定义对象与 Python 语法无缝融合。当你只需要一个"带方法的结构体"时，Python 类就是答案。

---

### 第一节：从 struct 到 class 的演化
---

1.1 同一个功能，三种实现
-------------------------

功能描述：一个表示二维点的数据结构，能计算到原点的距离。

**C 语言版本**：

```c
#include <stdio.h>
#include <math.h>

// 数据：struct
struct Point {
 double x;
 double y;
};

// 操作：全局函数，手动传递对象指针
double point_distance(struct Point *self) {
 return sqrt(self->x * self->x + self->y * self->y);
}

void point_print(struct Point *self) {
 printf("Point(x=%.2f, y=%.2f)\n", self->x, self->y);
}

// 使用
int main() {
 struct Point p = {3.0, 4.0};
 point_print(&p); // 手动传递 &p
 printf("distance = %.2f\n", point_distance(&p));
 return 0;
}
```

**C++ 版本**：

```cpp
#include <iostream>
#include <cmath>

class Point {
public:
 double x, y;

 Point(double x, double y) : x(x), y(y) {} // 构造函数

 double distance() const { // this 自动传递
 return std::sqrt(x*x + y*y);
 }

 void print() const {
 std::cout << "Point(x=" << x << ", y=" << y << ")" << std::endl;
 }
};

// 使用
int main() {
 Point p(3.0, 4.0);
 p.print(); // 方法调用 + 隐式 this
 std::cout << "distance = " << p.distance() << std::endl;
}
```

**Python 版本**：

```bash
python -c "
import math

class Point:
 def __init__(self, x, y): # 构造函数
 self.x = x # self 必须显式写出
 self.y = y

 def distance(self): # 方法，self 是惯例名
 return math.sqrt(self.x**2 + self.y**2)

 def __str__(self): # 魔法方法：给 print() 用
 return f'Point(x={self.x:.2f}, y={self.y:.2f})'

# 使用
p = Point(3.0, 4.0)
print(p)
print(f'distance = {p.distance():.2f}')
"
```

1.2 self 的三重身份
-------------------

```bash
python -c "
class Demo:
 def method(self, arg):
 print(f'self = {self}')
 print(f'arg = {arg}')

d = Demo()

# 以下两种调用完全等价：
d.method('hello') # 语法糖：对象自动传入为 self
Demo.method(d, 'hello') # 显式写法：手动传入 self
"
```

`self` 相当于：
- C 语言中手动传递的 `struct Point *self` 指针
- C++ 中隐式传递的 `this` 指针
- Python 中需要**显式写出参数列表中**（但调用时自动填充）

> **为什么 Python 的 `self` 必须显式写？** Guido 的设计哲学是"显式优于隐式"（Explicit is better than implicit）。你可以把 `self` 换成任何名字（如 `this`、`me`），但强烈建议遵守 `self` 的社区惯例。

### 小节练习


> [!question] 判断题 1
> Python 类的 `__init__` 方法相当于 C 语言的 `malloc` + 初始化。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: Python 在执行 `ClassName(...)` 时先调用 `__new__` 分配对象（对应 `malloc`），再调用 `__init__` 初始化属性（对应结构体字段赋值）。大多数情况下你只需要实现 `__init__`，Python 自动处理内存分配。

---

### 第二节：属性、方法与命名约定
---

2.1 实例属性 vs 类属性
-----------------------

```bash
python -c "
class Counter:
 total = 0 # 类属性：所有实例共享

 def __init__(self, name):
 self.name = name # 实例属性：每个实例独立
 self.count = 0
 Counter.total += 1 # 修改类属性

 def increment(self):
 self.count += 1

c1 = Counter('A')
c2 = Counter('B')

print('c1.total:', c1.total) # 2（通过实例访问类属性）
print('c2.total:', c2.total) # 2
print('Counter.total:', Counter.total) # 2（通过类访问）

# 陷阱：通过实例赋值会创建实例属性，不会修改类属性
c1.total = 100
print('c1.total:', c1.total) # 100（实例属性遮盖了类属性）
print('Counter.total:', Counter.total) # 2（类属性未变）
"
```

这个陷阱类似于 C 语言中在结构体内部意外定义了一个同名字段，遮盖了原来的值。

```c
// C 语言类似场景
struct Counter {
 int total; // 实例独立
};
static int total = 0; // 全局的"类变量"
// 如果某个实例手动修改了 total 字段，不会影响全局变量
```

2.2 属性和方法的访问控制
-------------------------

```bash
python -c "
class BankAccount:
 def __init__(self, owner, balance):
 self.owner = owner # 公开属性
 self._balance = balance # 约定：受保护的（_ 前缀）
 self.__id = hash(owner) # 名称改写：私有的（__ 前缀）

 def deposit(self, amount):
 if amount > 0:
 self._balance += amount

 def get_balance(self):
 return self._balance

acc = BankAccount('Alice', 1000)
print('owner:', acc.owner)

# Python 没有真正的私有属性
# _balance 是可以访问的（约定：请勿直接访问）
print('_balance:', acc._balance) # 可以，但不应该

# __id 被名称改写为 _BankAccount__id
# print(acc.__id) # AttributeError
print('mangled:', acc._BankAccount__id) # 可以访问，但极不推荐
"
```

> Python 的 `_前缀` 和 `__前缀` 都是**约定和名称改写**，不是编译时或运行时的强制访问控制。与 C++ 的 `public`/`protected`/`private` 不同，Python 社区依赖"我们都是成年人"的哲学。

### 小节练习


> [!question] 判断题 1
> Python 的 `__varname` 命名是真正的私有属性——外部代码完全无法访问。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `__varname` 触发 Python 的**名称改写**（name mangling）——解释器将 `__varname` 改为 `_ClassName__varname`。这是一种防止子类属性冲突的机制，不是安全措施。外部代码仍可通过 `obj._ClassName__varname` 访问。

---

### 第三节：魔术方法 —— 让对象像内置类型
---

3.1 最常用的魔术方法
--------------------

```bash
python -c "
class Vector:
 def __init__(self, x, y):
 self.x = x
 self.y = y

 def __repr__(self): # 给开发者看的字符串（\"官方的\"）
 return f'Vector({self.x}, {self.y})'

 def __str__(self): # 给用户看的字符串（友好的）
 return f'({self.x}, {self.y})'

 def __len__(self): # 支持 len()
 return 2

 def __eq__(self, other): # 支持 ==
 if not isinstance(other, Vector):
 return NotImplemented
 return self.x == other.x and self.y == other.y

 def __add__(self, other): # 支持 +
 return Vector(self.x + other.x, self.y + other.y)

 def __abs__(self): # 支持 abs()
 return (self.x**2 + self.y**2) ** 0.5

 def __getitem__(self, i): # 支持 obj[0]
 return [self.x, self.y][i]

v1 = Vector(3, 4)
v2 = Vector(3, 4)
v3 = Vector(1, 2)

print('repr:', repr(v1)) # Vector(3, 4)
print('str:', str(v1)) # (3, 4)
print('len:', len(v1)) # 2
print('==:', v1 == v2) # True
print('!=:', v1 != v3) # True（自动从 __eq__ 推导）
print('+:', v1 + v3) # (4, 6)
print('abs:', abs(v1)) # 5.0
print('v[0]:', v1[0]) # 3
"
```

3.2 魔术方法对照表
------------------

| 魔术方法 | 触发语法 | C/C++ 等价概念 |
|----------|----------|---------------|
| `__init__` | `obj = Class()` | 构造函数 |
| `__str__` | `print(obj)`, `str(obj)` | `toString()` / 格式化输出 |
| `__repr__` | `repr(obj)`, 交互环境 | 调试器显示 |
| `__len__` | `len(obj)` | `.size()` / `.length()` |
| `__eq__` | `obj1 == obj2` | `operator==` |
| `__lt__` | `obj1 < obj2` | `operator<` |
| `__add__` | `obj1 + obj2` | `operator+` |
| `__getitem__` | `obj[key]` | `operator[]` |
| `__iter__` | `for x in obj:` | 迭代器接口 |
| `__enter__/__exit__` | `with obj:` | RAII / 析构函数 |
| `__call__` | `obj()` | `operator()` (函数对象) |
| `__bool__` | `if obj:` | `operator bool` |

3.3 `@property` —— 让方法变成属性
---------------------------------

```bash
python -c "
class Thermometer:
 def __init__(self, celsius):
 self._celsius = celsius

 @property
 def fahrenheit(self): # 读取：像属性一样访问
 return self._celsius * 9/5 + 32

 @fahrenheit.setter
 def fahrenheit(self, value): # 写入：赋值时自动转换
 self._celsius = (value - 32) * 5/9

 @property
 def celsius(self):
 return self._celsius

t = Thermometer(100)
print(f'{t.celsius}°C = {t.fahrenheit}°F')

t.fahrenheit = 32 # 通过 setter 设置华氏度
print(f'After set: {t.celsius}°C') # 自动转换回摄氏度
"
```

> `@property` 很像 C# 的 `get`/`set` 访问器（accessor）。与 C++ 中常见的 `getTemperature()` / `setTemperature()` 方法对比，`@property` 让温度转换看起来像在直接读写字段——但背后运行自定义逻辑。

### 小节练习


> [!question] 判断题 1
> 如果定义了 `__eq__`，Python 会自动推导出 `__ne__`（不等于）的行为。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: Python 3 中，如果定义了 `__eq__` 但未定义 `__ne__`，`__ne__` 会自动返回 `not self.__eq__(other)`。同样，`__lt__` 和 `__le__`、`__gt__` 和 `__ge__` 也有一定的自动推导关系（通过 `functools.total_ordering` 装饰器补全）。

---

### 第四节：继承与 MRO（方法解析顺序）
---

4.1 基本继承
-------------

```bash
python -c "
class Animal:
 def __init__(self, name):
 self.name = name

 def speak(self):
 return f'{self.name} makes a sound.'

class Dog(Animal): # Dog 继承 Animal
 def speak(self): # 方法重写（override）
 return f'{self.name} barks!'

class Cat(Animal):
 def speak(self):
 return f'{self.name} meows!'

animals = [Dog('Rex'), Cat('Whiskers'), Animal('Thing')]
for a in animals:
 print(f'{type(a).__name__}: {a.speak()}')
"
```

对比 C++ 的虚函数：

```cpp
// C++ 虚函数需要显式声明 virtual
class Animal {
public:
 virtual string speak() { return name + " makes a sound."; }
};

// Dog 继承并 override
class Dog : public Animal {
public:
 string speak() override { return name + " barks!"; }
};
```

Python **所有方法默认都是"虚函数"**——子类可以重写任何方法，通过子类实例调用时会自动分发到子类的版本。

4.2 `super()` —— 调用父类方法
------------------------------

```bash
python -c "
class Logger:
 def __init__(self, prefix):
 self.prefix = prefix

 def log(self, msg):
 print(f'[{self.prefix}] {msg}')

class TimestampLogger(Logger):
 def __init__(self, prefix):
 super().__init__(prefix) # 调用父类的 __init__

 def log(self, msg):
 import datetime
 ts = datetime.datetime.now().isoformat()
 super().log(f'{ts} - {msg}') # 调用父类的 log

tl = TimestampLogger('INFO')
tl.log('Server started')
"
```

`super()` 不需要显式写出当前类名——它自动获取当前类和实例信息。这比 C++ 的 `BaseClass::method()` 更简洁。

4.3 多重继承与 MRO
-------------------

```bash
python -c "
class A:
 def method(self):
 return 'A.method'

class B(A):
 def method(self):
 return 'B.method → ' + super().method()

class C(A):
 def method(self):
 return 'C.method → ' + super().method()

class D(B, C): # 多重继承
 def method(self):
 return 'D.method → ' + super().method()

d = D()
print(d.method())

# 查看方法解析顺序
print('MRO:', [cls.__name__ for cls in D.__mro__])
"
```

输出：
```
D.method → B.method → C.method → A.method
MRO: ['D', 'B', 'C', 'A', 'object']
```

> Python 使用 **C3 线性化算法**（C3 Linearization）确定方法解析顺序（MRO）。多重继承在 Python 中是合法的（不同于 C++ 的菱形继承问题），但建议谨慎使用。C 语言中没有继承概念，[[../cpp教程/cpp目录|C++教程]] 中有更多关于多继承的讨论。

4.4 Mixin —— 轻量级多继承模式
-------------------------------

```bash
python -c "
import json

class JsonSerializableMixin:
 '''提供 JSON 序列化能力的混入类'''
 def to_json(self):
 # 收集所有非私有、非方法的实例属性
 data = {k: v for k, v in self.__dict__.items()
 if not k.startswith('_') and not callable(v)}
 return json.dumps(data, indent=2)

class Config(JsonSerializableMixin):
 def __init__(self, host, port, debug):
 self.host = host
 self.port = port
 self.debug = debug

c = Config('localhost', 8080, True)
print(c.to_json())
"
```

> Mixin 是 Python 社区推荐的"小粒度代码复用"模式——与 C++ 的完整多重继承不同，Mixin 类通常只提供一小组相关功能，不存储自己的状态。

### 小节练习


> [!question] 判断题 1
> Python 中所有方法默认是"虚函数"——子类重写后，通过基类引用调用也会执行子类版本。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: Python 没有 `virtual` 关键字——所有实例方法都通过对象的 `__dict__` 或类层次的属性查找进行动态分发。这相当于 C++ 中所有方法默认都是 `virtual`。

---

## 章节测试

### 一、判断题（正确选，错误选）

> [!question] 判断题 1
> Python 类的 `__init__` 方法是构造函数——它在对象创建时被自动调用。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `__init__` 在 `ClassName(...)` 调用时自动执行。它在 `__new__`（分配对象）之后被调用，用于初始化实例属性。通常称 `__init__` 为"初始化方法"或"构造函数"。

> [!question] 判断题 2
> `self` 是 Python 的保留关键字，方法的第一参数必须命名为 `self`。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `self` 不是关键字——它只是 Python 社区的**强约定**。你可以用任何名称：`this`、`me`、`s` 都合法。但偏离这一惯例会让代码难以阅读。

> [!question] 判断题 3
> `__str__` 和 `__repr__` 实现其中之一即可，Python 会自动推导出另一个。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 如果只定义了 `__repr__` 而未定义 `__str__`，`__str__` 会回退使用 `__repr__`。但反过来（只定义 `__str__`）不会推导 `__repr__`——没有 `__repr__` 时 REPL 显示的是默认的 `<ClassName object at 0x...>`。

> [!question] 判断题 4
> Python 支持类方法（`@classmethod`）和静态方法（`@staticmethod`）。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `@classmethod` 的第一个参数是类本身（惯例名 `cls`），`@staticmethod` 没有自动传入参数。`@classmethod` 常用于替代构造函数（工厂方法），`@staticmethod` 用于逻辑上属于类但不需要访问类/实例的方法。

> [!question] 判断题 5
> Python 的 `@property` 装饰器将一个方法转换为可以像属性一样访问的只读属性。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `@property` 将方法变为 getter。配合 `@name.setter` 可以添加写能力——让属性赋值自动触发自定义逻辑。这在概念上类似 C# 的 property 访问器。

> [!question] 判断题 6
> 在 C 语言中通过 `struct` 和函数指针模拟对象，每次方法调用必须手动传递对象指针。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: C 语言没有 `this` 或 `self` 概念——"方法"只是普通函数，需要程序员手动将 `struct*` 作为第一个参数传递。Python 的 `self` 在语法层面就是这种手动传递的"语法糖"版本。

> [!question] 判断题 7
> Python 类继承中的 MRO（Method Resolution Order）遵循 C3 线性化算法，保证多继承时方法的查找顺序是确定的。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: Python 从 2.3 开始使用 C3 线性化算法计算 MRO。该算法保证：子类在父类之前检查、保持基类声明顺序、所有父类只被检查一次。可通过 `ClassName.__mro__` 查看。

---


---

## 力扣练习

以下题目用于验证本章所学内容：

| 题号 | 题目 | 链接 | 涉及知识点 |
|------|------|------|-----------|
| 146 | LRU 缓存 | https://leetcode.cn/problems/lru-cache/ | 类设计、双向链表+哈希表 |
| 232 | 用栈实现队列 | https://leetcode.cn/problems/implement-queue-using-stacks/ | 类封装、双栈 |
| 225 | 用队列实现栈 | https://leetcode.cn/problems/implement-stack-using-queues/ | 类封装、数据结构 |



### 动手练习题

> [!example] 练习题 1：用 Python 类重新实现 C 链表
> **难度**: 简单
>
> C 语言的链表通常这样定义：
> ```c
> struct Node {
> int data;
> struct Node *next;
> };
> ```
>
> 用 Python 类实现一个功能更丰富的链表：
> 1. `LinkedList` 类支持 `append`、`prepend`、`insert_after`、`delete`
> 2. 实现 `__len__` 支持 `len(list_obj)`
> 3. 实现 `__iter__` 支持 `for item in list_obj`
> 4. 实现 `__getitem__` 支持 `list_obj[i]`
> 5. 实现 `__str__` 以可读的方式打印链表
>
> 不需要考虑 Python 内置 `list` 的所有特性——重点是理解从 C `struct` 到 Python `class` 的思维转换。

> [!example] 练习题 2：实现一个配置管理器
> **难度**: 简单
>
> 设计一个 `Config` 类，从 JSON 文件加载配置：
> - 用 `@classmethod` 实现 `Config.from_json(path)` 工厂方法
> - 用 `@property` 将配置项当作属性访问（如 `config.host` 而非 `config['host']`）
> - 用 `__getattr__` 在访问不存在的配置项时返回 `None`（而非 `AttributeError`）
> - 用 `__setattr__` 确保配置项的值不会被意外修改为错误的类型
>
> 在配置项值被访问时记录访问日志（使用 `__getattribute__`）。

> [!example] 练习题 3：从 C struct 到 Python dataclass
> **难度**: 简单
>
> 给定 C 结构体定义：
> ```c
> struct Student {
> int id;
> char name[64];
> float gpa;
> int year;
> };
> ```
>
> 分别用以下三种方式实现 Python 等价物：
> 1. 普通类（手动写 `__init__`、`__repr__`、`__eq__`）
> 2. `dataclasses.dataclass` 装饰器
> 3. `typing.NamedTuple`
>
> 统计每种方式的代码行数。用 `python -m timeit` 比较三种方式的实例化性能。

> [!example] 练习题 4：模拟 C 语言的函数指针表
> **难度**: 简单
>
> C 语言中常用函数指针表实现多态：
> ```c
> struct Operations {
> int (*add)(int, int);
> int (*sub)(int, int);
> };
> ```
>
> 用 Python 实现一个可以动态更换"运算策略"的 `Calculator` 类：
> 1. 定义 `AddStrategy`、`MultiplyStrategy` 等策略类
> 2. `Calculator` 接受一个策略实例，将运算委托给它
> 3. 支持运行时替换策略（`calc.strategy = NewStrategy()`）
> 4. 用 `__call__` 让 `Calculator` 实例本身也可调用
>
> 对比 Python 的策略模式和 C 语言的函数指针表——Python 的"一切皆对象"让策略传递变得简单直接。
