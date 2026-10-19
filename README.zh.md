<h1 align="center">DeepXiv</h1>
<p align="center"><em>补上 agentic search 缺失的那层数据 —— 论文全文、真实引用，以及论文背后的人。</em></p>

<p align="center">
  <a href="https://deepxiv.com">正式系统</a> ·
  <a href="USAGE.zh.md">完整文档</a> ·
  <a href="https://data.rag.ac.cn/api/docs">API 文档</a> ·
  <a href="https://data.rag.ac.cn/status">实时状态</a> ·
  <a href="https://arxiv.org/abs/2603.00084"><img src="https://img.shields.io/badge/arXiv-2603.00084-b31b1b" alt="arXiv"></a> ·
  <a href="README.md">English</a>
</p>

<p align="center">
  <img src="./assets/deepxiv_cover.jpg" width="100%" alt="DeepXiv —— 致力于做最好的垂域 Agent 数据服务">
</p>

> [!IMPORTANT]
> **容量提示：总并发约 50 rps，所有用户共享。** DeepXiv 的论文服务和 1stAuthor 的服务目前都部署在小服务器上，受资源和带宽限制。欢迎 donate 支持服务运行 🙏；如果有大量调用需求，请私聊我们（`tommy[at]chien.io`）协商方案。

---

## 这是什么

一个 CLI 加 Python SDK，背后的服务已经把文献读过一遍：论文以解析好的章节形式返回而不是 PDF，检索跑在全文而不是摘要上，agentic 接口回答问题时给出的引用能直接落到真实的 arXiv ID 和 URL。

它做四件事：

| | 命令 | |
|---|---|---|
| **问文献** | `deepxiv ask` | 一个问题进去，一个带真实 arXiv ID 引用的答案出来 |
| **问网页** | `deepxiv ask --web` | 同上，数据来自 Google 加缓存页面正文 |
| **分层读论文** | `deepxiv search` / `paper` | 先搜、再判断、最后只读需要的那一节 |
| **找人** | `deepxiv fa … talent` | 谁在做这个方向、人在哪、履历如何 |
| **看美股** 🆕 | `deepxiv fa … stocks` | 8000+ 支美股：行情、个股新闻、公告、财务、宏观，支持时点还原；`fa ask -d stocks` 直接出带引用的分析 |
| **论文之外** | `deepxiv fa` | 法规、判决、临床试验、药品、基金、公告、标准、CVE —— 经 1stAuthor |

## 解决什么问题

一个 agent 要调研某个课题，现有的选择都不好。搜索 API 给回十条蓝链接和摘要 —— 够说出论文名字，永远不够回答"它在 HumanEval 上报了多少加速比"。PDF 能回答，但一篇 5 万 token，而且是一整块没有结构可导航的文本。

