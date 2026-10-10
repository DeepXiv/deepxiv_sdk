"""
deepxiv-sdk - Agentic search over arXiv and the web, with real citations.
"""

__version__ = "1.2.0b1"

from .reader import (
    Reader,
    agent_search_sources,
    APIError,
    BadRequestError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ServerError,
)
from .fa import FAClient, FAError, FilterError, build_filters

__all__ = [
    "Reader",
    "agent_search_sources",
    "APIError",
    "BadRequestError",
    "AuthenticationError",
    "RateLimitError",
    "NotFoundError",
    "ServerError",
    "FAClient",
    "FAError",
    "FilterError",
    "build_filters",
]

# Try to import agent components if langgraph is available
try:
    from .agent.agent import Agent
    __all__.append("Agent")
except ImportError:
    # Agent functionality not available without langgraph
    pass
