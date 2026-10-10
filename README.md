<h1 align="center">DeepXiv</h1>
<p align="center"><em>The data layer agentic search is missing — full paper text, real citations, and the people behind them.</em></p>

<p align="center">
  <a href="https://deepxiv.com">Live system</a> ·
  <a href="USAGE.md">Full documentation</a> ·
  <a href="https://data.rag.ac.cn/api/docs">API docs</a> ·
  <a href="https://data.rag.ac.cn/status">Status</a> ·
  <a href="https://arxiv.org/abs/2603.00084"><img src="https://img.shields.io/badge/arXiv-2603.00084-b31b1b" alt="arXiv"></a> ·
  <a href="README.zh.md">中文</a>
</p>

<p align="center">
  <img src="./assets/demo.gif" width="100%">
  <br>
  <em><code>deepxiv ask</code> — a question in, a cited answer streaming out</em>
</p>

---

## What it is

A CLI and Python SDK over a service that has already read the literature. Papers arrive parsed into sections rather than PDFs, retrieval runs over full bodies rather than abstracts, and an agentic endpoint answers questions with citations that resolve to real arXiv IDs and URLs.

Four things it does:

| | Command | |
|---|---|---|
| **Ask the literature** | `deepxiv ask` | A question in, an answer out, cited with real arXiv IDs |
| **Ask the web** | `deepxiv ask --web` | Same, over Google plus cached page bodies |
| **Read a paper in layers** | `deepxiv search` / `paper` | Search, judge, then read only the section you need |
| **Find the people** | `deepxiv fa … talent` | Who works on a topic, where, and what their record is |
| **Go beyond papers** | `deepxiv fa` | Statutes, judgments, trials, drugs, grants, filings, standards, CVEs — via 1stAuthor |

## What problem it solves

An agent researching a topic has bad options. Search APIs return ten blue links and abstracts — enough to name a paper, never enough to answer "what speedup does it report on HumanEval". PDFs answer that, but cost 50k tokens each and arrive as a wall of text with no structure to navigate.

