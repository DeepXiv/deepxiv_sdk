# deepxiv-sdk

**DeepXiv is an agent-first paper search and progressive reading tool.**

> ⚠️ **Retrieval service is temporarily unavailable** due to high demand. We are expanding our capacity to better serve you.

Install it with `pip`, start using it immediately, and let the CLI auto-register an API token on first use. No extra setup is required before your first query.

- **📚 API Documentation**: [https://data.rag.ac.cn/api/docs](https://data.rag.ac.cn/api/docs)
- **🎥 Demo Video**: [![Watch Demo](https://img.shields.io/badge/YouTube-Watch%20Demo-red)](https://youtu.be/atr71CbQybM)
- **📄 Technical Report**: [![arxiv](https://img.shields.io/badge/arXiv-2603.00084-b31b1b)](https://arxiv.org/abs/2603.00084)
- **📖 中文文档**: [README.zh.md](README.zh.md)

---

> 🚀 **Live Demo**: I used vibe coding, based on deepxiv CLI, to build a [DeepResearch demo](https://demo.rag.ac.cn/) in 1 hour — feel free to try it out!
> A full-stack research platform is on the way. Stay tuned.

<p align="center">
  <img src="./assets/demo.gif" width="60%">
</p>

---

## What DeepXiv Does

DeepXiv is built around two core workflows that matter for agents:

1. **Search + Progressive Content Access**
2. **Trending + Popularity signals**

Instead of blindly loading full papers, DeepXiv lets agents read in layers, based on token budget and task value.

## Quick Start

```bash
pip install deepxiv-sdk
```

On first use, deepxiv automatically registers a free anonymous token (1,000 requests/day) and saves it to `~/.env`:

```bash
deepxiv search "agentic memory" --limit 5
```

If you want the full stack including MCP and the built-in research agent:

```bash
pip install "deepxiv-sdk[all]"
```

## CLI-First Workflow

The CLI is the primary interface. DeepXiv is designed so agents can work like researchers: search first, judge quickly, then read only the most valuable parts.

```bash
deepxiv search "agentic memory" --limit 5
deepxiv paper 2603.21489 --brief
deepxiv paper 2603.21489 --head
deepxiv paper 2603.21489 --section Analysis
```

Three commands matter most for progressive reading:

- `--brief`: decide whether a paper is worth deeper reading
- `--head`: inspect structure, sections, and token distribution
- `--section`: read only the most valuable parts such as `Introduction`, `Method`, or `Experiments`

This is the core DeepXiv idea: agents should not load full papers unless they truly need them.

## CLI Features

### 1. Paper Search and Reading

Basic usage:

```bash
deepxiv search "transformer" --limit 10
deepxiv paper 2409.05591 --brief
deepxiv paper 2409.05591 --head
deepxiv paper 2409.05591 --section Introduction
deepxiv paper 2409.05591
```

#### New search examples (2026-04)

The unified retrieve endpoint supports rich filtering and three sources in one
command. A few patterns worth knowing:

**Switch source with one flag**

```bash
deepxiv search "image generation on GenEval" --limit 5
deepxiv search "de novo protein design" --biorxiv --limit 5
deepxiv search "multimodal Alzheimer diagnosis" --medrxiv --limit 5
```

**Filter by authors, orgs, and categories (comma-separated lists)**

```bash
deepxiv search "image generation" \
  --authors "Shitao Xiao,Zheng Liu" \
  --orgs "Beijing Academy of Artificial Intelligence" \
  --categories cs.CV \
  --limit 5
```

> `--authors` and `--orgs` are filters *and* ranking signals. `--categories`
> is a pure filter.

**Convenience date filters (auto-mapped to the new date semantics)**

```bash
# Papers from June 2025 with at least 50 citations
deepxiv search "image generation outperforming SDXL" \
  --date-from 2025-06 --date-to 2025-06 \
  --min-citations 50 --limit 3

# Anything after a given date
deepxiv search "agentic memory" --date-from 2026-03-01 --limit 20
```

**Advanced date filter (`exact` / `after` / `before` / `between`)**

```bash
# exact month
deepxiv search "image generation" \
  --date-search-type exact --date-str 2025-06 --limit 5

# between (pass --date-str twice)
deepxiv search "image generation" \
  --date-search-type between \
  --date-str 2025-06-01 --date-str 2025-07-01 \
  --limit 5
```

**Pagination**

```bash
deepxiv search "LLM alignment" --limit 10 --offset 0
deepxiv search "LLM alignment" --limit 10 --offset 10
```

**Opt-in to fine reranking (off by default)**

```bash
# Default: fast recall, no rerank
deepxiv search "transformer model" --limit 10

# Enable upstream fine rerank when you need better ordering
deepxiv search "transformer model" --use-fine-rerank --limit 10
```

**JSON output for programmatic consumption**

```bash
deepxiv search "agentic memory" --limit 20 --format json
```

The JSON payload follows the new response shape
(`{status, total_count, result: [...]}`). See
[Search API changes (2026-04)](#search-api-changes-2026-04) for details.

#### Python equivalents

```python
from deepxiv_sdk import Reader
reader = Reader()

# Source + filters + advanced date
hits = reader.search(
    "image generation outperforming SDXL on GenEval",
    source="arxiv",
    size=5,
    categories=["cs.CV"],
    authors=["Shitao Xiao", "Zheng Liu"],
    orgs=["Beijing Academy of Artificial Intelligence"],
    min_citation=50,
    date_search_type="exact",
    date_str="2025-06",
)
for paper in hits["result"]:
    print(paper["arxiv_id"], paper["score"], paper["title"])

# Date range the shortcut way
reader.search("LLM alignment", date_from="2026-03-01", size=20)

# Switch source without a separate method
reader.search("de novo protein design", source="biorxiv", size=5)
reader.search("multimodal Alzheimer diagnosis", source="medrxiv", size=5)

# Opt-in to fine reranking
reader.search("transformer model", use_fine_rerank=True, size=10)
```

### 2. Trending and Popularity

Research is not only about what exists, but what is worth reading now.

```bash
deepxiv trending --days 7 --limit 30
deepxiv paper 2409.05591 --popularity
```

- `trending` finds the hottest recent papers from social signals
- `--popularity` gives paper-level propagation metrics such as views, tweets, likes, and replies

### 3. Web Search

```bash
deepxiv wsearch "karpathy"
deepxiv wsearch "karpathy" --json
```

Notes:
- `deepxiv wsearch` calls the DeepXiv web search endpoint
- each `wsearch` request costs **20 scores**, other requests cost **1 score**
- an auto-registered anonymous token gets **1,000 scores per day** (~50 web searches/day)
- a token registered at [data.rag.ac.cn/register](https://data.rag.ac.cn/register) gets **10,000 scores per day** (~500 web searches/day)

### 4. Semantic Scholar Metadata by ID

```bash
deepxiv sc 258001
deepxiv sc 258001 --json
```

`deepxiv sc` fetches metadata using a Semantic Scholar paper ID.

Notes:
- this is useful when your workflow already has Semantic Scholar IDs
- DeepXiv will **soon provide a Semantic Scholar search service** that returns Semantic Scholar IDs directly

### 5. Biomedical Papers

```bash
deepxiv pmc PMC544940 --head
deepxiv pmc PMC544940
```

### 6. bioRxiv & medRxiv Preprints

> ⚠️ **Beta**: bioRxiv and medRxiv support is currently in testing and optimization.
> To use it, install directly from source:
> ```bash
> pip install git+https://github.com/qhjqhj00/deepxiv_sdk.git
> ```

```bash
# Search (see "Paper Search and Reading" above for more patterns)
deepxiv search "protein design" --biorxiv --limit 5
deepxiv search "Alzheimer" --medrxiv --date-from 2024-01

# Fetch a paper by DOI
deepxiv biorxiv 10.1101/2021.02.26.433129
deepxiv biorxiv 10.1101/2021.02.26.433129 --format text
deepxiv biorxiv 10.1101/2021.02.26.433129 --section Introduction,Methods

deepxiv medrxiv 10.1101/2025.08.11.25333149
deepxiv medrxiv 10.1101/2025.08.11.25333149 --format text

# Also works via --biorxiv / --medrxiv flags on the paper command
deepxiv paper 10.1101/2021.02.26.433129 --biorxiv
deepxiv paper 10.1101/2021.02.26.433129 --biorxiv --section Introduction
```

## Example Agent Workflows

### Workflow 1: Review recent hot papers

```bash
deepxiv trending --days 7 --limit 30 --json
```

Then an agent can:

1. run `--brief` for each paper
2. run `--head` for the most promising ones
3. read only key sections
4. produce a report without manually opening dozens of papers

This workflow has already been written as a reusable skill. See [skills/deepxiv-trending-digest/SKILL.md](skills/deepxiv-trending-digest/SKILL.md).

### Workflow 2: Enter a new research topic

```bash
deepxiv search "agentic memory" --date-from 2026-03-01 --limit 100 --format json
```

Then an agent can:

1. batch-brief the results
2. prioritize papers with GitHub links
3. inspect experiments via `--head`
4. read `Experiments` / `Results`
5. turn datasets, metrics, and scores into a baseline table

This workflow is also available as a reusable skill. See [skills/deepxiv-baseline-table/SKILL.md](skills/deepxiv-baseline-table/SKILL.md).

## Built-in Deep Research Agent

If you do not want to compose the workflow manually, the CLI already includes a built-in research agent.

```bash
pip install "deepxiv-sdk[all]"
deepxiv agent config
deepxiv agent query "What are the latest papers about agent memory?" --verbose
```

If you already have your own agent stack, you can also just plug in the DeepXiv CLI skill and keep your own orchestration.

## Agent Integration

DeepXiv is designed to work well inside Codex, Claude Code, OpenClaw, and similar agent runtimes.

### MCP Server

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

### CLI Skill

```bash
mkdir -p $CODEX_HOME/skills
ln -s "$(pwd)/skills/deepxiv-cli" $CODEX_HOME/skills/deepxiv-cli
```

For frameworks without native skill support, load [skills/deepxiv-cli/SKILL.md](skills/deepxiv-cli/SKILL.md) as operating instructions.

## Python Usage

```python
from deepxiv_sdk import Reader

reader = Reader()

# Unified retrieve endpoint; arXiv by default.
results = reader.search("agent memory", size=5)
for paper in results["result"]:
    print(paper["arxiv_id"], paper["score"], paper["title"])

# Switch sources without a separate method.
bio_hits = reader.search("de novo protein design", source="biorxiv", size=5)
med_hits = reader.search("multimodal Alzheimer diagnosis", source="medrxiv", size=5)

brief = reader.brief("2409.05591")
head = reader.head("2409.05591")
intro = reader.section("2409.05591", "Introduction")

web = reader.websearch("karpathy")
sc_meta = reader.semantic_scholar("258001")
```

> **Upgrade note (2026-04)**: the unified retrieve endpoint replaced the old
> Elasticsearch-style interface. See
> [Search API changes](#search-api-changes-2026-04) below.

## Roadmap

DeepXiv is moving toward an **academic paper data interface at 100M+ scale**.

The roadmap is:

1. **Full arXiv coverage with T+1 automatic updates**
2. **anyXiv coverage**, including bioRxiv, medRxiv, and similar repositories
3. **Full open-access literature coverage**

The metadata backbone will increasingly rely on **Semantic Scholar metadata as the base layer**, while continuously expanding coverage and enrichment quality.

## Current Coverage

- ✅ **arXiv** - current primary source
- ✅ **PubMed Central (PMC)** - biomedical and life sciences
- 🧪 **bioRxiv / medRxiv** - biology & medicine preprints *(beta, install from source)*
- 🔄 **Semantic Scholar metadata integration** - expanding as the metadata foundation

> DeepXiv focuses on open-access literature so agents can work on unrestricted paper data instead of getting blocked by subscription barriers.

## Complete API Reference

### Search and Query

```python
reader.search(
    query,
    size=10,                  # mapped to upstream top_k (1~100)
    offset=0,                 # 0~10000
    source="arxiv",           # "arxiv" | "biorxiv" | "medrxiv"
    categories=None,          # list[str]; filter only
    authors=None,             # list[str]; also influences ranking
    orgs=None,                # list[str]; also influences ranking
    min_citation=None,
    date_from=None,           # convenience (mapped to date_search_type)
    date_to=None,             # convenience (mapped to date_search_type)
    date_search_type=None,    # advanced: "between"|"exact"|"after"|"before"
    date_str=None,            # advanced: str or [start, end]
    use_fine_rerank=False,    # SDK default: off
)
reader.websearch(query)            # Web search (20 limit per request)
reader.semantic_scholar(sc_id)     # Metadata lookup by Semantic Scholar ID
reader.head(arxiv_id)              # Paper metadata and sections overview
reader.brief(arxiv_id)             # Quick summary (title, TLDR, keywords, citations, GitHub URL)
reader.section(arxiv_id, section)  # Read specific section
reader.raw(arxiv_id)               # Full paper
reader.preview(arxiv_id)           # Paper preview (~10k characters)
reader.json(arxiv_id)              # Complete structured JSON
```

The search response shape now matches the upstream retrieve endpoint:

```jsonc
{
  "status": "success",
  "total_count": 3,
  "result": [
    {
      "arxiv_id": "2506.18871",    // biorxiv_id / medrxiv_id when source != arxiv
      "title": "...",
      "score": 0.9475,
      "abstract": "...",
      "tldr": "...",
      "authors": [{ "name": "...", "orgs": ["..."] }],
      "url": "...",
      "date": "2025-06-23T17:38:54Z",
      "citation_count": 217,
      "categories": ["cs.CV"]
    }
  ]
}
```

#### Search API changes (2026-04)

The search backend moved from Elasticsearch to the unified
`/arxiv/?type=retrieve` retrieval service. The SDK keeps parameter names where
possible, but a few behaviors changed — please review before upgrading:

| Parameter | Status | Notes |
|---|---|---|
| `size` | kept | Still works. Internally mapped to upstream `top_k`. You can also pass `top_k=` directly. |
| `offset` | kept | Now capped at `0~10000`. |
| `categories`, `authors`, `min_citation` | kept | Same semantics. |
| `source` | new | `"arxiv"` (default), `"biorxiv"`, `"medrxiv"`. Replaces the separate bioRxiv / medRxiv search endpoints. `reader.biomed_search()` is now a thin wrapper around `search(source=...)`. |
| `orgs` | new | Organization filter; also influences ranking. |
| `date_search_type` / `date_str` | new | Advanced date filter. Supports `between` / `exact` / `after` / `before`. |
| `date_from` / `date_to` | kept (mapped) | Automatically converted to `date_search_type` + `date_str`: both → `between`; only `date_from` → `after`; only `date_to` → `before`. Now also accepts `YYYY` / `YYYY-MM` (previously only `YYYY-MM-DD`). |
| `use_fine_rerank` | new | Upstream default is `True`; **the SDK defaults to `False`** so regular calls stay cheap. Set to `True` when you want better ordering. |
| `search_mode` / `bm25_weight` / `vector_weight` | **deprecated** | Accepted for backward compatibility but **ignored** (a warning is logged). Remove them from your code. |
| `search_funcs` | not exposed | The SDK always uses the full default index set (`metadata` + `section` + `roc`). |
| `return_contents` / `return_roc` | not exposed | Always disabled. Use `reader.raw()` / `reader.section()` / `reader.json()` to fetch content. |

Response-shape migration:

- `{total, took, results}` → `{status, total_count, result}`
- Per-item ID field depends on `source`: `arxiv_id` / `biorxiv_id` / `medrxiv_id`
- Old `paper["citation"]` → new `paper["citation_count"]`

CLI equivalents:

- `--limit` → maps to `size`/`top_k`
- `--offset`, `--authors`, `--orgs`, `--categories`, `--min-citations` — direct filters
- `--date-from` / `--date-to` — legacy convenience, auto-mapped
- `--date-search-type` / `--date-str` — advanced (use `--date-str` twice for `between`)
- `--use-fine-rerank` — opt-in flag
- `--biorxiv` / `--medrxiv` — switch `source`
- `--mode` — deprecated, no-op

### PMC (Biomedical Papers)

```python
reader.pmc_head(pmc_id)            # PMC paper metadata
reader.pmc_full(pmc_id)            # Complete PMC paper JSON
```

### bioRxiv / medRxiv *(beta)*

> Install from source to use these methods.

Preprint search now shares the unified retrieve endpoint with arXiv. Prefer
`reader.search(..., source="biorxiv" | "medrxiv")`; `biomed_search` remains as
a thin compatibility wrapper.

```python
# Recommended: unified search
reader.search("protein design", source="biorxiv", size=10)
reader.search("Alzheimer", source="medrxiv", size=10)

# Per-paper data access (DOI-based) is unchanged
reader.biomed_data(source_id, source="biorxiv")
reader.biomed_data(source_id, source="biorxiv", data_type="section", section_names=["Introduction"])
reader.biomed_data(source_id, source="medrxiv", data_type="roc", roc_num=5)

# Legacy (still supported)
reader.biomed_search(query, source="biorxiv", top_k=10)
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

**1. Auto-registration (Recommended)** - Automatically creates and saves on first use (1,000 requests/day)
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

**Daily limits by token type**:

| Token type | Daily limit | How to get |
|---|---|---|
| Auto-registered (anonymous) | 1,000 requests | Happens automatically on first CLI use |
| Registered token | 10,000 requests | Sign up at [data.rag.ac.cn/register](https://data.rag.ac.cn/register) |
| Custom / higher limit | Contact us | Email `tommy[at]chien.io` and describe your use case |

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
- 📧 **Higher Limits**: Register at [data.rag.ac.cn/register](https://data.rag.ac.cn/register) for 10,000 requests/day, or email `tommy[at]chien.io` to describe your use case for a custom limit
