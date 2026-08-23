# 05 第一个程序与 jshell

环境已就绪，本章正式写代码。我们把最简单的 Hello World 拆开揉碎——它的每一部分都藏着 Java 与 C 的重要差异；然后介绍 jshell 交互式解释器，最后用 LeetCode 第一题完成实战闭环。

---

## 一、Hello World 完整剖析

### 1.1 两个世界的 Hello World 对比

先看 C 版本：

```c
#include <stdio.h>

int main(void) {
    printf("Hello, World!\n");
    return 0;
}
```

再看 Java 版本（新建 `Hello.java`，注意**文件名必须是 Hello.java**）：

```java
public class Hello {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```

第一印象：Java 更啰嗦。但每一处啰嗦都有原因，逐层拆解。

### 1.2 类：与 C 的最大差异之一

```java
public class Hello {
```

- **Java 没有"游离的函数"，一切代码必须住在类里**。C 可以直接在文件顶层定义函数 `int add(int a, int b)`，Java 不行——`main` 必须是某个类的成员
- `class Hello` 声明一个名为 Hello 的类（类是什么，[[06_变量与数据类型|入门篇后续]] 与面向对象章节会系统讲；现在把它理解成"C 结构体的超集 + 函数容器"即可）
- **public class 的类名必须与文件名完全一致**（含大小写）：`Hello` 类必须在 `Hello.java` 里。这是编译器的强制约束，目的是让编译器按类名快速定位源码。C 的文件名与函数名毫无关系，这是习惯迁移的第一道坎
- 一个 .java 文件里可以有多个类，但最多只有一个 public 类，且文件名与它同名

### 1.3 main 方法签名逐词解释

```java
public static void main(String[] args)
```

八个词各有含义：

| 词 | 含义 | 与 C 对照 |
|----|------|----------|
| public | 访问修饰符：任何地方可调用 | C 无此概念，函数默认全局可见 |
| static | 静态方法：属于类本身，不需要创建对象就能调用 | 最接近 C 的普通函数——不依附于结构体实例 |
| void | 无返回值 | 同 C 的 void |
| main | JVM 规定的入口方法名 | 同 C |
| String[] args | 参数：字符串数组，接收命令行参数 | 对应 `char** argv`；但没有对应的 argc，数组自己带 length |

为什么 main 必须 `public static`？因为 JVM 启动时还没有任何对象存在，只能通过"类名直接调用静态方法"的方式进入你的代码。写成 `static void main`（JDK 21 起简化形式）也能跑，但初学请保持完整签名。

对比记忆表：

| C | Java | 说明 |
|---|------|------|
| `int main(void)` | `public static void main(String[] args)` | 入口签名 |
| 返回值 exit code（return 1）| `System.exit(1)` 显式退出 | main 是 void，不能靠返回值传退出码 |
| `char** argv` | `String[] args` | 命令行参数 |
| `argv[0]` 是程序名 | `args[0]` 是第一个参数 | 注意差异！Java 不含程序名 |

### 1.4 输出语句

```java
System.out.println("Hello, World!");
```

拆解这行：

- `System` —— java.lang 包中的一个现成类（对应 C 里你 include 后使用的标准设施）
- `.out` —— System 类的静态字段，类型 PrintStream，代表标准输出（对应 C 的 stdout）
- `.println(...)` —— out 对象的方法，打印内容并换行（println = print line）

与 C printf 对比：

| 特性 | C | Java |
|------|---|------|
| 基本输出 | `printf("hi\n")` | `System.out.println("hi")` 自动换行 |
| 不换行输出 | `printf("hi")` | `System.out.print("hi")` |
| 格式化 | `printf("%d %s", n, s)` | `System.out.printf("%d %s%n", n, s)` 格式串语法几乎相同 |
| 占位符换行 | `\n` | `\n` 或 `%n`（平台相关换行符）|

Java 完整保留了 printf 风格的格式化输出，格式符也基本一致：

