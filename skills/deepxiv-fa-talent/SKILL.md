---
name: deepxiv-fa-talent
description: Find and read AI researcher profiles with the deepxiv CLI: by name (Chinese, pinyin, English), organisation, role, area, location or h-index; education, career, top papers, coauthors. Use when asked who works on something, to build a list of researchers or students, or about a specific researcher.
---

# DeepXiv · Talent (`talent`)

AI researcher directory: 189k people, 160k LLM-researched profiles (education, career, representative papers, open source), Google Scholar metrics rendered live. One document per person; id is person_id.

Corpus: 191,238 documents, updated 2026-10-19.

## Setup

```bash
pip install -U deepxiv-sdk      # deepxiv registers a token on first use
```

`search` and `read` spend the deepxiv daily limit at the credits listed below. `ask` spends the agentic quota: a registered key from https://data.rag.ac.cn/register (300/day), or 3 lifetime trial asks on the auto-registered token. Data goes to stdout; cost, quota and sources go to stderr. Exit 0 ok, 1 API error, 2 usage error. The general CLI guide is the `deepxiv-cli` skill.

## Start here

```bash
deepxiv fa search talent "Yann LeCun" -k 3   # a name: English, Chinese, pinyin or "Last, First"
deepxiv fa search talent "具身智能" -F org=清华大学 -F role=教授 -F "h_index>=30" -k 10   # Chinese institutions take Chinese values
deepxiv fa search talent "world model" -F career_stage=student -F location=北京,上海 -k 20   # location values are Chinese city names: 北京, 上海
deepxiv fa read talent 15023 3426 2813 -l brief   # several cards in one call
deepxiv fa read talent 15023 -e network   # coauthors
deepxiv fa resolve "Geoffrey Hinton" "Yann LeCun"   # names → person_id, batch
deepxiv fa ask "who works on self-supervised learning at Mila" -d talent
```

Free samples: ids `7870`; queries `Federica Sarro`, `Jürgen Schmidhuber`, `软件工程 实证研究`.

## Search

```bash
deepxiv fa search talent "query" [-F FILTER]... [-k N] [--offset N] [--mode M] [--head] [--json]
```

Modes: hybrid, dense, bm25, name. Up to 100 hits. Cost 2 (with `--head`: 3).
An empty query is rejected; use `"*"` to list by filters only. Filters combine with AND; an undeclared field exits 2.

| filter | type | `-F` syntax | meaning |
|---|---|---|---|
| `org` | keyword | `k=v`, `k=a,b` | Current organisation, e.g. Tsinghua University; several allowed (past or current: advanced field orgs) |
| `role` | keyword | `k=v`, `k=a,b`, `k~text` | Title: the normalised titles match exactly; anything else (or {"text": …}) is a full-text match on the raw title Values: `教授`, `副教授`, `助理教授`, `研究员`, `博士后`, `博士生`, `硕士生`, `工程师`. |
| `area` | keyword | `k=v`, `k=a,b` | Research area, e.g. embodied AI, RAG; several allowed |
| `location` | keyword | `k=v`, `k=a,b` | Location, e.g. Beijing, Singapore; several allowed |
| `min_h_index` | integer | `k=v` | h-index at least |
| `active_since` | integer | `k=v` | Most recent paper in or after this year (drops inactive people) |

Advanced filters (see `deepxiv fa spec talent`): `names`, `name_zh`, `name_en`, `aff_raw`, `orgs`, `orgs_current`, `role_norm`, `career_stage`, `areas`, `h_index`, `citations_all`, `citations_5y`, `i10_index`, `last_paper_year`, `profile_at`, `has_profile`, `has_scholar`.

## Read

```bash
deepxiv fa read talent ID [ID...] [-l brief|detail|full] [-e EXTRA] [-p k=v]... [-f json|md|html]
```

| level | credits | returns |
|---|---|---|
| `brief` | 1 | Card: name, affiliation, title, areas, h-index, citations, has_profile (what search hits carry as brief) |
| `detail` (default) | 3 | Everything most callers need in one call (the default, level=detail): card + bio, current organisations, education, career, top 5 papers, Scholar metrics, top 5 coauthors, advisors, and the full profile's section map (read one with level=full&section=<name>) |
| `full` | 10 | The full profile markdown (level=full; the contact section is omitted unless contact=1) |

