# GPU 芯片级型号速查

> 本章列出 GPU 芯片的**硅片代号、修订版、CUDA/流处理器数、显存位宽、制程**——即芯片设计层面的标识。

---

## NVIDIA GPU 芯片代号

### Blackwell 架构（2025, TSMC 4nm）

| 芯片代号 | 零售产品 | SM 数 | CUDA 核心 | 显存位宽 | 显存 | TDP |
|---------|---------|:-----:|:---------:|:--------:|------|:---:|
| GB202 | RTX 5090 | 170 | 21760 | 512-bit | 32GB GDDR7 | 575W |
| GB202-300 | RTX 5080 | 84 | 10752 | 256-bit | 16GB GDDR7 | 360W |
| GB203 | RTX 5070 Ti | 70 | 8960 | 256-bit | 16GB GDDR7 | 300W |
| GB205 | RTX 5070 | 48 | 6144 | 192-bit | 12GB GDDR7 | 250W |
| GB206 | RTX 5060 Ti | 36 | 4608 | 128-bit | 16GB GDDR7 | 180W |
| GB206 | RTX 5060 | 24 | 3072 | 128-bit | 8GB GDDR7 | 150W |

### Ada Lovelace 架构（2022, TSMC 4nm）

| 芯片代号 | 零售产品 | SM 数 | CUDA 核心 | 显存位宽 | 显存 | TDP |
|---------|---------|:-----:|:---------:|:--------:|------|:---:|
| AD102 | RTX 4090 | 128 | 16384 | 384-bit | 24GB GDDR6X | 450W |
| AD102-301 | RTX 4090 D | 128 | 16384 | 384-bit | 24GB GDDR6X | 425W |
| AD103 | RTX 4080 Super | 80 | 10240 | 256-bit | 16GB GDDR6X | 320W |
| AD103 | RTX 4080 | 76 | 9728 | 256-bit | 16GB GDDR6X | 320W |
| AD104 | RTX 4070 Ti Super | 66 | 8448 | 256-bit | 16GB GDDR6X | 285W |
| AD104 | RTX 4070 Ti | 60 | 7680 | 192-bit | 12GB GDDR6X | 285W |
| AD104 | RTX 4070 | 46 | 5888 | 192-bit | 12GB GDDR6X | 200W |
| AD106 | RTX 4060 Ti 16GB | 34 | 4352 | 128-bit | 16GB GDDR6 | 165W |
| AD106 | RTX 4060 Ti 8GB | 34 | 4352 | 128-bit | 8GB GDDR6 | 160W |
| AD107 | RTX 4060 | 24 | 3072 | 128-bit | 8GB GDDR6 | 115W |

### Ampere 架构（2020, Samsung 8nm）

| 芯片代号 | 零售产品 | SM 数 | CUDA 核心 | 显存位宽 | 显存 | TDP |
|---------|---------|:-----:|:---------:|:--------:|------|:---:|
| GA102 | RTX 3090 Ti | 84 | 10752 | 384-bit | 24GB GDDR6X | 450W |
| GA102 | RTX 3090 | 82 | 10496 | 384-bit | 24GB GDDR6X | 350W |
| GA102 | RTX 3080 Ti | 80 | 10240 | 384-bit | 12GB GDDR6X | 350W |
| GA102 | RTX 3080 12GB | 70 | 8960 | 384-bit | 12GB GDDR6X | 350W |
| GA102 | RTX 3080 10GB | 68 | 8704 | 320-bit | 10GB GDDR6X | 320W |
| GA104 | RTX 3070 Ti | 48 | 6144 | 256-bit | 8GB GDDR6X | 290W |
| GA104 | RTX 3070 | 46 | 5888 | 256-bit | 8GB GDDR6 | 220W |
| GA106 | RTX 3060 Ti | 38 | 4864 | 256-bit | 8GB GDDR6 | 200W |
| GA106 | RTX 3060 12GB | 28 | 3584 | 192-bit | 12GB GDDR6 | 170W |
| GA106 | RTX 3060 8GB | 28 | 3584 | 128-bit | 8GB GDDR6 | 170W |
| GA107 | RTX 3050 8GB | 20 | 2560 | 128-bit | 8GB GDDR6 | 130W |
| GA107 | RTX 3050 6GB | 16 | 2048 | 96-bit | 6GB GDDR6 | 70W |

### Turing 架构（2018, TSMC 12nm）

