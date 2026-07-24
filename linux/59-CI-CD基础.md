# 59 - CI/CD 基础

> CI/CD（持续集成/持续交付/持续部署）让代码从提交到上线的过程自动化、可重复、可追溯。开发者推送代码后自动构建、测试、打包、部署——无需手动 scp 或 rsync，减少人为失误。本章讲解 CI/CD 的核心概念，并通过 GitLab CI 和 GitHub Actions 两个最主流的平台构建可落地的流水线。

---

## 59.1 理解 CI/CD

### 概念区分

```
CI  (Continuous Integration) 持续集成
    └─ 开发者频繁提交代码 → 自动构建 + 测试 → 尽早发现集成问题

CD  (Continuous Delivery) 持续交付
    └─ CI 通过后 → 自动打包为可部署的工件 → 手动触发部署

CD  (Continuous Deployment) 持续部署
    └─ CI 通过后 → 自动部署到生产环境 → 无需人工干预
```

### 典型 CI/CD 流水线

```
Push Code → [Build] → [Test] → [Package] → [Deploy Staging] → [Deploy Prod]
             └─ FAIL   └─ FAIL    └─ Manual Approval ─┘
                                                          └─ Canary / Blue-Green
```

### 为什么需要 CI/CD

| 传统方式 | CI/CD 后 |
|---------|---------|
| 手动上传文件 | 自动构建部署 |
| 忘记跑测试 | 流水线自动执行 |
| "在我机器上能跑" | 容器化标准环境 |
| 凌晨手动上线 | 定时或事件触发 |
| 部署出问题难回滚 | 版本化，一键回滚 |
| 谁改了什么不知道 | 每次提交都有部署记录 |

---

## 59.2 GitLab CI

GitLab CI 是 GitLab 内置的 CI/CD 系统，配置文件为 `.gitlab-ci.yml`，存放在仓库根目录。

### 基本概念

| 概念 | 说明 |
|------|------|
| **Pipeline** | 一次 CI/CD 运行的完整流程 |
| **Stage** | 流水线的阶段（如 build、test、deploy） |
| **Job** | Stage 中的具体任务，可并行执行 |
| **Runner** | 执行 Job 的环境（shell、Docker、k8s） |
| **Artifact** | Job 产出的文件，可传递给后续 Stage |
| **Cache** | 缓存依赖，加速后续运行 |
| **Environment** | 部署目标环境（staging/production） |

### 安装 GitLab Runner

```bash
# Debian / Ubuntu
curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | sudo bash
sudo apt install gitlab-runner

# RHEL / Fedora
curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.rpm.sh" | sudo bash
sudo dnf install gitlab-runner

# 注册 Runner 到 GitLab
sudo gitlab-runner register
# 输入 GitLab URL、registration token、描述、tag、executor 类型
# executor 推荐：shell（简单）、docker（隔离好）
```

### .gitlab-ci.yml 示例

```yaml
# .gitlab-ci.yml — 前端项目示例
stages:
  - build
  - test
  - deploy

variables:
  APP_NAME: "my-frontend"

# === Build Stage ===
build:
  stage: build
  image: node:20
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - node_modules/
  script:
    - npm install
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 1 week

# === Test Stage ===
lint:
  stage: test
  image: node:20
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - node_modules/
    policy: pull           # 只拉缓存不写入
  script:
    - npm install
    - npm run lint

unit-test:
  stage: test
  image: node:20
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - node_modules/
    policy: pull
  script:
    - npm install
    - npm run test:unit

# === Deploy Stage ===
deploy-staging:
  stage: deploy
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh-client rsync
    - mkdir -p ~/.ssh
    - echo "$SSH_PRIVATE_KEY" | tr -d '\r' > ~/.ssh/id_rsa
    - chmod 600 ~/.ssh/id_rsa
    - ssh-keyscan $STAGING_HOST >> ~/.ssh/known_hosts
  script:
    - rsync -avz --delete dist/ user@$STAGING_HOST:/var/www/$APP_NAME/
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - develop

deploy-production:
  stage: deploy
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh-client rsync
    - mkdir -p ~/.ssh
    - echo "$PROD_SSH_PRIVATE_KEY" | tr -d '\r' > ~/.ssh/id_rsa
    - chmod 600 ~/.ssh/id_rsa
    - ssh-keyscan $PROD_HOST >> ~/.ssh/known_hosts
  script:
    - rsync -avz --delete dist/ user@$PROD_HOST:/var/www/$APP_NAME/
  environment:
    name: production
    url: https://example.com
  only:
    - main
  when: manual
```