```java
int age = 25;
double score = 91.5;
String name = "RootStack";
// %d 整数 %f 浮点 %.2f 两位小数 %s 字符串 %b 布尔 %c 字符
System.out.printf("%s is %d years old, score: %.2f%n", name, age, score);
// RootStack is 25 years old, score: 91.50
```

> 细微差异：Java 的 `%s` 可以接任何对象（自动调 toString），且没有 C 中格式符与参数类型不匹配导致的未定义行为——类型不符会抛异常而非打印乱码。

---

## 二、编译运行的两步流程

### 2.1 传统两步

```bash
javac Hello.java    # 编译:生成 Hello.class(字节码)
java Hello          # 运行:JVM 加载执行,注意不带后缀!
```

流程图（呼应 [[00_Java是什么|第一章]] 的原理）：

```mermaid
flowchart LR
    A["Hello.java<br/>你写的源码"] -->|"javac<br/>编译期查语法/类型"| B["Hello.class<br/>字节码"]
    B -->|"java Hello<br/>启动 JVM"| C["类加载器<br/>加载字节码"]
    C --> D["字节码校验"]
    D --> E["解释器 + JIT<br/>执行 main 方法"]
    E --> F["终端输出<br/>Hello, World!"]
    style B fill:#e8f0fe,stroke:#4285f4
```

常见错误对照表（每个初学者都会全踩一遍）：

| 你敲的命令 | 结果 | 原因 |
|-----------|------|------|
| `java Hello.java Hello` | 报错 | 参数混乱 |
| `java Hello.class` | 找不到或无法加载主类 Hello.class | 把文件名当成了类名 |
| 在别的目录 `java Hello` | 找不到或无法加载主类 Hello | JVM 默认在当前目录找类 |
| 文件名 hello.java（小写）| 编译失败 | 与 public 类名不一致 |
| `javac Hello`（无后缀）| 报错 | javac 接收的是文件路径不是类名 |

记忆口诀：**javac 吃文件名（带 .java），java 吃类名（不带任何后缀）**。

### 2.2 JDK 11+ 单文件直接运行

```bash
# JDK 11 起,单文件源码可以一步到位:
java Hello.java
```

JVM 内部会先在内存中编译再立即运行（不产生 .class 文件）。适用边界：

| 场景 | 用哪种 |
|------|--------|
| 单文件学习/刷题/试验 | `java Hello.java` 省事 |
| 多个互相引用的源文件 | `java Main.java` 也可以（JDK 22+ 支持多文件源启动；低版本仍需 javac）|
| 正式项目 | 构建工具管理，见工程化篇 |

与 C 对比：类似 `gcc -x c - <<EOF` 或 tcc 的脚本化用法，但 Java 这条路是官方内建支持。

---

## 三、jshell：交互式 REPL

### 3.1 它是什么，C 为什么没有

jshell 是 JDK 9 引入的**交互式编程环境**（REPL：Read-Eval-Print Loop）：输入一行代码立刻看到结果，无需建文件、无需编译。

C 世界没有对应物——因为 C 的编译链接模型太重。Python 用户对此很熟悉（python 解释器），Node 有 node REPL。jshell 让 Java 补上了这块体验短板。

### 3.2 启动与基本使用

```bash
$ jshell
|  Welcome to JShell -- Version 21.0.5
|  For an introduction type: /help intro

jshell>
```

试试最基本的表达式求值——**不用 println，表达式结果自动回显**：

```text
jshell> 1 + 2
$1 ==> 3

jshell> "abc".toUpperCase()
$2 ==> "ABC"

jshell> Math.max(10, 7)
$3 ==> 10
```

`$1`、`$2` 是 jshell 自动创建的变量保存了每次求值结果，可以继续用：

```text
jshell> $1 * 100
$4 ==> 300
```

### 3.3 定义变量与方法

```text
jshell> int x = 42
x ==> 42

jshell> String name = "Java"
name ==> "Java"

jshell> int square(int n) {
   ...>     return n * n;
   ...> }
|  created method square(int)

jshell> square(x)
$8 ==> 1764
```

