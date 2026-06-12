## ==========================================================================
STL 容器速通 — string (字符串)
## ==========================================================================

string 是专为字符序列设计的容器，支持类似 vector<char> 的操作，并附加了丰富的字符串专用函数。

## --------------------------------------------------------------------------
## 一、适用场景
## --------------------------------------------------------------------------

| 场景 | 说明 |
|------|------|
| 输入大整数字符串 | 高精度运算的载体 |
| 字符串匹配与查找 | 用 `find()` 快速定位子串 |
| 拼接与裁剪 | `+`, `substr()` 方便操作 |
| 读入整行文本 | `getline()` 读带空格的字符串 |
| 字典序比较 | 直接使用 `<`, `>` 等比较运算符 |

## --------------------------------------------------------------------------
## 二、声明与初始化
## --------------------------------------------------------------------------

```cpp
#include <string>
using namespace std;

string s1;                         // 空字符串
string s2 = "hello";               // C 字符串初始化
string s3("world");                // 构造函数
string s4(5, 'a');                 // "aaaaa"
string s5(s2);                     // 拷贝
string s6 = s2 + " " + s3;        // 拼接 => "hello world"
string s7 = to_string(42);        // 数字转字符串 (C++11)
```

## --------------------------------------------------------------------------
## 三、成员函数总览
## --------------------------------------------------------------------------

### 容量

| 函数 | 说明 |
|------|------|
| `s.size()` / `s.length()` | 返回字符数 O(1) |
| `s.empty()` | 是否为空 |
| `s.resize(n)` | 调整为 n 长度 |
| `s.clear()` | 清空 |
| `s.shrink_to_fit()` | 释放多余内存 |

### 元素访问

| 函数 | 说明 |
|------|------|
| `s[i]` | 下标访问（不检查越界） |
| `s.at(i)` | 安全下标访问 |
| `s.front()` / `s.back()` | 首/尾字符 |
| `s.c_str()` | 返回 C 风格 `const char*` |
| `s.data()` | C++17 返回可修改的 `char*` |

### 修改

| 函数 | 说明 |
|------|------|
| `s += str` / `s2 = s + t` | 拼接字符串 |
| `s.push_back(c)` | 尾部添加字符 |
| `s.pop_back()` | 删除尾部字符 |
| `s.insert(pos, str)` | 在 pos 处插入字符串 |
| `s.erase(pos, n)` | 从 pos 删除 n 个字符 |
| `s.replace(pos, n, str)` | 替换子串 |

### 查找

| 函数 | 说明 |
|------|------|
| `s.find(str, pos=0)` | 从 pos 开始查找 str，返回下标或 `npos` |
| `s.rfind(str)` | 从后向前查找 |
| `s.find_first_of(str)` | 找 str 中任意字符首次出现 |
| `s.find_last_of(str)` | 找 str 中任意字符最后一次出现 |
| `s.find_first_not_of(str)` | 找第一个不在 str 中的字符 |
| `s.find_last_not_of(str)` | 找最后一个不在 str 中的字符 |
| `s.substr(pos, n)` | 返回从 pos 开始的 n 个字符的子串 |
| `s.compare(str)` | 字典序比较，返回 -1/0/1 |
| `stoi(s)`, `stoll(s)`, `to_string(n)` | 数值转换 (C++11) |

## --------------------------------------------------------------------------
## 四、洛谷实战
## --------------------------------------------------------------------------

### P5015 标题统计

```cpp
#include <iostream>
#include <string>
using namespace std;

int main() {
    string s;
    getline(cin, s);
    int cnt = 0;
    for (char c : s)
        if (c != ' ' && c != '\n') cnt++;
    cout << cnt << endl;
    return 0;
}
```

### P1553 数字反转（升级版）

