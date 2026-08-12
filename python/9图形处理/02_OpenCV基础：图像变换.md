# OpenCV 基础：图像变换 (OpenCV Basics)
---

## 章节概述

OpenCV（Open Source Computer Vision Library）是工业级的图像处理和计算机视觉库，由 Intel 发起，C++ 编写，提供 Python 绑定。本章聚焦于 OpenCV 在 Python 中的基础图像操作——这些操作在 C 中往往需要上百行代码来实现（手动管理矩阵、处理边界、手写卷积核）。你将看到 OpenCV 如何把 C++ 的高效实现暴露为 Python 的三行代码，同时理解其底层的 BGR 像素布局与 C 中 raw buffer 的对应关系。

> **核心理念**：OpenCV 的 Python API 和 C++ API 一一对应——`cv2.imread` 调用的是 C++ 的 `cv::imread`。这意味着你可以在 Python 中快速实验算法，确认无误后再将相同逻辑翻译为 C++ 部署到生产环境。Python 是你的算法试验场，C++ 是你的部署引擎。

---

### 第一节：图像读取、显示与 BGR 陷阱
---

1.1 基本 I/O
------------

```bash
pip install opencv-python
```

```python
import cv2
import numpy as np

img = cv2.imread('photo.jpg')
print(type(img)) # <class 'numpy.ndarray'>
print(img.shape) # (1080, 1920, 3) → (高度, 宽度, 通道)

cv2.imwrite('output.png', img)
```

**关键点**：OpenCV 读入的图像直接是 `numpy.ndarray`，而 Pillow 返回 `Image` 对象。这是两者的根本区别——OpenCV = NumPy，Pillow = 自有对象模型。

1.2 **BGR vs RGB —— 最大的坑**
-------------------------------

```python
img_cv = cv2.imread('photo.jpg') # 返回 BGR 顺序
img_pil = Image.open('photo.jpg') # 返回 RGB 顺序

# OpenCV 显示时颜色正常（因为它期望 BGR）
cv2.imshow('window', img_cv) # 颜色正确

# 用 matplotlib 显示时颜色错误
import matplotlib.pyplot as plt
plt.imshow(img_cv) # 偏蓝——matplotlib 期望 RGB
plt.imshow(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)) # 颜色正确
```

> 为什么是 BGR？历史原因：OpenCV 诞生于 1999 年，当时 Windows 上的相机驱动和位图格式普遍使用 BGR 顺序。Intel 团队选择了与 Windows BITMAPINFOHEADER 一致的 BGR 布局。二十多年后，这成了 OpenCV 用户的启蒙第一课。

在两库间传递数据：
```python
# Pillow → OpenCV
img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

# OpenCV → Pillow
img_pil = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
```

一行流快速操作：
```bash
python -c "import cv2; img = cv2.imread('test.jpg'); edges = cv2.Canny(img, 100, 200); cv2.imwrite('edges.jpg', edges)"
```

### 小节练习


> [!question] 判断题 1
> `cv2.imread` 读取不存在的文件时返回 `None`，不抛出异常。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 正确
> > > **解析**: OpenCV 的 `imread` 在文件不存在或无法解码时静默返回 `None`，不抛异常。这是 C++ API 风格——生产环境中请始终检查 `if img is None:`。

---

### 第二节：缩放与几何变换
---

2.1 尺寸缩放
------------

```python
resized = cv2.resize(img, (256, 256))
resized_fx = cv2.resize(img, None, fx=0.5, fy=0.5) # 按比例缩放

# 插值方法
cv2.resize(img, (256, 256), interpolation=cv2.INTER_NEAREST) # 最近邻
cv2.resize(img, (256, 256), interpolation=cv2.INTER_LINEAR) # 双线性（默认）
cv2.resize(img, (256, 256), interpolation=cv2.INTER_CUBIC) # 双三次
cv2.resize(img, (256, 256), interpolation=cv2.INTER_LANCZOS4) # Lanczos
```

2.2 仿射变换与透视变换
----------------------

