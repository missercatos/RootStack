# yaml-cpp

C++ 的 YAML 1.2 解析和生成库。YAML 是"人类可读"的配置格式，广泛用于 CI/CD、Docker、Kubernetes 等场景。支持 YAML 的所有核心类型和复杂嵌套结构。

## 核心组件

| 组件 | 说明 |
|------|------|
| YAML::Load / LoadFile | 从字符串或文件加载 YAML |
| YAML::Node | YAML 文档的树节点类型 |
| YAML::Node::operator[] | 通过键和索引访问 |
| YAML::Node::IsMap / IsSequence | 节点类型检查 |
| YAML::Emitter | 流式生成 YAML 输出 |
| YAML::Dump | 将节点序列化为字符串 |

## 何时使用

- 读取和生成配置文件
- 人类编辑的数据文件
- DevOps 工具链和构建系统配置
- 应用设置文件

## 关键特性

YAML 1.2 规范、人类可读格式、复杂结构支持、配置友好

## 相关链接

- [[nlohmann-json|nlohmann/json]] — JSON 格式
- [[Protobuf|Protobuf]] — 二进制序列化
- [[../../c语言教程/库大全/第三方库/相关文件|C 第三方库]]
- [[../索引|库索引]]
- (搜索: yaml-cpp)
