# Lua + Love2D 游戏开发示例

Love2D 是一个基于 Lua 的 2D 游戏引擎，让你用纯 Lua 编写游戏，无需编译，跨平台运行。本章演示如何运用你学到的 Lua 知识制作游戏。

---

## 第1节：Love2D 简介

### 什么是 Love2D？

Love2D（简称 Love）是一个开源的 2D 游戏框架，它：
- 使用 **Lua**（通常 LuaJIT）作为脚本语言
- 提供图形、音频、输入、物理等模块
- **跨平台**：Windows / macOS / Linux / iOS / Android
- 项目就是一个文件夹，运行 `love .` 即可

### 安装

```bash
# Arch Linux
sudo pacman -S love

# Ubuntu/Debian
sudo apt install love

# macOS
brew install love

# Windows: 从 https://love2d.org 下载安装包
```

### 验证

```bash
love --version
# LOVE 11.5 (Mysterious Mysteries)
```

---

## 第2节：最小项目结构与运行

```
my_game/
├── main.lua      # 唯一必需的文件
├── conf.lua      # 可选：窗口/渲染配置
└── assets/       # 可选：资源目录
    ├── images/
    └── sounds/
```

### main.lua 核心模板

```lua
-- main.lua — 游戏入口

function love.load()
  -- 初始化：只调用一次
end

function love.update(dt)
  -- 每帧更新：dt 是秒数（delta time）
end

function love.draw()
  -- 每帧渲染：所有绘制在这里
end

function love.keypressed(key)
  -- 按键事件
end
```

### conf.lua（窗口配置）

```lua
-- conf.lua
function love.conf(t)
  t.title = "我的游戏"        -- 窗口标题
  t.window.width = 800        -- 宽度
  t.window.height = 600       -- 高度
  t.window.resizable = false  -- 不可调整大小
  t.version = "11.5"          -- Love 版本
end
```

### 运行

```bash
love .          # 在项目目录下运行
# 或打包成 .love 文件：
zip -r game.love . && love game.love
```

---

## 第3节：完整游戏示例 — 打砖块 (Breakout)

这是一个完整的打砖块游戏，综合运用了之前学习的 Lua 知识。

### 项目结构

```
breakout/
├── main.lua      -- 主入口和游戏循环
├── conf.lua      -- 窗口配置
├── ball.lua      -- 球模块
├── paddle.lua    -- 挡板模块
├── brick.lua     -- 砖块模块
└── levels.lua    -- 关卡数据
```

### conf.lua

```lua
function love.conf(t)
  t.title = "打砖块 — Lua 示例"
  t.window.width = 800
  t.window.height = 600
  t.window.resizable = false
end
```

### ball.lua — 球模块

```lua
-- ball.lua
local Ball = {}
Ball.__index = Ball

function Ball:new(x, y, radius, speed)
  local obj = {
    x = x or 400,
    y = y or 400,
    radius = radius or 8,
    speed = speed or 300,
    dx = speed * 0.7,  -- 水平速度
    dy = -speed * 0.7, -- 垂直速度
  }
  return setmetatable(obj, self)
end

function Ball:update(dt)
  self.x = self.x + self.dx * dt
  self.y = self.y + self.dy * dt

  -- 墙壁碰撞
  local w = love.graphics.getWidth()
  if self.x - self.radius < 0 then
    self.x = self.radius
    self.dx = -self.dx
  elseif self.x + self.radius > w then
    self.x = w - self.radius
    self.dx = -self.dx
  end
  if self.y - self.radius < 0 then
    self.y = self.radius
    self.dy = -self.dy
  end
end

function Ball:draw()
  love.graphics.circle("fill", self.x, self.y, self.radius)
end

-- AABB 碰撞检测
function Ball:collidesWith(obj)
  return self.x + self.radius > obj.x
     and self.x - self.radius < obj.x + obj.width
     and self.y + self.radius > obj.y
     and self.y - self.radius < obj.y + obj.height
end

function Ball:bounceHorizontal()
  self.dx = -self.dx
end

function Ball:bounceVertical()
  self.dy = -self.dy
end

return Ball
```

