# 贡献指南

感谢你对 deepxiv-sdk 的兴趣！本指南将帮助你以最佳方式做出贡献。

> **English Version**: [CONTRIBUTING.md](CONTRIBUTING.md)

## 开发设置

### 克隆仓库并安装依赖

```bash
git clone https://github.com/qhjqhj00/deepxiv_sdk.git
cd deepxiv_sdk

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装开发依赖
pip install -e ".[all,dev]"
```

### 代码风格

我们使用以下工具维持代码质量：

- **black**: 代码格式化
- **isort**: Import 排序
- **mypy**: 类型检查
- **pytest**: 单元测试

运行这些工具：

```bash
# 格式化代码
black deepxiv_sdk tests examples

# 排序 imports
isort deepxiv_sdk tests examples

# 类型检查
mypy deepxiv_sdk

# 运行测试
pytest tests/ -v --cov=deepxiv_sdk
```

## 提交贡献

### 1. 创建特性分支

```bash
git checkout -b feature/your-feature-name
# 或用于 bug 修复
git checkout -b bugfix/issue-description
```

### 2. 编写代码和测试

- 遵循现有的代码风格
- 为新功能添加单元测试
- 更新相关文档
- 添加类型注解

### 3. 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_reader.py::TestSearch::test_search_basic -v

# 生成覆盖率报告
pytest tests/ --cov=deepxiv_sdk --cov-report=html
```

### 4. 提交 commit

遵循 Conventional Commits 格式：

```
type(scope): description

[optional body]
[optional footer]
```

类型：
- **feat**: 新功能
- **fix**: bug 修复
- **docs**: 文档更新
- **test**: 添加或修改测试
- **refactor**: 代码重构
- **perf**: 性能优化
- **chore**: 构建、依赖等

示例：

```bash
git commit -m "feat(reader): add caching for paper metadata"
git commit -m "fix(cli): handle invalid token gracefully"
```

### 5. 推送并创建 Pull Request

```bash
git push origin feature/your-feature-name
```

在 GitHub 上创建 Pull Request，使用以下模板：

```markdown
## 描述
简要说明你的更改内容。

## 关联的 Issue
修复 #123

## 改动类型
- [ ] Bug 修复
- [ ] 新功能
- [ ] Breaking change
- [ ] 文档更新

## 测试清单
- [ ] 添加了相关单元测试
- [ ] 所有测试通过
- [ ] 代码通过 linting 检查
- [ ] 更新了相关文档

## 额外信息
任何额外的上下文或信息。
```

## 项目结构

```
deepxiv-sdk/
├── deepxiv_sdk/          # 主包
│   ├── __init__.py       # 包初始化和导出
│   ├── reader.py         # 核心 Reader 类
│   ├── cli.py            # CLI 命令实现
│   ├── mcp_server.py     # MCP Server 实现
│   └── agent/            # Agent 实现
│       ├── agent.py      # 主 Agent 类
│       ├── graph.py      # ReAct 图定义
│       ├── tools.py      # Agent 工具
│       ├── state.py      # Agent 状态定义
│       └── prompts.py    # System prompts
├── tests/                # 测试
│   ├── conftest.py       # pytest fixtures
│   ├── test_reader.py    # Reader 单元测试
│   ├── test_cli.py       # CLI 集成测试
│   └── test_mcp_server.py # MCP Server 测试
├── examples/             # 示例代码
├── README.md             # 英文项目 README
├── README.zh.md          # 中文项目 README
├── USAGE.md              # 英文高级使用指南
├── USAGE.zh.md           # 中文高级使用指南
└── pyproject.toml        # 项目配置
```

## 常见贡献类型

### 添加新功能

1. 在 `Reader` 类中添加方法（如果是 API 功能）
2. 在 `mcp_server.py` 中添加对应的 MCP 工具
3. 添加单元测试和集成测试
4. 在 README 或 USAGE 中文档化

### 修复 Bug

1. 创建一个测试用例重现 bug
2. 修复代码
3. 确保测试通过

### 改进文档

直接编辑 README、USAGE 或创建新的文档文件。

### 改进错误处理

在 `reader.py` 中完善 `_make_request` 方法，处理特定的错误情况。

## 编码规范

### 类型注解

所有函数都应该有类型注解：

```python
from typing import Optional, Dict, List, Any

def search(
    self,
    query: str,
    size: int = 10,
    categories: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Search for papers.

    Args:
        query: Search query string
        size: Number of results
        categories: Optional category filters

    Returns:
        Dictionary with search results
    """
    pass
```

### 文档字符串

使用 Google 风格的 docstring：

```python
def method_name(param1: str, param2: int) -> bool:
    """One-line summary.

    Longer description explaining what this method does,
    how it works, and any important considerations.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: Description of when this is raised
        APIError: Description of when this is raised
    """
    pass
```

### 错误处理

使用特定的异常类型：

```python
from deepxiv_sdk import AuthenticationError, RateLimitError, APIError

try:
    # API call
    pass
except requests.exceptions.Timeout:
    # 处理超时
    pass
except requests.exceptions.ConnectionError:
    # 处理连接错误
    pass
```

## 测试指南

### 编写测试

测试应该：
- 测试单一的功能或场景
- 使用有意义的测试名称
- 包含快速的 setup 和 teardown
- 避免外部依赖（使用 mocking）

```python
def test_search_with_categories(self, mock_reader):
    """Test search filters by categories."""
    results = mock_reader.search(
        "transformer",
        categories=["cs.AI", "cs.CL"]
    )
    assert isinstance(results, dict)
    assert "results" in results
```

### 运行特定测试

```bash
# 运行特定类
pytest tests/test_reader.py::TestSearch -v

# 运行特定方法
pytest tests/test_reader.py::TestSearch::test_search_basic -v

# 运行匹配模式的测试
pytest tests/ -k "search" -v
```

## 报告问题

使用 [GitHub Issues](https://github.com/qhjqhj00/deepxiv_sdk/issues) 报告 bug 或提议新功能。

**Bug 报告应包含：**
- 清晰的问题描述
- 复现步骤
- 预期行为
- 实际行为
- 环境信息（Python 版本、操作系统等）

**功能请求应包含：**
- 清晰的需求描述
- 用例和动机
- 建议的 API 设计（如果有）

## 获取帮助

- 查看 [README.zh.md](README.zh.md) 了解基础用法
- 查看 [USAGE.zh.md](USAGE.zh.md) 了解高级用法
- 查看 [examples/](examples/) 了解示例代码
- 在 Issues 上提问

## 许可证

通过提交代码，你同意以 MIT License 许可你的贡献。

---

感谢你的贡献！🎉
