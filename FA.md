# deepxiv fa — 1stAuthor domains

> **中文版**: [FA.zh.md](FA.zh.md) · Back to [README](README.md) · Full CLI reference: [USAGE.md](USAGE.md)

DeepXiv works closely with [1stAuthor](https://1stauthor.com) to serve data beyond arXiv. `deepxiv fa` reaches 1stAuthor's domains (researchers, statutes, court judgments, clinical trials, drug labels, grants, filings, standards, vulnerabilities, the Federal Register) **with your deepxiv token**. Requests go through `data.rag.ac.cn/fa`, so you never need a separate 1stAuthor key.

DeepXiv itself stays focused on agentic data services for academic papers, and will remain free. If you need higher limits on the 1stAuthor domains, see [1stauthor.com](https://1stauthor.com).

> **Beta.** `deepxiv fa` ships in `1.2.0b1`, source install only, and 1stAuthor is in closed beta. Questions or problems? [Open an issue](https://github.com/DeepXiv/deepxiv_sdk/issues).
>
> ```bash
> pip install git+https://github.com/DeepXiv/deepxiv_sdk.git
> ```

**Contents**: [Domains](#domains) · [Quick start](#quick-start) · [Commands](#commands) · [Filters](#filters) · [Output](#output) · [Cost and quota](#cost-and-quota) · [Errors](#errors) · [Python](#python) · [Migrating from `deepxiv talent`](#migrating-from-deepxiv-talent) · [Troubleshooting](#troubleshooting)

## Domains

| Domain | What's in it | `fa ask` |
|---|---|---|
| `talent` | ~190k AI researchers; ~160k researched profiles (education, career, representative papers, open source), with live Google Scholar metrics | ✅ |
| `law` | ~33k statutes / 1.5M articles from 26 jurisdictions, searched article by article, with Chinese translations | ✅ |
| `us_law` | ~5M clause-level US provisions across 53 jurisdictions: statutes, regulations (CFR), session laws, agency decisions | |
| `cases` | Court judgments: ~17.5M from China and ~3.4M US opinions | |
| `trials` | Every study on ClinicalTrials.gov (~600k), with extracted eligibility, biomarkers and summaries | |
| `drugs` | ~256k US drug labels (openFDA SPL): indications, contraindications, interactions, boxed warnings | |
| `grants` | ~1.2M NSF awards and NIH projects | |
| `filings` | ~1.2M US and Chinese corporate filings and regulatory documents (8-K, 10-K, periodic reports, enforcement) | |
| `standards` | ~79k Chinese national standards (GB / GB/T / GB/Z): catalogue metadata only, no full text | |
| `cve` | ~384k public vulnerabilities (NVD), with CISA KEV and EPSS | |
| `fr` | ~1M Federal Register documents since 1994 | |
| `appraise` | Which academicians and society fellows cited a paper, and what they said about it | ✅ |

The list is live. `deepxiv fa domains` shows the current list and sizes, and `deepxiv fa spec <domain>` shows what each domain can do. Papers and the web aren't here because deepxiv serves them natively (`deepxiv search`, `paper`, `ask`).

## Quick start

```bash
deepxiv fa domains                                    # what's there (free)
deepxiv fa spec talent                                # filters, read levels, prices (free)

deepxiv fa search talent "Geoffrey Hinton"            # look someone up
deepxiv fa read talent 15023                          # read the profile
deepxiv fa search law "personal information protection" --top-k 5
deepxiv fa ask "who are the leading researchers on self-supervised learning" --domain talent
```

The workflow is the same as for papers: **search → read only what you need → ask when you want a synthesized answer.**

## Commands

### `fa domains` / `fa spec DOMAIN` (free)

`spec` is the domain's self-description. It lists the filter fields and their operators, the read levels and extras with their prices, the facet fields, free sample queries, and quickstart calls. Check it before filtering a domain you haven't used.

### `fa search DOMAIN "query"`

```bash
deepxiv fa search talent "Yann LeCun"                                  # names: English, Chinese, pinyin
deepxiv fa search talent "deep learning" -F "org=University of Toronto" -F "h_index>=50"
deepxiv fa search talent "diffusion models" -F career_stage=junior --top-k 20
deepxiv fa search trials "pancreatic cancer" -F overall_status=RECRUITING
deepxiv fa search cve "log4j" --json
```

| Option | |
|---|---|
| `--filter`, `-F EXPR` | Repeatable, combined with AND. See [Filters](#filters) |
| `--top-k`, `-k N` | Number of hits, 1~100 (default 10) |
| `--offset N` | Pagination |
| `--mode MODE` | Retrieval mode, if the domain offers several (e.g. `hybrid`, `dense`, `bm25`, `name` for talent) |
| `--head` | Richer hits (`fields=head`), at a higher price |
| `--json` | Full response |

### `fa read DOMAIN ID [ID ...]`

```bash
deepxiv fa read talent 15023                                  # default level (detail for talent)
deepxiv fa read talent 15023 --level brief                    # the card only, cheapest
deepxiv fa read talent 15023 --level full                     # the full researched profile, markdown
deepxiv fa read talent 15023 --level full -p section=荣誉与奖项  # one section of it
deepxiv fa read talent 15023 --extra network                  # coauthors, advisors, students
deepxiv fa read talent 15023 --format html > hinton.html      # a rendered page
deepxiv fa read talent 15023 3426 --level brief               # several ids in one call
```

| Option | |
|---|---|
| `--level`, `-l` | `brief` / `detail` / `full`; the domain's default if omitted |
| `--extra`, `-e NAME` | One extra facet (talent: `papers`, `network`, `scholar`, `scholar_live`, `sources`, …) |
| `--view NAME` | Read a named view instead (`GET /doc/{id}?view=…`) |
| `--format`, `-f` | `json` / `md` / `html`: server-side rendering |
| `--param`, `-p k=v` | Extra query parameter, repeatable (e.g. `section=…`, `contact=1`) |
| `--json` | Full response instead of just the document |

Start at `--level brief` and go deeper only when the brief isn't enough. A `full` read costs several times a `brief` one.

### `fa facets DOMAIN FIELD`

Value counts for a filter field, useful for finding the exact spelling to use in `-F`:

```bash
deepxiv fa facets talent orgs --limit 20
deepxiv fa facets talent career_stage
```

### `fa resolve NAME [NAME ...]`

Batch-match person names (paper authors, a team page) to talent ids, up to 50 per call:

```bash
deepxiv fa resolve "Geoffrey Hinton" "Yann LeCun" "Yoshua Bengio"
```

### `fa ask "question"`

A cited answer over one domain. An agent searches and reads the domain for you.

```bash
deepxiv fa ask "who are the leading researchers on self-supervised learning" --domain talent
deepxiv fa ask "what conditions apply to cross-border transfer of personal information under Chinese law" --domain law --effort high
deepxiv fa ask "which academicians cited Attention Is All You Need, and what did they say"   # no --domain: auto-routed
```

| Option | |
|---|---|
| `--domain`, `-d` | Domain to ask. Without it, 1stAuthor routes the question and stderr shows `🧭 routed to …` |
| `--effort`, `-e` | `low` / `medium` / `high` |
| `--no-stream` | Wait for the whole answer |
| `--no-sources` | Skip the sources list |
| `--verbose`, `-v` | Progress, tool calls and quota on stderr |
| `--json` | One JSON object (non-streaming) |

Needs a **registered key**. See [Cost and quota](#cost-and-quota).

### `fa whoami` (free)

Shows which token is in use (auto-registered SDK token or registered key), today's general quota, and, for registered keys, the agentic quota.

## Filters

`-F` takes one expression per flag, and flags combine with AND:

| Syntax | Meaning | Sent as |
|---|---|---|
| `k=v` | equals | `{"k": "v"}` |
| `k=a,b` | any of | `{"k": ["a", "b"]}` |
| `k>=n`, `k<=n` | bound | `{"k": {"gte": n}}` / `{"k": {"lte": n}}` |
| `k=n..m` | inclusive range (dates too: `2024-01..2024-06`) | `{"k": {"gte": n, "lte": m}}` |
| `k~text` | full-text match | `{"k": {"text": "text"}}` |

Field names, types and allowed operators differ per domain and come from `deepxiv fa spec DOMAIN`. The CLI checks your filters against the spec before sending, so an unknown field or a disallowed operator fails immediately with the list of valid fields, without spending quota. Quote expressions containing `>` or `<` so the shell doesn't treat them as redirects.

## Output

The output split is the same as `deepxiv ask`:

- **stdout**: the data: hits, the document, the answer.
- **stderr**: quota (`💳 cost 2 · 990/1000 left today`), routing, sources, hints and warnings.

So `deepxiv fa read talent 15023 --level full > hinton.md` captures only the profile. `--json` prints the full response, including `meta.quota`.

## Cost and quota

| Call | Pool | Price |
|---|---|---|
| `domains`, `spec`, `whoami` | — | free |
| `search` | general daily limit | 2 (3 with `--head`) |
| `read` | general daily limit | by level / extra / format (talent: brief 1, detail 3, full 10). `spec` lists every price |
| `facets` | general daily limit | 1 |
| `resolve` | general daily limit | 2 |
| `ask` | agentic quota (shared with `deepxiv ask`) | 1 call; **registered key only** |

- Any token works for everything except `ask`, including the token deepxiv auto-registers on first use.
- `ask` returns **403** on an auto-registered token. Register at [data.rag.ac.cn/register](https://data.rag.ac.cn/register), then run `deepxiv config --token YOUR_KEY`. Registered keys get 300 agentic calls/day free.
- Each key can run at most **4 `ask` calls at once**.
- Some of 1stAuthor's free sample queries cost 0.

For higher limits on the 1stAuthor domains, see [1stauthor.com](https://1stauthor.com).

## Errors

The CLI explains each of these on stderr and exits 1:

| What you see | Why | What to do |
|---|---|---|
| `fa ask` needs a registered account key | 403: SDK token used for `ask` | Register, then `deepxiv config` |
| Authentication failed (401) | Token missing or invalid | `deepxiv token`, or set `DEEPXIV_TOKEN` |
| Daily usage limit reached | 429: general daily limit used up | Wait for tomorrow or register for a higher limit |
| Too many concurrent requests, retry in Ns | 429: more than 4 `ask` calls at once | Wait as told |
| Rate-limited by 1stAuthor | 429: 1stAuthor's per-user throttle | Slow down |
| `HTTP 400 invalid_request: …` plus a list | Bad extra, level or filter | Pick from the list printed below the error |
| `❌ <code>: <message> (quota refunded)` after a partial answer | The `ask` agent failed mid-stream | Retry. The quota was refunded if the message says so |

## Python

```python
from deepxiv_sdk import FAClient, FAError, Reader, build_filters

fa = FAClient(token="...")                      # or Reader(token="...").fa()

fa.domains()                                    # free
spec = fa.spec("talent")                        # free

hits = fa.search(
    "talent", "deep learning", top_k=5,
    filters=build_filters(["org=University of Toronto", "h_index>=50"],
                          spec["search"]["filters"]),
)
person = fa.read("talent", hits["hits"][0]["id"], level="brief")
fa.read("talent", 15023, level="full")          # {"text": "# Geoffrey Hinton …"}
fa.read("talent", 15023, extra="network")
fa.read_many("talent", [15023, 3426], level="brief")
fa.facets("talent", "orgs", limit=20)
fa.resolve(["Geoffrey Hinton", "Yann LeCun"])
fa.whoami()

print(fa.last_quota)    # {"general": {"cost", "used", "daily_limit", "remaining"}, "agent": {...}}

# Registered key only
answer = fa.ask("who are the leading researchers on self-supervised learning", "talent")

for event in fa.ask_stream("which academicians cited Attention Is All You Need"):  # no domain: routed
    kind = event["event"]
    if kind == "route":
        print("routed to", event["domain"])
    elif kind == "answer_delta":
        print(event["delta"], end="")
    elif kind == "error":                       # arrives with HTTP 200, so check for it
        raise RuntimeError(event["message"])

try:
    fa.ask("…", "talent")
except FAError as e:
    if e.needs_registered_key:
        print("register at https://data.rag.ac.cn/register")
    else:
        print(e.status, e.code, e.message, e.details, e.retry_after)
```

The stream events arrive in order: `route` (only without a domain) → `start` → `answer_start` → `answer_delta`… → `sources` → `done`. A failure after the stream opened arrives as `{"event": "error", "code", "message", "refunded"}`.

## Migrating from `deepxiv talent`

`deepxiv talent search` and `deepxiv talent survey` still work for one release, as deprecated aliases that print a warning:

| Old | New |
|---|---|
| `deepxiv talent search "query"` | `deepxiv fa search talent "query"` |
| `--tags A,B` / `--career-stage S` | `-F areas=A,B` / `-F career_stage=S` |
| `--semantic`, `--sort`, `--order`, `--investigated` | ignored: search is always hybrid now |
| `deepxiv talent survey ID` | `deepxiv fa read talent ID` |
| `survey --format markdown` | `fa read talent ID --level full` |
| `survey --refresh` | `fa read talent ID --extra scholar_live` (live Scholar numbers) |
| `Reader.talent_search(q)` / `talent_survey(id)` | `Reader.fa().search("talent", q)` / `.read("talent", id)` |

**Person IDs from the old talent index don't carry over.** Look people up again with `fa search talent` or `fa resolve`.

## Troubleshooting

- **A filter is rejected.** Field names are per domain. Use `deepxiv fa spec DOMAIN` for the fields and `deepxiv fa facets DOMAIN FIELD` for the exact values.
- **`fa read talent` says not found.** IDs come from `fa search talent` or `fa resolve`. Old talent IDs, arXiv IDs and Scholar IDs don't work.
- **`--level full` returns 404 for a person.** Their card has `has_profile: false`, so only card-level data exists.
- **`standards` hits have no body.** That domain is catalogue metadata only.
- **Anything else.** [Open an issue](https://github.com/DeepXiv/deepxiv_sdk/issues). Both deepxiv and 1stAuthor's domains are in beta.
