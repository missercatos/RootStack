# 持续交付 02：GitHub Actions 多语言流水线

> 设计讲完要落到工具上。GitHub Actions 是目前多语言单仓最省事的选择：托管 runner 覆盖 Linux/macOS/Windows，官方 setup 动作覆盖主流语言，marketplace 里有现成的缓存与发布方案。**本章从核心概念一路写到可直接运行的完整多语言单仓工作流**。
>
> 前置知识：[[多语言工程化/6持续交付/01_CI_CD流水线设计|01 CI/CD 流水线设计]]（阶段划分、触发策略、缓存与制品原则）。

---

## 一、核心概念

| 概念 | 定义 | 关键点 |
|------|------|--------|
| workflow | 一个 `.github/workflows/*.yml` 文件 | 一个文件描述一条流水线 |
| job | 一组 step，跑在同一个 runner 上 | job 之间默认并行，用 `needs` 串行 |
| step | job 内最小执行单元 | 可以是 `run` 命令或 `uses` 动作 |
| action | 可复用的步骤封装 | 官方、社区或自建 |
| runner | 执行 job 的机器 | GitHub 托管或 self-hosted |
| event | 触发 workflow 的事件 | push、PR、tag、schedule、手动 |

```mermaid
flowchart TB
    E["event：push / PR / tag"] --> W["workflow（.github/workflows/ci.yml）"]
    W --> J1["job：build-cpp"]
    W --> J2["job：build-java"]
    W --> J3["job：test-python"]
    J1 --> S1["step：checkout"]
    S1 --> S2["step：run cmake --build"]
    J1 -.needs.-> J4["job：package（全部通过后执行）"]
```

job 之间**不共享文件系统**：每个 job 都在全新 runner 上开始，传递数据只能靠 artifacts 或缓存，这一点是初学者最常见的认知错误。

---

## 二、触发器与 path 过滤

```yaml
name: ci
on:
  pull_request:
    paths:
      - "cpp/**"
      - "java/**"
      - "python/**"
      - "dart/**"
      - "proto/**"
      - ".github/workflows/ci.yml"
  push:
    branches: [main]
    tags: ["v*"]
  schedule:
    - cron: "0 3 * * *"        # 每天 03:00 UTC 跑夜间全量
  workflow_dispatch:            # 手动补跑
```

monorepo 的 path 过滤有两种实现：**在触发器层过滤**（`on.pull_request.paths`）或**在 job 层过滤**（dorny/paths-filter 动作 + `if` 条件）。触发器层过滤会导致整个 workflow 跳过，适合「只有 Python 变更时连 workflow 都不启动」；job 层过滤更灵活，可以让「汇总 job」始终运行以提供必需的状态检查。

```yaml
      - uses: dorny/paths-filter@v3
        id: changes
        with:
          filters: |
            cpp:
              - "cpp/**"
              - "proto/**"
            java:
              - "java/**"
              - "proto/**"
      - name: 构建 C++
        if: steps.changes.outputs.cpp == 'true'
        run: cmake --build cpp/build
```

规则：`proto/**` 与共享库变更必须同时命中多个语言的过滤器，宁可多构建，不可漏下游。

---

## 三、matrix 策略

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false                 # 单点失败不取消其他组合
      matrix:
        os: [ubuntu-latest]
        language: [cpp, java, python, dart]
        include:
          - language: cpp
            setup: "sudo apt-get install -y cmake g++"
            test: "ctest --test-dir cpp/build --output-on-failure"
          - language: java
            setup: "java -version"
            test: "mvn -q test"
          - language: python
            setup: "pip install -e 'python[dev]'"
            test: "pytest -q python/tests"
          - language: dart
            setup: "dart pub get"
            test: "dart test"
    steps:
      - uses: actions/checkout@v4
      - name: 环境准备
        run: ${{ matrix.setup }}
      - name: 运行测试
        run: ${{ matrix.test }}
