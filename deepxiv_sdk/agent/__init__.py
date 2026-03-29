"""
Agent module for intelligent paper interaction.
"""

try:
    from .agent import Agent
    __all__ = ["Agent"]
except ImportError as e:
    _agent_import_error = e
    __all__ = []

    def __getattr__(name):
        if name == "Agent":
            raise ImportError(
                "Agent is unavailable because optional dependencies could not "
                f"be imported: {_agent_import_error}"
            ) from _agent_import_error
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
