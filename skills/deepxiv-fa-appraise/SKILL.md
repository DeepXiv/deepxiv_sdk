---
name: deepxiv-fa-appraise
description: Find which academicians and society fellows (CAS, CAE, NAS, NAE, Royal Society, ACM, IEEE, AAAI …) cited a paper and what they actually said, with the citing sentence, type and stance. Use for grant reports, promotion dossiers, or any 'who of note praised this paper' question.
---

# DeepXiv · Appraise (`appraise`)

Academic appraisal: which academicians and society fellows have cited a paper, and what they actually said. 112k arXiv papers authored by 5,427 fellows and academicians (Chinese Academies, US NAS/NAE, Royal Society / RAEng, ACM / IEEE / AAAI / ACL / AAAS / IAPR / CCF), with 5.26M parsed references and 8.3M citing sentences, each classified by type and stance. The id is the paper being appraised (arXiv id / DOI / title). ask turns the matched sentences into a Chinese appraisal paragraph for grant reports and promotion dossiers, with the English original attached to every claim.

Corpus: 284,124 documents.

## Setup

```bash
pip install -U deepxiv-sdk      # deepxiv registers a token on first use
```

`search` and `read` spend the deepxiv daily limit at the credits listed below. `ask` spends the agentic quota: a registered key from https://data.rag.ac.cn/register (300/day), or 3 lifetime trial asks on the auto-registered token. Data goes to stdout; cost, quota and sources go to stderr. Exit 0 ok, 1 API error, 2 usage error. The general CLI guide is the `deepxiv-cli` skill.

## Start here

```bash
deepxiv fa search appraise "DeepSeek-R1" -k 3   # → arxiv:2501.12948
deepxiv fa read appraise arxiv:2501.12948 -l brief   # counts and stance breakdown
deepxiv fa read appraise arxiv:2501.12948 -p stance=positive -p org=CAS,CAE   # positive sentences from Chinese academicians
deepxiv fa ask "DeepSeek-R1 得到了哪些院士的正面评价" -d appraise -p paper=arxiv:2501.12948
```

Free samples: ids `arxiv:2402.03216`; queries `BGE-M3`.

## Search

```bash
deepxiv fa search appraise "query" [-F FILTER]... [-k N] [--offset N] [--mode M] [--head] [--json]
```

Modes: hybrid, title. Up to 20 hits. Cost 3 (with `--head`: 4).
An empty query is rejected; use `"*"` to list by filters only. Filters combine with AND; an undeclared field exits 2.

| filter | type | `-F` syntax | meaning |
|---|---|---|---|
| `org` | keyword | `k=v`, `k=a,b` | Honour body: CAS / CAE (Chinese academies), NAS / NAE (US), ROYALSOC / RAENG (UK), ACM / IEEE / AAAI / ACL / AAAS / IAPR / CCF (fellows); several allowed Values: `CAS`, `CAE`, `NAS`, `NAE`, `ROYALSOC`, `RAENG`, `ACM`, `IEEE` …. |
| `bucket` | keyword | `k=v`, `k=a,b` | Weight class: academy (academicians) / major (ACM, IEEE … fellows) / other Values: `academy`, `major`, `other`. |
| `stance` | keyword | `k=v`, `k=a,b` | Stance of the citing sentence (model-assigned): positive / neutral / negative Values: `positive`, `neutral`, `negative`. |
| `type` | keyword | `k=v`, `k=a,b` | Citation type (model-assigned): endorse / buildon / exemplar / baseline / resource / critique / motivate / background Values: `endorse`, `buildon`, `exemplar`, `baseline`, `critique`, `resource`, `motivate`, `background`. |
| `about_target` | bool | `k=v` | Whether the sentence is about this paper itself rather than a passing mention |
| `min_h_index` | integer | `k=v` | Only people with at least this h-index |
| `honoree` | text | `k~text` | Filter by name (zh/en, substring) |
| `citing_year` | integer | `k=v`, `k>=n`, `k=n..m` | Year of the citing paper; ranges allowed |

