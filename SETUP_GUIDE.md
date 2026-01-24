# Complete Setup and Usage Guide

## 🎯 Overview

This guide will walk you through setting up and using py1stauthor from scratch.

## Step 1: Get API Token (5 minutes)

1. **Visit Registration Page**: https://data.rag.ac.cn/register

2. **Fill in the form**:
   - Name
   - Phone number (with country code)
   - Verification code (SMS)
   - Email
   - Organization (optional)

3. **Save your token**: You'll receive an API token immediately
   - Daily limit: 1000 requests
   - Currently free!

4. **Set environment variable**:
   ```bash
   export ARXIV_API_TOKEN="your_token_here"
   ```

## Step 2: Install Package (2 minutes)

### For Full Functionality (Recommended)
```bash
pip install py1stauthor[all]
```

### For API Access Only
```bash
pip install py1stauthor
```

### From Source (for development)
```bash
git clone https://github.com/qhjqhj00/py1stauthor.git
cd py1stauthor
pip install -e .[all]
```

## Step 3: Get LLM API Key

Choose one of these providers:

### OpenAI
1. Visit: https://platform.openai.com/api-keys
2. Create API key
3. Set environment variable:
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```

### DeepSeek (Cheaper alternative)
1. Visit: https://platform.deepseek.com/
2. Create API key
3. Set environment variable:
   ```bash
   export DEEPSEEK_API_KEY="sk-..."
   ```

### OpenRouter (Access multiple models)
1. Visit: https://openrouter.ai/keys
2. Create API key
3. Set environment variable:
   ```bash
   export OPENROUTER_API_KEY="sk-..."
   ```

## Step 4: Test Installation

```python
# test_installation.py
from py1stauthor import Reader

# Test Reader
reader = Reader(token="your_arxiv_token")
print("✓ Reader initialized")

# Test with free paper (no token needed)
head = reader.head("2409.05591")
print(f"✓ Loaded paper: {head['title']}")

# Test Agent (if installed)
try:
    from py1stauthor import Agent
    agent = Agent(
        api_key="your_llm_key",
        model="gpt-4",
        reader=reader
    )
    print("✓ Agent initialized")
except ImportError:
    print("⚠ Agent not available (install with: pip install py1stauthor[all])")
```

## Step 5: Run Your First Query

### Example 1: Simple Search
```python
import os
from py1stauthor import Reader

reader = Reader(token=os.getenv("ARXIV_API_TOKEN"))

# Search for papers
results = reader.search("transformer attention mechanism", top_k=5)

for i, paper in enumerate(results, 1):
    print(f"{i}. {paper['title']}")
    print(f"   arXiv ID: {paper['arxiv_id']}\n")
```

### Example 2: Read a Paper
```python
import os
from py1stauthor import Reader

reader = Reader(token=os.getenv("ARXIV_API_TOKEN"))

# Get paper metadata
arxiv_id = "2409.05591"
head = reader.head(arxiv_id)

print(f"Title: {head['title']}")
print(f"\nAbstract: {head['abstract'][:200]}...")

print("\nAvailable sections:")
for section_name in head['sections'].keys():
    print(f"  - {section_name}")

# Read a section
intro = reader.section(arxiv_id, "Introduction")
print(f"\nIntroduction (first 500 chars):\n{intro[:500]}...")
```

### Example 3: Use the Agent
```python
import os
from py1stauthor import Reader, Agent

# Initialize
reader = Reader(token=os.getenv("ARXIV_API_TOKEN"))
agent = Agent(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4",
    reader=reader,
    print_process=True,  # See reasoning steps
    stream=True          # Stream responses
)

# Ask a question
answer = agent.query(
    "What are the key innovations in recent transformer papers? "
    "Find and summarize the top 3 papers."
)

print(f"\n{'='*80}")
print("ANSWER:")
print('='*80)
print(answer)
```

## Step 6: Advanced Usage

### Multi-Turn Conversation
```python
# First question
answer1 = agent.query("Find papers about vision transformers")
print(answer1)

# Follow-up (uses context from previous query)
answer2 = agent.query("How do these compare to CNNs?")
print(answer2)

