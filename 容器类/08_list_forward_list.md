## ==========================================================================
STL 容器速通 — list & forward_list (链表)
## ==========================================================================

list 是双向链表，forward_list 是单向链表。两者支持 O(1) 的任意位置插入删除，但不支持随机访问。

## --------------------------------------------------------------------------
## 一、适用场景
## --------------------------------------------------------------------------

| 场景 | 说明 |
|------|------|
| 频繁中间插入/删除 | O(1) 插入删除，比 vector 的 O(n) 快得多 |
| LRU 缓存 | 用 list 维护访问顺序，map 做 O(1) 查找 |
| 邻接表 | 不过一般用 vector 即可，链表适用于频繁删边 |
| 需要稳定迭代器 | 插入/删除不会使其他迭代器失效（vector 会） |
| 大对象搬移 | splice 可以 O(1) 地整段移动，不拷贝元素 |

### list vs forward_list

| 特性 | list | forward_list |
|------|------|-------------|
| 方向 | 双向 | 单向 |
| 内存占用 | 每个节点 2 个指针 | 每个节点 1 个指针 |
| push_front/pop_front | 有 | 有 |
| push_back/pop_back | 有 | **无**（只有 `before_begin()`） |
| size() | O(1) | **无** (C++11 后部分编译器有) |

**竞赛建议**: 绝大多数场景用 vector 即可，list 仅用于需要 splice 或保证迭代器不失效的特殊场景。

## --------------------------------------------------------------------------
## 二、声明与初始化
## --------------------------------------------------------------------------

```cpp
#include <list>
#include <forward_list>
using namespace std;

// list (双向链表)
list<int> l1;                        // 空 list
list<int> l2(5, 10);                 // 5 个元素，值全 10
list<int> l3 = {1, 2, 3};            // 列表初始化
list<int> l4(l3);                    // 拷贝构造

// forward_list (单向链表)
forward_list<int> fl1;               // 空
forward_list<int> fl2(5, 10);        // 5 个 10
forward_list<int> fl3 = {1, 2, 3};
forward_list<int> fl4(fl3);
```

## --------------------------------------------------------------------------
## 三、成员函数总览
## --------------------------------------------------------------------------

### list — 容量

| 函数 | 说明 |
|------|------|
| `l.size()` | 元素个数 O(1) |
| `l.empty()` | 是否为空 |

### list — 访问

| 函数 | 说明 |
|------|------|
| `l.front()` | 首元素 |
| `l.back()` | 尾元素 |

**没有 `operator[]` 和 `at()`!**

### list — 增删

| 函数 | 说明 |
|------|------|
| `l.push_front(x)` / `l.pop_front()` | 头部增删 |
| `l.push_back(x)` / `l.pop_back()` | 尾部增删 |
| `l.emplace_front(args...)` | 头部原位构造 |
| `l.emplace_back(args...)` | 尾部原位构造 |
| `l.insert(pos, x)` | 在 pos 前插入 x |
| `l.emplace(pos, args...)` | 在 pos 前原位构造 |
| `l.erase(pos)` | 删除 pos 处元素 |
| `l.clear()` | 清空 |
| `l.remove(x)` | 删除所有值为 x 的元素 |
| `l.remove_if(pred)` | 按条件删除 |

### list — 特有操作

| 函数 | 说明 |
|------|------|
| `l.sort()` | 排序 O(n log n) |
| `l.sort(cmp)` | 自定义比较排序 |
| `l.unique()` | 删除相邻重复元素（需先排序） |
| `l.merge(other)` | 合并两个已排序的 list，other 变为空 |
| `l.merge(other, cmp)` | 自定义比较合并 |
| `l.splice(pos, other)` | 把 other 的全部元素移到 pos 前 O(1) |
| `l.splice(pos, other, it)` | 移动 other 的单个元素 |
| `l.splice(pos, other, first, last)` | 移动 other 的一段 |
| `l.reverse()` | 反转链表 |

### forward_list — 特有注意点

由于单向链表无法直接拿到前驱，forward_list 使用 `before_begin()` 表示首节点前的位置：

| 函数 | 说明 |
|------|------|
| `fl.before_begin()` | 返回首元素之前的虚拟位置 |
| `fl.insert_after(pos, x)` | 在 pos 之后插入 |
| `fl.emplace_after(pos, args...)` | 在 pos 之后原位构造 |
| `fl.erase_after(pos)` | 删除 pos 之后的元素 |
| `fl.push_front(x)` / `fl.pop_front()` | 头部操作 |
| 无 `push_back()` / `pop_back()` | 尾部操作需要 O(n) |

## --------------------------------------------------------------------------
## 四、洛谷实战
## --------------------------------------------------------------------------

### P1996 约瑟夫问题（list 版本）

