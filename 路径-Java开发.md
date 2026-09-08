## 路径 -- Java 开发

> 本路径面向想直接进入全栈开发的学习者，以 Java 为后端核心语言。Java 是全球企业级开发的第一语言——银行、保险、电商、电信的后端系统绝大多数由 Java 构建，Spring 生态灵活庞大，从 Web 服务、数据访问到安全认证均有成熟方案。
>
> 本路径覆盖 **Java 全栈**（语言入门 → 深入特性 → 工程化与 Spring 全家桶 → 前端闭环）。

---

### 目标受众

| 维度 | 描述 |
|------|------|
| 目标 | Java 后端工程师、全栈开发者、企业级应用开发 |
| 前置 | 零基础可入门；有其他语言经验者可加速通过 |
| 适用人群 | 想以就业为导向系统学习 Java 的学生与转行者；需要补全 Spring 工程能力的初级开发者 |
| 建议周期 | 约 28 周（7 个月左右，含实战项目） |

---

### 学习路线总览

```mermaid
flowchart TD
    P0[Phase 0 环境准备<br/>JDK安装/IDE选择] --> P1[Phase 1 语言入门<br/>语法/流程控制]
    P1 --> P2[Phase 2 OOP 核心<br/>类/继承/多态/接口]
    P2 --> P3[Phase 3 异常 IO 与巩固<br/>练习巩固]
    P3 --> P4[Phase 4 语言深入<br/>泛型/反射/集合/并发/JVM]
    P4 --> P5[Phase 5 进阶能力<br/>调优/Stream/NIO/设计模式]
    P5 --> P6[Phase 6 工具链与数据库<br/>Maven/Gradle/JDBC/MyBatis]
    P6 --> P7[Phase 7 Spring 体系<br/>IoC/MVC/Boot/JPA/Security]
    P7 --> P8[Phase 8 生产级工程<br/>日志/测试/Docker/CI/性能]
    P8 --> P9[Phase 9 全栈实战与架构<br/>项目/微服务/部署]
```

---

### Phase 0: 环境准备 (建议 3-4 天)

| 序号 | 文件 | 核心内容 | 建议学时 |
|:----:|------|---------|:-------:|
| 1 | [[java/java目录|Java 目录]] | 教程总索引，先通读建立全局地图 | 0.5h |
| 2 | [[java/1入门/00_Java是什么|00 Java 是什么]] | 语言定位、JVM/JRE/JDK 关系、生态概览 | 2h |
| 3 | [[java/1入门/01_Windows环境配置|01 Windows 环境配置]] | JDK 安装、JAVA_HOME 与 PATH 配置 | 2h |
| 4 | [[java/1入门/02_Linux环境配置|02 Linux 环境配置]] | apt/yum 安装、多版本管理 (update-alternatives) | 2h |
| 5 | [[java/1入门/03_macOS环境配置|03 macOS 环境配置]] | Homebrew 安装、SDKMAN 多版本切换 | 2h |
| 6 | [[java/1入门/04_编辑器与IDE选择|04 编辑器与 IDE 选择]] | IDEA 安装与常用设置、VS Code 备选方案 | 2h |

> **检查点**: `java -version` 与 `javac -version` 输出正确版本；能用 IDEA 新建项目并运行第一个类；能解释 JDK、JRE、JVM 三者关系。

---

### Phase 1: 语言入门 (约 3 周)

| 序号 | 文件 | 核心内容 | 建议学时 |
|:----:|------|---------|:-------:|
| 1 | [[java/1入门/05_第一个程序与jshell|05 第一个程序与 jshell]] | main 方法结构、编译运行流程、jshell 交互式实验 | 3h |
| 2 | [[java/1入门/06_变量与数据类型|06 变量与数据类型]] | 八大基本类型、引用类型、类型转换、var | 4h |
| 3 | [[java/1入门/07_运算符与表达式|07 运算符与表达式]] | 算术/关系/逻辑/位运算、短路求值、优先级 | 3h |
| 4 | [[java/1入门/08_条件语句|08 条件语句]] | if/else、switch 表达式（箭头语法） | 3h |
| 5 | [[java/1入门/09_循环结构|09 循环结构]] | for/while/do-while/break/continue、嵌套循环 | 4h |

