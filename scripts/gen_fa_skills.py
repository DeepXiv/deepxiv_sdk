#!/usr/bin/env python3
"""Generate one deepxiv skill per 1stAuthor domain from the live `fa spec`.

1stAuthor publishes HTTP-flavoured skills at https://1stauthor.com/skills/.
These are the same self-descriptions (`GET /v1/{domain}`, i.e.
`deepxiv fa spec DOMAIN --json`) rendered as `deepxiv fa` commands, plus
hand-written recipes and trigger descriptions kept below.

    python scripts/gen_fa_skills.py            # write skills/deepxiv-fa-*/SKILL.md
    python scripts/gen_fa_skills.py --check    # also run every recipe (no asks)

Needs a deepxiv token (DEEPXIV_TOKEN or ~/.env). Re-run when 1stAuthor changes a domain.
"""

import argparse
import datetime
import os
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from deepxiv_sdk import Reader  # noqa: E402
from deepxiv_sdk.cli import get_token  # noqa: E402

SKILLS = ROOT / "skills"

# Trigger descriptions: what an agent sees when deciding whether to load the skill.
DESCRIPTIONS = {
    "talent": "Find and read AI researcher profiles with the deepxiv CLI: by name (Chinese, pinyin, English), organisation, role, area, location or h-index; education, career, top papers, coauthors. Use when asked who works on something, to build a list of researchers or students, or about a specific researcher.",
    "appraise": "Find which academicians and society fellows (CAS, CAE, NAS, NAE, Royal Society, ACM, IEEE, AAAI …) cited a paper and what they actually said, with the citing sentence, type and stance. Use for grant reports, promotion dossiers, or any 'who of note praised this paper' question.",
    "law": "Search and read statutes from China and 25 other jurisdictions at article level, and ask cited legal questions over statutes plus judgments. Use when a task needs the text of a Chinese (or other national) law, regulation or article.",
    "cases": "Search Chinese and US court judgments (17M+ Chinese, 3.4M US) and read their extracted fields: claims, facts, reasoning, outcome, legal basis, sentencing. Use when a task needs how courts ruled on similar facts, or a specific case by number or name.",
    "us_law": "Search ~5M US legal provisions: federal and state statutes, regulations (CFR), session laws, agency decisions, guidance. Use when a task needs the text of a US law or rule, or obligations and penalties under it.",
    "uk_eu_law": "Search about 52k UK and EU legal instruments (EUR-Lex regulations, directives, decisions; UK Acts and SIs) with extracted obligations, penalties and summaries. Use when a task needs UK or EU legislation, e.g. GDPR articles.",
    "trials": "Search all ~607k ClinicalTrials.gov studies by condition, phase, status, sponsor, country, with eligibility and biomarkers extracted. Use when a task needs clinical trials for a drug, disease or target.",
    "drugs": "Search ~257k US drug labels (openFDA SPL): indications, contraindications, interactions, boxed warnings, pharmacologic class. Use when a task needs what a US drug label says.",
    "grants": "Search ~1.3M research grants: NSF awards, NIH projects and EU CORDIS projects, with amounts, PIs, organisations and topics. Use when a task needs who funds what, funding trends, or a PI's awards.",
    "filings": "Search ~1.3M US and Chinese corporate filings: SEC 8-K / 10-K / 10-Q / 13D / proxy / comment letters, Chinese periodic reports and announcements, exchange inquiries and CSRC penalties. Use when a task needs what a company disclosed.",
    "stocks": "Point-in-time US equity data for 8,000+ tickers: daily prices vs sector and SPY, per-ticker news and event clusters, SEC filings, XBRL financials, macro series and the daily macro digest, all replayable with as_of. Use for questions about a US stock, a market theme, or US macro data.",
    "standards": "Look up Chinese national standards (GB, GB/T, GB/Z): code, title, status, dates, ICS class. Metadata only, no full text. Use when a task needs which Chinese standard applies or whether it is in force.",
    "cve": "Search ~390k public vulnerabilities (NVD) with CISA KEV exploited-in-the-wild flags and EPSS exploitation probability. Use when a task needs vulnerabilities in a product, or which ones are being exploited now.",
    "osv": "Search ~200k open-source package advisories not covered by CVE, mostly malicious-package reports (npm, PyPI …) with behaviours, impersonated packages and IOCs. Use when checking whether a package is malicious or for supply-chain advisories.",
    "fr": "Search 1.0M US Federal Register documents (1994–): rules, proposed rules, notices, presidential documents, with agencies, action kind and dates. Use when a task needs what a US agency published or proposed.",
}

