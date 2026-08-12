# Lua 在 Neovim 中的实战应用

Neovim 已将 Lua 作为一等公民，支持用 Lua 编写配置、插件、快捷键等。本章通过实战示例教你掌握 Neovim + Lua 开发。

---

## 第1节：Neovim Lua 基础

### 配置入口

Neovim 配置根目录默认为 `~/.config/nvim/`。

```
~/.config/nvim/
├── init.lua # 主入口
├── lua/ # Lua 模块目录
│ ├── options.lua # 编辑器选项
│ ├── keymaps.lua # 快捷键
│ ├── autocmds.lua # 自动命令
│ └── plugins/ # 插件配置
│ └── ...
└── after/ # 覆盖/延后加载配置
```

### 访问 Vim API

```lua
-- vim.api 提供了 Neovim 的所有 API
-- vim.fn 提供了 Vimscript 的几乎所有函数

-- 等价对照表:
-- Vimscript -> Lua
-- set number -> vim.opt.number = true
-- let g:foo = "bar" -> vim.g.foo = "bar"
-- call Xxx() -> vim.fn.Xxx()
-- nnoremap <leader>x <cmd>...<CR> -> vim.keymap.set("n", "<leader>x", ...)
```

---

## 第2节：编辑器基本设置

### init.lua 主入口

```lua
-- init.lua — Neovim 主配置文件

-- 加载子模块（推荐拆分配置）
require("options") -- 编辑器基本设置
require("keymaps") -- 快捷键
require("autocmds") -- 自动命令
require("plugins") -- 插件管理
```

### options.lua — 编辑器选项

```lua
-- options.lua

vim.opt.number = true -- 显示行号
vim.opt.relativenumber = true -- 相对行号
vim.opt.tabstop = 2 -- Tab 宽度
vim.opt.shiftwidth = 2 -- 缩进宽度
vim.opt.expandtab = true -- Tab 转为空格
vim.opt.smartindent = true -- 智能缩进
vim.opt.wrap = false -- 不自动换行
vim.opt.cursorline = true -- 高亮当前行
vim.opt.termguicolors = true -- 真彩色终端
vim.opt.mouse = "a" -- 启用鼠标
vim.opt.clipboard = "unnamedplus" -- 系统剪贴板
vim.opt.ignorecase = true -- 搜索忽略大小写
vim.opt.smartcase = true -- 有大写时区分大小写
vim.opt.signcolumn = "yes" -- 始终显示标记列
vim.opt.updatetime = 300 -- 更快写入交换文件
vim.opt.splitright = true -- 垂直分屏时新窗口在右侧
vim.opt.splitbelow = true -- 水平分屏时新窗口在下侧
vim.opt.scrolloff = 8 -- 光标上下保留的行数
vim.opt.swapfile = false -- 禁用 swap 文件
vim.opt.undofile = true -- 启用持久撤销
```

---

## 第3节：快捷键设定 (keymaps.lua)

