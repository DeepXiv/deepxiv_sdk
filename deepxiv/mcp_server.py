"""
MCP (Model Context Protocol) server for deepxiv.
"""
import os
from mcp.server.fastmcp import FastMCP
from .reader import Reader

# Create the MCP server
mcp = FastMCP("deepxiv")

# Create a reader instance with token from environment
_reader = Reader(token=os.environ.get("DEEPXIV_TOKEN"))


@mcp.tool()
def search_papers(
    query: str,
    size: int = 10,
    search_mode: str = "hybrid",
    categories: str = None,
    authors: str = None,
    min_citation: int = None,
    date_from: str = None,
    date_to: str = None
) -> str:
    """Search for arXiv papers using hybrid search (BM25 + Vector).

    Args:
        query: Search query string (e.g., "agent memory", "transformer attention")
        size: Number of results to return (default: 10, max: 100)
        search_mode: Search mode - "bm25", "vector", or "hybrid" (default: "hybrid")
        categories: Filter by categories, comma-separated (e.g., "cs.AI,cs.CL")
        authors: Filter by authors, comma-separated
        min_citation: Minimum citation count
        date_from: Publication date from (format: YYYY-MM-DD)
        date_to: Publication date to (format: YYYY-MM-DD)

    Returns:
        Formatted search results with paper titles, IDs, and abstracts
    """
    # Parse comma-separated values
    cat_list = [c.strip() for c in categories.split(",")] if categories else None
    auth_list = [a.strip() for a in authors.split(",")] if authors else None

    results = _reader.search(
        query=query,
        size=size,
        search_mode=search_mode,
        categories=cat_list,
        authors=auth_list,
        min_citation=min_citation,
        date_from=date_from,
        date_to=date_to
    )

    if not results:
        return f"No results found for query: {query}"

    total = results.get("total", 0)
    result_list = results.get("results", [])

    output = [f"Found {total} papers for '{query}' (showing {len(result_list)}):\n"]

    for i, paper in enumerate(result_list, 1):
        arxiv_id = paper.get("arxiv_id", "Unknown")
        title = paper.get("title", "No title")
        abstract = paper.get("abstract", "")[:300]
        score = paper.get("score", 0)
        citations = paper.get("citation", 0)
        paper_cats = paper.get("categories", [])

        output.append(f"{i}. {title}")
        output.append(f"   arXiv ID: {arxiv_id}")
        output.append(f"   Score: {score:.3f} | Citations: {citations}")
        if paper_cats:
            cats_str = ", ".join(paper_cats[:3]) if isinstance(paper_cats, list) else str(paper_cats)
            output.append(f"   Categories: {cats_str}")
        output.append(f"   Abstract: {abstract}...")
        output.append("")

    return "\n".join(output)


@mcp.tool()
def get_paper_metadata(arxiv_id: str) -> str:
    """Get metadata and section overview for an arXiv paper.

    Args:
        arxiv_id: arXiv ID (e.g., "2409.05591", "2503.04975")

    Returns:
        Paper metadata including title, authors, abstract, and available sections with TLDRs
    """
    head = _reader.head(arxiv_id)

    if not head:
        return f"Failed to get metadata for paper {arxiv_id}"

    output = [f"Paper: {arxiv_id}\n"]
    output.append(f"Title: {head.get('title', 'No title')}\n")

    # Authors
    authors = head.get("authors", [])
    if isinstance(authors, str):
        authors = [a.strip() for a in authors.split(",")]

    output.append(f"Authors ({len(authors)} total):")
    for i, author in enumerate(authors[:5], 1):
        if isinstance(author, dict):
            name = author.get("name", "Unknown")
            orgs = author.get("orgs", [])
            orgs_str = ", ".join(orgs) if isinstance(orgs, list) else str(orgs) if orgs else ""
            output.append(f"  {i}. {name}" + (f" ({orgs_str})" if orgs_str else ""))
        else:
            output.append(f"  {i}. {author}")
    if len(authors) > 5:
        output.append(f"  ... and {len(authors) - 5} more authors")

    # Categories and date
    cats = head.get("categories", [])
    cats_str = ", ".join(cats) if isinstance(cats, list) else str(cats)
    output.append(f"\nCategories: {cats_str}")
    output.append(f"Published: {head.get('publish_at', 'N/A')}")
    output.append(f"Total tokens: {head.get('token_count', 'N/A')}")

    # Abstract
    output.append(f"\nAbstract:\n{head.get('abstract', 'No abstract')}\n")

    # Sections with TLDRs
    sections = head.get("sections", {})
    if sections:
        output.append("Available Sections:")
        sorted_sections = sorted(sections.items(), key=lambda x: x[1].get("idx", 999))
        for section_name, section_info in sorted_sections:
            tldr = section_info.get("tldr", "No summary")
            tokens = section_info.get("token_count", 0)
            output.append(f"  - {section_name} ({tokens} tokens)")
            output.append(f"    TLDR: {tldr}")

    return "\n".join(output)


@mcp.tool()
def get_paper_section(arxiv_id: str, section_name: str) -> str:
    """Get the full content of a specific section from a paper.

    Args:
        arxiv_id: arXiv ID (e.g., "2409.05591")
        section_name: Name of the section (e.g., "Introduction", "Methods", "Conclusion")

    Returns:
        Full section content in markdown format
    """
    content = _reader.section(arxiv_id, section_name)

    if not content:
        # Try to get available sections
        head = _reader.head(arxiv_id)
        if head:
            sections = head.get("sections", {})
            available = ", ".join(sections.keys()) if sections else "none found"
            return f"Section '{section_name}' not found in paper {arxiv_id}. Available sections: {available}"
        return f"Failed to get section '{section_name}' from paper {arxiv_id}"

    return f"=== {section_name} (Paper: {arxiv_id}) ===\n\n{content}"


@mcp.tool()
def get_full_paper(arxiv_id: str) -> str:
    """Get the complete full text of a paper in markdown format.

    Note: This may return a large amount of text (20k-100k+ tokens).
    Consider using get_paper_metadata first to check the paper size,
    or get_paper_section for specific sections.

    Args:
        arxiv_id: arXiv ID (e.g., "2409.05591")

    Returns:
        Full paper content in markdown format
    """
    content = _reader.raw(arxiv_id)

    if not content:
        return f"Failed to get full content for paper {arxiv_id}"

    return content


@mcp.tool()
def get_paper_preview(arxiv_id: str) -> str:
    """Get a preview of a paper (first ~10,000 characters).

    Useful for quickly scanning the introduction and getting an overview.

    Args:
        arxiv_id: arXiv ID (e.g., "2409.05591")

    Returns:
        Preview of the paper content
    """
    preview = _reader.preview(arxiv_id)

    if not preview:
        return f"Failed to get preview for paper {arxiv_id}"

    content = preview.get("content", preview.get("preview", ""))
    is_truncated = preview.get("is_truncated", True)
    total_chars = preview.get("total_characters", "unknown")

    result = content
    if is_truncated:
        result += f"\n\n[Preview truncated. Total paper size: {total_chars} characters]"

    return result


def create_server():
    """Create and return the MCP server instance."""
    return mcp


if __name__ == "__main__":
    mcp.run()