# Hand-written recipes, run against production by --check. Asks are listed but not run.
RECIPES = {
    "talent": [
        ('deepxiv fa search talent "Yann LeCun" -k 3', "a name: English, Chinese, pinyin or \"Last, First\""),
        ('deepxiv fa search talent "具身智能" -F org=清华大学 -F role=教授 -F "h_index>=30" -k 10', "Chinese institutions take Chinese values"),
        ('deepxiv fa search talent "world model" -F career_stage=student -F location=北京,上海 -k 20', "location values are Chinese city names: 北京, 上海"),
        ("deepxiv fa read talent 15023 3426 2813 -l brief", "several cards in one call"),
        ("deepxiv fa read talent 15023 -e network", "coauthors"),
        ('deepxiv fa resolve "Geoffrey Hinton" "Yann LeCun"', "names → person_id, batch"),
        ('deepxiv fa ask "who works on self-supervised learning at Mila" -d talent', None),
    ],
    "appraise": [
        ('deepxiv fa search appraise "DeepSeek-R1" -k 3', "→ arxiv:2501.12948"),
        ("deepxiv fa read appraise arxiv:2501.12948 -l brief", "counts and stance breakdown"),
        ("deepxiv fa read appraise arxiv:2501.12948 -p stance=positive -p org=CAS,CAE", "positive sentences from Chinese academicians"),
        ('deepxiv fa ask "DeepSeek-R1 得到了哪些院士的正面评价" -d appraise -p paper=arxiv:2501.12948', None),
    ],
    "law": [
        ('deepxiv fa search law "刑法第266条" -k 3', "statute + article number locates directly"),
        ('deepxiv fa search law "个人信息出境" -F jurisdiction=CHN -F status=in_force -k 5', None),
        ("deepxiv fa read law 刑法 -l brief", None),
        ('deepxiv fa ask "个人信息出境需要满足什么条件" -d law -e medium', None),
    ],
    "cases": [
        ('deepxiv fa search cases "网络刷单诈骗 未遂" -F province=浙江省 -F "judge_year>=2018" -k 5', None),
        ('deepxiv fa search cases "qualified immunity police" -F country=us -F court_level=scotus -k 5', "US cases filter on year, not judge_year"),
        ("deepxiv fa read cases us:10316651 -l brief", "TikTok v. Garland; the holding comes in English and Chinese"),
        ("deepxiv fa read cases 8a1c3791-0cce-4094-9b28-a9a600b657c7", "detail: every extracted field, no grant needed"),
        ('deepxiv fa ask "网络刷单诈骗未遂一般怎么判" -d cases', "answers from Chinese judgments only"),
    ],
    "us_law": [
        ('deepxiv fa search us_law "data breach notification" -F jurisdiction=ca,ny -k 5', None),
        ('deepxiv fa search us_law "foreign adversary sensitive personal data transfer" -k 3', None),
        ('deepxiv fa search us_law "HIPAA patient records disclosure" -F doc_group=regulation -F has_penalty=true -k 5', None),
        ("deepxiv fa read us_law uslaw:USC_T15_C123_S9901 -l brief", "15 U.S.C. § 9901"),
        ('deepxiv fa ask "What must a company do after a data breach under California law?" -d us_law', None),
    ],
    "uk_eu_law": [
        ('deepxiv fa search uk_eu_law "data protection" -F jurisdiction=eu -k 5', None),
        ('deepxiv fa search uk_eu_law "artificial intelligence high-risk systems" -F kind=REG -F "year>=2020" -k 5', None),
        ("deepxiv fa read uk_eu_law eu:32016R0679 -l brief", "GDPR"),
        ('deepxiv fa ask "Under the GDPR, when may personal data be transferred to a third country?" -d uk_eu_law', None),
    ],
    "trials": [
        ('deepxiv fa search trials "GLP-1 obesity" -F phase=PHASE3 -F overall_status=RECRUITING -k 5', None),
        ("deepxiv fa read trials NCT02082496 -l brief", None),
        ('deepxiv fa ask "recruiting phase 3 trials for pancreatic cancer" -d trials', None),
    ],
    "drugs": [
        ('deepxiv fa search drugs "GLP-1 weight loss" -F has_boxed_warning=true -k 5', None),
        ('deepxiv fa search drugs "anticoagulant" -F route=ORAL -F is_rx=true -k 5', None),
        ("deepxiv fa read drugs f5e548d0-cc79-4c34-a3f5-e20a5b8b6564 -l brief", None),
        ('deepxiv fa ask "Which drugs interact with warfarin according to their labels?" -d drugs', None),
    ],
    "grants": [
        ('deepxiv fa search grants "single-cell transcriptomics" -F agency=nih -F "fy>=2020" -k 5', None),
        ('deepxiv fa search grants "quantum computing" -F agency=nsf -F "amount_total>=1000000" -k 5', None),
        ("deepxiv fa read grants nih:R25HG007515 -l brief", None),
        ('deepxiv fa ask "Which NIH institutes fund single-cell atlas projects, and how much?" -d grants', None),
    ],
    "filings": [
        ('deepxiv fa search filings "CEO resignation" -F market=us -F event_types=officer_director_change -F "filed_year>=2023" -k 5', None),
        ('deepxiv fa search filings "*" -F form=10-Q -F cik=320193 --sort date -k 4', "10-Q is excluded unless you filter on it"),
        ("deepxiv fa read filings us:861838:0001104659-23-092550 -l brief", None),
        ('deepxiv fa ask "Which US companies disclosed a CEO departure in 2024 and why?" -d filings', None),
    ],
    "stocks": [
        ("deepxiv fa read stocks NVDA", "price vs sector ETF and SPY, recent events, news, filings"),
        ("deepxiv fa read stocks NVDA -e news", "the ticker's news feed"),
        ("deepxiv fa read stocks NVDA -e financials", "XBRL financials, as filed"),
        ("deepxiv fa read stocks NVDA -p as_of=2026-09-04", "the same view as of a past day"),
        ('deepxiv fa search stocks "AI data center power" -F source=stocks', "which tickers a theme touches"),
        ('deepxiv fa search stocks "chip export restrictions" -k 5', "news + events + filings, ranked together"),
        ('deepxiv fa search stocks "earnings guidance" -F ticker=TSLA -F source=events', None),
        ("deepxiv fa read stocks digest:macro", "today's macro releases, rates, FX, commodities"),
        ("deepxiv fa read stocks macro:CPIAUCSL", "a macro series with vintages and nowcast"),
        ('deepxiv fa ask "CoreWeave 最近一周为什么大跌？结合价格、新闻和财报说明" -d stocks', "cited analysis"),
    ],
    "standards": [
        ('deepxiv fa search standards "锂离子电池安全" -F state=现行 -k 5', None),
        ('deepxiv fa read standards "GB/T 42729-2023" -l brief', None),
        ('deepxiv fa ask "电动自行车用锂离子电池有哪些强制性国家标准？" -d standards', None),
    ],
    "cve": [
        ('deepxiv fa search cve "palo alto globalprotect rce" -k 5', None),
        ('deepxiv fa search cve "*" -F kev=true -F severity=critical,high --sort epss -k 10', "exploited in the wild, ranked by EPSS"),
        ("deepxiv fa read cve CVE-2024-3400 -l brief", None),
        ('deepxiv fa ask "今天有哪些高危在野利用漏洞" -d cve', None),
    ],
    "osv": [
        ('deepxiv fa search osv "malicious npm package credential theft" -F malicious=true -F ecosystems=npm -k 5', None),
        ('deepxiv fa search osv "*" -F behaviors=credential_theft --sort published -k 5', None),
        ("deepxiv fa read osv MAL-2026-17452 -l brief", None),
        ('deepxiv fa ask "Are there malicious npm packages impersonating popular crypto libraries?" -d osv', None),
    ],
    "fr": [
        ('deepxiv fa search fr "PFAS drinking water" -F doc_type=Rule -k 5', None),
        ('deepxiv fa search fr "artificial intelligence" -F doc_type="Proposed Rule" -F "pub_date>=2024-01-01" --sort pub_date -k 5', None),
        ("deepxiv fa read fr fr:2024-07332 -l brief", None),
        ('deepxiv fa ask "What did EPA finalize on PFAS in drinking water?" -d fr', None),
    ],
}

