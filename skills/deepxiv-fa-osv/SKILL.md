---
name: deepxiv-fa-osv
description: Search ~200k open-source package advisories not covered by CVE, mostly malicious-package reports (npm, PyPI …) with behaviours, impersonated packages and IOCs. Use when checking whether a package is malicious or for supply-chain advisories.
---

# DeepXiv · OSV (`osv`)

About 200k open-source package security advisories — the part of osv.dev that CVE does not cover (synced daily; exact count in corpus). **Over 90% are malicious-package reports** (MAL-*, overwhelmingly npm); the remaining ~13k are standalone advisories with no CVE id (GHSA / RUSTSEC / PYSEC / GO …). Malicious behaviours (closed set of 13), the legitimate package being impersonated, IOCs (domains / URLs / IPs / filenames, each verified to appear in the advisory text) and one-line summaries are model-extracted. Hybrid vector + lexical search; filters and sorting in Postgres.

Corpus: 199,701 documents.

## Setup

```bash
pip install -U deepxiv-sdk      # deepxiv registers a token on first use
```

With a registered key (https://data.rag.ac.cn/register), `search` and `read` are fair use: 60/min, 5 at once, 5,000/day; on the auto-registered token they spend the deepxiv daily limit at the credits listed below. `ask` draws on the daily ask allowance (resets 00:00 UTC; a site-wide daily total can run out early at peak times), or 3 lifetime trial asks on the auto-registered token. On 429, back off for `Retry-After` seconds. Data goes to stdout; cost, quota and sources go to stderr. Exit 0 ok, 1 API error, 2 usage error. The general CLI guide is the `deepxiv-cli` skill.

## Start here

```bash
deepxiv fa search osv "malicious npm package credential theft" -F malicious=true -F ecosystems=npm -k 5
deepxiv fa search osv "*" -F behaviors=credential_theft --sort published -k 5
deepxiv fa read osv MAL-2026-17452 -l brief
deepxiv fa ask "Are there malicious npm packages impersonating popular crypto libraries?" -d osv
```

Free samples: ids `MAL-2026-17452`; queries `malicious npm package`.

## Search

```bash
deepxiv fa search osv "query" [-F FILTER]... [-k N] [--offset N] [--mode M] [--sort S] [--head] [--json]
```

Modes: hybrid, dense, bm25, keyword. Up to 200 hits. Cost 2 (with `--head`: 3).
Sorts: `relevance`, `date`, `published` (default `relevance`).
An empty query is rejected; use `"*"` to list by filters only. Filters combine with AND; an undeclared field exits 2.

| filter | type | `-F` syntax | meaning |
|---|---|---|---|
| `behaviors` | keyword | `k=v`, `k=a,b` | Malicious behaviour (closed set of 13, model-assigned): credential_theft / data_exfiltration / downloader_or_dropper / backdoor_or_remote_access / spam_or_token_farming / obfuscated_unknown / other … (several allowed) |
| `ecosystems` | keyword | `k=v`, `k=a,b` | Package ecosystem: npm (about 177k) / PyPI (about 10k) / OSS-Fuzz / Linux / Julia / crates.io / Packagist … (several allowed) |
| `malicious` | bool | `k=v` | Whether it is a malicious package (about 186k true / 13k false; exact counts via facets) |
| `published` | datetime | `k>=n`, `k=n..m` | Publication date range |
| `source` | keyword | `k=v`, `k=a,b` | Advisory source = the id prefix: MAL 185.7k / OSV 4,479 / GHSA 3,786 / UVI 2,337 / JLSEC 1,693 / RUSTSEC 723 / PYSEC 351 Values: `MAL`, `OSV`, `GHSA`, `UVI`, `JLSEC`, `RUSTSEC`, `PYSEC`, `GO` …. |
| `vuln_class` | keyword | `k=v`, `k=a,b` | Vulnerability class for non-malicious advisories (cve's closed set plus unmaintained) Values: `memory_corruption`, `denial_of_service`, `other`, `information_disclosure`, `injection`, `xss`, `auth_bypass`, `remote_code_execution` …. |

Advanced filters (see `deepxiv fa spec osv`): `imitates`, `package_names`, `aliases`, `indicators`.

## Read

```bash
deepxiv fa read osv ID [ID...] [-l brief|detail|full] [-e EXTRA] [-p k=v]... [-f json|md|html]
```

| level | credits | returns |
|---|---|---|
| `brief` | 1 | Card: behaviors, doc_id, ecosystems, imitates, malicious, one_liner, one_liner_zh, package_names… |
| `detail` (default) | 2 | Every structured field (card plus the source abstract and detail fields) |

At `-l full`, `-p section=NAME` reads one section and `-p characters=N` the first N characters.

## Facets

`deepxiv fa facets osv FIELD` lists the legal values and counts, free. Use it instead of guessing a spelling. Fields: `source`, `vuln_class`.

## Ask

```bash
deepxiv fa ask "question" -d osv [-e low|medium|high] [-p k=v]... [--no-stream] [--json]
```

Agentic Q&A over this domain: hybrid vector + lexical search (filters the vector layer lacks fall back to Postgres full text); the model reads the hits and answers with [osv:<doc_id> <title>] citations; /stream is NDJSON with real token deltas

Always pass `-d osv`: automatic domain picking is still early.

## What this corpus will and will not tell you

- Division of labour with cve: **cve holds CVE-numbered vulnerabilities** (about 390k from NVD plus KEV and EPSS; exact count in /v1/cve corpus); **osv holds what CVE does not cover** — overwhelmingly poisoned / impersonating packages (mostly npm), which never get a CVE id. The two domains do not overlap; for supply-chain poisoning, use osv.
- Reverse lookup by IOC: filters.indicators=["some-domain"] finds every package that exfiltrates to it. Each IOC was verified to appear in the advisory text — not model-invented.
- Typosquatting: filters.imitates is a fuzzy match, so "requests" finds the packages impersonating it.
- behaviors and malicious are model-assigned — fine as a summary, not as a quote; the advisory text is details, in level=detail.
- ecosystems and package_names are arrays; passing a list means any-match.
- Displaying OSV data requires attribution (see the attribution field): the data comes from OSV.dev and its upstream databases, and each advisory's original source (GitHub Advisory / RustSec / PyPA …) keeps its own licence.
- **Terms are ANDed** (every term must match), so a long pile of words easily returns nothing — prefer fewer terms plus filters on the Postgres path. Two paths: with a query, no sort and only filters the vector layer has, search is hybrid vector + lexical (semantic recall, terms need not all match), topped up from Postgres; otherwise (sort given, indicators / imitates / published used, or mode=keyword) it runs in Postgres as an English tsvector and a Chinese zhparser pass, unioned; quoted phrases / OR / -exclusion work. Each hit's layer says which path.
- Model-written fields (summarise, do not quote): behaviors, imitates, impact, indicators, malicious, one_liner, one_liner_zh, vuln_class.
- The field table and enumerations are generated from the store's own self-description (search.field), not hand-written; enumeration counts are as of 2026-10-15.

## Citing

Cite records as `[MAL-2026-17452]`. Say plainly when the corpus has nothing.

---

Generated by `scripts/gen_fa_skills.py` from `deepxiv fa spec osv --json` on 2026-10-19. Field names and prices can change; `deepxiv fa spec osv` is the live source.
