---
name: deepxiv-fa-uk-eu-law
description: Search about 52k UK and EU legal instruments (EUR-Lex regulations, directives, decisions; UK Acts and SIs) with extracted obligations, penalties and summaries. Use when a task needs UK or EU legislation, e.g. GDPR articles.
---

# DeepXiv · UK & EU Law (`uk_eu_law`)

About 52k UK and EU legal instruments (synced daily; exact counts in corpus): about 42.4k EU (EUR-Lex — REG / REG_IMPL / DEC / DIR) plus about 9.3k UK (legislation.gov.uk — ukpga / asp / nia / asc / nisr / ssi / ukla; scanned-PDF-only items and pre-1837 items without text are excluded). Norm types (the same closed set as us_law), regulated parties, penalties, defined terms, deadlines, cross-references and bilingual summaries are model-extracted. Hybrid vector + lexical search; filters and sorting in Postgres.

Corpus: 51,737 documents.

## Setup

```bash
pip install -U deepxiv-sdk      # deepxiv registers a token on first use
```

With a registered key (https://data.rag.ac.cn/register), `search` and `read` are fair use: 60/min, 5 at once, 5,000/day; on the auto-registered token they spend the deepxiv daily limit at the credits listed below. `ask` draws on the daily ask allowance (resets 00:00 UTC; a site-wide daily total can run out early at peak times), or 3 lifetime trial asks on the auto-registered token. On 429, back off for `Retry-After` seconds. Data goes to stdout; cost, quota and sources go to stderr. Exit 0 ok, 1 API error, 2 usage error. The general CLI guide is the `deepxiv-cli` skill.

## Start here

```bash
deepxiv fa search uk_eu_law "data protection" -F jurisdiction=eu -k 5
deepxiv fa search uk_eu_law "artificial intelligence high-risk systems" -F kind=REG -F "year>=2020" -k 5
deepxiv fa read uk_eu_law eu:32016R0679 -l brief   # GDPR
deepxiv fa ask "Under the GDPR, when may personal data be transferred to a third country?" -d uk_eu_law
```

Free samples: ids `eu:32016R0679`; queries `data protection`.

## Search

```bash
deepxiv fa search uk_eu_law "query" [-F FILTER]... [-k N] [--offset N] [--mode M] [--sort S] [--head] [--json]
```

Modes: hybrid, dense, bm25, keyword. Up to 200 hits. Cost 2 (with `--head`: 3).
Sorts: `relevance`, `date` (default `relevance`).
An empty query is rejected; use `"*"` to list by filters only. Filters combine with AND; an undeclared field exits 2.

| filter | type | `-F` syntax | meaning |
|---|---|---|---|
| `date` | datetime | `k>=n`, `k=n..m` | Date adopted or signed, range |
| `jurisdiction` | keyword | `k=v`, `k=a,b` | uk (about 9.3k) or eu (about 42.4k) Values: `eu`, `uk`. |
| `kind` | keyword | `k=v`, `k=a,b` | Instrument type. EU: REG / REG_IMPL / DEC / DIR / DIR_IMPL. UK: ukpga (Act of Parliament) / asp (Scotland) / nia (Northern Ireland) / asc (Wales) / nisr / ssi / ukla Values: `REG`, `REG_IMPL`, `DEC`, `nisr`, `ukpga`, `DIR`, `asp`, `nia` …. |
| `norm_types` | keyword | `k=v`, `k=a,b` | Norm type (same closed set as us_law): obligation / prohibition / permission_or_authority / definition / procedure / penalty / effective_date_or_transition … (several allowed) |
| `status` | keyword | `k=v`, `k=a,b` | repealed means repealed (the title carries '(repealed)'); empty means in force or unknown. **EU instruments carry no status information — always empty** Values: `repealed`. |
| `year` | integer | `k>=n`, `k=n..m` | Year, range |

Advanced filters (see `deepxiv fa spec uk_eu_law`): `title`.

## Read

```bash
deepxiv fa read uk_eu_law ID [ID...] [-l brief|detail|full] [-e EXTRA] [-p k=v]... [-f json|md|html]
```

| level | credits | returns |
|---|---|---|
| `brief` | 1 | Card: citation, date, doc_id, jurisdiction, kind, norm_types, status, summary… |
| `detail` (default) | 2 | Every structured field (card plus the source abstract and detail fields) |

At `-l full`, `-p section=NAME` reads one section and `-p characters=N` the first N characters.

## Facets

`deepxiv fa facets uk_eu_law FIELD` lists the legal values and counts, free. Use it instead of guessing a spelling. Fields: `jurisdiction`, `kind`, `status`.

## Ask

```bash
deepxiv fa ask "question" -d uk_eu_law [-e low|medium|high] [-p k=v]... [--no-stream] [--json]
```

Agentic Q&A over this domain: hybrid vector + lexical search (filters the vector layer lacks fall back to Postgres full text); the model reads the hits and answers with [uk_eu_law:<doc_id> <title>] citations; /stream is NDJSON with real token deltas

Always pass `-d uk_eu_law`: automatic domain picking is still early.

## What this corpus will and will not tell you

- Division of labour with us_law: us_law holds **US** provisions in force (CFR / USC, clause level); uk_eu_law holds **UK statutes and EU instruments** (whole-instrument level). All three jurisdictions share one closed norm_types set, so 'find every data-protection instrument that carries penalties' is one question across domains.
- **The full text is not in Postgres**: path in level=detail points at the original on NAS, and source_url is the official link (EUR-Lex / legislation.gov.uk). So this domain has no level=full — fetch the text from source_url.
- summary_zh exists for about 92%; the other 8% have only the English summary. Both are model-written — not quotes.
- status is meaningful only for UK law (set when the title carries '(repealed)'); EU instruments are always empty, so do not filter EU material on status — it would exclude everything.
- subjects is an open model-generated label set and is not filterable before normalisation; filter on norm_types instead.
- Display requires attribution (see the attribution field): © European Union for the EU part, Open Government Licence v3.0 for the UK part.
- Two search paths: with a query, no sort and only filters the vector layer has (not date / title), search is hybrid vector + lexical (semantic recall, terms need not all match), topped up from Postgres; otherwise (sort given, date / title used, or mode=keyword) it runs in Postgres as an English tsvector and a Chinese zhparser pass whose results are unioned — quoted phrases / OR / -exclusion work, and **terms are ANDed**, so prefer fewer terms plus filters. Each hit's layer says which layer it came from.
- Model-written fields (summarise, do not quote): cross_references, deadlines, defined_terms, norm_types, penalties, regulated_parties, subjects, summary, summary_zh.
- The field table and enumerations are generated from the store's own self-description (search.field), not hand-written; enumeration counts are as of 2026-10-15.

## Citing

Cite records as `[CELEX 32016R0679]`. Say plainly when the corpus has nothing.

---

Generated by `scripts/gen_fa_skills.py` from `deepxiv fa spec uk_eu_law --json` on 2026-10-19. Field names and prices can change; `deepxiv fa spec uk_eu_law` is the live source.