| 芯片代号 | 零售产品 | SM 数 | CUDA 核心 | 显存位宽 | 显存 | TDP |
|---------|---------|:-----:|:---------:|:--------:|------|:---:|
| TU102 | RTX 2080 Ti | 68 | 4352 | 352-bit | 11GB GDDR6 | 250W |
| TU102 | Titan RTX | 72 | 4608 | 384-bit | 24GB GDDR6 | 280W |
| TU104 | RTX 2080 Super | 48 | 3072 | 256-bit | 8GB GDDR6 | 250W |
| TU104 | RTX 2080 | 46 | 2944 | 256-bit | 8GB GDDR6 | 215W |
| TU104 | RTX 2070 Super | 40 | 2560 | 256-bit | 8GB GDDR6 | 215W |
| TU106 | RTX 2070 | 36 | 2304 | 256-bit | 8GB GDDR6 | 175W |
| TU106 | RTX 2060 Super | 34 | 2176 | 256-bit | 8GB GDDR6 | 175W |
| TU106 | RTX 2060 12GB | 34 | 2176 | 192-bit | 12GB GDDR6 | 160W |
| TU106 | RTX 2060 6GB | 30 | 1920 | 192-bit | 6GB GDDR6 | 160W |
| TU117 | GTX 1660 Ti | 24 | 1536 | 192-bit | 6GB GDDR6 | 120W |
| TU116 | GTX 1660 Super | 22 | 1408 | 192-bit | 6GB GDDR6 | 125W |
| TU116 | GTX 1660 | 22 | 1408 | 192-bit | 6GB GDDR5 | 120W |
| TU116 | GTX 1650 Super | 20 | 1280 | 128-bit | 4GB GDDR6 | 100W |
| TU117 | GTX 1650 | 14 | 896 | 128-bit | 4GB GDDR5/GDDR6 | 75W |
| TU117 | GTX 1630 | 8 | 512 | 64-bit | 4GB GDDR6 | 75W |

### Pascal 架构（2016, TSMC 16nm）

| 芯片代号 | 零售产品 | SM 数 | CUDA 核心 | 显存位宽 | 显存 | TDP |
|---------|---------|:-----:|:---------:|:--------:|------|:---:|
| GP102 | Titan Xp | 60 | 3840 | 384-bit | 12GB GDDR5X | 250W |
| GP102 | GTX 1080 Ti | 28 | 3584 | 352-bit | 11GB GDDR5X | 250W |
| GP102 | GTX 1070 Ti | 19 | 2432 | 256-bit | 8GB GDDR5 | 180W |
| GP104 | GTX 1080 | 20 | 2560 | 256-bit | 8GB GDDR5X | 180W |
| GP104 | GTX 1070 | 15 | 1920 | 256-bit | 8GB GDDR5 | 150W |
| GP106 | GTX 1060 6GB | 10 | 1280 | 192-bit | 6GB GDDR5 | 120W |
| GP106 | GTX 1060 3GB | 9 | 1152 | 192-bit | 3GB GDDR5 | 120W |
| GP107 | GTX 1050 Ti | 6 | 768 | 128-bit | 4GB GDDR5 | 75W |
| GP107 | GTX 1050 | 4 | 640 | 128-bit | 2GB GDDR5 | 75W |
| GP108 | GT 1030 | 3 | 384 | 64-bit | 2GB GDDR5 | 30W |

### Maxwell 架构（2014, TSMC 28nm）

| 芯片代号 | 零售产品 | SM 数 | CUDA 核心 | 显存位宽 | 显存 | TDP |
|---------|---------|:-----:|:---------:|:--------:|------|:---:|
| GM200 | GTX Titan X | 24 | 3072 | 384-bit | 12GB GDDR5 | 250W |
| GM200 | GTX 980 Ti | 22 | 2816 | 384-bit | 6GB GDDR5 | 250W |
| GM204 | GTX 980 | 16 | 2048 | 256-bit | 4GB GDDR5 | 165W |
| GM204 | GTX 970 | 13 | 1664 | 224+32-bit | 4GB GDDR5 | 145W |
| GM206 | GTX 960 | 8 | 1024 | 128-bit | 2GB GDDR5 | 120W |
| GM206 | GTX 950 | 6 | 768 | 128-bit | 2GB GDDR5 | 90W |
| GM107 | GTX 750 Ti | 5 | 640 | 128-bit | 2GB GDDR5 | 60W |
| GM107 | GTX 750 | 4 | 512 | 128-bit | 1-2GB GDDR5 | 55W |

### Kepler 架构（2012, TSMC 28nm）

