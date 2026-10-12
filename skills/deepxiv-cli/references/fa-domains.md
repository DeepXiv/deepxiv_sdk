# 1stAuthor domains — field reference

Generated from `deepxiv fa spec <domain> --json` on 2026-10-12. Specs change; when a filter is rejected, re-run `deepxiv fa spec <domain>` — it is free and authoritative.

Costs are units of the deepxiv general daily limit (search per call, read per document). `ask` uses the separate agentic quota: 1 call per question.

| Domain | What | Docs | id (example) |
|---|---|---|---|
| [`talent`](#talent) | AI researcher directory: 189k people, 160k LLM-researched profiles (education, career, representative papers, open source), Google Scholar metrics rendered live | 189,109 | `person_id` (`7870`) |
| [`appraise`](#appraise) | Academic appraisal: which academicians and society fellows have cited a paper, and what they actually said | 284,124 | `target_key` (`arxiv:2402.03216`) |
| [`law`](#law) | 33,103 statutes / 1,539,593 articles from 26 jurisdictions; article-level hybrid retrieval, Chinese translations and per-article extraction (heading, subjects, conditions, consequences, references) | 1,539,593 | `law_id` (`刑法`) |
| [`cases`](#cases) | Court judgments: 17.49M from China (2.65M criminal plus 14.83M civil / administrative / enforcement) and 3.44M US opinions (country=us, tier A) | 27,580,773 | `uuid` (`8a1c3791-0cce-4094-9b28-a9a600b657c7`) |
| [`us_law`](#us_law) | 4,978,029 clause-level US legal provisions across 53 jurisdictions: 2.12M statutes, 1.95M regulations (including CFR annual editions), 425k session laws, 258k agency decisions, 77k proposed regulations, 77k guidance documents, 53k court rules, 13k constitutional provisions | 4,978,029 | `law_id` (`uslaw:CFRANN_2024_T42_P2_S2_33`) |
| [`trials`](#trials) | All 603,730 studies on ClinicalTrials.gov (one per NCT) | 603,730 | `nct_id` (`NCT02082496`) |
| [`drugs`](#drugs) | 256,282 US drug labels (openFDA SPL, latest version per set_id) | 256,282 | `set_id` (`f5e548d0-cc79-4c34-a3f5-e20a5b8b6564`) |
| [`grants`](#grants) | 1,221,279 research awards: 651,041 NSF awards (one per award id) plus 570,238 NIH RePORTER projects (multi-year funding merged per core project number, with per-year amounts) | 1,311,962 | `grant_id` (`nih:R25HG007515`) |
| [`filings`](#filings) | 1,199,147 corporate filings and regulatory documents across US and China, in two layers | 1,199,147 | `doc_id` (`us:861838:0001104659-23-092550`) |
| [`standards`](#standards) | Catalogue of 79,311 Chinese national standards (openstd: mandatory GB / recommended GB/T / guiding GB/Z) | 79,311 | `std_code` (`GB/T 42729-2023`) |
| [`cve`](#cve) | 384k public vulnerabilities (NVD) plus CISA KEV exploited-in-the-wild flags and FIRST EPSS exploitation probability | 386,833 | `doc_id` (`CVE-2024-3400`) |
| [`fr`](#fr) | 1.0M Federal Register documents (1994– ): rules, proposed rules, notices and presidential documents | 1,003,772 | `doc_id` (`fr:2024-07332`) |

## talent

AI researcher directory: 189k people, 160k LLM-researched profiles (education, career, representative papers, open source), Google Scholar metrics rendered live. One document per person; id is person_id.

- **id**: `person_id`, e.g. `7870`
- **search**: modes hybrid, dense, bm25, name; cost 2 (`--head`: 3)
- **read levels** (`-l`): `brief` 1, `detail` 3, `full` 10; default `detail`
- **extras** (`-e`): `scholar` 2, `scholar_live` 20, `papers` 2, `network` 2, `sources` 1, `source` 2
- **facets**: `orgs`, `orgs_current`, `areas`, `role_norm`, `career_stage`, `location`, `last_paper_year`
- **ask params** (`-p`): `top_k`
- **free samples** (cost 0): queries ['Federica Sarro', 'Jürgen Schmidhuber', '软件工程 实证研究'], ids ['7870']

| Filter (`-F`) | Type | Ops | Meaning |
|---|---|---|---|
| `org` | keyword | eq/any | Current organisation, e.g. Tsinghua University; several allowed (past or current: advanced field orgs) |
| `role` | keyword | eq/any/text | Title: the normalised titles match exactly; anything else (or {"text": …}) is a full-text match on the raw ti… |
| `area` | keyword | eq/any | Research area, e.g. embodied AI, RAG; several allowed |
| `location` | keyword | eq/any | Location, e.g. Beijing, Singapore; several allowed |
| `min_h_index` | integer | eq | h-index at least |
| `active_since` | integer | eq | Most recent paper in or after this year (drops inactive people) |
| `names` | text | text | Full-text match on name (zh/en): {"text": "Zhang San"} |
| `name_zh` | text | text | Chinese name |
| `name_en` | text | text | English name |
| `aff_raw` | text | text | Full-text match on the raw affiliation string |
| `orgs` | keyword | eq/any | Normalised organisation (past or current), e.g. Tsinghua University |
| `orgs_current` | keyword | eq/any | Current organisations only |
| `role_norm` | keyword | eq/any | Normalised title |
| `career_stage` | keyword | eq/any | student / junior / senior |
| `areas` | keyword | eq/any | Research areas (tags + interests + OpenAlex topics) |
| `h_index` | integer | eq/range | Google Scholar h-index |
| `citations_all` | integer | eq/range | Total citations |
| `citations_5y` | integer | eq/range | Citations in the last five years |
| `i10_index` | integer | eq/range | i10-index |
| `last_paper_year` | integer | eq/range | Year of the most recent paper |
| `profile_at` | datetime | range | Profile generation time |
| `has_profile` | bool | eq | Has a full profile (raw readable) |
| `has_scholar` | bool | eq | Has a Google Scholar page |

Notes:
- People with has_profile=false carry only name/affiliation-level data; level=full (and its sections) returns 404.
- Common usage is in quickstart: search to look people up or filter them, read (default level=detail) to read one in a single call; other facets via extra=, a human-readable page via format=html; filters marked advanced are there when you need them.
- Facet fields: org / role / area / location / active_since, plus orgs / career_stage (recomputed nightly).
- POST /v1/talent/resolve {names:[…]} checks a batch of names (paper authors, a team page) against the corpus and returns person_ids.
- Name lookup: when the query looks like a person's name (2–4 Chinese characters / 2–4 Latin words), people with that name come first (hit.match="name"); Chinese names are converted to pinyin and Hongjin / Hong Jin / Hong-Jin all match. The response carries name_match: exact (full name matches — a Latin name, or a Chinese name of 3+ characters matched directly) returns only those people; partial (e.g. matched only through pinyin) keeps the normal results after them. mode=name returns only people with that name (ordered by has_profile, then h-index).
- Every [n] in a profile points at an entry in extra=sources; extra=source&n=3 returns the page archived when the profile was researched (text plus the fetch date). Only snapshot=text has readable text — none / blocked (the site refused the crawler) / html (raw page only, add raw=1 for the original HTML) return 404, which is not charged.
- Scholar numbers inside profile.publications are crawl-time values; trust h_index / citations_* in level=brief / detail.
- The closing 'online footprint & contact' section comes from public homepages.

## appraise

Academic appraisal: which academicians and society fellows have cited a paper, and what they actually said. 112k arXiv papers authored by 5,427 fellows and academicians (Chinese Academies, US NAS/NAE, Royal Society / RAEng, ACM / IEEE / AAAI / ACL / AAAS / IAPR / CCF), with 5.26M parsed references and 8.3M citing sentences, each classified by type and stance. The id is the paper being appraised (arXiv id / DOI / title). ask turns the matched sentences into a Chinese appraisal paragraph for grant reports and promotion dossiers, with the English original attached to every claim.

- **id**: `target_key`, e.g. `arxiv:2402.03216`
- **search**: modes hybrid, title; cost 3 (`--head`: 4)
- **read levels** (`-l`): `brief` 1, `detail` 3, `full` 5; default `detail`
- **extras** (`-e`): `honorees` 2
- **facets**: `org`, `bucket`, `type`, `stance`
- **ask params** (`-p`): `paper`, `filters`
- **free samples** (cost 0): queries ['BGE-M3'], ids ['arxiv:2402.03216']

| Filter (`-F`) | Type | Ops | Meaning |
|---|---|---|---|
| `org` | keyword | eq/any | Honour body: CAS / CAE (Chinese academies), NAS / NAE (US), ROYALSOC / RAENG (UK), ACM / IEEE / AAAI / ACL / … |
| `bucket` | keyword | eq/any | Weight class: academy (academicians) / major (ACM, IEEE … fellows) / other |
| `stance` | keyword | eq/any | Stance of the citing sentence (model-assigned): positive / neutral / negative |
| `type` | keyword | eq/any | Citation type (model-assigned): endorse / buildon / exemplar / baseline / resource / critique / motivate / ba… |
| `about_target` | bool | eq | Whether the sentence is about this paper itself rather than a passing mention |
| `min_h_index` | integer | eq | Only people with at least this h-index |
| `honoree` | text | text | Filter by name (zh/en, substring) |
| `citing_year` | integer | eq/range | Year of the citing paper; ranges allowed |
| `affiliation` | text | text | Filter by the citer's affiliation (Google Scholar string, substring) |
| `section` | text | text | Section of the citing paper where the citation appears (substring, e.g. related work) |
| `mentions_name` | bool | eq | Whether the sentence names the method or model |
| `annotated` | bool | eq | Whether the sentence has been annotated (false = raw sentence only) |

Notes:
- Coverage: Covers only arXiv full texts authored by these 5,427 fellows and academicians; their journal-only papers and citations by anyone else are not included. No hit means this set of papers does not cite it — not that the work is uncited.
- Three id forms: arxiv:2402.03216 (bare ids accepted), doi:10.1145/…, and title:<paper title>. The first two are exact lookups (~40ms); title: is a substring match over normalised bibliography text — 3–6 seconds, and papers with similar titles can collide, so the response carries warnings.
- search has no vector index: the query first goes through the papers domain's semantic search to identify the paper (so a title, a model name or a one-line description all work), then the arXiv id is used for lookup. If it picks the wrong paper, read by id instead: read arxiv:<id>.
- type / stance / about_target / claim / zh are model-assigned; the sentence itself is the evidence. Quote the sentence in anything formal. Sentences with annotated=false have not been classified yet.
- level=detail returns only opinionated citation types by default; background citations are more than half the total — use level=full or pass type= to get them.
- How ask writes: early work may become 'early pioneering work' and a baseline 'widely adopted as a comparison baseline', but nothing may be asserted that the original sentence does not say. Every paragraph carries the English original so a reader can check it.
- people[].person_id is the talent domain's id — read talent <person_id> for that person's full profile.
- Attribution: author-year references ('Li et al., 2025') can match several bibliography entries; such sentences are marked ambiguous=true.

## law

33,103 statutes / 1,539,593 articles from 26 jurisdictions; article-level hybrid retrieval, Chinese translations and per-article extraction (heading, subjects, conditions, consequences, references).

- **id**: `law_id`, e.g. `刑法`
- **search**: modes hybrid, dense, bm25; cost 2 (`--head`: 3)
- **read levels** (`-l`): `brief` 1, `detail` 2, `full` 5; default `detail`
- **extras** (`-e`): `cases` 2
- **facets**: `jurisdiction`, `law_type`, `status`, `domain`, `norm_type`
- **ask params** (`-p`): `scope`, `jurisdiction`
- **free samples** (cost 0): queries ['诈骗罪 量刑'], ids ['刑法']

| Filter (`-F`) | Type | Ops | Meaning |
|---|---|---|---|
| `jurisdiction` | keyword | eq/any | ISO3 jurisdiction, e.g. CHN / JPN / GBR / USA / DEU / KOR; several allowed |
| `scope` | keyword | eq | national (default, no local regulations) / all / local |
| `granularity` | keyword | eq | article (default, article-level hits) / law (which statute to look at) |
| `law_id` | keyword | eq | Restrict to one statute: doc_id or Chinese title / short title |
| `law_type` | keyword | eq/any | Instrument type |
| `domain` | keyword | eq/any | Legal domain (domain_global id, see facets) |
| `status` | keyword | eq/any | in_force / repealed / not_yet / unknown |
| `norm_type` | keyword | eq/any | Norm type: obligation / prohibition / penalty / permission / procedure / definition / scope … (see facets) |
| `effective_at` | datetime | range | Effective date range |

Notes:
- law_id accepts a doc_id (jpn:law:労働基準法) or a Chinese title / short title (刑法, 劳动合同法).
- A query like '刑法第266条' (statute + article number) resolves exactly first.
- scope=national by default: local regulations copy national text and are the main source of noise.
- Translations and extractions are model-generated; cite text.src. needs_review=true marks translations of unusual length.
- knowledge_fill in level=brief / detail is model-recalled metadata, not a source.

## cases

Court judgments: 17.49M from China (2.65M criminal plus 14.83M civil / administrative / enforcement) and 3.44M US opinions (country=us, tier A). Brief-level hybrid retrieval with LLM-extracted structured fields; Chinese judgments are readable section by section, US full text waits on the PG store.

- **id**: `uuid`, e.g. `8a1c3791-0cce-4094-9b28-a9a600b657c7`
- **search**: modes hybrid, dense, bm25; cost 2 (`--head`: 3)
- **read levels** (`-l`): `brief` 1, `detail` 2, `full` 5; default `detail`
- **extras** (`-e`): `laws` 2
- **facets**: `cause`, `province`, `court_level`, `trial_round`, `sentence_type`, `circumstance_tags`, `proceeding_type`, `subject_areas`, `disposition`, `prevailing_party`, `precedential_status`, `procedural_posture`
- **ask params** (`-p`): `scope`
- **free samples** (cost 0): queries ['网络刷单诈骗 未遂'], ids ['8a1c3791-0cce-4094-9b28-a9a600b657c7', 'us:577203']

| Filter (`-F`) | Type | Ops | Meaning |
|---|---|---|---|
| `country` | keyword | eq | cn (default, Chinese judgments) / us (US opinions). The two have different fields: filters marked (country=us… |
| `nature` | keyword | eq | criminal / civil / all (default all; country=cn only) |
| `cause` | keyword | eq/any | Cause of action / crime, exact match (see facets) |
| `province` | keyword | eq/any | Province |
| `city` | keyword | eq/any | City |
| `court_level` | keyword | eq/any | Court level. country=cn: 基层 / 中级 / 高级 / 最高 / 专门; country=us: scotus / fed_appellate / fed_district / state_su… |
| `trial_round` | keyword | eq/any | Trial round |
| `decided_at` | datetime | range | Decision date range |
| `judge_year` | integer | range | Decision year range |
| `law_refs` | keyword | eq/any | Cited article key, e.g. CN/刑法/266 |
| `laws` | keyword | eq/any | Cited statute short title, e.g. 刑法 |
| `sentence_type` | keyword | eq/any | Sentence type |
| `sentence_months` | integer | range | Sentence length in months, range |
| `probation` | bool | eq | Probation granted |
| `fine_amount` | integer | range | Fine amount (CNY), range |
| `verdictno` | keyword | eq/any | Exact case number (country=cn). Use this filter rather than the query text: the Postgres layer tokenises Chin… |
| `articles` | keyword | eq/any | Cited provision, to the article (country=cn; full law name + Chinese article number) |
| `law_names` | keyword | eq/any | Cited law, full name (country=cn; laws uses short names) |
| `amount_max` | integer | range | Largest amount in the judgment, range (country=cn, CNY) |
| `org_parties` | keyword | eq/any | Organisation party name (country=cn). Natural persons are not filterable |
| `status` | keyword | eq/any | Document status (country=cn); only the ~2.04M v2 rows have it |
| `district` | keyword | eq/any | District (country=cn; not indexed, slower) |
| `circumstance_tags` | keyword | eq/any | Sentencing circumstances: 自首 / 立功 / 累犯 / 认罪认罚 / 退赃退赔 / 未遂 … |
| `year` | integer | eq/range | Decision year, range (country=us) |
| `proceeding_type` | keyword | eq/any | Proceeding type (country=us) |
| `subject_areas` | keyword | eq/any | Subject area (country=us, closed set of 23) |
| `disposition` | keyword | eq/any | Disposition (country=us, closed set of 12) |
| `prevailing_party` | keyword | eq/any | Prevailing party (country=us) |
| `precedential_status` | keyword | eq/any | Precedential status (country=us) |
| `procedural_posture` | keyword | eq/any | Procedural posture (country=us) |
| `cite_count` | integer | eq/range | Citation count, range (country=us) |
| `court_id` | keyword | eq/any | Court id (country=us, CourtListener) |
| `docket_number` | keyword | eq/any | Docket number (country=us, exact) |
| `statutes_cited` | keyword | eq/any | Statutes cited (country=us, as written) |
| `issue_tags` | keyword | eq/any | Issue tags (country=us, open model-generated labels) |
| `party_names` | keyword | eq/any | Party names (country=us) |
| `standard_of_review` | keyword | eq/any | Standard of review (country=us) |
| `holding_by` | keyword | eq | Which model produced the holding (atria overrides gemma) |
| `citation_norm` | keyword | eq/any | Normalised citation (country=us) |
| `tier` | keyword | eq | Layer (country=us): a = the 3.44M in the vector index; b = the long tail, Postgres only |
| `jurisdiction` | keyword | eq/any | Jurisdiction code (country=us, CourtListener: F / FD / FS / S / SA / ST) |

Notes:
- China: 2.65M criminal judgments fully extracted, mostly 2014–2019 (2020–2021 nearly empty); 14.83M civil / administrative / enforcement judgments finished ingesting on 2026-10-07. US (country=us): tier A only (3.44M); the ~6.63M tier-B long tail is not indexed. Every response carries coverage.
- A case number in the query resolves exactly first.
- For the verdict and sentence trust level=full&section=decision; level=brief / detail are extractions.
- country=us ids look like us:577203 — reading one needs no country parameter; full text (level=full / section / preview) is not available yet, pending the move of the opinion store into PG.
- US holdings, issues and dispositions are model-extracted; cite CourtListener for anything formal.
- Ask goes through /v1/law/ask (scope=case, Chinese judgments only for now).

## us_law

4,978,029 clause-level US legal provisions across 53 jurisdictions: 2.12M statutes, 1.95M regulations (including CFR annual editions), 425k session laws, 258k agency decisions, 77k proposed regulations, 77k guidance documents, 53k court rules, 13k constitutional provisions. English and Chinese summaries, norm types, regulated parties, subjects, defined terms, penalties, deadlines and cross-references are extracted per provision (citations and figures checked against the text).

- **id**: `law_id`, e.g. `uslaw:CFRANN_2024_T42_P2_S2_33`
- **search**: modes hybrid, dense, bm25; cost 2 (`--head`: 3)
- **read levels** (`-l`): `brief` 1, `detail` 2, `full` 5; default `detail`
- **facets**: `jurisdiction`, `doc_group`, `kind`, `status`, `norm_types`, `penalty_types`
- **free samples** (cost 0): queries ['HIPAA patient records disclosure'], ids ['uslaw:CFRANN_2024_T42_P2_S2_33']

| Filter (`-F`) | Type | Ops | Meaning |
|---|---|---|---|
| `jurisdiction` | keyword | eq/any | Jurisdiction: federal or a two-letter state code (53 in all) |
| `is_federal` | bool | eq | Federal |
| `doc_group` | keyword | eq/any | Document group |
| `kind` | keyword | eq/any | Specific kind (see facets) |
| `status` | keyword | eq/any | Status |
| `norm_types` | keyword | eq/any | Norm type (closed set of 15, model-assigned) |
| `has_penalty` | bool | eq | Carries a penalty |
| `penalty_types` | keyword | eq/any | Penalty type |
| `citation` | keyword | eq/any | Citation (exact, e.g. 42 C.F.R. § 2.33) |
| `subjects` | keyword | eq/any | Subjects (open model-generated labels, very high cardinality) |
| `defined_terms` | keyword | eq/any | Terms defined in this provision |
| `regulated_parties` | keyword | eq/any | Regulated parties |

Notes:
- Licence: CC BY 4.0 (open_us_law) — attribution required when displaying or redistributing.
- One document = one section / provision, not a whole act. The `excerpt` in level=detail is a snippet, not the full text.
- 928k provisions are status=superseded (mostly historical CFR annual editions) — filter status=in_force before citing.
- Summaries, norm types and subjects are model-generated; citations and figures were checked against the text, but cite the source for anything formal.
- `subjects` is an open label set (39k values): good to read, poor to filter on.
- The index holds no full text: level=full is not available yet (the provision text lives on NAS (open_us_law); the index carries the summary plus an excerpt).

## trials

All 603,730 studies on ClinicalTrials.gov (one per NCT). Phase / status / enrolment / countries / MeSH come from the ctgov record; eligibility highlights, biomarkers, prior therapy, ECOG and one-line summaries are model-extracted.

- **id**: `nct_id`, e.g. `NCT02082496`
- **search**: modes hybrid, dense, bm25; cost 2 (`--head`: 3)
- **read levels** (`-l`): `brief` 1, `detail` 2, `full` 5; default `detail`
- **facets**: `phase`, `overall_status`, `study_type`, `intervention_type`, `sponsor_class`, `sex`, `countries`, `condition_mesh`
- **free samples** (cost 0): queries ['glp-1 obesity phase 3'], ids ['NCT02082496']

| Filter (`-F`) | Type | Ops | Meaning |
|---|---|---|---|
| `phase` | keyword | eq/any | Trial phase |
| `overall_status` | keyword | eq/any | Recruitment status |
| `study_type` | keyword | eq/any | Study type |
| `intervention_type` | keyword | eq/any | Intervention type |
| `condition_mesh` | keyword | eq/any | Condition MeSH term (controlled, more reliable than free-text conditions) |
| `countries` | keyword | eq/any | Trial countries |
| `start_year` | integer | eq/range | Start year, range |
| `has_results` | bool | eq | Results posted |
| `sponsor_class` | keyword | eq/any | Sponsor class |
| `sex` | keyword | eq | Sex eligibility |
| `sponsor` | keyword | eq/any | Sponsor name (exact) |
| `intervention_mesh` | keyword | eq/any | Intervention MeSH term |
| `biomarker_names` | keyword | eq/any | Biomarkers named in eligibility (model-extracted) |
| `performance_status` | keyword | eq/any | Performance-status requirement, e.g. ECOG 0-1 (model-extracted) |
| `treatment_naive` | bool | eq | Requires treatment-naive patients (model-extracted) |
| `enrollment` | integer | eq/range | Enrolment, range |
| `age_min_years` | integer | eq/range | Minimum age, range |
| `age_max_years` | integer | eq/range | Maximum age, range |
| `completion_year` | integer | eq/range | Completion year, range |

Notes:
- Filter by condition_mesh (controlled terms); `conditions` is free text as entered by the registrant.
- Eligibility highlights, biomarkers, prior therapy and ECOG are model-extracted from the eligibility text — verify against the record before acting.
- 97k studies carry overall_status=UNKNOWN: the registrant stopped updating, which does not mean the trial ended.
- The index holds no full text: level=full is not available yet (the full registry record lives on NAS (ctgov/bulk) and is not in the index).

## drugs

256,282 US drug labels (openFDA SPL, latest version per set_id). Indications, contraindications, interacting drugs, boxed-warning gist and one-line summaries are model-extracted; route / product type / pharmacologic class come from the openfda mapping block.

- **id**: `set_id`, e.g. `f5e548d0-cc79-4c34-a3f5-e20a5b8b6564`
- **search**: modes hybrid, dense, bm25; cost 2 (`--head`: 3)
- **read levels** (`-l`): `brief` 1, `detail` 2, `full` 5; default `detail`
- **facets**: `route`, `product_type`, `pharm_class_epc`
- **free samples** (cost 0): queries ['semaglutide weight loss'], ids ['f5e548d0-cc79-4c34-a3f5-e20a5b8b6564']

| Filter (`-F`) | Type | Ops | Meaning |
|---|---|---|---|
| `route` | keyword | eq/any | Route of administration |
| `product_type` | keyword | eq/any | Product type; UNMAPPED = the SPL has no openfda mapping block |
| `is_rx` | bool | eq | Prescription-only |
| `has_boxed_warning` | bool | eq | Has a boxed warning |
| `pharm_class_epc` | keyword | eq/any | Pharmacologic class (EPC) |
| `effective_year` | integer | eq/range | Label version year, range |
| `generic_name` | keyword | eq/any | Generic name (exact) |
| `substance_names` | keyword | eq/any | Active substances |
| `pharm_class_moa` | keyword | eq/any | Pharmacologic class (mechanism of action) |
| `manufacturer` | keyword | eq/any | Labeler / manufacturer (exact) |
| `rxcui` | keyword | eq/any | RxNorm concept id |
| `unii` | keyword | eq/any | Substance UNII |
| `product_ndc` | keyword | eq/any | NDC product code |
| `application_number` | keyword | eq/any | FDA application number (NDA / ANDA / BLA) |

Notes:
- 67% (171,903) are product_type=UNMAPPED: those SPLs have no openfda mapping block, so generic name / route / pharmacologic class may be empty — use spl_name for the product name.
- Only the latest version per set_id is kept; no label history.
- Indications and contraindications are extracted highlights; go back to the label for prescribing decisions.
- Not medical advice.
- The index holds no full text: level=full is not available yet (the label sections live on NAS (openfda/label); the index carries only section names and token counts).

## grants

1,221,279 research awards: 651,041 NSF awards (one per award id) plus 570,238 NIH RePORTER projects (multi-year funding merged per core project number, with per-year amounts). Organisation / country / PI / directorate / activity code / dates / amounts come from the source; topics, methods, domain and one-line summaries are model-generated (title-only where no abstract exists — see _enrich.basis).

- **id**: `grant_id`, e.g. `nih:R25HG007515`
- **search**: modes hybrid, dense, bm25; cost 2 (`--head`: 3)
- **read levels** (`-l`): `brief` 1, `detail` 2, `full` 5; default `detail`
- **facets**: `agency`, `research_domain`, `ic_or_directorate`, `activity_code`, `org_country`, `org_state`
- **free samples** (cost 0): queries ['single cell transcriptomics'], ids ['nih:R25HG007515']

| Filter (`-F`) | Type | Ops | Meaning |
|---|---|---|---|
| `agency` | keyword | eq/any | Funding agency |
| `research_domain` | keyword | eq/any | Research domain (model-assigned, closed set of 13) |
| `ic_or_directorate` | keyword | eq/any | NIH institute or NSF directorate (see facets) |
| `activity_code` | keyword | eq/any | Funding mechanism: NIH activity code (R01 / R21 / F32 …) or NSF award type |
| `fy` | integer | eq/range | Fiscal year, range |
| `start_year` | integer | eq/range | Project start year, range |
| `end_year` | integer | eq/range | Project end year, range |
| `amount_total` | number | eq/range | Total amount (USD), range |
| `org_country` | keyword | eq/any | Organisation country (source casing is inconsistent — see notes) |
| `org_state` | keyword | eq/any | US state |
| `org_name` | keyword | eq/any | Organisation name (exact) |
| `pi_names` | keyword | eq/any | PI name as written in the source (NIH uses LAST, FIRST) |
| `topics` | keyword | eq/any | Research topics (open model-generated labels, very high cardinality) |
| `programs` | keyword | eq/any | Programme names |
| `core_project_num` | keyword | eq/any | NIH core project number |
| `is_renewal` | bool | eq | Renewal |

Notes:
- One NIH document = all yearly awards under a core project number (amount_total is the sum, funding_by_year the breakdown); one NSF document = one award.
- org_country casing is inconsistent in the source (both UNITED STATES and United States, 1.088M awards) — pass both spellings.
- `topics` are open labels with tens of thousands of values: good to read, poor to filter on — use research_domain.
- Where no abstract exists the summary comes from the title alone (_enrich.basis=title_only).
- The index holds no full text: level=full is not available yet (abstracts are already in level=detail; progress reports and publications are not in this corpus).

## filings

1,199,147 corporate filings and regulatory documents across US and China, in two layers. The vector layer holds 572,443 (semantic plus lexical): 393,660 EDGAR 8-K events, 46,542 structured 10-K/20-F, 119,399 Chinese periodic reports, 10,434 exchange inquiry letters and discipline decisions, 2,408 CSRC penalty decisions. The Postgres layer adds 626,704 reachable by keyword plus filters: 104,671 10-Q quarterlies (no vectors, by design), 153,705 6-K, 187,807 13D/13G ownership filings, 113,176 Chinese interim announcements (backfill in progress), 31,493 DEF 14A, 28,378 Form 425 and 6,589 S-1. One-liners, counterparties, amounts, MD&A drivers, inquiry points and violation types are model-extracted; company name / tickers / SIC come from EDGAR submissions.

- **id**: `doc_id`, e.g. `us:861838:0001104659-23-092550`
- **search**: modes hybrid, dense, bm25; sort relevance, date; cost 2 (`--head`: 3)
- **read levels** (`-l`): `brief` 1, `detail` 2, `full` 5; default `detail`
- **facets**: `market`, `doc_family`, `form`, `event_types`, `report_kind`, `letter_kind`, `exchange`, `issue_categories`, `violation_types`, `sic`
- **free samples** (cost 0): queries ['CEO resignation'], ids ['us:861838:0001104659-23-092550']

| Filter (`-F`) | Type | Ops | Meaning |
|---|---|---|---|
| `market` | keyword | eq | Market |
| `doc_family` | keyword | eq/any | Document family |
| `form` | keyword | eq/any | Form / document type. 10-Q, 6-K, 13D/G, DEF 14A, 425, S-1 and Chinese interim announcements live only in the … |
| `filed_at` | datetime | range | Filing date range (day precision; Postgres layer only, so it routes the query there) |
| `filed_year` | integer | eq/range | Filing year, range |
| `fiscal_year` | integer | eq/range | Fiscal year, range |
| `event_types` | keyword | eq/any | 8-K event type (closed set, see facets) |
| `items` | keyword | eq/any | 8-K item number, e.g. 5.02 |
| `sic` | keyword | eq/any | SIC industry code |
| `report_kind` | keyword | eq/any | Periodic report kind |
| `letter_kind` | keyword | eq/any | Inquiry-letter kind |
| `exchange` | keyword | eq/any | Exchange |
| `issue_categories` | keyword | eq/any | Inquiry focus (closed set of 16, see facets) |
| `violation_types` | keyword | eq/any | Violation type (CSRC penalties, closed set of 11) |
| `company_name` | keyword | eq/any | Company name (exact) |
| `cik` | keyword | eq/any | EDGAR CIK |
| `sec_code` | keyword | eq/any | A-share code |
| `tickers` | keyword | eq/any | US tickers |
| `counterparties` | keyword | eq/any | Counterparties (model-extracted) |
| `risk_categories` | keyword | eq/any | Risk categories (from 10-K) |
| `party_names` | keyword | eq/any | Parties named in penalty / discipline documents |
| `has_reply` | bool | eq | Inquiry letter has a reply |
| `has_ban` | bool | eq | Includes a market ban |

Notes:
- Fields differ by doc_family: event (8-K) has items / event_types / counterparties / amounts; periodic has main_business / segments / key_numbers; 10-Q quarterlies have mdna_drivers / liquidity / legal_updates / new_or_changed_risks / outlook; inquiry_letter has issues / deadline / has_reply; penalty has violation_types / facts / legal_basis / parties. Filter by doc_family before reading fields.
- The 104,671 10-Q quarterlies carry no vectors by design and live only in the Postgres layer: filtering on form=10-Q (or doc_family=periodic with market=us) routes the whole query there — lexical search, sort=date and day-precision filed_at ranges, but no semantic search. Every hit is tagged with its layer and the response says which layer answered.
- Lexical search in the Postgres layer also matches model-written retrieval keywords (kw_en / kw_zh, folded into the full-text index), so a Chinese query such as 持续经营 finds English going-concern language and synonyms absent from the source text. The trade-off: the score includes that contribution and the response does not distinguish a source-text match from a keyword-only match. The keywords themselves are not returned (the store marks them recall-only).
- Financial statements from 10-K / 20-F / 10-Q are not here — use XBRL; this corpus carries structured highlights only.
- Source documents are on NAS (raw_path in level=detail); the index holds no full text.
- The index holds no full text: level=full is not available yet (source documents are on NAS (raw_path); neither layer holds the body text, only structured highlights).

## standards

Catalogue of 79,311 Chinese national standards (openstd: mandatory GB / recommended GB/T / guiding GB/Z). **Metadata only, no full text**: code, Chinese and English title, status, issue and effective dates, ICS class, tags.

- **id**: `std_code`, e.g. `GB/T 42729-2023`
- **search**: modes hybrid, dense, bm25; cost 2 (`--head`: 3)
- **read levels** (`-l`): `brief` 1, `detail` 2, `full` 5; default `detail`
- **facets**: `nature`, `state`, `std_prefix`, `ics`
- **free samples** (cost 0): queries ['锂离子电池 安全'], ids ['GB/T 42729-2023']

| Filter (`-F`) | Type | Ops | Meaning |
|---|---|---|---|
| `nature` | keyword | eq/any | Nature: mandatory / recommended / guiding |
| `state` | keyword | eq/any | Status: in force / coming into force / withdrawn / suspended |
| `std_prefix` | keyword | eq/any | Code prefix |
| `ics` | keyword | eq/any | ICS top-level class (see facets) |
| `is_mandatory` | bool | eq | Mandatory |
| `issue_year` | integer | eq/range | Issue year, range |
| `act_year` | integer | eq/range | Effective year, range |
| `tags` | keyword | eq/any | Topic tags (model-generated) |

Notes:
- Metadata only: the text itself is on openstd (the `fulltext` flag says whether openstd has it online).
- English titles and tags are generated from the Chinese title alone — not authoritative translations.
- 48,406 are in force and 28,535 withdrawn — filter state=现行 before citing.
- The index holds no full text: level=full is not available yet (the standard text is not in this corpus — see openstd.samr.gov.cn).

## cve

384k public vulnerabilities (NVD) plus CISA KEV exploited-in-the-wild flags and FIRST EPSS exploitation probability. Vulnerability class (closed set of 17), attacker prerequisites, affected scope, impact and one-line summaries are model-extracted. No vectors: structured filters plus bilingual full-text search in Postgres.

- **id**: `doc_id`, e.g. `CVE-2024-3400`
- **search**: modes keyword; sort relevance, date, epss, kev_added, published; cost 2 (`--head`: 3)
- **read levels** (`-l`): `brief` 1, `detail` 2; default `detail`
- **facets**: `severity`, `vuln_class`
- **free samples** (cost 0): queries ['log4j'], ids ['CVE-2024-3400']

| Filter (`-F`) | Type | Ops | Meaning |
|---|---|---|---|
| `affected` | text | text | Affected product (fuzzy match, e.g. globalprotect) |
| `cvss_score` | number | range | CVSS score, range |
| `epss` | number | range | EPSS 30-day exploitation probability (0–1), range |
| `kev` | bool | eq | Listed in CISA KEV (known exploited in the wild) |
| `published` | datetime | range | Publication date range |
| `severity` | keyword | eq/any | CVSS severity (derived from the score) |
| `vuln_class` | keyword | eq/any | Vulnerability class (closed set of 17, model-assigned) |
| `cwe` | keyword | eq/any | CWE id |
| `kev_added` | datetime | range | Date added to KEV, range |

Notes:
- NVD data is used under its terms: any display must carry the not-endorsed notice (see the attribution field).
- kev=true means CISA confirmed exploitation in the wild; epss is FIRST's probability estimate — different things.
- severity is derived from cvss_score; the 3,347 CVEs without a score have neither.
- Rank by exploitation risk with sort=epss, by time with sort=date.
- vuln_class / attacker_needs / impact / one_liner* are model-written — fine as a summary, not as a quote; the original text is description, in level=detail.
- Model-written fields (summarise, do not quote): affected, attacker_needs, impact, one_liner, one_liner_zh, vuln_class.
- The field table and enumerations are generated from the store's own self-description (search.field), not hand-written; enumeration counts are as of 2026-10-10.

## fr

1.0M Federal Register documents (1994– ): rules, proposed rules, notices and presidential documents. Action kind (closed set of 19), issuing agencies, affected parties, effective and comment-close dates and one-line summaries are model-extracted. No vectors: structured filters plus bilingual full-text search in Postgres.

- **id**: `doc_id`, e.g. `fr:2024-07332`
- **search**: modes keyword; sort relevance, date, pub_date; cost 2 (`--head`: 3)
- **read levels** (`-l`): `brief` 1, `detail` 2; default `detail`
- **facets**: `action_kind`, `doc_type`
- **free samples** (cost 0): queries ['PFAS drinking water'], ids ['fr:2024-07332']

| Filter (`-F`) | Type | Ops | Meaning |
|---|---|---|---|
| `action_kind` | keyword | eq/any | Action kind (closed set of 19, model-assigned) |
| `agencies` | keyword | eq/any | Issuing agencies (several allowed, any match) |
| `doc_type` | keyword | eq/any | Document type (official capitalisation: Rule / Proposed Rule / Notice / Presidential Document …) |
| `pub_date` | datetime | range | Publication date range |
| `cfr_refs` | keyword | eq/any | CFR references touched, e.g. 40 CFR 141 |
| `comments_close_on` | datetime | range | Comment close date range |
| `docket_ids` | keyword | eq/any | Docket ids |
| `document_number` | keyword | eq/any | Document number (exact, e.g. 2024-07332) |
| `effective_on` | datetime | range | Effective date range |
| `fr_topics` | keyword | eq/any | Official Federal Register topics |
| `rins` | keyword | eq/any | RINs |
| `significant` | bool | eq | Whether it is a significant regulatory action |

Notes:
- Division of labour with us_law: us_law holds the provisions in force (clause-level CFR / USC); fr holds the notices themselves (who changed what, when).
- doc_type uses the official capitalisation (Rule / Proposed Rule / Notice / Presidential Document / Uncategorized Document / Correction / Sunshine Act Document); lowercase 'rule' matches nothing.
- Rules open for comment: filters.comments_close_on={"gte": "<today>"}; upcoming effect: a range on effective_on.
- subjects is an open model-generated label set and is not filterable before normalisation — filter on fr_topics (the official topics) instead.
- No vectors: the query runs as an English tsvector and a Chinese zhparser pass whose results are unioned; mixed queries are split automatically, and quoted phrases / OR / -exclusion work.
- Model-written fields (summarise, do not quote): action_kind, affected, key_point, one_liner, one_liner_zh, subjects.
- The field table and enumerations are generated from the store's own self-description (search.field), not hand-written; enumeration counts are as of 2026-10-10.