Advanced filters (see `deepxiv fa spec appraise`): `affiliation`, `section`, `mentions_name`, `annotated`.

## Read

```bash
deepxiv fa read appraise ID [ID...] [-l brief|detail|full] [-e EXTRA] [-p k=v]... [-f json|md|html]
```

| level | credits | returns |
|---|---|---|
| `brief` | 1 | Summary card: how many fellows, citing papers and sentences, the stance and type breakdown, and the single strongest sentence |
| `detail` (default) | 3 | The list plus the sentences (the default, level=detail): per citation the type, stance, whether it is about this paper, the model's one-line claim, a Chinese translation, the English original, the section and the citing paper. Only opinionated types by default (no background); pass type= for everything |
| `full` | 5 | All the evidence (level=full): background citations included, every sentence with its neighbouring sentences and the raw bibliography entry — for verification |

| `-e` extra | credits | returns |
|---|---|---|
| `honorees` | 2 | The list: each fellow's Chinese titles, affiliation, h-index, talent person_id, how many times they cited it and in which papers (no sentences) |

At `-l full`, `-p section=NAME` reads one section and `-p characters=N` the first N characters.

## Facets

`deepxiv fa facets appraise FIELD` lists the legal values and counts, free. Use it instead of guessing a spelling. Fields: `org`, `bucket`, `type`, `stance`.

## Ask

```bash
deepxiv fa ask "question" -d appraise [-e low|medium|high] [-p k=v]... [--no-stream] [--json]
```

Turns "who of note has evaluated this paper" into Chinese appraisal text: resolves the paper (semantic search over papers → arXiv id), pulls the fellows' citing sentences, then writes one paragraph per person. Wording may be positive but must not exceed what the original says; every paragraph carries the English original and its source. effort sets how many people are written up (low 5 / medium 10 / high 20)

Always pass `-d appraise`: automatic domain picking is still early.

| `-p` param | type | meaning |
|---|---|---|
| `paper` | string | name the paper directly (arXiv id / DOI / title) and skip resolution |
| `filters` | object | restrict which citations are used (same DSL as search filters) |

## What this corpus will and will not tell you

- Coverage: Covers only arXiv full texts authored by these 5,427 fellows and academicians; their journal-only papers and citations by anyone else are not included. No hit means this set of papers does not cite it — not that the work is uncited.
- Three id forms: arxiv:2402.03216 (bare ids accepted), doi:10.1145/…, and title:<paper title>. The first two are exact lookups (~40ms); title: is a substring match over normalised bibliography text — 3–6 seconds, and papers with similar titles can collide, so the response carries warnings.
- search has no vector index: the query first goes through the papers domain's semantic search to identify the paper (so a title, a model name or a one-line description all work), then the arXiv id is used for lookup. If it picks the wrong paper, read by id instead: read arxiv:<id>.
- type / stance / about_target / claim / zh are model-assigned; the sentence itself is the evidence. Quote the sentence in anything formal. Sentences with annotated=false have not been classified yet.
- level=detail returns only opinionated citation types by default; background citations are more than half the total — use level=full or pass type= to get them.
- How ask writes: early work may become 'early pioneering work' and a baseline 'widely adopted as a comparison baseline', but nothing may be asserted that the original sentence does not say. Every paragraph carries the English original so a reader can check it.
- people[].person_id is the talent domain's id — read talent <person_id> for that person's full profile.
- Attribution: author-year references ('Li et al., 2025') can match several bibliography entries; such sentences are marked ambiguous=true.

## Citing

Cite records as `[appraise:<honoree_id> <name>]`. Say plainly when the corpus has nothing.

---

Generated by `scripts/gen_fa_skills.py` from `deepxiv fa spec appraise --json` on 2026-10-19. Field names and prices can change; `deepxiv fa spec appraise` is the live source.
