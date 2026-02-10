# deepxiv-sdk Usage Guide

**Note:** Some papers require an API token, others are publicly accessible.

**Free test papers:**
- arXiv: `2409.05591` and `2504.21776` 
- PMC: `PMC544940` and `PMC514704`

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
# Basic install (Reader + CLI)
pip install deepxiv-sdk

# With MCP server support
pip install deepxiv-sdk[mcp]

# With Agent support
pip install deepxiv-sdk[agent]

# Full install (all features)
pip install deepxiv-sdk[all]
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

### 2. Get brief paper info

```bash
# Get quick summary with title, TLDR, keywords, citations
deepxiv paper 2409.05591 --brief
```

### 3. Get paper preview

```bash
# Use 2409.05591 - this paper is publicly accessible
deepxiv paper 2409.05591 --preview
```

### 4. Get paper in markdown format

```bash
deepxiv paper 2409.05591
```

### 5. Get specific section

```bash
deepxiv paper 2409.05591 --section Introduction
```

### 6. Get paper as JSON

```bash
deepxiv paper 2409.05591 --format json
```

### 7. Search papers (requires API token)

```bash
deepxiv search "agent memory" --limit 5
deepxiv search "transformer" --mode bm25 --format json
deepxiv search "LLM" --categories cs.AI,cs.CL --min-citations 10
```

### 8. Get PMC papers

```bash
# Get PMC paper metadata
deepxiv pmc PMC544940 --head

# Get full PMC paper (JSON)
deepxiv pmc PMC544940
deepxiv pmc PMC514704
```

### 9. Start MCP server

```bash
deepxiv serve
```

---

## Python API Usage

### 1. Basic Reader usage

```python
from deepxiv_sdk import Reader

reader = Reader()

# Get brief info (quick summary)
brief = reader.brief("2409.05591")
print(f"Title: {brief['title']}")
print(f"TLDR: {brief.get('tldr', 'N/A')}")
print(f"Citations: {brief.get('citations', 0)}")

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

### 2. Access PMC papers

```python
from deepxiv_sdk import Reader

reader = Reader()

# Get PMC paper metadata
pmc_head = reader.pmc_head("PMC544940")
print(f"PMC Title: {pmc_head['title']}")
print(f"DOI: {pmc_head.get('doi', 'N/A')}")
print(f"Abstract: {pmc_head.get('abstract', '')[:200]}")

# Get full PMC paper
pmc_full = reader.pmc_json("PMC544940")
print(f"PMC Full content: {len(str(pmc_full))} chars")
```

### 3. Search papers (requires token)

```python
from deepxiv_sdk import Reader

reader = Reader(token="your_api_token")

results = reader.search("agent memory", size=5)
for paper in results.get("results", []):
    print(f"{paper['title']} (arXiv:{paper['arxiv_id']})")
```

### 4. Agent usage (requires OpenAI API key)

```python
import os
from deepxiv_sdk import Reader, Agent

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
| `get_paper_brief` | Get brief info (title, TLDR, keywords, citations) |
| `get_paper_metadata` | Get paper metadata and section TLDRs |
| `get_paper_section` | Read a specific section |
| `get_full_paper` | Get complete paper content |
| `get_paper_preview` | Get preview (~10k chars) |
| `get_pmc_metadata` | Get PMC paper metadata |
| `get_pmc_full` | Get complete PMC paper in JSON |

---

## Project Structure

```
deepxiv-sdk/
├── deepxiv_sdk/
│   ├── __init__.py       # Package init
│   ├── reader.py         # Core API client
│   ├── cli.py            # Click CLI
│   ├── mcp_server.py     # FastMCP server
│   └── agent/            # ReAct agent
├── examples/             # Usage examples
├── pyproject.toml        # Package config
└── README.md             # Documentation
```
