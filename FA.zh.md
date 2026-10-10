# deepxiv fa —— 1stAuthor 垂域

> **English**: [FA.md](FA.md) · 返回 [README](README.zh.md)

DeepXiv 与 [1stAuthor](https://1stauthor.com) 深度合作，提供 arXiv 之外的多领域数据服务。`deepxiv fa` **用你的 deepxiv token** 访问 1stAuthor 的垂域：学者、法规、裁判文书、临床试验、药品说明书、科研基金、公司公告、标准、漏洞、美国联邦公报。请求经 `data.rag.ac.cn/fa` 转发，不需要另外申请 1stAuthor 的 key。

DeepXiv 本身专注于学术论文的 agentic 数据服务，**将持续免费**。如需更大额度的 1stAuthor 相关服务，可以到 [1stauthor.com](https://1stauthor.com) 看看。

> **Beta。** `deepxiv fa` 在 `1.2.0b1` 里，暂时仅源码安装；1stAuthor 目前处于纯内测阶段。任何问题欢迎[提 issue](https://github.com/DeepXiv/deepxiv_sdk/issues)。

本文是 `deepxiv fa` 的完整参考：每个命令、选项、参数和错误，以及 Python 和 HTTP 接口。

**目录**
1. [安装与 token](#1-安装与-token)
2. [有哪些域](#2-有哪些域)
3. [快速上手](#3-快速上手)
4. [命令](#4-命令)：[domains](#fa-domains) · [spec](#fa-spec) · [search](#fa-search) · [read](#fa-read) · [facets](#fa-facets) · [resolve](#fa-resolve) · [ask](#fa-ask) · [whoami](#fa-whoami)
5. [过滤](#5-过滤)
6. [读取：级别、extra、视图、章节、格式](#6-读取级别extra视图章节格式)
7. [输出与退出码](#7-输出与退出码)
8. [计费与配额](#8-计费与配额)
9. [错误与重试](#9-错误与重试)
10. [Python 接口](#10-python-接口)
11. [HTTP 接口](#11-http-接口)
12. [从 `deepxiv talent` 迁移](#12-从-deepxiv-talent-迁移)
13. [常见问题](#13-常见问题)

---

## 1. 安装与 token

```bash
pip install git+https://github.com/DeepXiv/deepxiv_sdk.git    # 1.2.0b1
deepxiv fa --help
```

`deepxiv fa` 和其它 deepxiv 命令用同一个 token，按以下顺序查找：

1. 命令上的 `--token` / `-t`
2. 环境变量 `DEEPXIV_TOKEN`
3. `~/.env` 里的 `DEEPXIV_TOKEN=`，然后是 `./.env` 里的
4. 以上都没有时，deepxiv 自动注册一个 token 并存入 `~/.env`

token 有两种：

| | 能用什么 | 怎么获得 |
|---|---|---|
| **自动注册的 SDK token** | 除 `fa ask` 外全部 | 首次使用时自动创建 |
| **注册账号的 key** | 全部，包括 `fa ask` | 到 [data.rag.ac.cn/register](https://data.rag.ac.cn/register) 注册，再执行 `deepxiv config --token YOUR_KEY` |

用 `deepxiv fa whoami` 可以看当前用的是哪一种。

## 2. 有哪些域

| 域 | 内容 | ID 字段 | `fa ask` |
|---|---|---|---|
| `talent` | 约 19 万 AI 研究者，约 16 万份调查档案（教育、履历、代表作、开源），Google Scholar 指标实时渲染 | `person_id` | ✅ |
| `law` | 26 个法域约 3.3 万部法规 / 150 万条，按条检索，附中译和逐条抽取 | `law_id` | ✅ |
| `us_law` | 美国 53 个法域约 500 万条条款级文本：成文法、联邦法规（CFR）、会期法、机构裁决、指引、法院规则 | `law_id` | ✅ |
| `cases` | 裁判文书：中国约 1,750 万篇 + 美国判例约 344 万篇，附抽取的结构化字段 | `uuid` | ✅（用 law 的 agent） |
| `trials` | ClinicalTrials.gov 全量临床研究（约 60 万项），抽取了入排标准、生物标志物、既往治疗和摘要 | `nct_id` | ✅ |
| `drugs` | 约 25.6 万份美国药品说明书（openFDA SPL）：适应症、禁忌、相互作用、黑框警告 | `set_id` | ✅ |
| `grants` | 约 120 万项 NSF 资助与 NIH 项目 | `grant_id` | ✅ |
| `filings` | 约 120 万份美股 + A 股公告与监管文书（8-K、10-K/20-F、定期报告、处罚） | `doc_id` | ✅ |
| `standards` | 约 7.9 万条中国国家标准（GB / GB/T / GB/Z），只有目录元数据，没有正文 | `std_code` | ✅ |
| `cve` | 约 38.4 万条公开漏洞（NVD），含 CISA KEV 与 EPSS | `doc_id` | ✅ |
| `fr` | 1994 年以来约 100 万篇美国联邦公报 | `doc_id` | ✅ |
| `appraise` | 一篇论文被哪些院士 / 会士引用过、他们原话怎么说 | `target_key` | ✅ |

所有域都支持 `fa ask`。law、talent、appraise 有各自专门的 agent；其余域共用一个通用 agent，它把问题翻成该域的过滤条件加关键词，所以只有数据库的域（cve、fr）也能问答。`cases` 用 law 的 agent。`standards` 只有目录元数据，它的 ask 会先说明答不了条文正文。

以上为实时列表的快照：`deepxiv fa domains` 显示当前的域和规模，`deepxiv fa spec <域>` 描述某个域。论文和网页不在这里，它们走 deepxiv 原生命令（`deepxiv search`、`paper`、`ask`）。

## 3. 快速上手

```bash
deepxiv fa domains                                    # 有哪些域（免费）
deepxiv fa spec talent                                # 过滤字段、读取级别、价格（免费）

deepxiv fa search talent "Geoffrey Hinton"            # 查人
deepxiv fa read talent 15023                          # 读档案
deepxiv fa search law "个人信息保护" --top-k 5
deepxiv fa ask "自监督学习领域最有影响力的研究者有哪些" --domain talent
```

流程和读论文一样：**先 search，只读需要的部分，想要综合答案时再 ask。**

## 4. 命令

所有 `fa` 命令都接受以下选项：

| 选项 | |
|---|---|
| `-t`, `--token TEXT` | 使用的 token，优先于 `DEEPXIV_TOKEN` |
| `--json` | 输出完整 JSON 响应，而不是文本渲染 |
| `--help` | 显示该命令的帮助 |

### `fa domains`

```
deepxiv fa domains [--json]
```

列出所有域：id、状态、是否支持 `ask`、语料规模和名称。**免费。**

### `fa spec`

```
deepxiv fa spec DOMAIN [--json]
```

域的自描述。**免费。** 文本输出包括：

- 名称、描述、ID 字段及示例 ID
- **SEARCH**：检索模式、价格，以及每个过滤字段的类型、运算符和说明
- **READ**：各个级别和 extra，以及各自的价格
- **ASK**：effort 档位和该域的额外 ask 参数（`-p`）；不支持时会注明
- **FACETS**：`fa facets` 可用的字段
- 免费样例查询和 ID，以及 quickstart 调用示例

`--json` 还会给出文本里省略的内容：视图、章节和格式选项、`brief_fields` / `head_fields`、notes，以及按 ID 类型区分的级别（例如 `law` 的法条 ID 与法规 ID 不同）。

### `fa search`

```
deepxiv fa search DOMAIN QUERY [-F EXPR]... [-k N] [--offset N] [--mode MODE] [--head] [--json]
```

| 选项 | 默认 | |
|---|---|---|
| `-F`, `--filter EXPR` | — | 可重复，之间为 AND，见[过滤](#5-过滤) |
| `-k`, `--top-k N` | 10 | 命中数，1~100 |
| `--offset N` | 0 | 跳过前 N 条（翻页） |
| `--mode MODE` | 域的默认值 | 检索模式，取自 `spec` → `search.modes`（talent：`hybrid`、`dense`、`bm25`、`name`） |
| `--head` | 关 | 更丰富的命中（`fields=head`），更贵 |

文本输出每条命中一块：

```
#1 [15023] Geoffrey Hinton · Emeritus Prof. Computer Science, University of Toronto
  1978 年博士毕业，现多伦多大学计算机科学荣誉教授、Vector Institute 联合创始人兼首席科学顾问
  h-index: 192 | citations: 1066174
```

- 第一行是方括号里的 ID 和标题。
- 下一行是一句话摘要。
- 然后是最多 5 个关键字段：talent 为 h-index 和被引，cve 为严重程度和 CVSS，trials 为状态和发起方，cases 为法院、案号和日期，等等。
- 最后是标签或研究方向。

检索的 warnings 打到 stderr。talent 的查询像人名时会先按人名匹配，中文名、拼音、英文名的写法互通。

```bash
deepxiv fa search talent "Yann LeCun"
deepxiv fa search talent "deep learning" -F "org=University of Toronto" -F "h_index>=50"
deepxiv fa search talent "扩散模型" -F career_stage=junior --top-k 20 --offset 20
deepxiv fa search talent "Hinton" --mode name
deepxiv fa search trials "pancreatic cancer" -F overall_status=RECRUITING
deepxiv fa search law "个人信息保护" --top-k 5
deepxiv fa search cve "log4j" --json
```

### `fa read`

```
deepxiv fa read DOMAIN ID [ID...] [-l LEVEL] [-e EXTRA] [--view VIEW] [-f FORMAT] [-p k=v]... [--json]
```

| 选项 | |
|---|---|
| `-l`, `--level` | `brief` / `detail` / `full`；不指定则用域的默认级别 |
| `-e`, `--extra NAME` | 读某一个 extra（而不是级别），如 talent 的 `papers` / `network` / `scholar` |
| `--view NAME` | 读某个命名视图（`GET /doc/{id}?view=…`），不能与 `--level` / `--extra` 同用 |
| `-f`, `--format` | `json` / `md` / `html`：服务端渲染，仅对 `spec` 里列出的格式生效 |
| `-p`, `--param k=v` | 额外查询参数，可重复：`section=…`、`contact=1`、`n=3`、`window=2` 等 |

- 一个 ID 读一篇文档；多个 ID 合成一次批量调用（`POST /read`），这时只接受 `--level` / `--extra`。
- 输出：markdown 或 HTML 正文原样打印，结构化数据打印成缩进的 JSON。`--json` 输出完整响应（含 `meta`）。

```bash
deepxiv fa read talent 15023                                  # 默认级别（talent 为 detail）
deepxiv fa read talent 15023 --level brief                    # 只要卡片，最便宜
deepxiv fa read talent 15023 --level full > hinton.md         # 完整调查档案（markdown）
deepxiv fa read talent 15023 --level full -p section=荣誉与奖项  # 档案中的某一节
deepxiv fa read talent 15023 --extra network                  # 合作者、导师、学生
deepxiv fa read talent 15023 --extra source -p n=1            # 参考来源 [1] 的存档页
deepxiv fa read talent 15023 --view scholar                   # 命名视图
deepxiv fa read talent 15023 --format html > hinton.html      # 渲染好的网页
deepxiv fa read talent 15023 3426 --level brief               # 一次读两个人
deepxiv fa read law "chn:law:中华人民共和国个人信息保护法~38"    # 按检索返回的 id 读一条法条
```

各选项返回什么，见[第 6 节](#6-读取级别extra视图章节格式)。

### `fa facets`

```
deepxiv fa facets DOMAIN FIELD [--limit N] [--json]
```

某个字段的取值和计数，按出现次数从多到少排列，用来查 `-F` 的确切写法。可用字段见 `spec` → `facets`（talent：`orgs`、`orgs_current`、`areas`、`role_norm`、`career_stage`、`location`、`last_paper_year`）。

```bash
deepxiv fa facets talent orgs --limit 20
deepxiv fa facets talent career_stage
```

### `fa resolve`

```
deepxiv fa resolve NAME [NAME...] [--json]
```

把一批人名（论文作者、实验室主页）核对成 talent ID，每次最多 50 个。对每个名字，能唯一确定时打印 `→ ID`，否则打印候选人数，后面列出最多 5 个候选。

```bash
deepxiv fa resolve "Geoffrey Hinton" "Yann LeCun" "Yoshua Bengio"
```

### `fa ask`

```
deepxiv fa ask QUESTION [-d DOMAIN] [-e EFFORT] [-p k=v]... [--no-stream] [--no-sources] [-v] [--json]
```

带引用的回答：agent 替你检索并阅读该域。**需要注册 key。**

| 选项 | |
|---|---|
| `-d`, `--domain` | 指定域；不指定时由 1stAuthor 在你的 key 可用的域里选一个，stderr 会打出 `🧭 routed to …`；把握不大时会提示你用 `-d` 指定 |
| `-e`, `--effort` | `low` / `medium` / `high`；不指定则用域的默认值。越高读得越多、越贵 |
| `-p`, `--param k=v` | 域专属的 ask 参数，可重复。值按 JSON 类型发送：`5` → 数字，`true` → 布尔，`{…}` / `[…]` → 对象或数组 |
| `--no-stream` | 等完整答案，不流式输出 |
| `--no-sources` | 不打来源 |
| `-v`, `--verbose` | 在 stderr 额外显示开始、工具调用、警告、运行统计和剩余 agentic 配额 |
| `--json` | 输出一个 JSON 对象（`answer`、`sources`、`stats`、`meta`） |

各域的 ask 参数（最新列表以 `deepxiv fa spec DOMAIN` 为准）：

| 域 | 参数 | |
|---|---|---|
| `talent` | `top_k` | 每次库内检索取多少候选（默认 20） |
| `law` | `scope` | `auto` / `law`（法条）/ `case`（判决）/ `both` |
| `cases` | `scope` | 与 law 同一个 agent，默认 `case`（只查判决） |
| `law` | `jurisdiction` | ISO3 代码（默认由模型判断） |
| `appraise` | `paper` | 直接指定论文（arXiv ID / DOI / 标题），跳过识别 |
| `appraise` | `filters` | 限定使用哪些引用，格式同检索的过滤条件 |

输出：

- 在终端里，答案边生成边流式打到 stdout；stdout 被重定向或接管道时，CLI 等答案结束后一次性写出，文件里只有最终答案（见下面的 `answer_reset`）。引用形如 `[talent:15023 Geoffrey Hinton]` 或 `[中华人民共和国个人信息保护法 第三十八条]`。
- 答案结束后，来源按类别分组（如 `laws`、`cases`、`people`）打到 stderr。
- 如果 agent 在流开始后失败，CLI 会打出 `❌ code: message`，配额已退还时附上 `(quota refunded)`，并以 1 退出。

```bash
deepxiv fa ask "自监督学习领域最有影响力的研究者有哪些" --domain talent
deepxiv fa ask "多伦多大学有哪些做深度学习的研究者"                         # 自动选域
deepxiv fa ask "中国个人信息保护法对个人信息出境有什么要求" -d law -p scope=law -e high
deepxiv fa ask "院士们怎么评价这篇论文" -d appraise -p paper=1706.03762
deepxiv fa ask "2024 年被 CISA 列入在野利用、CVSS 9 分以上的 RCE 有哪些" -d cve -e low
deepxiv fa ask "有哪些正在招募的胰腺癌三期临床试验" -d trials
deepxiv fa ask "Who is Yann LeCun?" -d talent --json > answer.json
```

### `fa whoami`

```
deepxiv fa whoami [--json]
```

**免费。** 显示 token 的类型和名称、今日通用配额（已用 / 上限 / 剩余），以及 agentic 配额（档位 / 已用 / 上限 / 剩余），或者 `ask` 不可用的原因。

## 5. 过滤

`-F` 每个写一个表达式，多个之间为 AND：

| 写法 | 含义 | 实际发送 |
|---|---|---|
| `k=v` | 等于 | `{"k": "v"}` |
| `k=a,b` | 任一 | `{"k": ["a", "b"]}` |
| `k>=n`、`k<=n` | 上下界；同一字段的两个界会合并 | `{"k": {"gte": n}}` / `{"k": {"lte": n}}` |
| `k=n..m` | 闭区间，缺一端即为开区间（`2024..`）；日期也行（`2024-01..2024-06`） | `{"k": {"gte": n, "lte": m}}` |
| `k~text` | 全文匹配 | `{"k": {"text": "text"}}` |

- 字段名、类型、允许的运算符因域而异，见 `deepxiv fa spec DOMAIN`。
- 值会按字段类型转换：整数、数字、布尔（`true/false/yes/no/1/0`）。
- 发送前，CLI 会先取 spec（免费）校验过滤条件。未知字段、不允许的运算符、类型不对的值会立即报错（退出码 2）并列出可用字段，不扣配额。
- 同一个字段不能写两次，`>=` 与 `<=` 合并的情况除外。
- 含 `>`、`<` 的表达式要加引号，否则 shell 会把它当重定向。

```bash
-F "org=University of Toronto"              # 关键字等于
-F career_stage=junior,senior               # 任一
-F "h_index>=50" -F "h_index<=120"          # 两个界合成区间
-F last_paper_year=2023..                   # 开区间
-F has_profile=true                         # 布尔
-F names~Hinton                             # 全文
```

## 6. 读取：级别、extra、视图、章节、格式

- **级别**（`--level`）是主要的调节旋钮。`brief` 是检索命中里的那张卡片；`detail` 满足大多数需求（talent 的默认值）；`full` 是全部内容，有长文的域给 markdown。越深越贵（talent：1 / 3 / 10）。有些域按 ID 类型区分级别。例如 `law` 的法条 ID（如 `…~38`）：`brief` 是卡片，`detail` 是原文 + 译文 + 抽取，`full` 是该条加前后条和所属章。详见 `spec --json` → `read.levels_by_id`。
- **extra**（`--extra`）读文档的某一个侧面，单独计价。talent 的 extra：`papers`（代表作）、`network`（合作者、导师、学生）、`scholar`（Scholar 指标快照）、`scholar_live`（实时抓取，更贵）、`sources`（档案的参考来源）、`source`（某条来源的存档页，配 `-p n=<编号>`）。law 的 extra：`cases`（引用该法条的判决）。
- **章节**：`--level full -p section=<名字>` 读长文档中的某一节。章节名见 `detail` 结果里的 `sections`（talent：`教育背景`、`工作履历`、`荣誉与奖项` 等）。
- **视图**（`--view`）是底层的命名渲染（`spec --json` → `views`）。级别和 extra 都会映射到视图，一般不需要直接用 `--view`。
- **格式**（`--format`）：`html` 在域列出时返回渲染好的网页（`spec --json` → `read.formats`；talent：`detail:html`），其余情况下仍返回 JSON。
- **其它参数**用 `-p` 传：`contact=1`（talent 完整档案带联系方式一节）、`window=N`（law 上下文）等，各域 `spec --json` 的 `notes` 里有说明。

## 7. 输出与退出码

与 `deepxiv ask` 一致：

- **stdout**：只有数据，即命中、文档、答案，或 `--json` 的 JSON。
- **stderr**：其它内容，包括配额（`💳 cost 2 · 990/1000 left today`）、路由（`🧭 routed to talent`）、来源、提示（`💡 Read one: …`）、警告和错误。

所以 `> file` 和 `| jq` 拿到的总是干净的数据：

```bash
deepxiv fa read talent 15023 --level full > hinton.md
deepxiv fa search talent "Geoffrey Hinton" --json | jq '.hits[0].id'
```

| 退出码 | |
|---|---|
| `0` | 成功 |
| `1` | API 或网络错误，包括 401 / 403 / 429 / 4xx / 5xx，以及 `ask` 流里出现 `error` 事件 |
| `2` | 用法错误：过滤条件不合法、`--param` 写错、选项冲突、选项取值不对 |

## 8. 计费与配额

| 调用 | 扣哪个池 | 价格 |
|---|---|---|
| `domains`、`spec`、`whoami` | — | 免费 |
| `search` | 通用 daily limit | 2（`--head` 为 3） |
| `read` | 通用 daily limit | 按级别 / extra / format 计，全部价格见 `spec`（talent：brief 1、detail 3、full 10，extra 1–20） |
| `facets` | 通用 daily limit | 1 |
| `resolve` | 通用 daily limit | 2 |
| `ask` | agentic 配额（与 `deepxiv ask` 共用） | 每次 1 次，与域和 effort 无关；**仅限注册 key** |

- 通用 daily limit：自动注册的 token 为 1,000，注册 key 为 10,000。注册 key 另有每天 300 次免费 agentic 调用。见 [USAGE.zh.md § Token 与额度](USAGE.zh.md#token-与额度)。
- 每次付费调用后，CLI 会在 stderr 打出 `💳 cost N · 剩余/上限`，剩余不足 20 时会提醒。
- `fa ask` 在 agentic 配额剩余不足 5 次时提醒（`-v` 时总会显示）。
- 每个 key 最多**同时跑 4 个 `ask`**。
- 1stAuthor 的免费样例查询和 ID（`spec` → `free_samples`）不扣费。
- 需要更大额度的 1stAuthor 服务，请看 [1stauthor.com](https://1stauthor.com)。

## 9. 错误与重试

以下情况 CLI 都会在 stderr 说明原因，并以 1 退出：

| 看到的提示 | 原因 | 怎么办 |
|---|---|---|
| `fa ask` 需要注册账号的 key | 403：用 SDK token 调了 `ask` | 注册后执行 `deepxiv config --token …` |
| 认证失败（401） | token 缺失或无效 | `deepxiv token` 查看，或设置 `DEEPXIV_TOKEN` |
| 已到日使用上限 | 429：通用 daily limit 用完 | 等明天，或注册以提高额度 |
| Too many concurrent requests, retry in Ns | 带 `Retry-After` 的 429：同时超过 4 个 `ask` | 按提示等待 |
| Rate-limited by 1stAuthor | 429：1stAuthor 的按用户限流 | 放慢速度 |
| `HTTP 400 invalid_request: …` 加一个列表 | extra、级别、视图或过滤条件写错 | 从错误下方列出的可选值中选 |
| `HTTP 404 …` | 没有这个 ID 的文档 | 从 `search` / `resolve` 取 ID |
| 答案输出一半后出现 `❌ <code>: <message> (quota refunded)` | `ask` 的 agent 在流中途失败 | 重试；提示里写了 refunded 就说明配额已退还 |

在报错之前，CLI 会自动重试：

- **带 `Retry-After` 且 ≤ 30 秒的 429**：等待后重试一次。
- **GET 请求的网络错误**（`domains`、`spec`、`read`、`facets`、`whoami`）：重试一次。POST（`search`、`resolve`、`ask`）不自动重试，避免重复扣费。

## 10. Python 接口

```python
from deepxiv_sdk import FAClient, FAError, FilterError, Reader, build_filters
```

### `FAClient`

```python
FAClient(token=None, base_url="https://data.rag.ac.cn/fa", timeout=120.0, session=None)
reader.fa()          # 同一个客户端，沿用 Reader 的 token、base URL 和超时
```

| 方法 | 接口 | 返回 |
|---|---|---|
| `domains()` | `GET /v1/domains` | `{"domains": [...]}` |
| `spec(domain)` | `GET /v1/{domain}` | 域的自描述 |
| `whoami()` | `GET /v1/whoami` | `{"source", "name", "subject", "quota", "agent", ...}` |
| `search(domain, query, *, top_k, offset, mode, filters, fields, sort)` | `POST /v1/{domain}/search` | `{"hits": [{"id", "score", "brief"}], "total", "warnings", "meta"}` |
| `read(domain, id, *, level, extra, format, **params)` | `GET /v1/{domain}/read/{id}` | `{"data": {...}}` 或 `{"text": "..."}`（markdown / HTML），另含 `meta` |
| `read_many(domain, ids, *, level, extra, params)` | `POST /v1/{domain}/read` | 一次调用返回多篇文档 |
| `doc(domain, id, view=None, **params)` | `GET /v1/{domain}/doc/{id}?view=` | 某个命名视图 |
| `facets(domain, field, limit=None)` | `GET /v1/{domain}/facets` | `{"values": [{"value", "count"}]}` |
| `resolve(names)` | `POST /v1/talent/resolve` | `{"results": [{"query", "candidates", "resolved"}]}` |
| `ask(query, domain=None, *, effort, **extra)` | `POST /v1/{domain}/ask` 或 `/v1/ask` | `{"answer", "sources", "stats", "meta"}` |
| `ask_stream(query, domain=None, *, effort, **extra)` | `POST …/ask/stream` | 事件字典的迭代器 |

- `**params` / `**extra` 原样透传，如 `read(..., section="荣誉与奖项")`、`ask(..., scope="law")`。
- `fields="head"` 对应 CLI 的 `--head`；`sort` 透传给支持排序的域。
- `client.last_quota` 是上一次调用的配额响应头：`{"general": {"cost", "used", "daily_limit", "remaining"}, "agent": {"tier", "daily_limit", "used", "remaining"}}`。每个 JSON 响应里也带 `meta.quota`。

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

### 流式

```python
for event in fa.ask_stream("多伦多大学有哪些做深度学习的研究者"):
    kind = event["event"]
    if kind == "route":
        print("routed to", event["domain"])
    elif kind == "answer_delta":
        print(event["delta"], end="", flush=True)
    elif kind == "answer_reset":               # 替换此前已显示的内容
        print("\n" + event["answer"], end="", flush=True)
    elif kind == "sources":
        sources = event["sources"]
    elif kind == "error":                       # HTTP 仍是 200，必须检查
        raise RuntimeError(f'{event["code"]}: {event["message"]}')
```

| 事件 | 何时出现 | 字段 |
|---|---|---|
| `route` | 仅在不指定域时出现，最先到达 | `domain`、`method`、`confident` |
| `start` | 开始运行 | `domain`、`effort`、`max_rounds` |
| `tool_call` / `tool_result` / `warning` | agent 工作过程中（并非每个域都发） | 工具名、参数、摘要 |
| `answer_start` | 第一个 token 之前 | — |
| `answer_delta` | 多次，随模型生成实时到达 | `delta` |
| `answer_reset` | 少见：模型在调工具前先写了一句过程说明（"我先查一下…"） | `answer`、`reason`：丢弃此前已显示的内容，改用 `answer` |
| `sources` | 答案之后 | `sources`（按类别分组）、`citation_format` |
| `done` | 结束 | `stats`（`rounds`、`tool_calls`、`elapsed_s`、`answer_truncated` 等） |
| `error` | 失败时，取代后续事件 | `code`、`message`、`refunded` |

### 错误

```python
try:
    fa.ask("…", "talent")
except FAError as e:
    e.status                # HTTP 状态码（网络错误、流中断时为 None）
    e.code                  # 1stAuthor 错误码，如 "invalid_request"；deepxiv 自身的错误为 None
    e.message               # 可读的错误信息
    e.details               # 如 {"extras": [...]} 或 {"allowed": [...]}
    e.retry_after           # 秒数，取自 Retry-After
    e.request_id            # 反馈问题时附上
    e.needs_registered_key  # SDK token 调 ask 得到 403 时为 True
```

`FAError` 是 `deepxiv_sdk.APIError` 的子类。

### 过滤辅助函数

```python
build_filters(["org=University of Toronto", "h_index>=50"], schema)   # → 过滤字典
build_filters(["year=2024"], None)                                    # 不传 schema：只按形状转换类型
```

`schema` 取 `spec(domain)["search"]["filters"]`；表达式不合法时抛 `FilterError`（`ValueError` 的子类）。

## 11. HTTP 接口

不用 Python 时，也可以拿你的 deepxiv token 直接调同一组接口：

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

- 响应里有 `meta.quota` 和 `X-DeepXiv-Quota-Cost / -Used / -Daily-Limit / -Remaining` 头；ask 的响应还有 `X-DeepXiv-Agent-Tier / -Daily-Limit / -Used / -Remaining` 头。
- 错误有两种格式：deepxiv 自身的 `{"detail": "..."}`（鉴权、配额、ask 资格），以及 1stAuthor 透传的 `{"error": {"code", "message", "details"}, "request_id"}`。
- `ask/stream` 返回 NDJSON，事件见上表。

## 12. 从 `deepxiv talent` 迁移

`deepxiv talent search` 和 `deepxiv talent survey` 作为弃用别名保留一个版本，调用时会打印警告：

| 旧 | 新 |
|---|---|
| `deepxiv talent search "query"` | `deepxiv fa search talent "query"` |
| `--limit N` / `--offset N` | `--top-k N` / `--offset N` |
| `--tags A,B` / `--career-stage S` | `-F areas=A,B` / `-F career_stage=S` |
| `--semantic`、`--sort`、`--order`、`--investigated`、`-v` | 忽略：检索现在一律是混合检索 |
| `--format json` / `--json` | `--json` |
| `deepxiv talent survey ID` | `deepxiv fa read talent ID` |
| `survey --format markdown` | `fa read talent ID --level full` |
| `survey --refresh` / `--no-refresh` | 忽略；要实时 Scholar 数据用 `fa read talent ID --extra scholar_live` |
| `Reader.talent_search(q, limit=, offset=)` | `Reader.fa().search("talent", q, top_k=, offset=)` |
| `Reader.talent_survey(id)` | `Reader.fa().read("talent", id)` |

**旧人才库的 ID 在新库里不通用**，请用 `fa search talent` 或 `fa resolve` 重新查。

## 13. 常见问题

- **过滤条件被拒？** 字段名因域而异：用 `deepxiv fa spec DOMAIN` 查字段，用 `deepxiv fa facets DOMAIN FIELD` 查确切取值。
- **加了过滤就没结果？** 取值必须完全一致。`facets` 能看到库里的实际写法，例如 `orgs` 里中英文名混存。
- **`fa read talent` 找不到？** ID 来自 `fa search talent` 或 `fa resolve`。旧 talent ID、arXiv ID、Scholar ID 都不通用。
- **某人 `--level full` 返回 404？** 他的卡片上 `has_profile: false`，只有卡片级数据。
- **`--format html` 还是打印 JSON？** 该域没有 HTML 渲染，`spec --json` → `read.formats` 列出了实际支持的格式。
- **`standards` 没有正文？** 这个域只有目录元数据。
- **`fa ask` 不带 `--domain` 时答错了域？** 路由只在你的 key 可用的域里选，没有合适的域时会提示 `low confidence`。请用 `--domain` 指定。
- **其它问题？** 欢迎[提 issue](https://github.com/DeepXiv/deepxiv_sdk/issues)。deepxiv 和 1stAuthor 的垂域都还在 beta。