### 变量与密钥管理

在 GitLab 项目 → Settings → CI/CD → Variables 中配置：

```
SSH_PRIVATE_KEY     — 部署服务器的 SSH 私钥
STAGING_HOST        — 预发布服务器 IP
PROD_HOST           — 生产服务器 IP
```

在 `.gitlab-ci.yml` 中引用：
```yaml
script:
  - ssh user@$STAGING_HOST "sudo systemctl restart nginx"
```

---

## 59.3 GitHub Actions

GitHub Actions 是 GitHub 的 CI/CD 平台，配置文件位于 `.github/workflows/`，YAML 格式。

### 基本概念

| 概念 | 说明 |
|------|------|
| **Workflow** | 一个自动化流程（一个 YAML 文件） |
| **Event** | 触发 workflow 的事件（push、PR、schedule） |
| **Job** | 在同一个 runner 上执行的一组步骤 |
| **Step** | 单个操作（run 命令 或 uses 外部 action） |
| **Runner** | 执行环境（ubuntu-latest、windows-latest、self-hosted） |
| **Action** | 可复用的打包步骤（市场有数千个） |

### workflow YAML 示例

```yaml
# .github/workflows/deploy.yml
name: Build and Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:        # 允许手动触发

env:
  APP_NAME: my-frontend
  NODE_VERSION: '20'

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Unit tests
        run: npm run test:unit

      - name: Build
        run: npm run build

      - name: Upload build artifact
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
          retention-days: 7

  deploy-staging:
    needs: build-and-test
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - name: Download artifact
        uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/

      - name: Deploy to staging
        uses: easingthemes/ssh-deploy@v4
        with:
          SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
          REMOTE_HOST: ${{ vars.STAGING_HOST }}
          REMOTE_USER: deploy
          TARGET: /var/www/app/
          SOURCE: dist/

  deploy-production:
    needs: build-and-test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Download artifact
        uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/

      - name: Deploy to production
        uses: easingthemes/ssh-deploy@v4
        with:
          SSH_PRIVATE_KEY: ${{ secrets.PROD_SSH_KEY }}
          REMOTE_HOST: ${{ vars.PROD_HOST }}
          REMOTE_USER: deploy
          TARGET: /var/www/app/
          SOURCE: dist/
      # 部署后重启 Nginx（可选）
      # - name: Reload Nginx
      #   run: |
      #     ssh deploy@${{ vars.PROD_HOST }} "sudo systemctl reload nginx"
```

### 环境与密钥

在 GitHub 仓库 → Settings → Secrets and variables → Actions：

```
Secrets（加密）:   SSH_PRIVATE_KEY, PROD_SSH_KEY, DB_PASSWORD
Variables（明文）: STAGING_HOST, PROD_HOST, APP_NAME
```

### 定时执行

```yaml
on:
  schedule:
    - cron: '0 2 * * 0'     # 每周日凌晨 2 点（UTC）
```

### Matrix 策略（多环境测试）

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18, 20, 22]
        os: [ubuntu-latest, macos-latest]
    steps:
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm ci && npm test
```

---

## 59.4 部署模式详解

### SSH + rsync（简单直接）

```yaml
# GitLab CI
deploy:
  script:
    - rsync -avz --delete dist/ deploy@$SERVER:/var/www/app/
    - ssh deploy@$SERVER "sudo systemctl reload nginx"
```

```yaml
# GitHub Actions — 使用 ssh-action
- name: Deploy via SSH
  uses: appleboy/ssh-action@v1
  with:
    host: ${{ secrets.HOST }}
    username: deploy
    key: ${{ secrets.SSH_KEY }}
    script: |
      cd /var/www/app
      git pull origin main
      npm ci --production
      sudo systemctl restart app
```

### Docker 部署

```yaml
# GitLab CI — 构建 Docker 镜像并推送
docker-build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t registry.example.com/$CI_PROJECT_NAME:$CI_COMMIT_SHA .
    - docker push registry.example.com/$CI_PROJECT_NAME:$CI_COMMIT_SHA
    - docker tag registry.example.com/$CI_PROJECT_NAME:$CI_COMMIT_SHA \
               registry.example.com/$CI_PROJECT_NAME:latest
    - docker push registry.example.com/$CI_PROJECT_NAME:latest

