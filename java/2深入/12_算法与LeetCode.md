# 12 算法与LeetCode

这是深入篇的收官章，也是通往面试与竞赛的桥梁：搭建高效的 Java 刷题环境、整理常用数据结构 API 速查表、盘点高频踩坑点，最后给出按专题推进的刷题路线。目标是让你打开 LeetCode 后不再纠结"环境怎么弄""API 怎么写"，把精力全部留给算法本身。

> 前置知识：本篇全部章节；联动 [[路径D-DSA算法刷题|DSA 学习路线]]。

---

## 一、刷题环境

### 1.1 单文件提交模板

LeetCode 核心代码模式只需补全给定函数。本地练习推荐一个万能骨架：

```java
public class Solution {

    // ===== 题目给定的签名，直接在此实现 =====
    public int[] twoSum(int[] nums, int target) {
        var seen = new java.util.HashMap<Integer, Integer>();   // var 减少样板
        for (int i = 0; i < nums.length; i++) {
            Integer j = seen.get(target - nums[i]);
            if (j != null) {
                return new int[]{j, i};
            }
            seen.put(nums[i], i);
        }
        return new int[0];
    }

    // ===== 本地调试 main，提交时删除或保留均可 =====
    public static void main(String[] args) {
        Solution s = new Solution();
        System.out.println(java.util.Arrays.toString(
            s.twoSum(new int[]{2, 7, 11, 15}, 9)));   // [0, 1]
    }
}
```

IDEA 用户建议装 "LeetCode Editor" 类插件直接刷；VS Code 有 LeetCode 扩展。

### 1.2 IO 模板：Scanner vs BufferedReader

部分平台（牛客、ACM 赛制）要求自己处理输入输出：

```java
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Arrays;
import java.util.StringTokenizer;

public class IoTemplate {
    public static void main(String[] args) throws IOException {
        // 方式一 Scanner：简单但慢（正则解析 + 同步开销），小数据量可用
        // var sc = new java.util.Scanner(System.in);
        // int n = sc.nextInt();

        // 方式二 BufferedReader：大数据量必用，快一个数量级
        var br = new BufferedReader(new InputStreamReader(System.in));
        var st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        int[] arr = new int[n];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            arr[i] = Integer.parseInt(st.nextToken());
        }

        Arrays.sort(arr);
        var sb = new StringBuilder();          // 输出也必须攒批，逐行 println 会超时
        for (int v : arr) {
            sb.append(v).append(' ');
        }
        System.out.println(sb);
    }
}
```

| 维度 | Scanner | BufferedReader+StringTokenizer |
|------|---------|--------------------------------|
| 易用性 | 直接 nextInt | 手动 parse |
| 百万级 token 耗时 | 秒级 | 百毫秒级 |
| 结论 | 小数据 | **竞赛与大数据量默认选它** |

---

## 二、常用数据结构 API 速查

### 2.1 ArrayDeque：栈与队列的统一答案

JDK 明确建议**用它替代 Stack 与 LinkedList** 做栈/队列：

```java
import java.util.ArrayDeque;
import java.util.Deque;

public class DequeApi {
    public static void main(String[] args) {
        // 当栈：push/pop/peek 对应 addFirst/removeFirst/peekFirst
        Deque<Integer> stack = new ArrayDeque<>();
        stack.push(1); stack.push(2); stack.push(3);
        System.out.println(stack.pop());       // 3
        System.out.println(stack.peek());      // 2

        // 当队列：offer/poll/peek
        Deque<Integer> queue = new ArrayDeque<>();
        queue.offer(1); queue.offer(2); queue.offer(3);
        System.out.println(queue.poll());      // 1

        // 当双端队列
        queue.addFirst(0);
        queue.addLast(4);
        System.out.println(queue);             // [0, 2, 3, 4]
    }
}
```

注意：`Stack` 继承自 Vector 且全表 synchronized，是历史遗留，不要再用。