| 芯片代号 | 零售产品 | SM 数 | CUDA 核心 | 显存位宽 | 显存 | TDP |
|---------|---------|:-----:|:---------:|:--------:|------|:---:|
| GK110B | GTX Titan Black | 15 | 2880 | 384-bit | 6GB GDDR5 | 250W |
| GK110B | GTX 780 Ti | 15 | 2880 | 384-bit | 3GB GDDR5 | 250W |
| GK110 | GTX Titan | 14 | 2688 | 384-bit | 6GB GDDR5 | 250W |
| GK110 | GTX 780 | 12 | 2304 | 384-bit | 3GB GDDR5 | 250W |
| GK104 | GTX 770 | 8 | 1536 | 256-bit | 2GB GDDR5 | 230W |
| GK104 | GTX 760 | 6 | 1152 | 256-bit | 2GB GDDR5 | 170W |
| GK104 | GTX 680 | 8 | 1536 | 256-bit | 2GB GDDR5 | 195W |
| GK104 | GTX 670 | 7 | 1344 | 256-bit | 2GB GDDR5 | 170W |
| GK106 | GTX 660 | 5 | 960 | 192-bit | 2GB GDDR5 | 140W |
| GK107 | GTX 650 | 2 | 384 | 128-bit | 1-2GB GDDR5 | 64W |
| GK107 | GT 640 | 2 | 384 | 128-bit | 1-2GB DDR3 | 65W |

---

## AMD GPU 芯片代号

### RDNA 3 架构（2022, TSMC 5nm/6nm）

| 芯片代号 | 零售产品 | CU 数 | 流处理器 | 显存位宽 | 显存 | TDP |
|---------|---------|:-----:|:--------:|:--------:|------|:---:|
| Navi 31 XTX | RX 7900 XTX | 96 | 6144 | 384-bit | 24GB GDDR6 | 355W |
| Navi 31 XT | RX 7900 XT | 84 | 5376 | 320-bit | 20GB GDDR6 | 315W |
| Navi 31 XL | RX 7900 GRE | 60 | 3840 | 256-bit | 16GB GDDR6 | 260W |
| Navi 32 XT | RX 7800 XT | 60 | 3840 | 256-bit | 16GB GDDR6 | 263W |
| Navi 32 XL | RX 7700 XT | 54 | 3456 | 192-bit | 12GB GDDR6 | 245W |
| Navi 33 XT | RX 7600 | 32 | 2048 | 128-bit | 8GB GDDR6 | 150W |

### RDNA 2 架构（2020, TSMC 7nm）

| 芯片代号 | 零售产品 | CU 数 | 流处理器 | 显存位宽 | 显存 | TDP |
|---------|---------|:-----:|:--------:|:--------:|------|:---:|
| Navi 21 XTX | RX 6950 XT | 80 | 5120 | 256-bit | 16GB GDDR6 | 335W |
| Navi 21 XT | RX 6900 XT | 80 | 5120 | 256-bit | 16GB GDDR6 | 300W |
| Navi 21 XL | RX 6800 XT | 72 | 4608 | 256-bit | 16GB GDDR6 | 300W |
| Navi 21 GL | RX 6800 | 60 | 3840 | 256-bit | 16GB GDDR6 | 250W |
| Navi 22 XT | RX 6750 XT | 40 | 2560 | 192-bit | 12GB GDDR6 | 250W |
| Navi 22 XT | RX 6700 XT | 40 | 2560 | 192-bit | 12GB GDDR6 | 230W |
| Navi 23 XT | RX 6650 XT | 32 | 2048 | 128-bit | 8GB GDDR6 | 180W |
| Navi 23 XT | RX 6600 XT | 32 | 2048 | 128-bit | 8GB GDDR6 | 160W |
| Navi 23 XL | RX 6600 | 28 | 1792 | 128-bit | 8GB GDDR6 | 132W |
| Navi 24 XT | RX 6500 XT | 16 | 1024 | 64-bit | 4GB GDDR6 | 107W |

### RDNA 1 架构（2019, TSMC 7nm）

| 芯片代号 | 零售产品 | CU 数 | 流处理器 | 显存位宽 | 显存 | TDP |
|---------|---------|:-----:|:--------:|:--------:|------|:---:|
| Navi 10 XT | RX 5700 XT | 40 | 2560 | 256-bit | 8GB GDDR6 | 225W |
| Navi 10 XL | RX 5700 | 36 | 2304 | 256-bit | 8GB GDDR6 | 180W |
| Navi 10 XL | RX 5600 XT | 36 | 2304 | 192-bit | 6GB GDDR6 | 150W |
| Navi 14 XT | RX 5500 XT | 22 | 1408 | 128-bit | 8GB GDDR6 | 130W |

