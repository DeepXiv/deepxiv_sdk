---
name: deepxiv-fa-cve
description: Search ~390k public vulnerabilities (NVD) with CISA KEV exploited-in-the-wild flags and EPSS exploitation probability. Use when a task needs vulnerabilities in a product, or which ones are being exploited now.
---

# DeepXiv · CVE (`cve`)

About 390k public vulnerabilities (NVD, synced daily; exact count in /v1/cve corpus) plus CISA KEV exploited-in-the-wild flags and FIRST EPSS exploitation probability. Vulnerability class (closed set of 17), attacker prerequisites, affected scope, impact and one-line summaries are model-extracted. Hybrid vector + lexical search; filters and sorting in Postgres.

Corpus: 390,242 documents.

## Setup

```bash
pip install -U deepxiv-sdk      # deepxiv registers a token on first use
```

`search` and `read` spend the deepxiv daily limit at the credits listed below. `ask` spends the agentic quota: a registered key from https://data.rag.ac.cn/register (300/day), or 3 lifetime trial asks on the auto-registered token. Data goes to stdout; cost, quota and sources go to stderr. Exit 0 ok, 1 API error, 2 usage error. The general CLI guide is the `deepxiv-cli` skill.

## Start here

```bash
deepxiv fa search cve "palo alto globalprotect rce" -k 5
deepxiv fa search cve "*" -F kev=true -F severity=critical,high --sort epss -k 10   # exploited in the wild, ranked by EPSS
deepxiv fa read cve CVE-2024-3400 -l brief
deepxiv fa ask "今天有哪些高危在野利用漏洞" -d cve
```

Free samples: ids `CVE-2024-3400`; queries `log4j`.

## Search

```bash
deepxiv fa search cve "query" [-F FILTER]... [-k N] [--offset N] [--mode M] [--sort S] [--head] [--json]
```

Modes: hybrid, dense, bm25, keyword. Up to 200 hits. Cost 2 (with `--head`: 3).
Sorts: `relevance`, `date`, `epss`, `kev_added`, `published` (default `relevance`).
An empty query is rejected; use `"*"` to list by filters only. Filters combine with AND; an undeclared field exits 2.

| filter | type | `-F` syntax | meaning |
|---|---|---|---|
| `cvss_score` | number | `k>=n`, `k=n..m` | CVSS score, range |
| `epss` | number | `k>=n`, `k=n..m` | EPSS 30-day exploitation probability (0–1), range |
| `kev` | bool | `k=v` | Listed in CISA KEV (known exploited in the wild) |
| `published` | datetime | `k>=n`, `k=n..m` | Publication date range |
| `severity` | keyword | `k=v`, `k=a,b` | CVSS severity (derived from the score) Values: `medium`, `high`, `critical`, `low`. |
| `vuln_class` | keyword | `k=v`, `k=a,b` | Vulnerability class (closed set of 17, model-assigned) Values: `remote_code_execution`, `xss`, `denial_of_service`, `information_disclosure`, `injection`, `memory_corruption`, `privilege_escalation`, `auth_bypass` …. |

Advanced filters (see `deepxiv fa spec cve`): `affected`, `cwe`, `kev_added`.

## Read

```bash
deepxiv fa read cve ID [ID...] [-l brief|detail|full] [-e EXTRA] [-p k=v]... [-f json|md|html]
```

| level | credits | returns |
|---|---|---|
| `brief` | 1 | Card: affected, cvss_score, doc_id, epss, kev, one_liner, one_liner_zh, published… |
| `detail` (default) | 2 | Every structured field (card plus the source abstract and detail fields) |

At `-l full`, `-p section=NAME` reads one section and `-p characters=N` the first N characters.

## Facets

`deepxiv fa facets cve FIELD` lists the legal values and counts, free. Use it instead of guessing a spelling. Fields: `severity`, `vuln_class`.

## Ask

```bash
deepxiv fa ask "question" -d cve [-e low|medium|high] [-p k=v]... [--no-stream] [--json]
```

Agentic Q&A over this domain: hybrid vector + lexical search (filters the vector layer lacks fall back to Postgres full text); the model reads the hits and answers with [cve:<doc_id> <title>] citations; /stream is NDJSON with real token deltas

Always pass `-d cve`: automatic domain picking is still early.

## What this corpus will and will not tell you

- NVD data is used under its terms: any display must carry the not-endorsed notice (see the attribution field).
- kev=true means CISA confirmed exploitation in the wild; epss is FIRST's probability estimate — different things.
- severity is derived from cvss_score; the 3,347 CVEs without a score have neither.
- Rank by exploitation risk with sort=epss, by time with sort=date.
- Two search paths: with a query, no sort and only filters the vector layer has (not affected / published / kev_added), search is hybrid vector + lexical, topped up from Postgres; otherwise, and with mode=keyword, it is Postgres full text (terms ANDed). Each hit's layer says which path.
- vuln_class / attacker_needs / impact / one_liner* are model-written — fine as a summary, not as a quote; the original text is description, in level=detail.
- Model-written fields (summarise, do not quote): affected, attacker_needs, impact, one_liner, one_liner_zh, vuln_class.
- The field table and enumerations are generated from the store's own self-description (search.field), not hand-written; enumeration counts are as of 2026-10-15.

## Citing

Cite records as `[CVE-2024-3400]`. Say plainly when the corpus has nothing.

---

Generated by `scripts/gen_fa_skills.py` from `deepxiv fa spec cve --json` on 2026-10-19. Field names and prices can change; `deepxiv fa spec cve` is the live source.
