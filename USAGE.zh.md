# 高级使用指南

本指南涵盖了高级场景、最佳实践和故障排查。基础使用请参考 [README.zh.md](README.zh.md)。

> **English Version**: [USAGE.md](USAGE.md)

## 高级搜索

### 使用混合搜索（默认）

混合搜索结合 BM25 和向量搜索，提供最好的结果：

```python
from deepxiv_sdk import Reader

reader = Reader()

# 混合搜索（默认）
results = reader.search(
    "agent memory",
    size=20,
    search_mode="hybrid",
    bm25_weight=0.5,
    vector_weight=0.5
)
```

调整权重以偏好关键词匹配或语义相似性：

```python
# 偏好关键词匹配
results = reader.search("llm agents", bm25_weight=0.8, vector_weight=0.2)

# 偏好语义相似性
results = reader.search("llm agents", bm25_weight=0.2, vector_weight=0.8)
```

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
```

**Token 成本**: 很低（~500 tokens）

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

**Token 成本**: 低（~2k tokens）

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

### 选择合适的搜索模式

```python
# 快速但可能不够精准
results = reader.search("agents", search_mode="bm25")

# 慢但更语义相关
results = reader.search("agents", search_mode="vector")

# 折中方案（默认）
results = reader.search("agents", search_mode="hybrid")
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