```python
rows, cols = img.shape[:2]

# 平移矩阵
M = np.float32([[1, 0, 100], [0, 1, 50]])
shifted = cv2.warpAffine(img, M, (cols, rows))

# 旋转矩阵（中心，角度，缩放）
M = cv2.getRotationMatrix2D((cols/2, rows/2), 45, 1.0)
rotated = cv2.warpAffine(img, M, (cols, rows))

# 透视变换
pts1 = np.float32([[56,65],[368,52],[28,387],[389,390]])
pts2 = np.float32([[0,0],[300,0],[0,300],[300,300]])
M = cv2.getPerspectiveTransform(pts1, pts2)
warped = cv2.warpPerspective(img, M, (300, 300))
```

2.3 对比 C 实现：旋转矩阵
-------------------------

```c
// C 中实现旋转变换——你需要：
// 1. 构建 2x3 仿射变换矩阵
// 2. 逆向映射（遍历目标像素，计算源坐标）
// 3. 插值（双线性/双三次）
// 4. 边界处理

float rad = angle * M_PI / 180.0;
float cos_a = cos(rad), sin_a = sin(rad);
float M[6] = {cos_a, -sin_a, cx - cos_a*cx + sin_a*cy,
 sin_a, cos_a, cy - sin_a*cx - cos_a*cy};
// 然后手动遍历每个目标像素做逆向映射+插值...
```

OpenCV 的 `warpAffine` 在内部使用了高度优化的 SIMD 指令（SSE/AVX）来加速插值计算，比手写的 C 循环快 5-20 倍。对 C 程序员来说，这相当于免费获得了手写汇编级别的优化。

### 小节练习


> [!question] 判断题 1
> `cv2.resize(img1, (512, 512))` 可以接收不同尺寸的输入图像，自动处理缩放。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 正确
> > > **解析**: `resize` 不关心输入的尺寸，只要是一个合法的 `numpy.ndarray` 即可。对 C 程序员意味着：不需要先 `malloc` 正确尺寸的目标缓冲区。

---

### 第三节：滤波与平滑
---

3.1 模糊操作家族
----------------

```python
blur = cv2.blur(img, (5, 5)) # 均值滤波（box filter）
gaussian = cv2.GaussianBlur(img, (5, 5), 0) # 高斯模糊
median = cv2.medianBlur(img, 5) # 中值滤波（椒盐噪声克星）
bilateral = cv2.bilateralFilter(img, 9, 75, 75) # 双边滤波（保边去噪）
```

对比它们的 C 等价实现：
```c
// 均值滤波——遍历窗口求和除以窗口大小
// 高斯模糊——用二维高斯公式构建核权重
// 中值滤波——对窗口内像素排序取中值，O(n log n)
// 双边滤波——空间域×值域双重高斯权重，计算量巨大
```

> 双边滤波在 C 中极其难写——它需要为每个像素计算空间距离高斯权重和像素值距离高斯权重，计算复杂度 O(W×H×K²)。OpenCV 使用了可分离近似算法，性能提升 10-100 倍。

3.2 自定义卷积核
-----------------

```python
kernel = np.ones((5, 5), np.float32) / 25 # 5x5 均值
sharp_kernel = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]]) # 锐化
filtered = cv2.filter2D(img, -1, kernel) # -1 表示输出同深度
```

C 程序员会发现 `cv2.filter2D` 和手写卷积循环在逻辑上完全一致——不同之处在于 OpenCV 内部使用了 `cv::filter2D`，后者根据核大小和数据类型自动选择最优实现（SIMD、多线程）。

### 小节练习

> [!question] 判断题 1
> 中值滤波对高斯噪声的处理效果优于高斯模糊。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: 中值滤波的强项是**椒盐噪声**（孤立异常像素），因为它取中位数天然排除极端值。高斯模糊更适合**高斯噪声**（整体性随机波动）。两者适用场景不同。


---

### 第四节：阈值化与形态学操作
---

4.1 阈值处理
------------

```python
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

ret, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY) # 全局固定
ret, binary_inv = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
ret, trunc = cv2.threshold(gray, 127, 255, cv2.THRESH_TRUNC)

# Otsu 自动阈值——无需人工指定阈值
ret, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# 自适应阈值——局部阈值
adaptive = cv2.adaptiveThreshold(gray, 255,
 cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
```

