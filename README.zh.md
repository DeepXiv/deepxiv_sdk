# deepxiv-sdk

**为 LLM 应用构建的高质量学术论文数据接口。** 提供混合搜索、智能摘要、分章节访问和内置推理代理。

- **📚 API 文档**: [https://data.rag.ac.cn/api/docs](https://data.rag.ac.cn/api/docs)
- **🎥 演示视频**: [![Watch Demo](https://img.shields.io/badge/YouTube-Watch%20Demo-red)](https://youtu.be/atr71CbQybM)
- **📄 技术报告**: [![arxiv](https://img.shields.io/badge/arXiv-2603.00084-b31b1b)](https://arxiv.org/abs/2603.00084)
- **📖 English Docs**: [README.md](README.md)

## 为什么选择 deepxiv？

| 特性 | deepxiv | 标准 arXiv API |
|------|---------|----------------|
| **混合搜索** (BM25 + 向量) | ✅ | ❌ |
| **AI 生成摘要** (TLDR) | ✅ | ❌ |
| **分章节访问** | ✅ | ❌ |
| **MCP 协议支持** | ✅ | ❌ |
| **内置推理代理** | ✅ | ❌ |
| **生物医学论文** (PMC) | ✅ | ❌ |
| **免费日请求数** | 10,000 | ∞* |

*arXiv API 无限制，但有严格的速率限制

## 核心特性

- 🔍 **混合搜索**: BM25 + 向量搜索，质量更好
- 📄 **分章节访问**: 只加载需要的内容，节省 tokens
- 📚 **PMC 支持**: 生物医学文献的完整访问
- 💻 **三层接口**: CLI / Python SDK / MCP Server
- 🤖 **内置代理**: ReAct 框架，支持多轮推理
- 🔌 **灵活的 LLM 支持**: 兼容 OpenAI、DeepSeek、OpenRouter 等
- ✨ **智能摘要**: AI 生成的论文摘要和关键词

## 🌐 开放获取文献支持

### 当前支持
- ✅ **arXiv** - 计算机科学、物理学、数学等领域
- ✅ **PubMed Central (PMC)** - 生物医学和生命科学文献

### 近期计划（路线图）
- 🔄 **bioRxiv** - 生物学预印本
- 🔄 **medRxiv** - 医学预印本
- 🔄 **其他 OA 来源** - 更多开放获取库
- 🔄 **全面 OA 文献覆盖** - 完整的开放获取生态系统

> **为什么是 OA 文献？** 通过专注于开放获取论文，deepxiv 确保研究人员和 AI 系统能够不受订阅限制地自由获取知识。

## 快速开始

### 1. 安装

```bash
# 基础安装 (Reader + CLI)
pip install deepxiv-sdk

# 完整安装 (MCP + Agent)
pip install deepxiv-sdk[all]
```

### 2. 首次使用

首次使用任何 CLI 命令时，deepxiv 会自动注册一个免费 token 并保存到 `~/.env`：

```bash
deepxiv search "agent memory" --limit 5
```

### 3. Python 使用

```python
from deepxiv_sdk import Reader

reader = Reader()

# 搜索论文
results = reader.search("agent memory", size=5)
for paper in results.get("results", []):
    print(f"{paper['title']} ({paper['arxiv_id']})")

# 获取论文信息
brief = reader.brief("2409.05591")
print(f"标题: {brief['title']}")
print(f"摘要: {brief.get('tldr', 'N/A')}")

# 读取特定章节
intro = reader.section("2409.05591", "Introduction")
print(intro[:500])
```

### 4. CLI 使用

```bash
# 搜索论文
deepxiv search "transformer" --limit 10

# 获取论文信息
deepxiv paper 2409.05591 --brief          # 快速概览
deepxiv paper 2409.05591 --head           # 元数据
deepxiv paper 2409.05591 --section intro  # 特定章节
deepxiv paper 2409.05591                  # 完整论文

# 获取 PMC 论文
deepxiv pmc PMC544940 --head

# 显示当前 token
deepxiv token
```

### 5. 在 Claude Desktop 中使用（MCP Server）

添加到 Claude Desktop MCP 配置文件：

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "deepxiv": {
      "command": "deepxiv",
      "args": ["serve"],
      "env": {
        "DEEPXIV_TOKEN": "your_token_here"
      }
    }
  }
}
```

### 6. Agent Skill（可选）

deepxiv 还提供了一个可重用的 **Agent Skill** 供 LLM 框架使用：

```bash
# 查看 skill 定义
cat skills/deepxiv-cli/SKILL.md

# 用于 Codex 或其他 agentic LLM 框架
# 复制或符号链接到你的 skills 目录：
mkdir -p $CODEX_HOME/skills
ln -s "$(pwd)/skills/deepxiv-cli" $CODEX_HOME/skills/deepxiv-cli
```

该 skill 教会代理何时使用：
- `deepxiv search` - 搜索论文
- `deepxiv paper` - 阅读论文
- `deepxiv pmc` - 访问生物医学文献
- `deepxiv agent` - 使用推理代理
- `deepxiv token` - 管理 token

对于不支持原生 skill 的框架，你可以将 [skills/deepxiv-cli/SKILL.md](skills/deepxiv-cli/SKILL.md) 作为系统提示或操作指南加载。

## 完整 API 参考

### 搜索和查询

```python
reader.search(query, size=10, search_mode="hybrid", categories=None, min_citation=None)
reader.head(arxiv_id)              # 论文元数据和章节概览
reader.brief(arxiv_id)             # 快速摘要 (标题、TLDR、关键词、引用数)
reader.section(arxiv_id, section)  # 读取特定章节
reader.raw(arxiv_id)               # 完整论文
reader.preview(arxiv_id)           # 论文预览 (~10k 字符)
reader.json(arxiv_id)              # 完整结构化 JSON
```

### PMC（生物医学论文）

```python
reader.pmc_head(pmc_id)            # PMC 论文元数据
reader.pmc_full(pmc_id)            # 完整 PMC 论文 JSON
```

### 代理（可选）

```python
from deepxiv_sdk import Agent

agent = Agent(api_key="your_openai_key", model="gpt-4")
answer = agent.query("最近关于 agent memory 的论文有哪些？")
print(answer)
```

## Token 管理

deepxiv 支持 4 种方式配置 token：

**1. 自动注册（推荐）** - 首次使用时自动创建并保存
```bash
deepxiv search "agent"
```

**2. 使用 config 命令**
```bash
deepxiv config --token YOUR_TOKEN
```

**3. 环境变量**
```bash
export DEEPXIV_TOKEN="your_token"
```

**4. 命令行参数**
```bash
deepxiv paper 2409.05591 --token YOUR_TOKEN
```

**提高日限额**: 默认 10,000 请求/天。需要更高限额，请发邮件到 `tommy@chien.io`，附上你的名字、邮箱和电话。

### 免费测试论文

这些论文无需 token 即可访问：

**arXiv**: `2409.05591`, `2504.21776`
**PMC**: `PMC544940`, `PMC514704`

## MCP 工具

使用 MCP Server 时可用的工具：

| 工具 | 说明 |
|------|------|
| `search_papers` | 搜索 arXiv 论文 |
| `get_paper_brief` | 快速摘要 |
| `get_paper_metadata` | 完整元数据 |
| `get_paper_section` | 读取特定章节 |
| `get_full_paper` | 完整论文 |
| `get_paper_preview` | 论文预览 |
| `get_pmc_metadata` | PMC 论文元数据 |
| `get_pmc_full` | 完整 PMC 论文 |

## 代理使用（可选）

内置的 ReAct 代理可以自动搜索论文、读取内容并执行多轮推理：

```python
from deepxiv_sdk import Agent

agent = Agent(
    api_key="your_deepseek_key",
    base_url="https://api.deepseek.com/v1",
    model="deepseek-chat"
)

answer = agent.query("比较 transformer 和 attention mechanism 的关键想法")
print(answer)
```

或通过 CLI：

```bash
deepxiv agent config  # 配置 LLM API
deepxiv agent query "最近关于 agent memory 的论文有哪些？" --verbose
```

## 错误处理

deepxiv 提供了具体的异常类型：

```python
from deepxiv_sdk import (
    Reader,
    AuthenticationError,  # 401 - 无效或过期的 token
    RateLimitError,       # 429 - 达到日限额
    NotFoundError,        # 404 - 论文未找到
    ServerError,          # 5xx - 服务器错误
    APIError              # 其他 API 错误
)

try:
    paper = reader.brief("2409.05591")
except AuthenticationError:
    print("请更新你的 token")
except RateLimitError:
    print("已达到日限额")
except NotFoundError:
    print("论文未找到")
except APIError as e:
    print(f"API 错误: {e}")
```

## 常见问题

**Q: 我需要 token 才能使用吗？**
A: 不需要。某些论文可以免费访问。搜索和某些内容需要 token，但会在首次使用时自动创建。

**Q: 最大搜索结果数是多少？**
A: 每次请求 100 个。使用 `offset` 参数进行分页。

**Q: 如何处理超时？**
A: Reader 会自动重试（最多 3 次）并进行指数退避。你可以自定义：
```python
reader = Reader(timeout=120, max_retries=5)
```

**Q: 我可以缓存论文内容吗？**
A: 可以。使用 reader 获取内容后，将其缓存到本地数据库或文件系统。

**Q: 代理支持哪些 LLM？**
A: 任何 OpenAI 兼容的 API（OpenAI、DeepSeek、OpenRouter、本地 Ollama 等）。

## 示例

查看 [examples/](examples/) 目录：

- `quickstart.py` - 5 分钟快速开始
- `example_reader.py` - 基础 Reader 使用
- `example_agent.py` - 代理使用
- `example_advanced.py` - 高级模式
- `example_error_handling.py` - 错误处理示例

## 许可证

MIT License - 查看 [LICENSE](LICENSE) 文件

## 支持

- 🐛 **GitHub Issues**: [https://github.com/qhjqhj00/deepxiv_sdk/issues](https://github.com/qhjqhj00/deepxiv_sdk/issues)
- 📚 **API 文档**: [https://data.rag.ac.cn/api/docs](https://data.rag.ac.cn/api/docs)
- 📧 **提高限额**: 发邮件到 `tommy@chien.io`，附上你的名字、邮箱和电话
