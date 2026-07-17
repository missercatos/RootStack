# SDL2

"Simple DirectMedia Layer" — 游戏开发底层库的行业标杆。提供跨平台的窗口创建、OpenGL/Vulkan 上下文、键盘/鼠标/手柄输入、2D 渲染、音频播放等功能。Valve、Unity 等商业产品在其底层使用 SDL2。C 语言编写但 C++ 可直接使用。

## 核心组件

| 组件 | 说明 |
|------|------|
| SDL_Window | 跨平台窗口管理 |
| SDL_Renderer | 2D 加速渲染 |
| SDL_Surface / Texture | 位图和纹理操作 |
| SDL_Event | 输入事件处理（键盘/鼠标/手柄） |
| SDL_Audio | 音频播放和录制 |
| SDL_ttf | 字体和文字渲染（扩展库） |
| SDL_image | 图像加载（扩展库） |

## 何时使用

- 需要完全控制游戏循环的底层开发
- 引擎开发和跨平台游戏移植
- 需要跨平台窗口+输入+OpenGL 的项目
- 需要手柄/游戏控制器支持

## 关键特性

跨平台窗口与输入、多图形 API 上下文、音频、手柄支持、稳定 API

## 相关链接

- [[SFML|SFML]] — C++ 风格多媒体库
- [[raylib|raylib]] — 更简化的游戏库
- 
- 
- (搜索: SDL2)
