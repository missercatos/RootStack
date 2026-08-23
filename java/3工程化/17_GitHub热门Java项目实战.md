# 17 GitHub热门Java项目实战

> 前置知识：[[java/2深入/02_注解与反射|注解与反射]]、[[java/3工程化/01_Maven构建|Maven构建]]、Git 基础。本章是工程实战篇：读源码不是收藏夹里吃灰，而是带着问题进去、带着理解出来；提 PR 不是简历装饰，而是工程协作能力的公开证明。

---

## 一、为什么读源码、提 PR

### 1.1 读源码的三个真实收益

1. **面试护城河**：背八股的人很多，能说清"MyBatis 一条 SQL 从 SqlSession 到 Executor 再到 StatementHandler 的流转"的人极少；
2. **写代码的品味**：读过 Netty 的人写的异步代码和没读过的人完全不是一个气质——接口设计、异常处理、注释密度都有参照物了；
3. **排障底气**：出诡异问题时，看过源码的人敢下断点进第三方 jar 里找答案，没看过的只能换库重试。

但注意顺序：**先会用、再精读、后魔改**。没用过 MyBatis 就去读源码，等于不游泳先学救生。

### 1.2 提 PR 的隐性价值

一次被合并的 PR 意味着：你会用 Git 分支协作、能读懂陌生代码库、能按社区规范沟通——这三件事正是高级工程师的日常。哪怕最终没被合并，review 往返中学到的东西也远超自己闷头写十个小项目。

---

## 二、如何判断优质的老项目

### 2.1 优质项目的五个信号

| 信号 | 看哪里 | 说明 |
|------|--------|------|
| 创建时间早 | Insights → 首次 commit | 2010 年前的项目活到现在，说明有真实生命力 |
| commit 历史长且连续 | Insights → Contributors | 十年间持续有人提交，曲线平滑无断崖 |
| 真人贡献者多 | Contributors 列表 | 有头像、有个人主页的真实开发者 |
| issue/PR 活跃 | Issues 页 | 维护者认真回复、给标签、关联 PR |
| 发布节奏稳定 | Releases 页 | 定期发版带 changelog，说明有人在负责 |

### 2.2 警惕 AI 刷 star 项目

2024 年起出现了大量"营销型仓库"：star 几千却查无此人。对比特征表：

| 维度 | 优质老项目 | AI 刷 star 项目 |
|------|-----------|-----------------|
| star 来源 | 多数来自 watch/fork 用户，随时间缓慢累积 | 短期暴涨，star 用户主页多为空壳 |
| commit 作者 | 大量真人邮箱与签名 | 少量账号批量提交，commit 信息模板化雷同 |
| issue 区 | 真实使用问题+维护者回复 | 冷清或全是机器人互吹 |
| README | 克制、讲清用法 | 夸张宣传语、"吊打 XX"、大量徽章堆砌 |
| 文档与代码一致性 | 示例可跑 | 示例残缺、依赖版本对不上 |
| fork/PR 比 | 有正常比例的外部 PR | 几乎没有外部贡献 |

一句话判断法：**star 是结果不是质量**。去看 contributor 的 GitHub 主页是否像真人、issue 是否有真对话，比看任何指标都准。

---

## 三、精选项目清单与学习路线

以下八个项目按学习难度递进排列。星数为约数，随时间浮动。

### 3.1 spring-projects/spring-petclinic（约 8k 星）

Spring 官方示范应用，1999 年以 PetClinic 形态存在，是"教科书级分层架构"的活标本。体量小（几十个类）、技术栈标准（Spring Boot + JPA + Thymeleaf），适合通读。

```text
学习路线:
第 1 步:克隆跑起来,把 owner/pet/vet 三条业务线点一遍
第 2 步:画 Controller -> Service -> Repository 的调用图
第 3 步:观察 JPA 实体的关系映射(@OneToMany 等)
第 4 步:看它的测试怎么写(集成测试切数据库的姿势)
复刻建议:仿照它写一个"诊所版"自己的 CRUD 应用,
比如图书管理系统,严格模仿它的分层与命名
```

### 3.2 iluwatar/java-design-patterns（约 90k 星）

GOF 二十三式及大量现代模式的 Java 实现，每个模式配 UML 与真实场景说明。不建议从头读到尾，当字典用：

```text
学习路线:
第 1 步:只看你项目里正在用的模式(如策略、工厂、建造者)
第 2 步:每读完一个,在自己的代码里找到或重构出一个实例
第 3 步:进阶读组合模式章节(abstract-document、monostate)
复刻建议:不用整库复刻,选 10 个模式各写一个
"业务化"示例(而非书上的 Shape/Pizza 教学例子)
```

### 3.3 TheAlgorithms/Java（约 60k 星）

