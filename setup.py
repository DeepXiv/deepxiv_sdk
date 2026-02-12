from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="deepxiv-sdk",
    version="0.1.1",
    author="Hongjin Qian",
    description="A Python package for arXiv paper access with CLI and MCP server support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/qhjqhj00/deepxiv-sdk",
    project_urls={
        "Homepage": "https://1stauthor.com/",
        "Documentation": "https://github.com/qhjqhj00/deepxiv-sdk#readme",
        "Repository": "https://github.com/qhjqhj00/deepxiv-sdk",
        "Bug Tracker": "https://github.com/qhjqhj00/deepxiv-sdk/issues",
        "Demo": "https://1stauthor.com/",
        "API Documentation": "https://data.rag.ac.cn/api/docs",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "click>=8.0.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "mcp": [
            "mcp[cli]>=1.2.0",
        ],
        "agent": [
            "openai>=1.0.0",
            "langgraph>=0.0.20",
            "langchain-core>=0.1.0",
        ],
        "all": [
            "requests>=2.31.0",
            "click>=8.0.0",
            "python-dotenv>=0.19.0",
            "mcp[cli]>=1.2.0",
            "openai>=1.0.0",
            "langgraph>=0.0.20",
            "langchain-core>=0.1.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "deepxiv=deepxiv_sdk.cli:main",
        ],
    },
    keywords=["arxiv", "research", "papers", "agent", "llm", "react", "mcp", "cli"],
    license="MIT",
)