```

`include` 给每个矩阵项附加专属字段，`exclude` 可剔除组合。矩阵项数是笛卡尔积，**加一个维度可能让 job 数翻倍**，务必用 `include` 精确描述而不是堆维度。

---

## 四、各语言环境安装与缓存

| 语言 | 安装 action | 缓存路径 | 缓存键（示例） |
|------|-------------|----------|----------------|
| Node | `actions/setup-node@v4` | `~/.npm` | `node-${{ hashFiles('**/package-lock.json') }}` |
| Python | `actions/setup-python@v5` | `~/.cache/pip` | `pip-${{ hashFiles('**/requirements*.txt', '**/pyproject.toml') }}` |
| Java | `actions/setup-java@v4` | `~/.m2/repository` | `maven-${{ hashFiles('**/pom.xml') }}` |
| Go | `actions/setup-go@v5` | `~/go/pkg/mod` | `go-${{ hashFiles('**/go.sum') }}` |
| Rust | `dtolnay/rust-toolchain@stable` | `~/.cargo/registry`、`target/` | `cargo-${{ hashFiles('**/Cargo.lock') }}` |
| Dart | `subosito/flutter-action@v2` 或 `dart-lang/setup-dart@v1` | `~/.pub-cache` | `pub-${{ hashFiles('**/pubspec.lock') }}` |

多数 setup 动作自带 `cache: true`（setup-node、setup-python、setup-java、setup-go 均支持），优先使用内置缓存；Rust 与 Dart 需要配合 `Swatinem/rust-cache` 与 `actions/cache` 手动配置。

```yaml
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: "21"
          cache: maven                  # 内置缓存，等价于手动配 actions/cache
      - uses: actions/cache@v4
        with:
          path: ~/.pub-cache
          key: pub-${{ runner.os }}-${{ hashFiles('**/pubspec.lock') }}
          restore-keys: pub-${{ runner.os }}-