算法大全：排序、搜索、图论、动态规划的纯 Java 实现，配合刷题食用最佳。

```text
学习路线:
第 1 步:刷题卡壳时来看对应算法的标准实现(先自己写再看)
第 2 步:对照 LeetCode 分类,按专题阅读
第 3 步:挑几个实现写单元测试,练习 JUnit 参数化测试
复刻建议:建一个 algorithm-notes 仓库,
每个算法用自己的话写注释+复杂度分析+刷题链接
```

### 3.4 redisson/redisson（约 23k 星）

功能最全的 Redis Java 客户端，分布式锁、限流器、延迟队列应有尽有。重点读它的**锁实现**：watchdog 续期、Lua 脚本保证原子性、RedLock 思想。

```text
学习路线:
第 1 步:先用 lock/unlock,思考"宕机了锁会死吗"
第 2 步:读 RLock 的 lock 加锁 Lua 脚本(HASH 记录持有线程)
第 3 步:追 watchdog 默认 30 秒租期的续期逻辑
第 4 步:对比 SETNX 手写版,理解为什么手写版本有坑
复刻建议:手写一个简化版分布式锁(加锁 Lua + 过期 + 续期线程),
再与 Redisson 对拍差异,收获极大
```

### 3.5 mybatis/mybatis-3（约 20k 星）

源码量适中（核心几万行），是"第一个通读的开源框架"的最佳选择。设计模式密度极高：工厂、建造者、责任链、动态代理全在里面。

```text
学习路线:
第 1 步:从 SqlSessionFactoryBuilder 的 build() 入口往下追
第 2 步:搞清 Configuration/MappedStatement 的解析装载
第 3 步:核心一条线:getMapper 动态代理 -> MapperMethod
        -> Executor -> StatementHandler -> JDBC
第 4 步:看一级/二级缓存的 PerpetualCache 与装饰器
复刻建议:写一个 100 行的 mini-mybatis:
解析简单 XML 映射 + 动态代理执行 SQL + 结果集映射成对象
```

### 3.6 netty/netty（约 34k 星）

Java NIO 巅峰之作，事件驱动模型的范本。门槛较高，建议有并发基础后再啃：

```text
学习路线:
第 1 步:先懂 NIO 基础(Channel/Buffer/Selector)
第 2 步:抓主线:EventLoop 线程模型与 pipeline 传播
第 3 步:读 ByteBuf 的池化与引用计数
第 4 步:看一个现成协议实现(如 HTTP 编解码器)收尾
复刻建议:用 Netty 写一个简单的 Redis 协议客户端
(RESP 协议文本简单,非常适合练手)
```

### 3.7 alibaba/druid（约 28k 星）

数据库连接池加 SQL 监控，国内生产环境存量巨大。学习重点是连接池的通用原理：

```text
学习路线:
第 1 步:配置并打开 Web 监控页,观察活跃/等待连接数
第 2 步:读 DruidDataSource 的 getConnection 归还逻辑
第 3 步:重点看它的防泄漏:removeAbandoned 追踪未归还连接
第 4 步:对比 HikariCP 设计文档,理解两种性能哲学
复刻建议:手写 50 行迷你连接池(预建 N 个连接 + 借还队列),
再故意制造"借了不还",体会泄漏检测的价值
```

### 3.8 google/guava（约 50k 星）

Google 的 Java 工具军火库。不必通读，按需取用并读对应实现：

```text
学习路线:
第 1 步:常用工具上手(ImmutableList/Maps/Joiner/StopWatch)
第 2 步:Cache 接口与 Caffeine 的渊源
第 3 步:ListenableFuture 理解 Guava 时代的异步观
第 4 步:读一个集合实现(如 ArrayListMultimap)看防御性编程
复刻建议:给自己造一个 utils 库,收录工作中重复造过的轮子
```

### 3.9 八个项目速查表

| 项目 | 星数 | 核心价值 | 难度 | 建议投入 |
|------|------|----------|------|----------|
| spring-petclinic | 8k | 分层架构范本 | 低 | 1 周 |
| java-design-patterns | 90k | 设计模式字典 | 低 | 长期查阅 |
| TheAlgorithms/Java | 60k | 算法参考实现 | 低 | 配合刷题 |
| guava | 50k | 工具库与编码品味 | 中 | 按需 |
| druid | 28k | 连接池原理+监控 | 中 | 2 周 |
| mybatis-3 | 20k | 第一个通读的框架 | 中 | 1-2 月 |
| redisson | 23k | 分布式锁源码 | 中高 | 2 周 |
| netty | 34k | NIO 与事件驱动 | 高 | 2-3 月 |

使用原则：同一时期主攻一个，读完一个的"学习路线四步"再开下一个；难度高的项目（netty）放在并发基础扎实之后。

---

