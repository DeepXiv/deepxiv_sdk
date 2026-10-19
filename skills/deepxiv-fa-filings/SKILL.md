---
name: deepxiv-fa-filings
description: Search ~1.3M US and Chinese corporate filings: SEC 8-K / 10-K / 10-Q / 13D / proxy / comment letters, Chinese periodic reports and announcements, exchange inquiries and CSRC penalties. Use when a task needs what a company disclosed.
---

# DeepXiv · Filings (`filings`)

~1.32M corporate filings and regulatory documents across US and China; the vector layer and the Postgres layer are kept in sync (semantic plus lexical): ~395k EDGAR 8-K events, 154k 6-K, 188k 13D/13G ownership filings, 47k structured 10-K/20-F, 105k 10-Q quarterlies, 32k DEF 14A, 28k Form 425, 7k S-1, 89k SEC comment-letter documents (CORRESP and UPLOAD), 119k Chinese periodic reports, 142k Chinese interim announcements, 10k exchange inquiry letters and discipline decisions, 2.4k CSRC penalty decisions (measured 10-15; Synced daily; exact counts are in corpus (live) — per-source counts in corpus.sources). **Default search excludes 10-Q** (numerous and topically similar, they would crowd out everything else); filter on form or doc_family to include them (e.g. form=10-Q, doc_family=periodic). One-liners, counterparties, amounts, MD&A drivers, inquiry points and violation types are model-extracted; company name / tickers / SIC come from EDGAR submissions.

Corpus: 1,318,627 documents, updated 2026-10.

## Setup

```bash
pip install -U deepxiv-sdk      # deepxiv registers a token on first use
```

`search` and `read` spend the deepxiv daily limit at the credits listed below. `ask` spends the agentic quota: a registered key from https://data.rag.ac.cn/register (300/day), or 3 lifetime trial asks on the auto-registered token. Data goes to stdout; cost, quota and sources go to stderr. Exit 0 ok, 1 API error, 2 usage error. The general CLI guide is the `deepxiv-cli` skill.

## Start here

```bash
deepxiv fa search filings "CEO resignation" -F market=us -F event_types=officer_director_change -F "filed_year>=2023" -k 5
deepxiv fa search filings "*" -F form=10-Q -F cik=320193 --sort date -k 4   # 10-Q is excluded unless you filter on it
deepxiv fa read filings us:861838:0001104659-23-092550 -l brief
deepxiv fa ask "Which US companies disclosed a CEO departure in 2024 and why?" -d filings
```

Free samples: ids `us:861838:0001104659-23-092550`; queries `CEO resignation`.

## Search

```bash
deepxiv fa search filings "query" [-F FILTER]... [-k N] [--offset N] [--mode M] [--sort S] [--head] [--json]
```

Modes: hybrid, dense, bm25. Up to 100 hits. Cost 2 (with `--head`: 3).
Sorts: `relevance`, `date` (default `relevance`).
An empty query is rejected; use `"*"` to list by filters only. Filters combine with AND; an undeclared field exits 2.

| filter | type | `-F` syntax | meaning |
|---|---|---|---|
| `market` | keyword | `k=v` | Market Values: `us`, `cn`. |
| `doc_family` | keyword | `k=v`, `k=a,b` | Document family Values: `event`, `periodic`, `inquiry_letter`, `discipline`, `penalty`, `registration`, `ownership`, `proxy` …. |
| `form` | keyword | `k=v`, `k=a,b` | Form / document type, values and counts in facets. Default search excludes 10-Q; filtering on form (or doc_family) includes it Values: `8-K`, `6-K`, `临时公告`, `10-Q`, `SC 13G/A`, `CORRESP`, `10-K`, `UPLOAD` …. |
| `filed_at` | datetime | `k>=n`, `k=n..m` | Filing date range (day precision; Postgres layer only, so it routes the query there) |
| `filed_year` | integer | `k=v`, `k>=n`, `k=n..m` | Filing year, range |
| `fiscal_year` | integer | `k=v`, `k>=n`, `k=n..m` | Fiscal year, range |
| `event_types` | keyword | `k=v`, `k=a,b` | 8-K event type (closed set, see facets) |
| `report_kind` | keyword | `k=v`, `k=a,b` | Periodic report kind Values: `annual`, `semi`, `q1`, `q3`. |

