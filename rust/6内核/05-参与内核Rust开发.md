# 参与内核 Rust 开发

## 1. 为什么你应该参与？

Linux 内核是世界上最广泛使用的操作系统内核，运行在数十亿台设备上。而 Rust for Linux 项目正站在一个历史性的十字路口——**将内存安全语言引入内核**，这可能是自 C 语言被用于 Unix 内核以来，操作系统内核开发中最重要的编程语言变革。

你参与的意义：
1. **历史性贡献**：成为第一个在主线内核中使用内存安全语言开发的先驱
2. **影响力巨大**：你的代码运行在数十亿台设备上
3. **技能提升**：内核开发经验是软件工程领域最有价值的经验之一
4. **社区认可**：内核贡献者的声誉在行业中极高
5. **做正确的事**：减少安全漏洞，直接保护数十亿用户

"Rust for Linux 是那种你可以在历史上留下印记的项目。它很小，你可以产生巨大的影响。" -- Wedson Almeida Filho（前 Google Rust for Linux 核心开发者）

> 📌 **C语言是内核的基础**：参与Rust内核开发同样需要理解C语言内核代码。请参阅 [[../../内核/系统内核/07_Linux内核源码导读|C语言教程: Linux内核源码导读]] 了解内核源码结构、编码规范和核心数据结构（如list.h、container_of等）。

## 2. 前提知识

### 2.1 必须掌握

| 领域 | 具体要求 | 学习资源 |
|------|---------|---------|
| **Rust** | 所有权、借用、生命周期、trait、泛型、unsafe 边界 | Rust Book、Rust by Example |
| **C** | 能阅读和理解 C 内核代码 | 内核源码 + LWN 文章 |
| **Linux 内核基础** | 模块、设备模型、内存管理、中断、锁、sysfs | Linux Device Drivers 第3版 |
| **Git** | 分支、格式化补丁、发送补丁邮件、变基 | Pro Git |
| **命令行** | 内核配置、编译、QEMU 测试 | 实践 |

### 2.2 推荐但不必须

- **Linux 内核子系统知识**：具体驱动框架（如 DRM、块层）
- **LLVM/clang 经验**：理解内核对 LLVM=1 的要求
- **嵌入式开发**：交叉编译、设备树
- **安全研究**：漏洞分析、fuzzing

### 2.3 自我评估清单

你能通过以下测试吗？
1. 理解一段 C 内核代码（如简单驱动的 probe 函数）
2. 解释 Rust 的 borrow checker 如何工作
3. 在内核源码树中找到特定子系统的维护者
4. 解释 GFP_KERNEL 和 GFP_ATOMIC 的区别
5. 编写一个可以加载/卸载的内核模块

如果上述任何一项让你不确定，建议先补齐基础。

## 3. 寻找任务

### 3.1 入门任务类型

最适合初学者的任务类型：

| 任务类型 | 难度 | 描述 | 示例 |
|---------|------|------|------|
| 文档改进 | 1星 | 修复语法错误、添加缺失的文档、翻译 | Documentation/rust/ 中的文件 |
| 警告修复 | 2星 | 修复 clippy 警告或编译警告 | unused imports、non_snake_case |
| 测试添加 | 2星 | 为现有抽象添加 kunit 测试 | rust/kernel/sync/arc.rs 的测试 |
| 简单抽象 | 3星 | 封装简单的 C API | 如 kmem_cache 的 Rust 封装 |
| 示例模块 | 2星 | 创建新的示例模块 | samples/rust/ 中的演示代码 |
| 错误修复 | 4星 | 修复已报告的 bug | syzbot 报告定位和修复 |

### 3.2 在哪里找任务

**1. 内核邮件列表（LKML）**

订阅 `rust-for-linux@vger.kernel.org`：发送空邮件到 `rust-for-linux+subscribe@vger.kernel.org` 即可订阅。

**2. GitHub Issues**

Rust for Linux 的 GitHub 组织：`https://github.com/Rust-for-Linux/linux/issues`，按 "good first issue" 标签筛选。

**3. 内核中的 TODO 注释**

在内核源码中搜索：
```bash
grep -rn "TODO\|FIXME\|XXX" rust/ samples/rust/
grep -rn "TODO" rust/kernel/ | head -20
```