> C 程序员注意：`ret` 是实际使用的阈值。对于 Otsu，你传入的阈值参数被忽略，Otsu 算法自动计算出使类间方差最大的阈值。

4.2 形态学操作
--------------

```python
kernel = np.ones((5, 5), np.uint8)

eroded = cv2.erode(binary, kernel, iterations=1) # 腐蚀
dilated = cv2.dilate(binary, kernel, iterations=1) # 膨胀
opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel) # 开运算（先腐后胀）
closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel) # 闭运算（先胀后腐）
gradient = cv2.morphologyEx(binary, cv2.MORPH_GRADIENT, kernel) # 形态梯度

# 结构元素形状
kernel_rect = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
kernel_ellip = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
kernel_cross = cv2.getStructuringElement(cv2.MORPH_CROSS, (5,5))
```

形态学操作在 C 中对应——对每个像素，在结构元素覆盖区域内求最小值（腐蚀）或最大值（膨胀）。OpenCV 使用查表法和 SIMD 加速，比 naive C 循环快一个数量级。

### 小节练习


> [!question] 判断题 1
> `cv2.threshold` 的 `THRESH_OTSU` 标志要求输入图像必须是灰度图。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 正确
> > > **解析**: Otsu 算法基于灰度直方图计算最佳阈值，因此必须是单通道灰度图。传入三通道图像会报错。

---

### 第五节：边缘检测
---

5.1 Canny 边缘检测
------------------

```python
edges = cv2.Canny(img, 100, 200) # 双阈值
edges_tight = cv2.Canny(img, 150, 250) # 更高阈值 → 更少边缘
edges_loose = cv2.Canny(img, 50, 150) # 更低阈值 → 更多边缘
```

Canny 算法的 C 实现需要以下步骤：
1. 高斯模糊去噪
2. 计算梯度（Sobel 算子）→ 幅值和方向
3. 非极大值抑制（NMS）——沿梯度方向只保留局部最大值
4. 双阈值检测——高于高阈值为强边缘，低于低阈值被丢弃
5. 边缘追踪（滞后）——与强边缘相连的弱边缘才保留

OpenCV 把这些步骤全部封装在 `cv2.Canny` 一个函数中，内部使用了 C++ 的多线程实现。

5.2 Sobel 和 Laplacian 算子
----------------------------

```python
sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3) # x 方向梯度
sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3) # y 方向梯度
sobel_combined = cv2.magnitude(sobel_x, sobel_y) # 梯度幅值

laplacian = cv2.Laplacian(gray, cv2.CV_64F) # 拉普拉斯算子
```

Sobel 算子的核矩阵正是 C 程序员熟悉的：

```
Gx = [[-1, 0, 1], Gy = [[-1,-2,-1],
 [-2, 0, 2], [ 0, 0, 0],
 [-1, 0, 1]] [ 1, 2, 1]]
```

这些就是 C 中手写卷积时的 `float kernel[9]`。

5.3 边缘检测与 C 对比
---------------------

```c
// C 中从零实现 Sobel 边缘检测——
// 你需要：
// 1. 灰度转换（加权求和）
// 2. 定义 Gx、Gy 核数组
// 3. 3x3 卷积（含边界判断）
// 4. 梯度幅值 = sqrt(Gx² + Gy²)
// 5. 归一化到 [0,255] 并写回 uint8 缓冲区
// → 大约 80-100 行代码

// OpenCV Python:
edges = cv2.Canny(img, 100, 200) // → 1 行
```

### 小节练习


> [!question] 判断题 1
> `cv2.Sobel` 的 `ksize` 参数只能是奇数。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 正确
> > > **解析**: Sobel 核需要中心对称，因此核尺寸必须是奇数（1, 3, 5, 7）。如果传入偶数，OpenCV 会报错。

---

## 章节测试

### 一、判断题（正确选，错误选）

> [!question] 判断题 1
> `cv2.imread` 返回的是 Pillow 的 `Image` 对象。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: `cv2.imread` 返回的是 `numpy.ndarray`（形状 `[H, W, C]`），不是 Pillow Image。这是 OpenCV 与 Pillow 最本质的数据结构差异。