Advanced filters (see `deepxiv fa spec filings`): `items`, `sic`, `letter_kind`, `exchange`, `issue_categories`, `violation_types`, `company_name`, `cik`, `sec_code`, `tickers`, `counterparties`, `risk_categories`, `party_names`, `has_reply`, `has_ban`.

## Read

```bash
deepxiv fa read filings ID [ID...] [-l brief|detail|full] [-e EXTRA] [-p k=v]... [-f json|md|html]
```

| level | credits | returns |
|---|---|---|
| `brief` | 1 | Card: the fields needed to triage, same as in search hits |
| `detail` (default) | 2 | Every structured field (rule-derived plus model-generated; model fields are listed in _enrich.fields) |
| `full` | 5 | Full text (not available yet: source documents are on NAS (raw_path); neither layer holds the body text, only structured highlights) |

At `-l full`, `-p section=NAME` reads one section and `-p characters=N` the first N characters.

## Facets

`deepxiv fa facets filings FIELD` lists the legal values and counts, free. Use it instead of guessing a spelling. Fields: `market`, `doc_family`, `form`, `event_types`, `report_kind`, `letter_kind`, `exchange`, `issue_categories`, `violation_types`, `sic`.

## Ask

```bash
deepxiv fa ask "question" -d filings [-e low|medium|high] [-p k=v]... [--no-stream] [--json]
```

Agentic Q&A over this domain: the model turns the question into filters plus keywords from the domain's own self-description, reads the hits and answers with [filings:<doc_id> <title>] citations; /stream is NDJSON with real token deltas

Always pass `-d filings`: automatic domain picking is still early.

## What this corpus will and will not tell you

- Fields differ by doc_family: event (8-K) has items / event_types / counterparties / amounts; periodic has main_business / segments / key_numbers; 10-Q quarterlies have mdna_drivers / liquidity / legal_updates / new_or_changed_risks / outlook; inquiry_letter has issues / deadline / has_reply; penalty has violation_types / facts / legal_basis / parties. Filter by doc_family before reading fields.
- The ~105k 10-Q quarterlies are in the vector layer but **excluded from default search**: with no form / doc_family filter the results contain no 10-Q. To search quarterlies, filter form=10-Q (semantic search) or doc_family=periodic (ranked together with 10-K, 20-F and Chinese periodic reports).
- Sorting (sort=date) and day-precision filed_at ranges exist only in the Postgres layer: either one routes the whole query there (lexical search), and that path does not apply the 10-Q exclusion (a company's filings listed by date should include its quarterlies). Every hit is tagged with its layer and the response says which layer answered.
- Lexical search in the Postgres layer also matches model-written retrieval keywords (kw_en / kw_zh, folded into the full-text index), so a Chinese query such as 持续经营 finds English going-concern language and synonyms absent from the source text. The trade-off: the score includes that contribution and the response does not distinguish a source-text match from a keyword-only match. The keywords themselves are not returned (the store marks them recall-only).
- Financial statements from 10-K / 20-F / 10-Q are not here — use XBRL; this corpus carries structured highlights only.
- Source documents are on NAS (raw_path in level=detail); the index holds no full text.
- The index holds no full text: level=full is not available yet (source documents are on NAS (raw_path); neither layer holds the body text, only structured highlights).

## Citing

Cite records as `[8-K 0001104659-23-092550]`. Say plainly when the corpus has nothing.

---

Generated by `scripts/gen_fa_skills.py` from `deepxiv fa spec filings --json` on 2026-10-19. Field names and prices can change; `deepxiv fa spec filings` is the live source.