### 2.2 PriorityQueue：堆题专用

```java
import java.util.Comparator;
import java.util.PriorityQueue;

public class HeapApi {
    public static void main(String[] args) {
        // 小顶堆（默认）
        PriorityQueue<Integer> minHeap = new PriorityQueue<>();
        // 大顶堆：自定义 Comparator
        PriorityQueue<Integer> maxHeap =
            new PriorityQueue<>(Comparator.reverseOrder());
        // 或 (a, b) -> b - a，但大数相减可能溢出，推荐 compare 方法

        int[] nums = {5, 1, 9, 3, 7};
        for (int n : nums) { minHeap.offer(n); }

        System.out.println(minHeap.peek());    // 1
        while (!minHeap.isEmpty()) {
            System.out.print(minHeap.poll() + " ");   // 依次弹出最小值
        }

        // 自定义对象排序：按第二个维度比较的二维数组
        PriorityQueue<int[]> bySecond =
            new PriorityQueue<>((a, b) -> Integer.compare(a[1], b[1]));
        bySecond.offer(new int[]{1, 5});
        bySecond.offer(new int[]{2, 3});
        System.out.println("\n" + java.util.Arrays.toString(bySecond.poll())); // [2, 3]
    }
}
```

### 2.3 其他高频容器速查表

| 容器 | 初始化 | 高频方法 |
|------|--------|----------|
| HashMap | `new HashMap<>()` | put/get/getOrDefault/containsKey |
| TreeMap | `new TreeMap<>()` | floorKey/ceilingKey/firstKey/subMap |
| HashSet | `new HashSet<>()` | add/contains/remove |
| StringBuilder | `new StringBuilder()` | append/reverse/setCharAt |
| char 数组 | `s.toCharArray()` | 直接下标操作比 charAt 快 |

---

## 三、字符与大整数技巧

```java
import java.math.BigInteger;

public class TricksDemo {
    public static void main(String[] args) {
        String s = "a1b2c3";

        // 技巧一：字符数字互转 —— char 本质是无符号整数
        char c = '7';
        int digit = c - '0';                    // 7，核心技巧必须秒写
        char back = (char) ('0' + 5);           // '5'

        // 技巧二：字符分类判断
        boolean isD = Character.isDigit('5');
        boolean isL = Character.isLetter('a');
        boolean upper = Character.isUpperCase('A');
        System.out.println(digit + " " + back + " " + isD + isL + upper);

        // 技巧三：大小写转换（位运算版更快）
        char lowerA = (char) ('A' | 32);        // 'a'

        // 技巧四：BigInteger 处理超长整数（阶乘/大数运算类题目）
        BigInteger fact = BigInteger.ONE;
        for (int i = 2; i <= 25; i++) {
            fact = fact.multiply(BigInteger.valueOf(i));   // 25! 已超 long
        }
        System.out.println("25! = " + fact);

        // 常用方法：add/subtract/multiply/mod/compareTo/pow
        System.out.println(BigInteger.TWO.pow(100));
    }
}
```

---

## 四、常见坑清单

每个坑都真实吞掉过无数 AC 时间：

| 坑 | 示例 | 正确姿势 |
|----|------|----------|
| Integer 缓存 == 比较 | `Integer a=127, b=127; a==b` 为 true，128 时为 false | 一律 equals 或拆箱 intValue() |
| String 拼接循环 | 循环内 `+=` 每次 O(n)，总 O(n^2) | StringBuilder.append |
| 二维数组排序 lambda | `(a, b) -> a - b` 可能溢出 | 用 `Integer.compare(a[0], b[0])` |
| Arrays.sort 降序 | `sort(arr, cmp)` 不支持 int[] | 先转 `Integer[]` 或排序后反转 |
| 整型溢出 | mid = (l+r)/2 在大数组越界 | `l + (r - l) / 2` |
| 除零与取模负数 | Java 的 % 结果符号跟被除数 | 需要非负模时 `((x % m) + m) % m` |
| 字符串相等 == | 比较的是引用 | equals() |
| 浮点比较 | `==` 受精度误差干扰 | `Math.abs(a-b) < 1e-6` |

