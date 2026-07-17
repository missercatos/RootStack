# taskflow

现代 C++ 任务并行库，核心是"任务图"（Task Graph）模型。用 C++ 描述有依赖关系的任务 DAG，框架自动处理并行调度。API 设计优雅（流式 API），可视化工具可生成任务图。

## 核心组件

| 组件 | 说明 |
|------|------|
| tf::Taskflow | 任务图容器，管理任务和依赖 |
| tf::Executor | 任务图执行器 |
| tf::Task | 单个任务节点 |
| task.precede() / succeed() | 定义任务间依赖 |
| tf::Pipeline | 流水线并行 |
| tf::Subflow | 运行时动态子图 |
| tf::Taskflow.dump() | 导出 Graphviz 可视化 |

## 何时使用

- 有复杂依赖关系的工作流并行化
- 数据处理管线和构建系统
- 仿真框架
- 任务之间有明显依赖但拓扑复杂的场景

## 关键特性

任务图模型、自动依赖调度、流式 API、任务可视化

## 相关链接

- [[TBB|Intel TBB]] — 并行算法框架
- [[OpenMP|OpenMP]] — 简单循环并行
- 
- 
- (搜索: taskflow C++)