docker-deploy:
  stage: deploy
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh-client
  script:
    - ssh deploy@$SERVER "docker pull registry.example.com/app:latest &&
      docker-compose -f /opt/app/docker-compose.yml up -d"
```

### Ansible 部署

```yaml
# GitLab CI — 使用 Ansible 部署
deploy:
  stage: deploy
  image: python:3.12
  before_script:
    - pip install ansible
    - echo "$ANSIBLE_VAULT_PASSWORD" > .vault_pass
    - mkdir -p ~/.ssh && echo "$SSH_KEY" > ~/.ssh/id_rsa && chmod 600 ~/.ssh/id_rsa
  script:
    - ansible-playbook -i inventory/production deploy.yml --vault-password-file .vault_pass
```

详见 [[60-Ansible与配置管理]] 和 [[44-容器技术]]。

---

## 59.5 完整实战：静态站点 CI/CD

### 项目结构

```
my-site/
├── .github/workflows/
│   └── deploy.yml
├── .gitlab-ci.yml
├── src/
│   └── index.html
├── package.json
├── nginx-config/
│   └── my-site.conf
└── scripts/
    └── deploy.sh
```

### 本地部署脚本

```bash
#!/bin/bash
# scripts/deploy.sh
set -euo pipefail

APP_NAME="my-site"
DEPLOY_USER="deploy"
DEPLOY_HOST="${1:?请提供目标主机 IP}"
DEPLOY_PATH="/var/www/${APP_NAME}"

echo "=== Build ==="
npm ci
npm run build

echo "=== Deploy to ${DEPLOY_HOST} ==="
rsync -avz --delete dist/ "${DEPLOY_USER}@${DEPLOY_HOST}:${DEPLOY_PATH}/"

echo "=== Reload Nginx ==="
ssh "${DEPLOY_USER}@${DEPLOY_HOST}" "sudo nginx -t && sudo systemctl reload nginx"

echo "=== Done ==="
```

### GitHub Actions 完整工作流

```yaml
# .github/workflows/deploy.yml
name: Build and Deploy Static Site

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: '部署环境'
        type: choice
        options:
          - staging
          - production
        default: staging

env:
  NODE_VERSION: '20'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      - run: npm ci
      - run: npm run lint || true
      - run: npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: site-dist
          path: dist/

  preview:      # 在 PR 中生成预览链接（使用 Netlify 或类似服务）
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    needs: build
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: site-dist
          path: dist/
      - name: Deploy preview
        run: |
          echo "Preview deployment placeholder"
          # 可集成 Netlify CLI、Cloudflare Pages 等
          # npx netlify-cli deploy --dir=dist --alias=pr-${{ github.event.number }}

  deploy:
    if: github.ref == 'refs/heads/main' && github.event_name != 'pull_request'
    runs-on: ubuntu-latest
    needs: build
    environment:
      name: ${{ github.event.inputs.environment || 'production' }}
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: site-dist
          path: dist/
      - name: Deploy to server
        uses: easingthemes/ssh-deploy@v4
        with:
          SSH_PRIVATE_KEY: ${{ secrets.DEPLOY_SSH_KEY }}
          REMOTE_HOST: ${{ vars.DEPLOY_HOST }}
          REMOTE_USER: ${{ vars.DEPLOY_USER }}
          TARGET: ${{ vars.DEPLOY_PATH }}
          SOURCE: dist/
```

### GitLab CI 对应配置

```yaml
# .gitlab-ci.yml
stages:
  - build
  - deploy

variables:
  NODE_VERSION: "20"

build:
  stage: build
  image: node:${NODE_VERSION}
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - node_modules/
  script:
    - npm ci
    - npm run build
    - npm run lint
  artifacts:
    paths:
      - dist/
    expire_in: 1 week
  only:
    - main
    - merge_requests

deploy:
  stage: deploy
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh-client rsync
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
    - mkdir -p ~/.ssh && chmod 700 ~/.ssh
    - ssh-keyscan $DEPLOY_HOST >> ~/.ssh/known_hosts
    - chmod 600 ~/.ssh/known_hosts
  script:
    - rsync -avz --delete dist/ deploy@$DEPLOY_HOST:/var/www/site/
    - ssh deploy@$DEPLOY_HOST "sudo nginx -t && sudo systemctl reload nginx"
  only:
    - main
  when: manual           # 手动触发部署到生产