注意两点：

1. 变量声明带类型（`int x`）——Java 是静态语言，REPL 也一样，这与 Python REPL 的本质区别
2. 定义多行方法时提示符变为 `...>`，结尾回车两次结束输入；单行语句末尾分号可省略，但方法体内建议保留

修改变量甚至改类型都可以（前向引用受限）：

```text
jshell> x = 99
x ==> 99

jshell> double y = 3.14
y ==> 3.14
```

### 3.4 自动补全与常用命令

Tab 键补全是 jshell 的灵魂：

```text
jshell> System.out.pr<Tab>      # 补全为 println 系列,连按两次列出所有重载
jshell> "hello".toUp<Tab>       # 补全为 toUpperCase()
jshell> <Tab>                   # 列出当前上下文所有可用符号
```

常用斜杠命令：

| 命令 | 作用 |
|------|------|
| `/vars` | 查看已定义的所有变量 |
| `/methods` | 查看已定义的方法 |
| `/list` | 查看历史输入的片段 |
| `/edit` | 打开图形编辑器修改历史片段 |
| `/exit` | 退出（Ctrl+D 同效）|
| `/help` | 帮助 |
| `/reset` | 清空全部状态 |

### 3.5 jshell 的典型工作流

推荐把 jshell 当作"Java 版草稿纸"：

1. 学到新 API 时进去试一下行为（比如 `"a b c".split(" ")` 返回什么）
2. 刷题前验证思路的小逻辑（下一节实战演示）
3. 排查问题时的最小复现场所

退出后一切消失——需要留存的代码写到 .java 文件里。也可以加载已有文件试验：`jshell MyCode.java`。

---

## 四、命令行参数 args 的使用

完整示例 `Greet.java`：

```java
public class Greet {
    public static void main(String[] args) {
        // args.length 相当于 C 里的 argc,但不含程序名
        if (args.length == 0) {
            System.out.println("用法: java Greet <名字>");
            return;   // main 是 void,直接 return 结束
        }
        for (int i = 0; i < args.length; i++) {
            // 字符串拼接用 + 号,C 需要 snprintf 或 strcat
            System.out.println("[" + i + "] Hello, " + args[i] + "!");
        }
    }
}
```

编译运行：

```bash
javac Greet.java
java Greet Alice Bob
# [0] Hello, Alice!
# [1] Hello, Bob!

java Greet
# 用法: java Greet <名字>
```

关键差异强调：C 的 `argv[0]` 是程序自身路径，`argv[1]` 才是第一个参数；**Java 的 `args[0]` 直接就是第一个参数**，没有程序名占位。迁移时最容易出 off-by-one。

---

## 五、注释的三种形式

```java
/**
 * 文档注释(javadoc):描述类或方法的用途,
 * 会被 javadoc 工具提取生成 HTML API 手册。
 * 这是 Java 生态的重要传统——所有标准库文档都是这么生成的。
 */
public class CommentDemo {

    // 行注释:同 C++

    /*
     * 块注释:同 C
     */

    public static void main(String[] args) {
        int sum = 0;              // 尾注释
        /* int old = 10; 注释掉的旧代码 */
        for (int i = 1; i <= 100; i++) {
            sum += i;
        }
        System.out.println("1..100 sum = " + sum);
    }
}
```

三种形式与 C 完全一致，唯一的新事物是 `/** */` 文档注释。试试用 javadoc 工具生成 HTML：

```bash
javadoc -d doc CommentDemo.java   # 生成 doc/ 目录下的 HTML 文档
```

文档注释的规范标签（后续章节会大量出现）：

| 标签 | 说明 | 示例 |
|------|------|------|
| @param | 参数说明 | `@param n 要平方的数` |
| @return | 返回值说明 | `@return n 的平方` |
| @author | 作者 | `@author RootStack` |
| @throws | 可能抛出的异常 | `@throws IllegalArgumentException ...` |

