"""
MCP (Model Context Protocol) server for deepxiv.
Provides tools for searching papers, accessing metadata, and reading content.
"""
import os
import json
import logging
from typing import Optional
from mcp.server.fastmcp import FastMCP
from .reader import Reader, APIError, AuthenticationError, RateLimitError

# Configure logging
logger = logging.getLogger(__name__)

# Create the MCP server
mcp = FastMCP("deepxiv-sdk")

# Create a reader instance with token from environment
_reader = Reader(token=os.environ.get("DEEPXIV_TOKEN"))


def _format_error(error: Exception) -> str:
    """Format an error message for the user."""
    if isinstance(error, AuthenticationError):
        return "❌ Authentication failed. Run 'deepxiv config' to set a valid token."
    elif isinstance(error, RateLimitError):
        return "⚠️  Daily limit reached. Email tommy@chien.io for higher limits."
    elif isinstance(error, APIError):
        return f"❌ API error: {str(error)}"
    else:
        return f"❌ Unexpected error: {str(error)}"


@mcp.tool()
def search_papers(
    query: str,
    size: int = 10,
    search_mode: str = "hybrid",
    categories: Optional[str] = None,
    authors: Optional[str] = None,
    min_citation: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
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
    try:
        if not query or not query.strip():
            return "❌ Search query cannot be empty"

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
            date_to=date_to,
        )

        if not results or not results.get("results"):
            return f"No papers found matching '{query}'. Try different keywords or adjust filters."

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
                cats_str = (
                    ", ".join(paper_cats[:3])
                    if isinstance(paper_cats, list)
                    else str(paper_cats)
                )
                output.append(f"   Categories: {cats_str}")
            output.append(f"   Abstract: {abstract}...")
            output.append("")

        return "\n".join(output)

    except Exception as e:
        logger.error(f"Error in search_papers: {e}")
        return _format_error(e)


@mcp.tool()
def get_paper_brief(arxiv_id: str) -> str:
    """Get brief information about an arXiv paper (quick summary).

    This is perfect for getting a quick overview without loading full metadata.
    Returns title, TLDR, keywords, publication date, and citation count.

    Args:
        arxiv_id: arXiv ID (e.g., "2409.05591", "2503.04975")

    Returns:
        Brief paper information including title, TLDR, keywords, citations
    """
    try:
        if not arxiv_id or not arxiv_id.strip():
            return "❌ arXiv ID cannot be empty"

        brief = _reader.brief(arxiv_id)

        if not brief:
            return f"❌ Paper {arxiv_id} not found. Check the arXiv ID and try again."

        output = [f"📄 Paper: {arxiv_id}\n"]
        output.append(f"📌 Title: {brief.get('title', 'No title')}\n")
        output.append(f"🔗 PDF: {brief.get('src_url', 'N/A')}")
        output.append(f"📅 Published: {brief.get('publish_at', 'N/A')}")
        output.append(f"📈 Citations: {brief.get('citations', 0)}\n")

        # Keywords
        keywords = brief.get("keywords", [])
        if keywords:
            if isinstance(keywords, list):
                output.append(f"🏷️  Keywords: {', '.join(keywords)}\n")
            else:
                output.append(f"🏷️  Keywords: {keywords}\n")

        # TLDR
        tldr = brief.get("tldr", "")
        if tldr:
            output.append(f"💡 TLDR:\n{tldr}")

        return "\n".join(output)

    except Exception as e:
        logger.error(f"Error in get_paper_brief: {e}")
        return _format_error(e)


