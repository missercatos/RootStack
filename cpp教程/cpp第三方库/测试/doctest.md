# doctest

"最快的 C++ 测试框架" — 编译速度和运行速度都经过极致优化。API 风格类似 Catch2，但编译时间比 Catch2 快数倍（大量使用前置声明和模板外置技巧）。也可以像 Catch2 一样单头文件。

## 核心组件

| 组件 | 说明 |
|------|------|
| TEST_CASE() | 测试用例定义 |
| SUBCASE() | 测试分区（等价 Catch2 SECTION） |
| CHECK() / REQUIRE() | 表达式断言 |
| CHECK_THROWS() | 异常断言 |
| DOCTEST_CONFIG_* | 编译期配置选项 |
| doctest::Context | 运行配置和命令行解析 |
| doctest::Approx | 浮点数近似比较 |

## 何时使用

- 对编译时间敏感的大项目
- 想要 Catch2 风格但不喜欢其编译速度
- 测试数量极大的项目
- 需要最低测试框架开销的嵌入式项目

## 关键特性

编译极快、API 类似 Catch2、单头文件、低开销

## 相关链接

- [[Catch2|Catch2]] — 更丰富的测试语法
- [[GoogleTest|GoogleTest]] — 行业标准测试框架
- [[../索引|库索引]]
- (搜索: doctest C++)