与 C 对比：C 社区的 doxygen 语法与之同源，概念可以直接迁移。

---

## 六、编码规范初探

从第一个程序开始就养成行业惯例，IDEA 会自动帮你执行大半：

| 对象 | 规范 | 示例 |
|------|------|------|
| 类名/接口名 | 大驼峰 UpperCamelCase | `HelloWorld`、`StringBuilder` |
| 方法名 | 小驼峰 lowerCamelCase | `main`、`toUpperCase` |
| 变量名 | 小驼峰 | `maxCount` |
| 常量 | 全大写 + 下划线 | `MAX_SIZE`、`DEFAULT_TIMEOUT` |
| 包名 | 全小写 | `java.util`、`com.example.app` |
| 缩进 | 4 空格（社区主流）| — |

对照 C 的常见风格差异：

| C 常见写法 | Java 惯例 |
|-----------|----------|
| `int max_count;` 下划线命名变量 | `int maxCount;` |
| 宏常量 `#define MAX_SIZE 100` | `static final int MAX_SIZE = 100;` |
| 头文件声明接口 | 无头文件，类即接口边界 |
| 大括号换行 Allman 风格 | 主流 K&R 风格（左括号不换行），IDEA 默认 |

这些不是语法强制（除了类名与文件名一致），而是生态约定——遵守它们，你读别人的代码和被别人读代码的成本都最低。

---

## 七、LeetCode 实战：两数之和

学完以上内容已经足够写出第一道题了。

