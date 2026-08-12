# OpenCV 进阶：特征与检测 (OpenCV: Features & Detection)
---

## 章节概述

上一章聚焦于像素级的图像变换——滤波、边缘检测、阈值化。本章进入中层计算机视觉：从像素中提取有意义的几何结构和视觉特征。你将看到 OpenCV 如何将 C++ 中最复杂的算法（轮廓查找、霍夫变换、特征匹配、人脸检测）打包成 Python 的几行调用。对于 C 程序员，理解这些算法的底层原理仍然至关重要——你需要在 Python 中快速验证算法选型，再决定是否用 C++ 重写核心部分。

> **核心理念**：特征检测的本质是**数据压缩**——从百万像素中提取几百个关键点和轮廓，将图像"压缩"为稀疏的几何描述。在 C 中你需要实现 trie 树、极值搜索、抛物线插值；在 Python 中你只需调用一个函数。但当你要把这些特征传给 C 库做实时处理时，你仍然需要理解它们的二进制表示——这也正是 [[04_与C图像库互操作：raw数据交换|C互操作]] 章节的基础。

---

### 第一节：轮廓检测与分析
---

1.1 寻找轮廓
------------

```python
import cv2
import numpy as np

img = cv2.imread('shapes.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

contours, hierarchy = cv2.findContours(
 binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
)

print(f"找到 {len(contours)} 个轮廓")
```

`RETR_TREE` 检索所有轮廓并建立层次关系；`CHAIN_APPROX_SIMPLE` 压缩水平/垂直/对角线段（只保留端点，减少内存）。

1.2 轮廓特征与筛选
------------------

```python
for cnt in contours:
 area = cv2.contourArea(cnt)
 perimeter = cv2.arcLength(cnt, closed=True)
 if area < 100:
 continue # 过滤小噪点

 M = cv2.moments(cnt)
 cx = int(M['m10'] / M['m00']) if M['m00'] != 0 else 0
 cy = int(M['m01'] / M['m00']) if M['m00'] != 0 else 0

 x, y, w, h = cv2.boundingRect(cnt) # 正外接矩形
 rect = cv2.minAreaRect(cnt) # 最小外接旋转矩形
 (cx_r, cy_r), (rw, rh), angle = rect

 hull = cv2.convexHull(cnt) # 凸包
 epsilon = 0.01 * perimeter
 approx = cv2.approxPolyDP(cnt, epsilon, True) # 多边形逼近

 cv2.drawContours(img, [approx], -1, (0, 255, 0), 2)
```

1.3 C 对比：轮廓跟踪算法
------------------------

```c
// C 中实现轮廓查找（Moore-Neighbor 边界追踪）的伪代码：
//
// 1. 扫描图像找到第一个前景像素
// 2. 以该像素为起点，按顺时针搜索 8 邻域
// 3. 找到下一个边界像素后移动到该位置
// 4. 重复直到回到起点
// 5. 需要处理孔洞（内轮廓）和层次关系
//
// 完整实现大约 200-300 行 C 代码
// OpenCV 使用的是 Suzuki-Abe 算法，工业级实现数千行
```

OpenCV 的 `findContours` 基于 1985 年 Suzuki 和 Abe 的论文，在 C++ 中实现了边界追踪、层次构建、轮廓压缩。Python 层面只是薄薄的一层 wrapper。

### 小节练习


> [!question] 判断题 1
> `cv2.contourArea` 在轮廓自交的情况下仍然返回正确的面积。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: `contourArea` 使用格林公式（Green's theorem）计算有向面积，对自交轮廓（如蝴蝶结形状）结果无意义。需要先用凸包或简单多边形逼近处理。

---

### 第二节：霍夫变换——线圆检测
---

2.1 霍夫线检测
--------------

```python
edges = cv2.Canny(gray, 50, 150)

# 标准霍夫变换（返回 rho, theta）
lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=150)
for line in lines:
 rho, theta = line[0]
 a, b = np.cos(theta), np.sin(theta)
 x0, y0 = a * rho, b * rho
 x1, y1 = int(x0 + 1000*(-b)), int(y0 + 1000*(a))
 x2, y2 = int(x0 - 1000*(-b)), int(y0 - 1000*(a))
 cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

# 概率霍夫变换（返回线段端点，通常更实用）
lines_p = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100,
 minLineLength=50, maxLineGap=10)
for line in lines_p:
 x1, y1, x2, y2 = line[0]
 cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
```

