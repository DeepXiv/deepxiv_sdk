# Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip package manager

## Installation Options

### Option 1: API Only (Lightweight)

If you only need to access the arXiv data service API without the intelligent agent:

```bash
pip install py1stauthor
```

This installs only the base dependencies:
- `requests>=2.31.0`

**Usage:**
```python
from py1stauthor import Reader
reader = Reader(token="your_token")
```

### Option 2: Full Installation (Recommended)

For complete functionality including the intelligent agent:

```bash
pip install py1stauthor[all]
```

This installs all dependencies including:
- `requests>=2.31.0`
- `openai>=1.0.0`
- `langgraph>=0.0.20`
- `langchain-core>=0.1.0`

**Usage:**
```python
from py1stauthor import Reader, Agent
reader = Reader(token="your_token")
agent = Agent(api_key="your_key", model="gpt-4", reader=reader)
```

### Option 3: Development Installation

For development and testing:

```bash
git clone https://github.com/yourusername/py1stauthor.git
cd py1stauthor
pip install -e .[all]
```

This installs the package in editable mode, so changes to the source code are immediately reflected.

## Upgrading

To upgrade to the latest version:

```bash
pip install --upgrade py1stauthor[all]
```

## Verifying Installation

After installation, verify that the package is installed correctly:

```bash
python -c "from py1stauthor import Reader; print('Reader imported successfully')"
```

Or run the test script:

```bash
cd py1stauthor
python test_package.py
```

## API Tokens

### arXiv Data Service Token

You need an API token to access the arXiv data service.

**Get your token:** [https://data.rag.ac.cn/register](https://data.rag.ac.cn/register)

**Features:**
- 🎁 1000 free requests per day
- 🚀 Fast Redis-cached access
- 📦 Multiple paper formats
- 🔍 Built-in semantic search

**Test Papers** (no token required):
- `2409.05591`
- `2504.21776`

**Free Search Queries** (no token required):
- "transformer"
- "attention mechanism"
- "large language model"

Set your token as an environment variable:
```bash
export ARXIV_API_TOKEN="your_token_here"
```

**API Documentation:** [https://data.rag.ac.cn/api/docs](https://data.rag.ac.cn/api/docs)

### LLM Provider API Keys

To use the Agent, you need an API key from an LLM provider:

#### OpenAI
```bash
export OPENAI_API_KEY="your_openai_key"
```

#### DeepSeek
```bash
export DEEPSEEK_API_KEY="your_deepseek_key"
```

#### OpenRouter
```bash
export OPENROUTER_API_KEY="your_openrouter_key"
```

## Troubleshooting

### Import Error: No module named 'langgraph'

If you get this error when trying to import Agent:
```python
ImportError: No module named 'langgraph'
```

Solution: Install the full package with agent dependencies:
```bash
pip install py1stauthor[all]
```

### Import Error: No module named 'py1stauthor'

If you get this error:
```python
ImportError: No module named 'py1stauthor'
```

Solution: Make sure you've installed the package:
```bash
pip install py1stauthor
```

### API Connection Errors

If you get connection errors when using the Reader:
```python
requests.exceptions.RequestException: ...
```

Possible solutions:
1. Check your internet connection
2. Verify your API token is correct
3. Check if the API endpoint is accessible: `https://data.rag.ac.cn`

### LLM API Errors

If you get errors when using the Agent:
```python
openai.error.AuthenticationError: ...
```

Possible solutions:
1. Verify your API key is correct
2. Check if you have credits/quota available
3. Verify the base_url if using a non-OpenAI provider

## Platform-Specific Notes

### Windows

Use PowerShell or Command Prompt:
```powershell
pip install py1stauthor[all]
```

Set environment variables:
```powershell
$env:ARXIV_API_TOKEN="your_token"
$env:OPENAI_API_KEY="your_key"
```

### macOS/Linux

```bash
pip install py1stauthor[all]
```

Set environment variables in `~/.bashrc` or `~/.zshrc`:
```bash
export ARXIV_API_TOKEN="your_token"
export OPENAI_API_KEY="your_key"
```

### Virtual Environments

It's recommended to use a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install package
pip install py1stauthor[all]
```

## Next Steps

After successful installation:

1. Check out the [Quick Start Guide](README.md#quick-start)
2. Explore the [examples](examples/) directory
3. Read the [API Reference](README.md#api-reference)
4. Try the live demo at [https://1stauthor.com/](https://1stauthor.com/)

## Getting Help

If you encounter issues:
- 🐛 Check the [GitHub Issues](https://github.com/qhjqhj00/py1stauthor/issues)
- 📚 Read the [API Documentation](https://data.rag.ac.cn/api/docs)
- 📖 Read the [Package Documentation](README.md)
- 🎮 Try the [Live Demo](https://1stauthor.com/)
