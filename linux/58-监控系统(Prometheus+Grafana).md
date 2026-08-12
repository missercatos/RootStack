# 58 - 监控系统（Prometheus + Grafana）

> 没有监控的系统如同在黑夜中飞行。Prometheus + Grafana 已成为云原生时代的监控事实标准——Prometheus 负责指标收集和告警，Grafana 负责可视化呈现。本文从零搭建完整的监控栈，涵盖 Node Exporter、PromQL 查询、告警规则、Grafana 面板和常用 Exporter，让你对服务器的运行状态了如指掌。

---

## 58.1 监控理念：Metrics / Logs / Traces

现代可观测性三大支柱：

```
Metrics（指标） Logs（日志） Traces（链路追踪）
 CPU: 67% [ERROR] db timeout request → auth → db → cache
 Memory: 8.2G [INFO] 200 GET /api │ 30ms 80ms 5ms
 QPS: 1240 [WARN] disk 85% total: 115ms
 └─ Prometheus └─ Loki / ELK └─ Jaeger / Tempo
```

| 维度 | Prometheus 适合什么 | 不适合什么 |
|------|-------------------|-----------|
| 数据类型 | 数值型时间序列（CPU、内存、请求数） | 非结构化文本、日志全文搜索 |
| 存储 | 本地 TSDB，自动 Downsample | 长期归档（应配合 Thanos/VictoriaMetrics） |
| 查询 | PromQL，聚合和计算能力强 | 全文搜索、字符串匹配 |
| 告警 | AlertManager，分组/抑制/静默 | 复杂事件关联（需配合其他工具） |

---

## 58.2 Prometheus 架构

```
┌──────────────────┐
│ Service 1 │──┐
│ /metrics endpoint│ │ scrape (pull) ┌──────────────┐
└──────────────────┘ │ ┌───────────────▶ │ │
 │ │ │ Prometheus │──▶ AlertManager ──▶ Email/Slack
┌──────────────────┐ │ │ ┌──────────── │ (TSDB) │
│ Service 2 │──┼──┼───┘ │ │──▶ Grafana
└──────────────────┘ │ │ └──────────────┘
 │ │
┌──────────────────┐ │ │ Push（短期）
│ Short-lived Job │──┘ └────▶ Pushgateway ──▶ Prometheus
└──────────────────┘
```

核心特点：
- **Pull 模型**：Prometheus 主动从 target 拉取 metrics（无需 agent 推送）
- **多维数据模型**：`metric_name{label1="value1", label2="value2"} = value @ timestamp`
- **服务发现**：自动发现 Kubernetes、Consul、EC2 等 target

---

## 58.3 安装 Prometheus

```bash
# 下载（所有发行版通用）
VERSION=$(curl -s https://api.github.com/repos/prometheus/prometheus/releases/latest | jq -r .tag_name)
wget https://github.com/prometheus/prometheus/releases/download/${VERSION}/prometheus-${VERSION#v}.linux-amd64.tar.gz
tar xzf prometheus-*.tar.gz
sudo mv prometheus-${VERSION#v}.linux-amd64 /opt/prometheus

# 创建用户
sudo useradd --system --no-create-home --shell /usr/sbin/nologin prometheus

# 创建目录
sudo mkdir -p /var/lib/prometheus
sudo chown -R prometheus:prometheus /opt/prometheus /var/lib/prometheus
```

### 创建 systemd 服务

```bash
sudo tee /etc/systemd/system/prometheus.service << 'EOF'
[Unit]
Description=Prometheus
After=network.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/opt/prometheus/prometheus \
 --config.file=/opt/prometheus/prometheus.yml \
 --storage.tsdb.path=/var/lib/prometheus \
 --storage.tsdb.retention.time=15d \
 --web.listen-address=0.0.0.0:9090 \
 --web.enable-lifecycle
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
```

### 基本配置

```bash
sudo vim /opt/prometheus/prometheus.yml
```

