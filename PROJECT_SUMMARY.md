# py1stauthor Package - Complete Summary

## 📦 Package Overview

**py1stauthor** is a Python package for accessing arXiv papers and enabling intelligent agent interaction using the ReAct framework.

- **Author**: Hongjin Qian (@qhjqhj00)
- **License**: MIT
- **Version**: 0.1.0
- **Repository**: https://github.com/qhjqhj00/py1stauthor

## 🌐 Related Resources

- 🎮 **Live Demo**: https://1stauthor.com/
- 📚 **API Documentation**: https://data.rag.ac.cn/api/docs
- 🔑 **Register for API Token**: https://data.rag.ac.cn/register (1000 free requests/day)
- 🐛 **GitHub Issues**: https://github.com/qhjqhj00/py1stauthor/issues

## 📁 Package Structure

```
py1stauthor/
├── py1stauthor/              # Main package
│   ├── __init__.py           # Package exports: Reader, Agent
│   ├── reader.py             # Reader class for API access
│   └── agent/                # Agent module (ReAct framework)
│       ├── __init__.py       # Agent module exports
│       ├── agent.py          # Main Agent class
│       ├── state.py          # State definitions (TypedDict)
│       ├── tools.py          # Tool definitions and executor
│       ├── prompts.py        # System prompts
│       └── graph.py          # LangGraph workflow
├── examples/                 # Example scripts
│   ├── quickstart.py         # Quick start example
│   ├── example_reader.py     # Reader usage examples
│   ├── example_agent.py      # Basic agent examples
│   ├── example_advanced.py   # Advanced agent patterns
│   └── README.md             # Examples documentation
├── setup.py                  # Setup script (backward compatibility)
├── pyproject.toml            # Modern Python packaging config
├── requirements.txt          # Base dependencies (API only)
├── requirements-full.txt     # Full dependencies (with agent)
├── README.md                 # English documentation
├── README_CN.md              # Chinese documentation
├── INSTALL.md                # Installation guide
├── CHANGELOG.md              # Version history
├── CONTRIBUTING.md           # Contribution guidelines
├── PACKAGE_STRUCTURE.md      # Detailed structure docs
├── QUICKREF.md               # Quick reference card
├── LICENSE                   # MIT License
├── MANIFEST.in               # Distribution includes
├── .gitignore               # Git ignore patterns
└── test_package.py          # Package test script
```

## 🚀 Key Features

### Reader Class
- Direct access to arXiv data service API
- Semantic search across papers
- Get paper metadata with section TLDRs
- Read specific sections
- Get full paper content in markdown
- Preview papers (first 10,000 characters)
- 1000 free API requests per day

### Agent Class
- ReAct-based intelligent paper analysis
- LangGraph workflow orchestration
- Support for OpenAI, DeepSeek, OpenRouter, and other OpenAI-compatible APIs
- Streaming responses
- Process logging with detailed reasoning traces
- Context persistence across queries
- Automatic tool selection

### Available Tools
1. `search_papers` - Semantic search for papers
2. `load_paper` - Load paper metadata and structure
3. `read_section` - Read specific paper sections
4. `get_full_paper` - Get complete paper content
5. `get_paper_preview` - Get limited preview

## 📥 Installation Options

### Option 1: API Only (Lightweight)
```bash
pip install py1stauthor
```
**Dependencies**: `requests>=2.31.0`

### Option 2: Full Installation (Recommended)
```bash
pip install py1stauthor[all]
```
**Dependencies**: `requests`, `openai`, `langgraph`, `langchain-core`

### Option 3: Development
```bash
git clone https://github.com/qhjqhj00/py1stauthor.git
cd py1stauthor
pip install -e .[all]
```

## 🔑 API Token Setup

1. Visit: https://data.rag.ac.cn/register
2. Register with phone number
3. Get API token (1000 free requests/day)
4. Set environment variable:
   ```bash
   export ARXIV_API_TOKEN="your_token"
   ```

**Test Papers** (no token required):
- `2409.05591`
- `2504.21776`

**Free Search Queries** (no token required):
- "transformer"
- "attention mechanism"
- "large language model"

## 💻 Basic Usage

### Reader Example
```python
from py1stauthor import Reader

reader = Reader(token="your_token")

# Search
results = reader.search("agent memory", top_k=10)

# Get paper info
head = reader.head("2409.05591")

# Read section
section = reader.section("2409.05591", "Introduction")

# Get full paper
full = reader.raw("2409.05591")
```