# How each filter operator is written on the command line.
OP_SYNTAX = {"eq": "`k=v`", "any": "`k=a,b`", "range": "`k>=n`, `k=n..m`", "text": "`k~text`"}


def esc(text):
    return str(text or "").replace("|", "\\|").replace("\n", " ").strip()


def skill_name(domain):
    return "deepxiv-fa-" + domain.replace("_", "-")


def filter_rows(filters, advanced):
    rows = []
    for name, f in filters.items():
        if bool(f.get("advanced")) != advanced:
            continue
        ops = ", ".join(OP_SYNTAX.get(op, op) for op in f.get("ops", []))
        desc = esc(f.get("desc_en") or f.get("desc"))
        values = f.get("values")
        if isinstance(values, list) and values:
            shown = ", ".join(f"`{v}`" for v in values[:8])
            desc += f" Values: {shown}{' …' if len(values) > 8 else ''}."
        rows.append(f"| `{name}` | {f.get('type', '')} | {ops} | {desc} |")
    return rows


def render(domain, spec, today):
    name = spec.get("name") or domain
    search = spec.get("search") or {}
    read = spec.get("read") or {}
    ask = spec.get("ask")
    samples = spec.get("free_samples") or {}
    corpus = spec.get("corpus") or {}
    out = [
        "---",
        f"name: {skill_name(domain)}",
        f"description: {DESCRIPTIONS[domain]}",
        "---",
        "",
        f"# DeepXiv · {name.replace('1stAuthor ', '')} (`{domain}`)",
        "",
        esc(spec.get("description_en") or spec.get("description")),
        "",
    ]
    if isinstance(corpus.get("docs"), int):
        updated = f", updated {corpus['updated_at']}" if corpus.get("updated_at") else ""
        out += [f"Corpus: {corpus['docs']:,} documents{updated}.", ""]

    out += [
        "## Setup",
        "",
        "```bash",
        "pip install -U deepxiv-sdk      # deepxiv registers a token on first use",
        "```",
        "",
        "With a registered key (https://data.rag.ac.cn/register), `search` and `read` are fair use: "
        "60/min, 5 at once, 5,000/day; on the auto-registered token they spend the deepxiv daily limit "
        "at the credits listed below. "
        + ("`ask` draws on the daily ask allowance (resets 00:00 UTC; a site-wide daily total can run out "
           "early at peak times), or 3 lifetime trial asks on the auto-registered token. " if ask else "")
        + "On 429, back off for `Retry-After` seconds. "
        + "Data goes to stdout; cost, quota and sources go to stderr. Exit 0 ok, 1 API error, 2 usage error. "
        "The general CLI guide is the `deepxiv-cli` skill.",
        "",
        "## Start here",
        "",
        "```bash",
    ]
    for cmd, note in RECIPES.get(domain, []):
        out.append(f"{cmd}{'   # ' + note if note else ''}")
    out += ["```", ""]
    if samples:
        bits = []
        if samples.get("ids"):
            bits.append("ids " + ", ".join(f"`{i}`" for i in samples["ids"]))
        if samples.get("queries"):
            bits.append("queries " + ", ".join(f"`{q}`" for q in samples["queries"]))
        out += [f"Free samples: {'; '.join(bits)}.", ""]

    if search:
        modes = ", ".join(search.get("modes") or [])
        credits = search.get("credits") or {}
        out += [
            "## Search",
            "",
            "```bash",
            f'deepxiv fa search {domain} "query" [-F FILTER]... [-k N] [--offset N] [--mode M]'
            + (" [--sort S]" if search.get("sorts") else "") + " [--head] [--json]",
            "```",
            "",
            f"Modes: {modes or 'default'}. Up to {search.get('max_top_k', '?')} hits. "
            f"Cost {credits.get('brief', '?')} (with `--head`: {credits.get('head', '?')}).",
        ]
        if search.get("sorts"):
            sorts = ", ".join(f"`{s}`" for s in dict.fromkeys(search["sorts"]))
            out.append(f"Sorts: {sorts} (default `{search.get('default_sort', 'relevance')}`).")
        out += [
            'An empty query is rejected; use `"*"` to list by filters only. '
            "Filters combine with AND; an undeclared field exits 2.",
            "",
        ]
        filters = search.get("filters") or {}
        main = filter_rows(filters, advanced=False)
        if main:
            out += ["| filter | type | `-F` syntax | meaning |", "|---|---|---|---|", *main, ""]
        adv = [n for n, f in filters.items() if f.get("advanced")]
        if adv:
            out += ["Advanced filters (see `deepxiv fa spec " + domain + "`): "
                    + ", ".join(f"`{n}`" for n in adv) + ".", ""]

    levels = read.get("levels") or {}
    if levels:
        out += [
            "## Read",
            "",
            "```bash",
            f"deepxiv fa read {domain} ID [ID...] [-l brief|detail|full] [-e EXTRA] [-p k=v]... [-f json|md|html]",
            "```",
            "",
            "| level | credits | returns |",
            "|---|---|---|",
        ]
        default = read.get("default_level", "detail")
        for lvl, v in levels.items():
            desc = esc(v.get("desc_en") or v.get("desc"))
            if v.get("requires"):
                desc += f" **Needs the `{v['requires']}` grant on the key** (403 otherwise, not charged)."
            out.append(f"| `{lvl}`{' (default)' if lvl == default else ''} | {v.get('credits', '?')} | {desc} |")
        out.append("")
        extras = read.get("extras") or {}
        if extras:
            out += ["| `-e` extra | credits | returns |", "|---|---|---|"]
            for ex, v in extras.items():
                out.append(f"| `{ex}` | {v.get('credits', '?')} | {esc(v.get('desc_en') or v.get('desc'))} |")
            out.append("")
        out += ["At `-l full`, `-p section=NAME` reads one section and `-p characters=N` the first N characters.", ""]

    facets = spec.get("facets") or []
    if facets:
        out += [
            "## Facets",
            "",
            f"`deepxiv fa facets {domain} FIELD` lists the legal values and counts, free. "
            "Use it instead of guessing a spelling. Fields: " + ", ".join(f"`{f}`" for f in facets) + ".",
            "",
        ]
    if "resolve" in (spec.get("extra_endpoints") or {}):
        out += ["`deepxiv fa resolve NAME [NAME...]` checks a batch of names against the corpus and returns ids.", ""]

    if ask:
        out += [
            "## Ask",
            "",
            "```bash",
            f'deepxiv fa ask "question" -d {domain} [-e low|medium|high] [-p k=v]... [--no-stream] [--json]',
            "```",
            "",
            esc(ask.get("desc_en") or ask.get("desc")),
            "",
            f"Always pass `-d {domain}`: automatic domain picking is still early.",
            "",
        ]
        params = ask.get("extra_params") or {}
        if params:
            out += ["| `-p` param | type | meaning |", "|---|---|---|"]
            for p, v in params.items():
                vals = v.get("values")
                kind = "/".join(vals) if isinstance(vals, list) else v.get("type", "")
                out.append(f"| `{p}` | {kind} | {esc(v.get('desc_en') or v.get('desc'))} |")
            out.append("")
    else:
        out += ["## Ask", "", f"`{domain}` is data only: no `ask`. Search and read, then answer from what you read.", ""]

    notes = spec.get("notes_en") or spec.get("notes") or []
    if notes:
        out += ["## What this corpus will and will not tell you", ""]
        out += [f"- {esc(n)[:600]}" for n in notes]
        out.append("")

    grants = spec.get("grants") or []
    quotas = spec.get("quotas") or []
    if grants or quotas:
        out += ["## Limits", ""]
        out += [f"- Quota `{q['id']}`: {esc(q.get('desc_en') or q.get('desc'))}" for q in quotas]
        out += [f"- Grant `{g['id']}`: {esc(g.get('desc_en') or g.get('desc'))} Issued on request, not self-serve."
                for g in grants]
        out.append("")

    if spec.get("citation_format"):
        out += ["## Citing", "", f"Cite records as `{esc(spec['citation_format'])}`. Say plainly when the corpus has nothing.", ""]

    out += [
        "---",
        "",
        f"Generated by `scripts/gen_fa_skills.py` from `deepxiv fa spec {domain} --json` on {today}. "
        "Field names and prices can change; `deepxiv fa spec " + domain + "` is the live source.",
        "",
    ]
    return "\n".join(out)