**4. 邮件列表中的待完成任务**

在 lore.kernel.org 上搜索：`https://lore.kernel.org/rust-for-linux/`，查找 "RFC v2 needed"、"needs review" 等。

### 3.3 具体的入门项目建议

| 项目 | 预计时间 | 技能收益 |
|------|---------|---------|
| 改善 rust/kernel/str.rs 的文档 | 4-8 小时 | 学习 CStr API |
| 为 Mutex<T> 添加单元测试 | 8-16 小时 | 理解同步抽象 |
| 实现 WARN_ON 宏的 Rust 等效 | 8-12 小时 | 宏开发、打印 API |
| 为 platform::Device 添加方法 | 16-24 小时 | 平台设备抽象 |
| 创建 Rust 的 pr_*_ratelimited 宏 | 12-20 小时 | 日志系统 |

### 3.4 判断一个任务是否适合你

问自己：
1. 我能理解这个任务的目标吗？
2. 我熟悉涉及的 C 内核 API 吗？
3. 这个任务有人在做了吗？（搜索邮件列表）
4. 维护者对这类贡献的接受度如何？（先发 RFC 探测）

## 4. 贡献工作流

### 4.1 完整流程概览

```
[1]  订阅邮件列表
      |
[2]  克隆开发仓库
      |
[3]  寻找/选择任务
      |
[4]  在邮件列表声明意图 （大任务建议做）
      |
[5]  编写代码 & 测试
      |
[6]  格式化 & 检查
      |
[7]  编写提交信息
      |
[8]  生成补丁
      |
[9]  发送到邮件列表
      |
[10] 处理审查反馈
      |   （重复 5-10 直到接受）
[11] 补丁被合并
      |
[12] 庆祝
```

### 4.2 准备工作

```bash
# 1. 确保工具链正确
rustc --version
bindgen --version
# 对照 Documentation/rust/quick-start.rst 检查版本

# 2. 克隆 Rust for Linux 开发仓库
git clone https://github.com/Rust-for-Linux/linux.git rust-dev
cd rust-dev

# 3. 添加官方主线作为上游
git remote add torvalds \
  https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git

# 4. 基于最新主线创建特性分支
git fetch torvalds
git checkout -b my-rust-contribution torvalds/master

# 5. 配置内核编译环境
make LLVM=1 rustavailable  # 确认 Rust 工具链就绪
make LLVM=1 defconfig
scripts/config --enable CONFIG_RUST
scripts/config --enable CONFIG_SAMPLE_RUST_MINIMAL
make LLVM=1 olddefconfig
```

### 4.3 代码和格式化

**代码风格**：

内核 Rust 代码使用 `rustfmt`，但带有内核特定的配置：

```bash
# 格式化你的代码
rustfmt +nightly rust/kernel/your_file.rs
# 或使用内核提供的格式化脚本
make LLVM=1 rustfmt
```

**关键编码规范**：

```rust
// 1. 使用内核错误码，不是自定义错误
// 正确:
fn my_func() -> Result<u32> {
    Err(Error::EINVAL)
}
// 错误:
// fn my_func() -> Result<u32, MyError> { Err(MyError::Invalid) }

// 2. 避免 unwrap/expect
// 正确:
let val = option.ok_or(Error::EINVAL)?;
// 错误:
// let val = option.unwrap();  // panic in kernel!

// 3. SAFETY 注释必须解释为什么不安全代码是安全的
// SAFETY: ptr is valid because the Arc reference ensures
// the allocation is not freed while this reference exists.
unsafe { (*ptr).field = value; }

// 4. 使用 kernel::prelude::* 导入常用项
use kernel::prelude::*;

// 5. 文档使用 /// 注释，包含安全性说明
/// Reads a 32-bit value from MMIO at the given offset.
///
/// # Errors
///
/// Returns ERANGE if the offset is out of bounds.
fn read32(&self, offset: usize) -> Result<u32> { Ok(0) }
```

**编译和检查**：

```bash
# 构建内核
make LLVM=1 -j$(nproc)

# 构建模块
make LLVM=1 -j$(nproc) modules

# Clippy（需要先安装 clippy 组件）
make LLVM=1 CLIPPY=1

# 检查是否有编译警告（内核警告被视为错误）
make LLVM=1 -j$(nproc) 2>&1 | grep -E "warning:|error:"
```

