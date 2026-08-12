
# GTK

| 属性 | 说明 |
|------|------|
| 类型 | 桌面 GUI 工具包 |
| 语言 | C（原生），有 C++/Python/JS 等绑定 |
| 许可证 | LGPL |
| 仓库 | https://www.gtk.org/ |

**核心概念**：GTK 是 GNOME 桌面环境的基础。基于 **GObject** 对象系统，采用信号/回调的事件驱动模型。所有控件（widget）都是 GObject 子类，通过 `g_signal_connect` 绑定回调。

**核心组件**：

| 组件 | 说明 |
|------|------|
| GTK | 控件库（窗口、按钮、文本框、列表、菜单等） |
| GLib | 底层工具库（数据结构、事件循环、Unicode） |
| GDK | 图形后端抽象（X11/Wayland/Win32/macOS） |
| Pango | 国际化文本渲染 |
| GdkPixbuf | 图像加载和操作 |
| ATK | 无障碍访问接口 |

**最小 GTK 窗口**：

```c
#include <gtk/gtk.h>
static void activate(GtkApplication *app, gpointer user_data) {
 GtkWidget *window = gtk_application_window_new(app);
 gtk_window_set_title(GTK_WINDOW(window), "Hello GTK");
 gtk_window_set_default_size(GTK_WINDOW(window), 400, 300);
 gtk_widget_show(window);
}
int main(int argc, char **argv) {
 GtkApplication *app =
 gtk_application_new("org.example.hello", G_APPLICATION_DEFAULT_FLAGS);
 g_signal_connect(app, "activate", G_CALLBACK(activate), NULL);
 int status = g_application_run(G_APPLICATION(app), argc, argv);
 g_object_unref(app);
 return status;
}
```

**编译**：`gcc $(pkg-config --cflags gtk4) main.c $(pkg-config --libs gtk4)`

**跨语言参考**: [[../../../2深化/08_标准库深度|C标准库深度剖析]]
