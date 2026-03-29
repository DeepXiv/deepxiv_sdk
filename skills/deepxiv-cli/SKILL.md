---
name: deepxiv-cli
version: "0.2.0"
description: Access academic papers (arXiv, PMC, and coming soon bioRxiv, medRxiv) via CLI with hybrid search and intelligent content extraction
frameworks: ["codex", "langchain", "claude-code", "custom-agents"]
use_cases: ["literature-search", "paper-analysis", "knowledge-synthesis", "research-assistant"]
---

# DeepXiv CLI Skill

## 🚀 30-Second Overview

**What**: Access open access academic papers (arXiv, PMC, bioRxiv, medRxiv) through a powerful CLI tool.

**What you can do**:
- 🔍 Search papers with hybrid search (BM25 + Vector)
- 📄 Read papers section-by-section (save tokens!)
- 🧠 Use built-in AI agent for analysis
- 📊 Access biomedical literature (PMC)

**When to use**: User wants to search, read, or analyze academic papers

---

## 🎯 Command Selection Guide

**I want to...** → **Use this command**

| Goal | Command | Example |
|------|---------|---------|
| Find papers on a topic | `deepxiv search` | `deepxiv search "agent memory" --limit 5` |
| Quickly understand a paper | `deepxiv paper <id> --brief` | `deepxiv paper 2409.05591 --brief` |
| Read specific section | `deepxiv paper <id> --section` | `deepxiv paper 2409.05591 --section Introduction` |
| See paper structure | `deepxiv paper <id> --head` | `deepxiv paper 2409.05591 --head` |
| Preview first 10k chars | `deepxiv paper <id> --preview` | `deepxiv paper 2409.05591 --preview` |
| Get full text | `deepxiv paper <id>` | `deepxiv paper 2409.05591` |
| Access biomedical paper | `deepxiv pmc <id>` | `deepxiv pmc PMC544940` |
| Intelligent analysis | `deepxiv agent query` | `deepxiv agent query "analyze this paper"` |

---

## 📚 Core Commands Reference

### 1. Search Papers (`deepxiv search`)

**When to use**: Finding relevant papers on a topic

```bash
# Basic search (quick)
deepxiv search "agent memory" --limit 5

# Advanced search with filters
deepxiv search "transformer" --mode bm25 --format json
deepxiv search "LLM" --categories cs.AI,cs.CL --min-citations 100

# Date range
deepxiv search "vision models" --date-from 2024-01-01 --date-to 2024-12-31
```

**Expected output**: List of papers with title, arxiv_id, score, citation count
**Token cost**: ~500-1000 tokens per search
**Tips**:
- Use `--limit 3-5` for quick overview
- Use `--format json` for downstream processing
- Adjust `bm25_weight` and `vector_weight` for different search styles

---

### 2. Read arXiv Papers (`deepxiv paper`)

**When to use**: Understanding specific papers (choose format by depth needed)

#### Option A: Quick Summary (30 seconds)
```bash
deepxiv paper 2409.05591 --brief
# ✓ Best for: Quick understanding
# → Title, TLDR, keywords, citation count
# Token cost: ~500 tokens
# Use when: "What's this paper about?"
```

#### Option B: Paper Structure (2 minutes)
```bash
deepxiv paper 2409.05591 --head
# ✓ Best for: Understanding paper organization
# → Metadata, all sections with summaries
# Token cost: ~1-2k tokens
# Use when: "What does this paper contain?"
```

#### Option C: Quick Scan (3 minutes)
```bash
deepxiv paper 2409.05591 --preview
# ✓ Best for: Fast preview without full read
# → First ~10k characters
# Token cost: ~2k tokens
# Use when: "Let me scan the introduction"
```

#### Option D: Specific Section (1 minute)
```bash
deepxiv paper 2409.05591 --section Introduction
# ✓ Best for: Reading one section in detail
# → Full section content
# Token cost: ~1-5k tokens (varies by section)
# Use when: "I only need the introduction"
```

