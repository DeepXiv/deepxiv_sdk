# 1stAuthor domains (`deepxiv fa`)

One skill per domain, generated from the live spec by `scripts/gen_fa_skills.py`. Load the domain's skill before filtering; `deepxiv fa spec DOMAIN` is the live source.

| domain | holds | id example | ask | skill |
|---|---|---|---|---|
| `law` | 1,539,593 docs. Search and read statutes from China and 25 other jurisdictions at article level, and ask cited legal questions over statutes plus judgments | `刑法` | yes | [deepxiv-fa-law](../../deepxiv-fa-law/SKILL.md) |
| `cases` | 27,580,773 docs. Search Chinese and US court judgments (17M+ Chinese, 3.4M US) and read their extracted fields: claims, facts, reasoning, outcome, legal basis, sentencing | `8a1c3791-0cce-4094-9b28-a9a600b657c7` | yes | [deepxiv-fa-cases](../../deepxiv-fa-cases/SKILL.md) |
| `us_law` | 5,195,942 docs. Search ~5M US legal provisions: federal and state statutes, regulations (CFR), session laws, agency decisions, guidance | `uslaw:CFRANN_2024_T42_P2_S2_33` | yes | [deepxiv-fa-us-law](../../deepxiv-fa-us-law/SKILL.md) |
| `uk_eu_law` | 51,737 docs. Search about 52k UK and EU legal instruments (EUR-Lex regulations, directives, decisions; UK Acts and SIs) with extracted obligations, penalties and summaries | `eu:32016R0679` | yes | [deepxiv-fa-uk-eu-law](../../deepxiv-fa-uk-eu-law/SKILL.md) |
| `trials` | 607,168 docs. Search all ~607k ClinicalTrials.gov studies by condition, phase, status, sponsor, country, with eligibility and biomarkers extracted | `NCT02082496` | yes | [deepxiv-fa-trials](../../deepxiv-fa-trials/SKILL.md) |
| `drugs` | 256,993 docs. Search ~257k US drug labels (openFDA SPL): indications, contraindications, interactions, boxed warnings, pharmacologic class | `f5e548d0-cc79-4c34-a3f5-e20a5b8b6564` | yes | [deepxiv-fa-drugs](../../deepxiv-fa-drugs/SKILL.md) |
| `grants` | 1,313,241 docs. Search ~1.3M research grants: NSF awards, NIH projects and EU CORDIS projects, with amounts, PIs, organisations and topics | `nih:R25HG007515` | yes | [deepxiv-fa-grants](../../deepxiv-fa-grants/SKILL.md) |
| `filings` | 1,318,627 docs. Search ~1.3M US and Chinese corporate filings: SEC 8-K / 10-K / 10-Q / 13D / proxy / comment letters, Chinese periodic reports and announcements, exchange inquiries and CSRC penalties | `us:861838:0001104659-23-092550` | yes | [deepxiv-fa-filings](../../deepxiv-fa-filings/SKILL.md) |
| `stocks` | Point-in-time US equity data for 8,000+ tickers: daily prices vs sector and SPY, per-ticker news and event clusters, SEC filings, XBRL financials, macro series and the daily macro digest, all replayable with as_of | `AAPL` | no | [deepxiv-fa-stocks](../../deepxiv-fa-stocks/SKILL.md) |
| `standards` | 79,787 docs. Look up Chinese national standards (GB, GB/T, GB/Z): code, title, status, dates, ICS class. Metadata only, no full text | `GB/T 42729-2023` | yes | [deepxiv-fa-standards](../../deepxiv-fa-standards/SKILL.md) |
| `talent` | 191,238 docs. Find and read AI researcher profiles with the deepxiv CLI: by name (Chinese, pinyin, English), organisation, role, area, location or h-index; education, career, top papers, coauthors | `7870` | yes | [deepxiv-fa-talent](../../deepxiv-fa-talent/SKILL.md) |
| `appraise` | 284,124 docs. Find which academicians and society fellows (CAS, CAE, NAS, NAE, Royal Society, ACM, IEEE, AAAI …) cited a paper and what they actually said, with the citing sentence, type and stance | `arxiv:2402.03216` | yes | [deepxiv-fa-appraise](../../deepxiv-fa-appraise/SKILL.md) |
| `cve` | 390,242 docs. Search ~390k public vulnerabilities (NVD) with CISA KEV exploited-in-the-wild flags and EPSS exploitation probability | `CVE-2024-3400` | yes | [deepxiv-fa-cve](../../deepxiv-fa-cve/SKILL.md) |
| `osv` | 199,701 docs. Search ~200k open-source package advisories not covered by CVE, mostly malicious-package reports (npm, PyPI …) with behaviours, impersonated packages and IOCs | `MAL-2026-17452` | yes | [deepxiv-fa-osv](../../deepxiv-fa-osv/SKILL.md) |
| `fr` | 1,008,597 docs. Search 1.0M US Federal Register documents (1994–): rules, proposed rules, notices, presidential documents, with agencies, action kind and dates | `fr:2024-07332` | yes | [deepxiv-fa-fr](../../deepxiv-fa-fr/SKILL.md) |

Generated on 2026-10-19.