DeepXiv removes the tradeoff. Papers are pre-parsed, so an agent can spend 300 tokens on a TLDR to decide whether to spend 5k on the Methods section. Questions that need evidence go to the agentic endpoint, which reads source text and hands back an answer with citations you can check. And because knowing *who* does the work is half of research, the same token searches scholars — plus law, clinical trials, drugs, grants and more through [1stAuthor](https://1stauthor.com)'s domains.

## DeepXiv × 1stAuthor

DeepXiv works closely with [1stAuthor](https://1stauthor.com) to serve data beyond papers: researchers, statutes, court judgments, clinical trials, drugs, grants, filings, standards and CVEs, all reached through `deepxiv fa` with the same token.

DeepXiv itself stays focused on agentic data services for academic papers, and **will remain free**. If you need higher limits on the 1stAuthor domains, see [1stauthor.com](https://1stauthor.com).

> 1stAuthor is in closed beta. Questions or problems? [Open an issue](https://github.com/DeepXiv/deepxiv_sdk/issues).

## Install

```bash
pip install deepxiv-sdk
```

> **Beta:** `deepxiv fa` (1stAuthor domains, including talent) isn't on PyPI yet. It ships in `1.2.0b1` from source:
>
> ```bash
> pip install git+https://github.com/DeepXiv/deepxiv_sdk.git
> ```

`deepxiv` auto-registers a token on first use. Agentic commands (`ask`, `fa ask`) need a registered key instead — get one at [data.rag.ac.cn/register](https://data.rag.ac.cn/register), then:

```bash
deepxiv config --token YOUR_REGISTERED_KEY
```

Every account gets 300 agentic calls/day free, on a pool separate from the general daily limit.

## Usage

One investigation, start to finish. You've heard speculative decoding got much faster this year and want to know what's real.

**1. Ask the literature.** Start with the question, not a keyword. The service picks its own tools, reads paper bodies, and cites what it used.

```bash
deepxiv ask "what speedup does speculative decoding report on HumanEval in 2025"
```

```
DEER reports a 5.54× speedup on HumanEval (with Qwen3-30B-A3B as the target
model), compared to EAGLE-3's 2.41× on the same benchmark [arXiv:2512.15176].

📚 Sources (1 cited, 10 retrieved — use --all-sources for the rest):
  1. [2512.15176] DEER: Draft with Diffusion, Verify with Autoregressive Models
```

The answer goes to stdout and sources to stderr, so `deepxiv ask "…" > answer.md` captures just the answer. Add `--effort high` when a question spans several papers.

**2. Read the paper it cited — in layers.** Never load a whole paper to answer a question about one section.

```bash
deepxiv paper 2512.15176 --brief              # title, TLDR, keywords, citations — worth reading?
deepxiv paper 2512.15176 --head               # section list + where the tokens are
deepxiv paper 2512.15176 --section Experiment # read only that
```

Each step costs an order of magnitude more than the last, so you stop as soon as you have your answer. Take section names from `--head` — papers don't share a common outline. `--preview` gives ~10k chars; no flag at all gives the full markdown.

**3. Widen it into a search.** Once you know what you're looking for, filter for the rest.

```bash
deepxiv search "speculative decoding" --date-from 2025-01 --min-citations 20 --limit 10
```

Filters combine with `AND` — `--authors`, `--orgs`, `--categories`, `--venue`/`--venue-year`, dates, citation floors. Stack too many and you'll legitimately get zero results; loosen one.

**4. Find the people behind it.** A method is worth more when you know whose lab it comes from and what else they've built.

```bash
deepxiv fa search talent "speculative decoding" --top-k 5   # names, topics, or both
deepxiv fa search talent "RAG" -F org=清华大学 -F "h_index>=30"
deepxiv fa read talent 12                                    # profile: bio, education, career, top papers, metrics
deepxiv fa read talent 12 --level full                       # the full researched profile (markdown)
```

Names (Chinese, pinyin, English) and topics both work. IDs from `search` feed `read`; `deepxiv fa spec talent` lists the filters and what each read level costs. `deepxiv talent search|survey` still work as deprecated aliases, but IDs from the old index don't carry over.

The same verbs cover 1stAuthor's other domains — `deepxiv fa domains` lists them:

```bash
deepxiv fa search law "个人信息保护" --top-k 5
deepxiv fa ask "个人信息出境需要满足什么条件" --domain law   # registered key, agentic quota
```

**5. Step off arXiv when the question isn't academic.** Licensing, pricing, who shipped what last week — same command, different backend.

```bash
deepxiv ask "which inference providers support speculative decoding today" --web
deepxiv ask "NeurIPS 2025 best paper" --web --search-type news
```

The web backend reads *cached* page bodies. Pages read in full are marked 📄, snippet-only ones 🔗 — weigh them accordingly.

**In Python**, the same pipeline is `Reader`:

```python
from deepxiv_sdk import Reader

reader = Reader(token="YOUR_REGISTERED_KEY")   # Reader takes the token explicitly
answer = reader.agent_search("what speedup does DEER report on HumanEval")["answer"]
method = reader.section("2512.15176", "Method")
people = reader.fa().search("talent", "speculative decoding", top_k=5)
```

## Documentation

- **[USAGE.md](USAGE.md)** — full CLI reference, the Python API, streaming, error handling, batching, and the built-in research agent. ([中文](USAGE.zh.md))
- **[skills/deepxiv-cli/SKILL.md](skills/deepxiv-cli/SKILL.md)** — drop-in operating instructions for coding agents. Two worked workflows also ship as skills: [trending digest](skills/deepxiv-trending-digest/SKILL.md), [baseline table](skills/deepxiv-baseline-table/SKILL.md).
- **[examples/](examples/)** — runnable scripts for each entry point.

Also available: PubMed Central, bioRxiv/medRxiv, trending papers, and per-paper social metrics — see [USAGE.md](USAGE.md#other-sources).

## Citation

If DeepXiv is useful in your work, please cite the technical report:

```bibtex
@article{qian2026deepxiv,
  title   = {DeepXiv-SDK: An Agentic Data Interface for Scientific Literature},
  author  = {Qian, Hongjin and Xia, Ziyi and Liu, Ze and Chen, Jianlyu and
             Luo, Kun and Qin, Minghao and Li, Chaofan and Xiong, Lei and
             Lan, Junwei and Wang, Sen and Liang, Zhengyang and Shao, Yingxia and
             Lian, Defu and Liu, Zheng},
  journal = {arXiv preprint arXiv:2603.00084},
  year    = {2026},
  url     = {https://arxiv.org/abs/2603.00084}
}
```

## License & support

MIT — see [LICENSE](LICENSE).

- 🐛 **Issues**: [github.com/DeepXiv/deepxiv_sdk/issues](https://github.com/DeepXiv/deepxiv_sdk/issues)
- 📧 **Higher limits**: email `tommy[at]chien.io` with your use case