### Agent Example
```python
from py1stauthor import Agent

agent = Agent(
    api_key="your_llm_key",
    model="gpt-4",
    reader=reader,
    print_process=True,  # Show reasoning
    stream=True          # Stream responses
)

answer = agent.query("What are the latest papers about transformers?")
```

### Using Different LLM Providers

**OpenAI:**
```python
agent = Agent(api_key=openai_key, model="gpt-4", reader=reader)
```

**DeepSeek:**
```python
agent = Agent(
    api_key=deepseek_key, 
    model="deepseek-chat",
    base_url="https://api.deepseek.com",
    reader=reader
)
```

**OpenRouter:**
```python
agent = Agent(
    api_key=openrouter_key,
    model="anthropic/claude-3-opus",
    base_url="https://openrouter.ai/api/v1",
    reader=reader
)
```

## 📚 Documentation Files

- **README.md** - Main English documentation with full API reference
- **README_CN.md** - Chinese documentation (中文文档)
- **INSTALL.md** - Detailed installation instructions
- **QUICKREF.md** - Quick reference card
- **PACKAGE_STRUCTURE.md** - Detailed package structure
- **CHANGELOG.md** - Version history and changes
- **CONTRIBUTING.md** - Contribution guidelines
- **examples/README.md** - Examples documentation

## 🧪 Testing

Run the package test:
```bash
python test_package.py
```

Expected output:
- ✓ Reader imported successfully
- ✓ Reader initialized successfully
- ⚠ Agent available only with full installation
- ✓ Package metadata correct

## 📦 Building and Distribution

### Build the package:
```bash
python setup.py sdist bdist_wheel
```

### Publish to PyPI:
```bash
twine upload dist/*
```

## 🎯 Use Cases

1. **Literature Review** - Survey papers by talking to them
2. **Research Assistant** - AI agents that consult paper experts
3. **Academic Learning** - Ask papers questions like talking to authors
4. **Knowledge Synthesis** - Connect insights across multiple papers
5. **Methodology Comparison** - Compare approaches across papers
6. **Trend Analysis** - Analyze research trends
7. **Related Work Finding** - Discover related research

## 🔧 Technical Details

- **Python Version**: 3.8+
- **Type Hints**: Full type annotations
- **Architecture**: Modular design with clear separation
- **Workflow**: LangGraph for agent orchestration
- **LLM Integration**: OpenAI SDK for LLM interactions
- **Error Handling**: Robust retry logic and error messages
- **Caching**: Redis-cached API for fast access

## 📝 API Rate Limits

- **Daily Limit**: 1000 requests per token
- **Rate Limit Error**: HTTP 429 when exceeded
- **Usage Stats**: GET /stats/usage?days=7
- **Higher Limits**: Contact through registration page

## 🤝 Contributing

Contributions welcome! See CONTRIBUTING.md for guidelines.

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## 📄 License

MIT License - See LICENSE file for details.

## 🙏 Acknowledgments

This package uses the arXiv data service API provided by [1stAuthor](https://1stauthor.com/).

**Service Features:**
- 🎁 1000 free API requests per day
- 🚀 Redis-cached fast access
- 📦 Multiple paper formats
- 🔍 Built-in semantic search

## 📞 Support

- 🐛 **GitHub Issues**: https://github.com/qhjqhj00/py1stauthor/issues
- 📚 **API Documentation**: https://data.rag.ac.cn/api/docs
- 🎮 **Live Demo**: https://1stauthor.com/
- 🔑 **Register**: https://data.rag.ac.cn/register

## 📊 Package Status

✅ **Completed Features:**
- ✓ Reader class with full API access
- ✓ Agent class with ReAct framework
- ✓ LangGraph workflow
- ✓ Tool definitions and execution
- ✓ Streaming support
- ✓ Process logging
- ✓ Context persistence
- ✓ Multiple LLM provider support
- ✓ Comprehensive documentation (EN + CN)
- ✓ Example scripts
- ✓ Package configuration
- ✓ Test script

## 🚀 Next Steps

To use the package:

1. **Install**: `pip install py1stauthor[all]`
2. **Get Token**: Visit https://data.rag.ac.cn/register
3. **Run Examples**: Check `examples/` directory
4. **Read Docs**: See README.md for full API reference
5. **Try Demo**: Visit https://1stauthor.com/

---

**Created**: 2024-01-24  
**Author**: Hongjin Qian (@qhjqhj00)  
**Package**: py1stauthor v0.1.0  
**Repository**: https://github.com/qhjqhj00/py1stauthor
