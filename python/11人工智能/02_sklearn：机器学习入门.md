# sklearn：机器学习入门 (scikit-learn: ML Basics)
---

## 章节概述

scikit-learn（简称 sklearn）是 Python 的传统机器学习标准库。对于 C 程序员，它的重要性在于：(1) 统一的 `fit/predict` API 设计让你无需记忆每个算法的细节，(2) 底层计算由 Cython/C 完成，性能不低，(3) 模型可以用 joblib 保存后由 C++ 程序加载。本章从分类、回归、聚类三大任务切入，带你掌握 sklearn 的核心工作模式。

> **核心理念**：机器学习的本质是 `y = f(X)` ——找到从输入 X 到输出 y 的映射函数。sklearn 把这个公式包装为 `model.fit(X, y)` → `model.predict(X_new)`。作为 C 程序员，你需要理解的不只是一行 API 调用，而是数据流（NumPy 数组 → 训练 → 模型对象 → 预测 → 结果）和模型序列化（.joblib 文件 → C++ 加载）。本章所有示例都可在 `python -c` 中一行运行。

---

### 第一节：sklearn 统一 API 与数据准备

1.1 核心 API 模式
-------------------

sklearn 的全部算法遵循三个核心方法：

```python
from sklearn.xxx import SomeModel

model = SomeModel(hyper_param=value) # 1. 创建模型，设置超参数
model.fit(X_train, y_train) # 2. 训练：从数据中学习
result = model.predict(X_test) # 3. 预测：对新数据做推断
```

这种统一性意味着：当你学会一个模型的使用方式，你就学会了所有 sklearn 模型。在 C 中，相当于所有算法都实现了同一个函数指针接口：

```c
// C 中的类比思维
typedef struct {
 void* model;
 void (*fit)(void* model, double* X, double* y, int n);
 void (*predict)(void* model, double* X, double* out, int n);
} BaseModel;
```

1.2 数据格式约定
-----------------

sklearn 的数据输入必须是以 NumPy 数组或 pandas DataFrame 形式：

```python
import numpy as np

# X: 特征矩阵，形状 (n_samples, n_features)
X = np.array([[1.0, 2.0],
 [3.0, 4.0],
 [5.0, 6.0]]) # 3 个样本，每个有 2 个特征

# y: 标签向量，形状 (n_samples,)
y = np.array([0, 1, 0]) # 3 个标签（分类）或连续值（回归）
```

> **C 对照**：`X` 等价于 C 中的 `double X[3][2]`，`y` 等价于 `int y[3]`。sklearn 内部将这些数据传给 Cython/C 实现处理。

1.3 经典数据集加载
-------------------

```bash
# 一行流：加载鸢尾花数据集并查看形状
python -c "
from sklearn.datasets import load_iris
X, y = load_iris(return_X_y=True)
print(f'X shape: {X.shape}, y shape: {y.shape}')
print(f'Classes: {set(y)}')
"
```

输出：
```
X shape: (150, 4), y shape: (150,)
Classes: {0, 1, 2}
```

150 个样本，4 个特征（花萼长/宽、花瓣长/宽），3 个类别（三种鸢尾花）。

1.4 训练/测试拆分
-------------------

```bash
python -c "
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
print(f'Train: {X_train.shape[0]}, Test: {X_test.shape[0]}')
"
```

> `random_state` 是随机种子，确保每次拆分结果一致。等同于 C 中的 `srand(42)`。

---

### 第二节：分类（Classification）

2.1 逻辑回归 — 最简单的分类器
------------------------------

```bash
python -c "
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

model = LogisticRegression(max_iter=200)
model.fit(X_train, y_train)
print(f'Accuracy: {model.score(X_test, y_test):.3f}')
print(f'Predictions: {model.predict(X_test[:5])}')
print(f'Probabilities:\n{model.predict_proba(X_test[:5])}')
"
```

2.2 随机森林 — 表格数据的王者
------------------------------

```bash
python -c "
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
model.fit(X_train, y_train)
print(f'Accuracy: {model.score(X_test, y_test):.3f}')
print(f'Feature importances: {model.feature_importances_}')
"
```

> `n_estimators=100` 意味着 100 棵决策树投票。每棵树在 C++ 底层递归分裂节点，所有树并行独立构建。

2.3 SVM — 最大边界分类器
-------------------------

```bash
python -c "
from sklearn.datasets import load_iris
from sklearn.svm import SVC

X, y = load_iris(return_X_y=True)
model = SVC(kernel='rbf', C=1.0, probability=True)
model.fit(X, y)
print(f'Support vectors: {len(model.support_vectors_)}')
"
```