```lua
-- keymaps.lua — 完整快捷键配置

local map = vim.keymap.set
local opts = { noremap = true, silent = true }

-- <leader> 默认是 \，这里改为空格
vim.g.mapleader = " "
vim.g.maplocalleader = " "

-- ============================================
-- 基础操作
-- ============================================

-- 保存和退出
map("n", "<leader>w", "<cmd>w<CR>", { desc = "保存文件" })
map("n", "<leader>q", "<cmd>q<CR>", { desc = "退出" })
map("n", "<leader>Q", "<cmd>q!<CR>", { desc = "强制退出" })
map("n", "<C-s>", "<cmd>w<CR>", { desc = "保存 (Ctrl+S)" })

-- 取消搜索高亮
map("n", "<Esc>", "<cmd>nohlsearch<CR>", opts)

-- ============================================
-- 窗口管理
-- ============================================

-- 分屏
map("n", "<leader>\\", "<cmd>vsplit<CR>", { desc = "垂直分屏" })
map("n", "<leader>-", "<cmd>split<CR>", { desc = "水平分屏" })

-- 窗口导航（Ctrl+hjkl）
map("n", "<C-h>", "<C-w>h", { desc = "跳到左侧窗口" })
map("n", "<C-j>", "<C-w>j", { desc = "跳到下方窗口" })
map("n", "<C-k>", "<C-w>k", { desc = "跳到上方窗口" })
map("n", "<C-l>", "<C-w>l", { desc = "跳到右侧窗口" })

-- 调整窗口大小
map("n", "<C-Up>", "<cmd>resize +2<CR>", { desc = "窗口增高" })
map("n", "<C-Down>", "<cmd>resize -2<CR>", { desc = "窗口降低" })
map("n", "<C-Left>", "<cmd>vertical resize -2<CR>", { desc = "窗口变窄" })
map("n", "<C-Right>", "<cmd>vertical resize +2<CR>", { desc = "窗口变宽" })

-- 关闭当前窗口
map("n", "<leader>c", "<cmd>close<CR>", { desc = "关闭窗口" })

-- ============================================
-- 终端集成
-- ============================================

-- 打开水平终端
map("n", "<leader>tt", function()
 vim.cmd("split | term")
 vim.cmd("resize 15")
end, { desc = "打开水平终端" })

-- 打开垂直终端
map("n", "<leader>tv", function()
 vim.cmd("vsplit | term")
 vim.cmd("vertical resize 80")
end, { desc = "打开垂直终端" })

-- 浮动终端（Toggle 式，按一次打开，再按关闭）
local float_term_id = nil
local float_term_buf = nil

map("n", "<leader>tf", function()
 if float_term_id and vim.api.nvim_win_is_valid(float_term_id) then
 vim.api.nvim_win_close(float_term_id, true)
 float_term_id = nil
 float_term_buf = nil
 return
 end

 local width = math.floor(vim.o.columns * 0.8)
 local height = math.floor(vim.o.lines * 0.8)
 local col = math.floor((vim.o.columns - width) / 2)
 local row = math.floor((vim.o.lines - height) / 2)

 float_term_buf = vim.api.nvim_create_buf(false, true)
 float_term_id = vim.api.nvim_open_win(float_term_buf, true, {
 relative = "editor",
 width = width,
 height = height,
 col = col,
 row = row,
 style = "minimal",
 border = "rounded",
 })

 vim.fn.termopen(vim.o.shell)
end, { desc = "切换浮动终端" })

-- 终端模式下按 Esc 或 jk 退出插入模式
map("t", "<Esc>", "<C-\\><C-n>", opts)
map("t", "jk", "<C-\\><C-n>", opts)

-- ============================================
-- 一键编译并在终端运行（核心功能）
-- ============================================

map("n", "<F5>", function()
 local ft = vim.bo.filetype
 local file = vim.fn.expand("%")
 local cmds = {
 python = "python3 " .. file,
 lua = "lua " .. file,
 sh = "bash " .. file,
 javascript = "node " .. file,
 typescript = "npx ts-node " .. file,
 c = "gcc " .. file .. " -o /tmp/a.out && /tmp/a.out",
 cpp = "g++ " .. file .. " -std=c++17 -o /tmp/a.out && /tmp/a.out",
 go = "go run " .. file,
 rust = "rustc " .. file .. " -o /tmp/a.out && /tmp/a.out",
 java = "javac " .. file .. " && java " .. vim.fn.expand("%:r"),
 }
 local cmd = cmds[ft]
 if not cmd then
 vim.notify("不支持的文件类型: " .. ft, vim.log.levels.WARN)
 return
 end

 vim.cmd("split | terminal " .. cmd)
 vim.cmd("resize 15")
end, { desc = "一键编译运行" })

-- <leader>r 增强版：异步运行，输出到通知
map("n", "<leader>rr", function()
 local ft = vim.bo.filetype
 local file = vim.fn.expand("%:p")
 local cmds = {
 lua = "lua " .. file,
 python = "python3 " .. file,
 javascript = "node " .. file,
 sh = "bash " .. file,
 c = "gcc " .. file .. " -o /tmp/a.out && /tmp/a.out",
 cpp = "g++ " .. file .. " -std=c++17 -o /tmp/a.out && /tmp/a.out",
 go = "go run " .. file,
 }
 local cmd = cmds[ft]
 if not cmd then
 vim.notify("不支持的文件类型: " .. ft, vim.log.levels.WARN)
 return
 end

 -- 异步执行，不阻塞编辑
 vim.fn.jobstart(cmd, {
 cwd = vim.fn.expand("%:p:h"),
 on_stdout = function(_, data)
 if data then
 for _, line in ipairs(data) do
 if line ~= "" then
 vim.schedule(function()
 vim.notify(line, vim.log.levels.INFO, { title = "输出" })
 end)
 end
 end
 end
 end,
 on_stderr = function(_, data)
 if data then
 for _, line in ipairs(data) do
 if line ~= "" then
 vim.schedule(function()
 vim.notify(line, vim.log.levels.ERROR, { title = "错误" })
 end)
 end
 end
 end
 end,
 })
end, { desc = "异步运行当前文件" })

-- 运行 Makefile
map("n", "<F6>", function()
 vim.cmd("w")
 vim.cmd("split | terminal make && echo '===== 编译成功 ====='")
 vim.cmd("resize 15")
end, { desc = "运行 make" })

-- ============================================
-- 文件操作
-- ============================================

-- 查找文件（需要 telescope 插件）
map("n", "<leader>ff", "<cmd>Telescope find_files<CR>", { desc = "查找文件" })
map("n", "<leader>fg", "<cmd>Telescope live_grep<CR>", { desc = "全文搜索" })
map("n", "<leader>fb", "<cmd>Telescope buffers<CR>", { desc = "缓冲区列表" })

-- Buffer 操作
map("n", "<Tab>", "<cmd>bnext<CR>", { desc = "下一个缓冲区" })
map("n", "<S-Tab>", "<cmd>bprevious<CR>", { desc = "上一个缓冲区" })
map("n", "<leader>bd", "<cmd>bdelete<CR>", { desc = "关闭缓冲区" })

-- ============================================
-- 代码操作（LSP）
-- ============================================

map("n", "gd", vim.lsp.buf.definition, { desc = "跳转到定义" })
map("n", "gr", vim.lsp.buf.references, { desc = "查找引用" })
map("n", "K", vim.lsp.buf.hover, { desc = "悬停文档" })
map("n", "<leader>rn", vim.lsp.buf.rename, { desc = "重命名符号" })
map("n", "<leader>ca", vim.lsp.buf.code_action, { desc = "代码操作" })
map("n", "<leader>fm", function()
 vim.lsp.buf.format({ async = true })
end, { desc = "格式化代码" })

-- 批量注释（Toggle）
map("v", "<leader>cc", function()
 local start = vim.fn.line("'<")
 local finish = vim.fn.line("'>")
 local lines = vim.api.nvim_buf_get_lines(0, start - 1, finish, false)
 local all_commented = true
 for _, line in ipairs(lines) do
 if not line:match("^%s*%-%-") then
 all_commented = false
 break
 end
 end

 if all_commented then
 vim.cmd("'<,'>s/^\\(\\s*\\)\\-\\- \\?/\\1/")
 else
 vim.cmd("'<,'>s/^/-- /")
 end
end, { desc = "切换注释" })

-- ============================================
-- 其他
-- ============================================

-- 移动选中行
map("v", "J", ":m '>+1<CR>gv=gv", { desc = "向下移动行" })
map("v", "K", ":m '<-2<CR>gv=gv", { desc = "向上移动行" })

-- 清除行尾空格
map("n", "<leader>sw", "<cmd>%s/\\s\\+$//e<CR>", { desc = "清除行尾空格" })

-- 粘贴不覆盖寄存器
map("x", "<leader>p", [["_dP]], { desc = "粘贴（不覆盖原有寄存器）" })
```