```yaml
global:
 scrape_interval: 15s
 evaluation_interval: 15s
 external_labels:
 datacenter: "dc-shanghai"

alerting:
 alertmanagers:
 - static_configs:
 - targets: ['localhost:9093']

rule_files:
 - "rules/*.yml"

scrape_configs:
 # Prometheus 自身监控
 - job_name: 'prometheus'
 static_configs:
 - targets: ['localhost:9090']

 # Node Exporter（系统指标）
 - job_name: 'node'
 static_configs:
 - targets:
 - '192.168.1.10:9100'
 - '192.168.1.11:9100'
 - '192.168.1.12:9100'
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now prometheus

# 访问 http://<server-ip>:9090
# 测试查询：http://<server-ip>:9090/graph
```

---

## 58.4 安装 Node Exporter

在 **每台被监控的服务器** 上安装：

```bash
VERSION=$(curl -s https://api.github.com/repos/prometheus/node_exporter/releases/latest | jq -r .tag_name)
wget https://github.com/prometheus/node_exporter/releases/download/${VERSION}/node_exporter-${VERSION#v}.linux-amd64.tar.gz
tar xzf node_exporter-*.tar.gz
sudo mv node_exporter-${VERSION#v}.linux-amd64/node_exporter /usr/local/bin/
rm -rf node_exporter-*

sudo tee /etc/systemd/system/node_exporter.service << 'EOF'
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=nobody
ExecStart=/usr/local/bin/node_exporter \
 --collector.systemd \
 --collector.processes \
 --collector.tcpstat
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now node_exporter

# 验证
curl http://localhost:9100/metrics | head -30
```

### Node Exporter 核心指标

| 指标 | PromQL 示例 | 说明 |
|------|------------|------|
| `node_cpu_seconds_total` | `rate(...[5m])` | CPU 各模式使用率 |
| `node_memory_MemAvailable_bytes` | `/ node_memory_MemTotal_bytes` | 可用内存比例 |
| `node_filesystem_avail_bytes` | — | 磁盘可用空间 |
| `node_disk_read_bytes_total` | `rate(...[5m])` | 磁盘读取速率 |
| `node_network_receive_bytes_total` | `rate(...[5m])` | 网络接收速率 |
| `node_load1/5/15` | — | 系统负载 |
| `node_uptime_seconds` | — | 运行时长 |

---

## 58.5 PromQL 核心查询

### 基本操作

```promql
# 瞬时向量 — 查询某个时刻所有 CPU idle 秒数
node_cpu_seconds_total{mode="idle"}

# 范围向量 — 过去 5 分钟的数据
node_cpu_seconds_total{mode="idle"}[5m]

# 函数配合
# CPU 每核使用率
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# 内存使用率
(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100

# 磁盘可用百分比（排除 tmpfs）
(node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100

# 网络流量（每秒字节数）
rate(node_network_receive_bytes_total{device="eth0"}[5m])

# 磁盘 IO 使用率
rate(node_disk_io_time_seconds_total{device="sda"}[5m]) * 100

# 每分钟请求计数
rate(http_requests_total[1m])

# 99 分位延迟（如指标有 histogram）
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))
```

### 聚合操作

```promql
# sum：求和
sum(rate(node_network_receive_bytes_total[5m]))

# avg：平均值
avg(rate(node_cpu_seconds_total{mode="user"}[5m]))

# max / min：最大/最小值
max(node_memory_Active_bytes)

# count：计数
count(up == 1) # 在线 target 数量

# topk / bottomk
topk(5, rate(node_cpu_seconds_total{mode="user"}[5m]))

# 按标签分组
sum by(instance) (rate(node_network_receive_bytes_total[5m]))
```

### 常用组合

```promql
# 计算百分比
100 * (metric_a / metric_b)

# 计算差值
metric_current - metric_current offset 1h

# 预测未来值
predict_linear(node_filesystem_free_bytes[1h], 24 * 3600)

# 计算变化率
changes(up[1h])
```

---

## 58.6 告警规则与 AlertManager

### 告警规则

```bash
sudo mkdir -p /opt/prometheus/rules
sudo vim /opt/prometheus/rules/node_alerts.yml
```