### 4.4 编写提交信息

内核提交信息有严格的格式要求：

```text
subsystem: Brief summary (50 chars max)

A more detailed explanation of what the patch does and why.
This can span multiple paragraphs. Explain the motivation
for the change, not just what changed.

Describe the approach taken. Reference previous discussions
on the mailing list. Explain any trade-offs made.

Mention testing performed:
- Build-tested: make LLVM=1 -j$(nproc)
- Boot-tested: QEMU x86_64
- Module tested: loaded/unloaded successfully

Link: https://lore.kernel.org/rust-for-linux/...
Signed-off-by: Your Name <your.email@example.com>
```

**规则**：
1. 首行：子系统: 简短摘要（不超过 50 字符），不加句号
2. 空一行
3. 正文：详细说明（每行 72 字符）
4. Signed-off-by：使用 git commit -s 自动添加

### 4.5 发送补丁

**单补丁**：

```bash
# 生成补丁文件
git format-patch -1 HEAD

# 检查补丁
scripts/checkpatch.pl 0001-*.patch

# 发送补丁（需要配置 msmtp 或 git send-email）
git send-email \
    --to="rust-for-linux@vger.kernel.org" \
    --cc="linux-kernel@vger.kernel.org" \
    --cc="Miguel Ojeda <ojeda@kernel.org>" \
    --cc="Alex Gaynor <alex.gaynor@gmail.com>" \
    0001-*.patch
```

**补丁系列（多个相关补丁）**：

```bash
# 生成补丁系列（最后 3 个提交）
git format-patch -3 --cover-letter

# 编辑封面信（cover letter）
vim 0000-cover-letter.patch

# 发送补丁系列
git send-email \
    --to="rust-for-linux@vger.kernel.org" \
    --cc="linux-kernel@vger.kernel.org" \
    0000-*.patch
```

**发送前的检查清单**：

- [ ] 补丁基于最新主线（torvalds/master）
- [ ] 没有未提交的更改
- [ ] 补丁通过了 checkpatch
- [ ] 编译通过（无警告）
- [ ] 提交信息格式正确
- [ ] Signed-off-by 正确

### 4.6 处理审查反馈

**积极回应的态度**：

> 感谢审查！你的建议很有道理。我会在下个版本中修复。

> 关于你提到的锁顺序问题——我选择当前顺序是因为
> [技术原因]。你觉得这个理由充分吗？

**修改代码并重新发送**：

```bash
# 1. 修改代码
vim rust/kernel/your_file.rs

# 2. 在提交信息中添加变更日志
git rebase -i HEAD~1
# 在提交信息中添加：
# ---
# Changes in v2:
# - Fixed lock ordering issue as suggested by Reviewer Name
# - Added missing SAFETY comment
# - Link to v1: https://lore.kernel.org/.../msg12345.html

# 3. 重新生成并发送
git format-patch -1 HEAD --subject-prefix="PATCH v2"
```

### 4.7 常见的审查反馈和应对

| 审查反馈 | 含义 | 应对 |
|----------|------|------|
| "Please add a SAFETY comment" | unsafe 块缺少安全性说明 | 添加 // SAFETY: 注释 |
| "NIT: s/funtion/function/" | 拼写错误 | 修复，无需讨论 |
| "Why not use ...?" | 建议采用替代方法 | 解释或采纳 |
| "This doesn't follow kernel style" | 风格不统一 | 参考现有代码修改 |
| "Please split this patch" | 一个补丁做了太多事 | 拆分为多个补丁 |
| "Needs more testing" | 测试不足 | 添加测试说明或编写测试 |
| "I don't think this is the right approach" | 设计问题 | 讨论替代方案 |
| "NAK" | 拒绝（Not Acknowledged） | 理解原因，重新设计 |

## 5. 理解审查流程

### 5.1 谁在审查？

Rust for Linux 的维护者（截至 2025 初）：

