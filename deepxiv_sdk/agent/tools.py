"""
Tools for the ReAct agent to interact with arXiv papers.
"""
import json
from typing import Dict, Optional, List


def get_tools_definition() -> List[Dict]:
    """
    Get tools definition for OpenAI-compatible APIs.

    Returns:
        List of tool definitions in OpenAI function calling format
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "search_papers",
                "description": "Search for papers using Elasticsearch hybrid search (BM25 + Vector). Supports multiple search modes and advanced filtering by categories, authors, citations, and publication dates. Returns a list of papers with their arXiv IDs, titles, abstracts, authors, categories, and citation counts.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query (e.g., 'agent memory', 'transformer models')"
                        },
                        "size": {
                            "type": "integer",
                            "description": "Number of results to return (default: 10, max: 100)",
                            "default": 10
                        },
                        "offset": {
                            "type": "integer",
                            "description": "Result offset for pagination (default: 0)",
                            "default": 0
                        },
                        "search_mode": {
                            "type": "string",
                            "enum": ["bm25", "vector", "hybrid"],
                            "description": "Search mode: 'bm25' for keyword matching, 'vector' for semantic search, 'hybrid' for combined (default: 'hybrid')",
                            "default": "hybrid"
                        },
                        "bm25_weight": {
                            "type": "number",
                            "description": "BM25 weight for hybrid search (default: 0.5, range: 0-1)",
                            "default": 0.5
                        },
                        "vector_weight": {
                            "type": "number",
                            "description": "Vector weight for hybrid search (default: 0.5, range: 0-1)",
                            "default": 0.5
                        },
                        "authors": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter by author names (e.g., ['John Doe'])"
                        },
                        "min_citation": {
                            "type": "integer",
                            "description": "Minimum citation count filter"
                        },
                        "date_from": {
                            "type": "string",
                            "description": "Publication date from (format: YYYY-MM-DD)"
                        },
                        "date_to": {
                            "type": "string",
                            "description": "Publication date to (format: YYYY-MM-DD)"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "load_paper",
                "description": "Load a paper's metadata and structure. This must be called before reading sections or getting full content. Returns paper title, abstract, authors, available sections with TLDRs.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "arxiv_id": {
                            "type": "string",
                            "description": "The arXiv ID of the paper (e.g., '2503.04975')"
                        }
                    },
                    "required": ["arxiv_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "read_section",
                "description": "Read the full content of a specific section from a loaded paper. Use this when you need detailed information beyond the section TLDR. The section_name must match one of the available sections shown in the paper metadata.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "arxiv_id": {
                            "type": "string",
                            "description": "The arXiv ID of the paper (e.g., '2503.04975')"
                        },
                        "section_name": {
                            "type": "string",
                            "description": "The exact name of the section to read (must match section names from paper metadata, e.g., 'Introduction', 'Method', 'Results')"
                        }
                    },
                    "required": ["arxiv_id", "section_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_full_paper",
                "description": "Get the complete full text of a paper in markdown format. This includes ALL sections and content. Use this when you need to analyze the entire paper comprehensively or when multiple sections are needed. Note: This may return a very large amount of text.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "arxiv_id": {
                            "type": "string",
                            "description": "The arXiv ID of the paper (e.g., '2503.04975')"
                        }
                    },
                    "required": ["arxiv_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_paper_preview",
                "description": "Get a preview of the paper with limited tokens. Good for quick overview without loading the full paper.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "arxiv_id": {
                            "type": "string",
                            "description": "The arXiv ID of the paper (e.g., '2503.04975')"
                        }
                    },
                    "required": ["arxiv_id"]
                }
            }
        }
    ]


class ToolExecutor:
    """Executor for agent tools."""

    def __init__(self, reader):
        """
        Initialize the tool executor.

        Args:
            reader: Reader instance for API access
        """
        self.reader = reader

    def search_papers(
        self,
        query: str,
        size: int = 10,
        offset: int = 0,
        search_mode: str = "hybrid",
        bm25_weight: float = 0.5,
        vector_weight: float = 0.5,
        authors: Optional[List[str]] = None,
        min_citation: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        state_cache: Dict = None
    ) -> str:
        """
        Search for papers with advanced filtering.

        Args:
            query: Search query
            size: Number of results to return
            offset: Result offset for pagination
            search_mode: Search mode ('bm25', 'vector', or 'hybrid')
            bm25_weight: BM25 weight for hybrid search
            vector_weight: Vector weight for hybrid search
            authors: Filter by author names
            min_citation: Minimum citation count
            date_from: Publication date from (YYYY-MM-DD)
            date_to: Publication date to (YYYY-MM-DD)
            state_cache: State cache for storing results

        Returns:
            Formatted search results
        """
        # Build search parameters
        search_params = {
            "size": size,
            "offset": offset,
            "search_mode": search_mode,
        }

        # Add hybrid search weights if applicable
        if search_mode == "hybrid":
            search_params["bm25_weight"] = bm25_weight
            search_params["vector_weight"] = vector_weight

        # Add optional filters
        if authors:
            search_params["authors"] = authors
        if min_citation is not None:
            search_params["min_citation"] = min_citation
        if date_from:
            search_params["date_from"] = date_from
        if date_to:
            search_params["date_to"] = date_to

        # Execute search
        results = self.reader.search(query=query, **search_params)

        if not results:
            return f"Error: Failed to search for papers with query '{query}'."

        # Cache results
        if state_cache is not None:
            state_cache["search_results"] = results

        # Format results
        total = results.get("total", 0) if isinstance(results, dict) else len(results)
        result_list = results.get("results", results) if isinstance(results, dict) else results

        output = [f"=== Search Results for '{query}' ==="]
        output.append(f"Total: {total} papers found | Showing: {len(result_list)} results")
        output.append(f"Mode: {search_mode.upper()}")

        # Show active filters
        filters = []
        if authors:
            # Handle authors as both list and str
            auth_str = ', '.join(authors) if isinstance(authors, list) else str(authors)
            filters.append(f"Authors: {auth_str}")
        if min_citation is not None:
            filters.append(f"Min Citations: {min_citation}")
        if date_from or date_to:
            date_range = f"{date_from or '*'} to {date_to or '*'}"
            filters.append(f"Date Range: {date_range}")

        if filters:
            output.append(f"Filters: {' | '.join(filters)}")

        output.append("")

        for i, paper in enumerate(result_list, offset + 1):
            arxiv_id = paper.get("arxiv_id", "Unknown")
            title = paper.get("title", "No title")
            abstract = paper.get("abstract", "No abstract")[:300]
            score = paper.get("score", 0)
            citation = paper.get("citation", 0)
            paper_categories = paper.get("categories", [])

            output.append(f"{i}. {title}")
            output.append(f"   arXiv ID: {arxiv_id} | Score: {score:.3f} | Citations: {citation}")

            if paper_categories:
                # Handle categories as both list and str
                if isinstance(paper_categories, list):
                    categories_str = ', '.join(paper_categories[:3])
                else:
                    categories_str = str(paper_categories)
                output.append(f"   Categories: {categories_str}")

            output.append(f"   Abstract: {abstract}...")
            output.append("")

        return "\n".join(output)

    def load_paper(
        self,
        arxiv_id: str,
        state_papers: Dict
    ) -> str:
        """
        Load a paper's metadata.

        Args:
            arxiv_id: arXiv ID
            state_papers: Papers dict in state

        Returns:
            Formatted paper information
        """
        # Check if already loaded
        if arxiv_id in state_papers:
            paper = state_papers[arxiv_id]
            return f"Paper {arxiv_id} is already loaded: {paper['title']}"

        # Load paper
        head_info = self.reader.head(arxiv_id)

        if not head_info:
            return f"Error: Failed to load paper {arxiv_id}."

        # Store in state (handle None values)
        state_papers[arxiv_id] = {
            "arxiv_id": arxiv_id,
            "title": head_info.get("title", ""),
            "abstract": head_info.get("abstract", ""),
            "authors": head_info.get("authors") or [],
            "sections": head_info.get("sections") or {},
            "token_count": head_info.get("token_count", 0),
            "categories": head_info.get("categories") or [],
            "publish_at": head_info.get("publish_at", ""),
            "loaded_sections": {}
        }

        # Format output
        paper = state_papers[arxiv_id]
        output = [f"=== Paper Loaded: {arxiv_id} ===\n"]
        output.append(f"Title: {paper['title']}")

        # Handle authors - could be list of dicts, list of strings, or a single string
        authors = paper['authors']
        if isinstance(authors, str):
            # Split comma-separated string into list
            authors = [a.strip() for a in authors.split(',') if a.strip()]

        output.append(f"\nAuthors ({len(authors)} total):")
        for i, author in enumerate(authors[:5], 1):
            # Handle both dict and str formats
            if isinstance(author, dict):
                name = author.get('name', 'Unknown')
                orgs = author.get('orgs', [])
                # Handle orgs as both list and str
                if isinstance(orgs, list):
                    orgs_str = ', '.join(orgs) if orgs else 'N/A'
                else:
                    orgs_str = str(orgs) if orgs else 'N/A'
                output.append(f"  {i}. {name} ({orgs_str})")
            else:
                # author is a string
                output.append(f"  {i}. {author}")

        if len(authors) > 5:
            output.append(f"  ... and {len(authors) - 5} more authors")

        # Handle categories as both list and str
        categories = paper['categories']
        if isinstance(categories, list):
            categories_str = ', '.join(categories) if categories else 'N/A'
        else:
            categories_str = str(categories) if categories else 'N/A'
        output.append(f"\nCategories: {categories_str}")
        output.append(f"Published: {paper.get('publish_at', 'N/A')}")
        output.append(f"\nAbstract:\n{paper['abstract']}\n")

        # Show section TLDRs
        sections = paper.get("sections") or {}
        if sections:
            output.append("Available Sections (with TLDRs):")
            sorted_sections = sorted(sections.items(), key=lambda x: x[1].get("idx", 999))
            for section_name, section_info in sorted_sections:
                tldr = section_info.get('tldr', 'N/A')
                tokens = section_info.get('token_count', 0)
                output.append(f"  - {section_name} ({tokens} tokens):")
                output.append(f"    {tldr}")
        else:
            output.append("Note: Section information not available for this paper.")

        output.append(f"\nTotal paper tokens: {paper['token_count']}")

        return "\n".join(output)

    def read_section(
        self,
        arxiv_id: str,
        section_name: str,
        state_papers: Dict,
        sections_cache: Dict
    ) -> str:
        """
        Read a specific section from a paper.

        Args:
            arxiv_id: arXiv ID
            section_name: Name of the section
            state_papers: Papers dict in state
            sections_cache: Cache for loaded sections

        Returns:
            Section content or error message
        """
        # Check if paper is loaded
        if arxiv_id not in state_papers:
            return f"Error: Paper {arxiv_id} is not loaded. Please use load_paper first."

        paper = state_papers[arxiv_id]

        # Check if sections are available
        sections = paper.get("sections") or {}
        if not sections:
            return f"Error: Section information is not available for paper {arxiv_id}. This paper may not have structured sections."

        # Check if section exists
        if section_name not in sections:
            available = ", ".join(sections.keys())
            return f"Error: Section '{section_name}' not found in paper {arxiv_id}. Available sections: {available}"

        # Check cache
        if arxiv_id in sections_cache and section_name in sections_cache[arxiv_id]:
            content = sections_cache[arxiv_id][section_name]
            return f"=== Section: {section_name} (Paper: {arxiv_id}) ===\n\n{content}\n\n=== End of Section ==="

        # Fetch section
        content = self.reader.section(arxiv_id, section_name)

        if not content:
            return f"Error: Failed to fetch section '{section_name}' from paper {arxiv_id}."

        # Cache it
        if arxiv_id not in sections_cache:
            sections_cache[arxiv_id] = {}
        sections_cache[arxiv_id][section_name] = content

        # Also update paper's loaded_sections
        paper["loaded_sections"][section_name] = content

        return f"=== Section: {section_name} (Paper: {arxiv_id}) ===\n\n{content}\n\n=== End of Section ==="

    def get_full_paper(
        self,
        arxiv_id: str,
        state_papers: Dict,
        full_paper_cache: Dict
    ) -> str:
        """
        Get the full paper content.

        Args:
            arxiv_id: arXiv ID
            state_papers: Papers dict in state
            full_paper_cache: Cache for full paper content

        Returns:
            Full paper content or error message
        """
        # Check if paper is loaded
        if arxiv_id not in state_papers:
            return f"Error: Paper {arxiv_id} is not loaded. Please use load_paper first."

        # Check cache
        if arxiv_id in full_paper_cache:
            content = full_paper_cache[arxiv_id]
            return f"=== Full Paper: {arxiv_id} ===\n\n{content}\n\n=== End of Full Paper ==="

        # Fetch full paper
        content = self.reader.raw(arxiv_id)

        if not content:
            return f"Error: Failed to fetch full paper content for {arxiv_id}."

        # Cache it
        full_paper_cache[arxiv_id] = content

        return f"=== Full Paper: {arxiv_id} ===\n\n{content}\n\n=== End of Full Paper ==="

    def get_paper_preview(
        self,
        arxiv_id: str,
    ) -> str:
        """
        Get a preview of the paper.

        Args:
            arxiv_id: arXiv ID
            max_tokens: Maximum tokens to return

        Returns:
            Paper preview or error message
        """
        preview = self.reader.preview(arxiv_id)

        if not preview:
            return f"Error: Failed to fetch preview for {arxiv_id}."

        output = [f"=== Preview: {arxiv_id} ===\n"]
        output.append(preview.get("content", "No content available"))
        output.append("\n=== End of Preview ===")

        return "\n".join(output)

    def execute_tool_call(
        self,
        tool_name: str,
        tool_args: Dict,
        state: Dict
    ) -> str:
        """
        Execute a single tool call.

        Args:
            tool_name: Name of the tool
            tool_args: Arguments for the tool
            state: Current agent state

        Returns:
            Tool execution result
        """
        try:
            if tool_name == "search_papers":
                query = tool_args.get("query", "")
                size = tool_args.get("size", 10)
                offset = tool_args.get("offset", 0)
                search_mode = tool_args.get("search_mode", "hybrid")
                bm25_weight = tool_args.get("bm25_weight", 0.5)
                vector_weight = tool_args.get("vector_weight", 0.5)
                authors = tool_args.get("authors")
                min_citation = tool_args.get("min_citation")
                date_from = tool_args.get("date_from")
                date_to = tool_args.get("date_to")

                return self.search_papers(
                    query=query,
                    size=size,
                    offset=offset,
                    search_mode=search_mode,
                    bm25_weight=bm25_weight,
                    vector_weight=vector_weight,
                    authors=authors,
                    min_citation=min_citation,
                    date_from=date_from,
                    date_to=date_to,
                    state_cache=state
                )

            elif tool_name == "load_paper":
                arxiv_id = tool_args.get("arxiv_id", "")
                return self.load_paper(arxiv_id, state["papers"])

            elif tool_name == "read_section":
                arxiv_id = tool_args.get("arxiv_id", "")
                section_name = tool_args.get("section_name", "")
                return self.read_section(
                    arxiv_id,
                    section_name,
                    state["papers"],
                    state["paper_sections_cache"]
                )

            elif tool_name == "get_full_paper":
                arxiv_id = tool_args.get("arxiv_id", "")
                return self.get_full_paper(
                    arxiv_id,
                    state["papers"],
                    state["full_paper_cache"]
                )

            elif tool_name == "get_paper_preview":
                arxiv_id = tool_args.get("arxiv_id", "")
                return self.get_paper_preview(arxiv_id)

            else:
                return f"Error: Unknown tool '{tool_name}'"

        except Exception as e:
            return f"Error executing {tool_name}: {e}"


def format_paper_context(papers: Dict[str, Dict]) -> str:
    """
    Format loaded papers for context.

    Args:
        papers: Dictionary of loaded papers

    Returns:
        Formatted context string
    """
    if not papers:
        return "No papers have been loaded yet."

    context_parts = ["=== Loaded Papers ===\n"]

    for arxiv_id, paper in papers.items():
        context_parts.append(f"## Paper: {arxiv_id}")
        context_parts.append(f"Title: {paper['title']}")
        context_parts.append(f"Abstract: {paper['abstract'][:200]}...")
        context_parts.append("")

    return "\n".join(context_parts)