### paddle.lua — 挡板模块

```lua
-- paddle.lua
local Paddle = {}
Paddle.__index = Paddle

function Paddle:new(x, y, width, height, speed)
  local obj = {
    x = x or 350,
    y = y or 560,
    width = width or 100,
    height = height or 15,
    speed = speed or 500,
  }
  return setmetatable(obj, self)
end

function Paddle:update(dt)
  if love.keyboard.isDown("left") or love.keyboard.isDown("a") then
    self.x = self.x - self.speed * dt
  elseif love.keyboard.isDown("right") or love.keyboard.isDown("d") then
    self.x = self.x + self.speed * dt
  end

  -- 边界限制
  local w = love.graphics.getWidth()
  if self.x < 0 then
    self.x = 0
  elseif self.x + self.width > w then
    self.x = w - self.width
  end
end

function Paddle:draw()
  love.graphics.rectangle("fill", self.x, self.y, self.width, self.height)
end

return Paddle
```

### brick.lua — 砖块模块

```lua
-- brick.lua
local Brick = {}
Brick.__index = Brick

-- 砖块颜色表（按行）
local colors = {
  {1, 0.3, 0.3},  -- 红
  {1, 0.6, 0.2},  -- 橙
  {0.2, 1, 0.3},  -- 绿
  {0.2, 0.6, 1},  -- 蓝
  {0.8, 0.3, 1},  -- 紫
}

function Brick:new(x, y, width, height, hits)
  local obj = {
    x = x,
    y = y,
    width = width or 70,
    height = height or 20,
    hp = hits or 1,  -- 需要击打次数
    maxHp = hits or 1,
  }
  return setmetatable(obj, self)
end

function Brick:hit()
  self.hp = self.hp - 1
  return self.hp <= 0  -- 返回 true 表示砖块被摧毁
end

function Brick:draw()
  if self.hp <= 0 then return end

  local alpha = self.hp / self.maxHp
  local row = math.floor(self.y / 25) % #colors + 1
  local c = colors[row]

  love.graphics.setColor(c[1], c[2], c[3], 0.5 + alpha * 0.5)
  love.graphics.rectangle("fill", self.x, self.y, self.width - 2, self.height - 2)
  love.graphics.setColor(1, 1, 1, 1)
end

return Brick
```

### levels.lua — 关卡数据

```lua
-- levels.lua
local levels = {}

-- 关卡1：标准布局
levels[1] = {
  {0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
  {1, 1, 1, 1, 1, 1, 1, 1, 1, 1},
  {1, 1, 1, 1, 1, 1, 1, 1, 1, 1},
  {1, 1, 1, 1, 1, 1, 1, 1, 1, 1},
  {1, 1, 1, 1, 1, 1, 1, 1, 1, 1},
  {2, 2, 2, 2, 2, 2, 2, 2, 2, 2},
}

-- 关卡2：交错布局
levels[2] = {
  {1, 0, 1, 0, 1, 0, 1, 0, 1, 0},
  {0, 1, 0, 1, 0, 1, 0, 1, 0, 1},
  {1, 0, 2, 0, 1, 0, 2, 0, 1, 0},
  {0, 1, 0, 2, 0, 1, 0, 2, 0, 1},
  {1, 0, 1, 0, 2, 0, 1, 0, 1, 0},
  {0, 1, 0, 1, 0, 2, 0, 1, 0, 1},
}

-- 数字含义: 0=空, 1=普通砖(1HP), 2=强化砖(2HP), 3=坚固砖(3HP)

return levels
```

### main.lua — 主游戏逻辑

