# glog

Google 的日志库，在 Google 内部大规模使用。提供简洁的 `LOG(INFO) << "message"` 语法。支持条件日志、CHECK 断言日志、信号处理崩溃时的堆栈跟踪。但格式化能力不如 spdlog 灵活。

## 核心组件

| 组件 | 说明 |
|------|------|
| LOG(INFO) / LOG(WARNING) | 流式风格各级别日志 |
| LOG(ERROR) / LOG(FATAL) | 错误和致命日志 |
| VLOG(n) | 详细级别日志（verbose） |
| CHECK(cond) / CHECK_EQ(a,b) | 条件断言日志 |
| DLOG / DCHECK | 仅 debug 构建的日志/断言 |
| SignalHandler | 崩溃时堆栈跟踪输出 |
| FLAGS_log_dir | 日志文件目录配置 |

## 何时使用

- 想要 Google 相同日志行为的项目
- 对堆栈跟踪和崩溃诊断有较高要求
- 常用于 Linux 服务端开发
- 与 gflags/gtest 技术栈配套

## 关键特性

简洁流式语法、条件日志、崩溃堆栈、信号安全

## 相关链接

- [[spdlog|spdlog]] — 更高性能的日志库
- [[../综合/fmt|fmt]] — 格式化库
- 
- 
- (搜索: glog)
