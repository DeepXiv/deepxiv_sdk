# Usage Guide

The complete reference for both surfaces. For the short version see [README.md](README.md).

> **中文版**: [USAGE.zh.md](USAGE.zh.md)

**Contents** — [Install](#install) · [Tokens and limits](#tokens-and-limits) · **CLI**: [ask](#cli-agentic-search-deepxiv-ask) · [search](#cli-search) · [paper](#cli-reading-papers) · [talent](#cli-talent--scholar-profiles) · [other sources](#other-sources) · [agent integration](#agent-integration) · **Python**: [agentic search](#agentic-search) · [Reader methods](#reader-methods) · [error handling](#error-handling-and-retry) · [batching](#batch-processing) · [research agent](#agent-for-complex-analysis) · [troubleshooting](#troubleshooting)

## Install

```bash
pip install deepxiv-sdk              # Reader + CLI
pip install "deepxiv-sdk[all]"       # + built-in research agent (needs your own LLM key)
pip install git+https://github.com/DeepXiv/deepxiv_sdk.git   # 1.1.0b1, adds `deepxiv talent` (beta)
```

```python
from deepxiv_sdk import Reader

reader = Reader(token="...")                              # required for anything beyond free papers
reader = Reader(token="...", timeout=60, max_retries=3)   # tune transport too

# `Reader` does not read DEEPXIV_TOKEN itself — only the CLI does. Pass it in:
import os
reader = Reader(token=os.environ["DEEPXIV_TOKEN"])
```

## Tokens and limits

deepxiv resolves the token from `--token`, then `DEEPXIV_TOKEN`, then `~/.env`. On first use it auto-registers one.

| | Daily limit | Agentic + talent calls | How to get |
|---|---|---|---|
| Auto-registered | 1,000 requests | ❌ not eligible | Automatic on first CLI use |
| Registered | 10,000 requests | ✅ 300/day | [data.rag.ac.cn/register](https://data.rag.ac.cn/register) |
| Custom | Contact us | Contact us | Email `tommy[at]chien.io` |

The two pools are independent: agentic calls don't consume your general limit, and vice versa. Lost your key? Recover it at [data.rag.ac.cn/token-lookup](https://data.rag.ac.cn/token-lookup).

Free test papers (no token) — arXiv: `2409.05591`, `2504.21776`; PMC: `PMC544940`.

### Coverage

| Source | Status |
|---|---|
| arXiv | ✅ full text, T+1 sync |
| Web | ✅ Google + cached page bodies |
| PubMed Central | ✅ biomedical & life sciences |
| bioRxiv / medRxiv | ✅ biology & medicine preprints |

DeepXiv focuses on open-access literature so agents work on unrestricted data instead of hitting subscription walls.

---

# CLI reference

## CLI: agentic search (`deepxiv ask`)

Two backends, same shape. A question goes in; the service picks its own tools, reads sources when it needs to, and streams back an answer with citations.

```bash
deepxiv ask "what speedup does speculative decoding report on HumanEval"
deepxiv ask "Anthropic Claude API pricing tiers" --web
```

| | Backend | Answers with | Best for |
|---|---|---|---|
| **`deepxiv ask`** | Local full-text arXiv corpus (Qdrant hybrid retrieval + paper bodies) | `[arXiv:2512.15176]` — real IDs | Methods, numbers, experimental results |
| **`deepxiv ask --web`** | Google + cached page bodies | Markdown links to real URLs | Current events, products, pricing, anything non-academic |

Neither is a wrapper around a web search box. The arXiv side reads actual paper sections; the web side reads cached page bodies.

**Registered accounts only.** Agentic search needs a key from [data.rag.ac.cn/register](https://data.rag.ac.cn/register); the auto-registered token returns `403`.

### Effort levels

| `--effort` | Gather rounds | First token (arXiv) | First token (web) |
|---|---|---|---|
| `default` *(default)* | 1–2 | **3–4s** | 5–9s |
| `high` | 3 | 7–8s | ≈13s |
| `xhigh` | 4–5 | 9–13s | longer |

Rounds are a ceiling, not a floor — the service converges early once it has enough evidence. Web is slower because Google cache misses cost 1.7–4.3s and aren't under our control.

### Writing queries that work

This is worth more than any flag.

- **Be specific.** The service assumes your query is already refined. `"what compression ratio does KV cache eviction report on LongBench"` beats `"kv cache"` by a wide margin.
- **Ask for numbers if you want numbers.** Saying "what speedup" or "which benchmark" pushes the service to read source text instead of skimming abstracts and snippets.
- **Chinese works directly.** arXiv queries are rewritten to English technical terms for retrieval; web switches to a Chinese locale. The answer comes back in your query's language.
- **Put arXiv scope limits in the query text** — year, venue (NeurIPS/ICLR/CVPR), category (cs.CL), author, institution, minimum citations. They become retrieval filters.
- **If results miss, rephrase.** Raising `--effort` only adds reading rounds; it can't redirect the first-round recall.

### Flags

```bash
deepxiv ask "reward hacking in RLHF" --verbose          # tool calls + quota on stderr
deepxiv ask "state space models vs transformers" --json # one JSON object
deepxiv ask "MoE routing collapse" --no-stream          # wait for the full answer
deepxiv ask "diffusion samplers" --all-sources          # every retrieved source

deepxiv ask "NeurIPS 2025 best paper" --web --search-type news
deepxiv ask "retrieval evaluation methodology" --web --search-type scholar
```

`--top-k N` (1–30, arXiv only) sets first-round retrieval size. `--search-type` / `--gl` / `--hl` are web-only. `--max-answer-tokens N` (256–16384) caps answer length; `--language LANG` overrides the answer language.

### Three things to know about the results

> **Citations are real.** The service is instructed never to invent an arXiv ID or URL, and says "no relevant papers" rather than fabricating one. `[arXiv:2512.15176]` maps directly to `https://arxiv.org/abs/2512.15176`.

> **Sources are the retrieval set, not the citation list.** A 10-paper retrieval often supports a single citation. The CLI shows only cited sources by default; `--all-sources` shows the rest.

> **Web evidence has two strengths.** The service reads only *cached* page bodies and never fetches live, so an uncached page contributes just its search snippet. Chinese sites and news pages are cached less often. The CLI marks pages read in full (📄) versus snippet-only (🔗), and the answer flags snippet-only claims. Weigh them accordingly.

Also: when the answer hits `--max-answer-tokens`, the CLI warns and the API sets `answer_truncated`. Don't treat a truncated answer as complete.

## CLI: reading papers

Read papers in layers so an agent doesn't load 50k tokens to answer a question about the method section.

```bash
deepxiv search "agentic memory" --limit 5     # 1. find candidates
deepxiv paper 2409.05591 --brief              # 2. is it worth reading?
deepxiv paper 2409.05591 --head               # 3. structure & token distribution
deepxiv paper 2409.05591 --section Method     # 4. read only what matters
```

- `--brief` — title, TLDR, keywords, citations, GitHub URL
- `--head` — sections overview and token distribution
- `--section NAME` — one section (`Introduction`, `Method`, `Experiments`, …)
- `--preview` / `--raw` / *(no flag)* — ≈10k-char preview / full markdown / full paper
- `--popularity` — social impact metrics for one paper

## CLI: search

```bash
deepxiv search "transformer" --limit 10 --format json

# Filter by author, org, category (comma-separated)
deepxiv search "image generation" --authors "Shitao Xiao" --categories cs.CV --limit 5

# Filter by venue (repeatable; NeurIPS ↔ NIPS aliases match automatically)
deepxiv search "diffusion model" --venue NeurIPS --venue-year 2025 --limit 5

# Filter by date and citations (dates accept YYYY, YYYY-MM, YYYY-MM-DD)
deepxiv search "diffusion models" --date-from 2024-01 --min-citations 50

# Advanced date modes: exact / after / before / between
deepxiv search "image generation" \
  --date-search-type between --date-str 2025-06-01 --date-str 2025-07-01

# Pagination and opt-in fine reranking
deepxiv search "LLM alignment" --limit 10 --offset 10
deepxiv search "transformer model" --use-fine-rerank
```

`--authors` and `--orgs` are filters *and* ranking signals; `--categories` is a pure filter. Filters combine with `AND`, so stacking a narrow date window on a high citation floor can legitimately return 0 results — loosen one.

Returns `{status, total_count, result: [...]}`. Each result carries `arxiv_id`, `title`, `abstract`, `tldr`, `authors`, `categories`, `citation_count`, `date`, `github_url`, `score`, and `venue`/`venue_year` when known.

## CLI: talent — scholar profiles

> **Beta.** Ships in `1.1.0b1`, source install only. The scholar index is still being built out, so coverage is uneven — expect thin profiles outside the areas that have been crawled.

Search people instead of papers: who works on a topic, where they are, and what their record looks like.

```bash
# Semantic search over the scholar index (takes a full sentence)
deepxiv talent search "young faculty working on retrieval-augmented generation" --semantic --limit 5

# Keyword mode matches names and affiliations
deepxiv talent search "窦志成"

# Filter by tag, career stage, and sort key
deepxiv talent search --tags 大语言模型,Agent --career-stage student --sort total_citations

# Full profile for one scholar (IDs come from search)
deepxiv talent survey 257
deepxiv talent survey 257 --format markdown    # the generated report
deepxiv talent survey 257 --no-refresh         # read-only, skip the Scholar refresh
```

`search` options: `--semantic`, `--tags T1,T2` (OR-ed), `--career-stage student|junior|senior`, `--investigated profile|deep|any|scholar`, `--sort h_index|total_citations|last_paper_at|updated_at|created_at`, `--order desc|asc`, `--limit`, `--offset`, `--json`.

`survey` options: `--format text|json|markdown`, `--refresh` / `--no-refresh`.

Search returns `{persons, total, semantic, quota, cached}`; survey returns `{person, papers, scholar, quota}` with education, work history, links, open source, and publication metrics. Profiles older than ~14 days refresh from Google Scholar automatically on `survey`; `--no-refresh` reads without triggering that.

Both commands spend one unit from the same agentic quota pool as `deepxiv ask`, so they need a registered key.

## Other sources

```bash
deepxiv trending --days 7 --limit 30       # hottest recent papers (social signals)
deepxiv paper 2409.05591 --popularity      # per-paper views, tweets, likes

deepxiv pmc PMC544940 --head               # PubMed Central

deepxiv search "protein design" --biorxiv --limit 5     # bioRxiv / medRxiv
deepxiv biorxiv 10.1101/2021.02.26.433129 --format text
deepxiv medrxiv 10.1101/2020.03.24.20042937 --section Methods
```

## Agent integration

### CLI skill

```bash
mkdir -p $CODEX_HOME/skills
ln -s "$(pwd)/skills/deepxiv-cli" $CODEX_HOME/skills/deepxiv-cli
```

For frameworks without native skill support, load [skills/deepxiv-cli/SKILL.md](skills/deepxiv-cli/SKILL.md) as operating instructions. Two worked workflows also ship as skills: [trending digest](skills/deepxiv-trending-digest/SKILL.md) and [baseline table](skills/deepxiv-baseline-table/SKILL.md).

### Built-in research agent

Runs the search → read → reason loop locally with your own LLM key — useful when you want to control the model or the loop. Install with `pip install "deepxiv-sdk[all]"`; works with any OpenAI-compatible API. The Python API is under [Agent for complex analysis](#agent-for-complex-analysis).

```bash
deepxiv agent config
deepxiv agent query "What are the latest papers about agent memory?" --verbose
```

### Rolling your own MCP server

deepxiv ships no MCP server — the CLI and `Reader` are the integration surface, and wrapping them takes about twenty lines. What's worth copying is not the plumbing but the guidance below: an agent given a bare `ask(query)` tool will use this API poorly.

```python
from mcp.server.mcpserver import MCPServer   # mcp>=2.0; it was FastMCP in 1.x
from deepxiv_sdk import Reader, agent_search_sources

mcp = MCPServer("deepxiv")
reader = Reader()

@mcp.tool()
def ask_arxiv(query: str, effort: str = "default") -> str:
    """Answer a research question, citing real arXiv IDs.

    Use for methods, numbers, and experimental results from papers. For current
    events, products, or anything non-academic, use ask_web.

    Be specific — "what compression ratio does KV cache eviction report on
    LongBench" works; "kv cache" does not. Ask for numbers explicitly ("what
    speedup", "which benchmark") to make it read paper bodies rather than
    abstracts. Put scope (year, venue, category, author) in the query text.
    Chinese works directly. If the answer misses, rephrase — raising effort adds
    reading rounds but cannot redirect first-round recall.

    effort: "default" (fastest), "high" (comparing papers), "xhigh" (surveys).
    """
    result = reader.agent_search(query, source="arxiv", effort=effort)
    answer = result["answer"]
    # `sources` is the retrieval set, a superset of what the answer cites.
    cited = [p for p in agent_search_sources(result) if p["arxiv_id"] in answer]
    lines = [answer]
    if cited:
        lines += ["\n---\nCited papers:"] + [
            f"- [{p['arxiv_id']}] {p['title']}" for p in cited
        ]
    if result["stats"]["answer_truncated"]:
        lines.append("\n⚠️ Truncated — do not treat as complete.")
    return "\n".join(lines)

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

Four things to put in your tool descriptions, or the agent will misuse the results:

1. **Citations are real** — the service never invents an ID, and says "no relevant papers" instead. Tell the agent to preserve them in what it reports back.
2. **`sources` is the retrieval set, not the citation list** — filter to IDs that appear in the answer, as above, or the agent will present unrelated papers as evidence.
3. **On the web backend, evidence has two strengths** — pages with `read: true` were read in full; the rest contributed only a search snippet. Surface that distinction so the agent can qualify weaker claims.
4. **`answer_truncated` means incomplete** — say so explicitly, otherwise the agent will summarise a cut-off answer as if it were whole.

For a `web` tool, swap `source="web"`, add `search_type` (`search` / `scholar` / `news` / `images`), and match on `page["url"] in answer` instead of `arxiv_id`.

---

# Python SDK

## Agentic search

```python
from deepxiv_sdk import Reader

reader = Reader(token=os.environ["DEEPXIV_TOKEN"])  # agentic search needs a registered key

# Blocking — simplest, waits 8~30s for the whole answer
result = reader.agent_search("what speedup does DEER report on HumanEval")
print(result["answer"])
print(result["quota"]["remaining"], "agentic calls left today")

# Web backend
result = reader.agent_search("Claude API pricing", source="web", search_type="news")
```

Streaming — first token in ≈3–4s on arXiv at `effort="default"`:

```python
from deepxiv_sdk import agent_search_sources

chunks, sources, truncated = [], [], False
for event in reader.agent_search_stream("test-time compute scaling laws"):
    name = event["event"]
    if name == "answer_delta":
        chunks.append(event["text"])
        print(event["text"], end="", flush=True)
    elif name == "sources":
        sources = agent_search_sources(event)   # normalises papers/pages
    elif name == "done":
        truncated = event["answer_truncated"]
    elif name == "error":
        raise RuntimeError(f"{event['stage']}: {event['message']}")
answer = "".join(chunks)
```

Events always sent: `billing` (carries `tier` / `used` / `remaining`), `start`, `answer_start`, `answer_delta` (or `answer` when `stream_answer=False`), `sources`, `done`. Pass `verbose=True` to also receive `tool_call`, `tool_result`, `thinking`, `warning`. `answer_delta` carries only the final answer — process narration goes to `thinking`/`tool_call` and never overlaps.

The `sources` event keys its payload by backend — `papers` for arXiv (`arxiv_id`/`title`/`url`), `pages` for web (`url`/`title`/`read`). `agent_search_sources()` normalises both, plus the blocking endpoint's `sources`.

Both methods take `source` (`"arxiv"` / `"web"`), `effort`, `max_answer_tokens`, `language`, `timeout` (default 180s), plus `top_k` (arXiv) or `search_type` / `gl` / `hl` (web). Arguments are validated client-side, so an invalid call fails for free instead of spending a quota unit on a 422. Passing a backend's flag to the other backend raises rather than being silently dropped.

> These two methods **do not auto-retry**, unlike the rest of `Reader` — each call spends a quota unit, and a retried stream would re-bill and restart the answer. Handle `RateLimitError` with your own backoff.
>
> An `error` event is **yielded, not raised**: a partial answer may already have streamed, so the caller decides what to keep.

---

## Reader methods

```python
reader.agent_search(query, source="arxiv"|"web")   # agentic search → cited answer
reader.agent_search_stream(query, ...)             # same, streaming NDJSON events
reader.search(query, size=10, source="arxiv")      # unified retrieve
reader.brief(arxiv_id)                             # title, TLDR, keywords, citations
reader.head(arxiv_id)                              # metadata + sections overview
reader.section(arxiv_id, name)                     # one section
reader.preview(arxiv_id)                           # ~10k-char preview
reader.raw(arxiv_id) / reader.json(arxiv_id)       # full markdown / structured JSON
reader.trending(days=7, limit=30)                  # trending papers (days 1~30)
reader.talent_search(query, semantic=True)         # scholar search (spends agent quota)
reader.talent_survey(person_id, refresh=False)     # full profile for one scholar
reader.social_impact(arxiv_id)                     # popularity metrics
reader.pmc_head(pmc_id) / reader.pmc_json(pmc_id)  # PubMed Central
reader.biomed_search(...) / reader.biomed_data(...) # bioRxiv / medRxiv
```

<details>
<summary><b><code>reader.search()</code> parameters</b></summary>

```python
reader.search(
    query,
    size=10,                  # → upstream top_k (1~100); top_k= also accepted
    offset=0,                 # 0~10000
    source="arxiv",           # "arxiv" | "biorxiv" | "medrxiv"
    categories=None,          # list[str], filter only
    authors=None,             # list[str], filters and influences ranking
    orgs=None,                # list[str], filters and influences ranking
    venue=None,               # str | list[str]; aliases match automatically
    venue_year=None,          # int
    min_citation=None,        # int
    date_search_type=None,    # "between" | "exact" | "after" | "before"
    date_str=None,            # str, or [start, end] for "between"
    date_from=None,           # convenience; auto-mapped to the pair above
    date_to=None,
    use_fine_rerank=False,    # SDK defaults off (cheaper); True for better ordering
)
```

Venue alias matching is rule-based and best-effort, so it isn't always exact.

</details>

---

## Advanced Search

### Semantic Search

The retrieve endpoint is built on qdrant vector search — there is no search-mode
or weight tuning to do:

```python
from deepxiv_sdk import Reader

reader = Reader()

results = reader.search("agent memory", size=20)
```

The one ranking knob is `use_fine_rerank`. The SDK leaves it off (cheaper); turn
it on when ordering quality matters more than latency:

```python
results = reader.search("llm agents", size=20, use_fine_rerank=True)
```

> The old `search_mode` / `bm25_weight` / `vector_weight` parameters were
> removed in 0.4.0. They had been accepted-and-ignored since the 0.3.0 backend
> migration; passing them now raises `TypeError`.

### Advanced Filtering

```python
# Filter by categories (CS categories)
results = reader.search(
    "reinforcement learning",
    categories=["cs.AI", "cs.LG"],
    min_citation=50  # At least 50 citations
)

# Filter by date range
results = reader.search(
    "transformer",
    date_from="2024-01-01",
    date_to="2024-12-31"
)

# Filter by authors
results = reader.search(
    "attention mechanism",
    authors=["Ashish Vaswani", "Ilya Sutskever"]
)
```

## Efficient Content Loading

### Strategy 1: Quick Preview

For quick browsing, use `brief()` to get key information:

```python
brief = reader.brief("2409.05591")
print(f"Title: {brief['title']}")
print(f"TLDR: {brief.get('tldr')}")
print(f"Keywords: {brief.get('keywords')}")
print(f"Citations: {brief.get('citations')}")
print(f"GitHub: {brief.get('github_url')}")
```

**Token cost**: Very low (≈500 tokens)

### Strategy 2: Progressive Loading

Get metadata and section summaries, then load progressively:

```python
# 1. Get structure
head = reader.head("2409.05591")
print("Available sections:")
for section, info in head['sections'].items():
    print(f"  {section}: {info['token_count']} tokens - {info['tldr']}")

# 2. Load only relevant sections
intro = reader.section("2409.05591", "Introduction")
methods = reader.section("2409.05591", "Methods")
```

**Token cost**: Controlled (load only what you need)

### Strategy 3: Preview

Quickly scan paper beginning:

```python
preview = reader.preview("2409.05591")
print(preview['content'][:1000])
if preview['is_truncated']:
    print(f"... (total: {preview['total_characters']} chars)")
```

**Token cost**: Low (≈2k tokens)

### Strategy 4: Full Content

Load complete paper only when needed:

```python
full = reader.raw("2409.05591")
print(f"Full paper: {len(full)} chars, ~{len(full) // 4} tokens")
```

**Token cost**: High (10k-50k+ tokens)

## Error Handling and Retry

### Catch Specific Errors

```python
from deepxiv_sdk import (
    Reader,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    APIError
)

reader = Reader(token="your_token")

try:
    paper = reader.head("2409.05591")
except AuthenticationError:
    print("❌ Token invalid. Run 'deepxiv config' to update")
except RateLimitError:
    print("⚠️  Daily limit reached. Try again tomorrow")
except NotFoundError:
    print("❌ Paper not found. Check arXiv ID")
except APIError as e:
    print(f"❌ API error: {e}")
```

For `agent_search` / `agent_search_stream`, two of these carry a different
meaning:

```python
try:
    result = reader.agent_search("...", source="web")
except AuthenticationError:
    # 401 (invalid token) OR 403 — a valid SDK token without agentic access.
    # Agentic search needs a registered key; see README.
    ...
except RateLimitError:
    # The agentic quota is exhausted. It is a separate pool from the general
    # daily limit, so other Reader calls still work. These two methods never
    # auto-retry, so back off yourself.
    ...
```

### Custom Retry Configuration

```python
reader = Reader(
    token="your_token",
    timeout=120,      # Increase timeout
    max_retries=5,    # Up to 5 retries
    retry_delay=1.0   # Initial retry delay (seconds)
)
```

Reader automatically uses exponential backoff:
- Attempt 1 retry: 1 second
- Attempt 2 retry: 2 seconds
- Attempt 3 retry: 4 seconds
- ...

## Batch Processing

### Process Multiple Papers

```python
arxiv_ids = ["2409.05591", "2504.21776", "2503.04975"]

papers = {}
for arxiv_id in arxiv_ids:
    try:
        papers[arxiv_id] = reader.brief(arxiv_id)
    except Exception as e:
        print(f"Failed to fetch {arxiv_id}: {e}")

# Process fetched papers
for arxiv_id, paper in papers.items():
    print(f"{paper['title']} ({paper['citations']} citations)")
```

### Search Pagination

```python
# Get first 500 results
all_results = []
for offset in range(0, 500, 100):
    results = reader.search(
        "agent memory",
        size=100,
        offset=offset
    )
    all_results.extend(results['results'])

print(f"Total papers fetched: {len(all_results)}")
```

## Agent for Complex Analysis

### Basic Query

```python
from deepxiv_sdk import Agent

agent = Agent(
    api_key="your_openai_key",
    model="gpt-4"
)

answer = agent.query("What are key innovations in recent transformer papers?")
print(answer)
```

### Multi-Turn Conversation

```python
# First query
answer1 = agent.query("Summarize the MemGPT paper")
print(answer1)

# Follow-up uses previously loaded papers
answer2 = agent.query("Compare MemGPT with other long-context approaches")
print(answer2)

# Check loaded papers
loaded = agent.get_loaded_papers()
print(f"Papers loaded: {list(loaded.keys())}")

# Reset for new conversation
agent.reset_papers()
```

### Manual Paper Loading

```python
# Preload specific papers
agent.add_paper("2409.05591")
agent.add_paper("2504.21776")

# Then query
answer = agent.query("Compare these two papers")
```

### Use Different LLMs

```python
# DeepSeek
agent = Agent(
    api_key="your_deepseek_key",
    base_url="https://api.deepseek.com/v1",
    model="deepseek-chat"
)

# OpenRouter
agent = Agent(
    api_key="your_openrouter_key",
    base_url="https://openrouter.ai/api/v1",
    model="openai/gpt-4"
)

# Requesty
agent = Agent(
    api_key="your_requesty_key",
    base_url="https://router.requesty.ai/v1",
    model="openai/gpt-4o-mini"
)

# Local Ollama
agent = Agent(
    api_key="ollama",  # dummy key
    base_url="http://localhost:11434/v1",
    model="llama2"
)
```

## Best Practices

### 1. Use Appropriate Loading Strategy

```python
# ❌ Bad: Always load full papers
for arxiv_id in search_results:
    content = reader.raw(arxiv_id)  # Wastes tokens!

# ✅ Good: Progressive loading
for arxiv_id in search_results:
    brief = reader.brief(arxiv_id)  # Quick filter
    if is_relevant(brief):
        content = reader.raw(arxiv_id)  # Load only relevant ones
```

### 2. Cache Results

```python
import json
from pathlib import Path

cache_file = Path("paper_cache.json")
cache = json.loads(cache_file.read_text()) if cache_file.exists() else {}

def get_paper_cached(arxiv_id):
    if arxiv_id in cache:
        return cache[arxiv_id]

    paper = reader.head(arxiv_id)
    cache[arxiv_id] = paper
    cache_file.write_text(json.dumps(cache))
    return paper
```

### 3. Handle Large Search Results

```python
# Stream process results instead of loading all at once
def search_and_process(query, callback):
    offset = 0
    while True:
        results = reader.search(query, size=100, offset=offset)
        if not results['results']:
            break

        for paper in results['results']:
            callback(paper)  # Process each paper

        offset += 100

search_and_process("reinforcement learning", process_paper_func)
```

### 4. Enable Logging

```python
import logging

# Enable deepxiv logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('deepxiv_sdk')
logger.setLevel(logging.DEBUG)

# Now you'll see deepxiv debug info
reader = Reader()
results = reader.search("agent")  # Outputs logs
```

## Troubleshooting

### CLI

- **`ask` returns 403?** You're on an auto-registered token. Agentic search needs a registered key — see [Tokens and limits](#tokens-and-limits).
- **`ask` feels slow to start?** Only `--effort default` targets a sub-5s first token; `high`/`xhigh` deliberately gather more.
- **`ask` missed the point?** Rephrase more specifically rather than raising `--effort` — effort adds reading rounds but can't redirect first-round recall.
- **`ask` listed papers unrelated to the answer?** That's the retrieval set, not the citation list. `--all-sources` shows it in full.
- **A search returns 0 results?** Loosen filters — stacked date and citation constraints over-narrow quickly.
- **`talent survey` says no scholar with that ID?** IDs come from `deepxiv talent search`; the index doesn't use arXiv or Scholar IDs.
- **Agent errors with `Reasoning content is only supported as the last assistant message`?** Reasoning models need thinking off for multi-round tool use: `deepxiv agent query "…" --disable-thinking`, or `Agent(..., enable_thinking=False)`.
- **`agent.add_paper()` on a brand-new paper?** Returns `False` when the paper isn't indexed yet — papers under 1–3 days old often aren't.

### Issue: Token Expired

**Symptom**: `AuthenticationError: Invalid or expired token`

**Solution**:
```bash
deepxiv config --token YOUR_NEW_TOKEN
```

### Issue: Rate Limit

**Symptom**: `RateLimitError: Daily limit reached`

**Solution**:
- Wait until tomorrow (daily reset)
- Or contact tommy@chien.io for higher limit

### Issue: Network Timeout

**Symptom**: `APIError: Request timed out after 3 retries`

**Solution**:
```python
# Increase timeout and retry count
reader = Reader(timeout=180, max_retries=5)
```

`Reader` retries (max 3) with exponential backoff by default. The `agent_search*` methods never auto-retry, by design — see [Agentic search](#agentic-search).

### Issue: Paper Not Found

**Symptom**: `NotFoundError: Paper not found`

**Solution**:
- Check arXiv ID format (should be like `2409.05591`)
- Verify paper exists at https://arxiv.org

### Issue: Empty Search Results

**Symptom**: `No papers found matching 'query'`

**Solution**:
- Try different keywords
- Remove restrictive filters
- Check category codes are correct

## Environment Variables

Control deepxiv behavior with environment variables:

```bash
# API Token
export DEEPXIV_TOKEN="your_token"

# LLM API keys (for agent)
export DEEPXIV_AGENT_API_KEY="your_api_key"
export DEEPXIV_AGENT_BASE_URL="https://api.example.com"
export DEEPXIV_AGENT_MODEL="gpt-4"

# Enable debug logging
export DEEPXIV_DEBUG=1
```

## Performance Optimization

### Skip Fine Reranking

```python
# Default: fine reranking off — fastest and cheapest
results = reader.search("agents")

# Better ordering, extra upstream latency
results = reader.search("agents", use_fine_rerank=True)
```

### Limit Search Scope

```python
# Faster search
results = reader.search(
    "transformers",
    size=10,                           # Only top 10
    categories=["cs.CL", "cs.AI"],     # Limit categories
    date_from="2024-01-01"             # Recent papers only
)
```

---

Have questions or suggestions? [Open an issue on GitHub](https://github.com/qhjqhj00/deepxiv_sdk/issues)