```cpp
#include <iostream>
#include <list>
using namespace std;

int main() {
    int n, m;
    cin >> n >> m;
    list<int> l;
    for (int i = 1; i <= n; i++) l.push_back(i);
    auto it = l.begin();
    while (!l.empty()) {
        for (int i = 1; i < m; i++) {
            it++;
            if (it == l.end()) it = l.begin();
        }
        cout << *it << " ";
        it = l.erase(it);
        if (it == l.end()) it = l.begin();
    }
    return 0;
}
```

### P1160 队列安排

```cpp
// N 个人排队，每次在某人左边或右边插入一个人，最后删除 M 个人，输出队伍
#include <iostream>
#include <list>
using namespace std;

list<int> team;
list<int>::iterator pos[100005]; // 记录每个人的迭代器位置
bool erased[100005];

int main() {
    int n;
    cin >> n;
    team.push_back(1);
    pos[1] = team.begin();
    for (int i = 2; i <= n; i++) {
        int k, p;
        cin >> k >> p;
        auto it = pos[k];
        if (p == 0) {
            pos[i] = team.insert(it, i);
        } else {
            auto nxt = next(it);
            pos[i] = team.insert(nxt, i);
        }
    }
    int m;
    cin >> m;
    for (int i = 0, x; i < m; i++) {
        cin >> x;
        erased[x] = true;
    }
    for (auto it = team.begin(); it != team.end(); ) {
        if (erased[*it]) it = team.erase(it);
        else ++it;
    }
    for (int x : team) cout << x << " ";
    return 0;
}
```

### P1540 机器翻译（list 版本，演示 splice）

