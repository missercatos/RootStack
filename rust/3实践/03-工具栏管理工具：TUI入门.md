# TUI

## 

TUITerminal UI `ratatui` crate  GUI TUI  terminal cell grid—— ANSI 

ratatui  widget tree`Block`, `Paragraph`, `List`, `Table` `frame.render_stateful_widget(widget, area, &mut state)`  `crossterm` `event::poll` / `event::read`

 60fps`std::time::Duration` diff rendering  frame buffer 

[[../4/07-|Rust: ]]

---

## 

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

## 

### 

TUI 
