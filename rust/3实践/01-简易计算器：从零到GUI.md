# GUI

## 

GUI  `egui` immediate moderetained mode
-  UI  widget 
- widget 

egui  OpenGL  `eframe`  winit  `update`  `ui.button("text").clicked()`  bool

 →  →  →  + - * / 

---

## 

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

## 

### 

:  — 

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