```yaml
groups:
 - name: node_alerts
 rules:
 # 实例下线
 - alert: InstanceDown
 expr: up == 0
 for: 2m
 labels:
 severity: critical
 annotations:
 summary: "{{ $labels.instance }} is down"
 description: "{{ $labels.instance }} 已经超过 2 分钟无响应"

 # 高 CPU 使用率
 - alert: HighCPUUsage
 expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 90
 for: 5m
 labels:
 severity: warning
 annotations:
 summary: "{{ $labels.instance }} CPU usage > 90%"

 # 内存不足
 - alert: LowMemory
 expr: (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100 < 10
 for: 5m
 labels:
 severity: warning
 annotations:
 summary: "{{ $labels.instance }} available memory < 10%"

 # 磁盘空间不足
 - alert: DiskAlmostFull
 expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 10
 for: 5m
 labels:
 severity: critical
 annotations:
 summary: "{{ $labels.instance }} 磁盘空间 < 10%"

 # 磁盘预测 4 小时内满
 - alert: DiskWillFillIn4Hours
 expr: predict_linear(node_filesystem_avail_bytes{mountpoint="/"}[1h], 4 * 3600) < 0
 labels:
 severity: critical
 annotations:
 summary: "{{ $labels.instance }} 磁盘预计 4 小时内写满"

 # 高负载
 - alert: HighLoad
 expr: node_load15 / count without(cpu, mode) (node_cpu_seconds_total{mode="system"}) > 2
 for: 10m
 labels:
 severity: warning
 annotations:
 summary: "{{ $labels.instance }} 15min load avg > CPU count * 2"

 # 重启检测
 - alert: HostOutOfMemory
 expr: node_memory_MemAvailable_bytes < 5 * 1024 * 1024
 for: 30s
 labels:
 severity: critical
 annotations:
 summary: "{{ $labels.instance }} 内存不足 5MB"
```

### AlertManager 安装与配置

```bash
# 下载
VERSION=$(curl -s https://api.github.com/repos/prometheus/alertmanager/releases/latest | jq -r .tag_name)
wget https://github.com/prometheus/alertmanager/releases/download/${VERSION}/alertmanager-${VERSION#v}.linux-amd64.tar.gz
tar xzf alertmanager-*.tar.gz
sudo mv alertmanager-${VERSION#v}.linux-amd64 /opt/alertmanager
sudo useradd --system --no-create-home --shell /usr/sbin/nologin alertmanager

sudo tee /etc/systemd/system/alertmanager.service << 'EOF'
[Unit]
Description=AlertManager
After=network.target

[Service]
User=alertmanager
ExecStart=/opt/alertmanager/alertmanager --config.file=/opt/alertmanager/alertmanager.yml
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

sudo chown -R alertmanager:alertmanager /opt/alertmanager
sudo systemctl daemon-reload
sudo systemctl enable --now alertmanager
```

```bash
sudo vim /opt/alertmanager/alertmanager.yml
```

```yaml
global:
 smtp_smarthost: 'smtp.example.com:587'
 smtp_from: 'alertmanager@example.com'
 smtp_auth_username: 'alertmanager@example.com'
 smtp_auth_password: 'your-password'

# 路由：按严重级别分组
route:
 group_by: ['alertname', 'severity']
 group_wait: 10s
 group_interval: 10s
 repeat_interval: 3h
 receiver: 'default'
 routes:
 - match:
 severity: critical
 receiver: 'critical-ops'
 continue: true
 - match:
 severity: warning
 receiver: 'ops-email'

receivers:
 - name: 'default'
 webhook_configs:
 - url: 'https://hooks.slack.com/services/T00/B00/xxx'

 - name: 'critical-ops'
 webhook_configs:
 - url: 'https://hooks.slack.com/services/T00/B00/xxx_alerts'
 - url: 'https://api.example.com/pagerduty'
 email_configs:
 - to: 'ops@example.com'

 - name: 'ops-email'
 email_configs:
 - to: 'ops@example.com'

inhibit_rules:
 - source_match:
 severity: 'critical'
 target_match:
 severity: 'warning'
 equal: ['instance']
```

### Prometheus 集成 AlertManager

在 `prometheus.yml` 中确保 `alerting` 指向 AlertManager：

```yaml
alerting:
 alertmanagers:
 - static_configs:
 - targets: ['localhost:9093']
```

---

## 58.7 Grafana 安装与配置