> **检查点**: 能独立写出猜数字游戏、九九乘法表、简单 ATM 菜单循环三个小程序；能解释基本类型与引用类型在内存中的区别。

### Phase 2: OOP 核心 (约 3 周)

| 序号 | 文件 | 核心内容 | 建议学时 |
|:----:|------|---------|:-------:|
| 1 | [[java/1入门/10_数组|10 数组]] | 一维/二维数组、遍历、Arrays 工具类 | 3h |
| 2 | [[java/1入门/11_字符串|11 字符串]] | String 不可变性、StringBuilder、常用 API | 4h |
| 3 | [[java/1入门/12_方法|12 方法]] | 参数传递、重载、递归、可变参数 | 3h |
| 4 | [[java/1入门/13_类与对象|13 类与对象]] | 字段/方法/构造器、this、封装与访问控制 | 5h |
| 5 | [[java/1入门/14_继承与多态|14 继承与多态]] | extends/super、方法重写、向上转型、动态绑定 | 5h |
| 6 | [[java/1入门/15_接口与抽象类|15 接口与抽象类]] | interface/default 方法、抽象类、面向接口编程 | 5h |

> **检查点**: 能设计一个"图形"继承体系（Shape -> Circle/Rect）体现多态；能用接口 + 实现类重构一段 if-else 分支逻辑；能解释重载与重写的区别。

---

### Phase 3: 异常 IO 与巩固 (约 2 周)

| 序号 | 文件 | 核心内容 | 建议学时 |
|:----:|------|---------|:-------:|
| 1 | [[java/1入门/16_异常处理|16 异常处理]] | try-catch-finally、受检/非受检异常、try-with-resources | 4h |
| 2 | [[java/1入门/17_文件IO|17 文件 IO]] | File/Path、字节流/字符流、缓冲流、序列化 | 5h |
| 3 | 练习巩固 | 见下方练习路线 | 持续 |

> **检查点**: 能解释受检异常与非受检异常的设计意图；能读写文本文件并正确关闭资源。

---

### Phase 4: 语言深入 (约 4 周)

| 序号 | 文件 | 核心内容 | 建议学时 |
|:----:|------|---------|:-------:|
| 1 | [[java/2深入/01_泛型深入|01 泛型深入]] | 类型擦除、通配符上下界、泛型方法 | 6h |
| 2 | [[java/2深入/02_注解与反射|02 注解与反射]] | Class 对象、Method/Field、自定义注解——Spring 的基石 | 6h |
| 3 | [[java/2深入/03_集合框架深入|03 集合框架深入]] | ArrayList/HashMap 源码、扩容机制、ConcurrentHashMap | 8h |
| 4 | [[java/2深入/04_多线程基础|04 多线程基础]] | Thread/Runnable、synchronized、volatile、线程通信 | 8h |
| 5 | [[java/2深入/05_并发包与线程池|05 并发包与线程池]] | JUC、Lock/Condition、ThreadPoolExecutor 七参数 | 8h |
| 6 | [[java/2深入/06_JVM内存模型|06 JVM 内存模型]] | 堆/栈/方法区、GC 基础、类加载机制 | 8h |

> **检查点**: 能画出 HashMap put 流程并解释 1.8 的红黑树化条件；能手写一个生产者-消费者模型；能解释 volatile 可见性与指令重排的关系。

---

### Phase 5: 进阶能力 (约 3 周)