DeepXiv 把这个取舍消掉。论文是预先解析好的，agent 可以先花 300 token 看 TLDR，再决定要不要花 5k token 读 Methods。需要证据支撑的问题交给 agentic 接口，它会真的去读原文，返回可核查的引用。而"谁在做"是调研的另一半，所以同一个 token 也能检索学者 —— 还能经 [1stAuthor](https://1stauthor.com) 的垂域查法规、临床试验、药品、基金等。

## DeepXiv × 1stAuthor

DeepXiv 与 [1stAuthor](https://1stauthor.com) 深度合作，提供论文之外的多领域数据服务：学者、美股、法规、裁判文书、临床试验、药品、基金、公告、标准、CVE 等，都可以用同一个 token 通过 `deepxiv fa` 访问。**→ [`deepxiv fa` 使用文档](FA.zh.md)**

一个 CLI，十五个垂域，同一套动词：`search` → `read` → `ask`。

| 域 | 内容 |
|---|---|
| **`stocks`** 🆕 | **8000+ 支美股：行情、个股新闻与事件、SEC 公告、财务、宏观序列与宏观新闻，全部支持时点还原** |
| `talent` | AI 学者档案：教育、履历、代表作、指标 |
| `appraise` | 院士和 Fellow 引用一篇论文时的评价 |
| `law` · `us_law` · `uk_eu_law` · `fr` | 中国及其它 25 个法域的法律法规；美国法典与联邦法规；英国与欧盟立法；Federal Register |
| `cases` | 中美法院判决 |
| `trials` · `drugs` · `grants` | ClinicalTrials.gov 临床试验、openFDA 药品说明书、NSF / NIH 基金 |
| `filings` · `standards` | SEC 与国内上市公司公告、国家标准 |
| `cve` · `osv` | NVD + CISA KEV + EPSS 漏洞；开源包安全公告与恶意包报告 |

> **建议指定 `--domain`（`-d`）。** 自动选域（`fa ask` 不加 `-d`）还在早期开发阶段，可能选错域。请自己指定域：`deepxiv fa domains` 列出全部，`deepxiv fa spec DOMAIN` 查看可用过滤条件。

```bash
# 找人：base 北京、上海的世界模型方向在校学生
deepxiv fa search talent "world model" -F career_stage=student -F location=北京,上海 -k 20

# DeepSeek-R1 被哪些院士 / Fellow 引用，正面评价都说了什么
deepxiv fa read appraise arxiv:2501.12948 -l brief
deepxiv fa read appraise arxiv:2501.12948 -p stance=positive -p org=CAS,CAE

# 法规与判例：国内法规 + 美国最高法院判决
deepxiv fa search law "个人信息保护" -k 5
deepxiv fa search cases "qualified immunity police" -F country=us -F court_level=scotus -k 5

# 临床试验、公司公告、漏洞
deepxiv fa search trials "GLP-1 obesity" -F phase=PHASE3 -F overall_status=RECRUITING -k 5
deepxiv fa search filings "CEO resignation" -F market=us -F "filed_year>=2023" -k 5
deepxiv fa search cve "*" -F kev=true -F severity=critical,high --sort epss -k 10

# 在一个域上要带引用的答案（扣 agentic 配额；SDK token 可试用 3 次）
deepxiv fa ask "个人信息出境需要满足什么条件" -d law
deepxiv fa ask "DeepSeek-R1 得到了哪些院士的正面评价" -d appraise -p paper=arxiv:2501.12948
```

### 🆕 美股

`deepxiv fa … stocks` 给 agent 提供带时点还原的美股数据：**8000+ 支股票**的日线行情，**每支股票的新闻**（2026 年 4 月以来 390 万条，去重后聚成约 92 万个事件，并标注正负面），SEC 公告、XBRL 财务，以及**宏观序列与宏观新闻**（CPI、工业产出、美债收益率、汇率、大宗商品，并给出与预期 / nowcast 的对比）。所有查询都支持 `as_of`，只返回那个时点已经可见的数据，回测和"X 日当天我们知道什么"这类问题不会穿越。

```bash
deepxiv fa read stocks NVDA                                      # 最新价（对比行业 ETF 和 SPY）、近期事件、新闻、公告
deepxiv fa read stocks NVDA -e news                              # 个股新闻流
deepxiv fa read stocks NVDA -e financials                        # XBRL 财务（按原始申报口径）
deepxiv fa read stocks NVDA -p as_of=2026-09-04                  # 回到过去某天的视图（这里能看到收购 Hugging Face 的 8-K）
deepxiv fa search stocks "AI data center power" -F source=stocks # 一个主题涉及哪些股票
deepxiv fa search stocks "chip export restrictions" -k 5         # 新闻 + 事件 + 公告混排
deepxiv fa search stocks "earnings guidance" -F ticker=TSLA -F source=events
deepxiv fa read stocks digest:macro                              # 当日宏观数据发布、利率、汇率、大宗商品
deepxiv fa read stocks macro:CPIAUCSL                            # 宏观序列，含历史版本和 nowcast

# 或者直接问：agent 自己拉行情、新闻、事件、公告、财报和宏观，每个数字都带引用
deepxiv fa ask "CoreWeave 最近一周为什么大跌？结合价格、新闻和财报说明" -d stocks
```

**`fa ask -d stocks` 已上线**：按主题找公司，问个股的涨跌与新闻面、事件、内部人交易、财务、宏观，答案引用上游记录 id（`[stocks:px:CRWV:2026-10-16]`、`[stocks:news:…]`、`[stocks:fin:…]`）。问过去某个时点会自动按那个时点回答，答案末尾附数据来源和「不构成投资建议」。`deepxiv fa spec stocks` 列出数据源、过滤条件和 extra。

DeepXiv 本身专注于学术论文的 agentic 数据服务，**将持续免费**。如需更大额度的 1stAuthor 相关服务，可以到 [1stauthor.com](https://1stauthor.com) 看看。

> 1stAuthor 目前处于纯内测阶段，任何问题欢迎[提 issue](https://github.com/DeepXiv/deepxiv_sdk/issues)。

## 安装

```bash
pip install deepxiv-sdk
```

`deepxiv fa`（1stAuthor 垂域，含 talent）需要 1.2.0 及以上：`pip install -U deepxiv-sdk`。

`deepxiv` 首次使用会自动注册一个 token。agentic 命令（`ask`、`fa ask`）需要注册过的 key；自动注册的 token 可以试用 3 次 `fa ask`（终身）。在 [data.rag.ac.cn/register](https://data.rag.ac.cn/register) 领一个 key，然后：

```bash
deepxiv config --token YOUR_REGISTERED_KEY
```

内测期间，注册 key 通过 `deepxiv fa …` 使用 1stAuthor，和 1stAuthor 自己的用户同等待遇：

- **`deepxiv fa ask`** 消耗**每日 AI 问答额度**，UTC 0 点重置；用完会提示「今日 AI 问答额度已用完」。全站也有每日总量，高峰时可能提前用完。
- **`deepxiv fa search` / `read`** 合理使用，按速率限制：每分钟 60 次、同时 5 个、每天 5,000 次。
- **`talent`** 另有每日读取上限（只限档案内容，检索和卡片不限）。
- **自动注册的 token** 保持现状：`fa ask` 可试用 3 次（终身），之后提示去 [data.rag.ac.cn/register](https://data.rag.ac.cn/register) 注册。
- **收到 429** 时按 `Retry-After` 给出的秒数退避。

`deepxiv ask`（论文问答）是 DeepXiv 自己的服务，规则不变：注册 key 每天 300 次，与通用 daily limit 相互独立。

## 用法

一次完整的调研。你听说今年 speculative decoding 快了不少，想知道实际情况。

**1. 先问文献。** 直接问问题，不要给关键词。服务端自主调工具、读论文正文、并标注它用了什么。

```bash
deepxiv ask "what speedup does speculative decoding report on HumanEval in 2025"
```

```
DEER reports a 5.54× speedup on HumanEval (with Qwen3-30B-A3B as the target
model), compared to EAGLE-3's 2.41× on the same benchmark [arXiv:2512.15176].

📚 Sources (1 cited, 10 retrieved — use --all-sources for the rest):
  1. [2512.15176] DEER: Draft with Diffusion, Verify with Autoregressive Models
```

<p align="center">
  <img src="./assets/demo.gif" width="100%">
  <br>
  <em><code>deepxiv ask</code> —— 一个问题进去，一个带引用的答案流式出来</em>
</p>

答案走 stdout，来源走 stderr，所以 `deepxiv ask "…" > answer.md` 只会捕获答案本身。问题横跨多篇论文时加 `--effort high`。

**2. 分层读它引用的那篇论文。** 不要为了回答一个关于某节的问题而加载整篇。

```bash
deepxiv paper 2512.15176 --brief              # 标题、TLDR、关键词、引用数 —— 值不值得读？
deepxiv paper 2512.15176 --head               # 章节列表 + token 分布
deepxiv paper 2512.15176 --section Experiment # 只读这一节
```

每一步的开销都比上一步高一个数量级，所以拿到答案就可以停。章节名从 `--head` 里取 —— 论文之间没有统一的目录结构。`--preview` 给约 1 万字符；什么 flag 都不加则给全文 markdown。

**3. 展开成一次检索。** 知道要找什么之后，再用过滤条件捞其余的。

```bash
deepxiv search "speculative decoding" --date-from 2025-01 --min-citations 20 --limit 10
```

过滤条件之间是 `AND` —— `--authors`、`--orgs`、`--categories`、`--venue`/`--venue-year`、日期、引用下限。叠太多会合理地返回 0 条，松开一个即可。

**4. 找到背后的人。** 知道方法出自谁的组、他们还做过什么，这个方法的价值才完整。

```bash
deepxiv fa search talent "投机解码" --top-k 5                # 按方向
deepxiv fa search talent "Geoffrey Hinton"                    # 或按人名
deepxiv fa search talent "deep learning" -F "org=University of Toronto" -F "h_index>=50"
deepxiv fa read talent 15023                                  # 画像：简介、教育、履历、代表作、指标
deepxiv fa read talent 15023 --level full                     # 完整调查档案（markdown）
```

中文名、拼音、英文名和研究方向都能直接搜。`search` 给出的 ID 喂给 `read`；`deepxiv fa spec talent` 列出可用过滤条件和各读取级别的价格。`deepxiv talent search|survey` 作为已弃用的别名仍可用，但旧库的 ID 在新库里不通用。

同一套动词也适用于 1stAuthor 的其它垂域（`deepxiv fa domains` 列出全部）。**完整文档：[FA.zh.md](FA.zh.md)。**

```bash
deepxiv fa search law "个人信息保护" --top-k 5
deepxiv fa ask "个人信息出境需要满足什么条件" --domain law   # 扣 agentic 配额；SDK token 可试用 3 次
```

**5. 问题不在学术圈里时，换个后端。** 授权、定价、上周谁发了什么 —— 同一个命令。

```bash
deepxiv ask "which inference providers support speculative decoding today" --web
deepxiv ask "NeurIPS 2025 最佳论文" --web --search-type news
```

web 后端读的是**缓存过的**页面正文。完整读到的页面标 📄，只拿到搜索摘要的标 🔗 —— 据此判断证据强度。

**在 Python 里**，同一条链路就是 `Reader`：

```python
from deepxiv_sdk import Reader

reader = Reader(token="YOUR_REGISTERED_KEY")   # Reader 需要显式传 token
answer = reader.agent_search("what speedup does DEER report on HumanEval")["answer"]
method = reader.section("2512.15176", "Method")
people = reader.fa().search("talent", "speculative decoding", top_k=5)
```

## 文档

- **[USAGE.zh.md](USAGE.zh.md)** —— 完整的 CLI 参考、Python API、流式、错误处理、批量、内置 research agent。（[English](USAGE.md)）
- **[FA.zh.md](FA.zh.md)**：`deepxiv fa`，即 1stAuthor 垂域（talent、law、cases、trials、drugs、grants、filings、standards、CVE 等）的命令、过滤、价格、错误处理和 Python 用法。（[English](FA.md)）
- **[skills/deepxiv-cli/SKILL.md](skills/deepxiv-cli/SKILL.md)** —— 给编码 agent 的即插即用操作说明。另有两个成型的工作流 skill：[热点摘要](skills/deepxiv-trending-digest/SKILL.md)、[baseline 表格](skills/deepxiv-baseline-table/SKILL.md)。
- **`skills/deepxiv-fa-*`** —— 每个 1stAuthor 垂域一个 skill（如 [stocks](skills/deepxiv-fa-stocks/SKILL.md)、[talent](skills/deepxiv-fa-talent/SKILL.md)、[law](skills/deepxiv-fa-law/SKILL.md)）：过滤条件、读取级别、extra 和实测过的命令，全部写成 `deepxiv fa` 命令，由 `scripts/gen_fa_skills.py` 从线上 spec 生成。索引：[fa-domains.md](skills/deepxiv-cli/references/fa-domains.md)。
- **[examples/](examples/)** —— 每个入口的可运行脚本。

还支持 PubMed Central、bioRxiv/medRxiv、热点论文以及单篇论文的社交指标 —— 见 [USAGE.zh.md](USAGE.zh.md#其他数据源)。

## 引用

如果 DeepXiv 对你的工作有帮助，请引用技术报告：

```bibtex
@article{qian2026deepxiv,
  title   = {DeepXiv-SDK: An Agentic Data Interface for Scientific Literature},
  author  = {Qian, Hongjin and Xia, Ziyi and Liu, Ze and Chen, Jianlyu and
             Luo, Kun and Qin, Minghao and Li, Chaofan and Xiong, Lei and
             Lan, Junwei and Wang, Sen and Liang, Zhengyang and Shao, Yingxia and
             Lian, Defu and Liu, Zheng},
  journal = {arXiv preprint arXiv:2603.00084},
  year    = {2026},
  url     = {https://arxiv.org/abs/2603.00084}
}
```

## 许可与支持

MIT —— 见 [LICENSE](LICENSE)。

- 🐛 **问题反馈**: [github.com/DeepXiv/deepxiv_sdk/issues](https://github.com/DeepXiv/deepxiv_sdk/issues)
- 📧 **更高额度、批量需求或 donate**: 邮件 `tommy[at]chien.io` 说明用途