```cpp
#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

string rev(string s) {
    reverse(s.begin(), s.end());
    while (s.size() > 1 && s[0] == '0') s.erase(0, 1);
    return s;
}

int main() {
    string s;
    cin >> s;
    auto pos = s.find('.');
    if (pos != string::npos) {
        string a = s.substr(0, pos), b = s.substr(pos + 1);
        while (b.size() > 1 && b.back() == '0') b.pop_back();
        cout << rev(a) << "." << rev(b) << endl;
        return 0;
    }
    pos = s.find('/');
    if (pos != string::npos) {
        cout << rev(s.substr(0, pos)) << "/" << rev(s.substr(pos + 1)) << endl;
        return 0;
    }
    if (s.back() == '%') { s.pop_back(); cout << rev(s) << "%" << endl; return 0; }
    cout << rev(s) << endl;
    return 0;
}
```

### P1765 手机

```cpp
#include <iostream>
#include <string>
using namespace std;

int main() {
    string keys[] = {"abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"};
    string s;
    getline(cin, s);
    int ans = 0;
    for (char c : s) {
        if (c == ' ') { ans++; continue; }
        for (int i = 0; i < 8; i++) {
            int pos = keys[i].find(c);
            if (pos != string::npos) { ans += pos + 1; break; }
        }
    }
    cout << ans << endl;
    return 0;
}
```

## ==========================================================================
### 📝 章节测试
## ==========================================================================

> [!question] 判断题 1
> `s.size()` 和 `s.length()` 返回的值完全相同。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: `size()` 和 `length()` 功能完全一样，都返回字符串中字符的个数。

> [!question] 判断题 2
> `string::npos` 的值是 -1。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: `npos` 是 `size_t` 类型的最大值，即 `(size_t)(-1)`，通常等于 -1 的无符号表示。

> [!question] 判断题 3
> `s.find("abc")` 如果找不到子串会返回 0。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: 找不到时返回 `string::npos`，不是 0。0 表示在下标 0 处找到了。

> [!question] 判断题 4
> string 可以用 `+` 运算符直接拼接两个字符串。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: string 重载了 `+` 运算符，支持字符串拼接。

> [!question] 判断题 5
> `s.c_str()` 返回的指针指向的字符串以 '\0' 结尾。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: `c_str()` 返回一个以 null 结尾的 C 风格字符串指针。

> [!question] 判断题 6
> `string s = "hello"; s[10] = 'x';` 会抛出异常。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: `s[10]` 不做越界检查，是未定义行为但不会抛异常。`s.at(10)` 才会抛出 `out_of_range` 异常。

> [!question] 判断题 7
> `getline(cin, s)` 可以读入含空格的整行字符串。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: `getline` 读取直到换行符（不包含换行符），可以读入空格。

> [!question] 判断题 8
> string 的 `substr()` 会修改原字符串。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: `substr()` 返回一个新的子字符串，不修改原字符串。

> [!question] 判断题 9
> 两个 string 可以直接用 `<` 进行字典序比较。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: string 重载了比较运算符，可以直接进行字典序比较。

> [!question] 判断题 10
> `to_string(42)` 返回字符串 `"42"`。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: `to_string()` 将数值转换为对应的字符串表示。

> [!question] 选择题 1
> `string s = "hello"; s.substr(1, 3)` 的结果是？
> - [ ] A. "hel"
> - [ ] B. "ell"
> - [ ] C. "ello"
> - [ ] D. "lo"
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: `substr(pos, len)` 从下标 pos=1 开始取 len=3 个字符，即 "ell"。

> [!question] 选择题 2
> 以下哪个函数可以将 string 转换为整数？
> - [ ] A. `atoi(s)`
> - [ ] B. `stoi(s)`
> - [ ] C. `int(s)`
> - [ ] D. `(int)s`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: `stoi(s)` 将 string 转换为 int。`atoi` 需要 C 风格字符串参数 `atoi(s.c_str())`。

> [!question] 选择题 3
> `string s(5, 'a')` 的结果是？
> - [ ] A. "5a"
> - [ ] B. "a5"
> - [ ] C. "aaaaa"
> - [ ] D. "a"
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > 
> > **解析**: `string(n, c)` 构造 n 个字符 c 组成的字符串，即 "aaaaa"。