> 霍夫变换把图像空间 `(x, y)` 中的直线检测转化为参数空间 `(ρ, θ)` 中的峰值查找。C 程序员可以想象这是一个"投票累加器"——每个边缘像素投票给所有可能穿过它的直线，得票最高的 `(ρ, θ)` 就是检测到的直线。

2.2 霍夫圆检测
--------------

```python
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.medianBlur(gray, 5) # 降噪对圆检测至关重要

circles = cv2.HoughCircles(
 gray, cv2.HOUGH_GRADIENT, dp=1, minDist=30,
 param1=100, param2=30, minRadius=10, maxRadius=100
)

if circles is not None:
 circles = np.uint16(np.around(circles))
 for (x, y, r) in circles[0]:
 cv2.circle(img, (x, y), r, (0, 255, 0), 2)
 cv2.circle(img, (x, y), 2, (0, 0, 255), 3)
```

参数含义对 C 程序员来说：
- `dp=1`：累加器分辨率（1=原图分辨率，2=半分辨率）
- `minDist`：两圆心最小距离（避免重复检测同一个圆）
- `param1`：Canny 高阈值
- `param2`：圆心累加器阈值（越小检测到越多圆）

### 小节练习


> [!question] 判断题 1
> `HoughCircles` 的 `minDist` 参数设得太小会导致同一圆被多次检测。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 正确
> > > **解析**: `minDist` 限制了输出圆之间的最小圆心距离。如果设得太小，同一个物理圆可能由于噪声产生多个检测结果（圆心相近）。增大 `minDist` 可以抑制这种现象。

---

### 第三节：模板匹配
---

3.1 滑动窗口匹配
-----------------

```python
img = cv2.imread('scene.jpg', 0)
template = cv2.imread('template.jpg', 0)
h, w = template.shape

methods = [
 cv2.TM_CCOEFF, cv2.TM_CCOEFF_NORMED,
 cv2.TM_CCORR, cv2.TM_CCORR_NORMED,
 cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED
]

for method in methods:
 result = cv2.matchTemplate(img, template, method)
 min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

 if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
 top_left = min_loc # SQDIFF 取最小值
 else:
 top_left = max_loc # 其他取最大值

 bottom_right = (top_left[0] + w, top_left[1] + h)
 cv2.rectangle(img, top_left, bottom_right, 255, 2)
```

3.2 多目标模板匹配
------------------

```python
template = cv2.imread('template.jpg', 0)
result = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
threshold = 0.8
locations = np.where(result >= threshold)

for pt in zip(*locations[::-1]):
 cv2.rectangle(img_color, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 1)
```

> C 程序员请注意：`matchTemplate` 返回的结果矩阵尺寸为 `(H_img - H_tmpl + 1, W_img - W_tmpl + 1)`。结果中位置 `(i,j)` 的值代表模板左上角对齐到图像 `(j,i)` 时的匹配分数。

### 小节练习


> [!question] 判断题 1
> 模板匹配可以处理缩放和旋转后的目标。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: `matchTemplate` 是刚性模板匹配——只能检测与模板**相同尺寸和角度**的目标。对于缩放/旋转不变性，需要使用特征匹配（见下节）。

---

### 第四节：特征检测与匹配
---

4.1 ORB 特征检测（免费+快速）
-----------------------------

```python
orb = cv2.ORB_create(nfeatures=500)
keypoints, descriptors = orb.detectAndCompute(img, None)

# 可视化关键点
img_kp = cv2.drawKeypoints(img, keypoints, None,
 flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
```

每个关键点是一个 `KeyPoint` 对象：`(x, y, size, angle, response, octave)`。`descriptors` 是 `(N, 32)` 的 uint8 矩阵——每个关键点一个 256-bit 二进制描述符。对 C 程序员来说就是 `uint8_t descriptors[N][32]`。

4.2 SIFT 特征检测（专利/付费，但更稳健）
-------------------------------------

