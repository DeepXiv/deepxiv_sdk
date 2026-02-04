"""
deepxiv-sdk - A Python package for arXiv paper access with CLI and MCP server support.
"""

__version__ = "0.1.0"

from .reader import Reader

__all__ = ["Reader"]

# Try to import agent components if langgraph is available
try:
    from .agent.agent import Agent
    __all__.append("Agent")
except ImportError:
    # Agent functionality not available without langgraph
    pass
