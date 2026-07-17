# Catch2

"Modern C++ test framework" — 推崇表达力强的测试语法，使用自然的 `REQUIRE(a == b)` 等表达式。单头文件（或少量头文件），测试用例可以用文件夹结构组织。v3 版本进行了模块化拆分。

## 核心组件

| 组件 | 说明 |
|------|------|
| TEST_CASE() | 测试用例定义 |
| SECTION() | BDD 风格的测试分区 |
| REQUIRE() / CHECK() | 表达式断言 |
| REQUIRE_THROWS() | 异常断言 |
| GENERATE() | 数据生成器（参数化） |
| Matchers | 匹配器表达式 |
| Catch2::Session | 自定义测试运行器 |

## 何时使用

- 小型到中型项目
- 喜欢自然语法和简洁配置的开发者
- 无需 CMake 深度集成也能轻松使用
- BDD 风格测试编写

## 关键特性

自然表达式断言、BDD 风格 section、单/少头文件、彩色输出

## 相关链接

- [[GoogleTest|GoogleTest]] — 行业标准测试框架
- [[doctest|doctest]] — 极速编译替代
- 
- (搜索: Catch2)