```java
import java.util.Arrays;
import java.util.List;

public class PitfallDemo {
    public static void main(String[] args) {
        // 坑一现场：Integer 缓存区间 [-128, 127]
        Integer a = 127, b = 127;
        Integer c = 128, d = 128;
        System.out.println((a == b) + " " + c.equals(d));   // true false->equals 为 true

        // 坑四现场：降序排 int[]
        List<Integer> boxed = new java.util.ArrayList<>(
            java.util.List.of(3, 1, 4, 1, 5));
        boxed.sort(java.util.Collections.reverseOrder());
        System.out.println(boxed);                          // [5, 4, 3, 1, 1]

        // 二维数组按首列升序的安全写法
        int[][] intervals = {{5, 8}, {1, 3}, {2, 6}};
        Arrays.sort(intervals, (x, y) -> Integer.compare(x[0], y[0]));
        System.out.println(Arrays.deepToString(intervals)); // [[1, 3], [2, 6], [5, 8]]
    }
}
```

---

## 五、复杂度分析复习

刷题前先校准复杂度直觉，它决定你选的算法能不能过：

| 数据规模 n | 可接受复杂度 | 典型算法 |
|------------|--------------|----------|
| n <= 20 | O(2^n) | 状压枚举、回溯 |
| n <= 500 | O(n^3) | 区间 DP、Floyd |
| n <= 5000 | O(n^2) | 普通 DP、双重循环 |
| n <= 10^5 | O(n log n) | 排序、堆、二分 |
| n >= 10^6 | O(n) 或 O(n log n) | 双指针、滑动窗口、哈希 |

经验法则：Java 每秒约执行 10^8 次简单操作，LeetCode 时限一般按此放宽两到四倍。

---

## 六、题型分类导航

### 6.1 双指针与滑动窗口（5 题入门）

