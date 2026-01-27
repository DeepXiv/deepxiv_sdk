# py1stauthor

一个用于访问 arXiv 论文并使用 ReAct 框架进行智能交互的 Python 包。

**🎮 在线演示：** [https://1stauthor.com/](https://1stauthor.com/)

**📚 API 文档：** [https://data.rag.ac.cn/api/docs](https://data.rag.ac.cn/api/docs)

[English Documentation](README.md)

## 功能特性

- 🔍 **论文搜索**：使用自然语言查询搜索 arXiv 论文
- 📄 **论文访问**：获取论文元数据、章节和完整内容
- 🤖 **智能代理**：基于 ReAct 的智能论文分析代理
- 🔌 **灵活的 LLM 支持**：兼容 OpenAI、DeepSeek、OpenRouter 和其他 OpenAI 兼容 API
- 💬 **流式支持**：实时流式输出 LLM 响应
- 📊 **过程日志**：详细记录推理和工具调用过程

## 安装

### 前置要求

安装前，您需要从 arXiv 数据服务获取 API token：

1. **获取 API Token**：访问 [https://data.rag.ac.cn/register](https://data.rag.ac.cn/register) 注册并获取免费 API token
2. **每日限额**：每个 token 包含 1000 次免费日请求
3. **测试论文**：论文 `2409.05591` 和 `2504.21776` 可以无需认证进行测试

### 仅 API 功能（轻量级）

仅安装基础的论文访问功能：

```bash
pip install py1stauthor
```

### 完整安装（包含智能代理）

安装包括智能代理在内的完整功能：

```bash
pip install py1stauthor[all]
```

或从源码安装：

```bash
git clone https://github.com/qhjqhj00/py1stauthor.git
cd py1stauthor
pip install -e .[all]
```

## 快速开始

### 使用 Reader（API 访问）

Reader 类提供对 [Agentic Data Interface API](https://data.rag.ac.cn/api/docs) 的直接访问。

**注意：** 论文 `2409.05591` 和 `2504.21776` 可以无需认证进行测试。

```python
from py1stauthor import Reader

# 使用你的 API token 初始化 reader
# 在此获取 token：https://data.rag.ac.cn/register
reader = Reader(token="your_api_token")

# 或者对于免费论文（2409.05591、2504.21776），可以无需 token 初始化
# reader = Reader()

# 使用高级选项搜索论文
results = reader.search(
    query="agent memory",
    size=10,
    search_mode="hybrid",  # 选项："bm25"、"vector"、"hybrid"
    categories=["cs.AI", "cs.CL"]
)
for paper in results['results']:
    print(f"{paper['title']} - {paper['arxiv_id']}")

# 获取论文元数据和结构
head_info = reader.head("2409.05591")
print(f"标题: {head_info['title']}")
print(f"摘要: {head_info['abstract']}")
print(f"章节: {head_info['sections']}")

# 读取特定章节
section_content = reader.section("2409.05591", "Introduction")
print(section_content)

# 获取 markdown 格式的完整论文内容
full_content = reader.raw("2409.05591")

# 获取预览（前 10,000 字符）
preview = reader.preview("2409.05591")
print(f"预览: {preview['preview']}")
print(f"已截断: {preview['is_truncated']}")

# 获取完整 JSON 结构
full_json = reader.json("2409.05591")

# 获取 HTML 视图 URL
html_url = reader.markdown("2409.05591")
print(f"在浏览器中查看: {html_url}")
```

### 使用 Agent（智能分析）

```python
import os
from py1stauthor import Reader, Agent

# 初始化 reader
reader = Reader(token="your_api_token")

# 使用 OpenAI 初始化 agent
agent = Agent(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4",
    reader=reader,
    print_process=True,  # 显示推理过程
    stream=True  # 流式输出 LLM 响应
)

# 查询 agent
answer = agent.query("关于 agent memory 的最新论文有哪些？")
print(answer)

# 使用之前论文的上下文继续查询
answer = agent.query("这些方法如何比较？")
print(answer)

# 重置论文以开始新话题
agent.reset_papers()
answer = agent.query("解释 transformer 注意力机制")
print(answer)
```

### 使用 DeepSeek 或其他提供商

```python
# DeepSeek
agent = Agent(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    model="deepseek-chat",
    base_url="https://api.deepseek.com",
    reader=reader
)

# OpenRouter
agent = Agent(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="anthropic/claude-3-opus",
    base_url="https://openrouter.ai/api/v1",
    reader=reader
)

# 任何兼容 OpenAI 的 API
agent = Agent(
    api_key="your_api_key",
    model="model-name",
    base_url="https://your-api-endpoint.com/v1",
    reader=reader
)
```

## API 参考

### Reader

`Reader` 类提供对 arXiv 数据服务 API 的直接访问。

**API 文档：** [https://data.rag.ac.cn/api/docs](https://data.rag.ac.cn/api/docs)

**获取 API Token：** [https://data.rag.ac.cn/register](https://data.rag.ac.cn/register)（每天 1000 次免费请求）

#### 方法

- `search(query, size=10, offset=0, search_mode="hybrid", ...)`: 使用 Elasticsearch 混合搜索（BM25 + 向量）查找论文
  - `query`: 搜索查询字符串
  - `size`: 返回结果数量（默认：10）
  - `offset`: 分页偏移量（默认：0）
  - `search_mode`: "bm25"、"vector" 或 "hybrid"（默认："hybrid"）
  - `bm25_weight`、`vector_weight`: 混合搜索权重（默认各 0.5）
  - `categories`: 按 arXiv 分类过滤（例如：["cs.AI", "cs.CL"]）
  - `authors`: 按作者过滤
  - `min_citation`: 最小引用数
  - `date_from`、`date_to`: 发表日期范围（YYYY-MM-DD）
- `head(arxiv_id)`: 获取论文元数据和结构（标题、摘要、作者、章节、token 数、分类、发表日期）
- `section(arxiv_id, section_name)`: 获取特定章节内容
- `raw(arxiv_id)`: 获取 markdown 格式的完整论文内容
- `preview(arxiv_id)`: 获取论文预览（前 10,000 字符）
- `json(arxiv_id)`: 获取包含所有章节和元数据的完整结构化 JSON
- `markdown(arxiv_id)`: 获取精美渲染的 HTML 页面 URL

### Agent

`Agent` 类实现了基于 ReAct 的智能论文分析代理。

#### 初始化参数

- `api_key` (str): LLM 提供商的 API 密钥
- `reader` (Reader): Reader 实例用于 API 访问
- `model` (str): 模型名称（默认："gpt-4"）
- `base_url` (str, 可选): OpenAI 兼容 API 的基础 URL
- `max_llm_calls` (int): 每次查询的最大 LLM 调用次数（默认：20）
- `max_time_seconds` (int): 每次查询的最大时间（默认：600）
- `max_tokens` (int): 每次调用的最大 token 数（默认：4096）
- `temperature` (float): 采样温度（默认：0.7）
- `print_process` (bool): 打印推理过程（默认：False）
- `stream` (bool): 流式输出 LLM 响应（默认：False）

#### 方法

- `query(question, reset_papers=False)`: 向 agent 提问
- `get_loaded_papers()`: 获取已加载论文的信息
- `reset_papers()`: 重置所有已加载的论文
- `add_paper(arxiv_id)`: 手动添加论文到上下文

## Agent 工具

Agent 可以访问以下工具：

1. **search_papers**: 使用 Elasticsearch 混合搜索（BM25 + 向量）搜索论文
   - 支持多种搜索模式：BM25（关键词）、Vector（语义）、Hybrid（混合）
   - 按分类、作者、引用数和发表日期高级过滤
   - 混合搜索可自定义权重
   - 支持大结果集分页
2. **load_paper**: 加载论文的元数据和结构（读取章节前必须调用）
3. **read_section**: 从已加载的论文中读取特定章节
4. **get_full_paper**: 获取 markdown 格式的完整论文内容
5. **get_paper_preview**: 获取有限 token 的预览，快速了解论文概要

Agent 使用 ReAct（推理 + 行动）模式：
1. 思考需要什么信息
2. 使用工具收集信息
3. 观察结果
4. 重复直到收集到足够的信息
5. 提供全面的答案

## Streamlit 网页界面

试试交互式网页界面，实时可视化 Agent 的推理过程！

### 快速开始

```bash
# 安装 Streamlit
pip install streamlit

# 运行简单版本（推荐用于演示）
streamlit run simple_app.py

# 或运行完整版本（完整的聊天界面）
streamlit run streamlit_app.py

# 或使用启动脚本
./run_app.sh  # Linux/Mac
run_app.bat   # Windows
```

### 功能特点

- ✅ **实时输出**：实时查看 Agent 的思考过程
- ✅ **交互式对话**：支持多轮对话和上下文
- ✅ **配置界面**：简单的 API token 和模型选择
- ✅ **论文追踪**：查看所有已加载的论文及其元数据
- ✅ **过程可视化**：可折叠的推理步骤视图

详细文档请参见 [STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md)。

## 示例

查看 [examples](examples/) 目录获取更详细的使用示例：

- `example_reader.py`: 基础 Reader 使用
- `example_agent.py`: 不同场景下的 Agent 使用
- `example_advanced.py`: 高级 Agent 使用模式

## 开发

### 运行测试

```bash
pytest tests/
```

### 构建包

```bash
python setup.py sdist bdist_wheel
```

## 依赖要求

### 基础（仅 API）
- Python >= 3.8
- requests >= 2.31.0

### Agent 功能
- openai >= 1.0.0
- langgraph >= 0.0.20
- langchain-core >= 0.1.0

## 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎贡献！请随时提交 Pull Request。

## 支持

问题和疑问：
- 🐛 **GitHub Issues**：[https://github.com/qhjqhj00/py1stauthor/issues](https://github.com/qhjqhj00/py1stauthor/issues)
- 📚 **API 文档**：[https://data.rag.ac.cn/api/docs](https://data.rag.ac.cn/api/docs)
- 🎮 **演示**：[https://1stauthor.com/](https://1stauthor.com/)

如需更高的 API 访问限额或定制需求，请通过注册页面联系服务提供商。

## 获取帮助

- 🎮 **在线演示**：[https://1stauthor.com/](https://1stauthor.com/)
- 📚 **API 文档**：[https://data.rag.ac.cn/api/docs](https://data.rag.ac.cn/api/docs)
- 🔑 **获取 API Token**：[https://data.rag.ac.cn/register](https://data.rag.ac.cn/register)
- 🐛 **GitHub Issues**：[https://github.com/qhjqhj00/py1stauthor/issues](https://github.com/qhjqhj00/py1stauthor/issues)
- 📖 **文档**：[README_CN.md](README_CN.md)

## 引用

如果您在研究中使用此包，请引用：

```bibtex
@software{py1stauthor2024,
  title = {py1stauthor: A Python Package for arXiv Paper Access and Intelligent Agent Interaction},
  author = {Hongjin Qian},
  year = {2024},
  url = {https://github.com/qhjqhj00/py1stauthor}
}
```

## 致谢

本包使用由 [1stAuthor](https://1stauthor.com/) 提供的 arXiv 数据服务 API。该服务提供：
- 🎁 每天 1000 次免费 API 请求
- 🚀 Redis 缓存快速访问
- 📦 多种论文格式（元数据、章节、完整内容）
- 🔍 内置语义搜索

API 文档和注册：
- API 文档：[https://data.rag.ac.cn/api/docs](https://data.rag.ac.cn/api/docs)
- 注册：[https://data.rag.ac.cn/register](https://data.rag.ac.cn/register)