### GCN 架构（2012-2017, TSMC/GF 28/14nm）

| 芯片代号 | 零售产品 | CU 数 | 流处理器 | 显存位宽 | 显存 | TDP |
|---------|---------|:-----:|:--------:|:--------:|------|:---:|
| Vega 20 | Radeon VII | 60 | 3840 | 4096-bit HBM2 | 16GB HBM2 | 300W |
| Vega 10 XT | RX Vega 64 | 64 | 4096 | 2048-bit HBM2 | 8GB HBM2 | 295W |
| Vega 10 XL | RX Vega 56 | 56 | 3584 | 2048-bit HBM2 | 8GB HBM2 | 210W |
| Polaris 30 XT | RX 590 | 36 | 2304 | 256-bit | 8GB GDDR5 | 225W |
| Polaris 20 XT | RX 580 | 36 | 2304 | 256-bit | 8GB GDDR5 | 185W |
| Polaris 20 XL | RX 570 | 32 | 2048 | 256-bit | 4-8GB GDDR5 | 150W |
| Polaris 11 | RX 560 | 16 | 1024 | 128-bit | 4GB GDDR5 | 75W |
| Polaris 12 | RX 550 | 10 | 640 | 64-bit | 2-4GB GDDR5 | 50W |
| Hawaii XT | R9 290X | 44 | 2816 | 512-bit | 4GB GDDR5 | 290W |
| Hawaii PRO | R9 290 | 40 | 2560 | 512-bit | 4GB GDDR5 | 250W |
| Tonga XT | R9 285 | 32 | 1792 | 256-bit | 2GB GDDR5 | 190W |
| Tahiti XT2 | R9 280X | 32 | 2048 | 384-bit | 3GB GDDR5 | 250W |
| Curacao XT | R9 270X | 20 | 1280 | 256-bit | 2-4GB GDDR5 | 180W |
| Bonaire XTX | R7 260X | 14 | 896 | 128-bit | 2GB GDDR5 | 115W |
| Oland | R7 240 | 6 | 320 | 128-bit | 2GB GDDR5 | 30W |

---

## Intel Arc GPU 芯片代号

### Battlemage 架构（2024, TSMC 5nm）

| 芯片代号 | 零售产品 | Xe 核心 | EU 数 | 显存位宽 | 显存 | TDP |
|---------|---------|:-------:|:-----:|:--------:|------|:---:|
| BMG-G21 | Arc B580 | 20 | 160 | 192-bit | 12GB GDDR6 | 150W |
| BMG-G21 | Arc B570 | 16 | 128 | 160-bit | 10GB GDDR6 | 150W |

### Alchemist 架构（2022, TSMC 6nm）

| 芯片代号 | 零售产品 | Xe 核心 | EU 数 | 显存位宽 | 显存 | TDP |
|---------|---------|:-------:|:-----:|:--------:|------|:---:|
| ACM-G10 | Arc A770 | 32 | 512 | 256-bit | 16GB GDDR6 | 225W |
| ACM-G10 | Arc A750 | 28 | 448 | 256-bit | 8GB GDDR6 | 225W |
| ACM-G10 | Arc A580 | 16 | 256 | 160-bit | 10GB GDDR6 | 150W |
| ACM-G11 | Arc A380 | 8 | 128 | 96-bit | 6GB GDDR6 | 75W |

---

## Apple GPU 芯片

| 芯片 | GPU 核心 | 统一内存带宽 | 制程 | 适用 |
|------|:--------:|:-----------:|:----:|------|
| M1 GPU | 7-8 核 | 68.25 GB/s | 5nm | MacBook Air/Pro 13 |
| M1 Pro GPU | 14-16 核 | 200 GB/s | 5nm | MacBook Pro 14/16 |
| M1 Max GPU | 24-32 核 | 400 GB/s | 5nm | MacBook Pro 16 |
| M2 GPU | 8-10 核 | 100 GB/s | 5nm | MacBook Air 13 |
| M2 Pro GPU | 19-30 核 | 200 GB/s | 5nm | MacBook Pro 14 |
| M3 GPU | 8-10 核 | 100 GB/s | 3nm | MacBook Air 13/15 |
| M3 Pro GPU | 14-18 核 | 150 GB/s | 3nm | MacBook Pro 14 |
| M3 Max GPU | 30-40 核 | 400 GB/s | 3nm | MacBook Pro 16 |
| M4 GPU | 10 核 | 120 GB/s | 3nm | MacBook Pro 14 |
| M4 Pro GPU | 16-20 核 | 273 GB/s | 3nm | MacBook Pro 14/16 |
