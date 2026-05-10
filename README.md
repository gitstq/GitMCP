<p align="center">
  <img src="https://img.shields.io/badge/version-v1.0.0-blue.svg" alt="Version" />
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License" />
  <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python" />
  <img src="https://img.shields.io/badge/tests-38%20passed-brightgreen.svg" alt="Tests" />
  <img src="https://img.shields.io/badge/MCP-1.0-orange.svg" alt="MCP" />
</p>

<h1 align="center">🔧 GitMCP</h1>

<p align="center">
  <strong>Lightweight Git Repository MCP Server</strong><br/>
  将 Git 仓库操作暴露为标准 MCP 工具，让 AI Agent 直接操作 Git 仓库
</p>

<p align="center">
  <a href="#-项目介绍">项目介绍</a> •
  <a href="#-核心特性">核心特性</a> •
  <a href="#-快速开始">快速开始</a> •
  <a href="#-详细使用指南">使用指南</a> •
  <a href="#english">English</a> •
  <a href="#繁體中文">繁體中文</a>
</p>

---

<a id="简体中文"></a>

## 🎉 项目介绍

**GitMCP** 是一个轻量级的 Git 仓库 MCP（Model Context Protocol）服务器，它将完整的 Git 操作能力暴露为标准 MCP 工具，使任何支持 MCP 协议的 AI 客户端（如 Claude Desktop、Cursor、Windsurf 等）都能直接对 Git 仓库进行读写操作。

### 🎯 解决的痛点

- **AI Agent 无法直接操作 Git**：大多数 AI 编码助手只能通过终端命令间接操作 Git，缺乏结构化的工具接口
- **MCP 生态缺乏 Git 工具**：MCP 协议生态快速发展，但缺少高质量的 Git 操作服务器
- **多客户端兼容困难**：不同 AI 客户端的 Git 集成方式各异，需要统一的标准化方案

### ✨ 自研差异化亮点

- 🔒 **安全沙箱机制**：支持路径白名单限制，防止 AI Agent 访问未授权的目录
- 📦 **零依赖核心**：核心功能仅依赖 Python 标准库和 GitPython，无重量级框架
- 🛠️ **20+ 工具覆盖**：涵盖仓库信息、分支管理、暂存提交、文件读写、远程操作、Stash、标签等完整 Git 工作流
- 📊 **结构化输出**：所有工具返回 JSON 格式的结构化数据，便于 AI Agent 解析和处理
- 🚀 **双传输模式**：支持 stdio（本地客户端）和 SSE（远程服务）两种传输方式

---

## ✨ 核心特性

### 📋 仓库信息
| 工具 | 说明 |
|------|------|
| `git_status` | 获取仓库状态（分支、暂存/未暂存/未跟踪文件） |
| `git_log` | 查看提交历史（支持分页） |
| `git_branches` | 列出所有分支 |
| `git_tags` | 列出所有标签 |
| `git_remote_url` | 获取远程仓库 URL |

### 🌿 分支操作
| 工具 | 说明 |
|------|------|
| `git_create_branch` | 创建新分支 |
| `git_checkout` | 切换分支/标签/提交 |

### 📝 暂存与提交
| 工具 | 说明 |
|------|------|
| `git_add` | 暂存文件（支持指定文件或全部暂存） |
| `git_commit` | 创建提交 |

### 📂 文件操作
| 工具 | 说明 |
|------|------|
| `git_read_file` | 读取文件内容（支持指定 Git 引用） |
| `git_write_file` | 写入文件（自动创建目录） |
| `git_list_files` | 列出仓库文件（支持子目录和 Git 引用） |
| `git_file_info` | 获取文件状态信息 |
| `git_search_files` | 使用 git grep 搜索文件内容 |

### 🔄 变更与差异
| 工具 | 说明 |
|------|------|
| `git_diff` | 查看文件差异（支持已暂存和未暂存） |

### 🏗️ 仓库管理
| 工具 | 说明 |
|------|------|
| `git_init` | 初始化新仓库 |
| `git_clone` | 克隆远程仓库 |

### 🌐 远程操作
| 工具 | 说明 |
|------|------|
| `git_push` | 推送到远程仓库 |
| `git_pull` | 从远程仓库拉取 |

### 💾 Stash 操作
| 工具 | 说明 |
|------|------|
| `git_stash` | 暂存当前更改 |
| `git_stash_pop` | 恢复暂存的更改 |
| `git_stash_list` | 列出所有暂存条目 |

### 🏷️ 标签与历史
| 工具 | 说明 |
|------|------|
| `git_create_tag` | 创建标签（支持轻量标签和注释标签） |
| `git_revert` | 回退提交 |
| `git_reset` | 重置到指定提交 |

---

## 🚀 快速开始

### 📋 环境要求

