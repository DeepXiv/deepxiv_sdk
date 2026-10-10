# deepxiv fa —— 1stAuthor 垂域

> **English**: [FA.md](FA.md) · 返回 [README](README.zh.md) · 完整 CLI 参考：[USAGE.zh.md](USAGE.zh.md)

DeepXiv 与 [1stAuthor](https://1stauthor.com) 深度合作，提供 arXiv 之外的多领域数据服务。`deepxiv fa` **用你的 deepxiv token** 访问 1stAuthor 的垂域：学者、法规、裁判文书、临床试验、药品说明书、科研基金、公司公告、标准、漏洞、美国联邦公报。请求经 `data.rag.ac.cn/fa` 转发，不需要另外申请 1stAuthor 的 key。

DeepXiv 本身专注于学术论文的 agentic 数据服务，**将持续免费**。如需更大额度的 1stAuthor 相关服务，可以到 [1stauthor.com](https://1stauthor.com) 看看。

> **Beta。** `deepxiv fa` 在 `1.2.0b1` 里，暂时仅源码安装；1stAuthor 目前处于纯内测阶段。任何问题欢迎[提 issue](https://github.com/DeepXiv/deepxiv_sdk/issues)。
>
> ```bash
> pip install git+https://github.com/DeepXiv/deepxiv_sdk.git
> ```

**目录**：[有哪些域](#有哪些域) · [快速上手](#快速上手) · [命令](#命令) · [过滤](#过滤) · [输出](#输出) · [计费与配额](#计费与配额) · [错误](#错误) · [Python](#python) · [从 `deepxiv talent` 迁移](#从-deepxiv-talent-迁移) · [常见问题](#常见问题)

## 有哪些域

| 域 | 内容 | `fa ask` |
|---|---|---|
| `talent` | 约 19 万 AI 研究者，约 16 万份调查档案（教育、履历、代表作、开源），Google Scholar 指标实时渲染 | ✅ |
| `law` | 26 个法域约 3.3 万部法规 / 150 万条，按条检索，附中译 | ✅ |
| `us_law` | 美国 53 个法域约 500 万条条款级文本：成文法、联邦法规（CFR）、会期法、机构裁决 | |
| `cases` | 裁判文书：中国约 1,750 万篇 + 美国判例约 344 万篇 | |
| `trials` | ClinicalTrials.gov 全量临床研究（约 60 万项），抽取了入排标准、生物标志物、摘要 | |
| `drugs` | 约 25.6 万份美国药品说明书（openFDA SPL）：适应症、禁忌、相互作用、黑框警告 | |
| `grants` | 约 120 万项 NSF 资助与 NIH 项目 | |
| `filings` | 约 120 万份美股 + A 股公告与监管文书（8-K、10-K、定期报告、处罚） | |
| `standards` | 约 7.9 万条中国国家标准（GB / GB/T / GB/Z），只有目录元数据，没有正文 | |
| `cve` | 约 38.4 万条公开漏洞（NVD），含 CISA KEV 与 EPSS | |
| `fr` | 1994 年以来约 100 万篇美国联邦公报 | |
| `appraise` | 一篇论文被哪些院士 / 会士引用过、他们原话怎么说 | ✅ |

以上为实时列表的快照。最新列表和规模以 `deepxiv fa domains` 为准，每个域能做什么看 `deepxiv fa spec <域>`。论文和网页不在这里，它们走 deepxiv 原生命令（`deepxiv search`、`paper`、`ask`）。

## 快速上手

```bash
deepxiv fa domains                                    # 有哪些域（免费）
deepxiv fa spec talent                                # 过滤字段、读取级别、价格（免费）

deepxiv fa search talent "Geoffrey Hinton"            # 查人
deepxiv fa read talent 15023                          # 读档案
deepxiv fa search law "个人信息保护" --top-k 5
deepxiv fa ask "自监督学习领域最有影响力的研究者有哪些" --domain talent
```

流程和读论文一样：**先 search，只读需要的部分，想要综合答案时再 ask。**

## 命令

### `fa domains` / `fa spec DOMAIN`（免费）

`spec` 是域的自描述，列出过滤字段及运算符、读取级别和 extra 的价格、可做 facets 的字段、免费样例和 quickstart。第一次在某个域里加过滤前，先看一眼。

### `fa search DOMAIN "query"`

```bash
deepxiv fa search talent "Yann LeCun"                                  # 英文名、中文名、拼音都行
deepxiv fa search talent "deep learning" -F "org=University of Toronto" -F "h_index>=50"
deepxiv fa search talent "扩散模型" -F career_stage=junior --top-k 20
deepxiv fa search trials "pancreatic cancer" -F overall_status=RECRUITING
deepxiv fa search cve "log4j" --json
```

| 选项 | |
|---|---|
| `--filter`, `-F EXPR` | 可重复，之间为 AND，见[过滤](#过滤) |
| `--top-k`, `-k N` | 命中数，1~100（默认 10） |
| `--offset N` | 翻页 |
| `--mode MODE` | 检索模式（域支持多种时，如 talent 的 `hybrid`、`dense`、`bm25`、`name`） |
| `--head` | 更丰富的命中（`fields=head`），更贵 |
| `--json` | 完整响应 |

### `fa read DOMAIN ID [ID ...]`

```bash
deepxiv fa read talent 15023                                  # 默认级别（talent 为 detail）
deepxiv fa read talent 15023 --level brief                    # 只要卡片，最便宜
deepxiv fa read talent 15023 --level full                     # 完整调查档案（markdown）
deepxiv fa read talent 15023 --level full -p section=荣誉与奖项  # 档案中的某一节
deepxiv fa read talent 15023 --extra network                  # 合作者、导师、学生
deepxiv fa read talent 15023 --format html > hinton.html      # 渲染好的网页
deepxiv fa read talent 15023 3426 --level brief               # 一次读多个 id
```

| 选项 | |
|---|---|
| `--level`, `-l` | `brief` / `detail` / `full`；不指定则用域的默认级别 |
| `--extra`, `-e NAME` | 单个 extra（talent：`papers`、`network`、`scholar`、`scholar_live`、`sources` 等） |
| `--view NAME` | 读某个命名视图（`GET /doc/{id}?view=…`） |
| `--format`, `-f` | `json` / `md` / `html`，服务端渲染 |
| `--param`, `-p k=v` | 额外查询参数，可重复（如 `section=…`、`contact=1`） |
| `--json` | 输出完整响应，而不只是文档 |

先读 `--level brief`，不够再往下读。`full` 的价格是 `brief` 的好几倍。

### `fa facets DOMAIN FIELD`

某个过滤字段的取值和计数，`-F` 该写什么，在这里查确切写法：

```bash
deepxiv fa facets talent orgs --limit 20
deepxiv fa facets talent career_stage
```

### `fa resolve NAME [NAME ...]`

把一批人名（论文作者、团队主页）核对成 talent id，每次最多 50 个：

```bash
deepxiv fa resolve "Geoffrey Hinton" "Yann LeCun" "Yoshua Bengio"
```

### `fa ask "question"`

在某个域上得到带引用的回答：agent 替你检索并阅读。

```bash
deepxiv fa ask "自监督学习领域最有影响力的研究者有哪些" --domain talent
deepxiv fa ask "个人信息出境需要满足什么条件" --domain law --effort high
deepxiv fa ask "哪些院士引用过 Attention Is All You Need，怎么评价的"   # 不指定 --domain：自动选域
```

| 选项 | |
|---|---|
| `--domain`, `-d` | 指定域；不指定时由 1stAuthor 选域，stderr 会打出 `🧭 routed to …` |
| `--effort`, `-e` | `low` / `medium` / `high` |
| `--no-stream` | 等完整答案 |
| `--no-sources` | 不打来源 |
| `--verbose`, `-v` | 在 stderr 打出进度、工具调用、配额 |
| `--json` | 输出一个 JSON 对象（非流式） |

需要**注册 key**，见[计费与配额](#计费与配额)。

### `fa whoami`（免费）

当前用的是哪种 token（自动注册的 SDK token 还是注册 key）、今日通用配额，注册 key 还会显示 agentic 配额。

## 过滤

`-F` 每个写一个表达式，多个之间为 AND：

| 写法 | 含义 | 实际发送 |
|---|---|---|
| `k=v` | 等于 | `{"k": "v"}` |
| `k=a,b` | 任一 | `{"k": ["a", "b"]}` |
| `k>=n`、`k<=n` | 上下界 | `{"k": {"gte": n}}` / `{"k": {"lte": n}}` |
| `k=n..m` | 闭区间（日期也行：`2024-01..2024-06`） | `{"k": {"gte": n, "lte": m}}` |
| `k~text` | 全文匹配 | `{"k": {"text": "text"}}` |

字段名、类型、允许的运算符因域而异，以 `deepxiv fa spec DOMAIN` 为准。CLI 会在发送前按 spec 校验，所以未知字段或不允许的运算符会立刻报错并列出可用字段，不扣配额。含 `>`、`<` 的表达式要加引号，否则 shell 会把它当重定向。

## 输出

与 `deepxiv ask` 一致：

- **stdout**：数据，包括命中、文档、答案。
- **stderr**：配额（`💳 cost 2 · 990/1000 left today`）、路由、来源、提示和警告。

所以 `deepxiv fa read talent 15023 --level full > hinton.md` 只会拿到档案本身。`--json` 输出完整响应（含 `meta.quota`）。

## 计费与配额

| 调用 | 扣哪个池 | 价格 |
|---|---|---|
| `domains`、`spec`、`whoami` | — | 免费 |
| `search` | 通用 daily limit | 2（`--head` 为 3） |
| `read` | 通用 daily limit | 按级别 / extra / format 计（talent：brief 1、detail 3、full 10），全部价格见 `spec` |
| `facets` | 通用 daily limit | 1 |
| `resolve` | 通用 daily limit | 2 |
| `ask` | agentic 配额（与 `deepxiv ask` 共用） | 每次 1 次；**仅限注册 key** |

- 除 `ask` 外，任何 token 都能用，包括 deepxiv 首次使用时自动申请的 token。
- 自动申请的 token 调 `ask` 会得到 **403**。到 [data.rag.ac.cn/register](https://data.rag.ac.cn/register) 注册，再执行 `deepxiv config --token YOUR_KEY`。注册 key 每天免费 300 次 agentic 调用。
- 每个 key 最多**同时跑 4 个 `ask`**。
- 1stAuthor 的部分免费样例查询不扣费。

需要更大额度的 1stAuthor 服务，请看 [1stauthor.com](https://1stauthor.com)。

## 错误

以下情况 CLI 都会在 stderr 说明原因，并以 1 退出：

| 看到的提示 | 原因 | 怎么办 |
|---|---|---|
| `fa ask` 需要注册账号的 key | 403：用 SDK token 调了 `ask` | 注册后用 `deepxiv config` 填入 |
| 认证失败（401） | token 缺失或无效 | `deepxiv token` 查看，或设置 `DEEPXIV_TOKEN` |
| 已到日使用上限 | 429：通用 daily limit 用完 | 等明天，或注册以提高额度 |
| Too many concurrent requests, retry in Ns | 429：同时超过 4 个 `ask` | 按提示等待 |
| Rate-limited by 1stAuthor | 429：1stAuthor 的按用户限流 | 放慢速度 |
| `HTTP 400 invalid_request: …` 加一个列表 | extra、级别或过滤条件写错 | 从错误下方列出的可选值中选 |
| 答案输出一半后出现 `❌ <code>: <message> (quota refunded)` | `ask` 的 agent 在流中途失败 | 重试；提示里写了 refunded 就说明配额已退还 |

## Python

```python
from deepxiv_sdk import FAClient, FAError, Reader, build_filters

fa = FAClient(token="...")                      # 或 Reader(token="...").fa()

fa.domains()                                    # 免费
spec = fa.spec("talent")                        # 免费

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

# 仅限注册 key
answer = fa.ask("自监督学习领域最有影响力的研究者有哪些", "talent")

for event in fa.ask_stream("哪些院士引用过 Attention Is All You Need"):   # 不指定域：自动选域
    kind = event["event"]
    if kind == "route":
        print("routed to", event["domain"])
    elif kind == "answer_delta":
        print(event["delta"], end="")
    elif kind == "error":                       # HTTP 仍是 200，必须自己检查
        raise RuntimeError(event["message"])

try:
    fa.ask("…", "talent")
except FAError as e:
    if e.needs_registered_key:
        print("请到 https://data.rag.ac.cn/register 注册")
    else:
        print(e.status, e.code, e.message, e.details, e.retry_after)
```

流式事件依次为：`route`（仅在不指定域时出现）→ `start` → `answer_start` → `answer_delta`… → `sources` → `done`。流开始后的失败以 `{"event": "error", "code", "message", "refunded"}` 的形式出现在流里。

## 从 `deepxiv talent` 迁移

`deepxiv talent search` 和 `deepxiv talent survey` 作为弃用别名保留一个版本，调用时会打印警告：

| 旧 | 新 |
|---|---|
| `deepxiv talent search "query"` | `deepxiv fa search talent "query"` |
| `--tags A,B` / `--career-stage S` | `-F areas=A,B` / `-F career_stage=S` |
| `--semantic`、`--sort`、`--order`、`--investigated` | 忽略：检索现在一律是混合检索 |
| `deepxiv talent survey ID` | `deepxiv fa read talent ID` |
| `survey --format markdown` | `fa read talent ID --level full` |
| `survey --refresh` | `fa read talent ID --extra scholar_live`（实时 Scholar 数据） |
| `Reader.talent_search(q)` / `talent_survey(id)` | `Reader.fa().search("talent", q)` / `.read("talent", id)` |

**旧人才库的 ID 在新库里不通用**，请用 `fa search talent` 或 `fa resolve` 重新查。

## 常见问题

- **过滤条件被拒？** 字段名因域而异：用 `deepxiv fa spec DOMAIN` 查字段，用 `deepxiv fa facets DOMAIN FIELD` 查确切取值。
- **`fa read talent` 找不到？** ID 来自 `fa search talent` 或 `fa resolve`。旧 talent ID、arXiv ID、Scholar ID 都不通用。
- **某人 `--level full` 返回 404？** 他的卡片上 `has_profile: false`，只有卡片级数据。
- **`standards` 没有正文？** 这个域只有目录元数据。
- **其它问题？** 欢迎[提 issue](https://github.com/DeepXiv/deepxiv_sdk/issues)。deepxiv 和 1stAuthor 的垂域都还在 beta。
