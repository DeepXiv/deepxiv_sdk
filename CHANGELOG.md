# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-01-24

### Added
- Initial release of py1stauthor package
- `Reader` class for accessing arXiv data service API ([https://data.rag.ac.cn/api/docs](https://data.rag.ac.cn/api/docs))
  - Search functionality with `search()` - semantic search across papers
  - Paper metadata access with `head()` - get title, authors, sections with TLDRs
  - Section reading with `section()` - read specific paper sections
  - Full paper content with `raw()` - get complete markdown content
  - Paper preview with `preview()` - get first 10,000 characters
  - Metadata access with `meta()` - get structured metadata
- `Agent` class implementing ReAct framework for intelligent paper analysis
  - LangGraph-based workflow orchestration
  - Support for OpenAI-compatible APIs (OpenAI, DeepSeek, OpenRouter)
  - Streaming response support
  - Process logging with `print_process` parameter
  - Context persistence across queries
  - Automatic tool selection and execution
- Tool implementations:
  - `search_papers`: Search for relevant papers
  - `load_paper`: Load paper metadata and structure
  - `read_section`: Read specific paper sections
  - `get_full_paper`: Get complete paper content
  - `get_paper_preview`: Get limited token preview
- Comprehensive documentation:
  - English README with full API reference
  - Chinese README (README_CN.md)
  - Installation guide (INSTALL.md)
  - Package structure documentation (PACKAGE_STRUCTURE.md)
- Example scripts:
  - Quick start example
  - Basic Reader usage examples
  - Basic Agent usage examples
  - Advanced Agent usage patterns
- Optional dependency installation via extras_require
  - Base installation for API-only functionality
  - `[agent]` extra for agent functionality
  - `[all]` extra for complete functionality
- MIT License
- Package configuration files:
  - setup.py for backward compatibility
  - pyproject.toml for modern Python packaging
  - requirements.txt and requirements-full.txt
  - MANIFEST.in for distribution

### Features
- 🔍 Natural language paper search using semantic search
- 📄 Structured paper access (metadata, sections, full content)
- 🤖 Intelligent ReAct-based agent for paper analysis
- 🔌 Flexible LLM provider support (any OpenAI-compatible API)
- 💬 Real-time streaming responses
- 📊 Detailed process logging and reasoning traces
- 🔄 Context persistence across multiple queries
- 🎯 Automatic tool selection based on query intent
- 🎁 1000 free API requests per day
- 🚀 Redis-cached fast access to papers

### Technical Details
- Python 3.8+ support
- Type hints for better IDE support
- Modular architecture with clear separation of concerns
- LangGraph for workflow orchestration
- OpenAI SDK for LLM interactions
- Robust error handling and retry logic

## [Unreleased]

### Planned
- Unit tests and integration tests
- CI/CD pipeline setup
- Additional tool implementations
- Enhanced caching mechanisms
- Async support for better performance
- CLI interface
- Web interface/demo
- More example notebooks
- Performance benchmarks
- API rate limiting and quota management