| 姓名 | 角色 | 邮件 |
|------|------|------|
| Miguel Ojeda | 主维护者 | ojeda@kernel.org |
| Alex Gaynor | 共同维护者 | alex.gaynor@gmail.com |
| Wedson Almeida Filho | 共同维护者 | wedsonaf@gmail.com |
| Boqun Feng | 共同维护者 | boqun.feng@gmail.com |
| Gary Guo | 共同维护者 | gary@garyguo.net |
| Bjorn Roy Baron | 共同维护者 | bjorn3_gh@protonmail.com |
| Andreas Hindborg | Rust 审查者 | a.hindborg@samsung.com |
| Alice Ryhl | Rust 审查者 | aliceryhl@google.com |

### 5.2 审查阶段

```
[邮件到达邮件列表]
       |
[维护者或审查者阅读补丁]
       |
[评论发送到邮件列表]
       |
[你回应评论并修改代码]
       |   （可能重复 1-10 次）
[审查者满意]
       |
["Reviewed-by" 或 "Acked-by" 标签]
       |
[维护者将补丁合并到 rust-next 分支]
       |
[linux-next 集成测试]
       |
[合并窗口开启时发送给 Linus]
       |
[Linus 合并入主线]
```

### 5.3 时间预期

| 步骤 | 典型时间 | 可能出现延迟 |
|------|---------|-------------|
| 首次审查反馈 | 1-7 天 | 维护者假期/会议周 |
| 每次修改后反馈 | 3-10 天 | 取决于审查者可用性 |
| 简单补丁从发送到合并 | 2-8 周 | 如果争议较大可能更久 |
| 复杂补丁从发送到合并 | 2-6 个月 | 大型新抽象需要多轮讨论 |

**耐心是参与内核开发的必备品质。**

## 6. 真实案例：一个合并补丁的完整旅程

### 6.1 背景

一个真实的小型补丁：向 kernel::error 添加 from_kernel_errno 函数。

### 6.2 初始提交（v1）

```rust
// 补丁：添加 from_kernel_errno 构造函数
// rust: error: add Error::from_kernel_errno function
//
// Add a convenience function to create an Error from a kernel
// errno value (e.g., EINVAL = 22).

impl Error {
    /// Creates an Error from a kernel error code (positive errno).
    pub fn from_kernel_errno(errno: core::ffi::c_int) -> Error {
        Error(-errno)
    }
}
```

### 6.3 审查者评论

**审查者 1**：
> Should this check that errno is in a valid range? If a caller
> accidentally passes a negative number, we'd create an Error
> with a positive internal value, which would be confusing.

**审查者 2**：
> Could you add a documentation example showing how this is used
> with a real C function wrapper?

**审查者 3**：
> NIT: the doc comment line is slightly over 100 chars, please wrap.

### 6.4 修改后重新提交（v2）

```rust
// Changes in v2:
// - Added documentation example
// - Fixed doc comment line length

impl Error {
    /// Creates an [`Error`] from a kernel error code.
    ///
    /// This is typically used when wrapping a C function that
    /// returns a positive `errno` value.
    ///
    /// # Example
    ///
    /// ```
    /// # use kernel::error::Error;
    /// let err = Error::from_kernel_errno(bindings::EINVAL);
    /// assert_eq!(err.to_errno(), bindings::EINVAL);
    /// ```
    pub fn from_kernel_errno(errno: core::ffi::c_int) -> Error {
        // SAFETY: The caller ensures that errno is a valid
        // positive kernel error code.
        Error(-errno)
    }
}
```

### 6.5 审查者接受（v2）

```
Reviewed-by: Reviewer Name <reviewer@example.com>
Acked-by: Another Reviewer <another@example.com>
```

### 6.6 合并

维护者将补丁合并到 rust-next 分支，经过 linux-next 测试后，在下一个合并窗口被 Linus 拉入主线。

**教训**：
1. 即使是简单补丁也需要多轮审查
2. 积极响应审查意见
3. 提供示例如何使用你的代码
4. 添加正确的文档和 SAFETY 注释

## 7. 建立社区关系

### 7.1 沟通规范

| 场景 | 建议 |
|------|------|
| 首次发补丁 | 简短自我介绍 + 补丁 |
| 不同意审查意见 | 礼貌地解释技术理由 |
| 不确定怎么做 | 问！社区愿意帮助新人 |
| 犯错了 | 道歉并修复，不反复解释 |
| 被代码审查 blocking | 耐心讨论替代方案 |
| 长期贡献后 | 申请成为 reviewer/maintainer |

### 7.2 社区文化

内核社区的文化特点：
1. **技术优先**：好的技术论证比职位更有分量
2. **直接沟通**：会有直接的批评，但通常是关于代码而非个人
3. **高质量要求**：内核不能"差不多就行"，每个补丁都必须正确
4. **耐心**：社区尊重花时间理解系统的贡献者
5. **长期承诺**：理想情况下，你会在一个子系统上工作多年

### 7.3 参加活动和会议

| 活动 | 频率 | 描述 |
|------|------|------|
| Linux Plumbers Conference | 每年 | Rust for Linux 有专门的微会议 |
| Kernel Recipes | 每年 | 巴黎的年度内核会议 |
| Kangrejos | 每年 | Rust for Linux 的专属聚会 |
| FOSDEM | 每年 | 布鲁塞尔的开源会议 |

### 7.4 在线参与

- **Zulip**：`https://rust-for-linux.zulipchat.com` -- 实时讨论、提问
- **Lore**：`https://lore.kernel.org/rust-for-linux/` -- 邮件存档
- **GitHub**：`https://github.com/Rust-for-Linux/` -- 问题跟踪和 WIP 代码

