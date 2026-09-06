# Conda：科学计算的环境与包管理

> Conda 是一个跨平台的环境和包管理器，最初为科学计算设计，但现在广泛用于 Python 开发。
> 与 venv/pip 不同，conda 可以管理**任何语言**的依赖（Python、R、C/C++、CUDA 等），
> 并且能创建**指定 Python 版本**的独立环境。

---

## 一、Conda vs venv/pip

| 特性 | venv + pip | conda |
|------|-----------|-------|
| 环境管理 | 仅 Python | 任何语言 (Python/R/CUDA) |
| Python 版本 | 需系统已安装 | 自动下载指定版本 |
| 包来源 | PyPI | conda-forge / defaults |
| C 库依赖 | 需手动装系统包 | conda 自动处理 |
| CUDA 支持 | 需手动装 | `conda install pytorch-cuda` |
| 跨平台 | 部分包有差异 | 一致的跨平台体验 |
| 环境激活 | `source .venv/bin/activate` | `conda activate env_name` |

**何时用 conda**：
- 需要特定 Python 版本（如 3.10）
- 项目依赖 CUDA、MKL、OpenBLAS 等 C 库
- 科学计算（NumPy、SciPy、PyTorch、TensorFlow）
- R 语言或混合 Python/R 项目

**何时用 venv/pip**：
- 纯 Python Web 开发
- 不需要特殊 C 库
- 追求轻量和速度

---

## 二、安装 Conda

### 2.1 Miniconda（推荐，轻量）

```bash
# Linux/macOS
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# 按照提示操作：
# - 按回车查看许可协议
# - 输入 yes 接受协议
# - 确认安装路径（默认 ~/miniconda3）
# - 输入 yes 初始化 conda

# 安装后重新加载 shell
source ~/.bashrc   # Linux
# source ~/.zshrc  # macOS (zsh)
```

### 2.2 验证安装

```bash
conda --version
# conda 24.x.x

# 查看 conda 配置
conda config --show
```

### 2.3 配置国内镜像（可选，推荐）

```bash
# 清华镜像
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
conda config --set show_channel_urls yes

# 中科大镜像
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/conda-forge/
```

---

## 三、创建虚拟环境

### 3.1 创建指定 Python 版本的环境

```bash
# 创建 Python 3.10 环境
conda create -n myenv python=3.10

# 创建环境并指定精确版本
conda create -n myenv python=3.10.12

# 创建环境并预装包
conda create -n myenv python=3.10 numpy pandas

# 创建环境时不自动激活
conda create -n myenv python=3.10 --no-default-packages
```

### 3.2 激活/退出环境

```bash
# 激活环境
conda activate myenv

# 退出环境
conda deactivate

# 查看当前环境
conda info --envs
# 或简写
conda env list
```

### 3.3 管理环境

```bash
# 列出所有环境
conda env list

# 复制环境
conda create -n myenv_copy --clone myenv

# 导出环境（用于分享/复现）
conda env export > environment.yml

# 从 yml 文件创建环境
conda env create -n newenv -f environment.yml

# 更新环境
conda env update -n myenv -f environment.yml

# 删除环境
conda env remove -n myenv
```

---

## 四、安装包

### 4.1 使用 conda install

```bash
# 激活环境后安装
conda activate myenv

# 安装包
conda install numpy
conda install pandas=2.0
conda install scikit-learn matplotlib

# 从 conda-forge 安装（社区维护，更新更快）
conda install -c conda-forge numpy

# 搜索包
conda search numpy
conda search numpy --info  # 查看详细信息
```

### 4.2 使用 pip（conda 环境内）

```bash
# conda 环境内可以使用 pip
conda activate myenv
pip install requests  # 从 PyPI 安装

# 注意：conda install 优先，pip install 作为补充
# 如果 conda 有该包，优先用 conda install
```

### 4.3 管理已安装包

```bash
# 查看当前环境的包
conda list

# 查看特定包
conda list numpy

# 更新包
conda update numpy
conda update --all  # 更新所有包

# 卸载包
conda uninstall numpy
```

---

## 五、实战：创建 Python 3.10 + PyTorch 环境

### 5.1 创建环境

```bash
# 创建 Python 3.10 环境
conda create -n py310 python=3.10 -y
conda activate py310

# 安装 PyTorch（CUDA 11.8）
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia

# 或从 conda-forge 安装
conda install -c conda-forge pytorch torchvision torchaudio
```

### 5.2 验证安装

```bash
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
# 2.x.x
# True
```

### 5.3 导出环境

```bash
conda env export > py310_torch.yml
```

```yaml
# py310_torch.yml 内容示例
name: py310
channels:
  - pytorch
  - nvidia
  - conda-forge
  - defaults
dependencies:
  - python=3.10
  - pytorch
  - torchvision
  - torchaudio
  - pytorch-cuda=11.8
```

---

## 六、常见问题

### 6.1 conda activate 不生效

```bash
# 需要先初始化 conda
conda init bash
# 重新打开终端
source ~/.bashrc
```

### 6.2 conda 安装太慢

```bash
# 使用国内镜像（见 §2.3）
# 或使用 mamba（conda 的加速版）
conda install -n base conda-libmamba-solver
conda config --set solver libmamba
```

### 6.3 conda 和 venv 混用

```bash
# 不建议混用，但可以在 conda 环境内创建 venv
conda activate myenv
python -m venv .venv  # 不推荐，多此一举

# 推荐：用 conda 管理环境，pip 作为补充
conda activate myenv
pip install some_package  # OK
```

### 6.4 清理无用包

```bash
# 清理不再需要的包
conda clean --all

# 查看环境占用空间
du -sh ~/miniconda3/envs/myenv
```

---

## 七、Conda 命令速查

| 操作 | 命令 |
|------|------|
| 创建环境 | `conda create -n env_name python=3.10` |
| 激活环境 | `conda activate env_name` |
| 退出环境 | `conda deactivate` |
| 列出环境 | `conda env list` |
| 删除环境 | `conda env remove -n env_name` |
| 导出环境 | `conda env export > environment.yml` |
| 从 yml 创建 | `conda env create -f environment.yml` |
| 安装包 | `conda install package_name` |
| 指定版本 | `conda install package_name=1.0` |
| 从 conda-forge 安装 | `conda install -c conda-forge package_name` |
| 更新包 | `conda update package_name` |
| 卸载包 | `conda uninstall package_name` |
| 搜索包 | `conda search package_name` |
| 列出已安装包 | `conda list` |
| 清理缓存 | `conda clean --all` |

---

## 八、与 venv/pip 的选择指南

```
需要特定 Python 版本？ ──是──→ conda
        │
        否
        │
需要 CUDA/MKL 等 C 库？ ──是──→ conda
        │
        否
        │
科学计算/数据分析？ ──是──→ conda
        │
        否
        │
Web 开发/纯 Python？ ──是──→ venv + pip
```