#### Option E: Complete Paper (for deep analysis)
```bash
deepxiv paper 2409.05591
# or explicitly: deepxiv paper 2409.05591 --raw
# ✓ Best for: Full text analysis
# → Complete paper in markdown
# Token cost: ~10-50k tokens
# Use when: "I need to thoroughly analyze this"
```

---

### 3. Access Biomedical Literature (`deepxiv pmc`)

**When to use**: Need medical, biology, or biomedical research

```bash
# Quick metadata
deepxiv pmc PMC544940 --head

# Full paper
deepxiv pmc PMC544940
```

**Expected output**: Paper metadata or complete paper JSON
**Token cost**: ~1-2k tokens (metadata), ~10-30k tokens (full)

---

### 4. Manage Token (`deepxiv token`)

**When to use**: Check your API token status

```bash
deepxiv token
# Shows current token and daily limit info
```

**Note**: Token auto-registers on first use, saves to `~/.env`

---

### 5. Intelligent Agent (`deepxiv agent`)

**When to use**: Need analysis beyond simple retrieval

```bash
# One-time query
deepxiv agent query "What are key innovations in this paper?"

# Multi-turn reasoning
deepxiv agent query "Compare these two approaches" --max-turn 10 --verbose

# First time setup
deepxiv agent config
# Configure your LLM (OpenAI, DeepSeek, OpenRouter, etc.)
```

**Token cost**: Varies by reasoning depth
**Requirements**: Requires langgraph and langchain-core

---

## 🎬 Common Workflows

### Workflow 1: Quick Paper Review (2 minutes)
```bash
# Step 1: Get brief info
deepxiv paper 2409.05591 --brief

# Step 2: Read introduction
deepxiv paper 2409.05591 --section Introduction

# Step 3: Check results (optional)
deepxiv paper 2409.05591 --section Results
```
**Total tokens**: ~2-3k | **Use case**: Quick assessment before deciding to read fully

### Workflow 2: Deep Paper Analysis (15 minutes)
```bash
# Step 1: Understand structure
deepxiv paper 2409.05591 --head

# Step 2: Read key sections
deepxiv paper 2409.05591 --section Introduction
deepxiv paper 2409.05591 --section Methods
deepxiv paper 2409.05591 --section Results

# Step 3: AI analysis
deepxiv agent query "Summarize the main contributions"
```
**Total tokens**: ~10-15k | **Use case**: Thorough understanding

### Workflow 3: Literature Search (5 minutes)
```bash
# Step 1: Find relevant papers
deepxiv search "agent memory" --limit 5

# Step 2: Quick assess each
for id in results; do
    deepxiv paper $id --brief
done

# Step 3: Deep read top 2
deepxiv paper <top_id_1>
deepxiv paper <top_id_2>
```
**Total tokens**: ~5-10k | **Use case**: Literature review

---

## 💪 Capabilities & Limitations

### What deepxiv Can Do ✅

| Capability | Details |
|-----------|---------|
| **Hybrid Search** | BM25 + Vector search across 2M+ arXiv papers |
| **Smart Summaries** | AI-generated TLDRs and keywords |
| **Section Access** | Read specific sections without loading full text |
| **Biomedical Access** | PubMed Central (PMC) papers |
| **Open Access Only** | arXiv, PMC, bioRxiv (coming), medRxiv (coming) |
| **Intelligent Analysis** | ReAct agent with multi-turn reasoning |
| **Multiple LLMs** | Compatible with OpenAI, DeepSeek, OpenRouter, etc. |

### What deepxiv Cannot Do ❌

| Limitation | Note |
|-----------|------|
| **Subscription Journals** | Only open access papers (by design) |
| **Real-time Updates** | arXiv has ~1-2 day delay |
| **Paywalled Content** | Cannot access IEEE, ACM, etc. journals |
| **Daily Limits** | 10,000 requests/day free (email for more) |
| **Proprietary Data** | Only academic papers, not internal docs |

---

## 🔧 Troubleshooting

### Problem: Paper Not Found
```bash
deepxiv paper invalid_id
# Error: NotFoundError: Paper not found
```
**Solution**:
- Check arXiv ID format (should be like `2409.05591`)
- Verify at https://arxiv.org