> [!question] 选择题 4
> string 的 `find()` 函数的时间复杂度是？
> - [ ] A. O(1)
> - [ ] B. O(n)
> - [ ] C. O(n*m)（n 为字符串长度，m 为模式串长度）
> - [ ] D. O(log n)
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > 
> > **解析**: 标准库的 `find()` 通常使用朴素匹配算法，最坏情况 O(n*m)。

> [!question] 选择题 5
> 以下哪个操作不会修改原字符串？
> - [ ] A. `s.erase(0, 1)`
> - [ ] B. `s.replace(0, 1, "X")`
> - [ ] C. `s.substr(0, 3)`
> - [ ] D. `s.insert(0, "Y")`
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > 
> > **解析**: `substr` 返回新字符串，不修改原串。其余都会修改原字符串。

> [!question] 选择题 6
> `string s = "abcabc"; s.find_first_of("cb")` 的返回值是？
> - [ ] A. 0
> - [ ] B. 1
> - [ ] C. 2
> - [ ] D. 3
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: `find_first_of` 查找参数字符串中任意字符首次出现的位置。'b' 在下标 1，'c' 在下标 2，所以返回 1。

> [!question] 选择题 7
> 以下哪种方式不能正确比较两个字符串是否相等？
> - [ ] A. `s1 == s2`
> - [ ] B. `s1.compare(s2) == 0`
> - [ ] C. `strcmp(s1, s2) == 0`
> - [ ] D. `s1 != s2` 取反
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > 
> > **解析**: `strcmp` 接受 `const char*` 参数，不能直接传 string 对象。需要用 `strcmp(s1.c_str(), s2.c_str())`。

> [!question] 选择题 8
> `string s = ""; s.push_back('A'); s += "BC";` 之后 s 的内容是？
> - [ ] A. "A BC"
> - [ ] B. "ABC"
> - [ ] C. "A"
> - [ ] D. "BC"
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: push_back 添加字符 'A'，+= 拼接 "BC"，结果为 "ABC"。

> [!question] 选择题 9
> 以下代码输出什么？
> ```cpp
> string s = "hello";
> s.erase(1, 2);
> cout << s;
> ```
> - [ ] A. "hlo"
> - [ ] B. "heo"
> - [ ] C. "llo"
> - [ ] D. "ho"
>
> > [!success]- 点击查看答案
> > 正确答案: A
> > 
> > **解析**: `erase(pos, n)` 从下标 1 开始删除 2 个字符（"el"），剩下 "hlo"。

> [!question] 选择题 10
> `rfind` 和 `find` 的区别是？
> - [ ] A. rfind 查找速度更快
> - [ ] B. rfind 从字符串末尾向前查找
> - [ ] C. rfind 只能查找单个字符
> - [ ] D. rfind 返回最后一个不匹配的位置
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: `rfind` (reverse find) 从字符串末尾向前查找子串或字符，返回最后一次出现的位置。

### 动手练习题

> [!question] 练习题 1
> **题目**: 输入一个字符串，统计其中大写字母、小写字母、数字和其他字符的个数，分别输出。
> 
> **输入示例**:
> ```
> Hello World! 123
> ```
> **输出示例**:
> ```
> 大写: 2
> 小写: 8
> 数字: 3
> 其他: 3
> ```

> [!question] 练习题 2
> **题目**: 输入一个字符串和一个子串，将字符串中所有出现的该子串替换为另一个指定字符串。使用 `find` 和 `replace` 实现。
> 
> **输入示例**:
> ```
> hello world hello
> hello
> hi
> ```
> **输出示例**:
> ```
> hi world hi
> ```

> [!question] 练习题 3
> **题目**: 输入一个由空格分隔的英文句子，将每个单词反转后输出（单词间顺序不变）。使用 string 的 `find`、`substr` 和 `reverse` 实现。
> 
> **输入示例**:
> ```
> hello world cpp
> ```
> **输出示例**:
> ```
> olleh dlrow ppc
> ```

## --------------------------------------------------------------------------
## 🔗 知识网络
## --------------------------------------------------------------------------

- **上一容器**: [[容器类/02_vector]] | **下一容器**: [[容器类/04_stack]] | **返回**: [[目录]]
- **相关**: [[算法技巧/字符串]] | [[10_文件与流]]
