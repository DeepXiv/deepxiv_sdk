# Documentation Structure / 文档结构

deepxiv-sdk provides comprehensive documentation in both English and Chinese.

## 📚 Documentation Map

### Core Documentation / 核心文档

**English Version:**
- [README.md](README.md) - Quick start and main features
- [USAGE.md](USAGE.md) - Advanced usage patterns
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines

**中文版本:**
- [README.zh.md](README.zh.md) - 快速开始和主要特性
- [USAGE.zh.md](USAGE.zh.md) - 高级用法模式
- [CONTRIBUTING.zh.md](CONTRIBUTING.zh.md) - 贡献指南

### Special Documents / 特殊文档

- [LANGUAGES.md](LANGUAGES.md) - Language selection guide / 语言选择指南
- [IMPROVEMENTS.md](IMPROVEMENTS.md) - Summary of improvements made / 改进总结
- [API Documentation](https://data.rag.ac.cn/api/docs) - API reference / API 参考

---

## 🎯 Quick Navigation / 快速导航

### For Beginners / 初学者

**English**: Start with [README.md](README.md) → Run `pip install deepxiv-sdk` → Try first command

**中文**: 从 [README.zh.md](README.zh.md) 开始 → 运行 `pip install deepxiv-sdk` → 尝试第一个命令

### For Advanced Users / 高级用户

**English**: Read [USAGE.md](USAGE.md) for patterns, best practices, and troubleshooting

**中文**: 阅读 [USAGE.zh.md](USAGE.zh.md) 了解模式、最佳实践和故障排查

### For Contributors / 贡献者

**English**: Read [CONTRIBUTING.md](CONTRIBUTING.md) for setup and guidelines

**中文**: 阅读 [CONTRIBUTING.zh.md](CONTRIBUTING.zh.md) 了解设置和指南

---

## 📖 Document Overview

### README.md / README.zh.md

**Purpose**: Main project documentation with quick start

**Contents**:
- Feature comparison table
- Installation instructions
- Quick start (Python, CLI, MCP)
- API reference
- Token management
- Error handling
- FAQ

**Time to read**: 10-15 minutes

### USAGE.md / USAGE.zh.md

**Purpose**: Advanced usage patterns and best practices

**Contents**:
- Advanced search techniques
- 4 content loading strategies
- Error handling patterns
- Batch processing
- Agent multi-turn conversations
- Best practices
- Troubleshooting

**Time to read**: 20-30 minutes

### CONTRIBUTING.md / CONTRIBUTING.zh.md

**Purpose**: Guide for contributors

**Contents**:
- Development setup
- Code style guidelines
- Testing guide
- Commit conventions
- Project structure
- Common contribution types
- Type annotations and docstrings

**Time to read**: 15-20 minutes

### IMPROVEMENTS.md

**Purpose**: Summary of all improvements made to the project

**Contents**:
- Improvement overview
- Core improvements (8 categories)
- Before/after comparison
- Quality metrics
- Implementation roadmap
- File changes list

**Time to read**: 10 minutes

---

## 🌐 Language Selection Strategy

The documentation uses the following convention:

1. **Main files** (README, USAGE, CONTRIBUTING): English version is primary
2. **Chinese versions**: Use `.zh` suffix (e.g., `README.zh.md`)
3. **Links**: Each language version links to its counterpart
4. **Navigation**: Use [LANGUAGES.md](LANGUAGES.md) for language switching

### File Naming Convention

```
README.md          # English (default)
README.zh.md       # Chinese
USAGE.md           # English (default)
USAGE.zh.md        # Chinese
CONTRIBUTING.md    # English (default)
CONTRIBUTING.zh.md # Chinese
```

---

## 📋 All Documentation Files

### Generated Files (Documentation)

| File | Purpose | Language |
|------|---------|----------|
| README.md | Main documentation | English |
| README.zh.md | 主文档 | 中文 |
| USAGE.md | Advanced guide | English |
| USAGE.zh.md | 高级指南 | 中文 |
| CONTRIBUTING.md | Contribution guide | English |
| CONTRIBUTING.zh.md | 贡献指南 | 中文 |
| IMPROVEMENTS.md | Improvement summary | English/Bilingual |
| LANGUAGES.md | Language navigation | Bilingual |
| LICENSE | MIT License | English |

### Code Files (With Docstrings)

| File | Description |
|------|-------------|
| `deepxiv_sdk/reader.py` | Core Reader class with full type hints and docstrings |
| `deepxiv_sdk/cli.py` | CLI implementation with help text |
| `deepxiv_sdk/mcp_server.py` | MCP Server implementation |
| `deepxiv_sdk/agent/` | Agent implementation files |

### Example Files

| File | Purpose |
|------|---------|
| `examples/quickstart.py` | 5-minute quick start |
| `examples/example_reader.py` | Basic Reader usage |
| `examples/example_agent.py` | Agent usage |
| `examples/example_advanced.py` | Advanced patterns |
| `examples/example_error_handling.py` | Error handling examples |

---

## 🔗 Cross-Language References

All documents include language switch links at the top:

**In English documents:**
```markdown
> **中文版**: [README.zh.md](README.zh.md)
```

**In Chinese documents:**
```markdown
> **English Version**: [README.md](README.md)
```

---

## 📖 Reading Paths

### Path 1: Complete Beginner

1. [README.md](README.md) - Quick Start section (5 min)
2. Install: `pip install deepxiv-sdk[all]`
3. Run: `deepxiv search "agent memory" --limit 5`
4. Try Python example from README
5. Read [USAGE.md](USAGE.md) as needed

### Path 2: Experienced Developer

1. [README.md](README.md) - Feature comparison and API reference (10 min)
2. [USAGE.md](USAGE.md) - Advanced patterns (20 min)
3. Explore code examples in `examples/`
4. Read [CONTRIBUTING.md](CONTRIBUTING.md) if interested in contributing

### Path 3: LLM/AI Researcher

1. [README.md](README.md) - Features and Quick Start (10 min)
2. Python API examples from README
3. [USAGE.md](USAGE.md) - Agent usage and advanced patterns (15 min)
4. `examples/example_agent.py` and `example_advanced.py`

### Path 4: Contributor

1. [README.md](README.md) - Overview (5 min)
2. [CONTRIBUTING.md](CONTRIBUTING.md) - Full guide (20 min)
3. Clone and `pip install -e ".[all,dev]"`
4. Run tests: `pytest tests/ -v --cov=deepxiv_sdk`
5. Make changes and submit PR

---

## 🎓 Learning Resources

### Official Resources

1. **API Documentation**: [https://data.rag.ac.cn/api/docs](https://data.rag.ac.cn/api/docs)
2. **GitHub Repository**: [https://github.com/qhjqhj00/deepxiv_sdk](https://github.com/qhjqhj00/deepxiv_sdk)
3. **GitHub Issues**: [Report issues or ask questions](https://github.com/qhjqhj00/deepxiv_sdk/issues)

### Code Examples

All example files are in `examples/` directory and are fully functional:

```bash
cd examples/
python quickstart.py
python example_reader.py
python example_error_handling.py
```

---

## ✅ Checklist for Documentation

- [x] English README with complete quick start
- [x] Chinese README with parallel content
- [x] English USAGE guide with advanced patterns
- [x] Chinese USAGE guide with advanced patterns
- [x] English CONTRIBUTING guide
- [x] Chinese CONTRIBUTING guide
- [x] Language navigation document
- [x] Full docstrings in code
- [x] Type hints on all public methods
- [x] Example files with error handling
- [x] API reference table
- [x] Troubleshooting section
- [x] FAQ section

---

**Last Updated**: 2024
**Coverage**: English and Chinese
**Status**: Complete

For questions or suggestions, please open an issue on [GitHub](https://github.com/qhjqhj00/deepxiv_sdk/issues).
