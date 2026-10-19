---
name: deepxiv-fa-cases
description: Search Chinese and US court judgments (17M+ Chinese, 3.4M US) and read their extracted fields: claims, facts, reasoning, outcome, legal basis, sentencing. Use when a task needs how courts ruled on similar facts, or a specific case by number or name.
---

# DeepXiv · Law · Judgments (`cases`)

Court judgments: 17.49M from China (2.65M criminal plus 14.83M civil / administrative / enforcement) and 3.44M US opinions (country=us, tier A). Brief-level hybrid retrieval with LLM-extracted structured fields. Chinese judgment text needs the cases:fulltext grant (the originals carry personal data); US full text waits on the PG store.

Corpus: 27,580,773 documents.

## Setup

```bash
pip install -U deepxiv-sdk      # deepxiv registers a token on first use
```

`search` and `read` spend the deepxiv daily limit at the credits listed below. `ask` spends the agentic quota: a registered key from https://data.rag.ac.cn/register (300/day), or 3 lifetime trial asks on the auto-registered token. Data goes to stdout; cost, quota and sources go to stderr. Exit 0 ok, 1 API error, 2 usage error. The general CLI guide is the `deepxiv-cli` skill.

## Start here

```bash
deepxiv fa search cases "网络刷单诈骗 未遂" -F province=浙江省 -F "judge_year>=2018" -k 5
deepxiv fa search cases "qualified immunity police" -F country=us -F court_level=scotus -k 5   # US cases filter on year, not judge_year
deepxiv fa read cases us:10316651 -l brief   # TikTok v. Garland; the holding comes in English and Chinese
deepxiv fa read cases 8a1c3791-0cce-4094-9b28-a9a600b657c7   # detail: every extracted field, no grant needed
deepxiv fa ask "网络刷单诈骗未遂一般怎么判" -d cases   # answers from Chinese judgments only
```

Free samples: ids `8a1c3791-0cce-4094-9b28-a9a600b657c7`, `us:577203`; queries `网络刷单诈骗 未遂`.

## Search

```bash
deepxiv fa search cases "query" [-F FILTER]... [-k N] [--offset N] [--mode M] [--head] [--json]
```

Modes: hybrid, dense, bm25. Up to 100 hits. Cost 2 (with `--head`: 3).
An empty query is rejected; use `"*"` to list by filters only. Filters combine with AND; an undeclared field exits 2.

| filter | type | `-F` syntax | meaning |
|---|---|---|---|
| `country` | keyword | `k=v` | cn (default, Chinese judgments) / us (US opinions). The two have different fields: filters marked (country=us) apply to US only, the rest to China only Values: `cn`, `us`. |
| `nature` | keyword | `k=v` | criminal / civil / all (default all; country=cn only) Values: `criminal`, `civil`, `all`. |
| `cause` | keyword | `k=v`, `k=a,b` | Cause of action / crime, exact match (see facets) |
| `province` | keyword | `k=v`, `k=a,b` | Province |
| `judge_year` | integer | `k>=n`, `k=n..m` | Decision year range |
| `law_refs` | keyword | `k=v`, `k=a,b` | Cited article key, e.g. CN/刑法/266 |
| `verdictno` | keyword | `k=v`, `k=a,b` | Exact case number (country=cn). Use this filter rather than the query text: the Postgres layer tokenises Chinese only |
| `articles` | keyword | `k=v`, `k=a,b` | Cited provision, to the article (country=cn; full law name + Chinese article number) |
| `amount_max` | integer | `k>=n`, `k=n..m` | Largest amount in the judgment, range (country=cn, CNY) |
| `year` | integer | `k=v`, `k>=n`, `k=n..m` | Decision year, range (country=us) |
| `proceeding_type` | keyword | `k=v`, `k=a,b` | Proceeding type (country=us) Values: `civil`, `criminal`, `administrative`, `bankruptcy`, `habeas_or_post_conviction`, `attorney_discipline`, `juvenile`, `other`. |
| `subject_areas` | keyword | `k=v`, `k=a,b` | Subject area (country=us, closed set of 23) |
| `disposition` | keyword | `k=v`, `k=a,b` | Disposition (country=us, closed set of 12) Values: `affirmed`, `affirmed_in_part`, `reversed`, `reversed_and_remanded`, `vacated`, `vacated_and_remanded`, `remanded`, `granted` …. |
| `prevailing_party` | keyword | `k=v`, `k=a,b` | Prevailing party (country=us) Values: `appellant_or_plaintiff`, `appellee_or_defendant`, `mixed`, `unclear`. |
| `precedential_status` | keyword | `k=v`, `k=a,b` | Precedential status (country=us) Values: `Published`, `Unpublished`, `Relating-to`, `Separate`, `In-chambers`, `Errata`, `Unknown`. |
| `cite_count` | integer | `k=v`, `k>=n`, `k=n..m` | Citation count, range (country=us) |

