# CMake 深入：IMPORTED、生成器表达式与构建加速

## 原理

上一节 [[c语言教程/4工程化/01_CMake深入|CMake 深入（C 语言篇）]] 建立了 target-based 的基本心智模型：属性挂在 target 上，依赖按 PUBLIC/PRIVATE/INTERFACE 传播。本章向前推进四个 C++ 工程绕不开的进阶主题：**IMPORTED 目标与 ALIAS、生成器表达式、CPack 打包、模板驱动的构建优化**。

### IMPORTED 目标：把"外部库"变成一等 target

`find_package` 成功后创建的就是 IMPORTED 目标——它描述一个**在本项目之外构建好的库**，自带 include 路径、链接库、位置等元数据：

```cmake
find_package(OpenSSL 3.0 REQUIRED)     # 版本参数会参与兼容性检查

get_target_property(loc OpenSSL::SSL IMPORTED_LOCATION)
message(STATUS "libssl 位于: ${loc}")  # imported target 可查询元数据
```cpp

三种 IMPORTED 配置域对应不同场景：

```cmake
add_library(coolutil STATIC IMPORTED)          # 声明：这是外部产物
set_target_properties(coolutil PROPERTIES
    IMPORTED_LOCATION_DEBUG   /opt/dbg/libcoolutil.a   # Debug 构建用这份
    IMPORTED_LOCATION_RELEASE /opt/opt/libcoolutil.a   # Release 用这份
    INTERFACE_INCLUDE_DIRECTORIES /opt/include          # 传给使用方
)
```cmake

自己手写 IMPORTED 声明的典型场景：预编译 SDK（厂商只发 `.a/.so + 头文件`）。把它包装成 target 后，下游 `target_link_libraries(app PRIVATE coolutil)` 一行搞定，无需再碰路径细节。

### ALIAS：给 target 起稳定别名

```cmake
add_library(mylib::mylib ALIAS mylib)      # 项目内别名，带命名空间风格

target_link_libraries(app PRIVATE mylib::mylib)
```cmake

价值在于**命名一致性**：无论 mylib 是本项目子目录里的真 target、FetchContent 拉进来的，还是 find_package 找到的 IMPORTED，使用方永远写同一个名字 `mylib::mylib`。开源库的标准姿势就是同时提供两者——本地的真实 target 和安装导出的同名 alias，让源码集成与二进制集成无缝切换。

### 生成器表达式：configure 时还不知道答案怎么办

普通变量在 configure 阶段求值；但有些信息要等生成阶段才知道（构建类型、平台、是否正在被 install）。生成器表达式 `$<...>` 就是延迟到生成期求值的语法：

```cmake
target_compile_options(mylib PRIVATE
    $<$<CXX_COMPILER_ID:MSVC>:/W4>       # 仅 MSVC 加 /W4
    $<$<NOT:$<CXX_COMPILER_ID:MSVC>>:-Wall -Wextra>
)

target_compile_definitions(mylib PRIVATE
    $<$<CONFIG:Debug>:MYLIB_VERBOSE_LOG>   # 只有 Debug 配置定义此宏
)
```cpp

最关键的一对是 install/export 场景下的**路径分身术**：

```cmake
target_include_directories(mylib PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>   # 源码内构建：指源码树
    $<INSTALL_INTERFACE:include>                             # 安装后消费：指相对前缀
)
```cmake

为什么必须这样拆？因为 build 树里的绝对路径在安装到别机器后毫无意义，而 `include` 相对路径在 build 阶段又不成立。两个表达式让同一份 target 元数据在两种生命周期里各自指向正确位置。

```mermaid
graph LR
    subgraph "BUILD_INTERFACE 生效期"
        S["源码树 include/"] --> B["build 中直接编译"]
    end
    subgraph "INSTALL_INTERFACE 生效期"
        P["prefix/include"] --> D["find_package 的下游项目"]
    end
    T["target_include_directories(PUBLIC)"] --> S
    T --> P
```cpp

---

## 语法

### FetchContent 依赖锁定 GIT_TAG

```cmake
include(FetchContent)
FetchContent_Declare(fmt
    GIT_REPOSITORY https://github.com/fmtlib/fmt.git
    GIT_TAG        10.2.1          # 必须锁 tag 或 commit hash，禁止分支名
    GIT_SHALLOW    TRUE            # 浅克隆只取该 tag，大幅提速
)
FetchContent_MakeAvailable(fmt)
```cpp

