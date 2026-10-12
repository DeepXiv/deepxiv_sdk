---
name: deepxiv-cli
version: "1.2.1"
description: Use the deepxiv CLI to search and read academic papers (arXiv, PMC, bioRxiv, medRxiv) section by section, get cited answers from papers or the web, and query 1stAuthor's domains with the same token — AI researchers and their profiles, which academicians and fellows cited a paper, Chinese and US statutes, court judgments, clinical trials, drug labels, research grants, company filings, Chinese national standards, CVEs and the US Federal Register. Use when a task needs papers, people, legal or regulatory text, trials, drugs, grants, filings, standards or vulnerabilities as evidence.
frameworks: ["claude-code", "codex", "langchain", "custom-agents"]
use_cases: ["literature-search", "paper-analysis", "talent-search", "citation-appraisal", "legal-research", "clinical-trials", "regulatory-research", "security-research"]
---

# DeepXiv CLI

One CLI, one token: papers (`search`, `paper`, `pmc`, `trending`, `ask`) plus 12
1stAuthor domains (`deepxiv fa …`). Everything below was run against production
on 2026-10-12 with deepxiv-sdk 1.2.1.

## 1. Setup

```bash
pip install -U deepxiv-sdk          # `deepxiv fa` needs 1.2.0+, `fa search --sort` 1.2.1+
deepxiv --version
deepxiv token                       # shows the active token
```

- **Token**: the first call auto-registers a free token and saves it to `~/.env`
  (`DEEPXIV_TOKEN`). Every command also takes `-t TOKEN`.
- **Registered key**: `deepxiv ask` and `deepxiv fa ask` (the agentic calls)
  return **403** on the auto-registered token. Tell the user to register at
  https://data.rag.ac.cn/register and run `deepxiv config --token THEIR_KEY`.
  Do not retry a 403. Search and read commands work on either token.
- **No other keys**: 1stAuthor domains go through deepxiv with the same token.

## 2. Which command

| The task needs… | Command |
|---|---|
| An answer, with citations, from the literature | `deepxiv ask "…"` |
| An answer about anything non-academic (news, products, pricing) | `deepxiv ask "…" --web` |
| Papers on a topic | `deepxiv search "…"` |
| One paper, as cheaply as possible | `deepxiv paper ID --brief` → `--head` → `--section NAME` |
| Biomedical full text | `deepxiv pmc PMCID`, `deepxiv search "…" --biorxiv/--medrxiv` |
| What's hot on arXiv | `deepxiv trending --days 7` |
| People: researchers, students, profiles, coauthors | `deepxiv fa … talent` |
| Which academicians / fellows cited a paper, and what they said | `deepxiv fa … appraise` |
| Statutes (China and 25 other jurisdictions) | `deepxiv fa … law` |
| Court judgments (China, US) | `deepxiv fa … cases` |
| US statutes, regulations, agency decisions | `deepxiv fa … us_law` |
| Clinical trials (ClinicalTrials.gov) | `deepxiv fa … trials` |
| US drug labels (openFDA) | `deepxiv fa … drugs` |
| NSF / NIH grants | `deepxiv fa … grants` |
| Company filings (SEC, China) | `deepxiv fa … filings` |
| Chinese national standards (GB, GB/T) | `deepxiv fa … standards` |
| Vulnerabilities (NVD + CISA KEV + EPSS) | `deepxiv fa … cve` |
| US Federal Register | `deepxiv fa … fr` |
| A cited answer over one of those domains | `deepxiv fa ask "…" -d DOMAIN` |

**Prefer `ask` when the user wants an answer**, and search/read when they want
the documents themselves, a complete list, or numbers you will compute on.

## 3. Output contract (all commands)

- **stdout is data only**: hits, documents, answers, or JSON with `--json`
  (`--format json` for `search`). **stderr** carries quota, progress, routing,
  sources, hints and errors. So `> file` and `| jq` get clean data.
- **Exit codes**: `0` success · `1` API/network error (401, 403, 429, 4xx, 5xx,
  or an error during `ask`) · `2` bad usage (unknown filter field, bad value).
- **Quota line** on stderr after every `fa` call: `💳 cost 2 · 9990/10000 left today`.

