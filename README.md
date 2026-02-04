# deepxiv-sdk

A Python SDK for accessing arXiv papers with CLI and MCP server support.

**🎮 Try the live demo:** [https://1stauthor.com/](https://1stauthor.com/)

**📚 API Documentation:** [https://data.rag.ac.cn/api/docs](https://data.rag.ac.cn/api/docs)

## Features

- 🔍 **Paper Search**: Search for arXiv papers using hybrid search (BM25 + Vector)
- 📄 **Paper Access**: Retrieve paper metadata, sections, and full content
- 💻 **CLI**: Command-line interface for quick access
- 🔌 **MCP Server**: Model Context Protocol server for Claude Desktop integration
- 🤖 **Intelligent Agent**: ReAct-based agent for intelligent paper analysis
- 🔌 **Flexible LLM Support**: Compatible with OpenAI, DeepSeek, OpenRouter, and other OpenAI-compatible APIs

## Installation

```bash
# Basic install (Reader + CLI)
pip install deepxiv-sdk

# With MCP server support
pip install deepxiv-sdk[mcp]

# With Agent support
pip install deepxiv-sdk[agent]

# Full install (all features)
pip install deepxiv-sdk[all]
```

## Quick Start

### CLI Usage

```bash
# Get paper preview
deepxiv paper 2409.05591 --preview

# Get specific section (case-insensitive)
deepxiv paper 2409.05591 --section introduction

# Search papers (requires token)
deepxiv search "agent memory" --limit 5 --token YOUR_TOKEN

# Start MCP server
deepxiv serve
```

### Python API

```python
from deepxiv_sdk import Reader

# Initialize the reader
reader = Reader(token="your_api_token")  # or Reader() for free papers

# Search for papers
results = reader.search("agent memory", size=10)
for paper in results['results']:
    print(f"{paper['title']} - {paper['arxiv_id']}")

# Get paper metadata
head = reader.head("2409.05591")
print(f"Title: {head['title']}")

# Read a section (case-insensitive)
intro = reader.section("2409.05591", "Introduction")
print(intro)

# Get full paper
content = reader.raw("2409.05591")
```

### Agent Usage

```python
import os
from deepxiv_sdk import Reader, Agent

reader = Reader(token="your_api_token")
agent = Agent(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4",
    reader=reader,
    print_process=True
)

answer = agent.query("What are the latest papers about agent memory?")
print(answer)
```

## MCP Server Setup

### For Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `search_papers` | Search arXiv with hybrid search |
| `get_paper_metadata` | Get paper metadata and section TLDRs |
| `get_paper_section` | Read a specific section |
| `get_full_paper` | Get complete paper content |
| `get_paper_preview` | Get preview (~10k chars) |

## API Token

- **Get API Token**: [https://data.rag.ac.cn/register](https://data.rag.ac.cn/register)
- **Daily Limit**: 1000 free requests per day
- **Test Papers**: `2409.05591` and `2504.21776` are available without authentication

Set token via environment variable or CLI option:

```bash
export DEEPXIV_TOKEN="your_token_here"
# or
deepxiv paper 2512.02556 --token "your_token_here"
```

## API Reference

### Reader Methods

- `search(query, size=10, search_mode="hybrid", ...)`: Search for papers
- `head(arxiv_id)`: Get paper metadata and structure
- `section(arxiv_id, section_name)`: Get a specific section (case-insensitive)
- `raw(arxiv_id)`: Get full paper in markdown
- `preview(arxiv_id)`: Get paper preview (~10k chars)
- `json(arxiv_id)`: Get complete structured JSON

### Agent Methods

- `query(question, reset_papers=False)`: Query the agent
- `get_loaded_papers()`: Get loaded papers info
- `reset_papers()`: Reset all loaded papers
- `add_paper(arxiv_id)`: Add a paper to context

## Examples

See the [examples](examples/) directory:

- `example_reader.py`: Basic Reader usage
- `example_agent.py`: Agent usage
- `example_advanced.py`: Advanced patterns
- `quickstart.py`: Quick start guide

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 🐛 **GitHub Issues**: [https://github.com/qhjqhj00/deepxiv_sdk/issues](https://github.com/qhjqhj00/deepxiv_sdk/issues)
- 📚 **API Documentation**: [https://data.rag.ac.cn/api/docs](https://data.rag.ac.cn/api/docs)
- 🎮 **Demo**: [https://1stauthor.com/](https://1stauthor.com/)