---

## 第4节：UI 美化设置

### 颜色主题

```lua
-- colorscheme.lua
local function set_colorscheme()
 local themes = { "catppuccin", "tokyonight", "onedark", "gruvbox", "rose-pine" }
 for _, theme in ipairs(themes) do
 local ok, _ = pcall(vim.cmd.colorscheme, theme)
 if ok then
 vim.notify("已加载主题: " .. theme, vim.log.levels.INFO)
 return
 end
 end
 vim.cmd.colorscheme("habamax") -- 回退
end
set_colorscheme()
```

### 状态栏 (lualine.nvim)

```lua
-- lua/plugins/ui.lua 中配置:
return {
 {
 "nvim-lualine/lualine.nvim",
 config = function()
 require("lualine").setup({
 options = {
 theme = "auto",
 component_separators = { left = "", right = "" },
 section_separators = { left = "", right = "" },
 disabled_filetypes = { "NvimTree", "alpha", "dashboard" },
 },
 sections = {
 lualine_a = { "mode" },
 lualine_b = { "branch", "diff", "diagnostics" },
 lualine_c = { { "filename", path = 1 } },
 lualine_x = { "encoding", "fileformat", "filetype" },
 lualine_y = { "progress" },
 lualine_z = { "location" },
 },
 })
 end,
 },
}
```