Advanced filters (see `deepxiv fa spec cases`): `city`, `court_level`, `trial_round`, `decided_at`, `laws`, `sentence_type`, `sentence_months`, `probation`, `fine_amount`, `law_names`, `org_parties`, `status`, `district`, `circumstance_tags`, `procedural_posture`, `court_id`, `docket_number`, `statutes_cited`, `issue_tags`, `party_names`, `standard_of_review`, `holding_by`, `citation_norm`, `tier`, `jurisdiction`.

## Read

```bash
deepxiv fa read cases ID [ID...] [-l brief|detail|full] [-e EXTRA] [-p k=v]... [-f json|md|html]
```

| level | credits | returns |
|---|---|---|
| `brief` | 1 | Card (~150 tok): case number, cause, court, level, date, one-line summary, disputed issues, cited articles, sentencing |
| `detail` (default) | 2 | Every structured field (~500 tok): claims, disputed issues, facts, circumstances, reasoning, outcome, parties, articles, amounts |
| `full` | 5 | Full text (mean 2.5k chars, p95 5.5k). Needs the cases:fulltext grant **Needs the `cases:fulltext` grant on the key** (403 otherwise, not charged). |

| `-e` extra | credits | returns |
|---|---|---|
| `laws` | 2 | Articles the judgment cites, with readable law links |

At `-l full`, `-p section=NAME` reads one section and `-p characters=N` the first N characters.

## Facets

`deepxiv fa facets cases FIELD` lists the legal values and counts, free. Use it instead of guessing a spelling. Fields: `cause`, `province`, `court_level`, `trial_round`, `sentence_type`, `circumstance_tags`, `proceeding_type`, `subject_areas`, `disposition`, `prevailing_party`, `precedential_status`, `procedural_posture`.

## Ask

```bash
deepxiv fa ask "question" -d cases [-e low|medium|high] [-p k=v]... [--no-stream] [--json]
```

Q&A over judgments: served by the same agent as the law domain (which already combines 'find the governing articles, then see how comparable judgments ruled'); scope defaults to case, i.e. judgments only. Answers cite [case number], with sources.cases / coverage as in law

Always pass `-d cases`: automatic domain picking is still early.

| `-p` param | type | meaning |
|---|---|---|
| `scope` | auto/law/case/both | judgments only (default) / statutes too |

## What this corpus will and will not tell you

- China: 2.65M criminal judgments fully extracted, mostly 2014–2019 (2020–2021 nearly empty); 14.83M civil / administrative / enforcement judgments finished ingesting on 2026-10-07. US (country=us): tier A only (3.44M); the ~6.63M tier-B long tail is not indexed. Every response carries coverage.
- A case number in the query resolves exactly first.
- Chinese judgment text is not served by default: the original documents carry party names, dates of birth and home addresses, so this API exposes only the parsed layer (level=brief / detail). level=full / section / preview need an API key carrying the cases:fulltext grant — without it the call is a 403 and costs nothing.
- At level=brief / detail the verdict, sentence, facts and reasoning are all model extractions (sentencing is derived from the verdict by regex); cite the official Chinese judgment site for anything formal.
- country=us ids look like us:577203 — reading one needs no country parameter; full text (level=full / section / preview) is not available yet, pending the move of the opinion store into PG.
- US holdings, issues and dispositions are model-extracted; cite CourtListener for anything formal.
- Ask goes through /v1/law/ask (scope=case, Chinese judgments only for now).

## Limits

- Grant `cases:fulltext`: Verbatim text of Chinese judgments (whole, by section, or first N characters). Off by default: the originals carry party names, dates of birth and home addresses (58% of a 400-judgment sample had an unmasked name). level=detail already has every extracted field. Issued on request, not self-serve.

## Citing

Cite records as `[（2018）闽0181刑初1319号]`. Say plainly when the corpus has nothing.

---

Generated by `scripts/gen_fa_skills.py` from `deepxiv fa spec cases --json` on 2026-10-19. Field names and prices can change; `deepxiv fa spec cases` is the live source.
