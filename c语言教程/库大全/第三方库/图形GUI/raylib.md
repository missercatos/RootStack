
# raylib

| 属性 | 说明 |
|------|------|
| 类型 | 跨平台游戏/多媒体库 |
| 许可证 | zlib |
| 仓库 | https://www.raylib.com/ |

**核心特点**：极简 API，无需复杂的面向对象知识。支持窗口管理、2D/3D 图形、音频、输入处理、数学工具。

**核心模块**：

| 模块 | 功能 |
|------|------|
| `rcore` | 窗口创建、输入、定时 |
| `rshapes` | 基本图形绘制 |
| `rtextures` | 纹理和图像管理 |
| `rtext` | 文本渲染和字体 |
| `rmodels` | 3D 模型加载渲染 |
| `raudio` | 音频播放 |

**最小 raylib 程序**：

```c
#include "raylib.h"
int main(void) {
    InitWindow(800, 600, "Raylib Window");
    while (!WindowShouldClose()) {
        BeginDrawing();
        ClearBackground(RAYWHITE);
        DrawText("Hello, Raylib!", 200, 250, 30, DARKGREEN);
        EndDrawing();
    }
    CloseWindow();
    return 0;
}
```

> raylib 是学习游戏编程和图形学的最佳 C 库——无需理解复杂的渲染管线即可绘制形状和纹理。

**跨语言参考**: [[../../../2深化/08_标准库深度|C标准库深度剖析]]