- **Python** 3.10 或更高版本
- **Git** 2.0 或更高版本
- 支持 MCP 协议的 AI 客户端（Claude Desktop、Cursor 等）

### 📦 安装

```bash
# 从 PyPI 安装（推荐）
pip install gitmcp

# 或从源码安装
git clone https://github.com/gitstq/GitMCP.git
cd GitMCP
pip install -e .
```

### ⚙️ 配置 Claude Desktop

在 Claude Desktop 的配置文件中添加以下内容：

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "gitmcp": {
      "command": "gitmcp",
      "args": ["--allowed-paths", "/path/to/your/projects"]
    }
  }
}
```

> 💡 **安全提示**：使用 `--allowed-paths` 参数限制 AI 可访问的目录范围，防止越权操作。

### ⚙️ 配置 Cursor

在 Cursor 的 MCP 设置中添加：

```json
{
  "mcpServers": {
    "gitmcp": {
      "command": "gitmcp",
      "args": ["--allowed-paths", "/path/to/your/projects"]
    }
  }
}
```

### 🏃 启动服务

```bash
# stdio 模式（默认，适用于 Claude Desktop / Cursor）
gitmcp

# 限制可访问的目录
gitmcp --allowed-paths "/home/user/projects,/home/user/work"

# SSE 模式（适用于远程服务）
gitmcp --transport sse --host 0.0.0.0 --port 8765
```

---

## 📖 详细使用指南

### 🔍 典型工作流示例

在 AI 客户端中，你可以这样使用 GitMCP：

**1. 查看仓库状态**
> 请使用 git_status 查看当前仓库的状态，repo_path 为 "/home/user/my-project"

**2. 查看提交历史**
> 使用 git_log 查看最近 10 条提交记录

**3. 创建功能分支**
> 使用 git_create_branch 创建一个名为 "feature/login" 的分支

**4. 修改文件并提交**
> 先用 git_write_file 修改 src/main.py，然后用 git_add 暂存，最后用 git_commit 提交

**5. 查看差异**
> 使用 git_diff 查看当前未暂存的更改

### 🛡️ 安全配置

```bash
# 仅允许访问特定目录（推荐）
gitmcp --allowed-paths "/home/user/projects"

# 允许多个目录
gitmcp --allowed-paths "/home/user/projects,/home/user/work"

# 不限制路径（仅限受信任环境）
gitmcp
```

### 📊 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--allowed-paths` | 逗号分隔的允许路径列表 | 无限制 |
| `--transport` | 传输方式：`stdio` 或 `sse` | `stdio` |
| `--host` | SSE 模式的主机地址 | `localhost` |
| `--port` | SSE 模式的端口号 | `8765` |

---

## 💡 设计思路与迭代规划

### 🎨 设计理念

GitMCP 的设计遵循以下原则：

1. **安全性优先**：路径白名单、超时控制、错误隔离，确保 AI Agent 的操作不会影响系统安全
2. **结构化数据**：所有工具返回 JSON 格式数据，便于 AI Agent 解析和决策
3. **零配置启动**：安装即可使用，无需复杂配置
4. **渐进式暴露**：工具集覆盖完整 Git 工作流，但每个工具职责单一

### 🔧 技术选型

- **Python**：AI 生态最成熟的编程语言，MCP SDK 原生支持
- **FastMCP**：官方推荐的 MCP 服务器框架，轻量高效
- **GitPython**：最成熟的 Python Git 库，提供完整的 Git 操作能力

### 🗺️ 后续迭代计划

- [ ] **v1.1**：添加 `git_blame`、`git_cherry_pick`、`git_merge` 等高级操作
- [ ] **v1.2**：支持 GitHub/GitLab API 集成（Issue、PR 操作）
- [ ] **v1.3**：添加文件变更统计和代码行数分析
- [ ] **v2.0**：支持 Webhook 回调，实现 CI/CD 触发

---

## 📦 打包与部署指南

### 📥 从源码安装

```bash
git clone https://github.com/gitstq/GitMCP.git
cd GitMCP
pip install -e .
```

### 🧪 运行测试

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行全部测试
pytest tests/ -v

