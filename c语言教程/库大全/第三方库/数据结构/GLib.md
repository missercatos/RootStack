
# GLib

| 属性 | 说明 |
|------|------|
| 类型 | 编译型库（C 共享库） |
| 许可证 | LGPL |
| 仓库 | https://docs.gtk.org/glib/ |

**核心数据结构**：

| 类型 | 说明 | 类比 |
|------|------|------|
| `GList` | 双向链表 | std::list |
| `GSList` | 单向链表 | std::forward_list |
| `GHashTable` | 哈希表（任意键值对） | std::unordered_map |
| `GArray` | 动态数组（任意大小元素） | std::vector |
| `GPtrArray` | 指针数组 | std::vector<void*> |
| `GQueue` | 双端队列 | std::deque |
| `GTree` | 平衡二叉树（红黑树） | std::map |
| `GString` | 动态字符串 | std::string |
| `GStringChunk` | 字符串池 | — |

**超出数据结构的附加能力**：GLib 还提供事件循环（`GMainLoop`）、线程抽象（`GThread`）、内存切片分配器（`GSlice`）、Unicode 支持、日志系统等，是 GNOME/GTK 生态的基础层。

```c
GHashTable *ht = g_hash_table_new(g_str_hash, g_str_equal);
g_hash_table_insert(ht, "key", "value");
char *val = g_hash_table_lookup(ht, "key");
g_hash_table_destroy(ht);
```

**跨语言参考**: [[../../../cpp教程/cpp深化教程/04_动态内存|C++动态内存]]