## 8. 技能发展路线图

### 8.1 短期目标（1-3 个月）

- [ ] 完成一个文档补丁（修正错字、添加缺失文档）
- [ ] 在内核中编译并运行示例 Rust 模块
- [ ] 参与邮件列表讨论（即使是 Tested-by 回复）
- [ ] 阅读并理解至少 3 个已合并的 Rust 补丁
- [ ] 为某个简单的抽象添加单元测试

### 8.2 中期目标（3-12 个月）

- [ ] 实现一个新的简单抽象（如封装 kernel 的 list_head）
- [ ] 修复一个已报告的 bug
- [ ] 参加一次 Linux Plumbers Conference 或 Kangrejos
- [ ] 建立与至少一名维护者的工作关系
- [ ] 写至少一个树外的 Rust 内核驱动

### 8.3 长期目标（1-3 年）

- [ ] 成为特定子系统的 Rust 部分的核心贡献者
- [ ] 审查他人的补丁并提供建设性反馈
- [ ] 驱动一个新的 Rust 子系统（如网络、文件系统）
- [ ] 在内核会议上发言
- [ ] 成为 Rust for Linux 的 reviewer 或维护者

### 8.4 核心能力矩阵

```
初级贡献者：
  Rust            --------------- 80%
  C 阅读理解      ---------- 60%
  内核基础        ------ 40%
  社区流程        -- 20%

中级贡献者：
  Rust            --------------- 90%
  C 阅读理解      -------------- 80%
  内核基础        -------------- 80%
  社区流程        ---------- 60%
  子系统知识      -------------- 80%

高级贡献者：
  Rust            ---------------- 100%
  C 阅读理解      ---------------- 100%
  内核基础        --------------- 90%
  社区流程        ---------------- 100%
  子系统知识      ---------------- 100%
   审查能力        --------------- 90%
```

---

## [[04-内核驱动：Rust vs C对比]] | [[06-内核Rust未来展望]]

---

## 章节考查（100分）

**1. 选择题（20分，每题5分）**

**1.1** "Signed-off-by" 标签在补丁中的作用是什么？
<details>
<summary>答案</summary>
表示开发者认证该补丁的原创性（DCO -- Developer's Certificate of Origin），确认他们有权在开源许可下贡献该代码。
</details>

**1.2** 补丁中的 `PATCH v3` 前缀表示什么？
<details>
<summary>答案</summary>
表示这是该补丁的第三个版本（经过两轮审查和修改后重新发送），帮助审查者跟踪补丁的演化。
</details>

**1.3** 发送到 Rust for Linux 邮件列表的补丁，除该列表外通常还需要抄送哪个列表？
<details>
<summary>答案</summary>
`linux-kernel@vger.kernel.org`（通用内核开发列表），以及可能涉及的相关子系统维护者。
</details>

