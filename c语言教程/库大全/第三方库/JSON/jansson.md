
# jansson

| 属性 | 说明 |
|------|------|
| 风格 | DOM |
| 许可证 | MIT |
| 仓库 | https://github.com/akheron/jansson |

**核心特点**：API 更严谨，错误处理更完善（每步操作返回错误码）。线程安全，引用计数管理内存。

| 函数 | 说明 |
|------|------|
| `json_loads` / `json_loadf` / `json_loadfd` | 从字符串/文件/文件描述符解析 |
| `json_dumps` / `json_dumpf` / `json_dumpfd` | 序列化到字符串/文件/描述符 |
| `json_object_get` / `json_object_set` | 访问/设置对象属性 |
| `json_array_get` / `json_array_append_new` | 数组访问和追加 |
| `json_string_value` / `json_integer_value` | 提取原始值 |
| `json_decref` | 释放引用 |

```c
json_error_t error;
json_t *root = json_loads(json_string, 0, &error);
const char *name = json_string_value(json_object_get(root, "name"));
json_decref(root);
```

**cJSON vs jansson**：

| 特性 | cJSON | jansson |
|------|-------|---------|
| 文件数量 | 2 个（.c + .h） | 完整构建系统 |
| 错误信息的详细程度 | 简单 | 详细（含行列号） |
| 内存管理 | 手动 free | 引用计数 |
| 线程安全 | 否 | 是 |

**跨语言参考**: [[../../../2深化/08_标准库深度|C标准库深度剖析]]
