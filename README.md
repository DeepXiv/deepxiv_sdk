# py1stauthor

A Python package for accessing arXiv papers and intelligent agent interaction using the ReAct framework.

**🎮 Try the live demo:** [https://1stauthor.com/](https://1stauthor.com/)

**📚 API Documentation:** [https://data.rag.ac.cn/api/docs](https://data.rag.ac.cn/api/docs)

[中文文档](README_CN.md)

## Features

- 🔍 **Paper Search**: Search for arXiv papers using natural language queries
- 📄 **Paper Access**: Retrieve paper metadata, sections, and full content
- 🤖 **Intelligent Agent**: ReAct-based agent for intelligent paper analysis
- 🔌 **Flexible LLM Support**: Compatible with OpenAI, DeepSeek, OpenRouter, and other OpenAI-compatible APIs
- 💬 **Streaming Support**: Real-time streaming of LLM responses
- 📊 **Process Logging**: Detailed logging of reasoning and tool calls

## Installation

### Prerequisites

Before installation, you need to get an API token from the arXiv data service:

1. **Get API Token**: Visit [https://data.rag.ac.cn/register](https://data.rag.ac.cn/register) to register and get your free API token
2. **Daily Limit**: Each token includes 1000 free daily requests
3. **Test Papers**: Papers `2409.05591` and `2504.21776` are available for testing without authentication

### API Only (Lightweight)

For basic paper access functionality only:

```bash
pip install py1stauthor
```

### Full Installation (with Agent)

For complete functionality including the intelligent agent:

```bash
pip install py1stauthor[all]
```

Or install from source:

```bash
git clone https://github.com/qhjqhj00/py1stauthor.git
cd py1stauthor
pip install -e .[all]
```

## Quick Start

### Using the Reader (API Access)

The Reader class provides direct access to the [Agentic Data Interface API](https://data.rag.ac.cn/api/docs).

**Note:** Papers `2409.05591` and `2504.21776` are available for testing without authentication.

```python
from py1stauthor import Reader

# Initialize the reader with your API token
# Get your token at: https://data.rag.ac.cn/register
reader = Reader(token="your_api_token")

# Or initialize without token for free papers (2409.05591, 2504.21776)
# reader = Reader()

# Search for papers with advanced options
results = reader.search(
    query="agent memory",
    size=10,
    search_mode="hybrid",  # Options: "bm25", "vector", "hybrid"
    categories=["cs.AI", "cs.CL"]
)
for paper in results['results']:
    print(f"{paper['title']} - {paper['arxiv_id']}")

# Get paper metadata and structure
head_info = reader.head("2409.05591")
print(f"Title: {head_info['title']}")
print(f"Abstract: {head_info['abstract']}")
print(f"Sections: {head_info['sections']}")

# Read a specific section
section_content = reader.section("2409.05591", "Introduction")
print(section_content)

# Get full paper content in markdown
full_content = reader.raw("2409.05591")

# Get a preview (first 10,000 characters)
preview = reader.preview("2409.05591")
print(f"Preview: {preview['preview']}")
print(f"Truncated: {preview['is_truncated']}")

# Get complete JSON structure
full_json = reader.json("2409.05591")

# Get URL for HTML view
html_url = reader.markdown("2409.05591")
print(f"View in browser: {html_url}")
```

### Using the Agent (Intelligent Analysis)

```python
import os
from py1stauthor import Reader, Agent

# Initialize reader
reader = Reader(token="your_api_token")

# Initialize agent with OpenAI
agent = Agent(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4",
    reader=reader,
    print_process=True,  # Show reasoning process
    stream=True  # Stream LLM responses
)

# Query the agent
answer = agent.query("What are the latest papers about agent memory?")
print(answer)

# Query with context from previous papers
answer = agent.query("How do these approaches compare?")
print(answer)

# Reset papers for a new topic
agent.reset_papers()
answer = agent.query("Explain transformer attention mechanisms")
print(answer)
```

### Using with DeepSeek or Other Providers

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

# Any OpenAI-compatible API
agent = Agent(
    api_key="your_api_key",
    model="model-name",
    base_url="https://your-api-endpoint.com/v1",
    reader=reader
)
```

## API Reference

### Reader

The `Reader` class provides direct access to the arXiv data service API.

**API Documentation:** [https://data.rag.ac.cn/api/docs](https://data.rag.ac.cn/api/docs)

**Get API Token:** [https://data.rag.ac.cn/register](https://data.rag.ac.cn/register) (1000 free requests/day)

#### Methods

- `search(query, size=10, offset=0, search_mode="hybrid", ...)`: Search for papers using Elasticsearch hybrid search (BM25 + Vector)
  - `query`: Search query string
  - `size`: Number of results (default: 10)
  - `offset`: Pagination offset (default: 0)
  - `search_mode`: "bm25", "vector", or "hybrid" (default: "hybrid")
  - `bm25_weight`, `vector_weight`: Weights for hybrid search (default: 0.5 each)
  - `categories`: Filter by arXiv categories (e.g., ["cs.AI", "cs.CL"])
  - `authors`: Filter by authors
  - `min_citation`: Minimum citation count
  - `date_from`, `date_to`: Publication date range (YYYY-MM-DD)
- `head(arxiv_id)`: Get paper metadata and structure (title, abstract, authors, sections, token_count, categories, publish_at)
- `section(arxiv_id, section_name)`: Get a specific section content
- `raw(arxiv_id)`: Get full paper content in markdown
- `preview(arxiv_id)`: Get a preview of the paper (first 10,000 characters)
- `json(arxiv_id)`: Get complete structured JSON with all sections and metadata
- `markdown(arxiv_id)`: Get URL for beautifully rendered HTML page

### Agent

The `Agent` class implements a ReAct-based intelligent agent for paper analysis.

#### Initialization Parameters

- `api_key` (str): API key for the LLM provider
- `reader` (Reader): Reader instance for API access
- `model` (str): Model name (default: "gpt-4")
- `base_url` (str, optional): Base URL for OpenAI-compatible APIs
- `max_llm_calls` (int): Maximum LLM calls per query (default: 20)
- `max_time_seconds` (int): Maximum time per query (default: 600)
- `max_tokens` (int): Maximum tokens per call (default: 4096)
- `temperature` (float): Sampling temperature (default: 0.7)
- `print_process` (bool): Print reasoning process (default: False)
- `stream` (bool): Stream LLM responses (default: False)

#### Methods

- `query(question, reset_papers=False)`: Query the agent with a question
- `get_loaded_papers()`: Get information about loaded papers
- `reset_papers()`: Reset all loaded papers
- `add_paper(arxiv_id)`: Manually add a paper to context

## Agent Tools

The agent has access to the following tools:

1. **search_papers**: Search for papers using Elasticsearch hybrid search (BM25 + Vector)
   - Supports multiple search modes: BM25 (keyword), Vector (semantic), Hybrid (combined)
   - Advanced filtering by categories, authors, citation count, and publication dates
   - Customizable weights for hybrid search
   - Pagination support for large result sets
2. **load_paper**: Load a paper's metadata and structure (must be called before reading sections)
3. **read_section**: Read a specific section from a loaded paper
4. **get_full_paper**: Get the complete paper content in markdown format
5. **get_paper_preview**: Get a preview with limited tokens for quick overview

The agent uses the ReAct (Reasoning + Acting) pattern to:
1. Think about what information is needed
2. Use tools to gather information
3. Observe the results
4. Repeat until sufficient information is gathered
5. Provide a comprehensive answer

## Streamlit Web Interface

Try the interactive web interface to visualize the agent's reasoning process in real-time!

### Quick Start

```bash
# Install Streamlit
pip install streamlit

# Run the simple version (recommended for demos)
streamlit run simple_app.py

# Or run the full version (complete chat interface)
streamlit run streamlit_app.py

# Or use the launcher script
./run_app.sh  # Linux/Mac
run_app.bat   # Windows
```

### Features

- ✅ **Real-time Output**: See the agent's thinking process as it happens
- ✅ **Interactive Chat**: Multi-turn conversations with context
- ✅ **Configuration UI**: Easy API token and model selection
- ✅ **Paper Tracking**: View all loaded papers and their metadata
- ✅ **Process Visualization**: Collapsible view of reasoning steps

See [STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md) for detailed documentation.

## Examples

See the [examples](examples/) directory for more detailed usage examples:

- `example_reader.py`: Basic Reader usage
- `example_agent.py`: Agent usage with different scenarios
- `example_advanced.py`: Advanced agent usage patterns

## Development

### Running Tests

```bash
pytest tests/
```

### Building the Package

```bash
python setup.py sdist bdist_wheel
```

## Requirements

### Base (API Only)
- Python >= 3.8
- requests >= 2.31.0

### Agent Functionality
- openai >= 1.0.0
- langgraph >= 0.0.20
- langchain-core >= 0.1.0

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions:
- 🐛 **GitHub Issues**: [https://github.com/qhjqhj00/py1stauthor/issues](https://github.com/qhjqhj00/py1stauthor/issues)
- 📚 **API Documentation**: [https://data.rag.ac.cn/api/docs](https://data.rag.ac.cn/api/docs)
- 🎮 **Demo**: [https://1stauthor.com/](https://1stauthor.com/)

For higher API rate limits or custom needs, contact the service provider through the registration page.

## Getting Help

- 🎮 **Live Demo**: [https://1stauthor.com/](https://1stauthor.com/)
- 📚 **API Documentation**: [https://data.rag.ac.cn/api/docs](https://data.rag.ac.cn/api/docs)
- 🔑 **Get API Token**: [https://data.rag.ac.cn/register](https://data.rag.ac.cn/register)
- 🐛 **GitHub Issues**: [https://github.com/qhjqhj00/py1stauthor/issues](https://github.com/qhjqhj00/py1stauthor/issues)
- 📖 **Documentation**: [README.md](README.md)

## Citation

If you use this package in your research, please cite:

```bibtex
@software{py1stauthor2026,
  title = {py1stauthor: A Python Package for arXiv Paper Access and Intelligent Agent Interaction},
  author = {Hongjin Qian},
  year = {2026},
  url = {https://github.com/qhjqhj00/py1stauthor}
}
```

## Acknowledgments

This package uses the arXiv data service API provided by [1stAuthor](https://1stauthor.com/). The service offers:
- 🎁 1000 free API requests per day
- 🚀 Redis-cached fast access
- 📦 Multiple paper formats (metadata, sections, full content)
- 🔍 Built-in semantic search

For API documentation and registration, visit:
- API Docs: [https://data.rag.ac.cn/api/docs](https://data.rag.ac.cn/api/docs)
- Register: [https://data.rag.ac.cn/register](https://data.rag.ac.cn/register)