```

---

## 59.6 Pipeline 优化技巧

### 缓存依赖加速

```yaml
# GitLab CI
cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - node_modules/
    - .npm/

# GitHub Actions
- uses: actions/setup-node@v4
  with:
    cache: 'npm'
```

### 并行 Stage

```yaml
stages:
  - build
  - test         # lint、unit-test、integration-test 并行
  - deploy

lint:
  stage: test
  script: npm run lint

unit-test:
  stage: test
  script: npm run test:unit
# lint 和 unit-test 在 test stage 中并行执行
```

### 条件执行

```yaml
# GitLab CI
deploy:
  only:
    - main
  except:
    - tags

deploy-hotfix:
  only:
    - /^hotfix-.*$/

# GitHub Actions
deploy:
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
```

### 多项目触发（CI/CD 链）

```yaml
# GitLab CI — 触发下游项目的 pipeline
trigger-api-tests:
  stage: deploy
  trigger:
    project: mygroup/e2e-tests
    branch: main
  variables:
    TARGET_URL: https://staging.example.com
```

---

## 59.7 自我托管 Runner

### GitLab Runner（Docker）

```bash
# 安装
curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | sudo bash
sudo apt install gitlab-runner

# 注册为 Docker executor（推荐）
sudo gitlab-runner register -n \
  --url https://gitlab.example.com/ \
  --registration-token <TOKEN> \
  --executor docker \
  --docker-image alpine:latest \
  --docker-privileged \
  --description "docker-runner-01" \
  --tag-list "docker,linux"
```

### GitHub Actions Self-Hosted Runner

```bash
# 在 GitHub 仓库 → Settings → Actions → Runners → New self-hosted runner
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64.tar.gz -L <下载URL>
tar xzf actions-runner-linux-x64.tar.gz
./config.sh --url https://github.com/org/repo --token <TOKEN>
./run.sh

# 作为服务运行
sudo ./svc.sh install
sudo ./svc.sh start
```

---

## 59.8 CI/CD 安全实践

```yaml
# 1. 永远不在 YAML 中硬编码密钥，使用 Secrets
script:
  - echo "$DB_PASSWORD" | docker login -u admin --password-stdin

# 2. 限制部署条件
deploy-prod:
  only:
    - main
  when: manual
  environment: production

# 3. 依赖版本锁定
# 使用 npm ci（而非 npm install）、pip install -r requirements.txt（锁定版本）
# CI 中的 npm ci 严格按 package-lock.json 安装

# 4. 最小权限 Runner
# Docker executor：禁止 privileged 模式
# Shell executor：使用非 root 用户运行

# 5. 审计 pipeline 日志
# GitLab：Settings → CI/CD → Pipeline logs
# GitHub：Actions → workflow runs → 查看每个 run
```

---

## 59.9 本章总结

| 维度 | GitLab CI | GitHub Actions |
|------|-----------|---------------|
| 配置方式 | `.gitlab-ci.yml` 在项目根目录 | `.github/workflows/*.yml` |
| Runner 类型 | Shared + Self-hosted | GitHub-hosted + Self-hosted |
| 定时执行 | `schedule` 关键字 | `schedule` 事件 |
| 手动触发 | `when: manual` | `workflow_dispatch` |
| 环境管理 | Environment 页面 | Environment 页面 + protection rules |
| 市场复用 | 无官方市场 | GitHub Actions Marketplace |
| Secret 管理 | Variables + Masking | Secrets + Variables |
| 容器 registry | 内置 Container Registry | GitHub Packages |

### 选择参考

| 场景 | 推荐 |
|------|------|
| 使用 GitLab 托管代码 | GitLab CI（原生集成度最高） |
| 使用 GitHub 托管代码 | GitHub Actions（生态最丰富） |
| 需要本地 Runner | 两者都支持 |
| 团队熟悉 Shell 脚本 | GitLab CI（语法更接近脚本） |
| 追求 Marketplace 复用 | GitHub Actions |

> 自动化配置管理见 [[60-Ansible与配置管理]]，容器化部署见 [[44-容器技术]]，Kubernetes CI/CD 见 [[45-容器编排与K8s入门]]。
