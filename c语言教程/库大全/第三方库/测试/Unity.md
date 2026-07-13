
# Unity

| 属性 | 说明 |
|------|------|
| 类型 | 纯 C 单元测试框架 |
| 许可证 | MIT |
| 仓库 | https://github.com/ThrowTheSwitch/Unity |

**核心特点**：仅 3 个文件（`unity.c`, `unity.h`, `unity_internals.h`），零依赖。与 ThrowTheSwitch 生态（CMock, Ceedling）配对使用，是嵌入式 C 测试的事实标准。

**核心断言**：

| 宏 | 说明 |
|----|------|
| `TEST_ASSERT(condition)` | 通用条件断言 |
| `TEST_ASSERT_TRUE(condition)` | 期望真 |
| `TEST_ASSERT_FALSE(condition)` | 期望假 |
| `TEST_ASSERT_EQUAL(expected, actual)` | 整数/指针相等 |
| `TEST_ASSERT_EQUAL_FLOAT(expected, actual)` | 浮点相等 |
| `TEST_ASSERT_EQUAL_STRING(expected, actual)` | 字符串相等 |
| `TEST_ASSERT_NULL(pointer)` | 期望 NULL |
| `TEST_ASSERT_NOT_NULL(pointer)` | 期望非 NULL |
| `TEST_ASSERT_EQUAL_MEMORY(expected, actual, len)` | 内存块相等 |

**典型测试**：

```c
#include "unity.h"
void setUp(void) {}
void tearDown(void) {}

void test_addition(void) {
    TEST_ASSERT_EQUAL(5, add(2, 3));
    TEST_ASSERT_EQUAL(0, add(-1, 1));
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_addition);
    return UNITY_END();
}
```

**跨语言参考**: [[../../2深化/08_标准库深度|C标准库深度剖析]]