```lua
-- main.lua — 打砖块游戏入口

local Ball = require("ball")
local Paddle = require("paddle")
local Brick = require("brick")
local levels = require("levels")

-- ============================================
-- 游戏状态
-- ============================================
local state = {
  menu = "menu",
  playing = "playing",
  win = "win",
  lose = "lose",
}

local game = {}

-- ============================================
-- love.load — 初始化
-- ============================================
function love.load()
  math.randomseed(os.time())
  game.state = state.menu
  game.lives = 3
  game.score = 0
  game.currentLevel = 1
  game.totalLevels = #levels
  loadLevel(game.currentLevel)
end

function loadLevel(levelNum)
  game.ball = Ball:new(400, 500, 8, 300)
  game.paddle = Paddle:new()

  -- 解析关卡数据生成砖块
  game.bricks = {}
  local levelData = levels[levelNum]
  if not levelData then
    game.state = state.win
    return
  end

  local brickW = 70
  local brickH = 20
  local offsetX = 50
  local offsetY = 50

  for row = 1, #levelData do
    for col = 1, #levelData[row] do
      local hp = levelData[row][col]
      if hp > 0 then
        table.insert(game.bricks, Brick:new(
          (col - 1) * brickW + offsetX,
          (row - 1) * brickH + offsetY,
          brickW, brickH, hp
        ))
      end
    end
  end
end

-- ============================================
-- love.update — 每帧更新
-- ============================================
function love.update(dt)
  if game.state == state.playing then
    updateGame(dt)
  end
end

function updateGame(dt)
  game.ball:update(dt)
  game.paddle:update(dt)

  -- 球与挡板碰撞
  if game.ball:collidesWith(game.paddle) then
    game.ball.y = game.paddle.y - game.ball.radius
    game.ball:bounceVertical()
    -- 根据击中挡板的位置改变球的角度
    local hitPos = (game.ball.x - game.paddle.x) / game.paddle.width
    game.ball.dx = game.ball.speed * (hitPos - 0.5) * 2
  end

  -- 球与砖块碰撞
  for i = #game.bricks, 1, -1 do
    local brick = game.bricks[i]
    if game.ball:collidesWith(brick) then
      local isDestroyed = brick:hit()
      if game.ball.x < brick.x or game.ball.x > brick.x + brick.width then
        game.ball:bounceHorizontal()
      else
        game.ball:bounceVertical()
      end

      if isDestroyed then
        table.remove(game.bricks, i)
        game.score = game.score + 10 * brick.maxHp
      end
      break  -- 每帧只处理一个碰撞
    end
  end

  -- 球落出屏幕
  if game.ball.y - game.ball.radius > love.graphics.getHeight() then
    game.lives = game.lives - 1
    if game.lives <= 0 then
      game.state = state.lose
    else
      -- 重置球和挡板
      game.ball = Ball:new(game.paddle.x + game.paddle.width / 2, 500, 8, 300)
    end
  end

  -- 检查胜利条件
  if #game.bricks == 0 then
    game.currentLevel = game.currentLevel + 1
    if game.currentLevel > game.totalLevels then
      game.state = state.win
    else
      loadLevel(game.currentLevel)
    end
  end
end

-- ============================================
-- love.draw — 每帧渲染
-- ============================================
function love.draw()
  love.graphics.clear(0.05, 0.05, 0.1)

  if game.state == state.menu then
    drawMenu()
  elseif game.state == state.playing then
    drawGame()
  elseif game.state == state.win then
    drawEnd("恭喜通关！", "最终分数: " .. game.score)
  elseif game.state == state.lose then
    drawEnd("游戏结束", "最终分数: " .. game.score)
  end
end

function drawMenu()
  love.graphics.setFont(love.graphics.newFont(36))
  love.graphics.printf("打砖块 Breakout", 0, 200, 800, "center")
  love.graphics.setFont(love.graphics.newFont(20))
  love.graphics.printf("使用左右方向键或 A/D 移动挡板", 0, 280, 800, "center")
  love.graphics.printf("按 Enter 开始游戏, Esc 退出", 0, 310, 800, "center")
end

function drawGame()
  -- 绘制砖块
  for _, brick in ipairs(game.bricks) do
    brick:draw()
  end

  -- 绘制挡板和球
  game.paddle:draw()
  game.ball:draw()

  -- 绘制 UI（分数和生命）
  love.graphics.setColor(1, 1, 1, 1)
  love.graphics.setFont(love.graphics.newFont(18))
  love.graphics.print("分数: " .. game.score, 10, 10)
  love.graphics.print("生命: " .. string.rep("♥ ", game.lives), 700, 10)
  love.graphics.print("关卡: " .. game.currentLevel, 350, 10)
end

function drawEnd(title, detail)
  love.graphics.setFont(love.graphics.newFont(48))
  love.graphics.setColor(1, 1, 0)
  love.graphics.printf(title, 0, 220, 800, "center")
  love.graphics.setFont(love.graphics.newFont(24))
  love.graphics.setColor(1, 1, 1)
  love.graphics.printf(detail, 0, 290, 800, "center")
  love.graphics.printf("按 Enter 重新开始, Esc 退出", 0, 340, 800, "center")
end

-- ============================================
-- 输入处理
-- ============================================
function love.keypressed(key)
  if key == "escape" then
    love.event.quit()
  elseif key == "return" or key == "enter" then
    if game.state == state.menu then
      game.state = state.playing
      game.lives = 3
      game.score = 0
      game.currentLevel = 1
      loadLevel(game.currentLevel)
    elseif game.state == state.win or game.state == state.lose then
      -- 重新开始
      game.state = state.playing
      game.lives = 3
      game.score = 0
      game.currentLevel = 1
      loadLevel(game.currentLevel)
    end
  end
end
```

