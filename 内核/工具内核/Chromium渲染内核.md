
# Chromium 渲染内核

> Blink 渲染引擎——HTML → DOM → Layout → Paint → Composite 的完整渲染流水线。

## 概念

Chromium 的渲染内核 (Blink) 是浏览器将 HTML/CSS/JavaScript 转化为屏幕像素的核心引擎。它的流水线是"声明式语言 → 树结构 → 像素"的逐层变换。理解 Blink 相当于理解"如何高效组织一个实时 UI 框架"。Chromium 的 C++ 代码量超过 2000 万行，渲染引擎部分约 200 万行。

## 核心组件

| 组件 | 职责 | 关键概念 |
|------|------|---------|
| HTML Parser | 字节流 → DOM Tree | 增量解析, 网络流式 |
| CSS Parser | 样式表 → 样式规则 | 优先级 (specificity) 计算 |
| Style Engine | 匹配选择器, 计算每个 DOM 节点的 computed style | 样式层叠 |
| Layout Engine | 根据 computed style 计算每个元素的几何位置与大小 | 格式化上下文 (BFC, IFC) |
| Paint Layer | 将 Layout 结果转化为绘制指令列表 (display list) | Skia 绘制 |
| Compositor | 分层渲染 + GPU 合成 | impl thread |
| V8 / JavaScript | JS 执行, DOM API 绑定 | 与渲染管道交错 |

## Blink 渲染管线

```
mermaid
graph TD
    HTML["HTML 字节流"] --> Parser["HTML Parser<br/>增量解析"]
    Parser --> DOM["DOM Tree"]
    DOM --> |"preload scanner"| NET["网络资源加载<br/>CSS, JS, 图片, 字体"]

    CSS["CSS 样式表"] --> CSSParser["CSS Parser"]
    CSSParser --> CSSOM["CSSOM Tree"]

    DOM --> Style["Style Engine<br/>选择器匹配 + 层叠"]
    CSSOM --> Style
    Style --> StyleTree["Computed Style<br/>(每个节点最终样式)"]

    StyleTree --> Layout["Layout Engine<br/>几何计算: BFC, IFC"]
    Layout --> LayoutTree["Layout Tree<br/>(每节点: x,y,w,h + LineBoxes)"]

    LayoutTree --> Paint["Paint<br/>将 Layout 转化为绘制指令"]
    Paint --> DisplayList["Skia Display List<br/>(drawRect, drawText, drawImage...)"]

    DisplayList --> Composite["Compositor<br/>图层合并"]
    Composite --> GPU["GPU 合成<br/>GL/D3D/Vulkan"]
    GPU --> Screen["屏幕像素"]

    style Parser fill:#ff9,stroke:#333
    style Layout fill:#9cf,stroke:#333
    style Composite fill:#9f9,stroke:#333
```

## Layout 引擎核心

```c++
// 简化版 Layout 流程
void LayoutObject::Layout() {
    // 1. 计算包含块宽度 (宽度自顶向下传递)
    int available_width = containing_block->Width();

    // 2. 根据 Display 类型决定格式化上下文
    if (IsBlockLevel()) {
        LayoutBlock();    // BFC: 宽度填满父容器, 高度由内容撑开
    } else if (IsInline()) {
        LayoutInline();   // IFC: 横向流式排列, 自动换行
    } else if (IsFlex()) {
        LayoutFlex();     // 主轴/交叉轴弹性计算
    } else if (IsGrid()) {
        LayoutGrid();     // 网格布局
    }

    // 3. 递归布局子节点
    for (auto child : Children()) {
        child->Layout();
    }

    // 4. 当子节点布局完毕, 父节点才能确定高度
    //    (这就是为什么 CSS 百分比高度需要父元素有明确高度)
    ComputeHeight();
}
```

## 合成器 (Compositor)

```
分层合成:
    传统方式: 每帧重绘整个页面 → 性能瓶颈
    分层合成: 将页面分为多个图层, 独立绘制, GPU 合成

图层提升条件:
    1. 3D 变换 (transform: translateZ(0))
    2. video / canvas 元素
    3. 滚动区域 (overflow: scroll)
    4. CSS will-change 属性
    5. CSS 动画 (animation / transition) 作用于 transform/opacity

合成线程 (Impl Thread):
    主线程: JS → Style → Layout → Paint → Commit (给出绘制指令)
    合成线程: 接收 Commit → 栅格化图层 → 合成 → Display
    关键: 合成线程可以处理滚动和 transform 动画,
          即使主线程被 JS 阻塞, 页面仍然可以平滑滚动!

GPU 命令:
    每帧给 GPU 的指令本质上是:
        对每层: 绑定纹理 → 设置变换矩阵 → 设置混合模式 → 绘制四边形
```
---

