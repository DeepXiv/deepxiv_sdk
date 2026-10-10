# deepxiv fa — 1stAuthor domains

> **中文版**: [FA.zh.md](FA.zh.md) · Back to [README](README.md)

DeepXiv works closely with [1stAuthor](https://1stauthor.com) to serve data beyond arXiv. `deepxiv fa` reaches 1stAuthor's domains (researchers, statutes, court judgments, clinical trials, drug labels, grants, filings, standards, vulnerabilities, the Federal Register) **with your deepxiv token**. Requests go through `data.rag.ac.cn/fa`, so you never need a separate 1stAuthor key.

DeepXiv itself stays focused on agentic data services for academic papers, and will remain free. If you need higher limits on the 1stAuthor domains, see [1stauthor.com](https://1stauthor.com).

> **Beta.** `deepxiv fa` ships in `1.2.0b1`, source install only, and 1stAuthor is in closed beta. Questions or problems? [Open an issue](https://github.com/DeepXiv/deepxiv_sdk/issues).

This page is the complete reference for `deepxiv fa`: every command, option, parameter and error, plus the Python and HTTP APIs.

**Contents**
1. [Install and token](#1-install-and-token)
2. [Domains](#2-domains)
3. [Quick start](#3-quick-start)
4. [Commands](#4-commands): [domains](#fa-domains) · [spec](#fa-spec) · [search](#fa-search) · [read](#fa-read) · [facets](#fa-facets) · [resolve](#fa-resolve) · [ask](#fa-ask) · [whoami](#fa-whoami)
5. [Filters](#5-filters)
6. [Reading: levels, extras, views, sections, formats](#6-reading-levels-extras-views-sections-formats)
7. [Output and exit codes](#7-output-and-exit-codes)
8. [Cost and quota](#8-cost-and-quota)
9. [Errors and retries](#9-errors-and-retries)
10. [Python API](#10-python-api)
11. [HTTP API](#11-http-api)
12. [Migrating from `deepxiv talent`](#12-migrating-from-deepxiv-talent)
13. [Troubleshooting](#13-troubleshooting)

---

## 1. Install and token

```bash
pip install git+https://github.com/DeepXiv/deepxiv_sdk.git    # 1.2.0b1
deepxiv fa --help
```

`deepxiv fa` uses the same token as every other deepxiv command, looked up in this order:

1. `--token` / `-t` on the command
2. the `DEEPXIV_TOKEN` environment variable
3. `DEEPXIV_TOKEN=` in `~/.env`, then in `./.env`
4. if none of these is set, deepxiv registers a token automatically and saves it to `~/.env`

There are two kinds of token:

| | Can use | How to get |
|---|---|---|
| **Auto-registered SDK token** | everything except `fa ask` | Created automatically on first use |
| **Registered account key** | everything, including `fa ask` | [data.rag.ac.cn/register](https://data.rag.ac.cn/register), then `deepxiv config --token YOUR_KEY` |

`deepxiv fa whoami` tells you which one you're using.

## 2. Domains

| Domain | What's in it | ID field | `fa ask` |
|---|---|---|---|
| `talent` | ~190k AI researchers; ~160k researched profiles (education, career, representative papers, open source), with live Google Scholar metrics | `person_id` | ✅ |
| `law` | ~33k statutes / 1.5M articles from 26 jurisdictions, searched article by article, with Chinese translations and per-article extraction | `law_id` | ✅ |
| `us_law` | ~5M clause-level US provisions across 53 jurisdictions: statutes, regulations (CFR), session laws, agency decisions, guidance, court rules | `law_id` | |
| `cases` | Court judgments: ~17.5M from China and ~3.4M US opinions, with extracted structured fields | `uuid` | |
| `trials` | Every study on ClinicalTrials.gov (~600k), with extracted eligibility, biomarkers, prior therapy and summaries | `nct_id` | |
| `drugs` | ~256k US drug labels (openFDA SPL): indications, contraindications, interactions, boxed warnings | `set_id` | |
| `grants` | ~1.2M NSF awards and NIH projects | `grant_id` | |
| `filings` | ~1.2M US and Chinese corporate filings and regulatory documents (8-K, 10-K/20-F, periodic reports, enforcement) | `doc_id` | |
| `standards` | ~79k Chinese national standards (GB / GB/T / GB/Z): catalogue metadata only, no full text | `std_code` | |
| `cve` | ~384k public vulnerabilities (NVD), with CISA KEV and EPSS | `doc_id` | |
| `fr` | ~1M Federal Register documents since 1994 | `doc_id` | |
| `appraise` | Which academicians and society fellows cited a paper, and what they said about it | `target_key` | ✅ |

The list is live: `deepxiv fa domains` shows the current domains and sizes, and `deepxiv fa spec <domain>` describes one domain. Papers and the web aren't here because deepxiv serves them natively (`deepxiv search`, `paper`, `ask`).

## 3. Quick start

```bash
deepxiv fa domains                                    # what's there (free)
deepxiv fa spec talent                                # filters, read levels, prices (free)

deepxiv fa search talent "Geoffrey Hinton"            # look someone up
deepxiv fa read talent 15023                          # read the profile
deepxiv fa search law "personal information protection" --top-k 5
deepxiv fa ask "who are the leading researchers on self-supervised learning" --domain talent
```

The workflow is the same as for papers: **search → read only what you need → ask when you want a synthesized answer.**

## 4. Commands

Every `fa` command accepts these options:

| Option | |
|---|---|
| `-t`, `--token TEXT` | Token to use; overrides `DEEPXIV_TOKEN` |
| `--json` | Print the full JSON response instead of the text rendering |
| `--help` | Show the command's help |

### `fa domains`

```
deepxiv fa domains [--json]
```

Lists every domain: id, status, whether `ask` is available, corpus size and name. **Free.**

### `fa spec`

```
deepxiv fa spec DOMAIN [--json]
```

The domain's self-description. **Free.** The text rendering shows:

- name, description, ID field and an example ID
- **SEARCH**: retrieval modes, prices, and every filter field with its type, operators and description
- **READ**: the levels and extras, each with its price
- **ASK**: the effort levels and the domain's extra ask parameters (`-p`), or a note that ask isn't available
- **FACETS**: the fields `fa facets` accepts
- free sample queries and IDs, and quickstart calls

`--json` adds what the text leaves out: views, section and format options, `brief_fields` / `head_fields`, notes, and per-ID-type levels (for example `law` article IDs vs statute IDs).

### `fa search`

```
deepxiv fa search DOMAIN QUERY [-F EXPR]... [-k N] [--offset N] [--mode MODE] [--head] [--json]
```

| Option | Default | |
|---|---|---|
| `-F`, `--filter EXPR` | — | Repeatable, combined with AND. See [Filters](#5-filters) |
| `-k`, `--top-k N` | 10 | Number of hits, 1~100 |
| `--offset N` | 0 | Skip the first N hits (pagination) |
| `--mode MODE` | domain default | Retrieval mode, from `spec` → `search.modes` (talent: `hybrid`, `dense`, `bm25`, `name`) |
| `--head` | off | Richer hits (`fields=head`); costs more |

The text output gives one block per hit:

```
#1 [15023] Geoffrey Hinton · Emeritus Prof. Computer Science, University of Toronto
  1978 年博士毕业，现多伦多大学计算机科学荣誉教授、Vector Institute 联合创始人兼首席科学顾问
  h-index: 192 | citations: 1066174
```

- The first line is the ID in brackets and the title.
- The next line is a one-line summary.
- Then up to five key fields: talent shows h-index and citations, cve severity and CVSS, trials status and sponsor, cases court, case number and date, and so on.
- Last are tags or areas.

Search warnings go to stderr. Talent queries that look like a name are matched as names first, across Chinese, pinyin and English spellings.

```bash
deepxiv fa search talent "Yann LeCun"
deepxiv fa search talent "deep learning" -F "org=University of Toronto" -F "h_index>=50"
deepxiv fa search talent "diffusion models" -F career_stage=junior --top-k 20 --offset 20
deepxiv fa search talent "Hinton" --mode name
deepxiv fa search trials "pancreatic cancer" -F overall_status=RECRUITING
deepxiv fa search law "personal information protection" --top-k 5
deepxiv fa search cve "log4j" --json
```

### `fa read`

```
deepxiv fa read DOMAIN ID [ID...] [-l LEVEL] [-e EXTRA] [--view VIEW] [-f FORMAT] [-p k=v]... [--json]
```

| Option | |
|---|---|
| `-l`, `--level` | `brief` / `detail` / `full`; the domain's default if omitted |
| `-e`, `--extra NAME` | Read one extra facet instead of a level, e.g. talent `papers` / `network` / `scholar` |
| `--view NAME` | Read a named view (`GET /doc/{id}?view=…`); can't be combined with `--level` / `--extra` |
| `-f`, `--format` | `json` / `md` / `html`: server-side rendering, for formats the domain lists in `spec` |
| `-p`, `--param k=v` | Extra query parameter, repeatable: `section=…`, `contact=1`, `n=3`, `window=2`, … |

- One ID reads one document. Several IDs make one batch call (`POST /read`), which takes only `--level` / `--extra`.
- Output: a markdown or HTML body is printed as is; structured data is printed as indented JSON. `--json` prints the whole response, including `meta`.

```bash
deepxiv fa read talent 15023                                  # default level (detail for talent)
deepxiv fa read talent 15023 --level brief                    # the card only, cheapest
deepxiv fa read talent 15023 --level full > hinton.md         # the full researched profile, markdown
deepxiv fa read talent 15023 --level full -p section=荣誉与奖项  # one section of it
deepxiv fa read talent 15023 --extra network                  # coauthors, advisors, students
deepxiv fa read talent 15023 --extra source -p n=1            # archived copy of reference [1]
deepxiv fa read talent 15023 --view scholar                   # a named view
deepxiv fa read talent 15023 --format html > hinton.html      # a rendered page
deepxiv fa read talent 15023 3426 --level brief               # two people in one call
deepxiv fa read law "chn:law:中华人民共和国个人信息保护法~38"    # one article, by the id search returned
```

[Section 6](#6-reading-levels-extras-views-sections-formats) explains what each of these returns.

### `fa facets`

```
deepxiv fa facets DOMAIN FIELD [--limit N] [--json]
```

Value counts for a field, most common first. Use it to find the exact spelling for a `-F` filter. The fields come from `spec` → `facets` (talent: `orgs`, `orgs_current`, `areas`, `role_norm`, `career_stage`, `location`, `last_paper_year`).

```bash
deepxiv fa facets talent orgs --limit 20
deepxiv fa facets talent career_stage
```

### `fa resolve`

```
deepxiv fa resolve NAME [NAME...] [--json]
```

Matches a batch of person names (paper authors, a lab page) to talent IDs, up to 50 per call. For each name the CLI prints `→ ID` when the match is unambiguous, or the number of candidates, followed by up to five candidates.

```bash
deepxiv fa resolve "Geoffrey Hinton" "Yann LeCun" "Yoshua Bengio"
```

### `fa ask`

```
deepxiv fa ask QUESTION [-d DOMAIN] [-e EFFORT] [-p k=v]... [--no-stream] [--no-sources] [-v] [--json]
```

A cited answer. An agent searches and reads the domain for you. **Needs a registered key.**

| Option | |
|---|---|
| `-d`, `--domain` | Domain to ask. Without it, 1stAuthor picks the domain and stderr shows `🧭 routed to …` |
| `-e`, `--effort` | `low` / `medium` / `high`; the domain's default if omitted. Higher effort reads more and costs more |
| `-p`, `--param k=v` | A domain-specific ask parameter, repeatable. Values are sent as JSON types: `5` → number, `true` → boolean, `{…}` / `[…]` → object or array |
| `--no-stream` | Wait for the whole answer instead of streaming it |
| `--no-sources` | Skip the sources list |
| `-v`, `--verbose` | Also show start, tool calls, warnings, run stats and remaining agentic quota on stderr |
| `--json` | One JSON object (`answer`, `sources`, `stats`, `meta`) |

Ask parameters by domain (current list: `deepxiv fa spec DOMAIN`):

| Domain | Parameter | |
|---|---|---|
| `talent` | `top_k` | Candidates per corpus search (default 20) |
| `law` | `scope` | `auto` / `law` (statutes) / `case` (judgments) / `both` |
| `law` | `jurisdiction` | ISO3 code (default: the model decides) |
| `appraise` | `paper` | Name the paper (arXiv ID / DOI / title) and skip resolution |
| `appraise` | `filters` | Which citations to use, in the same format as search filters |

What you get:

- The answer streams to stdout as it's written. Citations look like `[talent:15023 Geoffrey Hinton]` or `[中华人民共和国个人信息保护法 第三十八条]`.
- When the answer is done, sources go to stderr, grouped by kind (e.g. `laws`, `cases`, `people`).
- If the agent fails after the stream has started, the CLI prints `❌ code: message`, adding `(quota refunded)` when the quota was refunded, and exits 1.

```bash
deepxiv fa ask "who are the leading researchers on self-supervised learning" --domain talent
deepxiv fa ask "Which researchers at the University of Toronto work on deep learning?"         # auto-routed
deepxiv fa ask "中国个人信息保护法对个人信息出境有什么要求" -d law -p scope=law -e high
deepxiv fa ask "how did fellows assess this paper" -d appraise -p paper=1706.03762
deepxiv fa ask "Who is Yann LeCun?" -d talent --json > answer.json
```

### `fa whoami`

```
deepxiv fa whoami [--json]
```

**Free.** Shows the token type and name, today's general quota (used / limit / left), and either the agentic quota (tier / used / limit / left) or why `ask` isn't available.

## 5. Filters

`-F` takes one expression per flag, and flags combine with AND:

| Syntax | Meaning | Sent as |
|---|---|---|
| `k=v` | equals | `{"k": "v"}` |
| `k=a,b` | any of | `{"k": ["a", "b"]}` |
| `k>=n`, `k<=n` | bound; the two combine on one field | `{"k": {"gte": n}}` / `{"k": {"lte": n}}` |
| `k=n..m` | inclusive range, open on one side if a bound is missing (`2024..`); dates too (`2024-01..2024-06`) | `{"k": {"gte": n, "lte": m}}` |
| `k~text` | full-text match | `{"k": {"text": "text"}}` |

- Field names, types and allowed operators differ per domain; `deepxiv fa spec DOMAIN` lists them.
- Values are converted to the field's type: integers, numbers, and booleans (`true/false/yes/no/1/0`).
- Before sending, the CLI fetches the spec (free) and checks your filters. An unknown field, a disallowed operator or a badly typed value fails immediately (exit 2) with the list of valid fields, without spending quota.
- The same field can't be given twice, except for `>=` and `<=`, which combine.
- Quote expressions containing `>` or `<`, or the shell will treat them as redirects.

```bash
-F "org=University of Toronto"              # keyword equals
-F career_stage=junior,senior               # any of
-F "h_index>=50" -F "h_index<=120"          # range from two bounds
-F last_paper_year=2023..                   # open range
-F has_profile=true                         # boolean
-F names~Hinton                             # full text
```

## 6. Reading: levels, extras, views, sections, formats

- **Levels** (`--level`) are the main dial. `brief` is the card shown in search hits. `detail` is what most callers need (talent's default). `full` is everything, as markdown where the domain has a long form. Prices rise with depth (talent: 1 / 3 / 10). Some domains define levels per ID type. For `law`, an article ID such as `…~38` reads as `brief` = card, `detail` = original text + translations + extraction, `full` = the article with its neighbours and chapter. `spec --json` → `read.levels_by_id` has the details.
- **Extras** (`--extra`) are one facet of a document, priced separately. For talent: `papers` (representative papers), `network` (coauthors, advisors, students), `scholar` (Scholar metrics snapshot), `scholar_live` (fetched live; pricier), `sources` (the profile's reference list), `source` (an archived page, `-p n=<ref number>`). For law: `cases` (judgments citing the article).
- **Sections**: `--level full -p section=<name>` reads one section of a long document. The names are in the `detail` read's `sections` list (talent: `教育背景`, `工作履历`, `荣誉与奖项`, …).
- **Views** (`--view`) are the underlying named renderings (`spec --json` → `views`). Levels and extras map onto them, so you normally don't need `--view`.
- **Formats** (`--format`): `html` returns a rendered page where the domain lists one (`spec --json` → `read.formats`; talent: `detail:html`). Elsewhere the response stays JSON.
- **Other parameters** go through `-p`: `contact=1` (talent full profile with the contact section), `window=N` (law context), and so on. Each domain's `notes` in `spec --json` lists them.

## 7. Output and exit codes

The output split is the same as `deepxiv ask`:

- **stdout**: data only: hits, documents, answers, or the JSON with `--json`.
- **stderr**: everything else: quota (`💳 cost 2 · 990/1000 left today`), routing (`🧭 routed to talent`), sources, hints (`💡 Read one: …`), warnings, errors.

So `> file` and `| jq` always get clean data:

```bash
deepxiv fa read talent 15023 --level full > hinton.md
deepxiv fa search talent "Geoffrey Hinton" --json | jq '.hits[0].id'
```

| Exit code | |
|---|---|
| `0` | Success |
| `1` | API or network error, including 401 / 403 / 429 / 4xx / 5xx and an `error` event during `ask` |
| `2` | Bad usage: an invalid filter, a malformed `--param`, conflicting options, a bad option value |

## 8. Cost and quota

| Call | Pool | Price |
|---|---|---|
| `domains`, `spec`, `whoami` | — | free |
| `search` | general daily limit | 2 (3 with `--head`) |
| `read` | general daily limit | by level / extra / format; `spec` lists every price (talent: brief 1, detail 3, full 10, extras 1–20) |
| `facets` | general daily limit | 1 |
| `resolve` | general daily limit | 2 |
| `ask` | agentic quota (shared with `deepxiv ask`) | 1 call; **registered key only** |

- The general daily limit is 1,000 for an auto-registered token and 10,000 for a registered key. Registered keys also get 300 agentic calls/day free. See [USAGE.md § Tokens and limits](USAGE.md#tokens-and-limits).
- After each paid call, the CLI prints `💳 cost N · remaining/limit left today` to stderr, and warns when 20 or fewer remain.
- `fa ask` warns when 5 or fewer agentic calls remain (`-v` always shows the count).
- Each key can run at most **4 `ask` calls at once**.
- 1stAuthor's free sample queries and IDs (`spec` → `free_samples`) cost 0.
- For higher limits on the 1stAuthor domains, see [1stauthor.com](https://1stauthor.com).

## 9. Errors and retries

The CLI explains each of these on stderr and exits 1:

| What you see | Why | What to do |
|---|---|---|
| `fa ask` needs a registered account key | 403: SDK token used for `ask` | Register, then `deepxiv config --token …` |
| Authentication failed (401) | Token missing or invalid | `deepxiv token`, or set `DEEPXIV_TOKEN` |
| Daily usage limit reached | 429: general daily limit used up | Wait for tomorrow or register for a higher limit |
| Too many concurrent requests, retry in Ns | 429 with `Retry-After`: more than 4 `ask` calls at once | Wait as told |
| Rate-limited by 1stAuthor | 429 from 1stAuthor's per-user throttle | Slow down |
| `HTTP 400 invalid_request: …` plus a list | Bad extra, level, view or filter | Pick from the list printed below the error |
| `HTTP 404 …` | No document with that ID | Get IDs from `search` / `resolve` |
| `❌ <code>: <message> (quota refunded)` after a partial answer | The `ask` agent failed mid-stream | Retry; the quota was refunded if the message says so |

Automatic retries, before any error is shown:

- A **429 with `Retry-After` ≤ 30 s** is waited out and retried once.
- A **network error on a GET** (`domains`, `spec`, `read`, `facets`, `whoami`) is retried once. POSTs (`search`, `resolve`, `ask`) aren't retried, so you're never charged twice.

## 10. Python API

```python
from deepxiv_sdk import FAClient, FAError, FilterError, Reader, build_filters
```

### `FAClient`

```python
FAClient(token=None, base_url="https://data.rag.ac.cn/fa", timeout=120.0, session=None)
reader.fa()          # the same client, using the Reader's token, base URL and timeout
```

| Method | Endpoint | Returns |
|---|---|---|
| `domains()` | `GET /v1/domains` | `{"domains": [...]}` |
| `spec(domain)` | `GET /v1/{domain}` | the self-description |
| `whoami()` | `GET /v1/whoami` | `{"source", "name", "subject", "quota", "agent", ...}` |
| `search(domain, query, *, top_k, offset, mode, filters, fields, sort)` | `POST /v1/{domain}/search` | `{"hits": [{"id", "score", "brief"}], "total", "warnings", "meta"}` |
| `read(domain, id, *, level, extra, format, **params)` | `GET /v1/{domain}/read/{id}` | `{"data": {...}}` or `{"text": "..."}` (markdown / HTML), plus `meta` |
| `read_many(domain, ids, *, level, extra, params)` | `POST /v1/{domain}/read` | the documents, in one call |
| `doc(domain, id, view=None, **params)` | `GET /v1/{domain}/doc/{id}?view=` | one named view |
| `facets(domain, field, limit=None)` | `GET /v1/{domain}/facets` | `{"values": [{"value", "count"}]}` |
| `resolve(names)` | `POST /v1/talent/resolve` | `{"results": [{"query", "candidates", "resolved"}]}` |
| `ask(query, domain=None, *, effort, **extra)` | `POST /v1/{domain}/ask` or `/v1/ask` | `{"answer", "sources", "stats", "meta"}` |
| `ask_stream(query, domain=None, *, effort, **extra)` | `POST …/ask/stream` | an iterator of event dicts |

- `**params` / `**extra` are passed through, e.g. `read(..., section="荣誉与奖项")`, `ask(..., scope="law")`.
- `fields="head"` is the Python form of `--head`. `sort` is passed through for domains that accept it.
- `client.last_quota` holds the quota headers of the last call: `{"general": {"cost", "used", "daily_limit", "remaining"}, "agent": {"tier", "daily_limit", "used", "remaining"}}`. Each JSON response also carries `meta.quota`.

```python
fa = FAClient(token="...")

spec = fa.spec("talent")
hits = fa.search(
    "talent", "deep learning", top_k=5,
    filters=build_filters(["org=University of Toronto", "h_index>=50"],
                          spec["search"]["filters"]),
)
person = fa.read("talent", hits["hits"][0]["id"], level="brief")
profile_md = fa.read("talent", 15023, level="full")["text"]
honours = fa.read("talent", 15023, level="full", section="荣誉与奖项")
network = fa.read("talent", 15023, extra="network")
cards = fa.read_many("talent", [15023, 3426], level="brief")
fa.facets("talent", "orgs", limit=20)
fa.resolve(["Geoffrey Hinton", "Yann LeCun"])
print(fa.last_quota)

answer = fa.ask("中国个人信息保护法对个人信息出境有什么要求", "law", effort="low", scope="law")
print(answer["answer"])
```

### Streaming

```python
for event in fa.ask_stream("Which researchers at the University of Toronto work on deep learning?"):
    kind = event["event"]
    if kind == "route":
        print("routed to", event["domain"])
    elif kind == "answer_delta":
        print(event["delta"], end="", flush=True)
    elif kind == "sources":
        sources = event["sources"]
    elif kind == "error":                       # arrives with HTTP 200, so always check
        raise RuntimeError(f'{event["code"]}: {event["message"]}')
```

| Event | When | Fields |
|---|---|---|
| `route` | only without a domain, first | `domain` |
| `start` | run starts | `domain`, `effort`, `max_rounds` |
| `tool_call` / `tool_result` / `warning` | while the agent works (not every domain emits them) | tool name, arguments, summary |
| `answer_start` | before the first token | — |
| `answer_delta` | repeatedly | `delta` |
| `sources` | after the answer | `sources` (grouped by kind), `citation_format` |
| `done` | end | `stats` (`rounds`, `tool_calls`, `elapsed_s`, `answer_truncated`, …) |
| `error` | on failure, instead of the rest | `code`, `message`, `refunded` |

### Errors

```python
try:
    fa.ask("…", "talent")
except FAError as e:
    e.status                # HTTP status (None for network errors and stream interruptions)
    e.code                  # 1stAuthor error code, e.g. "invalid_request"; None for deepxiv's own errors
    e.message               # readable message
    e.details               # e.g. {"extras": [...]} or {"allowed": [...]}
    e.retry_after           # seconds, from Retry-After
    e.request_id            # for support
    e.needs_registered_key  # True for the 403 an SDK token gets from ask
```

`FAError` is a subclass of `deepxiv_sdk.APIError`.

### Filter helpers

```python
build_filters(["org=University of Toronto", "h_index>=50"], schema)   # → filter dict
build_filters(["year=2024"], None)                                    # no schema: shape-based coercion only
```

`schema` is `spec(domain)["search"]["filters"]`. An invalid expression raises `FilterError` (a `ValueError`).

## 11. HTTP API

Without Python, call the same endpoints with your deepxiv token:

```bash
BASE=https://data.rag.ac.cn/fa
AUTH="Authorization: Bearer $DEEPXIV_TOKEN"

curl -H "$AUTH" $BASE/v1/domains
curl -H "$AUTH" $BASE/v1/talent
curl -H "$AUTH" -H 'Content-Type: application/json' \
     -d '{"query": "deep learning", "top_k": 5, "filters": {"org": "University of Toronto", "h_index": {"gte": 50}}}' \
     $BASE/v1/talent/search
curl -H "$AUTH" "$BASE/v1/talent/read/15023?level=brief"
curl -H "$AUTH" -H 'Content-Type: application/json' -d '{"ids": ["15023", "3426"], "level": "brief"}' $BASE/v1/talent/read
curl -H "$AUTH" "$BASE/v1/talent/doc/15023?view=scholar"
curl -H "$AUTH" "$BASE/v1/talent/facets?field=orgs&limit=20"
curl -H "$AUTH" -H 'Content-Type: application/json' -d '{"names": ["Geoffrey Hinton"]}' $BASE/v1/talent/resolve
curl -N -H "$AUTH" -H 'Content-Type: application/json' -d '{"query": "Who is Yann LeCun?", "effort": "low"}' $BASE/v1/talent/ask/stream
curl -H "$AUTH" $BASE/v1/whoami
```

- Responses carry `meta.quota` and `X-DeepXiv-Quota-Cost / -Used / -Daily-Limit / -Remaining` headers; ask responses also carry `X-DeepXiv-Agent-Tier / -Daily-Limit / -Used / -Remaining`.
- Errors come in two shapes: `{"detail": "..."}` from deepxiv (auth, quota, ask eligibility) and `{"error": {"code", "message", "details"}, "request_id"}` from 1stAuthor.
- `ask/stream` returns NDJSON with the events listed above.

## 12. Migrating from `deepxiv talent`

`deepxiv talent search` and `deepxiv talent survey` still work for one release, as deprecated aliases that print a warning:

| Old | New |
|---|---|
| `deepxiv talent search "query"` | `deepxiv fa search talent "query"` |
| `--limit N` / `--offset N` | `--top-k N` / `--offset N` |
| `--tags A,B` / `--career-stage S` | `-F areas=A,B` / `-F career_stage=S` |
| `--semantic`, `--sort`, `--order`, `--investigated`, `-v` | ignored: search is always hybrid now |
| `--format json` / `--json` | `--json` |
| `deepxiv talent survey ID` | `deepxiv fa read talent ID` |
| `survey --format markdown` | `fa read talent ID --level full` |
| `survey --refresh` / `--no-refresh` | ignored; for live Scholar numbers use `fa read talent ID --extra scholar_live` |
| `Reader.talent_search(q, limit=, offset=)` | `Reader.fa().search("talent", q, top_k=, offset=)` |
| `Reader.talent_survey(id)` | `Reader.fa().read("talent", id)` |

**Person IDs from the old talent index don't carry over.** Look people up again with `fa search talent` or `fa resolve`.

## 13. Troubleshooting

- **A filter is rejected.** Field names are per domain. Use `deepxiv fa spec DOMAIN` for the fields and `deepxiv fa facets DOMAIN FIELD` for the exact values.
- **A filter returns nothing.** Values must match exactly. `facets` shows the indexed spelling; for example `orgs` mixes Chinese and English names.
- **`fa read talent` says not found.** IDs come from `fa search talent` or `fa resolve`. Old talent IDs, arXiv IDs and Scholar IDs don't work.
- **`--level full` returns 404 for a person.** Their card has `has_profile: false`, so only card-level data exists.
- **`--format html` still prints JSON.** That domain has no HTML rendering; `spec --json` → `read.formats` lists what exists.
- **`standards` hits have no body.** That domain is catalogue metadata only.
- **`fa ask` without `--domain` gives an odd error.** The router may have picked a domain the service doesn't allow. Pass `--domain` explicitly.
- **Anything else.** [Open an issue](https://github.com/DeepXiv/deepxiv_sdk/issues). Both deepxiv and 1stAuthor's domains are in beta.