### Tab 标签栏 (bufferline.nvim)

```lua
return {
 {
 "akinsho/bufferline.nvim",
 config = function()
 require("bufferline").setup({
 options = {
 mode = "buffers",
 numbers = "ordinal",
 indicator = { style = "underline" },
 diagnostics = "nvim_lsp",
 offsets = {
 { filetype = "NvimTree", text = "文件树", padding = 1 },
 },
 },
 })
 end,
 },
}
```

### 启动画面 (alpha-nvim)

```lua
return {
 {
 "goolord/alpha-nvim",
 config = function()
 local alpha = require("alpha")
 local dashboard = require("alpha.themes.dashboard")
 dashboard.section.buttons.val = {
 dashboard.button("e", " 新建文件", "<cmd>ene<CR>"),
 dashboard.button("f", " 查找文件", "<cmd>Telescope find_files<CR>"),
 dashboard.button("r", " 最近文件", "<cmd>Telescope oldfiles<CR>"),
 dashboard.button("c", " 打开配置", "<cmd>e ~/.config/nvim/init.lua<CR>"),
 dashboard.button("q", " 退出", "<cmd>qa<CR>"),
 }
 alpha.setup(dashboard.opts)
 end,
 },
}
```

---

## 第5节：自动命令 (autocmds.lua)

```lua
-- autocmds.lua

local autocmd = vim.api.nvim_create_autocmd
local augroup = vim.api.nvim_create_augroup

-- === 通用增强 ===
local general = augroup("GeneralSettings", { clear = true })

-- 高亮复制后的内容
autocmd("TextYankPost", {
 group = general,
 callback = function()
 vim.highlight.on_yank({ higroup = "IncSearch", timeout = 200 })
 end,
})

-- === 语言特定设置 ===
local lang = augroup("LanguageSettings", { clear = true })

autocmd("FileType", {
 group = lang,
 pattern = { "lua", "python", "javascript", "typescript", "c", "cpp", "go", "rust" },
 callback = function()
 vim.opt_local.shiftwidth = 2
 vim.opt_local.tabstop = 2
 end,
})

autocmd("FileType", {
 group = lang,
 pattern = "markdown",
 callback = function()
 vim.opt_local.wrap = true
 vim.opt_local.spell = true
 end,
})

-- === 编译/运行自动命令 ===
autocmd("FileType", {
 group = lang,
 pattern = "c",
 callback = function()
 vim.bo.makeprg = "gcc % -o %< && ./%<"
 end,
})

autocmd("FileType", {
 group = lang,
 pattern = "cpp",
 callback = function()
 vim.bo.makeprg = "g++ % -std=c++17 -o %< && ./%<"
 end,
})

autocmd("FileType", {
 group = lang,
 pattern = "lua",
 callback = function()
 vim.bo.makeprg = "lua %"
 end,
})

-- === 终端打开时自动进入插入模式 ===
autocmd("TermOpen", {
 group = general,
 callback = function()
 vim.opt_local.number = false
 vim.opt_local.relativenumber = false
 vim.cmd("startinsert")
 end,
})
```

---

## 第6节：插件管理系统

### 使用 lazy.nvim 管理插件

lazy.nvim 是当前最流行的 Neovim 插件管理器。

#### 安装 lazy.nvim

```lua
-- bootstrap.lua
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.uv.fs_stat(lazypath) then
 vim.fn.system({
 "git",
 "clone",
 "--filter=blob:none",
 "https://github.com/folke/lazy.nvim.git",
 "--branch=stable",
 lazypath,
 })
end
vim.opt.rtp:prepend(lazypath)
```

#### 插件文件结构

```
~/.config/nvim/lua/plugins/
├── lsp.lua # LSP 配置
├── telescope.lua # 模糊搜索
├── treesitter.lua # 语法高亮
├── ui.lua # 主题和 UI
├── coding.lua # 编码辅助
├── editor.lua # 编辑器增强
└── lang.lua # 语言特定
```

#### plugins/lsp.lua — LSP 和自动补全

