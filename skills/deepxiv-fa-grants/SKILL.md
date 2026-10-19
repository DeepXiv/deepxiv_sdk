---
name: deepxiv-fa-grants
description: Search ~1.3M research grants: NSF awards, NIH projects and EU CORDIS projects, with amounts, PIs, organisations and topics. Use when a task needs who funds what, funding trends, or a PI's awards.
---

# DeepXiv · Grants (`grants`)

~1.31M research awards: ~637k NSF awards (one per award id), ~570k NIH RePORTER projects (multi-year funding merged per core project number, with per-year amounts) and ~107k EU CORDIS projects (FP5 to Horizon Europe, amounts in EUR). Synced daily; exact counts are in corpus (live). Organisation / country / PI / directorate / activity code / dates / amounts come from the source; topics, methods, domain and one-line summaries are model-generated (title-only where no abstract exists — see _enrich.basis).

Corpus: 1,313,241 documents, updated 2026-10.

## Setup

```bash
pip install -U deepxiv-sdk      # deepxiv registers a token on first use
```

`search` and `read` spend the deepxiv daily limit at the credits listed below. `ask` spends the agentic quota: a registered key from https://data.rag.ac.cn/register (300/day), or 3 lifetime trial asks on the auto-registered token. Data goes to stdout; cost, quota and sources go to stderr. Exit 0 ok, 1 API error, 2 usage error. The general CLI guide is the `deepxiv-cli` skill.

## Start here

```bash
deepxiv fa search grants "single-cell transcriptomics" -F agency=nih -F "fy>=2020" -k 5
deepxiv fa search grants "quantum computing" -F agency=nsf -F "amount_total>=1000000" -k 5
deepxiv fa read grants nih:R25HG007515 -l brief
deepxiv fa ask "Which NIH institutes fund single-cell atlas projects, and how much?" -d grants
```

Free samples: ids `nih:R25HG007515`; queries `single cell transcriptomics`.

## Search

```bash
deepxiv fa search grants "query" [-F FILTER]... [-k N] [--offset N] [--mode M] [--head] [--json]
```

Modes: hybrid, dense, bm25. Up to 100 hits. Cost 2 (with `--head`: 3).
An empty query is rejected; use `"*"` to list by filters only. Filters combine with AND; an undeclared field exits 2.

| filter | type | `-F` syntax | meaning |
|---|---|---|---|
| `agency` | keyword | `k=v`, `k=a,b` | Funding agency Values: `nih`, `nsf`, `cordis`. |
| `research_domain` | keyword | `k=v`, `k=a,b` | Research domain (model-assigned, closed set of 13) Values: `biomedical`, `life_sciences`, `clinical`, `public_health`, `engineering`, `physical_sciences`, `chemistry`, `math_stats` …. |
| `ic_or_directorate` | keyword | `k=v`, `k=a,b` | NIH institute, NSF directorate or CORDIS framework programme (FP7 / H2020 / HORIZON …, see facets) |
| `activity_code` | keyword | `k=v`, `k=a,b` | Funding mechanism: NIH activity code (R01 / R21 / F32 …), NSF award type or CORDIS funding scheme |
| `fy` | integer | `k=v`, `k>=n`, `k=n..m` | Fiscal year, range |
| `start_year` | integer | `k=v`, `k>=n`, `k=n..m` | Project start year, range |
| `end_year` | integer | `k=v`, `k>=n`, `k=n..m` | Project end year, range |
| `amount_total` | number | `k=v`, `k>=n`, `k=n..m` | Total amount, range (USD for NIH / NSF; EU contribution in EUR for CORDIS — pair with agency when filtering across agencies) |
| `org_country` | keyword | `k=v`, `k=a,b` | Organisation country (source casing is inconsistent — see notes) |

Advanced filters (see `deepxiv fa spec grants`): `org_state`, `org_name`, `pi_names`, `topics`, `programs`, `core_project_num`, `is_renewal`.

## Read

```bash
deepxiv fa read grants ID [ID...] [-l brief|detail|full] [-e EXTRA] [-p k=v]... [-f json|md|html]
```

| level | credits | returns |
|---|---|---|
| `brief` | 1 | Card: the fields needed to triage, same as in search hits |
| `detail` (default) | 2 | Every structured field (rule-derived plus model-generated; model fields are listed in _enrich.fields) |
| `full` | 5 | Full text (not available yet: abstracts are already in level=detail; progress reports and publications are not in this corpus) |

At `-l full`, `-p section=NAME` reads one section and `-p characters=N` the first N characters.

## Facets

`deepxiv fa facets grants FIELD` lists the legal values and counts, free. Use it instead of guessing a spelling. Fields: `agency`, `research_domain`, `ic_or_directorate`, `activity_code`, `org_country`, `org_state`.

## Ask

```bash
deepxiv fa ask "question" -d grants [-e low|medium|high] [-p k=v]... [--no-stream] [--json]
```

Agentic Q&A over this domain: the model turns the question into filters plus keywords from the domain's own self-description, reads the hits and answers with [grants:<grant_id> <title>] citations; /stream is NDJSON with real token deltas

Always pass `-d grants`: automatic domain picking is still early.

## What this corpus will and will not tell you

- One NIH document = all yearly awards under a core project number (amount_total is the sum, funding_by_year the breakdown); one NSF document = one award; one CORDIS document = one project (grant_id = cordis:<project id>), org_* is the coordinator and amount_total the EU contribution in EUR (currency=EUR at level=head; NIH / NSF have no currency field and are in USD).
- org_country casing is inconsistent in the source (both UNITED STATES and United States, 1.088M awards) — pass both spellings.
- `topics` are open labels with tens of thousands of values: good to read, poor to filter on — use research_domain.
- Where no abstract exists the summary comes from the title alone (_enrich.basis=title_only).
- The index holds no full text: level=full is not available yet (abstracts are already in level=detail; progress reports and publications are not in this corpus).

## Citing

Cite records as `[NIH R25HG007515]`. Say plainly when the corpus has nothing.

---

Generated by `scripts/gen_fa_skills.py` from `deepxiv fa spec grants --json` on 2026-10-19. Field names and prices can change; `deepxiv fa spec grants` is the live source.
