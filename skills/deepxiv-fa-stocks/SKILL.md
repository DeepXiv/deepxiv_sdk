---
name: deepxiv-fa-stocks
description: Point-in-time US equity data for 8,000+ tickers: daily prices vs sector and SPY, per-ticker news and event clusters, SEC filings, XBRL financials, macro series and the daily macro digest, all replayable with as_of. Use for questions about a US stock, a market theme, or US macro data.
---

# DeepXiv · 美股数据 (`stocks`)

NASDAQ point-in-time US equity data. US equities: prices, news, SEC filings, insider trades, financials, macro series and events, all with as_of point-in-time replay (only data visible at that moment).

## Setup

```bash
pip install -U deepxiv-sdk      # deepxiv registers a token on first use
```

`search` and `read` spend the deepxiv daily limit at the credits listed below. Data goes to stdout; cost, quota and sources go to stderr. Exit 0 ok, 1 API error, 2 usage error. The general CLI guide is the `deepxiv-cli` skill.

## Start here

```bash
deepxiv fa read stocks NVDA   # price vs sector ETF and SPY, recent events, news, filings
deepxiv fa read stocks NVDA -e news   # the ticker's news feed
deepxiv fa read stocks NVDA -e financials   # XBRL financials, as filed
deepxiv fa read stocks NVDA -p as_of=2026-09-04   # the same view as of a past day
deepxiv fa search stocks "AI data center power" -F source=stocks   # which tickers a theme touches
deepxiv fa search stocks "chip export restrictions" -k 5   # news + events + filings, ranked together
deepxiv fa search stocks "earnings guidance" -F ticker=TSLA -F source=events
deepxiv fa read stocks digest:macro   # today's macro releases, rates, FX, commodities
deepxiv fa read stocks macro:CPIAUCSL   # a macro series with vintages and nowcast
```

Free samples: ids `AAPL`, `NVDA`, `macro:CPIAUCSL`; queries `chip export restrictions`, `cloud server`.

## Search

```bash
deepxiv fa search stocks "query" [-F FILTER]... [-k N] [--offset N] [--mode M] [--head] [--json]
```

Modes: keyword. Up to 100 hits. Cost 2 (with `--head`: 3).
An empty query is rejected; use `"*"` to list by filters only. Filters combine with AND; an undeclared field exits 2.

| filter | type | `-F` syntax | meaning |
|---|---|---|---|
| `source` | keyword | `k=v` | What to search: all (default; news + events + filings ranked together, and the first page also returns `stocks`: the top 5 matching tickers) \| news \| events \| filings \| stocks (find stocks by theme / business) \| insiders (time-ordered only) Values: `all`, `news`, `events`, `filings`, `stocks`, `insiders`. |
| `ticker` | keyword | `k=v` | Ticker symbol |
| `as_of` | keyword | `k=v` | Point in time (ISO date or datetime), passed through unchanged |
| `date` | datetime | `k>=n`, `k=n..m` | Time range {gte, lte} → upstream from / to |

Advanced filters (see `deepxiv fa spec stocks`): `news_kind`, `form`, `event_type`, `semantic`, `with_returns`, `side`, `min_value`.

## Read

```bash
deepxiv fa read stocks ID [ID...] [-l brief|detail|full] [-e EXTRA] [-p k=v]... [-f json|md|html]
```

| level | credits | returns |
|---|---|---|
| `brief` | 1 | Ticker overview: latest price, recent events, news, filings |
| `detail` (default) | 1 | Ticker overview: latest price, recent events, news, filings |
| `full` | 2 | Ticker digest input (every item carries a citable id; built on demand, ~45 s) |

| `-e` extra | credits | returns |
|---|---|---|
| `prices` | 1 | Prices: interval=1d \| 1m (IEX minute bars) |
| `financials` | 1 | Financials (XBRL, as filed; later restatements hidden) |
| `events` | 1 | Events (merged from news / 8-K / Form 4) |
| `news` | 1 | News |
| `filings` | 1 | SEC filings |
| `insiders` | 1 | Insider open-market trades (Form 4 P/S) |
| `features` | 2 | Features (price / event derived) |

At `-l full`, `-p section=NAME` reads one section and `-p characters=N` the first N characters.

## Facets

`deepxiv fa facets stocks FIELD` lists the legal values and counts, free. Use it instead of guessing a spelling. Fields: `source`, `news_kind`, `form`, `event_type`, `semantic`, `side`.