@mcp.tool()
def get_paper_metadata(arxiv_id: str) -> str:
    """Get metadata and section overview for an arXiv paper.

    Args:
        arxiv_id: arXiv ID (e.g., "2409.05591", "2503.04975")

    Returns:
        Paper metadata including title, authors, abstract, and available sections
    """
    try:
        if not arxiv_id or not arxiv_id.strip():
            return "❌ arXiv ID cannot be empty"

        head = _reader.head(arxiv_id)

        if not head:
            return (
                f"❌ Paper {arxiv_id} not found. Check the arXiv ID and try again."
            )

        output = [f"📄 Paper: {arxiv_id}\n"]
        output.append(f"📌 Title: {head.get('title', 'No title')}\n")

        # Authors
        authors = head.get("authors", [])
        if isinstance(authors, str):
            authors = [a.strip() for a in authors.split(",")]

        output.append(f"👥 Authors ({len(authors)} total):")
        for i, author in enumerate(authors[:5], 1):
            if isinstance(author, dict):
                name = author.get("name", "Unknown")
                orgs = author.get("orgs", [])
                orgs_str = (
                    ", ".join(orgs)
                    if isinstance(orgs, list)
                    else str(orgs)
                    if orgs
                    else ""
                )
                output.append(f"  {i}. {name}" + (f" ({orgs_str})" if orgs_str else ""))
            else:
                output.append(f"  {i}. {author}")
        if len(authors) > 5:
            output.append(f"  ... and {len(authors) - 5} more authors")

        # Categories and date
        cats = head.get("categories", [])
        cats_str = ", ".join(cats) if isinstance(cats, list) else str(cats)
        output.append(f"\n📚 Categories: {cats_str}")
        output.append(f"📅 Published: {head.get('publish_at', 'N/A')}")
        output.append(f"📊 Total tokens: {head.get('token_count', 'N/A')}")

        # Abstract
        output.append(f"\n📖 Abstract:\n{head.get('abstract', 'No abstract')}\n")

        # Sections with TLDRs
        sections = head.get("sections", {})
        if sections:
            output.append("📑 Available Sections:")
            if isinstance(sections, dict):
                sorted_sections = sorted(
                    sections.items(), key=lambda x: x[1].get("idx", 999)
                )
                for section_name, section_info in sorted_sections:
                    tldr = section_info.get("tldr", "No summary")
                    tokens = section_info.get("token_count", 0)
                    output.append(f"  - {section_name} ({tokens} tokens)")
                    output.append(f"    💡 {tldr}")
            else:
                # Handle if sections is a list instead of dict
                for section in sections:
                    if isinstance(section, dict):
                        output.append(f"  - {section.get('name', 'Unknown')}")
                    else:
                        output.append(f"  - {section}")

        return "\n".join(output)

    except Exception as e:
        logger.error(f"Error in get_paper_metadata: {e}")
        return _format_error(e)


@mcp.tool()
def get_paper_section(arxiv_id: str, section_name: str) -> str:
    """Get the full content of a specific section from a paper.

    Args:
        arxiv_id: arXiv ID (e.g., "2409.05591")
        section_name: Name of the section (e.g., "Introduction", "Methods", "Conclusion")

    Returns:
        Full section content in markdown format
    """
    try:
        if not arxiv_id or not arxiv_id.strip():
            return "❌ arXiv ID cannot be empty"
        if not section_name or not section_name.strip():
            return "❌ Section name cannot be empty"

        content = _reader.section(arxiv_id, section_name)

        if not content:
            # Try to get available sections
            head = _reader.head(arxiv_id)
            if head:
                sections = head.get("sections", {})
                if isinstance(sections, dict):
                    available = ", ".join(sections.keys()) if sections else "none found"
                else:
                    available = "Unable to list sections"
                return (
                    f"❌ Section '{section_name}' not found in paper {arxiv_id}.\n"
                    f"Available sections: {available}"
                )
            return f"❌ Unable to find section '{section_name}' in paper {arxiv_id}"

        return f"=== {section_name} (Paper: {arxiv_id}) ===\n\n{content}"

    except Exception as e:
        logger.error(f"Error in get_paper_section: {e}")
        return _format_error(e)


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
    try:
        if not arxiv_id or not arxiv_id.strip():
            return "❌ arXiv ID cannot be empty"

        content = _reader.raw(arxiv_id)

        if not content:
            return (
                f"❌ Failed to get full paper {arxiv_id}. "
                "Check the arXiv ID and try again."
            )

        return content

    except Exception as e:
        logger.error(f"Error in get_full_paper: {e}")
        return _format_error(e)


