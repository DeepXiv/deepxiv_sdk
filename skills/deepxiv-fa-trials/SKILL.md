---
name: deepxiv-fa-trials
description: Search all ~607k ClinicalTrials.gov studies by condition, phase, status, sponsor, country, with eligibility and biomarkers extracted. Use when a task needs clinical trials for a drug, disease or target.
---

# DeepXiv · Trials (`trials`)

All ~607k studies on ClinicalTrials.gov (one per NCT; Synced daily; exact counts are in corpus (live)). Phase / status / enrolment / countries / MeSH come from the ctgov record; eligibility highlights, biomarkers, prior therapy, ECOG and one-line summaries are model-extracted.

Corpus: 607,168 documents, updated 2026-10.

## Setup

```bash
pip install -U deepxiv-sdk      # deepxiv registers a token on first use
```

With a registered key (https://data.rag.ac.cn/register), `search` and `read` are fair use: 60/min, 5 at once, 5,000/day; on the auto-registered token they spend the deepxiv daily limit at the credits listed below. `ask` draws on the daily ask allowance (resets 00:00 UTC; a site-wide daily total can run out early at peak times), or 3 lifetime trial asks on the auto-registered token. On 429, back off for `Retry-After` seconds. Data goes to stdout; cost, quota and sources go to stderr. Exit 0 ok, 1 API error, 2 usage error. The general CLI guide is the `deepxiv-cli` skill.

## Start here

```bash
deepxiv fa search trials "GLP-1 obesity" -F phase=PHASE3 -F overall_status=RECRUITING -k 5
deepxiv fa read trials NCT02082496 -l brief
deepxiv fa ask "recruiting phase 3 trials for pancreatic cancer" -d trials
```

Free samples: ids `NCT02082496`; queries `glp-1 obesity phase 3`.

## Search

```bash
deepxiv fa search trials "query" [-F FILTER]... [-k N] [--offset N] [--mode M] [--head] [--json]
```

Modes: hybrid, dense, bm25. Up to 100 hits. Cost 2 (with `--head`: 3).
An empty query is rejected; use `"*"` to list by filters only. Filters combine with AND; an undeclared field exits 2.

| filter | type | `-F` syntax | meaning |
|---|---|---|---|
| `phase` | keyword | `k=v`, `k=a,b` | Trial phase Values: `EARLY_PHASE1`, `PHASE1`, `PHASE2`, `PHASE3`, `PHASE4`, `NA`. |
| `overall_status` | keyword | `k=v`, `k=a,b` | Recruitment status Values: `RECRUITING`, `NOT_YET_RECRUITING`, `ACTIVE_NOT_RECRUITING`, `ENROLLING_BY_INVITATION`, `COMPLETED`, `TERMINATED`, `WITHDRAWN`, `SUSPENDED` …. |
| `study_type` | keyword | `k=v`, `k=a,b` | Study type Values: `INTERVENTIONAL`, `OBSERVATIONAL`, `EXPANDED_ACCESS`. |
| `intervention_type` | keyword | `k=v`, `k=a,b` | Intervention type Values: `DRUG`, `BIOLOGICAL`, `DEVICE`, `PROCEDURE`, `BEHAVIORAL`, `DIAGNOSTIC_TEST`, `DIETARY_SUPPLEMENT`, `RADIATION` …. |
| `condition_mesh` | keyword | `k=v`, `k=a,b` | Condition MeSH term (controlled, more reliable than free-text conditions) |
| `countries` | keyword | `k=v`, `k=a,b` | Trial countries |
| `start_year` | integer | `k=v`, `k>=n`, `k=n..m` | Start year, range |
| `has_results` | bool | `k=v` | Results posted |
| `sponsor_class` | keyword | `k=v`, `k=a,b` | Sponsor class Values: `INDUSTRY`, `NIH`, `FED`, `OTHER_GOV`, `NETWORK`, `INDIV`, `OTHER`. |

Advanced filters (see `deepxiv fa spec trials`): `sex`, `sponsor`, `intervention_mesh`, `biomarker_names`, `performance_status`, `treatment_naive`, `enrollment`, `age_min_years`, `age_max_years`, `completion_year`.

## Read

```bash
deepxiv fa read trials ID [ID...] [-l brief|detail|full] [-e EXTRA] [-p k=v]... [-f json|md|html]
```

| level | credits | returns |
|---|---|---|
| `brief` | 1 | Card: the fields needed to triage, same as in search hits |
| `detail` (default) | 2 | Every structured field (rule-derived plus model-generated; model fields are listed in _enrich.fields) |
| `full` | 5 | Full text (not available yet: the full registry record lives on NAS (ctgov/bulk) and is not in the index) |

At `-l full`, `-p section=NAME` reads one section and `-p characters=N` the first N characters.

## Facets

`deepxiv fa facets trials FIELD` lists the legal values and counts, free. Use it instead of guessing a spelling. Fields: `phase`, `overall_status`, `study_type`, `intervention_type`, `sponsor_class`, `sex`, `countries`, `condition_mesh`.

## Ask

```bash
deepxiv fa ask "question" -d trials [-e low|medium|high] [-p k=v]... [--no-stream] [--json]
```

Agentic Q&A over this domain: the model turns the question into filters plus keywords from the domain's own self-description, reads the hits and answers with [trials:<nct_id> <title>] citations; /stream is NDJSON with real token deltas

Always pass `-d trials`: automatic domain picking is still early.

## What this corpus will and will not tell you

- Filter by condition_mesh (controlled terms); `conditions` is free text as entered by the registrant.
- Eligibility highlights, biomarkers, prior therapy and ECOG are model-extracted from the eligibility text — verify against the record before acting.
- 97k studies carry overall_status=UNKNOWN: the registrant stopped updating, which does not mean the trial ended.
- The index holds no full text: level=full is not available yet (the full registry record lives on NAS (ctgov/bulk) and is not in the index).

## Citing

Cite records as `[NCT02082496]`. Say plainly when the corpus has nothing.

---

Generated by `scripts/gen_fa_skills.py` from `deepxiv fa spec trials --json` on 2026-10-19. Field names and prices can change; `deepxiv fa spec trials` is the live source.