## 4. Papers

### Search

```bash
deepxiv search "speculative decoding" --limit 10
deepxiv search "world model" --date-from 2025-01 --min-citations 20 --limit 20
deepxiv search "LLM agents" --categories cs.AI,cs.CL --venue NeurIPS --venue-year 2025
deepxiv search "protein design" --biorxiv --limit 5
deepxiv search "world model" --limit 100 --format json | jq -r '.result[].arxiv_id'
```

Options: `--limit 1..100`, `--offset`, `--categories`, `--authors`, `--orgs`,
`--venue` (repeatable), `--venue-year`, `--min-citations`, `--date-from/--date-to`
(YYYY, YYYY-MM or YYYY-MM-DD), `--use-fine-rerank`. JSON hits carry
`arxiv_id, title, tldr, abstract, authors, date, citation_count, categories, venue, github_url`.

### Read progressively — the main token saver

```bash
deepxiv paper 2603.19312 --brief                 # ~300 tokens: TLDR, keywords, citations, GitHub
deepxiv paper 2603.19312 --head                  # section list with per-section TLDR and token_count (JSON)
deepxiv paper 2603.19312 --section "Introduction"  # one section
deepxiv paper 2603.19312 --preview               # first ~10k chars
deepxiv paper 2603.19312                         # full text (often 20–50k tokens)
deepxiv paper 2603.19312 --popularity            # social signal
deepxiv paper 10.1101/2021.02.26.433129 --biorxiv
deepxiv pmc PMC544940 --head
```

Rule: `--brief` to decide, `--head` to find the section, `--section` to read it.
Pass section names exactly as `--head` prints them (including odd escapes like
`\&`). For hundreds of papers, run `--brief` in parallel
(`xargs -P 8 -I{} deepxiv paper {} --brief`) — 340 briefs take ~16 s.

### Ask (registered key)

```bash
deepxiv ask "what speedup does speculative decoding report on HumanEval"
deepxiv ask "compare methods for MoE routing collapse" --effort high
deepxiv ask "NeurIPS 2025 best paper" --web --search-type news
deepxiv ask "…" > answer.md          # answer only; sources stay on stderr
```

`--effort default|high|xhigh` (more reading rounds), `--web`, `--search-type
search|scholar|news|images`, `--top-k`, `--max-answer-tokens`, `--json`,
`--all-sources`. Be specific and ask for numbers; if the answer misses,
rephrase rather than raising effort. Every `[arXiv:ID]` it cites is real — keep
them. On `--web`, pages marked 🔗 were read only as snippets; say so.

## 5. 1stAuthor domains (`deepxiv fa`)

### The loop

```bash
deepxiv fa domains                    # 12 domains, doc counts (free)
deepxiv fa spec talent                # filters, levels, extras, prices, samples (free)
deepxiv fa search talent "Geoffrey Hinton" -k 3      # → ids
deepxiv fa read talent 15023 -l brief                # cheapest card
deepxiv fa read talent 15023                         # default level (detail)
deepxiv fa ask "…" -d talent                         # cited answer (registered key)
```

**Always run `deepxiv fa spec DOMAIN` before filtering** — field names, allowed
operators, sort orders, read levels and prices differ per domain and are listed
there. A per-domain digest is in [references/fa-domains.md](references/fa-domains.md).

### search

```bash
deepxiv fa search DOMAIN "query" [-F FILTER]... [-k N] [--offset N] [--mode M] [--sort S] [--head] [--json]
```

- `-k` 1–100 (default 10). `--mode`: e.g. `hybrid`, `dense`, `bm25`, `name`
  (talent). `--sort`: e.g. `date`, `epss` (cve). `--head`: richer hits, costs more.
- Filter-only listing: pass `"*"` as the query (an empty string is rejected).
- Filter syntax (validated against the spec; a bad field exits 2):

| `-F` | Meaning |
|---|---|
| `k=v` | equals |
| `k=a,b` | any of |
| `k>=n`, `k<=n` | range bound |
| `k=n..m` | range |
| `k~text` | full-text match on a text field |
| `k=true` | boolean |

