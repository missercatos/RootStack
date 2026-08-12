# Pillow：图像读取与处理 (Pillow: Image Basics)
---

## 章节概述

Pillow 是 Python 最流行的图像处理库（前身是 PIL），提供了跨格式的图像读取、写入和基本操作能力。对于 C 程序员，Pillow 相当于 `stb_image.h` 但无需手动管理内存——不需要 `malloc` 分配缓冲区、不需要 `free` 释放、不需要手动跟踪宽/高/通道数。本章从 C 程序员的视角切入，逐层展示 Pillow 的核心 API 及其与 C 图像库的对应关系。

> **核心理念**：在 C 中处理图像意味着你手持一个 `uint8_t*` 指针，扛着宽高和通道数三个元数据变量；在 Python 中，`Image` 对象把这四样东西打包成一个黑箱，你只需调用方法。但黑箱之下，数据和 C 的 raw pixel buffer 是同一回事——理解这一点是后续 [[04_与C图像库互操作：raw数据交换|与 C 图像库互操作]] 的基础。

---

### 第一节：打开、显示与保存图像
---

1.1 基本读写操作
---------------

```bash
pip install Pillow
```

```python
from PIL import Image

img = Image.open('photo.jpg')
print(img.format, img.size, img.mode)
# JPEG (1920, 1080) RGB

img.save('photo.png')
img.save('thumb.jpg', quality=85)
```

对应 C 程序员熟悉的操作：

```c
// C: stb_image.h 方式
#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

int w, h, ch;
unsigned char *data = stbi_load("photo.jpg", &w, &h, &ch, 3);
// ... 使用 data ...
stbi_write_png("photo.png", w, h, 3, data, w * 3);
stbi_image_free(data);
```

Pillow 隐藏了三个问题：
- **内存分配**：`Image.open` 自动分配并管理像素缓冲区，不需要 `malloc`/`free`
- **格式检测**：自动从文件头检测格式，不需要指定 `stbi_load` vs `stbi_load_from_memory`
- **模式转换**：保存时自动将 RGB 转为 PNG 支持的 RGBA，不需要手动填充 alpha 通道

1.2 一行流快速操作
------------------

```bash
python -c "from PIL import Image; img = Image.open('test.jpg'); img.thumbnail((100,100)); img.save('thumb.jpg')"
```

这一行完成了 C 中约 30 行代码的工作：打开 → 解码 JPEG → 缩放 → 编码 JPEG → 写入文件。

### 小节练习


> [!question] 判断题 1
> `Image.save('out.png')` 会自动根据文件扩展名选择编码格式。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 正确
> > > **解析**: Pillow 根据 `save()` 的文件名后缀自动选择编码器（`.png`→PNG, `.jpg`→JPEG）。你也可以用 `format` 参数显式指定。

---

### 第二节：基本几何变换
---

2.1 缩放、裁剪、旋转、翻转
--------------------------

```python
from PIL import Image
img = Image.open('test.jpg')

resized = img.resize((256, 256))
resized_lanczos = img.resize((256, 256), Image.LANCZOS)

cropped = img.crop((100, 100, 400, 300))

rotated = img.rotate(45, expand=True)

flipped_h = img.transpose(Image.FLIP_LEFT_RIGHT) # 水平翻转
flipped_v = img.transpose(Image.FLIP_TOP_BOTTOM) # 垂直翻转
```

重采样滤镜对比：

| 滤镜 | 速度 | 质量 | 适用场景 |
|------|------|------|---------|
| `Image.NEAREST` | 最快 | 最差 | 像素艺术 |
| `Image.BILINEAR` | 快 | 一般 | 快速预览 |
| `Image.BICUBIC` | 中等 | 较好 | 一般缩放 |
| `Image.LANCZOS` | 慢 | 最好 | 高质量缩放（默认） |

2.2 C 对比：手动缩放
--------------------

```c
// C 中双线性缩放——你需要手动遍历每个目标像素
void bilinear_scale(uint8_t *src, uint8_t *dst,
 int sw, int sh, int dw, int dh, int ch) {
 for (int y = 0; y < dh; y++) {
 for (int x = 0; x < dw; x++) {
 float sx = (float)x / dw * sw;
 float sy = (float)y / dh * sh;
 int x0 = (int)sx, y0 = (int)sy;
 int x1 = min(x0 + 1, sw - 1);
 int y1 = min(y0 + 1, sh - 1);
 for (int c = 0; c < ch; c++) {
 float v00 = src[(y0 * sw + x0) * ch + c];
 float v10 = src[(y0 * sw + x1) * ch + c];
 float v01 = src[(y1 * sw + x0) * ch + c];
 float v11 = src[(y1 * sw + x1) * ch + c];
 dst[(y * dw + x) * ch + c] = /* 插值公式 */;
 }
 }
 }
}
```

Python 一行：
```python
resized = img.resize((256, 256), Image.LANCZOS)
```

### 小节练习