## 四、读源码的通用方法论

拿到一个陌生框架，不要从第一个文件顺着读。推荐"三条线切入法"：

### 4.1 主线一：从一次调用追进去

以 MyBatis 为例，你每天写的 `userMapper.selectById(1)` 就是入口。在接口处打断点，一路 step into，把经过的类记下来：

```mermaid
flowchart TD
    A["UserMapper.selectById()<br/>你看到的接口"] --> B["MapperProxy.invoke()<br/>JDK 动态代理接管调用"]
    B --> C["MapperMethod.execute()"]
    C --> D["Executor.query()<br/>真正干活的大管家"]
    D --> E["StatementHandler<br/>与 JDBC 对接"]
    E --> F["ResultSetHandler<br/>结果映射成对象"]

    style A fill:#e8f4fd
```

六个类就抓住了框架的主干。剩下的分支（插件、缓存、事务）等主干清晰后再补。

### 4.2 主线二：从启动流程看装配

Spring 系项目的另一条线是启动：`new SpringApplication().run()` 做了什么、自动配置怎么生效、Bean 怎么变成你注入的样子。这条线解释"魔法从哪来"，对排查配置问题极有用。

### 4.3 主线三：带着疑问定向突破

不追求通读时，直接带着具体问题进源码：

| 疑问 | 检索关键词 | 落点 |
|------|-----------|------|
| @Transactional 为什么失效 | TransactionAspectSupport | AOP 切面与自调用问题 |
| Redisson 锁会不会死锁 | watchdog, renewExpiration | 续期线程逻辑 |
| 连接池连接什么时候回收 | evictor, idleTimeout | 后台驱逐任务 |

### 4.4 配套习惯

```text
1. 边读边画时序图/类图,画不出来等于没读懂
2. 在 IDEA 里用 "Diagrams - Show Dependencies" 看模块依赖
3. 给关键路径写注释笔记,存进自己的仓库
4. 读不懂就写个最小 demo 复现行为,再回来看代码
5. 一周只攻一个框架,贪多必失
```

---

## 五、提 PR 全流程

### 4.1 流程总览

```mermaid
flowchart LR
    A["fork 仓库"] --> B["clone 自己的 fork"]
    B --> C["创建分支<br/>fix/xxx 或 feat/xxx"]
    C --> D["修改 + 补测试"]
    D --> E["conventional commits 提交"]
    E --> F["push 到 fork"]
    F --> G["发起 PR<br/>套描述模板"]
    G --> H{"CI 通过?"}
    H -->|"否"| I["修问题再 push"]
    I --> H
    H -->|"是"| J["maintainer review"]
    J -->|"要求修改"| K["同一分支继续提交"]
    K --> H
    J -->|"approve"| L["合并完成"]

    style L fill:#e8f7e8
```

### 5.2 Conventional Commits 规范

成熟开源项目几乎都要求规范化提交信息，格式 `类型: 简述`：

```text
fix: resolve connection leak in DruidDataSource#recycle
feat: add retry support for redisson lock watchdog
docs: fix typo in cache configuration example
test: add unit tests for bounded executor
refactor: extract duplicate code into helper method
chore: bump junit from 5.9 to 5.10
```

类型速查：fix（修 bug）、feat（新功能）、docs、test、refactor、chore（杂务）。一行不超过 72 字符，正文另起行解释 why 而非 what。

### 5.3 PR 描述模板

好的 PR 描述让 reviewer 五分钟内建立信任：

```markdown
## 问题
修复 #1234:高并发下 DruidDataSource 连接归还时可能抛 NPE

## 根因
recycle() 与 destroy() 并发执行时,conn holder 可能已被置空

## 修改内容
- 在 recycle() 中增加空值短路判断
- 新增并发回归测试 RecycleConcurrencyTest

## 自测
- [x] 新增测试本地通过
- [x] mvn verify 全量通过
- [x] 在压测环境复现场景验证不再抛错
```

### 5.4 review 应对与开源礼仪

| 场景 | 正确做法 | 错误做法 |
|------|----------|----------|
| reviewer 要求改 | "Good catch,已按建议调整"并提交 | 辩解或沉默硬扛 |
| 不认同意见 | 给出理由与依据,礼貌讨论 | 直接无视评论合并意图 |
| 长期无人回复 | 一到两周后礼貌 ping 一下 | 天天催或开重复 PR |
| PR 被关闭 | 询问原因,吸收反馈 | 情绪化发言 |
| 发现安全漏洞 | 私信维护者,绝不公开提 issue | 当众贴漏洞细节 |

礼仪要点：小步提交（一个 PR 只做一件事）、遵守项目的 CONTRIBUTING.md、commit message 与代码风格向项目看齐、中文国际项目一律英文交流。