- Filter values are the database's own values. For Chinese institutions and
  cities they are Chinese (`org=清华大学`, `location=北京,上海`). Get real values
  with `deepxiv fa facets DOMAIN FIELD`.

### read

```bash
deepxiv fa read DOMAIN ID [ID...] [-l brief|detail|full] [-e EXTRA] [-p k=v]... [-f json|md|html] [--json]
```

- `-l brief` is cheapest; default is usually `detail`; `full` is the longest
  (talent full = researched profile in markdown).
- `-e` adds one extra: talent `network` (coauthors/advisors/students), `papers`,
  `scholar`, `sources`; appraise `honorees`. Prices in the spec.
- `-p` passes domain parameters, e.g. appraise `-p stance=positive -p org=CAS,CAE
  -p honoree="Yoshua Bengio"`; law `-p section=<chapter id>` with `-l full`.
- Several ids in one call: `deepxiv fa read talent 15023 3426 2813`.
- IDs with slashes or spaces work as one quoted argument: `"GB/T 42729-2023"`.

### facets, resolve

```bash
deepxiv fa facets talent career_stage          # value → count, for -F
deepxiv fa resolve "Geoffrey Hinton" "Yann LeCun"   # names → talent ids, batch
```

### ask (registered key)

```bash
deepxiv fa ask "who works on self-supervised learning at Mila" -d talent
deepxiv fa ask "DeepSeek-R1 得到了哪些院士的正面评价" -d appraise -p paper=arxiv:2501.12948
deepxiv fa ask "个人信息出境需要满足什么条件" -d law -e medium
deepxiv fa ask "recruiting phase 3 trials for pancreatic cancer" -d trials
deepxiv fa ask "今天有哪些高危在野利用漏洞"            # no -d: routed; stderr says where
```

`-e low|medium|high`, `-p` domain params (`deepxiv fa spec D` lists them),
`--no-stream`, `--json`, `-v` (tool calls on stderr). Each domain's ask answers
from that domain only; to cover several, run one ask per domain (they can run
in parallel) and merge. If stderr shows a low-confidence route, re-run with `-d`.
Citations look like `[law:…]`, `[cve:CVE-…]`; keep them.

## 6. Domain recipes (verified)

```bash
# talent — people
deepxiv fa search talent "Yann LeCun" -k 3                       # names: English, Chinese, pinyin, "Last, First"
deepxiv fa search talent "具身智能" -F org=清华大学 -F role=教授 -F min_h_index=30 -k 10
deepxiv fa search talent "world model" -F career_stage=student -F location=北京,上海 -k 50
ids=$(deepxiv fa search talent "world model" -F career_stage=student -k 40 --json | jq -r '.hits[].id')
deepxiv fa read talent $ids > profiles.json                      # 40 profiles in one call (~4 s)
deepxiv fa read talent 15023 -e network

# appraise — who of note cited a paper
deepxiv fa search appraise "DeepSeek-R1" -k 3                    # → arxiv:2501.12948
deepxiv fa read appraise arxiv:2501.12948 -l brief               # counts + stance breakdown
deepxiv fa read appraise arxiv:2501.12948 -p stance=positive -p org=CAS,CAE

# law / cases / us_law
deepxiv fa search law "刑法第266条" -k 3                          # statute + article number locates directly
deepxiv fa read law 刑法 -l brief
deepxiv fa search cases "网络刷单诈骗 未遂" -F province=浙江省 -F "judge_year>=2018" -k 5
deepxiv fa search cases "qualified immunity police" -F country=us -F court_level=scotus -k 5
deepxiv fa search us_law "data breach notification" -F jurisdiction=ca,ny -k 5

# trials / drugs / grants
deepxiv fa search trials "GLP-1 obesity" -F phase=PHASE3 -F overall_status=RECRUITING -k 5
deepxiv fa read trials NCT02082496 -l brief
deepxiv fa search drugs "GLP-1 weight loss" -F has_boxed_warning=true -k 5
deepxiv fa search grants "single-cell transcriptomics" -F agency=nih -F "fy>=2020" -k 5

# filings / standards / cve / fr
deepxiv fa search filings "CEO resignation" -F market=us -F event_types=officer_director_change -F "filed_year>=2023" -k 5
deepxiv fa search filings "*" -F form=10-Q -F cik=320193 --sort date -k 4
deepxiv fa search standards "锂离子电池安全" -F state=现行 -k 5
deepxiv fa read standards "GB/T 42729-2023" -l brief
deepxiv fa search cve "*" -F kev=true -F severity=critical,high --sort epss -k 10
deepxiv fa read cve CVE-2024-3400 -l brief
deepxiv fa search fr "PFAS drinking water" -F doc_type=Rule -k 5
```