# Another follow-up
answer3 = agent.query("Which would you recommend for image classification?")
print(answer3)
```

### Custom Configuration
```python
agent = Agent(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4",
    reader=reader,
    max_llm_calls=25,          # More calls for complex queries
    max_time_seconds=900,      # 15 minutes timeout
    temperature=0.7,           # Creativity level
    max_tokens=6000,           # Longer responses
    print_process=True,        # Debug mode
    stream=True                # Real-time output
)
```

### Using DeepSeek (Cheaper)
```python
agent = Agent(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    model="deepseek-chat",
    base_url="https://api.deepseek.com",
    reader=reader,
    print_process=True
)
```

## Common Use Cases

### 1. Literature Review
```python
answer = agent.query(
    "I'm researching attention mechanisms in neural networks. "
    "Find the 5 most influential papers, summarize their contributions, "
    "and identify trends."
)
```

### 2. Methodology Comparison
```python
# Pre-load papers
agent.add_paper("2409.05591")
agent.add_paper("2504.21776")

answer = agent.query(
    "Compare the methodologies in these papers. "
    "What are the key differences in their approaches?"
)
```

### 3. Concept Explanation
```python
answer = agent.query(
    "Explain 'self-attention' mechanism in detail. "
    "Find papers that discuss this and provide examples."
)
```

### 4. Finding Related Work
```python
answer = agent.query(
    "I'm working on few-shot learning for NLP. "
    "Find related papers and organize them by approach."
)
```

## Troubleshooting

### Problem: "No module named 'py1stauthor'"
**Solution**: Install the package
```bash
pip install py1stauthor[all]
```

### Problem: "No module named 'langgraph'"
**Solution**: Install with agent dependencies
```bash
pip install py1stauthor[all]
```

### Problem: "401 Unauthorized"
**Solution**: Check your API token
```python
# Test token
reader = Reader(token="your_token")
result = reader.head("2409.05591")  # Free paper
```

### Problem: "429 Too Many Requests"
**Solution**: You've exceeded daily limit (1000 requests)
- Wait until next day
- Contact service provider for higher limits

### Problem: Agent takes too long
**Solution**: Reduce max_llm_calls or use simpler queries
```python
agent = Agent(
    ...,
    max_llm_calls=10,  # Fewer calls
    max_time_seconds=300  # 5 minute timeout
)
```

## Performance Tips

1. **Use Preview First**: For quick overviews
   ```python
   preview = reader.preview(arxiv_id, max_tokens=2000)
   ```

2. **Load Only Needed Sections**: Don't load full paper unless necessary
   ```python
   section = reader.section(arxiv_id, "Introduction")
   ```

3. **Cache Results**: Agent automatically caches loaded papers
   ```python
   # First query loads papers
   agent.query("Find papers about X")
   
   # Second query uses cached papers
   agent.query("Tell me more about the first paper")
   ```

4. **Use Streaming**: See results in real-time
   ```python
   agent = Agent(..., stream=True)
   ```

5. **Lower Temperature**: For more focused answers
   ```python
   agent = Agent(..., temperature=0.3)
   ```

## Next Steps

1. **Explore Examples**: Check `examples/` directory for more patterns
2. **Read API Docs**: https://data.rag.ac.cn/api/docs
3. **Try Live Demo**: https://1stauthor.com/
4. **Read Full Docs**: See README.md for complete API reference
5. **Contribute**: See CONTRIBUTING.md for guidelines

## Resources

- 🎮 **Live Demo**: https://1stauthor.com/
- 📚 **API Documentation**: https://data.rag.ac.cn/api/docs
- 🔑 **Register**: https://data.rag.ac.cn/register
- 📖 **Full README**: README.md
- 🐛 **Issues**: https://github.com/qhjqhj00/py1stauthor/issues
- 💬 **Examples**: examples/

## Support

Need help? 
- Check documentation: README.md
- Try examples: examples/
- Open issue: https://github.com/qhjqhj00/py1stauthor/issues
- Read API docs: https://data.rag.ac.cn/api/docs

---

**Happy researching! 🚀**