@mcp.tool()
def get_paper_preview(arxiv_id: str) -> str:
    """Get a preview of a paper (first ~10,000 characters).

    Useful for quickly scanning the introduction and getting an overview.

    Args:
        arxiv_id: arXiv ID (e.g., "2409.05591")

    Returns:
        Preview of the paper content
    """
    try:
        if not arxiv_id or not arxiv_id.strip():
            return "❌ arXiv ID cannot be empty"

        preview = _reader.preview(arxiv_id)

        if not preview:
            return (
                f"❌ Failed to get preview for paper {arxiv_id}. "
                "Check the arXiv ID and try again."
            )

        content = preview.get("content", preview.get("preview", ""))
        is_truncated = preview.get("is_truncated", True)
        total_chars = preview.get("total_characters", "unknown")

        result = content
        if is_truncated:
            result += f"\n\n[Preview truncated. Total paper size: {total_chars} characters]"

        return result

    except Exception as e:
        logger.error(f"Error in get_paper_preview: {e}")
        return _format_error(e)


@mcp.tool()
def get_pmc_metadata(pmc_id: str) -> str:
    """Get metadata for a PMC (PubMed Central) paper.

    Args:
        pmc_id: PMC ID (e.g., "PMC544940", "PMC514704")

    Returns:
        PMC paper metadata including title, authors, abstract, DOI, and publication info
    """
    try:
        if not pmc_id or not pmc_id.strip():
            return "❌ PMC ID cannot be empty"

        head = _reader.pmc_head(pmc_id)

        if not head:
            return f"❌ PMC paper {pmc_id} not found. Check the PMC ID and try again."

        output = [f"📄 PMC Paper: {pmc_id}\n"]
        output.append(f"📌 Title: {head.get('title', 'No title')}\n")

        # DOI
        doi = head.get("doi", "N/A")
        output.append(f"🔗 DOI: {doi}\n")

        # Authors
        authors = head.get("authors", [])
        if isinstance(authors, str):
            authors = [a.strip() for a in authors.split(",")]

        output.append(f"👥 Authors ({len(authors)} total):")
        for i, author in enumerate(authors[:10], 1):
            if isinstance(author, dict):
                name = author.get("name", "Unknown")
                output.append(f"  {i}. {name}")
            else:
                output.append(f"  {i}. {author}")
        if len(authors) > 10:
            output.append(f"  ... and {len(authors) - 10} more authors")

        # Categories and date
        cats = head.get("categories", [])
        if cats:
            cats_str = ", ".join(cats) if isinstance(cats, list) else str(cats)
            output.append(f"\n📚 Categories: {cats_str}")
        output.append(f"📅 Published: {head.get('publish_at', 'N/A')}")

        # Abstract
        abstract = head.get("abstract", "No abstract")
        output.append(f"\n📖 Abstract:\n{abstract}")

        return "\n".join(output)

    except Exception as e:
        logger.error(f"Error in get_pmc_metadata: {e}")
        return _format_error(e)


@mcp.tool()
def get_pmc_full(pmc_id: str) -> str:
    """Get the complete full content of a PMC paper in JSON format.

    Note: This may return a large amount of data.
    Consider using get_pmc_metadata first to check the paper info.

    Args:
        pmc_id: PMC ID (e.g., "PMC544940", "PMC514704")

    Returns:
        Full PMC paper content as JSON string
    """
    try:
        if not pmc_id or not pmc_id.strip():
            return "❌ PMC ID cannot be empty"

        content = _reader.pmc_full(pmc_id)

        if not content:
            return (
                f"❌ Failed to get PMC paper {pmc_id}. "
                "Check the PMC ID and try again."
            )

        return json.dumps(content, indent=2)

    except Exception as e:
        logger.error(f"Error in get_pmc_full: {e}")
        return _format_error(e)


def create_server():
    """Create and return the MCP server instance."""
    return mcp


if __name__ == "__main__":
    mcp.run()
