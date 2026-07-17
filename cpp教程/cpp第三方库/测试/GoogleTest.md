# GoogleTest

Google 出品的 C++ 测试框架，行业使用最广泛。提供丰富的断言宏、测试夹具、参数化测试、死亡测试等。与 CMake 深度集成，有大量 CI/CD 配套工具。Google Mock 已内置其中。

## 核心组件

| 组件 | 说明 |
|------|------|
| TEST() / TEST_F() | 基本测试和夹具测试 |
| ASSERT_* / EXPECT_* | 断言宏（致命/非致命） |
| INSTANTIATE_TEST_SUITE_P | 参数化测试 |
| SetUp() / TearDown() | 测试前后的初始化/清理 |
| EXPECT_CALL / MOCK_METHOD | Mock 对象定义和行为验证 |
| Testing::TestWithParam | 参数化测试基类 |
| ASSERT_DEATH | 死亡测试（验证程序崩溃） |

## 何时使用

- 几乎所有 C++ 项目的测试首选
- 大型团队和已有 CI/CD 流程的项目
- 需要 Mock 功能的单元测试
- 生态最完善，工具链支持最好

## 关键特性

最广泛使用、丰富的断言、参数化测试、死亡测试、集成 Mock

## 相关链接

- [[Catch2|Catch2]] — 现代语法测试框架
- [[doctest|doctest]] — 极速编译测试框架
- 
- (搜索: GoogleTest)
