
# cJSON

| 属性 | 说明 |
|------|------|
| 风格 | DOM（将整个 JSON 解析为内存树） |
| 许可证 | MIT |
| 仓库 | https://github.com/DaveGamble/cJSON |

**核心特点**：仅由 `cJSON.c` 和 `cJSON.h` 两个文件组成，零外部依赖。API 设计简洁直观，学习成本极低，是 C 语言最广泛使用的 JSON 库之一。

**核心类型与函数**：

| 类型/函数 | 说明 |
|-----------|------|
| `cJSON` | 核心类型，表示任意 JSON 节点 |
| `cJSON_Parse` | 解析 JSON 字符串为 cJSON 树 |
| `cJSON_Print` | 将 cJSON 树序列化为字符串（带格式） |
| `cJSON_GetObjectItem` | 从对象中按 key 获取值 |
| `cJSON_GetArrayItem` | 从数组中按索引获取值 |
| `cJSON_CreateObject` / `cJSON_CreateArray` | 创建各类型节点 |
| `cJSON_Delete` | 递归释放 cJSON 树 |

**典型解析**：

```c
cJSON *root = cJSON_Parse(json_string);
cJSON *name = cJSON_GetObjectItem(root, "name");
printf("Name: %s\n", name->valuestring);

cJSON *items = cJSON_GetObjectItem(root, "items");
int count = cJSON_GetArraySize(items);
for (int i = 0; i < count; i++) {
 cJSON *item = cJSON_GetArrayItem(items, i);
 printf("%d\n", item->valueint);
}
cJSON_Delete(root);
```

**跨语言参考**: [[../../../2深化/08_标准库深度|C标准库深度剖析]]
