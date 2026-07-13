---
class string
---

## 底层数据结构

连续内存的动态字符数组，类似 `vector<char>` 但针对字符串场景做了大量扩展。通常采用 SSO（Small String Optimization）：短字符串直接存储在对象内部栈空间，避免堆分配；超过阈值才在堆上分配。

## 复杂度

| 操作 | 复杂度 | 说明 |
|------|--------|------|
| operator[] | O(1) | 无边界检查 |
| at(i) | O(1) | 带边界检查，越界抛 out_of_range |
| push_back | 均摊 O(1) | 追加单字符 |
| pop_back | O(1) | 删除尾字符 |
| insert / erase | O(n) | 中间插入/删除 |
| find | O(n*m) 最坏 | 朴素匹配，n 为主串长 m 为子串长 |
| substr | O(count) | 截取子串，返回新 string |
| + 拼接 | O(n+m) | 创建新 string |
| += / append | 均摊 O(m) | 尾部追加，m 为追加长度 |
| size / length | O(1) | 两者完全等价 |
| compare | O(n) | 字典序比较 |

## 关键方法

| 方法 | 说明 |
|------|------|
| s[i] / s.at(i) | 下标访问字符 |
| s.front() / s.back() | 首/尾字符 |
| s.size() / s.length() | 字符个数（等价） |
| s += str / s.append(str) | 尾部追加 |
| s + str | 拼接返回新 string |
| s.find(sub) / s.rfind(sub) | 正向/反向查找子串 |
| s.find_first_of(chars) | 查找 chars 中任意字符首次出现 |
| s.find_last_of(chars) | 查找 chars 中任意字符末次出现 |
| s.substr(pos, count) | 截取从 pos 起 count 个字符 |
| s.insert(pos, str) | 在指定位置插入 |
| s.erase(pos, count) | 删除指定范围 |
| s.replace(pos, count, str) | 替换指定范围 |
| s.compare(other) | 字典序比较，返回负/零/正 |
| s.clear() | 清空字符串 |
| to_string(n) | 数值转 string |
| stoi(s) / stod(s) | string 转数值 |

## 伪代码示例

```
string s = "hello"

// 追加
s += " world"            // "hello world"

// 查找
pos = s.find("world")    // 返回 6
if pos != npos:
    print "found at " + to_string(pos)

// 截取
sub = s.substr(0, 5)     // "hello"

// 遍历并修改
for each c in s:
    c = toupper(c)

// 读入整行
getline(in, s)

// 数值转换
num_str = to_string(3.14)
val = stoi("12345")
```

## 相关链接

- [[../../数据结构/A_容器_Container]]
- [[../../../c语言教程/3数据结构/A_容器_Container]]
- [[./vector]]
