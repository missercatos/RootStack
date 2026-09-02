# Docker 从零到实战

> 完整的 Docker 学习教程，从安装配置到项目容器化，覆盖全平台，面向终端用户。

---

## 目录

| 章节 | 文件 | 内容 |
|------|------|------|
| 01 | [安装与配置](01-安装与配置.md) | 全平台安装（Ubuntu/Fedora/Arch/macOS/Windows）、daemon.json 配置 |
| 02 | [核心概念与架构](02-核心概念与架构.md) | Docker 架构、镜像/容器/仓库、containerd/runc、OCI 标准 |
| 03 | [命令速查](03-命令速查.md) | 镜像/容器/网络/卷/系统/Compose 命令速查表 |
| 04 | [镜像原理与管理](04-镜像原理与管理.md) | 分层机制、构建、标签策略、多阶段构建、缓存优化、推送/导入导出 |
| 05 | [Dockerfile 详解](05-Dockerfile详解.md) | 指令详解、ENTRYPOINT vs CMD、最小基础镜像、安全扫描 |
| 06 | [网络](06-网络.md) | bridge/host/none/macvlan、自定义网络、端口映射、DNS、跨主机网络 |
| 07 | [存储与数据持久化](07-存储与数据持久化.md) | Volume/Bind Mount/tmpfs、备份恢复、数据迁移 |
| 08 | [Docker Compose](08-Docker-Compose.md) | compose.yaml 语法、多服务编排、环境变量、生产部署 |
| 09 | [项目容器化实战](09-项目容器化实战.md) | Python/Node/Java/Go 完整 Dockerfile + Compose 示例 |
| 10 | [镜像加速](10-镜像加速.md) | 国内镜像源配置、BuildKit 加速、代理配置、镜像瘦身 |
| 11 | [使用注意事项](11-使用注意事项.md) | 安全、资源限制、日志管理、清理策略、权限、内核兼容性 |
| 12 | [故障排查](12-故障排查.md) | 20+ 常见错误 + 解决方案速查表 |
| 13 | [Docker 与虚拟环境](13-Docker与虚拟环境.md) | Python venv、Node 版本管理、数据库环境、CI/CD |

---

## 学习路线

```
初学者：01 → 02 → 03 → 05 → 08 → 09
进阶者：04 → 06 → 07 → 10 → 11 → 12 → 13
```

---

## 与其他教程的关系

| 本教程 | 已有相关教程 | 区别 |
|--------|-------------|------|
| 本教程 | `linux/46-容器技术.md` | 46 是 Arch 专用 + 底层原理 + Podman；本教程是全平台通用 + 项目实战 |
| 本教程 | `linux/47-容器编排与K8s入门.md` | 47 是 K8s 编排；本教程是 Docker 基础 |
| 本教程 | `java/3工程化/12_Docker容器化.md` | 12 是 Java 专用；本教程覆盖多语言 |
| 本教程 | `python/10web应用/05_部署：gunicorn与Docker.md` | 05 是 Python 专用；本教程更全面 |

---

## 环境要求

- Docker 20.10+
- Docker Compose v2
- Linux/macOS/Windows（WSL2）
