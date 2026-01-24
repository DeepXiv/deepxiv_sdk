# py1stauthor Package Structure

This document provides an overview of the package structure and files.

## Project Structure

```
py1stauthor/
├── py1stauthor/              # Main package directory
│   ├── __init__.py           # Package initialization, exports Reader and Agent
│   ├── reader.py             # Reader class for API access
│   └── agent/                # Agent module (ReAct framework)
│       ├── __init__.py       # Agent module initialization
│       ├── agent.py          # Main Agent class
│       ├── state.py          # State definitions for ReAct workflow
│       ├── tools.py          # Tool definitions and executor
│       ├── prompts.py        # System prompts for the agent
│       └── graph.py          # LangGraph workflow implementation
├── examples/                 # Example scripts
│   ├── README.md             # Examples documentation
│   ├── quickstart.py         # Quick start example
│   ├── example_reader.py     # Reader examples
│   ├── example_agent.py      # Basic agent examples
│   └── example_advanced.py   # Advanced agent examples
├── setup.py                  # Package setup script
├── requirements.txt          # Base dependencies (API only)
├── requirements-full.txt     # Full dependencies (with agent)
├── MANIFEST.in               # Files to include in distribution
├── LICENSE                   # MIT License
├── .gitignore               # Git ignore patterns
├── README.md                 # English documentation
└── README_CN.md              # Chinese documentation
```

## Key Components

### Reader (`reader.py`)

The `Reader` class provides direct access to the arXiv data service API:
- `search()`: Search for papers
- `head()`: Get paper metadata
- `section()`: Read specific sections
- `raw()`: Get full paper content
- `preview()`: Get limited preview
- `meta()`: Get metadata

### Agent (`agent/agent.py`)

The `Agent` class implements an intelligent ReAct-based agent:
- Uses LangGraph for workflow orchestration
- Supports OpenAI-compatible APIs (OpenAI, DeepSeek, OpenRouter, etc.)
- Implements reasoning + acting pattern
- Maintains context across queries
- Supports streaming and process logging

### State (`agent/state.py`)

Defines the TypedDict structures for:
- `PaperInfo`: Individual paper information
- `AgentState`: Overall agent state including messages, papers, and caches

### Tools (`agent/tools.py`)

Implements tool definitions and executor:
- `search_papers`: Search functionality
- `load_paper`: Load paper metadata
- `read_section`: Read specific sections
- `get_full_paper`: Get complete paper
- `get_paper_preview`: Get limited preview

### Graph (`agent/graph.py`)

LangGraph workflow with nodes:
- `planning_node`: LLM reasoning and decision making
- `tool_call_node`: Tool execution
- `check_limits_node`: Resource limit checking
- `finalize_node`: Answer extraction
- Conditional routing between nodes

### Prompts (`agent/prompts.py`)

System prompt generation for the agent with:
- Role definition
- Tool descriptions
- ReAct pattern instructions
- Response format guidelines

## Installation Options

### 1. API Only (Lightweight)
```bash
pip install py1stauthor
```
Dependencies: `requests`

### 2. Full Installation (with Agent)
```bash
pip install py1stauthor[all]
```
Dependencies: `requests`, `openai`, `langgraph`, `langchain-core`

### 3. Development Installation
```bash
git clone <repository>
cd py1stauthor
pip install -e .[all]
```

## Usage Patterns

### Basic Reader Usage
```python
from py1stauthor import Reader
reader = Reader(token="your_token")
results = reader.search("query")
head = reader.head("arxiv_id")
```

### Basic Agent Usage
```python
from py1stauthor import Reader, Agent
reader = Reader(token="your_token")
agent = Agent(api_key="key", model="gpt-4", reader=reader)
answer = agent.query("question")
```

### Advanced Agent Usage
```python
agent = Agent(
    api_key="key",
    model="gpt-4",
    reader=reader,
    print_process=True,  # Show reasoning
    stream=True,         # Stream responses
    max_llm_calls=20,
    temperature=0.7
)
```

## Development

### Running Tests
```bash
pytest tests/
```

### Building Package
```bash
python setup.py sdist bdist_wheel
```

### Publishing to PyPI
```bash
twine upload dist/*
```

## License

MIT License - See LICENSE file for details.