锁定的意义：`GIT_TAG main` 意味着每次 configure 可能拉到不同代码，昨天能编译今天报错，等于把不确定性引入版本控制体系。正确做法与 Maven 固定版本号同理——tag 即坐标。团队级复现可再加 `FETCHCONTENT_SOURCE_DIR_<NAME>` 指向本地镜像做离线构建。

### CPack：一条命令产出 deb/rpm/zip

CPack 复用你已写好的 install 规则来打包，install 定义什么进包，CPack 决定包成什么格式：

```cmake
install(TARGETS myapp RUNTIME DESTINATION bin)
install(FILES myapp.1 DESTINATION share/man/man1)

set(CPACK_PACKAGE_NAME           "myapp")
set(CPACK_PACKAGE_VERSION        ${PROJECT_VERSION})
set(CPACK_PACKAGE_CONTACT        "dev@example.com")   # deb/rpm 维护者字段
set(CPACK_DEBIAN_PACKAGE_SHLIBDEPS ON)                # 自动计算 .deb 依赖
set(CPACK_RPM_PACKAGE_LICENSE    "MIT")
include(CPack)                                        # 必须放最后
```cpp

```bash
cpack -G "DEB;RPM;ZIP"     # 一次生成多种格式
ls *.deb *.rpm *.zip
```cpp

对比手工维护 `debian/control` 与 `.spec` 文件，CPack 让"打包"退化为 install 规则的自然延伸。CI 里配合 matrix 可以同轮产出多发行版工件。

### 模板对构建的影响

C++ 特有的痛点：**每个翻译单元独立实例化模板**。同一个 `std::vector<int>` 被 100 个 .cpp 使用就实例化 100 次，链接器再去重——这是 C++ 编译慢于 C 的头号原因。缓解手段：

1. **接口与实现分离**：模板实现放 .tpp 并显式实例化常用类型，收敛爆炸半径；
2. **减少头文件中的重型模板**：pimpl 手法把实现细节移出头文件；
3. **PCH 预编译头**：把几乎不变的公共大头（STL、第三方头）提前编译。

显式实例化收敛的典型写法：

```cpp
// matrix.h —— 模板声明 + 底部声明"这些实例在别处已编译"
template<typename T> class Matrix { /* ... */ };
extern template class Matrix<float>;    // extern：告诉本 TU 不要重复实例化

// matrix.cpp —— 在唯一的地方定义实例化
template class Matrix<float>;
template class Matrix<double>;
```cpp

效果：使用 `Matrix<float>` 的 100 个 .cpp 都不再各自展开模板体，只引用 .cpp 里那一份符号。代价是可用类型集合被固定，泛型库（header-only）无法采用——这正是 header-only 与构建速度的取舍点。

### target_precompile_headers 预编译头

```cmake
target_precompile_headers(myengine
    PRIVATE
        <vector>
        <string>
        <unordered_map>
        <memory>
        <algorithm>
)
# CMake 会自动生成 cmake_pch.hxx，强制所有源文件先包含这些头并共享其编译结果
```cpp

工作原理图解：

```mermaid
graph TD
    subgraph "无 PCH"
        A1[a.cpp] --> C1[解析 vector/string/map...]
        B1[b.cpp] --> C2[再解析一遍]
        D1[c.cpp] --> C3[又解析一遍]
    end
    subgraph "有 PCH"
        H["稳定头集合"] --> P["cmake_pch.hxx.gch 只编译一次"]
        P --> A2["a.cpp 直接加载缓存"]
        P --> B2["b.cpp 直接加载缓存"]
        P --> D2["c.cpp 直接加载缓存"]
    end
```cpp

收益衡量标准：全量重编时间下降 30% 以上的项目才值得上 PCH；小项目反而增加复杂度。注意 PCH 只放**稳定不变**的头——把自己频繁修改的头塞进去会让每次改动都触发全量重编，适得其反。

两条工程细则：