2.4 评估指标
--------------

```bash
python -c "
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report

X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

print(f'Accuracy: {accuracy_score(y_test, y_pred):.3f}')
print(f'F1 (macro): {f1_score(y_test, y_pred, average=\"macro\"):.3f}')
print('Confusion Matrix:')
print(confusion_matrix(y_test, y_pred))
print('Report:')
print(classification_report(y_test, y_pred, target_names=load_iris().target_names))
"
```

| 指标 | 含义 | C 实现等价 |
|------|------|-----------|
| Accuracy | 预测正确的比例 | `sum(y_pred[i]==y_true[i]) / n` |
| Precision | 预测为正类中真正正类的比例 | `TP/(TP+FP)` |
| Recall | 真正正类被预测出的比例 | `TP/(TP+FN)` |
| F1 Score | Precision 和 Recall 的调和平均 | `2*P*R/(P+R)` |

---

### 第三节：回归与聚类

3.1 回归任务 — 预测连续值
--------------------------

```bash
python -c "
from sklearn.datasets import load_diabetes
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

X, y = load_diabetes(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

for name, model in [
 ('Linear', LinearRegression()),
 ('Ridge', Ridge(alpha=1.0)),
 ('RandomForest', RandomForestRegressor(n_estimators=100, random_state=42))
]:
 model.fit(X_train, y_train)
 y_pred = model.predict(X_test)
 print(f'{name:15s} | MSE: {mean_squared_error(y_test, y_pred):7.1f} | R²: {r2_score(y_test, y_pred):.3f}')
"
```

3.2 聚类任务 — 无标签数据的分组
--------------------------------

```bash
python -c "
from sklearn.datasets import make_blobs
from sklearn.cluster import KMeans
import numpy as np

X, _ = make_blobs(n_samples=300, centers=4, n_features=2, random_state=42)
kmeans = KMeans(n_clusters=4, random_state=42, n_init='auto')
labels = kmeans.fit_predict(X)
print(f'Cluster centers:\n{kmeans.cluster_centers_}')
print(f'Inertia: {kmeans.inertia_:.2f}')
print(f'Label counts: {np.bincount(labels)}')
"
```

> KMeans 使用 Lloyd 算法迭代优化：初始化中心 → 分配样本到最近中心 → 重新计算中心 → 重复。在 C 中，你可以用一个三重循环和一个距离函数实现相同的逻辑。

3.3 交叉验证 — 稳定评估模型性能
--------------------------------

```bash
python -c "
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

X, y = load_iris(return_X_y=True)
model = RandomForestClassifier(n_estimators=100, random_state=42)
scores = cross_val_score(model, X, y, cv=5) # 5 折交叉验证
print(f'CV scores: {scores}')
print(f'Mean: {scores.mean():.3f} ± {scores.std():.3f}')
"
```

> 5 折交叉验证 = 把数据分 5 份，轮流用 4 份训练、1 份测试，取 5 次指标的平均值。这比单次拆分更可靠。

---

### 第四节：Pipeline 与模型持久化

4.1 数据预处理
---------------

```bash
python -c "
from sklearn.preprocessing import StandardScaler, LabelEncoder
import numpy as np

# 标准化：使每个特征的均值为 0，方差为 1
X = np.array([[100, 2023],
 [200, 2024],
 [150, 2025]], dtype=float)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print(f'Original:\n{X}')
print(f'Scaled (mean=0, std=1):\n{X_scaled}')
print(f'Mean: {X_scaled.mean(axis=0)}, Std: {X_scaled.std(axis=0)}')
"
```

4.2 Pipeline —— 组装预处理和模型
---------------------------------

```bash
python -c "
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

pipe = Pipeline([
 ('scaler', StandardScaler()), # 第1步：标准化
 ('classifier', RandomForestClassifier(n_estimators=100, random_state=42)) # 第2步：分类
])
pipe.fit(X_train, y_train)
print(f'Pipeline accuracy: {pipe.score(X_test, y_test):.3f}')
"
```

> Pipeline 的思维和 Unix 管道一致：`数据 | 标准化 | 模型 | 预测`。在 C 中，相当于将多个函数组成一个执行链 `predict(model, scale(data))`。

4.3 模型保存与加载
--------------------

```python
import joblib

# 整个 Pipeline 作为一个整体保存
joblib.dump(pipe, 'iris_pipeline.joblib')

# C++ 程序或后续 Python 脚本中加载
loaded_pipe = joblib.load('iris_pipeline.joblib')
loaded_pipe.predict(X_new)
```