def render_index(specs, today):
    out = [
        "# 1stAuthor domains (`deepxiv fa`)",
        "",
        "One skill per domain, generated from the live spec by `scripts/gen_fa_skills.py`. "
        "Load the domain's skill before filtering; `deepxiv fa spec DOMAIN` is the live source.",
        "",
        "| domain | holds | id example | ask | skill |",
        "|---|---|---|---|---|",
    ]
    for domain, spec in specs.items():
        corpus = spec.get("corpus") or {}
        docs = f"{corpus['docs']:,} docs. " if isinstance(corpus.get("docs"), int) else ""
        holds = esc(DESCRIPTIONS[domain].split(". Use ")[0])
        link = f"[{skill_name(domain)}](../../{skill_name(domain)}/SKILL.md)"
        out.append(f"| `{domain}` | {docs}{holds} | `{spec.get('id_example', '')}` | "
                   f"{'yes' if spec.get('ask') else 'no'} | {link} |")
    out += ["", f"Generated on {today}.", ""]
    return "\n".join(out)


def check(domains):
    failed = 0
    for domain in domains:
        for cmd, _ in RECIPES.get(domain, []):
            if " fa ask " in cmd:
                continue
            r = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
            hits = "No hits" not in r.stderr
            ok = r.returncode == 0 and hits
            failed += not ok
            print(f"{'ok  ' if ok else 'FAIL'} {cmd}" + ("" if ok else f"\n     {(r.stderr or r.stdout).strip()[:300]}"))
    return failed


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="run every non-ask recipe against production")
    args = ap.parse_args()

    fa = Reader(token=os.environ.get("DEEPXIV_TOKEN") or get_token(None)).fa()
    domains = [d["id"] for d in fa.domains().get("domains") or []]
    missing = [d for d in domains if d not in DESCRIPTIONS]
    if missing:
        sys.exit(f"New domains need a DESCRIPTIONS / RECIPES entry: {', '.join(missing)}")

    today = datetime.date.today().isoformat()
    specs = {d: fa.spec(d) for d in domains}
    for domain, spec in specs.items():
        path = SKILLS / skill_name(domain) / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(domain, spec, today), encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    index = SKILLS / "deepxiv-cli" / "references" / "fa-domains.md"
    index.write_text(render_index(specs, today), encoding="utf-8")
    print(f"wrote {index.relative_to(ROOT)}")

    if args.check and check(domains):
        sys.exit(1)


if __name__ == "__main__":
    main()
