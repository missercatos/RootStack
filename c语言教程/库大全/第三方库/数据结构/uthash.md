
# uthash

| 属性 | 说明 |
|------|------|
| 类型 | 纯头文件 (header-only) |
| 许可证 | BSD |
| 仓库 | https://github.com/troydhanson/uthash |

**核心结构**：

| 组件 | 说明 |
|------|------|
| `uthash` | 侵入式哈希表，在结构体内嵌入 `UT_hash_handle` 字段即可使用 |
| `utlist` | 侵入式双向/单向链表宏 |
| `utarray` | 类型安全的动态数组宏 |
| `utstring` | 动态字符串，类似 C++ 的 std::string 简化版 |
| `utringbuffer` | 环形缓冲区 |

**设计理念**：侵入式设计——数据结构的元数据直接嵌入用户结构体，不额外分配节点内存。添加、查找、删除均为 O(1) 均摊。

**典型代码**：

```c
struct my_struct {
    int id;
    char name[64];
    UT_hash_handle hh;   // 使该结构可哈希
};

struct my_struct *users = NULL;  // 哈希表头指针
struct my_struct *user = malloc(sizeof *user);
user->id = 1;
HASH_ADD_INT(users, id, user);   // 以 id 为键添加
HASH_FIND_INT(users, &search_id, user);  // 查找
HASH_DEL(users, user);  // 删除
```

**跨语言参考**: [[../../../../cpp教程/cpp深化教程/04_动态内存|C++动态内存]]