Domain caveats worth passing on (details in the reference): model-written
fields (one-liners, summaries, cve `vuln_class`, standards `title_en`) are for
summarising, not quoting — quote the original-text fields and cite by `id`.
CVE output must carry the NVD "not endorsed" notice. The standards domain is a
catalogue only (no clause text).

## 7. Workflows

**Literature survey** (≈2 min for a few hundred papers):
1. 8–15 `deepxiv search … --limit 100 --format json` calls on sub-topics; dedupe ids.
2. `--brief` on the 200–400 most relevant (parallel).
3. `--head` + one `--section` on the 10–15 key papers.
4. Write the synthesis citing only papers you read, with arXiv ids.

**Find people for a topic**: `fa search talent` with `career_stage` / `location`
/ `org` / `min_h_index` filters → `fa read talent <ids>` in one batch → rank on
h-index, areas and representative papers. Profiles are LLM-researched: verify
before making decisions about a person, and don't publish personal details.

**Who praised this paper**: `fa search appraise "<title>"` → `read -l brief` for
counts → `read -p stance=positive` (add `-p org=…` to narrow) → or
`fa ask -d appraise -p paper=<id>` for a written, quote-backed summary.

**Legal question across jurisdictions**: run `fa ask -d law`, `-d cases` and
`-d us_law` in parallel with the same question, then merge, keeping every
citation. Answers are research aids, not legal advice; say so.

## 8. Cost and limits

- `fa` search/read/facets/resolve draw on the general daily limit at the prices
  in `fa spec` (search 2; read 1–10 by level; extras 1–20). Free samples in the
  spec cost 0. Read `brief` first and go deeper only for what you will use.
- `ask` and `fa ask` use the separate agentic pool: 1 per question, 300/day on a
  free registered account, regardless of effort.
- On **429**: daily limit (wait, or the user asks for more), or concurrency
  (the CLI retries once after `Retry-After`); keep parallelism ≤ 4 per key for
  `fa` and ≤ 8 for `paper --brief`.

## 9. Errors

| Symptom | Do |
|---|---|
| `403 … registered account key` on `ask` / `fa ask` | Ask the user to register (https://data.rag.ac.cn/register) and `deepxiv config --token KEY`; meanwhile use search + read |
| Exit 2, `unknown filter` / bad op | `deepxiv fa spec DOMAIN`; use the listed field and operator |
| `400 … query must be 1–1000 characters` | Use `"*"` for filter-only searches |
| No hits | Loosen filters, check values with `fa facets`, try another `--mode` |
| `Paper not found` | Check the id format (`2409.05591`); bioRxiv/medRxiv need the flag |
| Truncation warning on `ask` | Raise `--max-answer-tokens` or narrow the question |

## 10. Python

```python
import os
from deepxiv_sdk import Reader
r = Reader(token=os.environ["DEEPXIV_TOKEN"])  # Reader takes the token explicitly
r.search("world model", size=10)
r.brief("2603.19312"); r.head("2603.19312"); r.section("2603.19312", "Introduction")

fa = r.fa()                                     # FAClient, same token
fa.search("talent", "Geoffrey Hinton", top_k=3)
fa.search("cve", "*", filters={"kev": True}, sort="epss")
fa.read("talent", "15023", level="brief")
for ev in fa.ask_stream("个人信息出境需要满足什么条件", domain="law"):
    ...                                         # route, answer_delta, sources, done, error
```

Full references: [FA.md](../../FA.md) (every `fa` option, events, HTTP API),
[USAGE.md](../../USAGE.md) (papers and the Python API).
