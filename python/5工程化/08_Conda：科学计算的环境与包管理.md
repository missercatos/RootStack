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
# Linux
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# macOS (Intel)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
bash Miniconda3-latest-MacOSX-x86_64.sh

# macOS (Apple Silicon)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
bash Miniconda3-latest-MacOSX-arm64.sh
```

### 2.2 安装交互流程

```bash
# 安装脚本会依次提示：
$ bash Miniconda3-latest-Linux-x86_64.sh

# 1. 查看许可协议（按回车滚动）
# 输入 yes 接受许可协议

# 2. 确认安装路径
# 默认路径：~/miniconda3
# 按回车确认，或输入自定义路径

# 3. 初始化 Miniconda
# 是否运行 conda init？（推荐 yes）
# 输入 yes，它会自动修改 ~/.bashrc

# 4. 安装完成后重新加载 shell
source ~/.bashrc   # Linux
# source ~/.zshrc  # macOS (zsh)
```

### 2.3 验证安装

```bash
conda --version
# conda 24.x.x

# 查看 conda 配置
conda config --show

# 查看 Python 版本
python --version
```

### 2.4 接受条款（批量操作）

```bash
# 如果需要静默安装（如脚本自动化）
bash Miniconda3-latest-Linux-x86_64.sh -b -p ~/miniconda3
# -b = batch mode（不进入交互）
# -p = 指定安装路径

# 安装后初始化
~/miniconda3/bin/conda init bash
source ~/.bashrc
```

---

## 三、Conda 初始化

### 3.1 什么是 conda init

`conda init` 会修改 shell 配置文件（`~/.bashrc`、`~/.zshrc` 等），添加一段初始化代码，
使得 `conda activate` 和 `conda deactivate` 命令可用。

```bash
# 手动初始化（如果安装时跳过了）
conda init bash       # for bash
conda init zsh        # for zsh
conda init fish       # for fish
conda init powershell # for PowerShell

# 初始化后需要重新加载 shell
source ~/.bashrc
```

### 3.2 初始化做了什么

```bash
# conda init 会在 ~/.bashrc 末尾添加类似以下内容：
 >>> conda initialize >>>
 # !! Contents within this block are managed by 'conda init' !!
 __conda_setup="$('/home/user/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
 if [ $? -eq 0 ]; then
     eval "$__conda_setup"
 else
     if [ -f "/home/user/miniconda3/etc/profile.d/conda.sh" ]; then
         . "/home/user/miniconda3/etc/profile.d/conda.sh"
     else
         export PATH="/home/user/miniconda3/bin:$PATH"
     fi
 fi
 unset __conda_setup
 <<< conda initialize <<<
```

### 3.3 禁止自动激活 base 环境

conda 安装后默认会自动激活 `base` 环境，这会让终端提示符变长且可能影响 venv 使用。

```bash
# 禁止自动激活 base
conda config --set auto_activate_base false

# 验证配置
conda config --show | grep auto_activate_base
# auto_activate_base: False

# 恢复自动激活
conda config --set auto_activate_base true
```

### 3.4 手动激活/退出 base

```bash
# 禁止自动激活后，需要手动激活
conda activate base    # 手动激活
conda deactivate       # 退出

# 或者直接激活其他环境
conda activate myenv   # 直接跳到目标环境
```

---

## 四、配置国内镜像源

### 4.1 清华镜像（推荐）

```bash
# 添加清华镜像源
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/
conda config --set show_channel_urls yes
```

### 4.2 中科大镜像

```bash
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/conda-forge/
conda config --set show_channel_urls yes
```

### 4.3 查看当前源

```bash
conda config --show channels
# channels:
#   - https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
#   - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
#   - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
#   - defaults
```

### 4.4 恢复默认源

```bash
conda config --remove-key channels
```

### 4.5 直接编辑配置文件

```bash
# 配置文件位置
~/.condarc   # 用户级配置

# 查看配置文件
cat ~/.condarc
```

```yaml
# ~/.condarc 完整示例
channels:
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
  - defaults
show_channel_urls: true
auto_activate_base: false
solver: libmamba
```

---

## 五、创建虚拟环境

### 5.1 创建指定 Python 版本的环境

```bash
# 创建 Python 3.10 环境
conda create -n myenv python=3.10

# 创建环境并指定精确版本
conda create -n myenv python=3.10.12

# 创建环境并预装包
conda create -n myenv python=3.10 numpy pandas

# 创建环境时不自动激活
conda create -n myenv python=3.10 --no-default-packages

# 静默创建（不交互确认）
conda create -n myenv python=3.10 -y
```

### 5.2 激活/退出环境

```bash
# 激活环境
conda activate myenv

# 退出当前环境
conda deactivate

# 退出多层嵌套环境（连续 deactivate）
conda deactivate
conda deactivate   # 如果嵌套了两层

# 查看当前激活的环境
conda info --envs
# 当前环境前会有 * 号
# # conda environments:
# #
# base                  *  /home/user/miniconda3
# myenv                    /home/user/miniconda3/envs/myenv
```

### 5.3 按需自动激活环境

> 进入项目目录时自动激活对应环境，离开时自动退出。

```bash
# 方法一：使用 direnv（推荐）

# 安装 direnv
sudo apt install direnv   # Debian/Ubuntu
brew install direnv       # macOS

# 配置 bash
echo 'eval "$(direnv hook bash)"' >> ~/.bashrc

# 在项目目录创建 .envrc
cd ~/myproject
echo 'conda activate py310' > .envrc
direnv allow