```bash
# Debian / Ubuntu
sudo apt install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt update && sudo apt install grafana -y

# RHEL / Fedora
sudo tee /etc/yum.repos.d/grafana.repo << 'EOF'
[grafana]
name=grafana
baseurl=https://packages.grafana.com/oss/rpm
repo_gpgcheck=1
enabled=1
gpgcheck=1
gpgkey=https://packages.grafana.com/gpg.key
sslverify=1
sslcacert=/etc/pki/tls/certs/ca-bundle.crt
EOF
sudo dnf install grafana -y

# Arch
sudo pacman -S grafana

# 所有发行版
sudo systemctl daemon-reload
sudo systemctl enable --now grafana-server

# 访问 http://<server-ip>:3000（默认 admin/admin）
```

### 添加 Prometheus 数据源

1. 访问 http://<server-ip>:3000
2. 左侧菜单 → Connections → Data Sources → Add data source → Prometheus
3. URL 填写 `http://localhost:9090`
4. 点击 Save & Test

### 导入预设 Dashboard

Grafana 社区有大量预设 Dashboard，Node Exporter Full 是最常用的：

```
Dashboard ID: 1860 — Node Exporter Full（推荐）
Dashboard ID: 11074 — Node Exporter for Prometheus
Dashboard ID: 111 — Prometheus Stats
```

导入方式：
1. 左侧菜单 → Dashboards → New → Import
2. 输入 Dashboard ID → Load
3. 选择 Prometheus 数据源 → Import

---

## 58.8 自定义 Grafana Dashboard

### 创建 CPU 面板

进入 Dashboard → Add visualization → 选择 Prometheus 数据源：

```promql
# CPU 使用率
100 - (avg(rate(node_cpu_seconds_total{mode="idle",instance=~"$instance"}[$__rate_interval])) * 100)
```

设置：
- Unit: Percent (0-100)
- Title: CPU Usage
- Legend: `{{instance}}`

### 创建内存仪表盘

```promql
# 可用内存
node_memory_MemAvailable_bytes{instance=~"$instance"}

# 总内存
node_memory_MemTotal_bytes{instance=~"$instance"}

# 使用率（Gauge 面板）
(1 - (node_memory_MemAvailable_bytes{instance=~"$instance"} / node_memory_MemTotal_bytes{instance=~"$instance"})) * 100
```

### 创建网络流量面板

```promql
# 接收
rate(node_network_receive_bytes_total{instance=~"$instance",device!="lo"}[$__rate_interval])

# 发送
- rate(node_network_transmit_bytes_total{instance=~"$instance",device!="lo"}[$__rate_interval])
```

设置：
- Unit: bytes/sec(IEC)
- Graph mode: Lines

### 创建系统概览（Stat 面板）

```
Stat 面板 — Up status: up{instance=~"$instance"}
Stat 面板 — Uptime: time() - node_boot_time_seconds{instance=~"$instance"}
Stat 面板 — CPU Cores: count(node_cpu_seconds_total{mode="system",instance=~"$instance"})
Stat 面板 — Total Memory: node_memory_MemTotal_bytes{instance=~"$instance"}
Stat 面板 — Disk Used %: (1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100
```

### Dashboard 变量（Template Variables）

在 Dashboard Settings → Variables → Add variable：

```
Name: instance
Type: Query
Query: label_values(node_cpu_seconds_total, instance)
Multi-value: 
Include All option: 
```

然后在面板查询中使用 `instance=~"$instance"` 即可动态过滤。

---

## 58.9 更多 Exporter

### Blackbox Exporter（端点探测）

```bash
# 安装
VERSION=$(curl -s https://api.github.com/repos/prometheus/blackbox_exporter/releases/latest | jq -r .tag_name)
wget https://github.com/prometheus/blackbox_exporter/releases/download/${VERSION}/blackbox_exporter-${VERSION#v}.linux-amd64.tar.gz
tar xzf blackbox_exporter-*.tar.gz
sudo mv blackbox_exporter-${VERSION#v}.linux-amd64/blackbox_exporter /usr/local/bin/

sudo tee /etc/systemd/system/blackbox_exporter.service << 'EOF'
[Unit]
Description=Blackbox Exporter
After=network.target
[Service]
User=nobody
ExecStart=/usr/local/bin/blackbox_exporter --config.file=/opt/blackbox_exporter.yml
[Install]
WantedBy=multi-user.target
EOF
```

```bash
sudo mkdir /opt/blackbox && sudo vim /opt/blackbox/blackbox_exporter.yml
```