| 序号 | 文件 | 核心内容 | 建议学时 |
|:----:|------|---------|:-------:|
| 1 | [[java/2深入/07_JVM调优|07 JVM 调优]] | 常用参数、jstat/jmap/jstack、GC 日志分析 | 6h |
| 2 | [[java/2深入/08_Stream与函数式|08 Stream 与函数式]] | Lambda、函数式接口、Stream API、Optional | 6h |
| 3 | [[java/2深入/09_NIO与网络编程|09 NIO 与网络编程]] | Buffer/Channel/Selector、Socket 编程基础 | 6h |
| 4 | [[java/2深入/10_设计模式|10 设计模式]] | 单例/工厂/建造者/代理/策略/模板方法——结合 JDK 与 Spring 源码讲 | 8h |
| 5 | [[java/2深入/11_Java新特性|11 Java 新特性]] | record/sealed/模式匹配/虚拟线程 (LTS 版本速览) | 4h |
| 6 | [[java/2深入/12_算法与LeetCode|12 算法与练习]] | 用 Java 刷高频题型，巩固数据结构 | 8h |

> **检查点**: 能用 jmap + MAT 分析一次内存泄漏 dump；能解释 Spring AOP 底层是 JDK 动态代理还是 CGLIB 及两者取舍；能熟练用 Stream 重写命令式集合操作。

---

### Phase 6: 工具链与数据库 (约 2 周)

| 序号 | 文件 | 核心内容 | 建议学时 |
|:----:|------|---------|:-------:|
| 1 | [[java/3工程化/01_Maven构建|01 Maven 构建]] | pom/GAV 坐标、依赖传递、生命周期、多模块聚合 | 6h |
| 2 | [[java/3工程化/02_Gradle构建|02 Gradle 构建]] | Kotlin DSL、增量构建、与 Maven 对比选型 | 4h |
| 3 | [[java/3工程化/03_JDBC与数据库连接|03 JDBC 与数据库连接]] | Connection/PreparedStatement、连接池 (HikariCP)、事务 | 6h |
| 4 | [[java/3工程化/04_MyBatis|04 MyBatis]] | mapper 映射、动态 SQL、缓存机制、与 JDBC 对比 | 8h |

> **检查点**: 能配置一个多模块 Maven 工程并用父 pom 统一依赖版本；能解释 PreparedStatement 如何防止 SQL 注入；能写出含动态 SQL 的多条件分页查询。

---

### Phase 7: Spring 体系 (约 4 周)

| 序号 | 文件 | 核心内容 | 建议学时 |
|:----:|------|---------|:-------:|
| 1 | [[java/3工程化/05_Spring IoC与AOP|05 Spring IoC 与 AOP]] | Bean 生命周期、依赖注入、切面编程、事务传播 | 10h |
| 2 | [[java/3工程化/06_Spring Boot快速开发|06 Spring Boot 快速开发]] | starter/auto-configuration、application.yml、Actuator | 8h |
| 3 | [[java/3工程化/07_Spring MVC|07 Spring MVC]] | DispatcherServlet、RESTful 控制器、参数校验、全局异常 | 8h |
| 4 | [[java/3工程化/08_Spring Data JPA|08 Spring Data JPA]] | Repository 抽象、实体映射、派生查询、事务集成 | 8h |
| 5 | [[java/3工程化/09_Spring Security|09 Spring Security]] | 过滤器链、认证授权、JWT 集成、RBAC 权限模型 | 10h |

> **实战练习**: 用 Spring Boot + JPA + MySQL 实现一套用户-文章 REST API，含 JWT 登录、分页、全局异常处理。
>
> **检查点**: 能手写一个 BeanPostProcessor 并说明其执行时机；能解释 Boot 自动装配原理 (@EnableAutoConfiguration + spring.factories)；能独立完成登录鉴权全流程。

---

### 数据库深入（与 Phase 6-7 配合学习）

Java 全栈开发离不开数据库。以下数据库教程与 Java 各阶段紧密关联：