### Problem: Daily Limit Exceeded
```bash
deepxiv search "topic"
# Error: RateLimitError: Daily limit reached
```
**Solution**:
- Wait until tomorrow (limit resets daily)
- OR email `tommy@chien.io` with name, email, phone for higher limit

### Problem: Token Invalid
```bash
deepxiv paper 2409.05591
# Error: AuthenticationError: Invalid or expired token
```
**Solution**:
- Run `deepxiv config --token YOUR_NEW_TOKEN`
- Or delete `~/.env` to auto-register new token

### Problem: Agent Dependencies Missing
```bash
deepxiv agent query "analyze"
# Error: langgraph not installed
```
**Solution**:
```bash
pip install deepxiv-sdk[agent]
```

### Problem: Timeout on Large Papers
```bash
deepxiv paper <large_paper_id>
# Error: Request timed out
```
**Solution**:
- Use `--brief` or `--head` instead of full paper
- Or use `--section` to read specific parts
- Increase timeout: Use Python API with `Reader(timeout=180)`

---

## 📊 Output Format Guide

### For Search Results
**Format**: Show title, arxiv_id, brief context
```
1. Title of Paper (2409.05591)
   - Field: Computer Science / AI
   - Citations: 150
   - Key idea: Brief 1-line summary of main contribution
```

### For Paper Reading
**Always mention what command was used**:
```
From `deepxiv paper 2409.05591 --brief`:
- Title: MemGPT: Towards LLMs as Operating Systems
- TLDR: Introduces hierarchical memory management for extended context
- Key concepts: agent memory, context management, LLM systems
- (~500 tokens)
```

### For Structured Data
**Use JSON format when**:
- Processing results programmatically
- Building pipelines
- Storing for later analysis
```bash
deepxiv search "topic" --format json  # Pipe to other tools
```

---

## ⏱️ Token Budget Guide

When planning queries, consider token costs:

```
Quick Summary:        500 tokens
Metadata (--head):    1-2k tokens
One Section:          1-5k tokens (depends on section)
Full Paper:           10-50k tokens
Search Query:         0.5-1k tokens
Agent Analysis:       5-20k tokens (reasoning depth)
```

**Recommendation**: For general use, stick to `--brief` and `--section` to keep tokens under 5k per query.

---

## 🚀 Advanced Usage

### Batch Processing (Multiple Papers)
```bash
for id in 2409.05591 2504.21776 2503.04975; do
    echo "=== $id ==="
    deepxiv paper $id --brief
done
```

### Piping to Other Tools
```bash
deepxiv search "topic" --format json | jq '.results[] | .arxiv_id'
```

### Custom Token Configuration
```python
from deepxiv_sdk import Reader
reader = Reader(token="YOUR_TOKEN", timeout=120, max_retries=5)
```

---

## 🌐 Supported & Coming Soon

### Current Support ✅
- **arXiv** - Computer Science, Physics, Math, Economics
- **PMC** - PubMed Central biomedical literature

### Coming Soon 🔄
- **bioRxiv** - Biology preprints
- **medRxiv** - Medicine preprints
- **Other OA** - Additional open access sources
- **Full OA Ecosystem** - Unified cross-source search

---

## 📞 Getting Help

**Command not working?**
```bash
deepxiv <command> --help
```

**Need a higher daily limit?**
Email: `tommy@chien.io` with name, email, phone

**Found a bug?**
[GitHub Issues](https://github.com/qhjqhj00/deepxiv_sdk/issues)

**Learn more?**
[Full Documentation](https://github.com/qhjqhj00/deepxiv_sdk#readme)

---

## ✨ Tips & Best Practices

1. **Start with `--brief`** - Always start with brief overview
2. **Use sections** - Don't load full papers when sections suffice
3. **Save tokens** - Stack operations to reduce API calls
4. **Check limits** - Run `deepxiv token` before large batches
5. **Use agent wisely** - For complex analysis that needs reasoning
6. **Format choice** - Use `--format json` for piping, plain text for humans
7. **Error handling** - Always handle "Paper not found" and "Limit exceeded" cases

---

**Last Updated**: 2024 | **Version**: 0.2.0 | **Status**: Production Ready