| `-e` extra | credits | returns |
|---|---|---|
| `scholar` | 2 | Structured Google Scholar: metrics (all / 5y), citations by year, top papers, as_of, stale, source. A stale snapshot is rebuilt from cache for free when possible, otherwise queued for background refresh |
| `scholar_live` | 20 | Same as scholar but synchronously fetches the latest numbers from Google Scholar (≤10s). Subject to a per-account daily quota (talent:scholar_live) and a global crawl budget; if the refresh does not actually happen you get a 502 and the credits and quota back — use extra=scholar for the stored snapshot |
| `papers` | 2 | Representative papers: Scholar top papers + profile top_papers + OpenAlex works, deduplicated by title, sorted by citations |
| `network` | 2 | Relations: coauthors (with in-corpus person_id), advisors, students |
| `sources` | 1 | The profile's reference list: the [n] numbers used in the report, url, title, confidence, whether the page archived at research time is still readable (snapshot), and which facts it backs (backs: education / affiliation) |
| `source` | 2 | The archived page behind one reference (the snapshot taken at research time; no live fetch). n is the [n] in the report; raw=1 returns the original HTML |
| `structured` | 3 | Structured profile for section-by-section rendering: education / work with dates (verbatim strings plus parsed start_year / end_year / current), open_source, top_papers, links, bio_md, activities_md, tags, career_stage; every item carries source_ids numbered as in view=sources. No Scholar metrics (live ones are in view=scholar); email only with contact=1; people without a researched profile get 404 (not charged) |

At `-l full`, `-p section=NAME` reads one section and `-p characters=N` the first N characters.

## Facets

`deepxiv fa facets talent FIELD` lists the legal values and counts, free. Use it instead of guessing a spelling. Fields: `orgs`, `orgs_current`, `areas`, `role_norm`, `career_stage`, `location`, `last_paper_year`.

`deepxiv fa resolve NAME [NAME...]` checks a batch of names against the corpus and returns ids.

## Ask

```bash
deepxiv fa ask "question" -d talent [-e low|medium|high] [-p k=v]... [--no-stream] [--json]
```

Find or understand people: an agent searches the corpus and reads profiles, answering with [talent:<id> <name>] citations; no web access, says so when nobody matches

Always pass `-d talent`: automatic domain picking is still early.

| `-p` param | type | meaning |
|---|---|---|
| `top_k` | integer | candidates per corpus search |

## What this corpus will and will not tell you

- People with has_profile=false carry only name/affiliation-level data; level=full (and its sections) returns 404.
- Profile content has a daily quota counted in distinct people read per day (talent:profiles; per-plan numbers are in the self-description's quotas): re-reading the same person is free, card / brief and search are not capped. Over the limit returns 429 quota_exceeded with used_today and resets_at. Contact us for a talent:bulk key for volume or offline use (it lifts the scholar_live quota too).
- Common usage is in quickstart: search to look people up or filter them, read (default level=detail) to read one in a single call; other facets via extra=, a human-readable page via format=html; filters marked advanced are there when you need them.
- Facet fields: org / role / area / location / active_since, plus orgs / career_stage (recomputed nightly).
- POST /v1/talent/resolve {names:[…]} checks a batch of names (paper authors, a team page) against the corpus and returns person_ids.
- Name lookup: when the query looks like a person's name (2–4 Chinese characters / 2–4 Latin words), people with that name come first (hit.match="name"); Chinese names are converted to pinyin and Hongjin / Hong Jin / Hong-Jin all match. The response carries name_match: exact (full name matches — a Latin name, or a Chinese name of 3+ characters matched directly) returns only those people; partial (e.g. matched only through pinyin) keeps the normal results after them. mode=name returns only people with that name (ordered by has_profile, then h-index).
- Every [n] in a profile points at an entry in extra=sources; extra=source&n=3 returns the page archived when the profile was researched (text plus the fetch date). Only snapshot=text has readable text — none / blocked (the site refused the crawler) / html (raw page only, add raw=1 for the original HTML) return 404, which is not charged.
- Scholar numbers inside profile.publications are crawl-time values; trust h_index / citations_* in level=brief / detail.
- The closing 'online footprint & contact' section comes from public homepages.

## Limits

- Quota `talent:profiles`: How many distinct people's profile content you may read per day (profile / page / full / raw / head / preview / section / source). Re-reading the same person is free; card / brief and search are not capped. Contact us for a talent:bulk key if you need volume.
- Quota `talent:scholar_live`: How many distinct people you may refresh live from Google Scholar per day (scholar_live). This is your share of the global crawl budget; counted per person, cache hits included, so it stays predictable.
- Grant `talent:bulk`: Lifts talent's daily quotas (profile content and live Scholar refreshes). For callers with a bulk or licence agreement. Issued on request, not self-serve.

## Citing

Cite records as `[talent:7870 Federica Sarro]`. Say plainly when the corpus has nothing.

---

Generated by `scripts/gen_fa_skills.py` from `deepxiv fa spec talent --json` on 2026-10-19. Field names and prices can change; `deepxiv fa spec talent` is the live source.