1. `target_precompile_headers` 支持三种写法：尖括号系统头 `<string>`、引号项目头 `"base/config.h"`、`CMARK` 强制注入；PUBLIC 可让依赖此 target 的下游共享同一份 PCH；
2. Unity Build（`set_target_properties(t UNITY_BUILD ON)`）是另一条加速路线——把多个 .c/.cpp 合并成一个 TU 编译，与 PCH 正交可叠加，但要小心同名 static 函数冲突。

### compile_commands.json 与编辑器生态

```bash
cmake -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
ls build/compile_commands.json   # 每个源文件的精确编译命令清单
```cmake

这份 JSON 是现代 C++ 工具链的通用输入格式：

| 工具 | 如何消费 |
|------|---------|
| clangd | 编辑器补全/跳转/诊断的事实标准输入 |
| clang-tidy | 无它则无法准确分析（见 [[c语言教程/4工程化/02_C项目工程化\|C 项目工程化]]） |
| include-what-you-use | 头文件包含审计 |

编辑器接入三选一：

- **VSCode + clangd 插件**：装好后指向 build 目录即生效，体验接近 CLion；
- **CLion**：内置 CMake 支持，自动生成并使用 compile_commands.json，零配置；
- **CMake Tools 扩展**：提供 configure/build/debug 全流程按钮，与 clangd 组合是 VSCode 下主流方案。

工程惯例是把 `-DCMAKE_EXPORT_COMPILE_COMMANDS=ON` 写成默认（3.20+ 可用 `set(CMAKE_EXPORT_COMPILE_COMMANDS ON ...)`），或在仓库根放一个指向 `build/compile_commands.json` 的软链供工具发现。

---

## 实践

实战目标：实现一个 header-only 库 `tinyjson`（纯模板 + 头文件，无 .cpp），并用一个使用方项目展示现代消费范式。

### header-only 库的项目结构（嵌套列表）

- tinyjson/
  - CMakeLists.txt
  - include/tinyjson/tinyjson.h （全部实现在这一个头里）
  - tests/test_tinyjson.cpp

### 库端 CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.16)
project(tinyjson VERSION 1.2.0 LANGUAGES CXX)

add_library(tinyjson INTERFACE)                 # INTERFACE = 无物可编，纯契约
add_library(tinyjson::tinyjson ALIAS tinyjson)  # 别名与安装名保持一致

target_compile_features(tinyjson INTERFACE cxx_std_17)   # 要求使用方 C++17

target_include_directories(tinyjson INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>  # 源码内构建用绝对路径
    $<INSTALL_INTERFACE:include>                            # 安装后用相对前缀
)

