"""
State definitions for the ReAct agent.
"""
from typing import TypedDict, List, Dict, Optional, Annotated
import operator


class PaperInfo(TypedDict):
    """Information about a loaded paper."""
    arxiv_id: str
    title: str
    abstract: str
    authors: List[Dict]
    sections: Dict[str, Dict]  # section_name -> {idx, tldr, token_count}
    token_count: int
    categories: List[str]
    publish_at: str
    loaded_sections: Dict[str, str]  # section_name -> full_content


class AgentState(TypedDict):
    """Overall state for the ReAct agent."""
    # Papers being tracked
    papers: Dict[str, PaperInfo]  # arxiv_id -> PaperInfo

    # Conversation messages (accumulated)
    messages: Annotated[List[Dict], operator.add]

    # Current state tracking
    question: str  # Current user question
    response: str  # Current LLM response
    status: List[str]  # Status history: ["planning", "tool_call", "answer", etc.]

    # Round tracking
    round: int
    num_llm_calls_available: int
    start_time: float

    # Final output
    prediction: str
    termination: str

    # Additional metadata
    paper_sections_cache: Dict[str, Dict[str, str]]  # arxiv_id -> {section_name: content}
    full_paper_cache: Dict[str, str]  # arxiv_id -> full_content
    search_results_cache: List[Dict]  # Cache for search results
