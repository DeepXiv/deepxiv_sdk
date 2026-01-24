"""
Agent module for intelligent paper interaction.
"""

try:
    from .agent import Agent
    __all__ = ["Agent"]
except ImportError:
    # Dependencies not available
    pass
