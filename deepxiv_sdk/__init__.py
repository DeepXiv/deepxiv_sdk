"""
deepxiv-sdk - A Python package for arXiv paper access with CLI and MCP server support.
"""

__version__ = "0.2.0"

from .reader import (
    Reader,
    APIError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ServerError,
)

__all__ = [
    "Reader",
    "APIError",
    "AuthenticationError",
    "RateLimitError",
    "NotFoundError",
    "ServerError",
]

# Try to import agent components if langgraph is available
try:
    from .agent.agent import Agent
    __all__.append("Agent")
except ImportError:
    # Agent functionality not available without langgraph
    pass