**1.4** 内核文档中使用 `// SAFETY:` 注释的作用是什么？
<details>
<summary>答案</summary>
解释为什么 `unsafe` 块中的操作是安全的，说明满足安全前提的理由。这是内核 Rust 代码的必要规范，帮助审查者核验不安全代码的正确性。
</details>

---

**2. 简答题（40分，每题10分）**

**2.1** 描述从选择任务到补丁合并的完整贡献流程（至少 8 个步骤）。

<details>
<summary>答案</summary>
1. 找到合适的问题（GitHub issues、LKML 邮件、内核 TODO 注释）
2. 在邮件列表声明意图（可选但推荐）
3. 创建分支并编写代码
4. 在 QEMU 或真实硬件上测试
5. 运行 rustfmt 和 checkpatch 格式化检查
6. 编写规范的提交信息（标题、正文、Signed-off-by）
7. 生成补丁文件并用 git send-email 发送
8. 接收审查反馈并回应
9. 修改代码、重写提交信息、发送新版本
10. 等待维护者合并到 rust-next 分支
11. 补丁通过 linux-next 集成测试
12. 在合并窗口中被 Linus 拉入主线
</details>

**2.2** 内核 Rust 编码规范禁止直接使用 `unwrap()` 和 `expect()`。请设计一套替代方案，用具体代码展示。

<details>
<summary>答案</summary>
替代方案：

```rust
// 禁止：可能 panic
// let val = some_option.unwrap();
// let val = some_result.expect("should not fail");

// 方案 1：使用 ? 运算符传播错误
let val = some_option.ok_or(Error::EINVAL)?;
let val = some_result?;

// 方案 2：提供合理的默认值
let val = some_option.unwrap_or(default_value);

// 方案 3：使用 if let 处理
if let Some(val) = some_option {
    // 使用 val
} else {
    return Err(Error::EINVAL);
}

// 方案 4：对于确实不可能失败的情况
match some_option {
    Some(val) => { /* 使用 */ }
    None => {
        // SAFETY: 这里不可达，因为[具体原因]
        unsafe { core::hint::unreachable_unchecked() }
    }
}
```

关键原则：永远给调用者一个错误路径，而不是直接崩溃内核。
</details>

**2.3** 讨论"补丁拆分"的策略。如果一个任务需要修改多个地方，什么时候应该拆分为多个补丁？

<details>
<summary>答案</summary>
**应该拆分为多个补丁的情况**：
1. 逻辑上独立的变更：如同时修复 bug 和添加文档
2. 跨越多个子系统：同时修改 rust/kernel/ 和 drivers/gpu/
3. 渐进式添加：先添加底层抽象，再添加使用该抽象的驱动
4. 一个补丁做一件事：这是内核补丁的铁律

**应该保持单一补丁的情况**：
1. 紧密耦合：如果 B 不能独立于 A 存在
2. API 变更 + 所有使用点：修改 API 签名并更新所有调用点

**验证方法**：
- 如果补丁描述需要用"and"连接多个不相关的事情 -> 拆分
- 如果补丁的某一部分可以独立 revert -> 拆分
- 如果审查者对补丁的不同部分可能有不同意见 -> 拆分
</details>

**2.4** 如何处理审查者拒绝了你的设计（"NAK"）？请描述适当的应对策略。

<details>
<summary>答案</summary>
1. **不要防御性反应**：NAK 是关于代码而非个人，深呼吸，冷静分析
2. **理解拒绝原因**：技术问题？方法冲突？架构冲突？
3. **适当的回应**："感谢你的反馈。我理解了你的顾虑。让我重新设计并发送新的 RFC。"
4. **不要反复争论**：用新的证据支持观点，不要重复同样论点
5. **寻求共识**：询问是否有中间方案
6. **接受并重新开始**：如果维护者确实正确，设计更好的方案
7. **绝对不要做**：在邮件列表抱怨、在社交媒体批评审查者、发送重复补丁刷屏
</details>

---

**3. 论述题（40分，每题20分）**

**3.1** 假设你是一个中级 Rust 开发者，计划在 6 个月内从"零内核贡献"成长为"Rust for Linux 的常规贡献者"。请制定一个详细的 6 个月计划，包含每月目标、具体任务和里程碑。