# 现在进入 ~/myproject 会自动激活 py310
# 离开目录自动 deactivate
```

```bash
# 方法二：使用 conda-autoenv（社区工具）
pip install autoenv
echo 'source /path/to/autoenv/activate.sh' >> ~/.bashrc

# 在项目目录创建 .conda-init
cd ~/myproject
echo 'conda activate py310' > .conda-init
```

### 5.4 管理环境

```bash
# 列出所有环境
conda env list

# 复制环境
conda create -n myenv_copy --clone myenv

# 导出环境（用于分享/复现）
conda env export > environment.yml

# 仅导出手动安装的包（不含依赖）
conda env export --from-history > environment-minimal.yml

# 从 yml 文件创建环境
conda env create -n newenv -f environment.yml

# 更新环境
conda env update -n myenv -f environment.yml

# 重命名环境
conda rename -n old_name new_name

# 删除环境
conda env remove -n myenv
```

---

## 六、Mamba：Conda 的加速版

> Mamba 是 conda 的 C++ 重写版本，解析依赖速度比 conda 快 10-100 倍。

### 6.1 安装 Mamba

```bash
# 在 base 环境中安装 mamba
conda install -n base conda-libmamba-solver

# 或直接安装 mamba（推荐）
conda install -n base -c conda-forge mamba
```

### 6.2 使用 Mamba

```bash
# mamba 命令与 conda 完全兼容，直接替换即可
mamba create -n myenv python=3.10
mamba activate myenv
mamba install numpy pandas scikit-learn
mamba search numpy
mamba env list
```

### 6.3 设置 mamba 为默认求解器

```bash
# 让 conda 使用 mamba 作为求解器
conda config --set solver libmamba

# 验证
conda config --show | grep solver
# solver: libmamba
```

### 6.4 Mamba vs Conda 速度对比

| 操作 | conda | mamba |
|------|-------|-------|
| `create -n env python=3.10` | ~60s | ~5s |
| `install pytorch` | ~120s | ~15s |
| `update --all` | ~90s | ~10s |

---

## 七、安装包

### 7.1 使用 conda install

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

# 安装多个包
conda install numpy pandas matplotlib -y
```

### 7.2 使用 pip（conda 环境内）

```bash
# conda 环境内可以使用 pip
conda activate myenv
pip install requests  # 从 PyPI 安装

# 注意：conda install 优先，pip install 作为补充
# 如果 conda 有该包，优先用 conda install
# pip 安装的包 conda 无法管理，可能造成依赖冲突
```

### 7.3 管理已安装包

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

## 八、实战：创建 Python 3.10 + PyTorch 环境

### 8.1 创建环境

```bash
# 创建 Python 3.10 环境
conda create -n py310 python=3.10 -y
conda activate py310

# 安装 PyTorch（CUDA 11.8）
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia

# 或从 conda-forge 安装
conda install -c conda-forge pytorch torchvision torchaudio
```

### 8.2 验证安装

```bash
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
# 2.x.x
# True
```

### 8.3 导出环境

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

## 九、常见问题

### 9.1 conda activate 不生效

```bash
# 错误：CommandNotFoundError: Command 'conda' not found
# 原因：conda init 未执行

# 解决：
conda init bash
source ~/.bashrc
```

### 9.2 conda 安装太慢

```bash
# 方法一：使用国内镜像（见 §四）
# 方法二：使用 mamba（见 §六）
# 方法三：设置超时时间
conda config --set remote_read_timeout_secs 600
```

### 9.3 conda 和 venv 混用

```bash
# 不建议混用，但可以在 conda 环境内创建 venv
conda activate myenv
python -m venv .venv  # 不推荐，多此一举

# 推荐：用 conda 管理环境，pip 作为补充
conda activate myenv
pip install some_package  # OK
```

### 9.4 清理无用包

```bash
# 清理不再需要的包
conda clean --all

# 查看环境占用空间
du -sh ~/miniconda3/envs/myenv
```

### 9.5 环境损坏修复

```bash
# 如果环境无法激活
conda activate myenv
# 报错：CondaError: Run 'conda init' first

# 尝试重建
conda env remove -n myenv
conda create -n myenv python=3.10
```

---

## 十、Conda 命令速查

| 操作 | 命令 |
|------|------|
| 创建环境 | `conda create -n env_name python=3.10` |
| 静默创建 | `conda create -n env_name python=3.10 -y` |
| 激活环境 | `conda activate env_name` |
| 退出环境 | `conda deactivate` |
| 列出环境 | `conda env list` |
| 删除环境 | `conda env remove -n env_name` |
| 重命名环境 | `conda rename -n old new` |
| 复制环境 | `conda create -n copy --clone original` |
| 导出环境 | `conda env export > environment.yml` |
| 精简导出 | `conda env export --from-history > min.yml` |
| 从 yml 创建 | `conda env create -f environment.yml` |
| 安装包 | `conda install package_name` |
| 指定版本 | `conda install package_name=1.0` |
| 从 conda-forge 安装 | `conda install -c conda-forge package_name` |
| 更新包 | `conda update package_name` |
| 卸载包 | `conda uninstall package_name` |
| 搜索包 | `conda search package_name` |
| 列出已安装包 | `conda list` |
| 清理缓存 | `conda clean --all` |
| 禁止自动激活 base | `conda config --set auto_activate_base false` |
| 设置 mamba 求解器 | `conda config --set solver libmamba` |
| 初始化 shell | `conda init bash` |

---

## 十一、与 venv/pip 的选择指南

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