| 数据库 | 与 Java 的关联 | 教程链接 |
|--------|----------------|----------|
| MySQL | JDBC 驱动、MyBatis 映射、Spring Data JPA 实体 | [[数据库/mysql/01-安装与配置\|MySQL 安装]] → [[数据库/mysql/02-SQL基础语法\|SQL 基础]] → [[数据库/mysql/03-查询进阶\|查询进阶]] |
| MySQL 深入 | 索引优化（EXPLAIN）、事务隔离级别、连接池配置 | [[数据库/mysql/04-索引事务与优化\|索引与事务]] → [[数据库/mysql/05-用户权限与备份恢复\|权限与备份]] |
| MySQL 高级 | 存储过程调用、触发器审计、主从读写分离 | [[数据库/mysql/06-存储过程与触发器\|存储过程]] → [[数据库/mysql/07-主从复制与高可用\|主从复制]] |
| PostgreSQL | JPA 方言、JSONB 字段、高级查询 | [[数据库/postgresql/PostgreSQL教程\|PostgreSQL 教程]] |
| Redis | Spring Data Redis、缓存注解、分布式锁 | [[数据库/redis/Redis教程\|Redis 教程]] |
| MongoDB | Spring Data MongoDB、文档存储 | [[数据库/mongodb/MongoDB教程\|MongoDB 教程]] |
| Elasticsearch | Spring Data Elasticsearch、全文搜索 | [[数据库/elasticsearch/Elasticsearch入门教程\|Elasticsearch 入门]] |

> **建议**：在学 Phase 6（JDBC/MyBatis）时同步学习 MySQL 01-05；在学 Phase 7（Spring Data JPA）时同步学习 MySQL 04（索引与事务）；在做 Phase 9 实战项目时按需学习 Redis/MongoDB/Elasticsearch。

---

### Phase 8: 生产级工程 (约 3 周)

| 序号 | 文件 | 核心内容 | 建议学时 |
|:----:|------|---------|:-------:|
| 1 | [[java/3工程化/10_日志框架|10 日志框架]] | SLF4J 门面、Logback 配置、MDC 链路追踪 | 4h |
| 2 | [[java/3工程化/11_单元测试|11 单元测试]] | JUnit 5、Mockito、覆盖率、测试金字塔 | 6h |
| 3 | [[java/3工程化/12_Docker容器化|12 Docker 容器化]] | Dockerfile 多阶段构建、分层镜像、docker-compose 编排 | 6h |
| 4 | [[java/3工程化/13_CICD流水线|13 CICD 流水线]] | GitHub Actions/Jenkins：测试-构建-镜像-部署 | 6h |
| 5 | [[java/3工程化/14_性能调优与监控|14 性能调优与监控]] | 压测 (JMeter)、慢 SQL 定位、JVM 参数实战、Arthas | 8h |

> **检查点**: 能为项目配置分级日志并在 MDC 中注入 traceId；能把核心模块测试覆盖率提到 60% 以上；能编写一条完整 CI 流水线把 jar 打成镜像推送到仓库。

---

### Phase 9: 全栈实战与架构 (约 4 周)

| 序号 | 文件 | 核心内容 | 建议学时 |
|:----:|------|---------|:-------:|
| 1 | [[java/3工程化/15_全栈开发技巧|15 全栈开发技巧]] | 前后端联调、接口设计、完整业务项目实战 | 30h |
| 2 | [[java/3工程化/16_应急处理与线上问题排查|16 应急处理与线上问题排查]] | CPU 飙高/内存泄漏/死锁排查、止血三板斧、复盘 | 12h |
| 3 | [[java/3工程化/17_GitHub热门Java项目实战|17 GitHub 热门项目实战]] | 读源码、提 PR、参与开源 | 20h |
| 4 | [[java/3工程化/18_架构设计入门|18 架构设计入门]] | DDD、微服务拆分、分布式事务、限流降级 | 12h |

> **检查点**: 独立完成一个含前端页面的部署上线项目；能画出自己项目的架构图并回答"为什么这么拆"；向任一开源项目提交过至少一个被合并的 PR。

---

### 相关路径

- [[路径-C开发]] — C 语言主线，理解内存与底层，反哺 JVM 认知
- [[路径-CPP开发]] — C++ 主线，对比两门静态强类型语言的设计哲学
- [[路径-Rust开发]] — Rust 主线，体验无 GC 内存安全模型的另一极端
- [[java/java目录|Java 教程目录]] — 本路径全部章节的总索引
