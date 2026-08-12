
# SDL2

| 属性 | 说明 |
|------|------|
| 类型 | 跨平台多媒体基础库 |
| 许可证 | zlib |
| 仓库 | https://www.libsdl.org/ |

**核心概念**：SDL2 是游戏行业的"汇编语言级"基础——不是引擎，而是跨平台的系统和图形抽象层。几乎所有的 C/C++ 游戏引擎和多媒体应用都以某种方式依赖 SDL2。

**核心子系统**：

| 子系统 | 功能 |
|--------|------|
| Video | 窗口管理 + 2D 渲染（软件/OpenGL/Direct3D/Vulkan） |
| Events | 事件队列（键盘、鼠标、窗口、手柄） |
| Audio | 音频播放和录制 |
| Timer | 高精度计时器 |
| Joystick/GameController | 游戏手柄和力反馈 |

```c
#include <SDL2/SDL.h>
int main(void) {
 SDL_Init(SDL_INIT_VIDEO);
 SDL_Window *win = SDL_CreateWindow("SDL2", 100, 100, 800, 600, 0);
 SDL_Renderer *ren = SDL_CreateRenderer(win, -1, 0);
 SDL_Event e;
 int running = 1;
 while (running) {
 while (SDL_PollEvent(&e))
 if (e.type == SDL_QUIT) running = 0;
 SDL_SetRenderDrawColor(ren, 0, 0, 0, 255);
 SDL_RenderClear(ren);
 SDL_RenderPresent(ren);
 }
 SDL_DestroyRenderer(ren);
 SDL_DestroyWindow(win);
 SDL_Quit();
 return 0;
}
```

**编译**：`gcc main.c $(sdl2-config --cflags --libs)`

**跨语言参考**: [[../../../2深化/08_标准库深度|C标准库深度剖析]]