> **C++ 部署注意**：joblib 是 Python 的 pickle 协议，C++ 不能直接读取。要 C++ 部署 sklearn 模型，你需要：(1) 提取模型参数（如树的节点、SVM 的支持向量），手动用 C 实现推理；(2) 或者改用 XGBoost/LightGBM（有原生 C API）。

---

### 小节练习


> [!question] 判断题 1
> sklearn 的 RandomForest 和 SVM 使用完全不同的 Python API。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 所有 sklearn 模型遵循统一的 `fit()`/`predict()` API。换模型只需要改类名和超参数，其余代码可以不变。

---

## 章节测试

### 一、判断题（正确选 ，错误选 ）

> [!question] 判断题 1
> `train_test_split(X, y, test_size=0.3)` 随机将数据的 30% 分给测试集。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `test_size=0.3` 指定测试集比例为 30%，剩余 70% 为训练集。加上 `random_state` 可保证可复现性。

> [!question] 判断题 2
> `StandardScaler().fit_transform(X)` 将数据缩放到 [0, 1] 区间。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `StandardScaler` 执行的是 z-score 标准化（均值 0，标准差 1），不是 MinMax 缩放。`MinMaxScaler` 才缩放到 [0, 1]。

> [!question] 判断题 3
> 回归任务和分类任务的区别是：回归预测连续值，分类预测离散类别。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 回归输出实数（如房价 350.5 万元），分类输出类别标签（如猫/狗/鸟）。两者都是监督学习（有标签数据）。

> [!question] 判断题 4
> KMeans 是一种监督学习算法。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: KMeans 是无监督学习（unsupervised learning），训练时不需要标签 `y`，只需特征矩阵 `X`。它自动将样本分组为 k 个簇。

> [!question] 判断题 5
> joblib 保存的 sklearn 模型文件可以直接被 C++ 程序加载。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: joblib 使用 Python 的 pickle 序列化协议，C++ 无法直接读取。要部署到 C++，需要将模型转换为 ONNX 格式或手动提取参数用 C 重写推理逻辑。

> [!question] 判断题 6
> Pipeline 中 `fit()` 会对 Pipeline 中的每一步依次调用 `fit_transform()`（最后一步调用 `fit()`）。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: Pipeline 的 `fit()` 按顺序执行：对中间步骤调用 `fit_transform()`，对最后一步调用 `fit()`。这确保了预处理参数只在训练集上学习。


---

## 力扣练习

以下题目用于验证本章所学内容：

| 题号 | 题目 | 链接 | 涉及知识点 |
|------|------|------|-----------|
| — | 本章无对应力扣题 | — | 请用动手练习题自检 |



### 动手练习题

> [!example] 练习题 1：完整的分类 Pipeline
> **难度**: 简单
>
> 构建一个完整的 sklearn Pipeline：
> 1. 加载 `load_wine` 葡萄酒数据集
> 2. 用 `StandardScaler` 标准化特征
> 3. 用 `RandomForestClassifier(n_estimators=200)` 分类
> 4. 输出 `classification_report`
> 5. 用 `cross_val_score` 做 5 折交叉验证
> 6. 用 `joblib.dump` 保存 Pipeline 到 `wine_pipeline.joblib`
>
> 所有代码写在一个 `.py` 文件中，`python wine_classifier.py` 即可运行。

> [!example] 练习题 2：从 C 思维重新实现 KMeans
> **难度**: 简单
>
> 用 sklearn 的 `make_blobs` 生成 200 个样本、3 个簇的数据。然后用纯 Python（不要调 sklearn 的 KMeans）实现 KMeans 的 Lloyd 算法：
> 1. 随机初始化 3 个中心
> 2. 迭代：分配标签（找最近中心）→ 更新中心（计算每个簇的均值）→ 重复
> 3. 直到中心不再变化或达到 `max_iter`
>
> 将你的结果与 sklearn 的 `KMeans` 输出对比。这让你从 C 程序员的视角理解 sklearn 在做什么。

> [!example] 练习题 3：对比不同模型的性能
> **难度**: 简单
>
> 对 `load_digits` 手写数字数据集（8×8 像素图像，10 个类别），比较以下模型的准确率：
> - LogisticRegression (max_iter=5000)
> - RandomForestClassifier (n_estimators=200)
> - SVC (kernel='rbf')
> - KNeighborsClassifier (n_neighbors=3)
>
> 哪个模型在这个数据集上表现最好？用 `python -c` 一行流输出结果。