```lua
return {
 -- LSP 包管理器
 {
 "williamboman/mason.nvim",
 build = ":MasonUpdate",
 config = function()
 require("mason").setup()
 end,
 },
 {
 "williamboman/mason-lspconfig.nvim",
 config = function()
 require("mason-lspconfig").setup({
 ensure_installed = { "lua_ls", "pyright", "clangd", "tsserver" },
 })
 end,
 },

 -- LSP 配置
 {
 "neovim/nvim-lspconfig",
 config = function()
 local lspconfig = require("lspconfig")
 local capabilities = require("cmp_nvim_lsp").default_capabilities()

 lspconfig.lua_ls.setup({
 capabilities = capabilities,
 settings = {
 Lua = {
 runtime = { version = "Lua 5.4" },
 diagnostics = { globals = { "vim" } },
 workspace = { checkThirdParty = false },
 },
 },
 })
 lspconfig.clangd.setup({ capabilities = capabilities })
 lspconfig.pyright.setup({ capabilities = capabilities })
 lspconfig.tsserver.setup({ capabilities = capabilities })
 end,
 },

 -- 自动补全
 {
 "hrsh7th/nvim-cmp",
 dependencies = {
 "hrsh7th/cmp-nvim-lsp",
 "hrsh7th/cmp-buffer",
 "hrsh7th/cmp-path",
 "L3MON4D3/LuaSnip",
 },
 config = function()
 local cmp = require("cmp")
 cmp.setup({
 mapping = cmp.mapping.preset.insert({
 ["<C-Space>"] = cmp.mapping.complete(),
 ["<C-e>"] = cmp.mapping.abort(),
 ["<CR>"] = cmp.mapping.confirm({ select = true }),
 ["<Tab>"] = cmp.mapping.select_next_item(),
 ["<S-Tab>"] = cmp.mapping.select_prev_item(),
 }),
 sources = cmp.config.sources({
 { name = "nvim_lsp" },
 { name = "buffer" },
 { name = "path" },
 }),
 })
 end,
 },
}
```

#### plugins/telescope.lua — 模糊搜索

```lua
return {
 {
 "nvim-telescope/telescope.nvim",
 tag = "0.1.6",
 dependencies = { "nvim-lua/plenary.nvim" },
 config = function()
 require("telescope").setup({
 defaults = {
 layout_strategy = "horizontal",
 layout_config = { prompt_position = "top" },
 sorting_strategy = "ascending",
 file_ignore_patterns = { "node_modules", ".git/" },
 },
 })
 end,
 },
}
```

#### plugins/coding.lua — 编码辅助

```lua
return {
 -- 自动括号配对
 {
 "windwp/nvim-autopairs",
 event = "InsertEnter",
 config = true,
 },

 -- 注释工具
 {
 "numToStr/Comment.nvim",
 config = true,
 },

 -- Git 集成
 {
 "lewis6991/gitsigns.nvim",
 config = function()
 require("gitsigns").setup()
 end,
 },

 -- 缩进线
 {
 "lukas-reineke/indent-blankline.nvim",
 main = "ibl",
 config = function()
 require("ibl").setup()
 end,
 },
}
```

#### plugins/editor.lua — 编辑器增强

```lua
return {
 -- 文件树
 {
 "nvim-tree/nvim-tree.lua",
 config = function()
 require("nvim-tree").setup({
 view = { width = 30 },
 renderer = {
 icons = {
 glyphs = {
 folder = { arrow_open = "", arrow_closed = "" },
 },
 },
 },
 })
 end,
 keys = { { "<leader>e", "<cmd>NvimTreeToggle<CR>", desc = "文件树" } },
 },

 -- 状态栏
 {
 "nvim-lualine/lualine.nvim",
 config = function()
 require("lualine").setup({
 options = { theme = "auto" },
 })
 end,
 },

 -- Buffer 标签
 {
 "akinsho/bufferline.nvim",
 config = true,
 },
}
```

---

## 第7节：引入 GitHub 现成插件

### 方式1：直接引用 GitHub 仓库

```lua
-- plugins/community.lua
return {
 -- 高亮 TODO/FIXME 注释
 { "folke/todo-comments.nvim", dependencies = { "nvim-lua/plenary.nvim" }, opts = {} },

 -- 颜色主题
 { "catppuccin/nvim", name = "catppuccin", priority = 1000 },

 -- 快速跳转
 {
 "ggandor/leap.nvim",
 config = function()
 require("leap").add_default_mappings()
 end,
 },

 -- Markdown 预览
 {
 "iamcco/markdown-preview.nvim",
 cmd = { "MarkdownPreviewToggle", "MarkdownPreview", "MarkdownPreviewStop" },
 build = "cd app && npm install",
 ft = { "markdown" },
 },
}
```