## Ask

`stocks` is data only: no `ask`. Search and read, then answer from what you read.

## What this corpus will and will not tell you

- read 的 id：代码（AAPL）、macro:<series>（如 macro:CPIAUCSL）、digest:market、digest:macro，或任一条记录的 id（news:… / evt_… / filing:…）
- search：文字按相关性（filters.source = all \| news \| events \| filings），source=stocks 按主题找股票；query 为 '*' 或全大写代码时按时间倒序列出（insiders 只能这样）
- as_of：search 放 filters.as_of，read 用查询参数 as_of；不带 = 现在。结果缓存 60 秒
- 每条记录带 license（取值和说明见下面的 license · 各行）
- as_of 口径 · prices: daily bar of D visible after D 16:00 ET; 1m IEX bar visible at ts+1min
- as_of 口径 · news: visible_at (live: first_seen_at; backfilled: crawl_at + 336 s)
- as_of 口径 · filings: live 8-K / Form 4: acceptance (or first_seen_at if later); date-only filings: 22:00 ET of the date
- as_of 口径 · financials: XBRL facts with filed date <= as_of (filed date counts from 22:00 ET)
- as_of 口径 · macro: ALFRED vintage at as_of; daily FRED series: value dated X visible from X+1 17:00 ET; Treasury curve from 18:00 ET (backfill) / first seen (live); monthly releases after 16:00 ET on release day for the daily cut
- as_of 口径 · events: cluster/member first_seen_at; partial clusters re-derive direction and summary from visible members
- as_of 口径 · returns: only horizons whose end session closed before as_of
- as_of 口径 · features: row D uses only data visible at D 16:00 ET; rows computed after as_of are recomputed
- as_of 口径 · digest: as_of capped at the end of the session day; each section follows its source rule
- license · sec_public: SEC EDGAR, public
- license · us_gov_public: US federal agencies / Federal Reserve Board, public
- license · cleveland_fed_public: Cleveland Fed nowcast, public
- license · tiingo_licensed: Tiingo news/prices, licensed for redistribution (was tiingo_internal before 2026-10-19)
- license · fed_bank: regional Reserve Bank / FRED-computed series (terms of use)
- license · third_party: copyrighted series redistributed by FRED (ICE BofA, Cboe, Moody's, UMich, S&P, NAR, Freddie Mac)
- license · wire_rss_summary: press-release RSS summaries
- 覆盖缺口 · news history starts 2026-04-19
- 覆盖缺口 · Form 4 before 2026-10-16 arrives with the fadata history (2026-10-23)
- 覆盖缺口 · IEX 1-minute bars from 2026-10-19, focus list only
- 覆盖缺口 · fundamentals: SEC XBRL filers only (no ADRs / funds)
- 覆盖缺口 · analyst signals come from news stance (no broker feed, no consensus)
- macro 序列（read macro:<series>）：{'id': 'A191RL1Q225SBEA', 'title': 'Real Gross Domestic Product', 'frequency': 'Q', 'license': 'us_gov_public'}, {'id': 'AAA', 'title': "Moody's Seasoned Aaa Corporate Bond Yield", 'frequency': 'M', 'license': 'third_party'}, {'id': 'AWHAETP', 'title': 'Average Weekly Hours of All Employees, Total Private', 'frequency': 'M', 'license': 'us_gov_public'}, {'id': 'BAA', 'title': "Moody's Seasoned Baa Corporate Bond Yield", 'frequency': 'M', 'license': 'third_party'}, {'id': 'BAMLC0A0CM', 'title': 'ICE BofA US Corporate Index Option-Adjusted Spread', 'frequency': 'D',
- 上游 1.0-beta（2026-10-19）：license tiingo_internal renamed tiingo_licensed: Tiingo data is now licensed for redistribution; statement timeout (12 s) returns 504 with Retry-After: 60 instead of 500; GET /v1/search and GET /v1/stocks/search results cached for 60 s per parameter set; /v1/meta: base and routes[].free_samples are host-relative paths (no internal address, no doubled /v1)

## Citing

Cite records as `上游每条记录的 id（px: / evt_ / news: / filing: / form4: / fin: / macro:…@vintage）原样引用，并注明 license`. Say plainly when the corpus has nothing.

---

Generated by `scripts/gen_fa_skills.py` from `deepxiv fa spec stocks --json` on 2026-10-19. Field names and prices can change; `deepxiv fa spec stocks` is the live source.
