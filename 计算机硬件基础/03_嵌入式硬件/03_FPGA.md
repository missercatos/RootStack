# FPGA（现场可编程门阵列）

> FPGA 是可以通过编程改变硬件电路结构的芯片——同一块 FPGA 可以配置为 CPU、DSP、加密引擎或任何数字电路。适合需要硬件并行加速的场景。

---

## FPGA 厂商

| 厂商 | 产品线 | 市场份额 | 生态 |
|------|--------|:--------:|------|
| AMD (Xilinx) | Artix / Kintex / Versal | 约 50% | Vivado/Quartus |
| Intel (Altera) | Cyclone / Stratix / Agilex | 约 30% | Quartus Prime |
| Lattice | iCE40 / ECP5 / CrossLink | 低功耗市场 | Diamond/Yosys |
| Microchip | PolarFire / IGLOO | 内航天/军工 | Libero |

---

## AMD (Xilinx) FPGA

### 按等级分类

| 系列 | 逻辑单元 | 收发器 | 适用 | 参考价 |
|------|:--------:|:------:|------|:------:|
| Artix-7 | 15K-215K | 无 | 低成本/学习 | 50-500 |
| Kintex-7 | 190K-480K | 28G | 中端通信/视频 | 500-5000 |
| Artix UltraScale+ | 150K-500K | 16G | 高性能+低成本 | 300-2000 |
| Kintex UltraScale+ | 300K-1700K | 32G | 高端通信/雷达 | 2000-20000 |
| Versal | 自适应 SoC | 100G | AI/数据中心 | 10000+ |

---

## Intel (Altera) FPGA

| 系列 | 逻辑单元 | 收发器 | 适用 | 参考价 |
|------|:--------:|:------:|------|:------:|
| Cyclone V | 25K-300K | 5G | 低成本/嵌入式 | 50-500 |
| Cyclone 10 | 50K-200K | 10G | 中端 | 100-1000 |
| Stratix 10 | 500K-2800K | 28G | 高端通信/HPC | 3000-30000 |
| Agilex | 自适应 SoC | 112G | 数据中心 | 10000+ |

---

## FPGA 开发板

| 开发板 | 芯片 | 逻辑单元 | 价格 | 适用 |
|--------|:----:|:--------:|:----:|------|
| 正点原子 达芬奇 | Artix-7 35T | 33K | 300 | 入门学习 |
| 野火 天启 | Artix-7 200T | 215K | 500 | 进阶开发 |
| Digilent Arty A7 | Artix-7 35T | 33K | 150 | 官方入门 |
| Terasic DE10-Lite | MAX 10 | 10K | 500 | Intel 入门 |
| Xilinx KCU105 | Kintex UltraScale | 455K | 3000 | 官方评估 |

---

## FPGA vs MCU vs GPU

| 维度 | FPGA | MCU | GPU |
|------|:----:|:---:|:---:|
| 并行度 | 硬件并行（定制电路） | 软件串行 | 大规模并行 |
| 灵活性 | 极高（可重配置） | 中（固定外设） | 低（固定架构） |
| 功耗 | 中 | 极低 | 高 |
| 开发难度 | 高（Verilog/VHDL） | 低（C 语言） | 中（CUDA） |
| 适用 | 定制硬件加速 | 通用控制 | 图形/矩阵计算 |
| 单位成本 | 量产后低 | 极低 | 高 |
| 开发周期 | 长 | 短 | 中 |

---

## 选型建议

| 用途 | 推荐 | 说明 |
|------|------|------|
| 入门学习 | Artix-7 35T | 资源够用，价格便宜 |
| 视频处理 | Artix-7 200T / Kintex-7 | 高速串行收发器 |
| 通信基站 | Kintex UltraScale | 高速 ADC/DAC 接口 |
| 加密加速 | Artix-7 / MAX 10 | 并行 AES/RSA |
| 原型验证 | Versal / Agilex | 高端 SoC |
| 量产后 | iCE40 / MAX V | 极低成本 |