<details>
<summary>答案</summary>
**第 1 个月：环境+基础**
- 搭建开发环境（内核源码 + rustc + QEMU）
- 编译并启动自己的内核，加载/卸载示例模块
- 订阅 rust-for-linux 邮件列表和 Zulip
- 阅读 Documentation/rust/ 下的所有文档
- 阅读 rust/kernel/prelude.rs 和 error.rs（理解基础类型）
- 找到 1-2 个文档错误并提交修复补丁
- 里程碑：第一个文档补丁被合并

**第 2 个月：理解抽象层**
- 阅读 rust/kernel/sync/arc.rs 和 lock.rs
- 理解 Arc 和 Mutex 如何封装 C 内核 API
- 写一个简单的树外内核模块（字符设备）
- 为现有抽象添加 1-2 个单元测试
- 里程碑：单元测试补丁被合并

**第 3 个月：第一个有意义的抽象**
- 选择一个简单的 C 内核 API（如 wait_queue, completion）
- 设计 Rust 抽象，实现并在 QEMU 中测试
- 发送到邮件列表并回应审查反馈
- 里程碑：第一个抽象补丁被审查

**第 4 个月：深入子系统**
- 选择一个子系统：块层、GPU、网络或输入
- 阅读该子系统在 C 中的实现（至少 500 行核心代码）
- 尝试写一个简单的 Rust 驱动
- 里程碑：完成一个 Rust 驱动的初版

**第 5 个月：修复一个真实 bug**
- 在内核 bugzilla 或 syzbot 报告中找到 Rust 相关 bug
- 复现、分析根因、实现修复
- 里程碑：bug 修复补丁被合并

**第 6 个月：成为常规贡献者**
- 确定自己的专长领域
- 开始审查他人的简单补丁
- 至少发出 2 个新补丁
- 里程碑：收到维护者的 "Reviewed-by" 在至少 5 个补丁上
</details>

**3.2** 内核社区有时被认为对新人不友好。请基于你的理解，分析这种现象的原因，并提出你作为新人如何成功融入的策略。

<details>
<summary>答案</summary>
**现象分析**：

内核社区以高标准和直接沟通著称，原因包括：
1. **质量标准极高**：内核运行在数十亿设备上，维护者有责任严格把关
2. **沟通风格直接**：社区以"效率优先"为文化，直接批评是技术交流效率习惯
3. **隐性知识丰富**：有很多不成文的规则，新手可能因未遵循而受挫
4. **审查资源有限**：维护者处理数百个补丁，无法给每个人详尽解释
5. **历史包袱**：过去有不认真的贡献者浪费维护者时间

**融入策略**：
1. **极小的第一步**：从最简单的补丁开始（修错字、格式修正），证明基础能力
2. **预先做好功课**：阅读 Documentation/process/，观察邮件列表交流模式
3. **以学习者姿态**：收到严厉反馈时问"你能帮我理解为什么这种方案不好吗"
4. **证明你的认真**：测试充分，补丁描述完整，真正按反馈修改代码
5. **建立信誉**：5 个高质量小补丁 > 1 个匆忙的大补丁
6. **使用辅助渠道**：Zulip 聊天室比邮件列表更宽松
7. **理解"不友好"的正面意义**：高标准保护数十亿用户，包括你

Rust for Linux 子社区以相对友好著称，许多维护者积极鼓励新人。
</details>

---

## 本章小结

本章提供了参与内核 Rust 开发的完整指南，从自我评估到补丁合并的每一步。

**关键要点**：
- 内核开发有显著的学习曲线，但回报巨大
- 从文档改进或单元测试等小任务开始
- 遵循严格的补丁格式和提交规范
- 积极回应审查反馈，保持耐心
- 内核社区重视技术能力和长期承诺
- Rust for Linux 是一个相对友好和活跃的子社区
- 参与这个项目意味着参与操作系统的历史性变革

**行动号召**：
1. 今天就订阅 `rust-for-linux@vger.kernel.org`
2. 在 `git.kernel.org` 上克隆内核源码
3. 在内核中搜索 `TODO` 注释
4. 发送你的第一个补丁

**你不需要成为专家就能开始 -- 你只需要开始才能成为专家。**