```cpp
// 此题的 list 解法不是最优，仅用于演示 splice
#include <iostream>
#include <list>
#include <algorithm>
using namespace std;

int main() {
    int m, n, ans = 0;
    cin >> m >> n;
    list<int> cache;
    for (int i = 0, x; i < n; i++) {
        cin >> x;
        auto it = find(cache.begin(), cache.end(), x);
        if (it == cache.end()) {
            ans++;
            cache.push_back(x);
            if ((int)cache.size() > m) cache.pop_front();
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
> list 是双向链表，支持 O(1) 任意位置插入和删除（已知迭代器位置时）。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: 已知迭代器位置时，链表的插入和删除只需修改指针，时间 O(1)。

> [!question] 判断题 2
> list 支持下标随机访问 `l[i]`。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: list 不支持随机访问，没有 `operator[]` 和 `at()`。访问第 i 个元素需要 O(n) 遍历。

> [!question] 判断题 3
> forward_list 支持 `push_back()` 操作。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: forward_list 是单向链表，没有尾指针，尾部操作需要 O(n) 遍历。它只支持 `push_front()`。

> [!question] 判断题 4
> list 的插入和删除操作不会使其他元素的迭代器失效。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: 链表节点是独立分配的，插入/删除某个节点不影响其他节点的地址和迭代器。

> [!question] 判断题 5
> `list::sort()` 的时间复杂度是 O(n log n)。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: list 自带的 sort 使用归并排序，时间复杂度 O(n log n)。

> [!question] 判断题 6
> 可以对 list 使用 `std::sort()` 算法。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: `std::sort()` 要求随机访问迭代器，list 只有双向迭代器。必须用 list 自己的 `l.sort()`。

> [!question] 判断题 7
> `splice()` 操作可以 O(1) 地将一个 list 的全部元素移动到另一个 list 中。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: splice 只修改指针，不拷贝元素，时间 O(1)（移动整个 list 或单个元素时）。

> [!question] 判断题 8
> forward_list 有 `size()` 成员函数。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: forward_list 为了节省空间没有维护 size，没有 `size()` 函数。需要用 `std::distance()` 计算。

> [!question] 判断题 9
> list 比 vector 更适合需要频繁随机访问的场景。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: list 不支持随机访问，访问第 i 个元素需要 O(n)。频繁随机访问应该用 vector。

> [!question] 判断题 10
> list 的每个节点比 vector 多占用两个指针的内存空间。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: 双向链表每个节点需要一个 prev 指针和一个 next 指针，相比 vector 多出 2 个指针的开销。

> [!question] 选择题 1
> list 定义在哪个头文件中？
> - [ ] A. `<vector>`
> - [ ] B. `<list>`
> - [ ] C. `<deque>`
> - [ ] D. `<forward_list>`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: list 在 `<list>` 中，forward_list 在 `<forward_list>` 中。

> [!question] 选择题 2
> forward_list 使用哪个特殊迭代器来在首元素前插入？
> - [ ] A. `begin()`
> - [ ] B. `end()`
> - [ ] C. `before_begin()`
> - [ ] D. `rbegin()`
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > 
> > **解析**: `before_begin()` 返回首元素之前的虚拟位置，配合 `insert_after` 在头部插入。

> [!question] 选择题 3
> 以下哪个操作 list 有但 vector 没有？
> - [ ] A. `push_back()`
> - [ ] B. `push_front()`
> - [ ] C. `size()`
> - [ ] D. `clear()`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: vector 没有 `push_front()`（头部插入效率低），list 有。

> [!question] 选择题 4
> `list::unique()` 的作用是？
> - [ ] A. 删除所有重复元素
> - [ ] B. 删除相邻的重复元素
> - [ ] C. 对元素排序去重
> - [ ] D. 返回不重复元素的个数
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: `unique()` 只删除相邻重复元素。要去除所有重复需先 sort 再 unique。

> [!question] 选择题 5
> list 相比 vector 的最大劣势是？
> - [ ] A. 不支持排序
> - [ ] B. 不能存储自定义类型
> - [ ] C. 缓存不友好，随机访问 O(n)
> - [ ] D. 不支持迭代器
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > 
> > **解析**: list 节点分散在内存各处，缓存命中率低，且不支持随机访问。

> [!question] 选择题 6
> 在约瑟夫环问题中使用 list 的好处是？
> - [ ] A. 随机访问第 m 个人更快
> - [ ] B. 删除一个人后迭代器仍有效
> - [ ] C. 内存占用更少
> - [ ] D. 自动排序
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: list 删除元素后，其余元素的迭代器不失效，可以继续遍历。

> [!question] 选择题 7
> `list::merge(other)` 要求什么前提条件？
> - [ ] A. 两个 list 大小相等
> - [ ] B. 两个 list 都已排序
> - [ ] C. 两个 list 元素类型不同
> - [ ] D. 没有前提条件
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: merge 将两个已排序的 list 合并为一个排序的 list，前提是两者都已排序。

> [!question] 选择题 8
> forward_list 与 list 相比，优势是？
> - [ ] A. 支持双向遍历
> - [ ] B. 每个节点少一个指针，内存更省
> - [ ] C. 支持 push_back
> - [ ] D. 查找更快
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: forward_list 每个节点只有一个 next 指针，比 list 的两个指针省一半指针空间。

> [!question] 选择题 9
> 以下代码的作用是？
> ```cpp
> auto it = l.erase(it);
> ```
> - [ ] A. 删除 it 指向的元素并返回下一个有效迭代器
> - [ ] B. 删除 it 指向的元素并返回前一个迭代器
> - [ ] C. 清空整个 list
> - [ ] D. 编译错误
>
> > [!success]- 点击查看答案
> > 正确答案: A
> > 
> > **解析**: `erase` 返回被删除元素的下一个迭代器，是遍历删除的标准模式。

> [!question] 选择题 10
> LRU 缓存中，list 配合 map/unordered_map 使用的原因是？
> - [ ] A. list 访问最快
> - [ ] B. list 支持 O(1) 将已有元素移到头部（splice），map 做 O(1) 查找定位
> - [ ] C. list 自动排序
> - [ ] D. map 自动去重
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: map 存 key→迭代器映射实现 O(1) 查找，list 的 splice 可以 O(1) 移动节点到头部表示最近访问。

### 动手练习题

> [!question] 练习题 1
> **题目**: 使用 list 实现约瑟夫环问题：n 个人围成一圈，从第 1 个人开始报数，报到 m 的人出列。输出出列顺序。
> 
> **输入示例**:
> ```
> 7 3
> ```
> **输出示例**:
> ```
> 3 6 2 7 5 1 4
> ```

> [!question] 练习题 2
> **题目**: 使用 list 实现简单的文本编辑器：支持在光标位置插入字符、删除光标前的字符、光标左移、光标右移。输入操作序列，输出最终字符串。
> 
> **输入示例**:
> ```
> abcDE[[[de
> ```
> （`[` 表示光标左移，大写字母照常插入）
> **输出示例**:
> ```
> deabcDE
> ```

> [!question] 练习题 3
> **题目**: 实现一个简单的 LRU 缓存：容量为 k，支持 get(key) 和 put(key, value) 操作。使用 list + unordered_map 实现 O(1) 的 get 和 put。输出每次 get 的结果（不存在输出 -1）。
> 
> **输入示例**:
> ```
> 2
> put 1 10
> put 2 20
> get 1
> put 3 30
> get 2
> ```
> **输出示例**:
> ```
> 10
> -1
> ```

## --------------------------------------------------------------------------
## 🔗 知识网络
## --------------------------------------------------------------------------

- **上一容器**: [[容器类/07_priority_queue]] | **下一容器**: [[容器类/09_set_multiset]] | **返回**: [[目录]]
- **相关**: [[数据结构/D_链表_LinkedList]]