SIFT 在纯开源版 OpenCV 中可能需要额外安装 `opencv-contrib-python`：

```bash
pip install opencv-contrib-python
```

```python
sift = cv2.SIFT_create(nfeatures=500)
keypoints, descriptors = sift.detectAndCompute(img, None)
```

SIFT 描述子是 `(N, 128)` 的 float32 矩阵。相比 ORB 的 32 字节二进制，SIFT 的 512 字节浮点更占内存但匹配更准确。

4.3 特征匹配
------------

暴力匹配（穷举搜索）：
```python
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True) # ORB 用汉明距离
matches = bf.match(des1, des2)
matches = sorted(matches, key=lambda x: x.distance)[:50]
result = cv2.drawMatches(img1, kp1, img2, kp2, matches[:30], None)

# SIFT 用 L2 距离
bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
```

FLANN 近似最近邻（大数据量推荐）：
```python
FLANN_INDEX_KDTREE = 1
index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
search_params = dict(checks=50)
flann = cv2.FlannBasedMatcher(index_params, search_params)
matches = flann.knnMatch(des1, des2, k=2)

# Lowe's ratio test 过滤误匹配
good = []
for m, n in matches:
 if m.distance < 0.7 * n.distance:
 good.append(m)
```

### 小节练习


> [!question] 判断题 1
> ORB 描述子使用浮点数向量，SIFT 使用二进制比特串。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: 正好相反——ORB 使用 256-bit 二进制描述子（BRIEF 改进），匹配用汉明距离；SIFT 使用 128 维浮点向量，匹配用欧氏距离。

---

### 第五节：人脸检测（Haar Cascade）
---

5.1 使用预训练级联分类器
------------------------

```python
cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(cascade_path)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
faces = face_cascade.detectMultiScale(
 gray,
 scaleFactor=1.1, # 每次搜索窗口缩放比例
 minNeighbors=5, # 最小邻接检测数（过滤误检）
 minSize=(30, 30) # 最小人脸尺寸
)

for (x, y, w, h) in faces:
 cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
```

5.2 级联分类器的 C 本质
-----------------------

Haar 级联分类器是一个多级增强分类器链。C 程序员可以这样理解：

```c
// 伪代码：Haar 级联的决策逻辑
int detect_face(uint8_t *gray, int w, int h, int x, int y, int win_w, int win_h) {
 for (int stage = 0; stage < num_stages; stage++) {
 float stage_sum = 0.0;
 for (int feature = 0; feature < features_per_stage[stage]; feature++) {
 // 计算 Haar 特征：白矩形和 - 黑矩形和（用积分图加速）
 float feat_val = compute_haar_feature(integral_img, features[stage][feature]);
 stage_sum += feat_val * weights[stage][feature];
 }
 if (stage_sum < stage_thresholds[stage])
 return 0; // 该级未通过 → 非人脸
 }
 return 1; // 所有级通过 → 是人脸
}
```

积分图是 Haar 级联快的关键——它让任意矩形的像素和可以在 O(1) 时间计算。C 程序员应该立刻想到预计算前缀和数组。

5.3 深度学习方法概述
--------------------

OpenCV 的 DNN 模块支持加载预训练深度学习模型：

```python
net = cv2.dnn.readNetFromCaffe('deploy.prototxt', 'model.caffemodel')
blob = cv2.dnn.blobFromImage(img, 1.0, (300,300), (104,177,123))
net.setInput(blob)
detections = net.forward()
```

> 深度学习目标检测（YOLO、SSD、Faster R-CNN）超越了传统视觉方法。详细内容见 [[../11人工智能/]]。

### 小节练习


> [!question] 判断题 1
> OpenCV 的 Haar 级联分类器使用积分图加速 Haar 特征计算。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 正确
> > > **解析**: 积分图（Integral Image）是 Haar 级联的核心加速技巧——将任意矩形像素和的计算从 O(w×h) 降为 O(1)。这正是 Viola-Jones 2001 年论文的关键贡献。

---

## 章节测试

### 一、判断题（正确选，错误选）

> [!question] 判断题 1
> `cv2.findContours` 会修改输入的图像（标记已访问的边界）。( )
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 正确
> > > **解析**: `findContours` 会**原地修改**输入的二值图像（用于标记已访问的边界像素）。如果你后续还需要原图，请传入 `binary.copy()`。