| 题目 | 链接 |
|------|------|
| [移动零](https://leetcode.cn/problems/move-zeroes/) | move-zeroes，快慢指针最简模型 |
| [盛最多水的容器](https://leetcode.cn/problems/container-with-most-water/) | container-with-most-water，对撞指针贪心 |
| [无重复字符的最长子串](https://leetcode.cn/problems/longest-substring-without-repeating-characters/) | longest-substring-without-repeating-characters，滑动窗口模板题 |
| [三数之和](https://leetcode.cn/problems/3sum/) | 3sum，排序+对撞去重综合 |
| [接雨水](https://leetcode.cn/problems/trapping-rain-water/) | trapping-rain-water，双指针进阶 |

滑动窗口模板骨架：右指针扩张 -> 条件不满足时左指针收缩 -> 每步更新答案。背熟这个循环不变量，一类题全通。

### 6.2 二叉树递归（5 题）

| 题目 | 链接 |
|------|------|
| [二叉树的中序遍历](https://leetcode.cn/problems/binary-tree-inorder-traversal/) | binary-tree-inorder-traversal，递归/迭代/Morris 三解 |
| [二叉树的最大深度](https://leetcode.cn/problems/maximum-depth-of-binary-tree/) | maximum-depth-of-binary-tree，后序递归入门 |
| [翻转二叉树](https://leetcode.cn/problems/invert-binary-tree/) | invert-binary-tree |
| [对称二叉树](https://leetcode.cn/problems/symmetric-tree/) | symmetric-tree，双参数递归 |
| [验证二叉搜索树](https://leetcode.cn/problems/validate-binary-search-tree/) | validate-binary-search-tree，上下界传递 |

递归心法：只想"当前节点做什么"与"返回什么给父节点"，不要展开整棵树的执行过程。

### 6.3 回溯（5 题）

| 题目 | 链接 |
|------|------|
| [全排列](https://leetcode.cn/problems/permutations/) | permutations，回溯第一课 |
| [子集](https://leetcode.cn/problems/subsets/) | subsets，选或不选 |
| [组合总和](https://leetcode.cn/problems/combination-sum/) | combination-sum，可重复选取 |
| [电话号码的字母组合](https://leetcode.cn/problems/letter-combinations-of-a-phone-number/) | letter-combinations-of-a-phone-number |
| [单词搜索](https://leetcode.cn/problems/word-search/) | word-search，网格 DFS+状态还原 |

回溯三件套：路径（已做选择）、选择列表、结束条件；递归前后对称地"做选择/撤销选择"。

### 6.4 动态规划（5 题）

| 题目 | 链接 |
|------|------|
| [爬楼梯](https://leetcode.cn/problems/climbing-stairs/) | climbing-stairs，DP 的 Hello World |
| [打家劫舍](https://leetcode.cn/problems/house-robber/) | house-robber，选与不选的状态机 |
| [零钱兑换](https://leetcode.cn/problems/coin-change/) | coin-change，完全背包 |
| [最长递增子序列](https://leetcode.cn/problems/longest-increasing-subsequence/) | longest-increasing-subsequence，O(n^2) 与贪心+二分双解 |
| [编辑距离](https://leetcode.cn/problems/edit-distance/) | edit-distance，二维 DP 终极试炼 |

动规五步法：定义状态 -> 转移方程 -> 初始化 -> 遍历顺序 -> 空间优化。

### 6.5 栈与哈希（补充）

| 题目 | 链接 |
|------|------|
| [有效的括号](https://leetcode.cn/problems/valid-parentheses/) | valid-parentheses |
| [最小栈](https://leetcode.cn/problems/min-stack/) | min-stack，辅助栈设计 |
| [两数之和](https://leetcode.cn/problems/two-sum/) | two-sum |
| [每日温度](https://leetcode.cn/problems/daily-temperatures/) | daily-temperatures，单调栈模板 |

---

## 七、刷题计划建议

```mermaid
flowchart LR
    A["第 1-2 周<br/>数组/字符串/哈希<br/>约 30 题"] --> B["第 3-4 周<br/>双指针/滑动窗口/栈<br/>约 25 题"]
    B --> C["第 5-6 周<br/>链表/二叉树<br/>约 25 题"]
    C --> D["第 7-8 周<br/>回溯/DFS/BFS<br/>约 25 题"]
    D --> E["第 9-10 周<br/>动态规划专题<br/>约 30 题"]
    E --> F["第 11-12 周<br/>热题 100 收尾<br/>错题重做"]
```

执行要点：

1. **按专题推进**而非随机刷——同类型连做形成模式识别
2. **一题多解**：暴力解先 AC，再优化到目标复杂度
3. **隔天复盘**：错题第二天重写一遍，一周后再来一遍
4. **控制时长**：单题卡 40 分钟看题解不丢人，理解后闭卷重写才算过
5. 与 [[路径D-DSA算法刷题|DSA 学习路线]] 配合：理论章与对应 LeetCode 专题同步推进

---

## 八、小结

| 板块 | 关键词 |
|------|--------|
| 环境 | BufferedReader + StringBuilder 批量 IO |
| API | ArrayDeque 当栈队列，PriorityQueue 自定义比较器 |
| 技巧 | c - '0'、Character.isDigit、BigInteger |
| 坑 | Integer equals、compare 防溢出、StringBuilder |
| 计划 | 专题推进 + 错题复盘 + 一题多解 |

至此深入篇完结。你已经拥有：泛型与反射的底层认知、集合与并发的源码级理解、JVM 的运维能力、现代 Java 的完整语法，以及一条通往面试的刷题路线。下一步建议进入 [[java/3工程化|工程化篇]]：Maven、Spring Boot 与真实项目开发。
