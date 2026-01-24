# Examples

This directory contains example scripts demonstrating how to use py1stauthor.

## Quick Start

- **`quickstart.py`**: The fastest way to get started - minimal example to get up and running

## Basic Examples

- **`example_reader.py`**: Basic usage of the Reader class for accessing arXiv papers
  - Searching for papers
  - Getting paper metadata
  - Reading sections
  - Getting previews and full content

- **`example_agent.py`**: Basic usage of the Agent class for intelligent paper analysis
  - Simple queries
  - Follow-up questions with context
  - Detailed paper analysis
  - Using different LLM providers (OpenAI, DeepSeek, OpenRouter)

## Advanced Examples

- **`example_advanced.py`**: Advanced Agent usage patterns
  - Literature reviews
  - Methodology comparisons
  - Concept explanations
  - Research trend analysis
  - Finding related work
  - Multi-query interactive sessions

## Running the Examples

1. Set up your API tokens as environment variables:

```bash
export ARXIV_API_TOKEN="your_arxiv_token"
export OPENAI_API_KEY="your_openai_key"
# Or for DeepSeek:
export DEEPSEEK_API_KEY="your_deepseek_key"
```

2. Install the package:

```bash
pip install py1stauthor[all]
```

3. Run an example:

```bash
python examples/quickstart.py
python examples/example_reader.py
python examples/example_agent.py
python examples/example_advanced.py
```

## Customization

All examples can be customized by:
- Changing the model (e.g., "gpt-4", "gpt-3.5-turbo", "deepseek-chat")
- Adjusting parameters (temperature, max_tokens, max_llm_calls)
- Using different LLM providers (OpenAI, DeepSeek, OpenRouter, etc.)
- Modifying the queries to suit your research needs

## Tips

- Use `print_process=True` to see the agent's reasoning steps
- Use `stream=True` for real-time response streaming
- Start with simpler queries and build up to more complex ones
- The agent maintains context across queries, so you can ask follow-up questions
- Use `agent.reset_papers()` to start fresh on a new topic
