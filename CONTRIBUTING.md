# Contributing to py1stauthor

Thank you for your interest in contributing to py1stauthor! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/py1stauthor.git
   cd py1stauthor
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install development dependencies:
   ```bash
   pip install -e .[all,dev]
   ```

## Development Setup

### Running Tests

```bash
pytest tests/
```

### Code Style

We use:
- `black` for code formatting
- `flake8` for linting
- `mypy` for type checking

Format your code:
```bash
black py1stauthor/
```

Check linting:
```bash
flake8 py1stauthor/
```

Type checking:
```bash
mypy py1stauthor/
```

## Making Changes

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following these guidelines:
   - Write clear, descriptive commit messages
   - Add docstrings to all functions and classes
   - Add type hints where appropriate
   - Update documentation if needed
   - Add tests for new functionality

3. Test your changes:
   ```bash
   python test_package.py
   pytest tests/
   ```

4. Commit your changes:
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Create a Pull Request

## Pull Request Guidelines

- Provide a clear description of the changes
- Reference any related issues
- Ensure all tests pass
- Update documentation as needed
- Follow the code style guidelines

## Code Structure

```
py1stauthor/
├── py1stauthor/          # Main package
│   ├── reader.py         # API access layer
│   └── agent/            # Agent implementation
│       ├── agent.py      # Main Agent class
│       ├── state.py      # State definitions
│       ├── tools.py      # Tool implementations
│       ├── prompts.py    # System prompts
│       └── graph.py      # LangGraph workflow
├── examples/             # Example scripts
└── tests/                # Test suite
```

## Adding New Features

### Adding a New Tool

1. Define the tool in `py1stauthor/agent/tools.py`:
   ```python
   def tool_name(self, arg1: str, arg2: int) -> str:
       """Tool description."""
       # Implementation
       pass
   ```

2. Add tool definition to `get_tools_definition()`:
   ```python
   {
       "type": "function",
       "function": {
           "name": "tool_name",
           "description": "Tool description",
           "parameters": {...}
       }
   }
   ```

3. Add execution logic in `execute_tool_call()`:
   ```python
   elif tool_name == "tool_name":
       return self.tool_name(arg1, arg2)
   ```

4. Add tests and examples

### Adding a New Reader Method

1. Add method to `Reader` class in `py1stauthor/reader.py`
2. Follow existing pattern for API calls
3. Add proper error handling
4. Update documentation
5. Add examples

## Documentation

- Update README.md for user-facing changes
- Update docstrings for code changes
- Add examples for new features
- Update CHANGELOG.md

## Testing

- Write unit tests for new functions
- Add integration tests for new features
- Ensure all tests pass before submitting PR
- Aim for high test coverage

## Issue Reporting

When reporting issues, please include:
- Python version
- Package version
- Operating system
- Minimal code to reproduce the issue
- Expected vs actual behavior
- Error messages and stack traces

## Questions?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Questions about usage
- Documentation improvements

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
