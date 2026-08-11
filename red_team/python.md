
# Python 编程练习 — 力扣题目精选

> 本文是 [[补充-Python黑客脚本基础]] 的配套练习指南，精选力扣 (LeetCode) 在线评测平台的编程题目，按难度和安全性相关性分组，帮助红队学习者在实战编码中提升 Python 能力。


## 如何使用力扣 (LeetCode)

1. **注册账号**：访问 [https://leetcode.cn](https://leetcode.cn) 注册。
2. **选择语言**：提交代码时选择 **Python 3** 作为编程语言。
3. **阅读题面**：每道题有详细的题目描述、输入输出格式和样例。
4. **提交代码**：编写 `input()` 读取标准输入、`print()` 输出的标准程序。不要添加多余提示文字。
5. **查看题解**：做完后可以参考其他人的题解，学习更优的写法。

> **提示**：在力扣上，标准 Python 输入模板通常为：
> ```python
> import sys
> data = sys.stdin.read().split()
> ```
> 这样可以一次性读取所有输入并按空白符分割，比逐行 `input()` 更高效。


### 第 2 级 — 基础控制流：条件判断与循环

| 编号        | 题目    | 简述             | 安全相关性                         |
| --------- | ----- | -------------- | ----------------------------- |
| 力扣简单条件判断题 | 数的性质  | 复杂条件判断（and/or） | 布尔逻辑是防火墙规则、访问控制的底层            |
| 力扣循环条件题   | 小鱼的航程 | 循环 + 条件分支      | 自动化脚本中遍历 + 筛选的典型模式            |
| 力扣分类统计题   | 分类平均  | 遍历数组分类统计       | 流量分类、日志分类的编程基础                |
| 力扣循环递减题   | 一尺之棰  | while 循环模拟递减   | `while` 是爆破循环的骨架（如目录遍历直到找到目标） |
| 力扣质数题     | 质数口袋  | 质数判断           | 密码学基础——RSA 算法依赖质数             |
| 力扣数组操作题   | 打分    | 数组去高低分取平均      | 数据处理中去除异常值（outlier）的通用模式      |

> **学习目标**：掌握 `if/elif/else`、`for` 循环、`while` 循环、`list` 基本操作。


### 第 4 级 — 数据结构：栈、队列、链表

> **重点**：解析嵌套协议、匹配括号、BFS/DFS 搜索都需要这些数据结构。

| 编号 | 题目 | 简述 | 安全相关性 |
|------|------|------|------------|
| 力扣约瑟夫环 | 约瑟夫问题 | 队列循环出队 | 类似循环调度器、任务队列管理 |
| 力扣逆波兰表达式 | 后缀表达式 | 栈计算后缀表达式 | shellcode 解释器、自定义 DSL 解析的基础 |
| 力扣有效括号 | 表达式括号匹配 | 栈验证括号配对 | SQL 注入 payload 中括号平衡、输入校验 |
| 力扣链表 | 队列安排 | 双向链表插入/删除 | 内核漏洞利用中链表破坏的原理理解 |

> **学习目标**：用 Python `list` 模拟栈（`append/pop`）和队列（`append/pop(0)` 或 `collections.deque`）。


### 第 6 级 — 进阶算法：直接与安全相关

| 编号 | 题目 | 简述 | 安全相关性 |
|------|------|------|------------|
| 力扣哈希表 | 字符串哈希 | 实现字符串哈希判重 | 哈希函数原理——密码 hash 破解的底层理解 |
| 力扣并查集 | 亲戚 | 并查集判断关系 | 网络拓扑分析、域信任关系建模 |
| 力扣最小生成树 | 修复公路 | 最小生成树 Kruskal | 网络路径优化、最小代价攻击路径 |
| 力扣并查集 | 并查集模板 | 并查集路径压缩优化 | 集群连通性分析、内网横向移动路径规划 |

> **学习目标**：理解并实现基础算法。这些算法本身对应安全场景的实际需求。


### 挑战 2：URL 解码器

**要求**：实现 URL 百分号编解码。`%20` → 空格，`%3C` → `<`，支持中文的 UTF-8 编码 URL 解码。

```python
def url_decode(s: str) -> str:
    # 把 %XX 和 %XX%XX%XX（UTF-8多字节）还原为原始字符串
    pass

def url_encode(s: str) -> str:
    # 把非字母数字字符替换为 %XX 形式
    pass

# 测试
assert url_decode("hello%20world") == "hello world"
assert url_decode("%E4%BD%A0%E5%A5%BD") == "你好"
```

**知识点**：十六进制解析、UTF-8 编码理解——Web 安全、注入攻击中操作 payload 的必备技能。


### 挑战 4：Hash 类型检测器

**要求**：给定一个哈希字符串，根据长度和字符集判断其可能的类型。

```python
import re

HASH_PATTERNS = {
    "MD5": r"^[a-f0-9]{32}$",
    "SHA1": r"^[a-f0-9]{40}$",
    "SHA256": r"^[a-f0-9]{64}$",
    "SHA512": r"^[a-f0-9]{128}$",
    "NTLM": r"^[A-F0-9]{32}$",
    "MySQL4.1": r"^\*[A-F0-9]{40}$",
    "bcrypt": r"^\$2[aby]\$\d+\$[./A-Za-z0-9]{53}$",
}

def identify_hash(hash_str: str) -> list[str]:
    """返回所有可能匹配的哈希类型列表"""
    pass

# 测试
assert "MD5" in identify_hash("5d41402abc4b2a76b9719d911017c592")
assert "bcrypt" in identify_hash("$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy")
```

**知识点**：正则表达式、哈希识别——破解哈希前的第一步就是确定哈希类型。John the Ripper 和 Hashcat 都有自己的识别逻辑。


### 挑战 6：日志分析器

**要求**：解析常见的 Apache/Nginx 访问日志，提取 IP 地址和状态码，统计访问量最高的前 N 个 IP。

```python
import re
from collections import Counter

LOG_PATTERN = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[.*?\] ".*?" (?P<status>\d+) \S+ ".*?" ".*?"'
)

def analyze_log(filepath: str) -> dict:
    """返回 {ip: 访问次数} 的前 10 名、{状态码: 次数} 的统计"""
    pass
```

**知识点**：正则表达式、文件读取、数据统计——实际上是蓝队日常，但红队在信息收集阶段同样需要分析目标日志。


## 参考链接

- 力扣 (LeetCode)：[https://leetcode.cn](https://leetcode.cn)
- 力扣题单：[https://leetcode.cn/problemset/](https://leetcode.cn/problemset/)
- Python 官方文档：[https://docs.python.org/zh-cn/3/](https://docs.python.org/zh-cn/3/)
- 力扣题库搜索：[https://leetcode.cn/problemset/](https://leetcode.cn/problemset/)