---

## 第4节：Love2D 核心回调函数

| 回调 | 说明 |
|------|------|
| `love.load()` | 游戏启动时调用一次，用于初始化资源 |
| `love.update(dt)` | 每帧调用一次，`dt` = 帧间隔秒数，用于游戏逻辑 |
| `love.draw()` | 每帧调用一次（在 update 之后），用于渲染 |
| `love.keypressed(key)` | 键盘按下时触发 |
| `love.keyreleased(key)` | 键盘释放时触发 |
| `love.mousepressed(x, y, button)` | 鼠标按下时触发 |
| `love.mousereleased(x, y, button)` | 鼠标释放时触发 |
| `love.mousemoved(x, y, dx, dy)` | 鼠标移动时触发 |
| `love.resize(w, h)` | 窗口大小改变时触发 |
| `love.quit()` | 游戏退出前调用，用于清理资源 |

---

## 第5节：常用 API 速查

### 图形模块 `love.graphics`

```lua
-- 绘制形状
love.graphics.rectangle("fill", x, y, w, h)   -- 矩形
love.graphics.rectangle("line", x, y, w, h)   -- 线框矩形
love.graphics.circle("fill", x, y, r)          -- 圆
love.graphics.circle("line", x, y, r)          -- 线框圆
love.graphics.ellipse("fill", x, y, rx, ry)   -- 椭圆
love.graphics.line(x1, y1, x2, y2, ...)       -- 折线
love.graphics.polygon("fill", x1, y1, ...)    -- 多边形
love.graphics.arc("fill", x, y, r, a1, a2)    -- 弧/扇形

-- 颜色（0~1 范围）
love.graphics.setColor(1, 0, 0)                -- 红色
love.graphics.setColor(1, 1, 1, 0.5)          -- 半透明白色
love.graphics.setBackgroundColor(0.1, 0.1, 0.2) -- 背景色

-- 图像
local img = love.graphics.newImage("player.png")
love.graphics.draw(img, x, y, rotation, scaleX, scaleY, originX, originY)

-- 文字
local font = love.graphics.newFont("font.ttf", 24)
love.graphics.setFont(font)
love.graphics.print("Hello", 100, 100)         -- 单行
love.graphics.printf("多行文字", x, y, maxW, "center")  -- 多行，自动换行

-- 变换
love.graphics.push()       -- 保存图形状态
love.graphics.pop()        -- 恢复图形状态
love.graphics.translate(dx, dy)  -- 平移
love.graphics.rotate(angle)      -- 旋转（弧度）
love.graphics.scale(sx, sy)      -- 缩放

-- 其他
local w, h = love.graphics.getDimensions()
love.graphics.setBlendMode("add")  -- 加色混合（发光效果）
love.graphics.setLineWidth(2)      -- 线宽
```

### 音频模块 `love.audio`

