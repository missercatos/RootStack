# Eigen

C++ 线性代数库的领军者，纯头文件库。提供矩阵/向量/四元数等数值线性代数操作，支持固定大小和动态大小的矩阵。表达模板（Expression Templates）技术在编译期优化表达式，消除临时变量。比手写 C 循环更快。

## 核心组件

| 组件 | 说明 |
|------|------|
| Matrix<T, Rows, Cols> | 通用矩阵类型模板 |
| VectorXd / Vector3d | 动态和固定大小向量 |
| Matrix3d / MatrixXf | 常用矩阵类型别名 |
| Geometry 模块 | 四元数、旋转矩阵、变换 |
| Eigen::SparseMatrix | 稀疏矩阵 |
| LDLT / LLT / QR / SVD | 线性方程求解和矩阵分解 |
| Tensor 模块 | 多维张量（Eigen unsupported） |

## 何时使用

- 所有需要矩阵运算的 C++ 项目
- 机器人、计算机图形学、物理模拟
- 机器学习底层和张量运算
- TensorFlow 和 PyTorch 的 C++ 底层都用 Eigen

## 关键特性

纯头文件、表达模板优化、SSE/AVX 向量化、丰富线性代数分解、固定/动态大小

## 相关链接

- [[OpenCV|OpenCV]] — 计算机视觉（内部使用 Eigen 风格）
- [[CGAL|CGAL]] — 计算几何算法
- [[../../c语言教程/库大全/第三方库/相关文件|C 第三方库]]
- [[../索引|库索引]]
- (搜索: Eigen C++)