```

---

## 五、reusable workflow 与 composite action

### 5.1 两种封装对比

| 维度 | reusable workflow | composite action |
|------|-------------------|------------------|
| 复用粒度 | 整个 job 集合 | 一组 step |
| 定义位置 | `.github/workflows/*.yml` + `workflow_call` | 仓库任意目录 `action.yml` |
| 能否包含 job | 可以 | 只能包含 step |
| 调用方式 | `uses: org/repo/.github/workflows/x.yml@ref` | `uses: ./path/to/action` |
| 适用 | 跨仓库复用整条流水线 | 仓库内复用一段步骤 |

```yaml
# .github/workflows/reusable-build.yml —— 可复用工作流
on:
  workflow_call:
    inputs:
      language:
        required: true
        type: string

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make build-${{ inputs.language }}
```

```yaml
# 调用方
jobs:
  build-java:
    uses: ./.github/workflows/reusable-build.yml
    with: { language: java }
```

```yaml
# .github/actions/setup-toolchain/action.yml —— composite action
name: setup-toolchain
description: 安装项目所需的多语言工具链
runs:
  using: composite
  steps:
    - uses: actions/setup-java@v4
      with: { distribution: temurin, java-version: "21", cache: maven }
    - run: sudo apt-get install -y cmake g++
      shell: bash
```

注意：composite action 的每个 `run` 必须显式声明 `shell`。

---

## 六、artifacts 上传下载

```yaml
      - name: 上传 Java 制品
        uses: actions/upload-artifact@v4
        with:
          name: java-service-${{ github.sha }}
          path: java/service/target/*.jar
          retention-days: 14
          if-no-files-found: error

  deploy:
    needs: [build-java]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: java-service-${{ github.sha }}
          path: dist
```

v4 版本的 artifact **不允许同名覆盖**，命名里带 SHA 或矩阵变量是标准做法。跨 job 传大文件用 artifact；同一 job 内传文件用工作目录即可。

---

## 七、service containers

集成测试需要数据库、Redis、消息队列时，用 service container 起临时依赖，测试结束自动销毁：

```yaml
jobs:
  integration:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: app_test
        ports: ["5432:5432"]
        options: --health-cmd "pg_isready -U postgres" --health-interval 10s --health-retries 5
      redis:
        image: redis:7
        ports: ["6379:6379"]
    steps:
      - uses: actions/checkout@v4
      - run: pytest tests/integration
        env:
          DATABASE_URL: postgres://postgres:test@localhost:5432/app_test
          REDIS_URL: redis://localhost:6379
```

`options` 里的 healthcheck 必须有：否则 job 可能在数据库就绪前开始测试，产生随机失败。service container 只在 Linux runner 上可用，且端口映射到宿主机 localhost。

---

## 八、self-hosted runner 与缓存持久化

托管 runner 每次都是干净的，缓存必须显式保存与恢复；self-hosted runner 的磁盘持久，但**不能依赖上一轮残留**——同一台机器可能被不同 job 复用，状态不可控。

| 维度 | GitHub 托管 runner | self-hosted runner |
|------|--------------------|---------------------|
| 维护 | 零维护 | 需自行打补丁、监控、扩容 |
| 成本 | 按分钟计费 | 自有机器成本 |
| 环境定制 | 有限（可自定义镜像） | 完全可控 |
| 缓存 | actions/cache 走云存储 | 可挂载本地大盘，速度更快 |
| 安全 | 隔离好 | 公共仓库慎用（PR 可执行任意代码） |
| 适用 | 通用项目 | 大仓库、需要特殊硬件或内网访问 |

self-hosted 的缓存建议：把依赖目录挂载到固定磁盘路径，用 `actions/cache` 管理键但把 `path` 指向持久目录；构建容器内的工作目录每轮清理，避免脏状态。

---

## 九、完整多语言单仓示例

```yaml
# .github/workflows/monorepo-ci.yml
name: monorepo-ci
on: [pull_request, push]

jobs:
  changes:
    runs-on: ubuntu-latest
    outputs:
      cpp: ${{ steps.filter.outputs.cpp }}
      java: ${{ steps.filter.outputs.java }}
      python: ${{ steps.filter.outputs.python }}
      dart: ${{ steps.filter.outputs.dart }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            cpp: ["cpp/**", "proto/**"]
            java: ["java/**", "proto/**"]
            python: ["python/**", "proto/**"]
            dart: ["dart/**", "proto/**"]

  cpp:
    needs: changes
    if: needs.changes.outputs.cpp == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cmake -S cpp -B cpp/build -DCMAKE_BUILD_TYPE=Release
      - run: cmake --build cpp/build --parallel
      - run: ctest --test-dir cpp/build --output-on-failure

  java:
    needs: changes
    if: needs.changes.outputs.java == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: "21", cache: maven }
      - run: mvn -q -f java/pom.xml test

  python:
    needs: changes
    if: needs.changes.outputs.python == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12", cache: pip }
      - run: pip install -e "python[dev]"
      - run: pytest -q python/tests

  dart:
    needs: changes
    if: needs.changes.outputs.dart == 'true'
    runs-on: ubuntu-latest
    defaults: { run: { working-directory: dart } }
    steps:
      - uses: actions/checkout@v4
      - uses: dart-lang/setup-dart@v1
        with: { sdk: stable }
      - run: dart pub get
      - run: dart analyze --fatal-infos
      - run: dart test

  summary:
    needs: [cpp, java, python, dart]
    if: always()                     # 即使上游失败也运行，用于汇总状态
    runs-on: ubuntu-latest
    steps:
      - name: 检查所有子任务
        run: |
          if [[ "${{ contains(needs.*.result, 'failure') }}" == "true" ]]; then
            exit 1
          fi
          echo "全部通过"
```

关键设计：`changes` job 计算路径过滤结果，四个语言 job 按需运行，`summary` 汇总并保证「被跳过的 job 不会导致分支保护卡住」。

---

## 十、密钥与权限

```yaml
permissions:
  contents: read               # 默认最小权限，需要什么加什么
  packages: write              # 推送镜像时需要
  id-token: write              # OIDC 换取云厂商短期凭证

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/ci-deploy
        # 无需长期 AK/SK：GitHub OIDC 令牌换取临时凭证
```

| 机制 | 用途 | 注意 |
|------|------|------|
| `GITHUB_TOKEN` | 仓库内操作（打 tag、发 Release、推镜像） | 每个 job 自动生成，按 `permissions` 授权，任务结束即失效 |
| Repository Secrets | 长期密钥（签名密码、注册表 token） | 只在 workflow 中可用，日志自动脱敏 |
| Environment Secrets | 绑定环境的密钥（prod 单独一套） | 可配合环境保护规则强制审批 |
| OIDC | 免密钥换取云凭证 | 需云厂商配置信任策略，优先级最高 |

规则：**能用 OIDC 就不用长期密钥，能用 GITHUB_TOKEN 就不用 Personal Access Token**。第三方 action 必须锁定版本（`@v4` 或 commit SHA），避免上游被投毒后自动执行。

---

## 常见坑

1. **跨 job 找文件**：job 不共享文件系统，忘了 artifact 下载就会 `No such file`。
2. **path filter 写得太窄**：改了 `proto/` 没触发 Dart job，线上协议不匹配；共享路径必须列进所有相关过滤器。
3. **`if` 条件与 `needs` 冲突**：上游 job 被跳过时，下游 `needs` 默认也跳过；用 `if: always() && ...` 或 `!cancelled()` 明确处理。
4. **缓存键遗漏锁文件**：依赖升级后命中旧缓存；所有缓存键都要包含对应锁文件的哈希。
5. **service container 没健康检查**：测试随机连接失败；必须配置 `--health-cmd` 与重试。
6. **第三方 action 用分支引用**：`@main` 会被上游随时改变，存在供应链风险；锁定 tag 或 SHA。
7. **矩阵爆炸与供应链风险**：OS × 版本 × 语言的全组合可能几十个 job，只保留有意义的组合；第三方 action 锁定 tag 或 SHA，避免 `@main` 被投毒。

---

## 本章小结

- workflow/job/step/action/runner 五层概念中，job 之间不共享文件系统是设计一切数据流的前提；
- monorepo 用 path filter 或 paths-filter 动作实现受影响构建，共享路径（proto）必须触发全部下游；
- matrix 用 include/exclude 精确控制组合，警惕笛卡尔积导致的 job 爆炸；
- 跨仓库复用整条流水线用 reusable workflow，仓库内复用步骤用 composite action；
- artifacts 是跨 job 传制品的唯一正道，service container 是集成测试依赖的标准姿势；
- self-hosted 适合大仓库与内网，但不能依赖残留状态，公共仓库慎用；
- 权限最小化：OIDC 优先、GITHUB_TOKEN 次之、长期密钥最后，第三方 action 锁定版本。

---

## 动手实践

1. **单仓多语言流水线**：在本地建一个含 `cpp/`（CMake）、`python/`（pytest）、`dart/`（test）的 monorepo，照第九节写出工作流并推送到 GitHub。
   - 验收：只改 `python/` 时 C++ 与 Dart job 被跳过；改 `proto/` 时全部触发；summary 能正确报告结果。
2. **缓存对比实验**：给 Python 与 Dart 分别配置缓存，记录两次运行的耗时。
   - 验收：第二次命中缓存（日志出现 cache hit）；说明缓存丢失时任务仍能成功；缓存键包含锁文件哈希。
3. **集成测试环境**：为 Python 集成测试接入 postgres service container，并配置 healthcheck。
   - 验收：测试连接数据库成功；故意去掉 healthcheck 时能复现随机失败；说明端口映射与连接串写法。
4. **权限加固**：把示例工作流的权限收敛到最小，并用 OIDC（或模拟的短期凭证）替换一个长期密钥。
   - 验收：workflow 顶部 `permissions` 只保留必要项；长期密钥从 Secrets 中移除后流水线仍可完成部署步骤（或说明云侧信任策略配置）。

- 返回目录：[[多语言工程化/多语言工程化目录|多语言工程化]]