```lua
-- 音效（短音效，完全加载到内存）
local shoot = love.audio.newSource("shoot.wav", "static")
shoot:play()

-- 音乐（长音频，流式播放）
local bgm = love.audio.newSource("bgm.ogg", "stream")
bgm:setLooping(true)
bgm:setVolume(0.5)
bgm:play()

-- 控制
bgm:pause()
bgm:stop()
```

### 键盘/鼠标模块

```lua
-- 键盘
love.keyboard.isDown("left")         -- 按键是否按住
love.keyboard.isScancodeDown("w")    -- 按物理键位检测（WSAD）

-- 鼠标
local mx, my = love.mouse.getPosition()  -- 鼠标位置
love.mouse.isDown(1)                     -- 左键是否按住
love.mouse.setVisible(false)             -- 隐藏光标
```

### 计时和数学

```lua
local elapsed = love.timer.getTime()  -- 游戏运行总秒数
love.timer.sleep(0.5)                 -- 暂停 0.5 秒

-- Love2D 中可直接使用 Lua 的 math 库
math.random()           -- 随机数
math.angle(x1, y1, x2, y2)  -- 两点间夹角
math.dist(x1, y1, x2, y2)   -- 两点间距离
```

---

## 第6节：常见游戏模式

### 粒子效果

```lua
-- main.lua
local ps

function love.load()
  local img = love.graphics.newImage("particle.png")
  ps = love.graphics.newParticleSystem(img, 1000)

  ps:setEmissionRate(100)       -- 每秒发射数量
  ps:setParticleLifetime(1, 2)  -- 粒子寿命范围
  ps:setSpeed(100, 200)         -- 速度范围
  ps:setSpread(math.pi / 4)     -- 扩散角度
  ps:setColors({1, 1, 0, 1}, {1, 0, 0, 0})  -- 从黄色渐变到红色透明
  ps:setSizes(1, 0.5)           -- 从完整到一半
end

function love.update(dt)
  ps:update(dt)
end

function love.draw()
  love.graphics.draw(ps, 400, 300)
end

function love.keypressed(key)
  if key == "space" then
    ps:emit(50)  -- 一次性发射 50 个粒子
  end
end
```

### 场景管理器

```lua
-- sceneManager.lua
local SceneManager = {
  scenes = {},
  current = nil,
}

function SceneManager:add(name, scene)
  self.scenes[name] = scene
end

function SceneManager:switch(name, ...)
  if self.current and self.scenes[self.current].exit then
    self.scenes[self.current].exit()
  end
  self.current = name
  if self.scenes[self.current].enter then
    self.scenes[self.current].enter(...)
  end
end

function SceneManager:update(dt)
  if self.current then
    self.scenes[self.current].update(dt)
  end
end

function SceneManager:draw()
  if self.current then
    self.scenes[self.current].draw()
  end
end

function SceneManager:keypressed(key)
  if self.current and self.scenes[self.current].keypressed then
    self.scenes[self.current].keypressed(key)
  end
end

return SceneManager

-- 使用：
-- local sceneManager = require("sceneManager")
-- sceneManager:add("menu", { enter = ..., update = ..., draw = ..., keypressed = ... })
-- sceneManager:add("game", ...)
-- sceneManager:switch("menu")
```

### 动画精灵表 (Sprite Sheet)

```lua
-- player.lua
local Player = {}
Player.__index = Player

function Player:new(imagePath, frameWidth, frameHeight)
  local obj = {
    x = 400, y = 300,
    image = love.graphics.newImage(imagePath),
    frameWidth = frameWidth,
    frameHeight = frameHeight,
    currentFrame = 1,
    totalFrames = 4,
    frameTime = 0,
    frameDuration = 0.1,  -- 每帧持续 0.1 秒
  }
  return setmetatable(obj, self)
end

function Player:update(dt)
  -- 动画计时器
  self.frameTime = self.frameTime + dt
  if self.frameTime >= self.frameDuration then
    self.frameTime = self.frameTime - self.frameDuration
    self.currentFrame = self.currentFrame % self.totalFrames + 1
  end
end

function Player:draw()
  local frameX = (self.currentFrame - 1) * self.frameWidth
  local quad = love.graphics.newQuad(
    frameX, 0,
    self.frameWidth, self.frameHeight,
    self.image:getDimensions()
  )
  love.graphics.draw(self.image, quad, self.x, self.y)
end

return Player
```