### 5.5 good first issue 怎么找

在仓库 Issues 页用标签筛选 `good first issue` 或 `help wanted`，这是社区明确标注的入门任务（通常是文档错字、补充测试、小 bug）。进阶路径：good first issue → 文档改进 → 小 bug 修复 → 功能特性。持续在同一项目贡献，维护者会记住你，review 会越来越快。

---

## 六、实战前的准备

准备一台装好 JDK 17 与 Git 的机器，注册 GitHub 账号并配置 SSH key。下面的命令流可以直接跟着敲。

---

## 七、实战：spring-petclinic 从克隆到提 PR

目标：走完一次真实的贡献闭环。我们虚构一个小 bug——宠物列表页的出生日期显示格式不一致——从发现到 PR 全程。

### 7.1 克隆与启动

```bash
# 1. fork 后克隆自己的仓库(替换 YOUR_NAME)
git clone git@github.com:YOUR_NAME/spring-petclinic.git
cd spring-petclinic

# 2. 关联上游,以后同步官方更新用
git remote add upstream https://github.com/spring-projects/spring-petclinic.git
git fetch upstream

# 3. 启动确认环境没问题
./mvnw spring-boot:run
# 浏览器打开 http://localhost:8080,能看到诊所首页
```

### 7.2 定位并修复问题

```bash
# 4. 从最新上游 main 切出工作分支(分支名体现意图)
git checkout -b fix/owner-list-date-format upstream/main

# 5. 全局搜索日期展示相关代码
grep -rn "pet.birthDate" src/main/
# 找到 ownerDetails.html 中两处展示,一处用了 yyyy-MM-dd,一处没格式化
```

修改模板统一为 `th:text="${#temporals.format(pet.birthDate, 'yyyy-MM-dd')}"`，顺手检查同页面其他日期字段保持一致。

```bash
# 6. 本地验证:启动应用,打开 owner 详情页目视检查 + 跑已有测试
./mvnw test

# 7. 规范化提交
git add src/main/resources/templates/owners/ownerDetails.html
git commit -m "fix: unify birth date format on owner details page"

# 8. 推送到自己的 fork
git push -u origin fix/owner-list-date-format
```

### 7.3 发起 PR 与后续跟进

```bash
# 9. 用 gh CLI 创建 PR(也可在网页上点 Compare & pull request)
gh pr create --repo spring-projects/spring-petclinic \
  --base main \
  --title "fix: unify birth date format on owner details page" \
  --body "$(cat <<'EOF'
## Issue
The birth dates of pets are displayed inconsistently on the owner
details page: some cells use yyyy-MM-dd while others fall back to
the default locale format.

## Change
Apply #temporals.format(pet.birthDate, 'yyyy-MM-dd') uniformly to
all date columns on the page.

## Verification
Ran ./mvnw test locally and manually checked the owner details page.
EOF
)"
```

之后 CI 自动跑起来。若 maintainer 留下修改意见：

```bash
# 10. 在同一分支上继续修改并推送,PR 自动更新
git add -u
git commit -m "refactor: apply review suggestion to use shared formatter"
git push
```

被合并后同步本地：

```bash
# 11. 合并后清理
git checkout main
git pull upstream main
git branch -d fix/owner-list-date-format
git push origin --delete fix/owner-list-date-format
```

### 7.4 如果第一次 PR 没被合并

完全正常。常见被拒原因与预防：

| 被拒原因 | 预防方式 |
|----------|----------|
| 方向与项目规划不符 | 大改动先开 issue 讨论,得到维护者认可再动手 |
| 缺少测试 | 修 bug 必附回归测试,加功能必带单元测试 |
| 代码风格不符 | 提交前跑项目的 checkstyle/spotless 等 CI 同款工具 |
| 改动过大难以 review | 拆成多个小 PR 分批提交 |
| 长期无人处理 | 一到两周礼貌 ping,或换个活跃度高的项目练手 |

把它当成免费的 code review 课，改完再战。事实上，多数人的前三个 PR 都是小改动——这正是社区设计的成长路径。

---

## 小结

- 判断优质项目看五件事：创建早、commit 连续、真人贡献者、issue 有对话、发版有节奏；star 数本身不代表质量，警惕短期暴涨的 AI 刷量仓库；
- 读源码路径：先会用 → 带着调用链问题读 → mini 复刻验证理解；mybatis-3 是通读首选，netty 放到最后；
- 提 PR 铁律：一个 PR 一件事、conventional commits、描述讲清问题/根因/修改/自测、礼貌应对 review；
- good first issue 是社区给你留的门，沿着文档 → 测试 → bug → feature 的阶梯往上爬；
- 本章的 petclinic 命令流可直接复用到任何仓库：fork → branch → fix → conventional commit → PR → 应对 review → 清理。
