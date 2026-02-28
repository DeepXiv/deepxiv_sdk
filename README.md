# deepxiv-sdk

A Python SDK for accessing arXiv papers with CLI and MCP server support.

**🎮 Try the live demo:** [https://1stauthor.com/](https://1stauthor.com/)

**📚 API Documentation:** [https://data.rag.ac.cn/api/docs](https://data.rag.ac.cn/api/docs)

## Features

- 🔍 **Paper Search**: Search for arXiv papers using hybrid search (BM25 + Vector)
- 📄 **Paper Access**: Retrieve paper metadata, sections, and full content
- 🏥 **PMC Support**: Access PubMed Central biomedical literature
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

# With Agent support (includes OpenAI SDK)
pip install deepxiv-sdk[agent]

# Full install (all features)
pip install deepxiv-sdk[all]
```

**Note:** Agent requires `openai>=1.0.0` for LLM calls. Install with `[agent]` or `[all]` extras.

## Quick Start

### Step 1: Get Your Free API Token

Visit [https://data.rag.ac.cn/register](https://data.rag.ac.cn/register) to get your free API token (10000 requests/day).

### Step 2: Configure Your Token

```bash
# Interactive configuration (saves to ~/.env)
deepxiv config

# Or provide token directly
deepxiv config --token YOUR_TOKEN

# The CLI will automatically load token from ~/.env
```

### CLI Usage

```bash
# Show help
deepxiv help

# Get paper in different formats
deepxiv paper 2409.05591                    # Full markdown
deepxiv paper 2409.05591 --head             # Metadata (JSON)
deepxiv paper 2409.05591 --brief            # Brief info (title, TLDR, keywords)
deepxiv paper 2409.05591 --raw              # Raw markdown
deepxiv paper 2409.05591 --preview          # Preview (~10k chars)
deepxiv paper 2409.05591 --section intro    # Specific section

# Search papers
deepxiv search "agent memory" --limit 5
deepxiv search "transformer" --mode bm25 --format json
deepxiv search "LLM" --categories cs.AI,cs.CL --min-citations 100

# Get PMC papers
deepxiv pmc PMC544940                       # Full JSON
deepxiv pmc PMC544940 --head                # Metadata only
deepxiv pmc PMC514704                       # Another example

# Intelligent Agent (requires agent installation)
deepxiv agent config                        # Configure LLM API first
deepxiv agent query "What are the latest papers about agent memory?"
# show reasoning process
deepxiv agent query 'What are the key ideas in the MemGPT paper?' --max-turn 5 --verbose

# Start MCP server
deepxiv serve
```

**Agent Configuration:**
- Config is saved to `~/.deepxiv_agent_config.json`
- Supports environment variables: `DEEPXIV_AGENT_API_KEY`, `DEEPXIV_AGENT_BASE_URL`, `DEEPXIV_AGENT_MODEL`
- Compatible with OpenAI, DeepSeek, OpenRouter, and other OpenAI-compatible APIs

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

# Get brief info (quick summary)
brief = reader.brief("2409.05591")
print(f"Title: {brief['title']}")
print(f"TLDR: {brief.get('tldr', 'N/A')}")
print(f"Citations: {brief.get('citations', 0)}")

# Read a section (case-insensitive)
intro = reader.section("2409.05591", "Introduction")
print(intro)

# Get full paper
content = reader.raw("2409.05591")

# Access PMC papers
pmc_head = reader.pmc_head("PMC544940")
print(f"PMC Title: {pmc_head['title']}")

pmc_full = reader.pmc_json("PMC544940")
print(f"PMC Content: {len(str(pmc_full))} chars")
```

### Agent Usage

The intelligent agent can search papers, read content, and answer questions using ReAct reasoning.




#### Python API

```python
import os
from deepxiv_sdk import Reader, Agent

reader = Reader(token="your_api_token")
agent = Agent(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4",
    reader=reader,
    max_llm_calls=20,  # Maximum reasoning turns
    print_process=True  # Show reasoning steps
)

answer = agent.query("What are the latest papers about agent memory?")
print(answer)

# For DeepSeek or other APIs
agent = Agent(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    model="deepseek-chat",
    reader=reader
)
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
| `get_paper_brief` | Get brief info (title, TLDR, keywords, citations) |
| `get_paper_metadata` | Get paper metadata and section TLDRs |
| `get_paper_section` | Read a specific section |
| `get_full_paper` | Get complete paper content |
| `get_paper_preview` | Get preview (~10k chars) |
| `get_pmc_metadata` | Get PMC paper metadata |
| `get_pmc_full` | Get complete PMC paper in JSON |

## API Token

- **Get Your Free Token**: [https://data.rag.ac.cn/register](https://data.rag.ac.cn/register)
- **Daily Limit**: 1000 free requests per day
- **Test Papers**: 
  - arXiv: `2409.05591` and `2504.21776` are available without authentication
  - PMC: `PMC544940` and `PMC514704` are available without authentication

### Token Configuration (3 Ways)

**1. Using `config` command (Recommended)**
```bash
deepxiv config
# Saves to ~/.env and automatically loads on every command
```

**2. Environment Variable**
```bash
export DEEPXIV_TOKEN="your_token_here"
# Add to ~/.bashrc or ~/.zshrc for persistence
```

**3. Command-line Option**
```bash
deepxiv paper 2512.02556 --token "your_token_here"
# Useful for one-time usage or multiple tokens
```

The CLI automatically loads tokens from:
1. Command-line `--token` option (highest priority)
2. `DEEPXIV_TOKEN` environment variable
3. `.env` file in current directory
4. `~/.env` file in home directory (lowest priority)

## API Reference

### Reader Methods

#### arXiv Methods
- `search(query, size=10, search_mode="hybrid", ...)`: Search for papers
- `head(arxiv_id)`: Get paper metadata and structure
- `brief(arxiv_id)`: Get brief info (title, TLDR, keywords, citations)
- `section(arxiv_id, section_name)`: Get a specific section (case-insensitive)
- `raw(arxiv_id)`: Get full paper in markdown
- `preview(arxiv_id)`: Get paper preview (~10k chars)
- `json(arxiv_id)`: Get complete structured JSON
- `markdown(arxiv_id)`: Get HTML view URL

#### PMC Methods
- `pmc_head(pmc_id)`: Get PMC paper metadata
- `pmc_json(pmc_id)`: Get complete PMC paper in JSON

### Agent Methods

- `query(question, reset_papers=False)`: Query the agent with a question
- `get_loaded_papers()`: Get information about loaded papers
- `reset_papers()`: Clear all loaded papers from context
- `add_paper(arxiv_id)`: Manually add a paper to context

### Agent Tools

The agent has access to the following tools:

| Tool | Description |
|------|-------------|
| `search_papers` | Search arXiv papers with filters |
| `load_paper` | Load paper metadata and structure |
| `read_section` | Read a specific section |
| `get_full_paper` | Get complete paper content |
| `get_paper_preview` | Get paper preview (~10k chars) |
| `quick_preview` | Batch preview multiple papers (brief info only) |

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