> [!question] 判断题 1
> `img.resize((256, 256))` 会修改原始 `img` 对象。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: Pillow 的所有变换操作都返回**新 Image 对象**，原始对象不变。这是不可变（immutable）风格，类似于 C 中传值而非传指针。

---

### 第三节：颜色模式转换与像素操作
---

3.1 颜色模式
------------

```python
img = Image.open('photo.jpg') # RGB

gray = img.convert('L') # 灰度 (8-bit)
rgba = img.convert('RGBA') # 带 alpha 通道
cmyk = img.convert('CMYK') # 印刷四色
binary = img.convert('1') # 二值（黑白，每像素1bit）
```

常见模式速查：

| 模式 | 通道数 | 每像素位数 | 用途 |
|------|--------|-----------|------|
| `1` | 1 | 1 bit | 二值图（黑白） |
| `L` | 1 | 8 bit | 灰度图 |
| `LA` | 2 | 8+8 bit | 灰度+透明 |
| `RGB` | 3 | 24 bit | 真彩色 |
| `RGBA` | 4 | 32 bit | 真彩色+透明 |
| `CMYK` | 4 | 32 bit | 印刷色 |

3.2 像素级访问
--------------

```python
pixel = img.getpixel((10, 20)) # 返回 (R, G, B) 元组
img.putpixel((10, 20), (255, 0, 0)) # 将该像素设为红色
```

对 C 程序员的对应：

```c
// C: 通过指针偏移访问像素
uint8_t *p = data + (y * width + x) * channels;
uint8_t r = p[0], g = p[1], b = p[2];
```

Pillow 的 `getpixel`/`putpixel` 适合单点操作，但**性能极差**——每次调用都涉及 Python 函数调用和坐标检查。批量操作应该用：
```python
pixels = list(img.getdata()) # 获取所有像素的扁平列表
# 或直接用 numpy（下一章详细讲）
```

> `getpixel`/`putpixel` 对应 C 中的指针偏移，但 Python 的函数调用开销使它们比 C 慢 100-1000 倍。需要批量像素操作时，请跳转到 [[02_OpenCV基础：图像变换|OpenCV+Numpy]]。

3.3 像素直方图统计
------------------

```python
hist = img.histogram() # 每个通道 256 个桶
r_hist = hist[0:256] # R 通道直方图
g_hist = hist[256:512] # G 通道直方图
b_hist = hist[512:768] # B 通道直方图
```

### 小节练习


> [!question] 判断题 1
> `img.getpixel((0, 0))` 在 RGB 图像上返回一个包含 3 个整数的元组。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 正确
> > > **解析**: RGB 模式下每个像素返回 `(R, G, B)` 三元组，灰度模式返回单个整数，RGBA 返回四元组。

---

### 第四节：滤镜与增强
---

4.1 内置滤镜
------------

```python
from PIL import Image, ImageFilter

img = Image.open('test.jpg')

blurred = img.filter(ImageFilter.BLUR) # 均值模糊
sharpened = img.filter(ImageFilter.SHARPEN) # 锐化
edges = img.filter(ImageFilter.FIND_EDGES) # 边缘检测
emboss = img.filter(ImageFilter.EMBOSS) # 浮雕效果
detail = img.filter(ImageFilter.DETAIL) # 细节增强

# 自定义核（kernel）——这正是 C 中卷积的本质
custom_kernel = ImageFilter.Kernel(
 (3, 3),
 [-1, -1, -1, -1, 8, -1, -1, -1, -1],
 scale=1, offset=0
)
edge_enhanced = img.filter(custom_kernel)
```

4.2 对比 C 中的卷积实现
-----------------------

```c
// C 手写 3x3 卷积——你需要管理边界、步长、累加器
void convolve3x3(uint8_t *src, uint8_t *dst,
 int w, int h, int c,
 float kernel[9]) {
 for (int y = 1; y < h - 1; y++) {
 for (int x = 1; x < w - 1; x++) {
 for (int ch = 0; ch < c; ch++) {
 float sum = 0;
 for (int dy = -1; dy <= 1; dy++)
 for (int dx = -1; dx <= 1; dx++)
 sum += src[((y+dy)*w + (x+dx))*c + ch]
 * kernel[(dy+1)*3 + (dx+1)];
 dst[(y*w + x)*c + ch] = (uint8_t)fmaxf(0, fminf(255, sum));
 }
 }
 }
}
```

Pillow 一行：
```python
img.filter(ImageFilter.Kernel((3,3), kernel))
```

核矩阵就是 C 中的 `kernel[9]` 数组——概念完全一致，区别在于 Pillow 帮你处理了边界条件（补零/扩展/镜像）和溢出裁剪。

4.3 `ImageEnhance` 增强模块
---------------------------

```python
from PIL import ImageEnhance

enhancer = ImageEnhance.Brightness(img)
brighter = enhancer.enhance(1.5) # 1.0=原图, >1 更亮, <1 更暗

contrast = ImageEnhance.Contrast(img).enhance(1.3)
color = ImageEnhance.Color(img).enhance(2.0)
sharp = ImageEnhance.Sharpness(img).enhance(2.0)
```

