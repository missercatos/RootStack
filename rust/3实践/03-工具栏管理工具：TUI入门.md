# 工具栏管理工具：TUI入门

## 原理

TUI（Terminal UI）使用 `ratatui` crate 在终端中构建界面。与 GUI 不同，TUI 基于 terminal cell grid，无像素渲染——整个界面由字符（包括 ANSI 颜色码）构成。

ratatui 是保留模式框架：先构建 widget tree（`Block`, `Paragraph`, `List`, `Table`），再调用 `frame.render_stateful_widget(widget, area, &mut state)` 绘制。事件处理通过 `crossterm` 读取键盘输入（`event::poll` / `event::read`）。

帧绘制频率通常为 60fps（`std::time::Duration` 的帧间隔）。diff rendering 避免重绘未变化区域（从上一次 frame buffer 比较）。

[[../4工程/07-并发与异步安全|Rust: 异步安全]]

---

## 语法

```toml
[dependencies]
ratatui = "0.28"
crossterm = "0.28"
```

```rust
use ratatui::{Frame, widgets::{Block, Borders, List, ListItem}};
use crossterm::event::{self, Event, KeyCode};

struct App {
    items: Vec<String>,
    selected: usize,
}

fn ui(frame: &mut Frame, app: &App) {
    let items: Vec<ListItem> = app.items.iter()
        .map(|s| ListItem::new(s.as_str()))
        .collect();
    let list = List::new(items)
        .block(Block::default().title("Tools").borders(Borders::ALL));
    frame.render_widget(list, frame.area());
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let stdout = std::io::stdout();
    let mut backend = ratatui::backend::CrosstermBackend::new(stdout);
    backend.enable_raw_mode()?;

    let mut app = App { items: vec![], selected: 0 };
    loop {
        backend.draw(|f| ui(f, &app))?;
        if event::poll(Duration::from_millis(16))? {
            match event::read()? {
                Event::Key(key) => match key.code {
                    KeyCode::Char('q') => break,
                    KeyCode::Down => { app.selected += 1; }
                    _ => {}
                },
                _ => {}
            }
        }
    }
    Ok(())
}
```

---

## 实践

### 洛谷问题

TUI 项目与算法竞赛无直接关系。建议用此项目练习字符串格式化和结构体组织。

### AI 自检

1. ratatui 的 `render_widget` 如何在 60fps 下保持流畅？diff rendering 原理？
2. `crossterm` 和 `termion` 的区别？为何推荐 crossterm？
