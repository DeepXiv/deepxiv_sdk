"""
Main Agent class for intelligent paper interaction.
"""
import time
from typing import Optional, Dict
from openai import OpenAI

from ..reader import Reader
from .graph import create_react_graph, create_initial_state
from .tools import ToolExecutor
from .state import AgentState

import tiktoken

encoding = tiktoken.get_encoding("o200k_base")

def num_tokens_from_messages(messages, tokens_per_message=3, tokens_per_name=1):
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            if not isinstance(value, str):
                continue
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3
    return num_tokens   

class Agent:
    """
    Intelligent agent for interacting with arXiv papers using ReAct framework.

    Example:
        >>> from deepxiv_sdk import Reader, Agent
        >>> reader = Reader(token="your_token")
        >>> agent = Agent(
        ...     api_key="your_api_key",
        ...     model="gpt-4",
        ...     reader=reader,
        ...     print_process=True
        ... )
        >>> answer = agent.query("What are the latest papers about agent memory?")
    """

    def __init__(
        self,
        api_key: str,
        reader: Reader,
        model: str = "gpt-4",
        base_url: Optional[str] = None,
        max_llm_calls: int = 20,
        max_time_seconds: int = 600,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        print_process: bool = False,
        stream: bool = False
    ):
        """
        Initialize the Agent.

        Args:
            api_key: API key for the LLM provider
            reader: Reader instance for API access
            model: Model name (e.g., "gpt-4", "gpt-3.5-turbo", "deepseek-chat")
            base_url: Optional base URL for OpenAI-compatible APIs
                     (e.g., "https://api.deepseek.com", "https://openrouter.ai/api/v1")
            max_llm_calls: Maximum number of LLM calls per query (default: 20)
            max_time_seconds: Maximum time in seconds per query (default: 600)
            max_tokens: Maximum tokens per LLM call (default: 4096)
            temperature: Sampling temperature (default: 0.7)
            print_process: Whether to print the reasoning process (default: False)
            stream: Whether to stream LLM responses (default: False)
        """
        self.reader = reader
        self.model = model
        self.max_llm_calls = max_llm_calls
        self.max_time_seconds = max_time_seconds
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.print_process = print_process
        self.stream = stream

        # Initialize OpenAI client
        if base_url:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = OpenAI(api_key=api_key)

        # Initialize tool executor
        self.tool_executor = ToolExecutor(reader)

        # Create graph
        self.graph = create_react_graph()

        # State for persistent papers across queries
        self.persistent_papers: Dict = {}

    def query(self, question: str, reset_papers: bool = False) -> str:
        """
        Query the agent with a question.

        Args:
            question: The question to ask
            reset_papers: Whether to reset loaded papers (default: False)

        Returns:
            The answer string
        """
        if self.print_process:
            print(f"\n{'='*80}")
            print(f"🤔 Question: {question}")
            print(f"{'='*80}\n")

        # Reset papers if requested
        if reset_papers:
            self.persistent_papers = {}

        # Create initial state
        state = create_initial_state(papers=self.persistent_papers.copy())
        state["question"] = question
        state["num_llm_calls_available"] = self.max_llm_calls
        state["start_time"] = time.time()

        # Prepare config
        config = {
            "configurable": {
                "client": self.client,
                "model_name": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "max_llm_calls": self.max_llm_calls,
                "max_time_seconds": self.max_time_seconds,
                "print_process": self.print_process,
                "stream": self.stream,
                "tool_executor": self.tool_executor
            },
            "recursion_limit": 100
        }

        # Run graph
        try:
            final_state = self.graph.invoke(state, config)

            # Update persistent papers
            self.persistent_papers.update(final_state.get("papers", {}))

            prediction = final_state.get("prediction", "No answer found.")
            termination = final_state.get("termination", "unknown")
            total_token = num_tokens_from_messages(final_state.get("messages", []))
            if self.print_process:
                print(f"\n{'='*80}")
                print(f"✅ Completed: {termination}")
                print(f"📊 Rounds: {final_state.get('round', 0)}")
                print(f"📄 Papers loaded: {len(self.persistent_papers)}")
                print(f"🔢 Total tokens: {total_token}")
                print(f"{'='*80}\n")

            return prediction

        except Exception as e:
            if self.print_process:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()
            return f"Error: {e}"

    def get_loaded_papers(self) -> Dict:
        """
        Get information about currently loaded papers.

        Returns:
            Dictionary of loaded papers
        """
        return self.persistent_papers

    def reset_papers(self):
        """Reset all loaded papers."""
        self.persistent_papers = {}
        if self.print_process:
            print("🔄 Papers reset.")

    def add_paper(self, arxiv_id: str) -> bool:
        """
        Manually add a paper to the context.

        Args:
            arxiv_id: arXiv ID to load

        Returns:
            True if successful
        """
        if arxiv_id in self.persistent_papers:
            if self.print_process:
                print(f"Paper {arxiv_id} already loaded.")
            return True

        head_info = self.reader.head(arxiv_id)
        if not head_info:
            if self.print_process:
                print(f"Failed to load paper {arxiv_id}.")
            return False

        self.persistent_papers[arxiv_id] = {
            "arxiv_id": arxiv_id,
            "title": head_info.get("title", ""),
            "abstract": head_info.get("abstract", ""),
            "authors": head_info.get("authors", []),
            "sections": head_info.get("sections", {}),
            "token_count": head_info.get("token_count", 0),
            "categories": head_info.get("categories", []),
            "publish_at": head_info.get("publish_at", ""),
            "loaded_sections": {}
        }

        if self.print_process:
            print(f"✅ Loaded paper {arxiv_id}: {head_info.get('title', '')}")

        return True
