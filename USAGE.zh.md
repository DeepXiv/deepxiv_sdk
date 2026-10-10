# 使用指南

CLI 与 Python 两个入口的完整参考。精简版见 [README.zh.md](README.zh.md)。

> **English**: [USAGE.md](USAGE.md)

**目录** —— [安装](#安装) · [Token 与额度](#token-与额度) · **CLI**：[ask](#cliagentic-searchdeepxiv-ask) · [检索](#cli检索) · [读论文](#cli读论文) · [fa：1stAuthor 垂域](#clifa--1stauthor-垂域talentlawtrials) · [其他数据源](#其他数据源) · [Agent 集成](#agent-集成) · **Python**：[Agentic Search](#agentic-search) · [Reader 方法](#reader-方法) · [错误处理](#错误处理和重试) · [批量处理](#批量处理) · [research agent](#使用代理进行复杂分析) · [故障排查](#故障排查)

## 安装

```bash
pip install deepxiv-sdk              # Reader + CLI
pip install "deepxiv-sdk[all]"       # + 内置 research agent（需要你自己的 LLM key）
pip install git+https://github.com/DeepXiv/deepxiv_sdk.git   # 1.2.0b1，含 `deepxiv fa`（beta）
```

```python
from deepxiv_sdk import Reader

reader = Reader(token="...")                              # 免费论文之外都需要
reader = Reader(token="...", timeout=60, max_retries=3)   # 也可调传输参数

# `Reader` 自己不读 DEEPXIV_TOKEN —— 只有 CLI 读。需要显式传入：
import os
reader = Reader(token=os.environ["DEEPXIV_TOKEN"])
```

## Token 与额度

deepxiv 依次从 `--token`、`DEEPXIV_TOKEN`、`~/.env` 解析 token，首次使用会自动注册一个。

| | 通用 daily limit | Agentic 调用（`ask`、`fa ask`） | 获取方式 |
|---|---|---|---|
| 自动注册 | 1,000 请求 | ❌ 不可用 | 首次使用 CLI 时自动完成 |
| 注册用户 | 10,000 请求 | ✅ 300 次/天 | [data.rag.ac.cn/register](https://data.rag.ac.cn/register) |
| 自定义 | 联系我们 | 联系我们 | 邮件 `tommy[at]chien.io` |

两份额度相互独立：agentic 调用不消耗通用额度，反之亦然。找回 key：[data.rag.ac.cn/token-lookup](https://data.rag.ac.cn/token-lookup)（支持 Google 注册，方便没有中国手机号的用户）。

免费测试论文（无需 token）—— arXiv：`2409.05591`、`2504.21776`；PMC：`PMC544940`。

### 数据覆盖

| 数据源 | 状态 |
|---|---|
| arXiv | ✅ 全文，T+1 同步 |
| Web | ✅ Google + 缓存页面正文 |
| PubMed Central | ✅ 生物医学与生命科学 |
| bioRxiv / medRxiv | ✅ 生物与医学预印本 |

DeepXiv 聚焦开放获取文献，让 agent 在无限制的数据上工作，而不是撞上订阅墙。

---

# CLI 参考

## CLI：Agentic Search（`deepxiv ask`）

两个同构的后端。一个问题进去，服务端自主调工具、按需读原文，流式返回一个带引用的答案。

```bash
deepxiv ask "what speedup does speculative decoding report on HumanEval"
deepxiv ask "Anthropic Claude API 的定价档位" --web
```

| | 后端 | 引用形式 | 适合 |
|---|---|---|---|
| **`deepxiv ask`** | 本地 arXiv 全文库（Qdrant 混合检索 + 论文正文） | `[arXiv:2512.15176]` —— 真实 ID | 方法、数字、实验结果 |
| **`deepxiv ask --web`** | Google + 缓存页面正文 | 指向真实 URL 的 markdown 链接 | 时事、产品、定价，以及一切非学术问题 |

两者都不是搜索框的包装。arXiv 侧真的在读论文章节，web 侧真的在读缓存的页面正文。

**仅限注册用户。** agentic search 需要 [data.rag.ac.cn/register](https://data.rag.ac.cn/register) 的 key，自动注册的 token 会返回 `403`。

### effort 档位

| `--effort` | 检索轮数 | 首 token（arXiv） | 首 token（web） |
|---|---|---|---|
| `default`（默认） | 1–2 | **3–4 秒** | 5–9 秒 |
| `high` | 3 | 7–8 秒 | 约 13 秒 |
| `xhigh` | 4–5 | 9–13 秒 | 更久 |

轮数是上限不是下限 —— 证据够了就会提前收敛。web 更慢是因为 Google 缓存未命中要花 1.7–4.3 秒，这部分不受我们控制。

### 怎么写 query

这比任何 flag 都重要。

- **要具体。** 服务端假设你的 query 已经打磨过。`"what compression ratio does KV cache eviction report on LongBench"` 远胜于 `"kv cache"`。
- **想要数字就明确要数字。** 问"多少加速比"、"哪个 benchmark"会促使服务端去读原文，而不是扫摘要和摘录。
- **中文直接可用。** arXiv query 会被改写成英文术语做检索，web 会切到中文 locale。答案按 query 的语言返回。
- **arXiv 的范围限制写进 query 正文** —— 年份、会议（NeurIPS/ICLR/CVPR）、分类（cs.CL）、作者、机构、最低引用数，它们会变成检索过滤条件。
- **结果不对就换个说法。** 提高 `--effort` 只增加阅读轮数，改变不了第一轮的召回方向。

### 参数

```bash
deepxiv ask "reward hacking in RLHF" --verbose          # 工具调用 + 配额，走 stderr
deepxiv ask "state space models vs transformers" --json # 单个 JSON 对象
deepxiv ask "MoE routing collapse" --no-stream          # 等完整答案
deepxiv ask "diffusion samplers" --all-sources          # 列出全部召回来源

deepxiv ask "NeurIPS 2025 best paper" --web --search-type news
deepxiv ask "retrieval evaluation methodology" --web --search-type scholar
```

`--top-k N`（1–30，仅 arXiv）设定第一轮召回量。`--search-type` / `--gl` / `--hl` 仅 web 可用。`--max-answer-tokens N`（256–16384）限制答案长度；`--language LANG` 覆盖答案语言。

### 关于结果的三件事

> **引用是真的。** 服务端被要求绝不编造 arXiv ID 或 URL，宁可回答"没有相关论文"。`[arXiv:2512.15176]` 直接对应 `https://arxiv.org/abs/2512.15176`。

> **sources 是召回集，不是引用列表。** 召回 10 篇往往只支撑 1 条引用。CLI 默认只显示被引用的来源，`--all-sources` 显示其余。

> **web 证据有两种强度。** 服务端只读**缓存过的**页面正文，从不实时抓取，所以未缓存的页面只贡献一条搜索摘要。中文站点和新闻页被缓存的比例更低。CLI 用 📄 标记完整读到的页面、🔗 标记仅有摘要的，答案里也会标注仅基于摘要的论断。据此判断。

另外：答案触到 `--max-answer-tokens` 时 CLI 会警告，API 会置 `answer_truncated`。被截断的答案不要当完整答案用。

## CLI：读论文

分层读，避免为了回答一个关于某节的问题而加载 5 万 token。

```bash
deepxiv search "agentic memory" --limit 5     # 1. 找候选
deepxiv paper 2409.05591 --brief              # 2. 值不值得读？
deepxiv paper 2409.05591 --head               # 3. 结构与 token 分布
deepxiv paper 2409.05591 --section Method     # 4. 只读要紧的那节
```

- `--brief` —— 标题、TLDR、关键词、引用数、GitHub URL
- `--head` —— 章节概览与 token 分布
- `--section NAME` —— 单节（`Introduction`、`Method`、`Experiments`…）
- `--preview` / `--raw` / *(不加 flag)* —— 约 1 万字符预览 / 全文 markdown / 完整论文
- `--popularity` —— 单篇论文的社交影响力指标

## CLI：检索

```bash
deepxiv search "transformer" --limit 10 --format json

# 按作者、机构、分类过滤（逗号分隔）
deepxiv search "image generation" --authors "Shitao Xiao" --categories cs.CV --limit 5

# 按会议过滤（可重复；NeurIPS ↔ NIPS 别名自动匹配）
deepxiv search "diffusion model" --venue NeurIPS --venue-year 2025 --limit 5

# 按日期和引用数过滤（日期接受 YYYY、YYYY-MM、YYYY-MM-DD）
deepxiv search "diffusion models" --date-from 2024-01 --min-citations 50

# 高级日期模式：exact / after / before / between
deepxiv search "image generation" \
  --date-search-type between --date-str 2025-06-01 --date-str 2025-07-01

# 分页与可选的精排
deepxiv search "LLM alignment" --limit 10 --offset 10
deepxiv search "transformer model" --use-fine-rerank
```

`--authors` 和 `--orgs` 既是过滤条件也是排序信号；`--categories` 是纯过滤。过滤条件之间取 `AND`，所以在高引用门槛上再叠一个窄日期窗，返回 0 条是合理的 —— 松开一个。

返回 `{status, total_count, result: [...]}`。每条结果带 `arxiv_id`、`title`、`abstract`、`tldr`、`authors`、`categories`、`citation_count`、`date`、`github_url`、`score`，已知时还有 `venue`/`venue_year`。

## CLI：fa —— 1stAuthor 垂域（talent、law、trials……）

> **Beta。** 功能在 `1.2.0b1`，仅源码安装。**完整文档：[FA.zh.md](FA.zh.md)。**

`deepxiv fa` 用你的 deepxiv token 访问 [1stAuthor](https://1stauthor.com) 的垂域：学者、法规、裁判文书、临床试验、药品、基金、公告、标准、CVE、美国联邦公报。

```bash
deepxiv fa domains                                    # 有哪些域（免费）
deepxiv fa search talent "Geoffrey Hinton"            # 在某个域里检索
deepxiv fa read talent 15023 --level brief            # 读检索到的结果
deepxiv fa ask "自监督学习领域最有影响力的研究者有哪些" --domain talent   # 需注册 key
```

`search`、`read`、`facets`、`resolve` 任何 token 都能用，扣通用 daily limit；`fa ask` 需要注册 key。`deepxiv talent search|survey` 已是弃用别名。过滤语法、读取级别、价格、错误处理、Python 用法和迁移说明都在 [FA.zh.md](FA.zh.md)。

## 其他数据源

```bash
deepxiv trending --days 7 --limit 30       # 最近最热的论文（社交信号）
deepxiv paper 2409.05591 --popularity      # 单篇论文的浏览、推文、点赞

deepxiv pmc PMC544940 --head               # PubMed Central

deepxiv search "protein design" --biorxiv --limit 5     # bioRxiv / medRxiv
deepxiv biorxiv 10.1101/2021.02.26.433129 --format text
deepxiv medrxiv 10.1101/2020.03.24.20042937 --section Methods
```

## Agent 集成

### CLI Skill

```bash
mkdir -p $CODEX_HOME/skills
ln -s "$(pwd)/skills/deepxiv-cli" $CODEX_HOME/skills/deepxiv-cli
```

不支持原生 skill 的框架，直接把 [skills/deepxiv-cli/SKILL.md](skills/deepxiv-cli/SKILL.md) 作为操作说明加载。另有两个成型的工作流 skill：[热点摘要](skills/deepxiv-trending-digest/SKILL.md)、[baseline 表格](skills/deepxiv-baseline-table/SKILL.md)。

### 内置 Research Agent

用你自己的 LLM key 在本地跑 搜索 → 阅读 → 推理 的循环，适合需要控制模型或循环本身的场景。`pip install "deepxiv-sdk[all]"` 安装，兼容任何 OpenAI 协议的 API。Python 接口见[使用代理进行复杂分析](#使用代理进行复杂分析)。

```bash
deepxiv agent config
deepxiv agent query "What are the latest papers about agent memory?" --verbose
```

### 自己包一个 MCP Server

deepxiv 不附带 MCP server —— CLI 和 `Reader` 就是集成面，包一层大概二十行。值得抄的不是这些管道代码，而是下面的说明：只给 agent 一个裸的 `ask(query)` 工具，它会用得很糟。

```python
from mcp.server.mcpserver import MCPServer   # mcp>=2.0；1.x 里叫 FastMCP
from deepxiv_sdk import Reader, agent_search_sources

mcp = MCPServer("deepxiv")
reader = Reader()

@mcp.tool()
def ask_arxiv(query: str, effort: str = "default") -> str:
    """回答一个研究问题，引用真实的 arXiv ID。

    用于论文中的方法、数字和实验结果。时事、产品或任何非学术问题用 ask_web。

    要具体 —— "what compression ratio does KV cache eviction report on
    LongBench" 有效，"kv cache" 无效。明确索要数字（"多少加速比"、"哪个
    benchmark"）会让它去读论文正文而不是摘要。范围（年份、会议、分类、作者）
    写进 query 正文。中文直接可用。结果不对就换说法 —— 提高 effort 只增加
    阅读轮数，改变不了第一轮的召回方向。

    effort: "default"（最快）、"high"（对比多篇）、"xhigh"（综述）。
    """
    result = reader.agent_search(query, source="arxiv", effort=effort)
    answer = result["answer"]
    # `sources` 是召回集，是答案引用的超集。
    cited = [p for p in agent_search_sources(result) if p["arxiv_id"] in answer]
    lines = [answer]
    if cited:
        lines += ["\n---\n引用的论文："] + [
            f"- [{p['arxiv_id']}] {p['title']}" for p in cited
        ]
    if result["stats"]["answer_truncated"]:
        lines.append("\n⚠️ 已截断，不要当完整答案。")
    return "\n".join(lines)

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

四件事一定要写进工具描述，否则 agent 会误用结果：

1. **引用是真的** —— 服务端从不编造 ID，宁可说"没有相关论文"。告诉 agent 在汇报时保留它们。
2. **`sources` 是召回集不是引用列表** —— 像上面那样过滤到答案里出现的 ID，否则 agent 会把无关论文当证据呈上。
3. **web 后端的证据有两种强度** —— `read: true` 的页面被完整读过，其余只贡献了搜索摘要。把这个区别暴露出来，agent 才能对弱论断加限定。
4. **`answer_truncated` 意味着不完整** —— 明确说出来，否则 agent 会把截断的答案当完整的来总结。

要做 `web` 工具，把 `source="web"` 换上，加 `search_type`（`search` / `scholar` / `news` / `images`），并改成匹配 `page["url"] in answer` 而不是 `arxiv_id`。

---

# Python SDK

## Agentic Search

```python
from deepxiv_sdk import Reader

reader = Reader(token=os.environ["DEEPXIV_TOKEN"])  # agentic search 需要注册过的 key

# 阻塞式 —— 最简单，等 8~30s 拿完整答案
result = reader.agent_search("what speedup does DEER report on HumanEval")
print(result["answer"])
print(result["quota"]["remaining"], "次 agentic 调用剩余")

# web 后端
result = reader.agent_search("Claude API 定价", source="web", search_type="news")
```

流式 —— arXiv 在 `effort="default"` 下约 3–4s 出首字：

```python
from deepxiv_sdk import agent_search_sources

chunks, sources, truncated = [], [], False
for event in reader.agent_search_stream("test-time compute scaling laws"):
    name = event["event"]
    if name == "answer_delta":
        chunks.append(event["text"])
        print(event["text"], end="", flush=True)
    elif name == "sources":
        sources = agent_search_sources(event)   # 统一 papers / pages
    elif name == "done":
        truncated = event["answer_truncated"]
    elif name == "error":
        raise RuntimeError(f"{event['stage']}: {event['message']}")
answer = "".join(chunks)
```

始终下发的事件：`billing`（带 `tier` / `used` / `remaining`）、`start`、`answer_start`、`answer_delta`（`stream_answer=False` 时改为 `answer`）、`sources`、`done`。传 `verbose=True` 会追加 `tool_call`、`tool_result`、`thinking`、`warning`。`answer_delta` 只含最终答案，过程叙述走 `thinking`/`tool_call`，两者不重叠。

`sources` 事件的键随后端不同 —— arXiv 是 `papers`（`arxiv_id`/`title`/`url`），web 是 `pages`（`url`/`title`/`read`）。`agent_search_sources()` 统一这两者以及阻塞接口的 `sources`。

两个方法都接受 `source`（`"arxiv"` / `"web"`）、`effort`、`max_answer_tokens`、`language`、`timeout`（默认 180s），以及 `top_k`（arXiv）或 `search_type` / `gl` / `hl`（web）。参数在客户端先校验，避免非法调用白白花掉一次额度换一个 422。把某个后端的参数传给另一个后端会直接报错，而不是被静默丢弃。

> 与 `Reader` 的其他方法不同，这两个方法**不会自动重试** —— 每次调用消耗一次额度，重试流会重复计费并从头重新生成答案。`RateLimitError` 请自行退避处理。
>
> `error` 事件是**被 yield 出来而不是抛出**的：此时可能已经流出了部分答案，留给调用方决定怎么处理。

---

## Reader 方法

```python
reader.agent_search(query, source="arxiv"|"web")   # agentic search → 带引用的答案
reader.agent_search_stream(query, ...)             # 同上，流式 NDJSON 事件
reader.search(query, size=10, source="arxiv")      # 统一 retrieve
reader.brief(arxiv_id)                             # 标题、TLDR、关键词、引用数
reader.head(arxiv_id)                              # 元数据 + 章节概览
reader.section(arxiv_id, name)                     # 单个章节
reader.preview(arxiv_id)                           # 约 10k 字符预览
reader.raw(arxiv_id) / reader.json(arxiv_id)       # 完整 markdown / 结构化 JSON
reader.trending(days=7, limit=30)                  # 热点论文（days 1~30）
reader.fa()                                        # 1stAuthor 垂域的 FAClient（见下）
reader.social_impact(arxiv_id)                     # 热度指标
reader.pmc_head(pmc_id) / reader.pmc_json(pmc_id)  # PubMed Central
reader.biomed_search(...) / reader.biomed_data(...) # bioRxiv / medRxiv
```

### 1stAuthor 垂域（`FAClient`）

`FAClient`（或 `reader.fa()`）是 `deepxiv fa` 的 Python 接口，见 [FA.zh.md § Python](FA.zh.md#python)。

<details>
<summary><b><code>reader.search()</code> 参数</b></summary>

```python
reader.search(
    query,
    size=10,                  # 映射到上游 top_k（1~100）；也可直接传 top_k=
    offset=0,                 # 0~10000
    source="arxiv",           # "arxiv" | "biorxiv" | "medrxiv"
    categories=None,          # list[str]，只过滤
    authors=None,             # list[str]，过滤 + 影响排序
    orgs=None,                # list[str]，过滤 + 影响排序
    venue=None,               # str | list[str]；别名自动匹配
    venue_year=None,          # int
    min_citation=None,        # int
    date_search_type=None,    # "between" | "exact" | "after" | "before"
    date_str=None,            # str，或 "between" 时传 [start, end]
    date_from=None,           # 便捷参数，自动映射到上面两个
    date_to=None,
    use_fine_rerank=False,    # SDK 默认关闭（更便宜）；需要更好排序时设 True
)
```

venue 别名是基于规则匹配的，因此不一定完全准确。

</details>

---

## 高级搜索

### 语义搜索

retrieve 接口构建在 qdrant 向量检索之上，没有搜索模式或权重需要调：

```python
from deepxiv_sdk import Reader

reader = Reader()

results = reader.search("agent memory", size=20)
```

唯一的排序开关是 `use_fine_rerank`。SDK 默认关闭（更便宜）；当排序质量比延迟更重要时打开：

```python
results = reader.search("llm agents", size=20, use_fine_rerank=True)
```

> 旧的 `search_mode` / `bm25_weight` / `vector_weight` 参数已在 0.4.0 移除。
> 自 0.3.0 后端迁移起它们就是"接受但忽略"，现在传入会抛 `TypeError`。

### 高级过滤

```python
# 按类别过滤（CS 类别）
results = reader.search(
    "reinforcement learning",
    categories=["cs.AI", "cs.LG"],
    min_citation=50  # 最少 50 引用
)

# 按日期范围过滤
results = reader.search(
    "transformer",
    date_from="2024-01-01",
    date_to="2024-12-31"
)

# 按作者过滤
results = reader.search(
    "attention mechanism",
    authors=["Ashish Vaswani", "Ilya Sutskever"]
)
```

## 高效的内容加载

### 策略 1：快速预览

对于快速浏览，使用 `brief()` 获取关键信息：

```python
brief = reader.brief("2409.05591")
print(f"标题: {brief['title']}")
print(f"摘要: {brief.get('tldr')}")
print(f"关键词: {brief.get('keywords')}")
print(f"引用数: {brief.get('citations')}")
print(f"GitHub: {brief.get('github_url')}")
```

**Token 成本**: 很低（≈500 tokens）

### 策略 2：分阶段加载

获取元数据和章节摘要，然后按需加载：

```python
# 1. 获取结构
head = reader.head("2409.05591")
print("可用章节:")
for section, info in head['sections'].items():
    print(f"  {section}: {info['token_count']} tokens - {info['tldr']}")

# 2. 只加载相关章节
intro = reader.section("2409.05591", "Introduction")
methods = reader.section("2409.05591", "Methods")
```

**Token 成本**: 可控（只加载所需的）

### 策略 3：预览

快速扫描论文开头：

```python
preview = reader.preview("2409.05591")
print(preview['content'][:1000])
if preview['is_truncated']:
    print(f"... (总计: {preview['total_characters']} 字符)")
```

**Token 成本**: 低（≈2k tokens）

### 策略 4：完整内容

仅在需要时加载完整论文：

```python
full = reader.raw("2409.05591")
print(f"完整论文: {len(full)} 字符，约 {len(full) // 4} tokens")
```

**Token 成本**: 高（10k-50k+ tokens）

## 错误处理和重试

### 捕获特定错误

```python
from deepxiv_sdk import (
    Reader,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    APIError
)

reader = Reader(token="your_token")

try:
    paper = reader.head("2409.05591")
except AuthenticationError:
    print("❌ Token 无效。运行 'deepxiv config' 更新")
except RateLimitError:
    print("⚠️  已达到日限额。明天再试")
except NotFoundError:
    print("❌ 论文未找到。检查 arXiv ID")
except APIError as e:
    print(f"❌ API 错误: {e}")
```

对 `agent_search` / `agent_search_stream` 来说，其中两个异常的含义不同：

```python
try:
    result = reader.agent_search("...", source="web")
except AuthenticationError:
    # 401（token 无效），或 403 —— 有效的 SDK token 但没有 agentic 权限。
    # Agentic search 需要注册 key，见 README。
    ...
except RateLimitError:
    # agentic 额度用尽。它与通用 daily limit 是两个独立的池子，
    # 所以其他 Reader 调用仍然可用。这两个方法从不自动重试，请自行退避。
    ...
```

### 自定义重试策略

```python
reader = Reader(
    token="your_token",
    timeout=120,      # 增加超时时间
    max_retries=5,    # 增加重试次数
    retry_delay=1.0   # 初始重试延迟（秒）
)
```

Reader 会自动使用指数退避重试：
- 第 1 次重试: 1 秒
- 第 2 次重试: 2 秒
- 第 3 次重试: 4 秒
- ...

## 批量处理

### 处理多篇论文

```python
arxiv_ids = ["2409.05591", "2504.21776", "2503.04975"]

papers = {}
for arxiv_id in arxiv_ids:
    try:
        papers[arxiv_id] = reader.brief(arxiv_id)
    except Exception as e:
        print(f"获取 {arxiv_id} 失败: {e}")

# 处理获取的论文
for arxiv_id, paper in papers.items():
    print(f"{paper['title']} ({paper['citations']} 引用)")
```

### 搜索分页

```python
# 获取前 500 个结果
all_results = []
for offset in range(0, 500, 100):
    results = reader.search(
        "agent memory",
        size=100,
        offset=offset
    )
    all_results.extend(results['results'])

print(f"总共获取论文数: {len(all_results)}")
```

## 使用代理进行复杂分析

### 基础查询

```python
from deepxiv_sdk import Agent

agent = Agent(
    api_key="your_openai_key",
    model="gpt-4"
)

answer = agent.query("最近 transformer 论文的关键创新有哪些？")
print(answer)
```

### 多轮对话

```python
# 首次查询
answer1 = agent.query("总结 MemGPT 论文")
print(answer1)

# 后续查询会使用前面加载的论文
answer2 = agent.query("比较 MemGPT 和其他长上下文方法")
print(answer2)

# 查看当前加载的论文
loaded = agent.get_loaded_papers()
print(f"已加载论文: {list(loaded.keys())}")

# 重置论文上下文开始新对话
agent.reset_papers()
```

### 手动加载论文

```python
# 预加载特定论文
agent.add_paper("2409.05591")
agent.add_paper("2504.21776")

# 然后查询
answer = agent.query("比较这两篇论文")
```

### 使用不同的 LLM

```python
# DeepSeek
agent = Agent(
    api_key="your_deepseek_key",
    base_url="https://api.deepseek.com/v1",
    model="deepseek-chat"
)

# OpenRouter
agent = Agent(
    api_key="your_openrouter_key",
    base_url="https://openrouter.ai/api/v1",
    model="openai/gpt-4"
)

# 本地 Ollama
agent = Agent(
    api_key="ollama",  # dummy key
    base_url="http://localhost:11434/v1",
    model="llama2"
)
```

## 最佳实践

### 1. 使用适当的加载策略

```python
# ❌ 坏的做法：总是加载完整论文
for arxiv_id in search_results:
    content = reader.raw(arxiv_id)  # 浪费 token！

# ✅ 好的做法：分阶段加载
for arxiv_id in search_results:
    brief = reader.brief(arxiv_id)  # 快速过滤
    if is_relevant(brief):
        content = reader.raw(arxiv_id)  # 只加载相关的
```

### 2. 缓存结果

```python
import json
from pathlib import Path

cache_file = Path("paper_cache.json")
cache = json.loads(cache_file.read_text()) if cache_file.exists() else {}

def get_paper_cached(arxiv_id):
    if arxiv_id in cache:
        return cache[arxiv_id]

    paper = reader.head(arxiv_id)
    cache[arxiv_id] = paper
    cache_file.write_text(json.dumps(cache))
    return paper
```

### 3. 处理大型搜索结果

```python
# 流式处理搜索结果，而不是一次性加载全部
def search_and_process(query, callback):
    offset = 0
    while True:
        results = reader.search(query, size=100, offset=offset)
        if not results['results']:
            break

        for paper in results['results']:
            callback(paper)  # 处理每篇论文

        offset += 100

search_and_process("reinforcement learning", process_paper_func)
```

### 4. 记录日志

```python
import logging

# 启用 deepxiv 日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('deepxiv_sdk')
logger.setLevel(logging.DEBUG)

# 现在会看到 deepxiv 的调试信息
reader = Reader()
results = reader.search("agent")  # 会输出日志
```

## 故障排查

### CLI

- **`ask` 返回 403？** 你用的是自动注册的 token。agentic search 需要注册过的 key —— 见 [Token 与额度](#token-与额度)。
- **`ask` 起步慢？** 只有 `--effort default` 以 5 秒内首 token 为目标，`high`/`xhigh` 是刻意多检索。
- **`ask` 答非所问？** 换个更具体的说法，而不是提高 `--effort` —— effort 只增加阅读轮数，改变不了第一轮的召回方向。
- **`ask` 列出了和答案无关的论文？** 那是召回集不是引用列表，`--all-sources` 会完整显示。
- **检索返回 0 条？** 松开过滤条件 —— 日期和引用数叠加会很快过窄。
- **`deepxiv fa` 的问题？** 见 [FA.zh.md § 常见问题](FA.zh.md#常见问题)。
- **Agent 报 `Reasoning content is only supported as the last assistant message`？** 推理模型做多轮工具调用需要关掉 thinking：`deepxiv agent query "…" --disable-thinking`，或 `Agent(..., enable_thinking=False)`。
- **`agent.add_paper()` 加不进新论文？** 论文还没入库时返回 `False` —— 1–3 天内的论文经常还没有。


### 问题：Token 过期

**症状**: `AuthenticationError: Invalid or expired token`

**解决方案**:
```bash
deepxiv config --token YOUR_NEW_TOKEN
```

### 问题：速率限制

**症状**: `RateLimitError: Daily limit reached`

**解决方案**:
- 等到明天（每天重置）
- 或联系 tommy@chien.io 申请更高限额

### 问题：网络超时

**症状**: `APIError: Request timed out after 3 retries`

**解决方案**:
```python
# 增加超时时间和重试次数
reader = Reader(timeout=180, max_retries=5)
```

### 问题：论文未找到

**症状**: `NotFoundError: Paper not found`

**解决方案**:
- 检查 arXiv ID 格式（应为如 `2409.05591`）
- 访问 https://arxiv.org 验证论文是否存在

### 问题：搜索结果为空

**症状**: `No papers found matching 'query'`

**解决方案**:
- 尝试不同的关键词
- 移除过多的过滤条件
- 检查分类代码是否正确

## 环境变量配置

控制 deepxiv 行为的环境变量：

```bash
# API Token
export DEEPXIV_TOKEN="your_token"

# LLM API 密钥（用于代理）
export DEEPXIV_AGENT_API_KEY="your_api_key"
export DEEPXIV_AGENT_BASE_URL="https://api.example.com"
export DEEPXIV_AGENT_MODEL="gpt-4"

# 启用调试日志
export DEEPXIV_DEBUG=1
```

## 性能优化

### 跳过精排

```python
# 默认：精排关闭 —— 最快、最省
results = reader.search("agents")

# 排序更好，但上游延迟更高
results = reader.search("agents", use_fine_rerank=True)
```

### 限制搜索范围

```python
# 更快的搜索
results = reader.search(
    "transformers",
    size=10,                           # 只要前 10 个
    categories=["cs.CL", "cs.AI"],     # 限制类别
    date_from="2024-01-01"             # 只要最近的论文
)
```

---

有任何问题或建议？[在 GitHub 上提交 issue](https://github.com/qhjqhj00/deepxiv_sdk/issues)
