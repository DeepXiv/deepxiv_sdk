---
name: deepxiv-fa-fr
description: Search 1.0M US Federal Register documents (1994–): rules, proposed rules, notices, presidential documents, with agencies, action kind and dates. Use when a task needs what a US agency published or proposed.
---

# DeepXiv · Federal Register (`fr`)

1.0M Federal Register documents (1994– ): rules, proposed rules, notices and presidential documents. Action kind (closed set of 19), issuing agencies, affected parties, effective and comment-close dates and one-line summaries are model-extracted. No vectors: structured filters plus bilingual full-text search in Postgres.

Corpus: 1,008,597 documents.

## Setup

```bash
pip install -U deepxiv-sdk      # deepxiv registers a token on first use
```

With a registered key (https://data.rag.ac.cn/register), `search` and `read` are fair use: 60/min, 5 at once, 5,000/day; on the auto-registered token they spend the deepxiv daily limit at the credits listed below. `ask` draws on the daily ask allowance (resets 00:00 UTC; a site-wide daily total can run out early at peak times), or 3 lifetime trial asks on the auto-registered token. On 429, back off for `Retry-After` seconds. Data goes to stdout; cost, quota and sources go to stderr. Exit 0 ok, 1 API error, 2 usage error. The general CLI guide is the `deepxiv-cli` skill.

## Start here

```bash
deepxiv fa search fr "PFAS drinking water" -F doc_type=Rule -k 5
deepxiv fa search fr "artificial intelligence" -F doc_type="Proposed Rule" -F "pub_date>=2024-01-01" --sort pub_date -k 5
deepxiv fa read fr fr:2024-07332 -l brief
deepxiv fa ask "What did EPA finalize on PFAS in drinking water?" -d fr
```

Free samples: ids `fr:2024-07332`; queries `PFAS drinking water`.

## Search

```bash
deepxiv fa search fr "query" [-F FILTER]... [-k N] [--offset N] [--mode M] [--sort S] [--head] [--json]
```

Modes: keyword. Up to 200 hits. Cost 2 (with `--head`: 3).
Sorts: `relevance`, `date`, `pub_date` (default `relevance`).
An empty query is rejected; use `"*"` to list by filters only. Filters combine with AND; an undeclared field exits 2.

| filter | type | `-F` syntax | meaning |
|---|---|---|---|
| `action_kind` | keyword | `k=v`, `k=a,b` | Action kind (closed set of 19, model-assigned) Values: `information_collection`, `meeting_or_hearing`, `amendment`, `approval_or_authorization`, `determination_or_finding`, `other`, `new_requirement`, `petition_or_request` …. |
| `agencies` | keyword | `k=v`, `k=a,b` | Issuing agencies (several allowed, any match) |
| `doc_type` | keyword | `k=v`, `k=a,b` | Document type (official capitalisation: Rule / Proposed Rule / Notice / Presidential Document …) Values: `Notice`, `Rule`, `Proposed Rule`, `Uncategorized Document`, `Presidential Document`, `Correction`, `Sunshine Act Document`. |
| `pub_date` | datetime | `k>=n`, `k=n..m` | Publication date range |

Advanced filters (see `deepxiv fa spec fr`): `norm_tags`, `cfr_refs`, `comments_close_on`, `docket_ids`, `document_number`, `effective_on`, `fr_topics`, `rins`, `significant`.

## Read

```bash
deepxiv fa read fr ID [ID...] [-l brief|detail|full] [-e EXTRA] [-p k=v]... [-f json|md|html]
```

| level | credits | returns |
|---|---|---|
| `brief` | 1 | Card: action_kind, agencies, citation, doc_id, doc_type, html_url, norm_tags, one_liner… |
| `detail` (default) | 2 | Every structured field (card plus the source abstract and detail fields) |

At `-l full`, `-p section=NAME` reads one section and `-p characters=N` the first N characters.

## Facets

`deepxiv fa facets fr FIELD` lists the legal values and counts, free. Use it instead of guessing a spelling. Fields: `action_kind`, `doc_type`.

## Ask

```bash
deepxiv fa ask "question" -d fr [-e low|medium|high] [-p k=v]... [--no-stream] [--json]
```

Agentic Q&A over this domain: with no vector layer, the model turns the question into structured filters plus bilingual full-text search; the model reads the hits and answers with [fr:<doc_id> <title>] citations; /stream is NDJSON with real token deltas

Always pass `-d fr`: automatic domain picking is still early.

## What this corpus will and will not tell you

- Division of labour with us_law: us_law holds the provisions in force (clause-level CFR / USC); fr holds the notices themselves (who changed what, when).
- doc_type uses the official capitalisation (Rule / Proposed Rule / Notice / Presidential Document / Uncategorized Document / Correction / Sunshine Act Document); lowercase 'rule' matches nothing.
- Rules open for comment: filters.comments_close_on={"gte": "<today>"}; upcoming effect: a range on effective_on.
- subjects is an open model-generated label set and is not filterable before normalisation — filter on fr_topics (the official topics) instead.
- No vectors: the query runs as an English tsvector and a Chinese zhparser pass whose results are unioned; mixed queries are split automatically, and quoted phrases / OR / -exclusion work.
- Model-written fields (summarise, do not quote): action_kind, affected, key_point, norm_tags, one_liner, one_liner_zh, subjects.
- The field table and enumerations are generated from the store's own self-description (search.field), not hand-written; enumeration counts are as of 2026-10-15.

## Citing

Cite records as `[89 FR 12345]`. Say plainly when the corpus has nothing.

---

Generated by `scripts/gen_fa_skills.py` from `deepxiv fa spec fr --json` on 2026-10-19. Field names and prices can change; `deepxiv fa spec fr` is the live source.