> [!question] 判断题 2
> 霍夫线检测对图像中的曲线也能正确检测。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: 霍夫线检测专门检测直线。检测圆使用霍夫圆检测（三维参数空间）。推广到任意形状用广义霍夫变换，但计算成本随参数空间维度指数增长。

> [!question] 判断题 3
> 模板匹配 `TM_CCOEFF_NORMED` 的匹配分数范围是 [0, 1]。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: `TM_CCOEFF_NORMED` 返回归一化互相关系数，范围是 [-1, 1]。1 表示完美正匹配，-1 表示完美负匹配（如负片效果），0 表示不相关。

> [!question] 判断题 4
> FLANN 匹配器返回的是近似最近邻，而非精确最近邻。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 正确
> > > **解析**: FLANN（Fast Library for Approximate Nearest Neighbors）使用 KD 树或其他索引结构做近似搜索，适合高维海量特征。暴力匹配（`BFMatcher`）做的是穷举精确匹配。

> [!question] 判断题 5
> `cv2.CascadeClassifier` 只能用于人脸检测。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: Haar/LBP 级联分类器是通用框架，可以检测任何物体——只要你有对应的 XML 训练文件。OpenCV 预装了人脸、眼睛、微笑、身体、车牌等多种检测器。

---


---

## 力扣练习

以下题目用于验证本章所学内容：

| 题号 | 题目 | 链接 | 涉及知识点 |
|------|------|------|-----------|
| 200 | 岛屿数量 | https://leetcode.cn/problems/number-of-islands/ | 连通区域检测、DFS/BFS |
| 463 | 岛屿的周长 | https://leetcode.cn/problems/island-perimeter/ | 边界检测、区域特征 |
| 695 | 岛屿的最大面积 | https://leetcode.cn/problems/max-area-of-island/ | 区域面积计算 |



### 动手练习题

> [!example] 练习题 1：工业零件计数
> **难度**: 简单
>
> 给定一张含多个圆形零件的俯拍图像：
> 1. 灰度化 + 高斯模糊降噪
> 2. 霍夫圆检测（调整 `param1`, `param2`, `minDist` 直到准确）
> 3. 统计检测到的圆数量
> 4. 在原图上标注圆心和半径，并标注编号
> 5. 输出计数结果
>
> 用 C 伪代码写出霍夫圆检测的核心累加器投票逻辑，与 Python 版本对比。

> [!example] 练习题 2：图像拼接（Panorama）
> **难度**: 简单
>
> 用特征匹配实现两张有重叠区域的图像拼接：
> 1. 使用 ORB 或 SIFT 在两图上检测特征
> 2. 用 `BFMatcher` + Lowe's ratio test 筛选良好匹配
> 3. 用 `cv2.findHomography` + RANSAC 计算单应矩阵
> 4. 用 `cv2.warpPerspective` 变换并对齐
> 5. 处理接缝处的曝光差异（简单的权重融合）
>
> 提示：`cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)`。

> [!example] 练习题 3：实时人脸模糊
> **难度**: 简单
>
> 使用 Haar 级联分类器检测人脸，然后对检测区域应用高斯模糊：
> 1. 加载 `haarcascade_frontalface_default.xml`
> 2. 对图像检测所有人脸
> 3. 对每个人脸区域的像素做高斯模糊（kernel 与人脸大小成比例）
> 4. 处理重叠检测框（NMS —— 非极大值抑制）
> 5. 封装为 `blur_faces(img, cascade, blur_ratio=0.1)` 函数

> [!example] 练习题 4：模板匹配工业缺陷检测
> **难度**: 简单
>
> 使用模板匹配检测 PCB 板上的缺陷：
> 1. 用标准 PCB 照片做模板
> 2. 对测试 PCB 执行滑动窗口模板匹配
> 3. 找到匹配区域后，计算残差图（差值图像）
> 4. 对残差图二值化，找出异常区域
> 5. 统计异常面积和位置
>
> 注意：实际的缺陷检测需要考虑光照变化、旋转偏移，仅用原始模板匹配是不够的——思考有哪些改进方法。
