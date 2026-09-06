# no_std

## 

 Rust 

**`#![no_std]`**`std``core``core` `Option`/`Result` OS 

**`#[panic_handler]`** panic  `loop {}`  `cortex_m::peripheral::SCB::sys_reset()` 

**`alloc` crate** `extern crate alloc`  `Vec``Box``String` `#[global_allocator]`

**`embedded_hal`** SPII2CGPIOPWMADC  API  MCU  stm32nrfesp32

****`thumbv7em-none-eabi` (ARM Cortex-M4), `riscv32imac-unknown-none-elf` (RISC-V) `cargo build --target <triple>` 

[[../../red_team/archstrike-exploit/03-IoT|: ]]

---

## 

```rust
#![no_std]
#![no_main]

use panic_halt as _; // panic =  CPU

#[cortex_m_rt::entry]
fn main() -> ! {
 let peripherals = stm32f4::Peripherals::take().unwrap();

 // GPIO 
 let gpioc = peripherals.GPIOC;
 let rcc = peripherals.RCC;

 // ...  LED ...

 loop {
 // 
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

### 

|  triple |  |  MCU |
|-------------|------|----------|
| `thumbv7em-none-eabihf` | ARM Cortex-M4F | STM32F4 |
| `thumbv6m-none-eabi` | ARM Cortex-M0+ | RP2040 (Raspberry Pi Pico) |
| `riscv32imac-unknown-none-elf` | RISC-V | ESP32-C3 |
| `xtensa-esp32-espidf` | Xtensa | ESP32 |

---

## 