### 方式2：从特定分支/标签安装

```lua
-- 从特定分支
{ "folke/noice.nvim", branch = "main", event = "VeryLazy", opts = {} }

-- 从特定标签
{ "nvim-telescope/telescope.nvim", tag = "0.1.6" }
```

### 方式3：引用本地开发中的插件

```lua
{
 dir = "~/projects/my-neovim-plugin",
 config = function()
 require("my-neovim-plugin").setup()
 end,
}
```

---

## 第8节：编写 Neovim 插件骨架

### 完整插件模块 `lua/mytools/init.lua`

```lua
-- lua/mytools/init.lua — 自定义工具插件

local M = {}

M.config = {
 auto_format_on_save = true,
 template_dir = vim.fn.stdpath("config") .. "/templates",
}

function M.setup(opts)
 M.config = vim.tbl_deep_extend("force", M.config, opts or {})

 -- 注册用户命令
 vim.api.nvim_create_user_command("MyTasks", function()
 M.show_tasks()
 end, {})

 -- 注册快捷键
 vim.keymap.set("n", "<leader>mt", M.show_tasks, { desc = "[MyTools] 任务列表" })
 vim.keymap.set("n", "<leader>mn", M.new_note, { desc = "[MyTools] 新建笔记" })

 -- 保存时自动格式化
 if M.config.auto_format_on_save then
 vim.api.nvim_create_autocmd("BufWritePre", {
 group = vim.api.nvim_create_augroup("MyTools", { clear = true }),
 pattern = { "*.lua", "*.py", "*.js", "*.ts" },
 callback = function()
 vim.lsp.buf.format({ async = false })
 end,
 })
 end
end

-- 显示待办任务
function M.show_tasks()
 local tasks = {
 "1. 完成 Lua 教程",
 "2. 优化 Neovim 配置",
 "3. 学习 C++ 模板",
 }

 local buf = vim.api.nvim_create_buf(false, true)
 vim.api.nvim_buf_set_lines(buf, 0, -1, false, tasks)
 vim.api.nvim_buf_set_option(buf, "modifiable", false)

 vim.api.nvim_open_win(buf, true, {
 relative = "cursor",
 width = 40,
 height = #tasks,
 row = 1,
 col = 0,
 border = "rounded",
 title = " 待办任务 ",
 title_pos = "center",
 })
end

-- 新建笔记
function M.new_note()
 local date = os.date("%Y-%m-%d")
 local filename = vim.fn.expand("~/notes/" .. date .. ".md")
 vim.cmd("edit " .. filename)

 local lines = {
 "# " .. date .. " 笔记本",
 "",
 "## 待办",
 "- [ ] ",
 "",
 "## 笔记",
 "",
 }
 vim.api.nvim_buf_set_lines(0, 0, -1, false, lines)
 vim.fn.cursor(4, 7)
end

return M
```

### 在 init.lua 中加载

```lua
require("mytools").setup({
 auto_format_on_save = false,
})
```

---

## 第9节：调试 Neovim Lua 代码

```lua
-- 1. print() 基本调试
vim.schedule(function()
 print("在事件循环中执行")
end)

-- 2. vim.notify 通知
vim.notify("Hello from Lua!", vim.log.levels.INFO)
vim.notify("Warning", vim.log.levels.WARN)
vim.notify("Error", vim.log.levels.ERROR)

-- 3. vim.inspect 打印表
local t = { a = 1, b = { c = 3 } }
print(vim.inspect(t)) -- { a = 1, b = { c = 3 } }

-- 4. 检查快捷键映射
vim.keymap.set("n", "<F2>", function()
 local key = vim.fn.input("检查快捷键: ")
 local map = vim.fn.maparg(key, "n", false, true)
 print(vim.inspect(map))
end, { desc = "检查快捷键" })

-- 5. 热重载配置（无需重启 Neovim）
vim.keymap.set("n", "<leader>R", function()
 dofile(vim.fn.stdpath("config") .. "/init.lua")
 vim.notify("配置已重新加载!", vim.log.levels.INFO)
end, { desc = "重载配置" })
```

---

> 下一步：[06-Love2D示例.md](./06-Love2D示例.md) — 使用 Lua 和 Love2D 引擎制作游戏

---

## 相关知识点

- [[../linux/README|Linux 教程]] — 终端编辑器生态与 Linux 环境配置
