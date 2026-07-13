
# Check

| 属性 | 说明 |
|------|------|
| 类型 | C 单元测试框架 |
| 许可证 | LGPL |
| 仓库 | https://libcheck.github.io/check/ |

**核心特点**：在**独立进程**中运行每个测试（可选 `CK_FORK` 模式），防止崩溃或段错误终止整个测试套件。每个测试可以设置独立的 fixture（setup/teardown）。

**核心 API**：

| 函数 | 说明 |
|------|------|
| `tcase_create / suite_add_tcase` | 创建测试套件和用例 |
| `tcase_add_test` | 向用例添加测试 |
| `tcase_add_checked_fixture` | 添加 setup/teardown |
| `ck_assert_int_eq` | 整数相等断言 |
| `ck_assert_str_eq` | 字符串相等断言 |
| `ck_assert_ptr_null` | 指针为 NULL 断言 |

```c
#include <check.h>
START_TEST(test_add) {
    ck_assert_int_eq(add(2, 3), 5);
}
END_TEST

Suite *suite = suite_create("Math");
TCase *tc = tcase_create("Core");
tcase_add_test(tc, test_add);
suite_add_tcase(suite, tc);

SRunner *sr = srunner_create(suite);
srunner_run_all(sr, CK_NORMAL);
int failed = srunner_ntests_failed(sr);
srunner_free(sr);
```

**跨语言参考**: [[../../2深化/08_标准库深度|C标准库深度剖析]]
