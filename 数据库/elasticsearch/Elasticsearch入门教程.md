# Elasticsearch 入门教程

Elasticsearch 是一个**分布式全文搜索引擎**，基于 Apache Lucene 构建。它是 ELK Stack（Elasticsearch + Logstash + Kibana）的核心组件，广泛用于日志分析、全文搜索、实时数据分析。

---

## 一、Elasticsearch 是什么

### 1.1 核心概念

| 概念 | 类比 MySQL | 说明 |
|------|------------|------|
| Index | Database | 索引，存储一类数据的集合 |
| Document | Row | 文档，一条数据记录（JSON 格式） |
| Field | Column | 字段，文档中的一个属性 |
| Mapping | Schema | 映射，定义字段类型和分析器 |
| Shard | Partition | 分片，索引的数据分片（水平拆分） |
| Replica | Replica | 副本，分片的复制（高可用 + 读扩展） |

### 1.2 为什么需要 Elasticsearch

| 场景 | MySQL | Elasticsearch |
|------|-------|---------------|
| 全文搜索 | `LIKE '%keyword%'` 慢，无法分词 | 倒排索引，毫秒级响应 |
| 模糊匹配 | `LIKE '%partial%'` 无法索引 | 支持分词、同义词、纠错 |
| 聚合分析 | `GROUP BY` + 子查询，性能差 | 内置聚合管道，实时分析 |
| 实时搜索 | 需要额外配置 | 近实时（1秒延迟） |

---

## 二、安装与配置

### 2.1 Docker 安装

```bash
# 单节点
docker run -d \
  --name elasticsearch \
  -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
  docker.elastic.co/elasticsearch/elasticsearch:8.12.0

# 验证
curl http://localhost:9200
```

### 2.2 核心配置

```yaml
# elasticsearch.yml
cluster.name: my-cluster
node.name: node-1
path.data: /var/lib/elasticsearch
path.logs: /var/log/elasticsearch
network.host: 0.0.0.0
discovery.seed_hosts: ["node-1", "node-2", "node-3"]
cluster.initial_master_nodes: ["node-1", "node-2", "node-3"]
```

---

## 三、基本操作

### 3.1 索引操作

```bash
# 创建索引
curl -X PUT "localhost:9200/students" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "name": { "type": "text" },
      "age": { "type": "integer" },
      "score": { "type": "float" },
      "class": { "type": "keyword" }
    }
  }
}'

# 查看索引
curl "localhost:9200/students"

# 删除索引
curl -X DELETE "localhost:9200/students"
```

### 3.2 文档操作（CRUD）

```bash
# 创建文档（POST，自动生成 ID）
curl -X POST "localhost:9200/students/_doc" -H 'Content-Type: application/json' -d'
{
  "name": "张三",
  "age": 20,
  "score": 85.5,
  "class": "三班"
}'

# 创建文档（PUT，指定 ID）
curl -X PUT "localhost:9200/students/_doc/1" -H 'Content-Type: application/json' -d'
{
  "name": "李四",
  "age": 21,
  "score": 92.0,
  "class": "一班"
}'

# 查询文档
curl "localhost:9200/students/_doc/1"

# 更新文档
curl -X POST "localhost:9200/students/_update/1" -H 'Content-Type: application/json' -d'
{
  "doc": { "score": 95.0 }
}'

# 删除文档
curl -X DELETE "localhost:9200/students/_doc/1"
```

### 3.3 搜索

```bash
# 全文搜索
curl -X GET "localhost:9200/students/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match": {
      "name": "张三"
    }
  }
}'

# 精确查询
curl -X GET "localhost:9200/students/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "term": {
      "class": "三班"
    }
  }
}'

# 范围查询
curl -X GET "localhost:9200/students/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "range": {
      "score": { "gte": 80, "lte": 100 }
    }
  }
}'

# 组合查询（bool）
curl -X GET "localhost:9200/students/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must": [
        { "match": { "class": "三班" } }
      ],
      "filter": [
        { "range": { "score": { "gte": 80 } } }
      ]
    }
  }
}'
```

---

## 四、Java 集成

### 4.1 添加依赖

```xml
<!-- pom.xml -->
<dependency>
    <groupId>co.elastic.clients</groupId>
    <artifactId>elasticsearch-java</artifactId>
    <version>8.12.0</version>
</dependency>
```

### 4.2 基本操作

```java
import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch.core.*;
import co.elastic.clients.elasticsearch.core.search.Hit;

public class ElasticsearchExample {
    private ElasticsearchClient client;

    public void init() throws Exception {
        client = new ElasticsearchClient.Builder()
            .transport(new RestTransportOptions.Builder(
                HttpTransportOptions.builder()
                    .setHosts(new HttpHost("localhost", 9200, "http"))
                    .build())
                .build())
            .build();
    }

    // 索引文档
    public void indexDocument(String id, Map<String, Object> data) throws Exception {
        IndexRequest<Map<String, Object>> request = IndexRequest.of(builder -> builder
            .index("students")
            .id(id)
            .document(data));
        client.index(request);
    }

    // 搜索
    public void search(String keyword) throws Exception {
        SearchRequest request = SearchRequest.of(builder -> builder
            .index("students")
            .query(q -> q
                .match(m -> m
                    .field("name")
                    .query(keyword))));
        
        SearchResponse<Map<String, Object>> response = client.search(request, Map.class);
        
        for (Hit<Map<String, Object>> hit : response.hits().hits()) {
            System.out.println(hit.source());
        }
    }
}
```

---

## 五、与 MySQL 集成

### 5.1 数据同步方案

| 方案 | 说明 | 适用场景 |
|------|------|----------|
| Logstash JDBC Input | 定时轮询 MySQL | 小数据量、非实时 |
| Canal | 监听 MySQL binlog | 实时同步、大数据量 |
| Flink CDC | 流式处理 + CDC | 实时、高吞吐 |
| 应用层双写 | 代码中同时写 MySQL 和 ES | 简单场景 |

### 5.2 Canal 示例

```yaml
# canal.properties
canal.instance.master.address=127.0.0.1:3306
canal.instance.dbUsername=canal
canal.instance.dbPassword=canal
canal.instance.filter.regex=mysdb\\.students
```

---

## 六、性能优化

### 6.1 索引优化

```json
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1,
    "refresh_interval": "30s"
  },
  "mappings": {
    "properties": {
      "name": {
        "type": "text",
        "analyzer": "ik_max_word"
      }
    }
  }
}
```

### 6.2 查询优化

| 优化点 | 说明 |
|--------|------|
| 使用 `filter` 代替 `query` | filter 不计算评分，可缓存 |
| 避免深分页 | 使用 `search_after` 代替 `from + size` |
| 使用 `routing` | 相同 routing 的文档在同一分片 |
| 控制返回字段 | `_source` 指定需要的字段 |

---

## 七、监控与运维

```bash
# 集群健康
curl "localhost:9200/_cluster/health?pretty"

# 节点状态
curl "localhost:9200/_nodes/stats?pretty"

# 索引统计
curl "localhost:9200/students/_stats?pretty"

# 热点线程
curl "localhost:9200/_nodes/hot_threads"
```

---

## 练习

| 题号 | 题目 | 链接 | 知识点 |
|------|------|------|--------|
| P3375 | KMP字符串 | https://www.luogu.com.cn/problem/P3375 | 全文搜索、分词 |
| P3372 | 线段树 | https://www.luogu.com.cn/problem/P3372 | 实时分析、聚合 |