### 小节练习


> [!question] 判断题 1
> `ImageEnhance.Brightness(img).enhance(1.0)` 返回的是原始图像的深拷贝。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: `enhance(1.0)` 返回的是原始图像的**引用**（同一个对象），不是拷贝。要深拷贝请用 `img.copy()`。

---

## 章节测试

### 一、判断题（正确选，错误选）

> [!question] 判断题 1
> Pillow 的 `Image.open()` 在调用时立即将整个图像文件解码到内存中。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: Pillow 采用惰性加载（lazy loading）——`Image.open()` 只读取文件头和元数据，像素数据在第一次访问（如 `getpixel`、`resize`、`getdata`）时才真正解码。这对应 C 中的"先解析头，按需解码"策略。

> [!question] 判断题 2
> `img.crop((0,0,100,100))` 的坐标格式是 `(x1, y1, x2, y2)`，左闭右开。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 正确
> > > **解析**: `crop` 的 box 参数是 `(left, upper, right, lower)`，裁剪区域包含 left 和 upper 但不包含 right 和 lower（即左闭右开区间）。

> [!question] 判断题 3
> Pillow 的 `Image` 对象可以直接与 numpy 数组互转。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 正确
> > > **解析**: `numpy.array(img)` 将 Image 转为 `ndarray`（形状 `(H, W, C)`），`Image.fromarray(arr)` 反向转换。这是连接 Pillow 和 NumPy/OpenCV 世界的桥梁。

> [!question] 判断题 4
> `img.convert('L')` 使用固定的灰度转换系数，与 `cv2.cvtColor(..., cv2.COLOR_BGR2GRAY)` 使用的是同一组系数。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: Pillow 和 OpenCV 使用的灰度转换加权系数略有不同，虽然差异微乎其微但对精度敏感的场景需要注意。

> [!question] 判断题 5
> `ImageFilter.Kernel((3,3), kernel)` 中的核矩阵元素可以为负数。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 正确
> > > **解析**: 核矩阵值可以是任意整数（正或负）。`scale` 参数用于除法归一化，`offset` 用于加偏置。这正是边缘检测核（如拉普拉斯核）需要负值的原因。

---


---

## 力扣练习

以下题目用于验证本章所学内容：

| 题号 | 题目 | 链接 | 涉及知识点 |
|------|------|------|-----------|
| 48 | 旋转图像 | https://leetcode.cn/problems/rotate-image/ | 图像旋转、矩阵变换 |
| 733 | 图像渲染 | https://leetcode.cn/problems/flood-fill/ | 图像填充、DFS/BFS |
| 832 | 翻转图像 | https://leetcode.cn/problems/flipping-an-image/ | 图像水平翻转与反转 |



### 动手练习题

> [!example] 练习题 1：批量缩略图生成器
> **难度**: 简单
>
> 编写一个 Python 脚本 `thumbnailer.py`，使用 `python -c` 一行流版：
> - 遍历当前目录所有 `.jpg` 和 `.png` 文件
> - 为每个文件生成 128×128 的缩略图（保持比例，填充为正方形）
> - 缩略图保存到 `thumbs/` 子目录，文件名为 `thumb_` + 原名
> - 使用 `Image.LANCZOS` 重采样
>
> 提示：用 `os.makedirs('thumbs', exist_ok=True)` 创建输出目录。

> [!example] 练习题 2：自定义滤镜实现
> **难度**: 简单
>
> 用 C 和 Python 分别实现 5×5 高斯模糊核：
> - C 版本：手写卷积函数，对比 `stb_image.h` 的用法流程
> - Python 版本：用 `ImageFilter.Kernel` 一行实现
> - 对比两种实现的代码行数和性能差异
> - 在 Python 中也手写一遍像素级卷积（用 `getpixel`/`putpixel`），感受速度差异

> [!example] 练习题 3：图像格式批量转换工具
> **难度**: 简单
>
> 编写脚本 `convert_images.py`，接收三个命令行参数：
> ```bash
> python convert_images.py ./input/ ./output/ png
> ```
> - 将 `input/` 下所有图像文件转换为指定格式
> - 保留原始文件名，仅改扩展名
> - 对 JPEG 输出支持 `quality` 参数（通过第 4 个可选参数传入）
> - 使用 `if __name__ == "__main__":` 守卫
> - 处理文件不存在的异常

> [!example] 练习题 4：图像直方图均衡化
> **难度**: 简单
>
> 使用 Pillow 的像素级 API 实现灰度图像的直方图均衡化：
> 1. 计算每个灰度级（0-255）的累积分布函数（CDF）
> 2. 将 CDF 映射为新的像素值
> 3. 用 `putpixel` 写回图像
> 4. 对比均衡化前后的直方图
>
> 然后再用 `ImageOps.equalize()` 一行完成，对比结果差异。
