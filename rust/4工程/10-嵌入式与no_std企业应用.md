# 嵌入式与no_std企业应用

## 原理

嵌入式 Rust 的核心工具链：

**`#![no_std]`**：移除标准库依赖（`std`）使用核心库（`core`）。`core` 提供基本类型、`Option`/`Result`、迭代器但不含任何 OS 依赖（如文件、网络、线程、动态分配）。

**`#[panic_handler]`**：用户必须定义 panic 行为（通常是 `loop {}` 禁止继续执行或 `cortex_m::peripheral::SCB::sys_reset()` 重置）。

**`alloc` crate**：需要动态内存时可通过 `extern crate alloc` 引入 `Vec`、`Box`、`String` 等，但需提供全局分配器（`#[global_allocator]`）。

**`embedded_hal`**：硬件抽象层，定义 SPI、I2C、GPIO、PWM、ADC 等标准接口。同一 API 可在不同 MCU 上运行（如 stm32、nrf、esp32）。

**编译目标**：`thumbv7em-none-eabi` (ARM Cortex-M4), `riscv32imac-unknown-none-elf` (RISC-V)，使用 `cargo build --target <triple>` 交叉编译。

[[../../red_team/archstrike-exploit教学/03-路由器与IoT漏洞利用|安全: 固件安全]]

---

## 语法

```rust
#![no_std]
#![no_main]

use panic_halt as _; // panic = 停止 CPU

#[cortex_m_rt::entry]
fn main() -> ! {
 let peripherals = stm32f4::Peripherals::take().unwrap();

 // GPIO 配置
 let gpioc = peripherals.GPIOC;
 let rcc = peripherals.RCC;

 // ... 点亮 LED ...

 loop {
 // 主循环
 }
}
```

```toml
# Cargo.toml for embedded
[dependencies]
cortex-m = "0.7"
cortex-m-rt = "0.7"
panic-halt = "0.2"
embedded-hal = "1.0"
```

### 常见嵌入式目标

| 目标 triple | 架构 | 典型 MCU |
|-------------|------|----------|
| `thumbv7em-none-eabihf` | ARM Cortex-M4F | STM32F4 |
| `thumbv6m-none-eabi` | ARM Cortex-M0+ | RP2040 (Raspberry Pi Pico) |
| `riscv32imac-unknown-none-elf` | RISC-V | ESP32-C3 |
| `xtensa-esp32-espidf` | Xtensa | ESP32 |

---

## 实践

### AI 自检

1. `no_std` 环境下 `format!` 宏仍可用吗？`core::fmt` 与 `std::fmt` 的关系？
2. 嵌入式 `.elf` 文件如何 flashing 到 MCU？`probe-rs` 的工作流程是什么？
