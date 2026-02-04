"""
Command-line interface for deepxiv.
"""
import json
import os
import sys
import click
from .reader import Reader


def get_token(token_option):
    """Get token from option or environment variable."""
    if token_option:
        return token_option
    return os.environ.get("DEEPXIV_TOKEN")


@click.group()
@click.version_option()
def main():
    """deepxiv - Access arXiv papers from the command line.

    Set token via --token option or DEEPXIV_TOKEN environment variable.
    """
    pass


@main.command()
@click.argument("query")
@click.option("--token", "-t", default=None, envvar="DEEPXIV_TOKEN", help="API token (or set DEEPXIV_TOKEN env var)")
@click.option("--limit", "-l", default=10, help="Number of results to return (default: 10)")
@click.option("--mode", "-m", default="hybrid", type=click.Choice(["bm25", "vector", "hybrid"]),
              help="Search mode (default: hybrid)")
@click.option("--format", "-f", "output_format", default="text", type=click.Choice(["text", "json"]),
              help="Output format (default: text)")
@click.option("--categories", "-c", default=None, help="Filter by categories (comma-separated, e.g., cs.AI,cs.CL)")
@click.option("--min-citations", default=None, type=int, help="Minimum citation count")
@click.option("--date-from", default=None, help="Publication date from (YYYY-MM-DD)")
@click.option("--date-to", default=None, help="Publication date to (YYYY-MM-DD)")
def search(query, token, limit, mode, output_format, categories, min_citations, date_from, date_to):
    """Search for arXiv papers.

    Example:
        deepxiv search "agent memory" --limit 5
        deepxiv search "transformer" --mode bm25 --format json
        deepxiv search "LLM" --token YOUR_TOKEN
    """
    reader = Reader(token=token)

    # Parse categories
    cat_list = None
    if categories:
        cat_list = [c.strip() for c in categories.split(",")]

    results = reader.search(
        query=query,
        size=limit,
        search_mode=mode,
        categories=cat_list,
        min_citation=min_citations,
        date_from=date_from,
        date_to=date_to
    )

    if not results:
        click.echo("No results found or search failed.", err=True)
        sys.exit(1)

    if output_format == "json":
        click.echo(json.dumps(results, indent=2))
    else:
        total = results.get("total", 0)
        result_list = results.get("results", [])

        click.echo(f"\nFound {total} papers for '{query}' (showing {len(result_list)}):\n")

        for i, paper in enumerate(result_list, 1):
            arxiv_id = paper.get("arxiv_id", "Unknown")
            title = paper.get("title", "No title")
            abstract = paper.get("abstract", "")[:200]
            score = paper.get("score", 0)
            citations = paper.get("citation", 0)

            click.echo(f"{i}. {title}")
            click.echo(f"   arXiv: {arxiv_id} | Score: {score:.3f} | Citations: {citations}")
            click.echo(f"   {abstract}...")
            click.echo()


@main.command()
@click.argument("arxiv_id")
@click.option("--token", "-t", default=None, envvar="DEEPXIV_TOKEN", help="API token (or set DEEPXIV_TOKEN env var)")
@click.option("--format", "-f", "output_format", default="markdown", type=click.Choice(["markdown", "json"]),
              help="Output format (default: markdown)")
@click.option("--section", "-s", default=None, help="Get a specific section by name")
@click.option("--preview", "-p", is_flag=True, help="Get only a preview (first ~10k chars)")
def paper(arxiv_id, token, output_format, section, preview):
    """Get an arXiv paper by ID.

    Example:
        deepxiv paper 2409.05591
        deepxiv paper 2409.05591 --preview
        deepxiv paper 2409.05591 --token YOUR_TOKEN
        deepxiv paper 2409.05591 --section Introduction
    """
    reader = Reader(token=token)

    if section:
        # Get specific section
        content = reader.section(arxiv_id, section)
        if not content:
            click.echo(f"Failed to get section '{section}' from paper {arxiv_id}", err=True)
            sys.exit(1)

        if output_format == "json":
            click.echo(json.dumps({"arxiv_id": arxiv_id, "section": section, "content": content}, indent=2))
        else:
            click.echo(f"# {section}\n")
            click.echo(content)

    elif preview:
        # Get preview
        result = reader.preview(arxiv_id)
        if not result:
            click.echo(f"Failed to get preview for paper {arxiv_id}", err=True)
            sys.exit(1)

        if output_format == "json":
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(result.get("content", result.get("preview", "")))

    elif output_format == "json":
        # Get full JSON
        result = reader.json(arxiv_id)
        if not result:
            click.echo(f"Failed to get paper {arxiv_id}", err=True)
            sys.exit(1)
        click.echo(json.dumps(result, indent=2))

    else:
        # Get full markdown
        content = reader.raw(arxiv_id)
        if not content:
            # Try head for metadata
            head = reader.head(arxiv_id)
            if head:
                click.echo(f"# {head.get('title', arxiv_id)}\n")
                click.echo(f"**Authors:** {', '.join([a.get('name', str(a)) if isinstance(a, dict) else str(a) for a in head.get('authors', [])])}\n")
                click.echo(f"**Categories:** {', '.join(head.get('categories', []))}\n")
                click.echo(f"\n## Abstract\n\n{head.get('abstract', 'No abstract')}\n")
                click.echo("\n## Sections\n")
                for name, info in head.get("sections", {}).items():
                    click.echo(f"- {name}: {info.get('tldr', 'No summary')[:100]}...")
            else:
                click.echo(f"Failed to get paper {arxiv_id}", err=True)
                sys.exit(1)
        else:
            click.echo(content)


@main.command()
@click.option("--transport", "-t", default="stdio", type=click.Choice(["stdio"]),
              help="Transport type (default: stdio)")
def serve(transport):
    """Start the MCP server.

    Example:
        deepxiv serve
        deepxiv serve --transport stdio
    """
    try:
        from .mcp_server import create_server
    except ImportError:
        click.echo("MCP server requires the 'mcp' package. Install with: pip install deepxiv[mcp]", err=True)
        sys.exit(1)

    server = create_server()
    server.run(transport=transport)


if __name__ == "__main__":
    main()
