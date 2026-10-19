---
name: deepxiv-fa-us-law
description: Search ~5M US legal provisions: federal and state statutes, regulations (CFR), session laws, agency decisions, guidance. Use when a task needs the text of a US law or rule, or obligations and penalties under it.
---

# DeepXiv · US Law (`us_law`)

~5M clause-level US legal provisions across 53 jurisdictions (synced daily since 10-15 as new eCFR and other text arrives; exact count in corpus). The open_us_law v2026.08 base: 2.12M statutes, 1.95M regulations (including CFR annual editions), 425k session laws, 258k agency decisions, 77k proposed regulations, 77k guidance documents, 53k court rules, 13k constitutional provisions. English and Chinese summaries, norm types, regulated parties, subjects, defined terms, penalties, deadlines and cross-references are extracted per provision (citations and figures checked against the text).

Corpus: 5,195,942 documents, updated 2026-08.

## Setup

```bash
pip install -U deepxiv-sdk      # deepxiv registers a token on first use
```

With a registered key (https://data.rag.ac.cn/register), `search` and `read` are fair use: 60/min, 5 at once, 5,000/day; on the auto-registered token they spend the deepxiv daily limit at the credits listed below. `ask` draws on the daily ask allowance (resets 00:00 UTC; a site-wide daily total can run out early at peak times), or 3 lifetime trial asks on the auto-registered token. On 429, back off for `Retry-After` seconds. Data goes to stdout; cost, quota and sources go to stderr. Exit 0 ok, 1 API error, 2 usage error. The general CLI guide is the `deepxiv-cli` skill.

## Start here

```bash
deepxiv fa search us_law "data breach notification" -F jurisdiction=ca,ny -k 5
deepxiv fa search us_law "foreign adversary sensitive personal data transfer" -k 3
deepxiv fa search us_law "HIPAA patient records disclosure" -F doc_group=regulation -F has_penalty=true -k 5
deepxiv fa read us_law uslaw:USC_T15_C123_S9901 -l brief   # 15 U.S.C. § 9901
deepxiv fa ask "What must a company do after a data breach under California law?" -d us_law
```

Free samples: ids `uslaw:CFRANN_2024_T42_P2_S2_33`; queries `HIPAA patient records disclosure`.

## Search

```bash
deepxiv fa search us_law "query" [-F FILTER]... [-k N] [--offset N] [--mode M] [--head] [--json]
```

Modes: hybrid, dense, bm25. Up to 100 hits. Cost 2 (with `--head`: 3).
An empty query is rejected; use `"*"` to list by filters only. Filters combine with AND; an undeclared field exits 2.

| filter | type | `-F` syntax | meaning |
|---|---|---|---|
| `jurisdiction` | keyword | `k=v`, `k=a,b` | Jurisdiction: federal or a two-letter state code (53 in all) |
| `is_federal` | bool | `k=v` | Federal |
| `doc_group` | keyword | `k=v`, `k=a,b` | Document group Values: `statute`, `regulation`, `session_law`, `decision`, `proposed_regulation`, `guidance`, `court_rule`, `constitution` …. |
| `kind` | keyword | `k=v`, `k=a,b` | Specific kind (see facets) |
| `status` | keyword | `k=v`, `k=a,b` | Status Values: `in_force`, `superseded`, `enacted`, `repealed`, `proposed`, `reserved`, `transferred`, `rescinded` …. |
| `norm_types` | keyword | `k=v`, `k=a,b` | Norm type (closed set of 15, model-assigned) Values: `obligation`, `prohibition`, `permission_or_authority`, `definition`, `procedure`, `eligibility_or_criteria`, `reporting_or_recordkeeping`, `penalty` …. |
| `has_penalty` | bool | `k=v` | Carries a penalty |

Advanced filters (see `deepxiv fa spec us_law`): `penalty_types`, `citation`, `subjects`, `defined_terms`, `regulated_parties`.

## Read

```bash
deepxiv fa read us_law ID [ID...] [-l brief|detail|full] [-e EXTRA] [-p k=v]... [-f json|md|html]
```

| level | credits | returns |
|---|---|---|
| `brief` | 1 | Card: the fields needed to triage, same as in search hits |
| `detail` (default) | 2 | Every structured field (rule-derived plus model-generated; model fields are listed in _enrich.fields) |
| `full` | 5 | Full text (not available yet: the provision text lives on NAS (open_us_law); the index carries the summary plus an excerpt) |

At `-l full`, `-p section=NAME` reads one section and `-p characters=N` the first N characters.

## Facets

`deepxiv fa facets us_law FIELD` lists the legal values and counts, free. Use it instead of guessing a spelling. Fields: `jurisdiction`, `doc_group`, `kind`, `status`, `norm_types`, `penalty_types`.

## Ask

```bash
deepxiv fa ask "question" -d us_law [-e low|medium|high] [-p k=v]... [--no-stream] [--json]
```

Agentic Q&A over this domain: the model turns the question into filters plus keywords from the domain's own self-description, reads the hits and answers with [us_law:<law_id> <title>] citations; /stream is NDJSON with real token deltas

Always pass `-d us_law`: automatic domain picking is still early.

## What this corpus will and will not tell you

- Licence: CC BY 4.0 (open_us_law) — attribution required when displaying or redistributing.
- One document = one section / provision, not a whole act. The `excerpt` in level=detail is a snippet, not the full text.
- 928k provisions are status=superseded (mostly historical CFR annual editions) — filter status=in_force before citing.
- Summaries, norm types and subjects are model-generated; citations and figures were checked against the text, but cite the source for anything formal.
- `subjects` is an open label set (39k values): good to read, poor to filter on.
- The index holds no full text: level=full is not available yet (the provision text lives on NAS (open_us_law); the index carries the summary plus an excerpt).

## Citing

Cite records as `[42 C.F.R. § 2.33]`. Say plainly when the corpus has nothing.

---

Generated by `scripts/gen_fa_skills.py` from `deepxiv fa spec us_law --json` on 2026-10-19. Field names and prices can change; `deepxiv fa spec us_law` is the live source.
