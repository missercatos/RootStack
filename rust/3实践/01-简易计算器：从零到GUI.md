# 简易计算器：从零到GUI

## 原理

GUI 框架选择 `egui`（立即模式 immediate mode），与保留模式（retained mode）的区别：
- 立即模式：每帧重建 UI 描述，无持久 widget 树，适合工具和原型
- 保留模式：widget 有生命周期，适合复杂应用程序

egui 基于 OpenGL 渲染后端，通过 `eframe` 运行。事件循环由 winit 驱动，每帧调用 `update` 函数重新绘制。按钮由 `ui.button("text").clicked()` 返回 bool，无回调注册。

表达式求值使用简单的运算符扫描（状态机：读数字 → 遇到运算符 → 保存操作数 → 继续），支持 + - * / 四则运算。

---

## 语法

```toml
# Cargo.toml
[dependencies]
eframe = "0.28"
```

```rust
use eframe::egui;

#[derive(Default)]
struct Calculator {
    display: String,
}

impl eframe::App for Calculator {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui::CentralPanel::default().show(ctx, |ui| {
            ui.heading(&self.display);
            ui.columns(4, |cols| {
                for (i, label) in ["7","8","9","/"].iter().enumerate() {
                    if cols[i].button(label).clicked() {
                        self.display.push_str(label);
                    }
                }
            });
        });
    }
}

fn main() -> Result<(), eframe::Error> {
    eframe::run_native(
        "Calculator",
        Default::default(),
        Box::new(|_cc| Ok(Box::<Calculator>::default())),
    )
}
```

---

## 实践

### 力扣问题

力扣: 力扣表达式求值 — 基础表达式解析

```rust
fn eval(expr: &str) -> i64 {
    let mut result = 0i64;
    let mut num = String::new();
    let mut is_mul = false;
    let mut last = 1i64;
    for ch in expr.chars().chain(std::iter::once(' ')) {
        match ch {
            '0'..='9' => num.push(ch),
            _ => {
                let n: i64 = num.parse().unwrap_or(0);
                num.clear();
                if is_mul { last = (last * n) % 10000; }
                else { result = (result + last) % 10000; last = n; }
                is_mul = ch == '*';
            }
        }
    }
    (result + last) % 10000
}
```

### AI 自检

1. egui 的立即模式如何避免界面闪烁？布局缓存机制是什么？
2. `eframe::run_native` 的主事件循环结构是怎样的？
