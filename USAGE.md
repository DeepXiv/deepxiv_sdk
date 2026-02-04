# deepxiv Usage Guide

**Note:** Some papers require an API token, others are publicly accessible. Use `2409.05591` (MemoRAG paper) for testing - it works without authentication.

## Setting API Token

```bash
# Option 1: Environment variable (recommended)
export DEEPXIV_TOKEN="your_token_here"

# Option 2: Pass directly to command
deepxiv paper 2512.02556 --token "your_token_here"
deepxiv search "agent" --token "your_token_here"
```

## Installation

```bash
cd /Users/zhengliu/workspace/arxiv_mcp/deepxiv

# Basic install (Reader + CLI)
pip install -e .

# With MCP server support
pip install -e ".[mcp]"

# With Agent support
pip install -e ".[agent]"

# Full install (all features)
pip install -e ".[all]"
```

---

## CLI Usage

### 1. Check version and help

```bash
deepxiv --version
deepxiv --help
deepxiv search --help
deepxiv paper --help
deepxiv serve --help
```

### 2. Get paper preview

```bash
# Use 2409.05591 - this paper is publicly accessible
deepxiv paper 2409.05591 --preview
```

### 3. Get paper in markdown format

```bash
deepxiv paper 2409.05591
```

### 4. Get specific section

```bash
deepxiv paper 2409.05591 --section Introduction
```

### 5. Get paper as JSON

```bash
deepxiv paper 2409.05591 --format json
```

### 6. Search papers (requires API token)

```bash
deepxiv search "agent memory" --limit 5
deepxiv search "transformer" --mode bm25 --format json
deepxiv search "LLM" --categories cs.AI,cs.CL --min-citations 10
```

### 7. Start MCP server

```bash
deepxiv serve
```

---

## Python API Usage

### 1. Basic Reader usage

```python
from deepxiv import Reader

reader = Reader()

# Get paper preview
preview = reader.preview("2409.05591")
print(preview.get("content", "")[:500])

# Get paper metadata
head = reader.head("2409.05591")
print(f"Title: {head['title']}")
print(f"Abstract: {head['abstract'][:200]}")

# Get specific section
intro = reader.section("2409.05591", "Introduction")
print(intro[:500])

# Get full paper
content = reader.raw("2409.05591")
print(f"Full paper length: {len(content)} chars")
```

### 2. Search papers (requires token)

```python
from deepxiv import Reader

reader = Reader(token="your_api_token")

results = reader.search("agent memory", size=5)
for paper in results.get("results", []):
    print(f"{paper['title']} (arXiv:{paper['arxiv_id']})")
```

### 3. Agent usage (requires OpenAI API key)

```python
import os
from deepxiv import Reader, Agent

reader = Reader()
agent = Agent(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4",
    reader=reader,
    print_process=True
)

answer = agent.query("Summarize paper 2409.05591")
print(answer)
```

---

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

---

## Run Examples

```bash
cd /Users/zhengliu/workspace/arxiv_mcp/deepxiv

# Basic reader example
python examples/example_reader.py

# Agent example (requires OPENAI_API_KEY)
python examples/example_agent.py

# Advanced examples
python examples/example_advanced.py

# Quick start
python examples/quickstart.py
```

---

## Project Structure

```
deepxiv/
├── deepxiv/
│   ├── __init__.py       # Package init
│   ├── reader.py         # Core API client
│   ├── cli.py            # Click CLI
│   ├── mcp_server.py     # FastMCP server
│   └── agent/            # ReAct agent
├── examples/             # Usage examples
├── pyproject.toml        # Package config
└── README.md             # Documentation
```