```yaml
modules:
 http_2xx:
 prober: http
 timeout: 5s
 http:
 valid_status_codes: [200, 301, 302]
 method: GET
 fail_if_ssl: false
 fail_if_not_ssl: false

 tcp_connect:
 prober: tcp
 timeout: 5s

 icmp:
 prober: icmp
 timeout: 5s
```

在 Prometheus 中添加 scrape job：

```yaml
scrape_configs:
 - job_name: 'blackbox-http'
 metrics_path: /probe
 params:
 module: [http_2xx]
 static_configs:
 - targets:
 - https://example.com
 - https://api.example.com/health
 relabel_configs:
 - source_labels: [__address__]
 target_label: __param_target
 - source_labels: [__param_target]
 target_label: instance
 - target_label: __address__
 replacement: 127.0.0.1:9115
```

### Pushgateway（短期任务指标）

```bash
# 安装
wget https://github.com/prometheus/pushgateway/releases/download/v1.7/pushgateway-1.7.linux-amd64.tar.gz
sudo mv pushgateway /usr/local/bin/

# 推送指标（用于 cron 任务、批处理等）
echo "batch_job_duration_seconds 45" | curl --data-binary @- \
 http://localhost:9091/metrics/job/batch_example/instance/batch-server-01
```

### 其他常用 Exporter

| Exporter | 监控对象 |
|----------|---------|
| `mysqld_exporter` | MySQL/MariaDB |
| `postgres_exporter` | PostgreSQL |
| `redis_exporter` | Redis |
| `nginx_exporter` | Nginx stub_status |
| `cadvisor` | 容器资源（Docker/k8s） |
| `process_exporter` | 进程状态 |
| `ssl_exporter` | SSL 证书过期 |
| `snmp_exporter` | 网络设备 SNMP |

---

## 58.10 备选方案：Netdata

如果你需要"开箱即用"的监控，Netdata 比 Prometheus+Grafana 简单得多：

```bash
# 一条命令安装
curl -s https://get.netdata.cloud/kickstart.sh | bash

# 访问 http://<server-ip>:19999
# 自带 200+ 采集器，自动发现，无需配置
```

Netdata vs Prometheus：
| 方面 | Netdata | Prometheus |
|------|---------|-----------|
| 安装复杂度 | 极简 | 中等 |
| 可视化 | 内置 | 需 Grafana |
| 长期存储 | 默认 3 天（需扩展） | 默认 15 天（可调） |
| 多主机 | Netdata Cloud（免费） | Federation + Thanos |
| 告警 | 内置 | AlertManager |
| 定制能力 | 有限 | 无限（自定义 metrics） |

---

## 58.11 监控系统维护

```bash
# 检查 Prometheus 健康状态
curl http://localhost:9090/-/healthy
curl http://localhost:9090/-/ready

# 查看 target 状态
curl -s http://localhost:9090/api/v1/targets | jq .

# 查看告警规则
curl -s http://localhost:9090/api/v1/rules | jq .

# 查看当前活跃告警
curl -s http://localhost:9093/api/v2/alerts | jq .

# 检查 TSDB 状态
curl -s http://localhost:9090/api/v1/status/tsdb | jq .

# 日志
sudo journalctl -u prometheus -f
sudo journalctl -u node_exporter -f
sudo journalctl -u grafana-server -f

# Prometheus 版本信息
prometheus --version

# 重载配置（需在启动时加 --web.enable-lifecycle）
curl -X POST http://localhost:9090/-/reload

# 备份 Prometheus 数据
sudo tar -czf /backup/prometheus_data_$(date +%Y%m%d).tar.gz /var/lib/prometheus
```

---

## 58.12 本章总结

| 组件 | 端口 | 功能 |
|------|------|------|
| Prometheus | 9090 | 指标收集、存储、PromQL 查询 |
| Node Exporter | 9100 | 系统指标暴露 |
| AlertManager | 9093 | 告警分组、路由、静默 |
| Grafana | 3000 | 可视化面板和仪表板 |
| Blackbox Exporter | 9115 | HTTP/TCP/ICMP 端点探测 |
| Pushgateway | 9091 | 短期任务指标中转 |

> 深入系统性能分析见 [[37-系统调优与性能分析]]，集中式日志方案见 [[14-日志系统]]。
