# MCU（微控制器）

> MCU 是将 CPU、RAM、Flash、外设接口集成在一颗芯片上的微型计算机。嵌入式系统的核心就是 MCU。

---

## STM32 全系列（2024-2026）

### 按性能分级

| 系列 | 内核 | 频率 | RAM | Flash | 适用 |
|------|:----:|:----:|:---:|:-----:|------|
| F0 | Cortex-M0 | 48MHz | 8-32KB | 16-256KB | 极低成本 |
| F1 | Cortex-M3 | 72MHz | 20-64KB | 64-512KB | 入门经典 |
| F4 | Cortex-M4 | 168MHz | 192KB-1MB | 512KB-2MB | 主流高性能 |
| G4 | Cortex-M4 | 170MHz | 128KB | 512KB | 电机控制 |
| H5 | Cortex-M33 | 250MHz | 512KB | 2MB | 新一代主流 |
| H7 | Cortex-M7 | 480MHz | 1MB | 2MB | 最高性能 |
| L0 | Cortex-M0+ | 32MHz | 8KB | 32KB | 超低功耗 |
| L4 | Cortex-M4 | 80MHz | 128KB | 1MB | 低功耗+性能 |

### 型号命名规则

以 **STM32F407VET6** 为例：

| 字段 | 含义 |
|------|------|
| STM32 | 产品系列 |
| F | 产品线（F=主流, L=低功耗, G=通用, H=高性能） |
| 4 | 内核（4=Cortex-M4, 7=Cortex-M7, 0=Cortex-M0） |
| 07 | 具体型号 |
| V | 引脚数（V=100pin, C=48pin, R=64pin, Z=144pin） |
| E | Flash 容量（E=512KB, H=1MB, I=2MB） |
| T | 封装（T=LQFP） |
| 6 | 温度范围（6=-40~85C） |

### 常用开发板

| 开发板 | 芯片 | 价格 | 适用 |
|--------|:----:|:----:|------|
| Nucleo-64 | STM32F401RE | 100 | 官方评估板 |
| STM32F4 Discovery | STM32F407VG | 150 | 官方开发板 |
| 正点原子 F407 | STM32F407ZET6 | 80 | 国内教学 |
| 野火 F429 | STM32F429IGT6 | 120 | 国内教学 |

---

## ESP32 系列详解

| 型号 | 内核 | 频率 | RAM | Flash | WiFi | 蓝牙 | 特色 | 价格 |
|------|:----:|:----:|:---:|:-----:|:----:|:----:|------|:----:|
| ESP32 | Xtensa 双核 | 240MHz | 520KB | 4MB | 2.4GHz | 4.2 | 经典款 | 20 |
| ESP32-S2 | Xtensa 单核 | 240MHz | 320KB | 4MB | 2.4GHz | 无 | USB OTG | 18 |
| ESP32-S3 | Xtensa 双核 | 240MHz | 512KB | 8MB | 2.4GHz | 5.0 | AI 加速 | 25 |
| ESP32-C3 | RISC-V 单核 | 160MHz | 400KB | 4MB | 2.4GHz | 5.0 | 低成本 | 15 |
| ESP32-C6 | RISC-V | 160MHz | 512KB | 4MB | WiFi 6 | 5.0 | 新一代 | 18 |

---

## 选型要点

| 需求 | 推荐 | 说明 |
|------|------|------|
| 最低成本 | ESP32-C3 / STM32F0 | <20 元 |
| GPIO 最多 | STM32H7 / STM32F4 | 100-176 pin |
| 最低功耗 | STM32L0 / ESP32-C3 | 睡眠模式 uA 级 |
| 最高性能 | STM32H7 / ESP32-S3 | 480MHz / 240MHz |
| 自带 WiFi | ESP32 系列 | 开发最快 |
| 工业认证 | STM32 系列 | 宽温/车规可选 |
