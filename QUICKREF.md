# py1stauthor - Quick Reference Card

## Installation
```bash
pip install py1stauthor[all]
```

## Get API Token
🔑 Register at: https://data.rag.ac.cn/register
- 1000 free requests/day
- No credit card required

## Quick Start

### Reader (API Access)
```python
from py1stauthor import Reader

reader = Reader(token="your_token")

# Search papers
results = reader.search("agent memory", top_k=10)

# Load paper metadata
head = reader.head("2409.05591")

# Read section
section = reader.section("2409.05591", "Introduction")

# Get full paper
full = reader.raw("2409.05591")
```

### Agent (Intelligent Analysis)
```python
from py1stauthor import Agent

agent = Agent(
    api_key="your_llm_key",
    model="gpt-4",
    reader=reader,
    print_process=True,
    stream=True
)

answer = agent.query("What are the latest papers about transformers?")
```

## Links
- 🎮 Demo: https://1stauthor.com/
- 📚 API Docs: https://data.rag.ac.cn/api/docs
- 🐛 Issues: https://github.com/qhjqhj00/py1stauthor/issues
- 📖 Full README: [README.md](README.md)

## Author
Hongjin Qian (@qhjqhj00)

## License
MIT