# 运行测试并生成覆盖率报告
pytest tests/ -v --cov=gitmcp --cov-report=html
```

### 🐍 兼容环境

| 环境 | 版本要求 |
|------|----------|
| Python | 3.10+ |
| Git | 2.0+ |
| 操作系统 | Linux / macOS / Windows |
| AI 客户端 | Claude Desktop / Cursor / Windsurf / 任何 MCP 兼容客户端 |

---

## 🤝 贡献指南

欢迎贡献代码！请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

### 📝 提交规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- `feat:` 新功能
- `fix:` 修复问题
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关

### 🐛 问题反馈

请通过 [GitHub Issues](https://github.com/gitstq/GitMCP/issues) 提交问题，包含以下信息：
- 操作系统和 Python 版本
- GitMCP 版本
- 复现步骤
- 期望行为与实际行为

---

## 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源。

---

<a id="繁體中文"></a>

## 🇹🇼 繁體中文

<p align="center">
  <strong>🔧 GitMCP - 輕量級 Git 倉庫 MCP 伺服器</strong><br/>
  將 Git 倉庫操作暴露為標準 MCP 工具，讓 AI Agent 直接操作 Git 倉庫
</p>

### 🎉 專案介紹

**GitMCP** 是一個輕量級的 Git 倉庫 MCP（Model Context Protocol）伺服器，它將完整的 Git 操作能力暴露為標準 MCP 工具，使任何支援 MCP 協議的 AI 客戶端（如 Claude Desktop、Cursor、Windsurf 等）都能直接對 Git 倉庫進行讀寫操作。

### ✨ 自研差異化亮點

- 🔒 **安全沙箱機制**：支援路徑白名單限制，防止 AI Agent 存取未授權的目錄
- 📦 **零依賴核心**：核心功能僅依賴 Python 標準庫和 GitPython，無重量級框架
- 🛠️ **20+ 工具覆蓋**：涵蓋倉庫資訊、分支管理、暫存提交、檔案讀寫、遠端操作、Stash、標籤等完整 Git 工作流
- 📊 **結構化輸出**：所有工具回傳 JSON 格式的結構化資料，便於 AI Agent 解析和處理
- 🚀 **雙傳輸模式**：支援 stdio（本地客戶端）和 SSE（遠端服務）兩種傳輸方式

### 🚀 快速開始

```bash
# 從 PyPI 安裝
pip install gitmcp

# 或從原始碼安裝
git clone https://github.com/gitstq/GitMCP.git
cd GitMCP
pip install -e .
```

### ⚙️ 配置 Claude Desktop

在 Claude Desktop 的設定檔中添加：

```json
{
  "mcpServers": {
    "gitmcp": {
      "command": "gitmcp",
      "args": ["--allowed-paths", "/path/to/your/projects"]
    }
  }
}
```

### ⚙️ 配置 Cursor

```json
{
  "mcpServers": {
    "gitmcp": {
      "command": "gitmcp",
      "args": ["--allowed-paths", "/path/to/your/projects"]
    }
  }
}
```

> 💡 **安全提示**：使用 `--allowed-paths` 參數限制 AI 可存取的目錄範圍，防止越權操作。

### 🏃 啟動服務

```bash
# stdio 模式（預設）
gitmcp

# 限制可存取的目錄
gitmcp --allowed-paths "/home/user/projects,/home/user/work"

# SSE 模式（遠端服務）
gitmcp --transport sse --host 0.0.0.0 --port 8765
```

### 🛠️ 工具清單

| 分類 | 工具 | 說明 |
|------|------|------|
| 📋 倉庫資訊 | `git_status` | 取得倉庫狀態 |
| | `git_log` | 檢視提交歷史 |
| | `git_branches` | 列出所有分支 |
| | `git_tags` | 列出所有標籤 |
| 🌿 分支操作 | `git_create_branch` | 建立新分支 |
| | `git_checkout` | 切換分支/標籤/提交 |
| 📝 暫存與提交 | `git_add` | 暫存檔案 |
| | `git_commit` | 建立提交 |
| 📂 檔案操作 | `git_read_file` | 讀取檔案內容 |
| | `git_write_file` | 寫入檔案 |
| | `git_list_files` | 列出倉庫檔案 |
| | `git_file_info` | 取得檔案狀態 |
| | `git_search_files` | 搜尋檔案內容 |
| 🌐 遠端操作 | `git_push` | 推送到遠端 |
| | `git_pull` | 從遠端拉取 |
| 💾 Stash | `git_stash` / `git_stash_pop` / `git_stash_list` | 暫存管理 |
| 🏷️ 標籤與歷史 | `git_create_tag` / `git_revert` / `git_reset` | 標籤與歷史操作 |

### 📦 部署指南

```bash
# 安裝開發依賴
pip install -e ".[dev]"

# 執行測試
pytest tests/ -v

