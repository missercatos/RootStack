
# yyjson

| 属性 | 说明 |
|------|------|
| 风格 | DOM（不可变树） + 流式读取 |
| 许可证 | MIT |
| 仓库 | https://github.com/ibireme/yyjson |

**核心特点**：**性能导向**——在 JSON 解析基准测试中通常排 C 语言榜第一。采用"不可变对象模型"（immutable），解析后生成的 JSON 树数据位不变，调用者只能读取。

| 特性 | 说明 |
|------|------|
| 解析性能 | 极快（比 cJSON 快 5-20x） |
| 内存效率 | 单一连续分配，内存碎片少 |
| 数字精度 | 支持完整 int64/uint64/double |
| 流式读取 | 支持分片解析大文件 |
| 修改 | DOM 树不可变，需用 mutable API 构建新文档 |

```c
yyjson_doc *doc = yyjson_read(json_data, json_len, 0);
yyjson_val *root = yyjson_doc_get_root(doc);
yyjson_val *name = yyjson_obj_get(root, "name");
printf("%s\n", yyjson_get_str(name));
yyjson_doc_free(doc);
```

> 需要高性能且只需读 JSON 时选 yyjson。需要修改 JSON 结构时选 cJSON 或 jansson。

**跨语言参考**: [[../../../2深化/08_标准库深度|C标准库深度剖析]]
