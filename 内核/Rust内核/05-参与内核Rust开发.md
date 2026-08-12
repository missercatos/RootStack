# 参与内核 Rust 开发

## 1. 前提知识

| 领域 | 具体要求 |
|------|---------|
| Rust | 所有权、借用、生命周期、trait、泛型、unsafe 边界 |
| C | 能阅读和理解 C 内核代码 |
| Linux 内核基础 | 模块、设备模型、内存管理、中断、锁、sysfs |
| Git | 分支、format-patch、send-email、变基 |

日常参见 [[../系统内核/07_Linux内核源码导读|Linux内核源码导读]] 了解内核源码结构和编码规范。

## 2. 寻找任务

### 入门任务类型

| 任务 | 难度 | 示例 |
|------|------|------|
| 文档改进 | 1星 | 修复语法错误、添加缺失文档 |
| 警告修复 | 2星 | 修复 clippy 或编译警告 |
| 测试添加 | 2星 | 为现有抽象添加 kunit 测试 |
| 简单抽象 | 3星 | 封装简单的 C API（如 kmem_cache） |
| 示例模块 | 2星 | 创建新的 samples/rust/ 示例 |

### 任务来源

1. 邮件列表 `rust-for-linux@vger.kernel.org`
2. GitHub Issues: `https://github.com/Rust-for-Linux/linux/issues`，筛选 "good first issue"
3. 内核源码内的 TODO 注释:
```bash
grep -rn "TODO\|FIXME\|XXX" rust/ samples/rust/
```
4. lore.kernel.org 搜索 "RFC"、"WIP"、"needs review"

### 具体入门项目

| 项目 | 预计时间 | 技能收益 |
|------|---------|---------|
| 改善 rust/kernel/str.rs 文档 | 4-8h | 学习 CStr API |
| 为 Mutex<T> 添加单元测试 | 8-16h | 理解同步抽象 |
| 实现 WARN_ON 宏的 Rust 等效 | 8-12h | 宏开发、打印 API |
| 为 platform::Device 添加方法 | 16-24h | 平台设备抽象 |

## 3. 贡献工作流

```
[1] 订阅邮件列表
[2] 克隆开发仓库
[3] 寻找/选择任务
[4] 在邮件列表声明意图（大任务建议）
[5] 编写代码 & 测试
[6] 格式化 & 检查
[7] 编写提交信息
[8] 生成补丁
[9] 发送到邮件列表
[10] 处理审查反馈（重复 5-10 直到接受）
[11] 补丁被合并
```

### 环境准备

```bash
git clone https://github.com/Rust-for-Linux/linux.git rust-dev
cd rust-dev
git remote add torvalds https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
git fetch torvalds
git checkout -b my-rust-contribution torvalds/master
make LLVM=1 rustavailable # 确认工具链就绪
make LLVM=1 defconfig
scripts/config --enable CONFIG_RUST
make LLVM=1 olddefconfig
```

## 4. 编码规范

```rust
// 1. 使用内核错误码
fn my_func() -> Result<u32> { Err(Error::EINVAL) } // 正确

// 2. 避免 unwrap/expect
let val = option.ok_or(Error::EINVAL)?; // 正确

// 3. SAFETY 注释解释安全前提
// SAFETY: ptr is valid because the Arc reference ensures
// the allocation is not freed while this reference exists.
unsafe { (*ptr).field = value; }

// 4. 使用 kernel::prelude::* 导入常用项
use kernel::prelude::*;

// 5. 文档包含安全性说明
/// Reads a 32-bit value from MMIO at the given offset.
///
/// # Errors
/// Returns ERANGE if the offset is out of bounds.
fn read32(&self, offset: usize) -> Result<u32>;
```

编译和检查：
```bash
make LLVM=1 -j$(nproc) # 构建内核
make LLVM=1 -j$(nproc) modules # 构建模块
make LLVM=1 CLIPPY=1 # clippy 检查
make LLVM=1 rustfmt # 格式化
```

## 5. 提交信息格式

内核提交信息严格格式：

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

规则：首行不超过 50 字符无句号；正文 72 字符/行；Signed-off-by 通过 `git commit -s` 添加。

## 6. 发送补丁

```bash
# 生成补丁
git format-patch -1 HEAD

# 检查补丁
scripts/checkpatch.pl 0001-*.patch

# 发送
git send-email \
 --to="rust-for-linux@vger.kernel.org" \
 --cc="linux-kernel@vger.kernel.org" \
 --cc="Miguel Ojeda <ojeda@kernel.org>" \
 0001-*.patch
```

补丁系列（多个相关提交）：
```bash
git format-patch -3 --cover-letter # 生成封面信
vim 0000-cover-letter.patch
git send-email --to="..." 0000-*.patch
```

发送前检查清单：
- 基于最新主线
- 通过 checkpatch
- 编译无警告
- 提交信息格式正确
- Signed-off-by 正确

## 7. 处理审查反馈

修改后重新发送：
```bash
git rebase -i HEAD~1
# 在提交信息中添加变更日志：
# ---
# Changes in v2:
# - Fixed lock ordering as suggested by Reviewer
# - Added missing SAFETY comment
# - Link to v1: https://lore.kernel.org/.../msg12345.html

git format-patch -1 HEAD --subject-prefix="PATCH v2"
```

| 审查反馈 | 应对 |
|----------|------|
| "Please add a SAFETY comment" | 添加 // SAFETY: 注释 |
| "NIT: s/funtion/function/" | 修复 |
| "Why not use ...?" | 解释或采纳 |
| "Doesn't follow kernel style" | 参考现有代码修改 |
| "Please split this patch" | 拆分为多个补丁 |
| "Needs more testing" | 添加测试 |
| "NAK" | 理解原因，重新设计 |

## 8. 审查流程

维护者（截至 2025）：Miguel Ojeda（主维护者）、Alex Gaynor、Wedson Almeida Filho、Boqun Feng、Gary Guo、Bjorn Roy Baron、Andreas Hindborg、Alice Ryhl。

典型时间：首次审查反馈 1-7 天；修改后反馈 3-10 天；简单补丁合并 2-8 周；复杂补丁 2-6 个月。

## 9. 技能发展路线

**短期（1-3个月）**：完成文档补丁 → 编译运行示例模块 → 参与邮件列表 → 阅读已合并的 Rust 补丁。

**中期（3-12个月）**：实现简单的内核抽象 → 修复已报告的 bug → 参加 Linux Plumbers Conference 或 Kangrejos → 建立与维护者的工作关系。

**长期（1-3年）**：成为子系统 Rust 核心贡献者 → 审查他人补丁 → 驱动新的 Rust 子系统 → 成为 reviewer 或 maintainer。

## 10. 社区文化

- 技术优先：好的技术论证比职位更有分量
- 直接沟通：直接批评但针对代码非个人
- 高质量要求：每个补丁必须正确
- 耐心：尊重花时间理解系统的贡献者
- 长期承诺：理想情况下在一个子系统上工作多年

在线参与：Zulip (`rust-for-linux.zulipchat.com`) 实时讨论；Lore (`lore.kernel.org/rust-for-linux/`) 邮件存档。