# 產生覆蓋率報告
pytest tests/ -v --cov=gitmcp --cov-report=html
```

### 🤝 貢獻指南

歡迎貢獻程式碼！請參閱 [CONTRIBUTING.md](CONTRIBUTING.md)。

### 📄 開源協議

本專案基於 [MIT License](LICENSE) 開源。

---

<a id="english"></a>

## 🇬🇧 English

<p align="center">
  <strong>🔧 GitMCP - Lightweight Git Repository MCP Server</strong><br/>
  Expose Git operations as standard MCP tools for AI agents
</p>

### 🎉 Introduction

**GitMCP** is a lightweight Git repository MCP (Model Context Protocol) server that exposes comprehensive Git operations as standard MCP tools, enabling any MCP-compatible AI client (Claude Desktop, Cursor, Windsurf, etc.) to directly read from and write to Git repositories.

### 🎯 Problem Statement

- **AI agents can't directly operate Git**: Most AI coding assistants can only interact with Git indirectly through terminal commands, lacking structured tool interfaces
- **Missing Git tools in MCP ecosystem**: The MCP protocol ecosystem is growing rapidly, but high-quality Git operation servers are scarce
- **Multi-client compatibility challenges**: Different AI clients have varying Git integration approaches, requiring a unified standard solution

### ✨ Key Differentiators

- 🔒 **Security Sandbox**: Path whitelist restrictions to prevent AI agents from accessing unauthorized directories
- 📦 **Zero-Dependency Core**: Core functionality depends only on Python standard library and GitPython
- 🛠️ **20+ Tools**: Complete Git workflow coverage including repo info, branch management, staging, file I/O, remote ops, stash, and tags
- 📊 **Structured Output**: All tools return JSON-formatted structured data for easy AI agent parsing
- 🚀 **Dual Transport**: Support for both stdio (local clients) and SSE (remote services) transport modes

### 🚀 Quick Start

#### Prerequisites

- **Python** 3.10+
- **Git** 2.0+
- An MCP-compatible AI client (Claude Desktop, Cursor, etc.)

#### Installation

```bash
# Install from PyPI (recommended)
pip install gitmcp

# Or install from source
git clone https://github.com/gitstq/GitMCP.git
cd GitMCP
pip install -e .
```

#### Configure Claude Desktop

Add the following to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "gitmcp": {
      "command": "gitmcp",
      "args": ["--allowed-paths", "/path/to/your/projects"]
    }
  }
}
```

> 💡 **Security Tip**: Use `--allowed-paths` to restrict directories the AI can access.

#### Configure Cursor

```json
{
  "mcpServers": {
    "gitmcp": {
      "command": "gitmcp",
      "args": ["--allowed-paths", "/path/to/your/projects"]
    }
  }
}
```

#### Run the Server

```bash
# stdio mode (default, for Claude Desktop / Cursor)
gitmcp

# Restrict accessible directories
gitmcp --allowed-paths "/home/user/projects,/home/user/work"

# SSE mode (for remote services)
gitmcp --transport sse --host 0.0.0.0 --port 8765
```

### 🛠️ Available Tools

| Category | Tool | Description |
|----------|------|-------------|
| 📋 **Repository Info** | `git_status` | Get repository status |
| | `git_log` | View commit history (with pagination) |
| | `git_branches` | List all branches |
| | `git_tags` | List all tags |
| | `git_remote_url` | Get remote repository URL |
| 🌿 **Branch Ops** | `git_create_branch` | Create a new branch |
| | `git_checkout` | Switch branches/tags/commits |
| 📝 **Staging & Commit** | `git_add` | Stage files |
| | `git_commit` | Create commits |
| 📂 **File Ops** | `git_read_file` | Read file contents (supports Git refs) |
| | `git_write_file` | Write files (auto-creates directories) |
| | `git_list_files` | List repository files |
| | `git_file_info` | Get file status info |
| | `git_search_files` | Search file contents with git grep |
| 🔄 **Changes** | `git_diff` | View file differences |
| 🏗️ **Repo Management** | `git_init` | Initialize new repository |
| | `git_clone` | Clone remote repository |
| 🌐 **Remote Ops** | `git_push` | Push to remote |
| | `git_pull` | Pull from remote |
| 💾 **Stash** | `git_stash` / `git_stash_pop` / `git_stash_list` | Stash management |
| 🏷️ **Tags & History** | `git_create_tag` / `git_revert` / `git_reset` | Tag and history operations |

### 📖 Usage Example

In your AI client, you can use GitMCP like this:

**1. Check repository status**
> Use git_status to check the current repository state, repo_path is "/home/user/my-project"

**2. View commit history**
> Use git_log to view the last 10 commits

**3. Create a feature branch**
> Use git_create_branch to create a branch named "feature/login"

**4. Modify files and commit**
> First use git_write_file to modify src/main.py, then git_add to stage, and finally git_commit to commit

### 📦 Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Generate coverage report
pytest tests/ -v --cov=gitmcp --cov-report=html
```

### 🗺️ Roadmap

- [ ] **v1.1**: Add `git_blame`, `git_cherry_pick`, `git_merge` operations
- [ ] **v1.2**: GitHub/GitLab API integration (Issues, PRs)
- [ ] **v1.3**: File change statistics and line count analysis
- [ ] **v2.0**: Webhook callbacks for CI/CD triggering

### 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq">gitstq</a>
</p>