> [!question] 判断题 2
> OpenCV 的 `cv2.cvtColor(img, cv2.COLOR_BGR2RGB)` 修改原始数组。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: `cvtColor` 返回新数组，不会原地修改输入。这是函数式风格，输入和输出可以是同一个数组（但内部仍是先计算再覆盖）。

> [!question] 判断题 3
> 高斯模糊的内核大小 `(5, 5)` 中，标准差的默认值由核大小自动计算。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 正确
> > > **解析**: `GaussianBlur` 的 `sigmaX` 参数若设为 0，则自动从核大小计算：`sigma = 0.3*((ksize-1)*0.5 - 1) + 0.8`。

> [!question] 判断题 4
> 腐蚀操作（erode）会使二值图像中白色前景区域变大。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: 腐蚀缩小白色区域（取邻域最小值），膨胀扩大白色区域（取邻域最大值）。记住：腐蚀→缩小，膨胀→扩大。

> [!question] 判断题 5
> `cv2.Canny` 的内部实际调用了 `cv2.Sobel` 计算梯度。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 正确
> > > **解析**: Canny 算法的第二步梯度计算就是用的 Sobel 算子（默认 3x3）。你可以通过对同一图像分别调用 `Sobel` 和观察 Canny 中间结果来验证。

---


---

## 力扣练习

以下题目用于验证本章所学内容：

| 题号 | 题目 | 链接 | 涉及知识点 |
|------|------|------|-----------|
| 48 | 旋转图像 | https://leetcode.cn/problems/rotate-image/ | 图像旋转90度 |
| 832 | 翻转图像 | https://leetcode.cn/problems/flipping-an-image/ | 水平翻转与颜色反转 |
| 867 | 转置矩阵 | https://leetcode.cn/problems/transpose-matrix/ | 矩阵转置、图像变换基础 |



### 动手练习题

> [!example] 练习题 1：灰度化 + 边缘检测流水线
> **难度**: 简单
>
> 使用 `python -c` 一行流完成以下管道：
> - 读取 `input.jpg`
> - 转为灰度
> - 高斯模糊（5×5）
> - Canny 边缘检测（阈值 80, 160）
> - 保存为 `edges.png`
>
> 然后将这一行改写为 Python 脚本 `edge_pipeline.py`，包含完整的错误处理和参数化。

> [!example] 练习题 2：自定义滤波器对比
> **难度**: 简单
>
> 用 C 和 Python 分别实现
> - Python：`cv2.filter2D` 使用自定义核
> - C：手写 3×3 卷积函数
>
> 用 5 个不同核（均值、高斯近似、锐化、拉普拉斯、Sobel X）分别测试两张不同尺寸的图像（64×64 和 1920×1080），记录两种实现的耗时差异。分析为什么小图上手写 C 可能更快，但大图上 OpenCV 反超。

> [!example] 练习题 3：文档图像去噪与二值化
> **难度**: 简单
>
> 给定一张手机拍摄的文档照片（光照不均、有噪声）：
> 1. 转灰度 → 高斯模糊去噪
> 2. 使用自适应阈值（`adaptiveThreshold`）二值化
> 3. 对比全局阈值（Otsu）和自适应阈值的效果差异
> 4. 用形态学闭运算去除文字中的小孔洞
> 5. 保存最终结果
>
> 整理成一个函数 `clean_document(input_path, output_path, block_size=11, C=2)`。

> [!example] 练习题 4：图像边缘强度热力图
> **难度**: 简单
>
> 使用 Sobel 算子计算 x 和 y 方向的梯度，合成梯度幅值图像：
> 1. 分别计算 Gx 和 Gy
> 2. 用 `cv2.magnitude` 合成幅值
> 3. 归一化到 [0, 255]
> 4. 应用伪彩色映射（`cv2.applyColorMap`）生成热力图
> 5. 将热力图与原图混合：`cv2.addWeighted(original, 0.5, heatmap, 0.5, 0)`
>
> 对比 `COLORMAP_JET`、`COLORMAP_HOT`、`COLORMAP_VIRIDIS` 的效果。
