# deepxiv-sdk

**High-quality academic paper data interface designed for LLM applications.** Provides hybrid search, intelligent summaries, section-by-section access, and built-in reasoning agents.

- **📚 API Documentation**: [https://data.rag.ac.cn/api/docs](https://data.rag.ac.cn/api/docs)
- **🎥 Demo Video**: [![Watch Demo](https://img.shields.io/badge/YouTube-Watch%20Demo-red)](https://youtu.be/atr71CbQybM)
- **📄 Technical Report**: [![arxiv](https://img.shields.io/badge/arXiv-2603.00084-b31b1b)](https://arxiv.org/abs/2603.00084)
- **📖 中文文档**: [README.zh.md](README.zh.md)

## Why Choose deepxiv?

| Feature | deepxiv | Standard arXiv API |
|---------|---------|-------------------|
| **Hybrid Search** (BM25 + Vector) | ✅ | ❌ |
| **AI-Generated Summaries** (TLDR) | ✅ | ❌ |
| **Section-by-Section Access** | ✅ | ❌ |
| **MCP Protocol Support** | ✅ | ❌ |
| **Built-in Reasoning Agent** | ✅ | ❌ |
| **Biomedical Papers** (PMC) | ✅ | ❌ |
| **Free Daily Requests** | 10,000 | ∞* |

*arXiv API has no limit, but strict rate limiting

## Core Features

- 🔍 **Hybrid Search**: BM25 + Vector search for better quality results
- 📄 **Section-Based Access**: Load only what you need, save tokens
- 📚 **PMC Support**: Full access to biomedical literature
- 💻 **Three-Layer Interface**: CLI / Python SDK / MCP Server
- 🤖 **Built-in Agent**: ReAct framework with multi-turn reasoning
- 🔌 **Flexible LLM Support**: Compatible with OpenAI, DeepSeek, OpenRouter, etc.
- ✨ **Smart Summaries**: AI-generated paper abstracts and keywords

## 🌐 Open Access Literature Support

### Current Support
- ✅ **arXiv** - Computer Science, Physics, Math, and more
- ✅ **PubMed Central (PMC)** - Biomedical and life sciences

### Coming Soon (Roadmap)
- 🔄 **bioRxiv** - Preprints in biology
- 🔄 **medRxiv** - Preprints in medicine
- 🔄 **Other OA Sources** - Additional open access repositories
- 🔄 **Full OA Literature Coverage** - Comprehensive open access ecosystem

> **Why OA Literature?** By focusing on open access papers, deepxiv ensures that researchers and AI systems have unrestricted access to knowledge without subscription barriers.

## Quick Start

### 1. Installation

```bash
# Basic install (Reader + CLI)
pip install deepxiv-sdk

# Full install (MCP + Agent)
pip install deepxiv-sdk[all]
```

### 2. First Use

On first use, deepxiv automatically registers a free token and saves it to `~/.env`:

```bash
deepxiv search "agent memory" --limit 5
```

### 3. Python Usage

```python
from deepxiv_sdk import Reader

reader = Reader()

# Search papers
results = reader.search("agent memory", size=5)
for paper in results.get("results", []):
    print(f"{paper['title']} ({paper['arxiv_id']})")

# Get paper info
brief = reader.brief("2409.05591")
print(f"Title: {brief['title']}")
print(f"TLDR: {brief.get('tldr', 'N/A')}")

# Read specific section
intro = reader.section("2409.05591", "Introduction")
print(intro[:500])
```

### 4. CLI Usage

```bash
# Search papers
deepxiv search "transformer" --limit 10

# Get paper info
deepxiv paper 2409.05591 --brief          # Quick overview
deepxiv paper 2409.05591 --head           # Metadata
deepxiv paper 2409.05591 --section intro  # Specific section
deepxiv paper 2409.05591                  # Full paper

# Get PMC papers
deepxiv pmc PMC544940 --head

# Show current token
deepxiv token
```

### 5. Use in Claude Desktop (MCP Server)

Add to Claude Desktop MCP config file:

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

### 6. Agent Skill (Optional)

deepxiv also provides a reusable **Agent Skill** for LLM frameworks:

```bash
# View the skill definition
cat skills/deepxiv-cli/SKILL.md

# Use with Codex or other agentic LLM frameworks
# Copy or symlink to your skills directory:
mkdir -p $CODEX_HOME/skills
ln -s "$(pwd)/skills/deepxiv-cli" $CODEX_HOME/skills/deepxiv-cli
```

The skill teaches agents when to use:
- `deepxiv search` - Find papers
- `deepxiv paper` - Read papers
- `deepxiv pmc` - Access biomedical literature
- `deepxiv agent` - Use the reasoning agent
- `deepxiv token` - Manage tokens

For frameworks without native skill support, you can load [skills/deepxiv-cli/SKILL.md](skills/deepxiv-cli/SKILL.md) as system prompts or operating instructions.

## Complete API Reference

### Search and Query

```python
reader.search(query, size=10, search_mode="hybrid", categories=None, min_citation=None)
reader.head(arxiv_id)              # Paper metadata and sections overview
reader.brief(arxiv_id)             # Quick summary (title, TLDR, keywords, citations)
reader.section(arxiv_id, section)  # Read specific section
reader.raw(arxiv_id)               # Full paper
reader.preview(arxiv_id)           # Paper preview (~10k characters)
reader.json(arxiv_id)              # Complete structured JSON
```

### PMC (Biomedical Papers)

```python
reader.pmc_head(pmc_id)            # PMC paper metadata
reader.pmc_full(pmc_id)            # Complete PMC paper JSON
```

### Agent (Optional)

```python
from deepxiv_sdk import Agent

agent = Agent(api_key="your_openai_key", model="gpt-4")
answer = agent.query("What are the latest papers about agent memory?")
print(answer)
```

## Token Management

deepxiv supports 4 ways to configure tokens:

**1. Auto-registration (Recommended)** - Automatically creates and saves on first use
```bash
deepxiv search "agent"
```

**2. Using config command**
```bash
deepxiv config --token YOUR_TOKEN
```

**3. Environment variable**
```bash
export DEEPXIV_TOKEN="your_token"
```

**4. Command-line option**
```bash
deepxiv paper 2409.05591 --token YOUR_TOKEN
```

**Increase daily limit**: Default is 10,000 requests/day. For higher limits, email your name, email, and phone to `tommy@chien.io`.

### Free Test Papers

These papers can be accessed without a token:

**arXiv**: `2409.05591`, `2504.21776`
**PMC**: `PMC544940`, `PMC514704`

## MCP Tools

Available tools when using MCP Server:

| Tool | Description |
|------|-------------|
| `search_papers` | Search arXiv papers |
| `get_paper_brief` | Quick summary |
| `get_paper_metadata` | Full metadata |
| `get_paper_section` | Read specific section |
| `get_full_paper` | Complete paper |
| `get_paper_preview` | Paper preview |
| `get_pmc_metadata` | PMC paper metadata |
| `get_pmc_full` | Complete PMC paper |

## Agent Usage (Optional)

The built-in ReAct agent can automatically search papers, read content, and perform multi-turn reasoning:

```python
from deepxiv_sdk import Agent

agent = Agent(
    api_key="your_deepseek_key",
    base_url="https://api.deepseek.com/v1",
    model="deepseek-chat"
)

answer = agent.query("Compare key ideas in transformers and attention mechanisms")
print(answer)
```

Or via CLI:

```bash
deepxiv agent config  # Configure LLM API
deepxiv agent query "What are the latest papers about agent memory?" --verbose
```

## Error Handling

deepxiv provides specific exception types:

```python
from deepxiv_sdk import (
    Reader,
    AuthenticationError,  # 401 - Invalid or expired token
    RateLimitError,       # 429 - Daily limit reached
    NotFoundError,        # 404 - Paper not found
    ServerError,          # 5xx - Server error
    APIError              # Other API errors
)

try:
    paper = reader.brief("2409.05591")
except AuthenticationError:
    print("Please update your token")
except RateLimitError:
    print("Daily limit reached")
except NotFoundError:
    print("Paper not found")
except APIError as e:
    print(f"API error: {e}")
```

## Troubleshooting

**Q: Do I need a token to use?**
A: No. Some papers are free to access. Search and some content require a token, but it's auto-created on first use.

**Q: What's the maximum search results?**
A: 100 per request. Use `offset` parameter for pagination.

**Q: How to handle timeouts?**
A: Reader automatically retries (max 3 times) with exponential backoff. You can customize:
```python
reader = Reader(timeout=120, max_retries=5)
```

**Q: Can I cache paper content?**
A: Yes. After getting content with reader, cache locally to database or file system.

**Q: Which LLMs does the agent support?**
A: Any OpenAI-compatible API (OpenAI, DeepSeek, OpenRouter, local Ollama, etc.).

## Examples

See [examples/](examples/) directory:

- `quickstart.py` - 5-minute quick start
- `example_reader.py` - Basic Reader usage
- `example_agent.py` - Agent usage
- `example_advanced.py` - Advanced patterns
- `example_error_handling.py` - Error handling examples

## License

MIT License - see [LICENSE](LICENSE) file

## Support

- 🐛 **GitHub Issues**: [https://github.com/qhjqhj00/deepxiv_sdk/issues](https://github.com/qhjqhj00/deepxiv_sdk/issues)
- 📚 **API Documentation**: [https://data.rag.ac.cn/api/docs](https://data.rag.ac.cn/api/docs)
- 📧 **Higher Limits**: Email with your name, email, and phone to `tommy@chien.io`