---

## 第7节：Love2D 开发工具

### 常用第三方库

| 库 | 用途 | 安装方式 |
|----|------|----------|
| `classic` | 轻量级 class 库 | 复制 `classic.lua` 到项目 |
| `bump.lua` | 碰撞检测 | `luarocks install bump` |
| `hump` | 游戏工具集（相机、计时器等） | 复制文件到项目 |
| `anim8` | 动画管理 | 复制 `anim8.lua` 到项目 |
| `sti` | Tiled 地图加载 | `luarocks install sti` |
| `push` | 分辨率管理 | 复制 `push.lua` 到项目 |

### Neovim 插件（love2d.nvim）

```lua
-- lua/plugins/love2d.lua
return {
  {
    "S1M0N38/love2d.nvim",
    cmd = "LoveRun",
    keys = {
      { "<leader>vl", "<cmd>LoveRun<cr>", desc = "运行 Love2D 项目" },
      { "<leader>vs", "<cmd>LoveStop<cr>", desc = "停止 Love2D" },
      { "<leader>vr", "<cmd>LoveRestart<cr>", desc = "重启 Love2D" },
    },
  },
}
```

---

## 第8节：Lua 技巧在 Love2D 中的应用

### 使用闭包创建按钮

```lua
function createButton(x, y, w, h, text, onClick)
  return {
    x = x, y = y, w = w, h = h,
    text = text,
    onClick = onClick,  -- 闭包捕获的回调函数
    draw = function(self)
      love.graphics.setColor(0.3, 0.3, 0.5)
      love.graphics.rectangle("fill", self.x, self.y, self.w, self.h)
      love.graphics.setColor(1, 1, 1)
      love.graphics.printf(self.text, self.x, self.y + 10, self.w, "center")
    end,
    checkClick = function(self, mx, my)
      if mx > self.x and mx < self.x + self.w
         and my > self.y and my < self.y + self.h then
        self.onClick()
      end
    end,
  }
end

-- 使用
local btn = createButton(300, 250, 200, 50, "开始游戏", function()
  print("游戏开始！")
end)
```

### 使用协程实现过场动画

```lua
function fadeTransition(fromScene, toScene)
  local alpha = 1
  while alpha > 0 do
    love.graphics.setColor(0, 0, 0, alpha)
    love.graphics.rectangle("fill", 0, 0, 800, 600)
    alpha = alpha - 0.02
    coroutine.yield()
  end
  fromScene.exit()
  toScene.enter()
  while alpha < 1 do
    love.graphics.setColor(0, 0, 0, alpha)
    love.graphics.rectangle("fill", 0, 0, 800, 600)
    alpha = alpha + 0.02
    coroutine.yield()
  end
end

-- 在 update 中驱动
local fadeCo = coroutine.create(function()
  fadeTransition(menuScene, gameScene)
end)
-- 每帧调用: coroutine.resume(fadeCo)
```

### 使用元表管理实例池

```lua
-- 对象池模式（减少 GC 压力）
local Pool = {}
Pool.__index = Pool

function Pool:new(factory, initialSize)
  local obj = { factory = factory, items = {} }
  for _ = 1, (initialSize or 10) do
    table.insert(obj.items, factory())
  end
  return setmetatable(obj, self)
end

function Pool:acquire()
  if #self.items > 0 then
    return table.remove(self.items)
  end
  return self.factory()  -- 池空了则创建
end

function Pool:release(item)
  table.insert(self.items, item)
end

return Pool

-- 使用：
-- local bulletPool = Pool:new(function() return { x = 0, y = 0, active = false } end, 50)
```

---

> 恭喜你完成了整个 Lua 教程！
>
> 现在你已经掌握了：
> - Lua 基础语法与进阶特性
> - 将 Lua 嵌入 C/C++ 项目
> - 使用 Lua 配置 Neovim
> - 使用 Lua + Love2D 开发游戏
>
> 继续练习，打造属于你自己的项目吧！