# ---- 安装与导出：让下游可以 find_package(tinyjson) ----
include(GNUInstallDirs)                         # 提供 CMAKE_INSTALL_INCLUDEDIR 等标准目录
install(TARGETS tinyjson EXPORT tinyjsonTargets)
install(DIRECTORY include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

install(EXPORT tinyjsonTargets
    NAMESPACE tinyjson::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/tinyjson
)
```cmake

### header-only 库的全部价值浓缩

INTERFACE target 没有编译产物，PUBLIC/PRIVATE 之辨消失，一切要求都通过 INTERFACE 传播给使用方。它适合承载：纯模板/纯宏/纯内联实现、编译期计算工具（类似 `std::integer_sequence`）、以及跨平台抽象层。不适合的场景：含较多非模板实现代码（会拖慢所有下游 TU 的解析）、需要隐藏商业逻辑的闭源组件（头文件即源码，无法保密）。

一个值得记住的对照案例：fmt 库同时提供 header-only 模式（`FMT_HEADER_ONLY` 宏）与编译库模式——默认走编译库换取下游构建速度，header-only 模式服务"不想管理二进制依赖"的用户。设计自己库时同样应该回答：**我的用户更怕链接麻烦，还是更怕编译慢？**

### 使用方项目

```cmake
cmake_minimum_required(VERSION 3.16)
project(json_app LANGUAGES CXX)

# 方式一：FetchContent 直接源码集成（开发期首选）
include(FetchContent)
FetchContent_Declare(tinyjson
    GIT_REPOSITORY https://git.example.com/libs/tinyjson.git
    GIT_TAG v1.2.0                 # 锁定发布 tag
)
FetchContent_MakeAvailable(tinyjson)

add_executable(json_app main.cpp)
target_link_libraries(json_app PRIVATE tinyjson::tinyjson)   # 一个名字走天下

# 开发体验增强：导出编译数据库给 clangd
set(CMAKE_EXPORT_COMPILE_COMMANDS ON CACHE INTERNAL "")

# 大型项目可选：为 main.cpp 所在 target 上预编译头
target_precompile_headers(json_app PRIVATE
    <string> <vector> <iostream>)
```asm

```cpp
// main.cpp —— 使用方对集成方式完全无感知
#include <tinyjson/tinyjson.h>
#include <iostream>

int main() {
    auto doc = tinyjson::parse(R"({"name":"root","n":42})");
    std::cout << doc["name"].as_string() << "\n";   // root
    return 0;
}
```cpp

验证流程：

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build && ./build/json_app
ctest --test-dir build --output-on-failure
```cpp

### 打包发布（CPack 补完）

在库端 CMakeLists 追加：

```cmake
set(CPACK_GENERATOR "TGZ")
set(CPACK_PACKAGE_VERSION ${PROJECT_VERSION})
include(CPack)
```cmake

执行 `cpack -G TGZ` 得到源码/安装包，上传 release 页并附 SHA256，即可被任何下游 FetchContent 按 tag 锁定消费——完成从"我写了库"到"生态可依赖"的最后一步。

### 实践自检清单

发布一个 C++ 库前逐项核对：

1. target 是否带命名空间别名（`tinyjson::tinyjson`），下游源码/二进制两种集成方式名字一致？
2. include 目录是否用 `$<BUILD_INTERFACE:>`/`$<INSTALL_INTERFACE:>` 双表达式声明？
3. 是否通过 `target_compile_features` 声明最低语言标准，而不是让下游猜？
4. FetchContent 的 GIT_TAG 是否锁定到具体 release tag？
5. install(EXPORT) 产出的 targets 文件能否在干净机器上 `find_package` 成功？
6. CI 中 Debug 与 Release 双配置均编译通过，CTest 全绿？
7. 若为 header-only 库，是否在 README 中明确"纯头文件、无链接步骤"的使用说明？

---

## 常见坑排查

### 链接顺序与循环依赖

传统链接器从左到右解析符号，`target_link_libraries(app PRIVATE a b)` 中若 a 依赖 b，顺序错误会报 undefined reference。现代 CMake 的 target 依赖图会自动推导传递闭包并重排，所以**只要依赖声明完整**就不会踩坑——再次印证"显式声明一切"的价值。真正的循环依赖（a 要 b、b 又要 a）需要重构拆层，CMake 无法替你设计架构。

### 双 target 同名冲突

子目录里 `add_library(mylib ...)` 后又 `find_package(mylib)` 会产生同名冲突。规范解法：项目内部用真实 target，外部引入统一走 ALIAS/命名空间名，二者永不撞车。

### 全局函数与 target 函数混用自查清单

| 见到这个 | 换成这个 |
|---------|---------|
| `include_directories(...)` | `target_include_directories(t ...)` |
| `add_definitions(-DX)` | `target_compile_definitions(t PRIVATE X)` |
| `link_directories(...)` | 给 imported/alias target 正确设置路径后直接 link |
| `set(CMAKE_CXX_FLAGS ...)` | `target_compile_options(t ...)` + 生成器表达式 |
| `file(GLOB ...)` 收源文件 | 显式列出，新增文件重新 configure |

---

## 小结

- IMPORTED 目标把外部/预编译库包装成带元数据的一等公民，ALIAS 保证集成方式切换时使用方零改动；
- 生成器表达式解决"生成期才可知"的条件配置，`$<BUILD_INTERFACE:>`/`$<INSTALL_INTERFACE:>` 是 export 正确性的基石；
- FetchContent 必须锁 GIT_TAG，CPack 让打包复用 install 规则；
- 模板逐 TU 实例化是 C++ 构建慢的根源，显式实例化收敛符号、PCH 用 `target_precompile_headers` 精准打击稳定大头；
- `CMAKE_EXPORT_COMPILE_COMMANDS` 导出的 JSON 是 clangd/clang-tidy/IDE 的通用底座，现代 C++ 开发环境的地基。

下一章解决更上游的问题——第三方库从哪来、怎么管：[[cpp教程/cpp深化教程/17_包管理器Conan与vcpkg|包管理器 Conan 与 vcpkg]]。