[两数之和](https://leetcode.cn/problems/two-sum/)：给定整数数组 nums 和目标值 target，找出和为目标值的两个整数下标。假设恰好有一个答案，同一元素不能用两次。

### 7.1 思路

暴力法：双重循环枚举所有下标组合 `(i, j)`，检查 `nums[i] + nums[j] == target`。

### 7.2 先在 jshell 里验证核心逻辑

刷题好习惯：先用 REPL 验证最小逻辑片段。

```text
jshell> int[] nums = {2, 7, 11, 15}
nums ==> int[4] { 2, 7, 11, 15 }

jshell> int target = 9
target ==> 9

jshell> nums[0] + nums[1]
$3 ==> 9

jshell> nums.length
$4 ==> 4
```

确认数组字面量语法 `{2, 7, 11, 15}`、`.length` 属性都符合预期，开始写正式版。

### 7.3 完整题解（单文件可直接运行）

```java
/**
 * 两数之和 —— 暴力解法(入门第一题)
 *
 * 时间复杂度 O(n^2):双重循环
 * 空间复杂度 O(1):只用常数个额外变量
 *
 * 后续学到 HashMap 时会给出 O(n) 解法,敬请期待。
 */
public class TwoSum {

    /**
     * 在数组中寻找和为 target 的两个数的下标
     * @param nums 整数数组
     * @param target 目标和
     * @return 两个下标组成的数组;题目保证有解
     */
    public static int[] twoSum(int[] nums, int target) {
        // 外层固定一个数
        for (int i = 0; i < nums.length; i++) {
            // 内层从 i+1 开始,避免重复配对和自己配自己
            for (int j = i + 1; j < nums.length; j++) {
                if (nums[i] + nums[j] == target) {
                    // 数组字面量只能在声明时用 {},这里用 new 显式创建
                    return new int[]{i, j};
                }
            }
        }
        // 题目保证有解,理论上不会到这里;
        // 但编译器不知道,必须有返回值兜底
        throw new IllegalArgumentException("no solution");
    }

    public static void main(String[] args) {
        // 测试用例 1:题目示例
        int[] result1 = twoSum(new int[]{2, 7, 11, 15}, 9);
        System.out.println("case1: [" + result1[0] + ", " + result1[1] + "]");
        // case1: [0, 1]

        // 测试用例 2
        int[] result2 = twoSum(new int[]{3, 2, 4}, 6);
        System.out.println("case2: [" + result2[0] + ", " + result2[1] + "]");
        // case2: [1, 2]

        // 测试用例 3:重复元素
        int[] result3 = twoSum(new int[]{3, 3}, 6);
        System.out.println("case3: [" + result3[0] + ", " + result3[1] + "]");
        // case3: [0, 1]
    }
}
```

运行方式二选一：

```bash
javac TwoSum.java && java TwoSum    # 传统两步
java TwoSum.java                    # JDK 11+ 单文件直跑
```

预期输出：

```text
case1: [0, 1]
case2: [1, 2]
case3: [0, 1]
```

### 7.4 本题暴露的 C→Java 迁移要点

| 点位 | C 写法 | Java 写法 | 备注 |
|------|--------|----------|------|
| 数组声明 | `int nums[]` | `int[] nums` | 两种都合法，Java 惯用前者风格 |
| 数组长度 | 手动传入参数或 sizeof | `nums.length` 属性 | 没有 argc/n 的烦恼 |
| 数组初始化 | `{2, 7, 11, 15}` 仅声明时可省长度 | 同样语法，但作为参数传递时须 `new int[]{...}` | 7.3 代码中两处用法对比 |
| 返回数组 | malloc + 指针 + 长度出参 | 直接 `new int[]{i, j}` | GC 免去 free，也不怕悬垂指针 |
| 无解情况 | 返回 -1 或 NULL 约定 | 抛异常 `throw new IllegalArgumentException` | 异常机制深入篇详述 |

### 7.5 提交到 LeetCode

LeetCode 的 Java 模板只给你核心方法（signature 已定），把 `twoSum` 方法体填入即可提交。注意模板中方法是实例方法（没有 static），照抄我们的实现去掉 static 也能过。暴力法在本题的数据规模下可以通过，但最优解是哈希表一次遍历——这正是 [[06_变量与数据类型|后续章节]] 学完集合框架后的回头题。

---

## 八、常见问题排查

| 现象 | 原因 | 解决 |
|------|------|------|
| `类 Hello 是公共的, 应在名为 Hello.java 的文件中声明` | 类名与文件名不一致 | 改文件名或类名 |
| `找不到或无法加载主类` | 目录不对 / 带了 .class 后缀 / classpath 问题 | 回到 .class 所在目录，`java Hello` |
| `错误: 缺少方法主体` | 写了 `void main(String[] args);` 分号结尾 | 方法体要有 `{}` |
| jshell 里中文乱码 | Windows cmd 编码 | `chcp 65001` 或换 Windows Terminal |
| `java Hello.java` 报 UnsupportedClassVersionError 反而更怪 | 混用了不同版本的 java/javac | `which -a java javac` 统一版本 |

---

## 九、本章小结

- 一切代码都在类里：public 类名必须等于文件名，这是与 C 的结构性差异
- main 签名 `public static void main(String[] args)` 八个词各有含义；`args[0]` 是第一个参数（不含程序名）
- 流程：javac 吃文件名，java 吃类名；JDK 11+ 可 `java Hello.java` 直跑
- 输出三件套：print / println / printf（格式串与 C 几乎兼容）
- jshell 是 Java 的草稿纸：表达式自动回显、Tab 补全、`/vars` `/methods` 管理
- 注释三种形式，`/** */` 配合 javadoc 生成 HTML 文档
- 命名规范：类大驼峰、方法变量小驼峰、常量全大写下划线
- 实战完成两数之和暴力解法，体会了数组 length、new int[]{}、抛异常等迁移要点

## LeetCode 巩固

本章实战已完成 [两数之和](https://leetcode.cn/problems/two-sum/) 的暴力解法。巩固建议：

1. 把题解提交到 LeetCode 通过，感受在线判题流程
2. 进阶尝试：[罗马数字转整数](https://leetcode.cn/problems/roman-to-integer/) ——练习字符串遍历与条件分支（学完 [[06_变量与数据类型|变量与数据类型]] 后更顺手）
3. 保持节奏：每章一道，攒够五十题时你对 Java 语法的肌肉记忆就建立了
