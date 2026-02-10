"""
Command-line interface for deepxiv.
"""
import json
import os
import sys
import click
from pathlib import Path
from .reader import Reader

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    # Load from home directory first (global config), then current directory (project config)
    # Later files override earlier ones
    env_paths = [
        Path.home() / ".env",  # Home directory (global)
        Path.cwd() / ".env",   # Current directory (project-specific, can override global)
    ]
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path, override=False)  # Don't override already set env vars
except ImportError:
    # python-dotenv not installed, skip loading .env file
    pass


def get_token(token_option):
    """Get token from option or environment variable."""
    if token_option:
        return token_option
    return os.environ.get("DEEPXIV_TOKEN")


def check_token_and_warn(token):
    """Check if token is configured and warn if not."""
    if not token:
        click.echo("⚠️  Warning: DEEPXIV_TOKEN not configured.", err=True)
        click.echo("   Some features may not work without authentication.\n", err=True)
        click.echo("   Get your free token at: https://data.rag.ac.cn/register", err=True)
        click.echo("   Then configure it with: deepxiv config\n", err=True)
        return False
    return True


def handle_auth_error():
    """Handle authentication errors with helpful message."""
    click.echo("\n❌ Authentication failed (401 Unauthorized)\n", err=True)
    click.echo("Your API token is missing or invalid.\n", err=True)
    click.echo("📝 To get a free token:", err=True)
    click.echo("   1. Visit: https://data.rag.ac.cn/register", err=True)
    click.echo("   2. Register and copy your token", err=True)
    click.echo("   3. Run: deepxiv config\n", err=True)
    click.echo("💡 Or set it directly: export DEEPXIV_TOKEN=your_token", err=True)


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
    # Warn if token not configured
    check_token_and_warn(token)
    
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
        handle_auth_error()
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
@click.option("--head", is_flag=True, help="Get paper metadata (returns JSON)")
@click.option("--brief", "-b", is_flag=True, help="Get brief info (title, TLDR, keywords, citations)")
@click.option("--raw", is_flag=True, help="Get raw markdown content")
def paper(arxiv_id, token, output_format, section, preview, head, brief, raw):
    """Get an arXiv paper by ID.

    Example:
        deepxiv paper 2409.05591
        deepxiv paper 2409.05591 --preview
        deepxiv paper 2409.05591 --brief
        deepxiv paper 2409.05591 --token YOUR_TOKEN
        deepxiv paper 2409.05591 --section Introduction
        deepxiv paper 2409.05591 --head
        deepxiv paper 2409.05591 --raw
    """
    # Warn if token not configured
    check_token_and_warn(token)
    
    reader = Reader(token=token)

    if head:
        # Get paper metadata
        result = reader.head(arxiv_id)
        if not result:
            handle_auth_error()
            sys.exit(1)
        click.echo(json.dumps(result, indent=2))

    elif brief:
        # Get brief information
        result = reader.brief(arxiv_id)
        if not result:
            handle_auth_error()
            sys.exit(1)
        
        if output_format == "json":
            click.echo(json.dumps(result, indent=2))
        else:
            # Pretty print brief info
            click.echo(f"\n📄 {result.get('title', 'No title')}\n")
            click.echo(f"🆔 arXiv: {result.get('arxiv_id', arxiv_id)}")
            click.echo(f"📅 Published: {result.get('publish_at', 'N/A')}")
            click.echo(f"📊 Citations: {result.get('citations', 0)}")
            click.echo(f"🔗 PDF: {result.get('src_url', 'N/A')}")
            
            if result.get('keywords'):
                keywords = result.get('keywords', [])
                if isinstance(keywords, list):
                    click.echo(f"\n🏷️  Keywords: {', '.join(keywords)}")
                else:
                    click.echo(f"\n🏷️  Keywords: {keywords}")
            
            if result.get('tldr'):
                click.echo(f"\n💡 TLDR:\n{result.get('tldr')}\n")

    elif raw:
        # Get raw markdown content
        content = reader.raw(arxiv_id)
        if not content:
            handle_auth_error()
            sys.exit(1)
        click.echo(content)

    elif section:
        # Get specific section
        content = reader.section(arxiv_id, section)
        if not content:
            handle_auth_error()
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
            handle_auth_error()
            sys.exit(1)

        if output_format == "json":
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(result.get("content", result.get("preview", "")))

    elif output_format == "json":
        # Get full JSON
        result = reader.json(arxiv_id)
        if not result:
            handle_auth_error()
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
                handle_auth_error()
                sys.exit(1)
        else:
            click.echo(content)


@main.command()
@click.option("--token", "-t", default=None, help="DEEPXIV_TOKEN to save (if not provided, will prompt)")
@click.option("--global", "-g", "is_global", is_flag=True, default=True, help="Save to home directory (default: True)")
def config(token, is_global):
    """Configure DEEPXIV_TOKEN in .env file.

    Get your free token at: https://data.rag.ac.cn/register

    Example:
        deepxiv config                    # Save to ~/.env (global)
        deepxiv config --token YOUR_TOKEN
        deepxiv config --no-global        # Save to current directory
    """
    # Get token from option or prompt
    if not token:
        click.echo("📝 Get your free token at: https://data.rag.ac.cn/register\n")
        token = click.prompt("Please enter your DEEPXIV_TOKEN", hide_input=True)
    
    if not token or not token.strip():
        click.echo("Error: Token cannot be empty", err=True)
        sys.exit(1)
    
    token = token.strip()
    
    # Determine .env file location
    if is_global:
        env_file = Path.home() / ".env"
    else:
        env_file = Path.cwd() / ".env"
    
    env_line = f"DEEPXIV_TOKEN={token}\n"
    
    # Check if .env file exists
    if env_file.exists():
        # Read existing content
        with open(env_file, "r") as f:
            lines = f.readlines()
        
        # Check if DEEPXIV_TOKEN already exists
        token_exists = False
        for i, line in enumerate(lines):
            if line.strip().startswith("DEEPXIV_TOKEN="):
                lines[i] = env_line
                token_exists = True
                break
        
        # If token doesn't exist, append it
        if not token_exists:
            lines.append(env_line)
        
        # Write back to file
        with open(env_file, "w") as f:
            f.writelines(lines)
        
        action = "updated" if token_exists else "added"
        click.echo(f"✓ DEEPXIV_TOKEN {action} in {env_file}")
    else:
        # Create new .env file
        with open(env_file, "w") as f:
            f.write(env_line)
        click.echo(f"✓ Created {env_file} with DEEPXIV_TOKEN")
    
    click.echo(f"\n✅ Token saved successfully!")
    click.echo(f"   The deepxiv CLI will automatically load it from {env_file}")
    click.echo(f"\n💡 To use in other apps/shells:")
    click.echo(f"   - Run: source {env_file}")
    click.echo(f"   - Or add to ~/.bashrc: export DEEPXIV_TOKEN=your_token")


@main.command()
@click.argument("pmc_id")
@click.option("--token", "-t", default=None, envvar="DEEPXIV_TOKEN", help="API token (or set DEEPXIV_TOKEN env var)")
@click.option("--format", "-f", "output_format", default="json", type=click.Choice(["json"]),
              help="Output format (default: json)")
@click.option("--head", is_flag=True, help="Get PMC paper metadata (returns JSON)")
def pmc(pmc_id, token, output_format, head):
    """Get a PMC (PubMed Central) paper by ID.

    Example:
        deepxiv pmc PMC544940
        deepxiv pmc PMC544940 --head
        deepxiv pmc PMC514704 --token YOUR_TOKEN
    """
    # Warn if token not configured
    check_token_and_warn(token)
    
    reader = Reader(token=token)

    if head:
        # Get PMC paper metadata
        result = reader.pmc_head(pmc_id)
        if not result:
            handle_auth_error()
            sys.exit(1)
        click.echo(json.dumps(result, indent=2))
    else:
        # Get full PMC JSON
        result = reader.pmc_json(pmc_id)
        if not result:
            handle_auth_error()
            sys.exit(1)
        click.echo(json.dumps(result, indent=2))


@main.command()
def help():
    """Show detailed help and usage examples.

    Example:
        deepxiv help
    """
    help_text = """
deepxiv - Access arXiv papers from the command line

CONFIGURATION:
  deepxiv config                    Configure your DEEPXIV_TOKEN

SEARCH:
  deepxiv search "query"            Search for papers
    --limit, -l N                   Number of results (default: 10)
    --mode, -m MODE                 Search mode: bm25, vector, hybrid (default: hybrid)
    --format, -f FORMAT             Output format: text, json (default: text)
    --categories, -c CATS           Filter by categories (e.g., cs.AI,cs.CL)
    --min-citations N               Minimum citation count
    --date-from YYYY-MM-DD          Publication date from
    --date-to YYYY-MM-DD            Publication date to

GET PAPER:
  deepxiv paper ARXIV_ID            Get paper by arXiv ID
    --head                          Get paper metadata (JSON)
    --brief, -b                     Get brief info (title, TLDR, keywords, citations)
    --raw                           Get raw markdown content
    --preview, -p                   Get preview (~10k chars)
    --section, -s NAME              Get specific section
    --format, -f FORMAT             Output format: markdown, json (default: markdown)

GET PMC PAPER:
  deepxiv pmc PMC_ID                Get PMC paper by ID
    --head                          Get PMC paper metadata (JSON)
    --format, -f FORMAT             Output format: json (default: json)

MCP SERVER:
  deepxiv serve                     Start MCP server
    --transport, -t TYPE            Transport type: stdio (default: stdio)

EXAMPLES:
  # Configure token
  deepxiv config

  # Search examples
  deepxiv search "transformer architecture" --limit 5
  deepxiv search "machine learning" --categories cs.AI,cs.LG --min-citations 100
  deepxiv search "quantum computing" --mode vector --format json

  # Get paper examples
  deepxiv paper 2409.05591
  deepxiv paper 2409.05591 --head
  deepxiv paper 2409.05591 --brief
  deepxiv paper 2409.05591 --raw
  deepxiv paper 2409.05591 --preview
  deepxiv paper 2409.05591 --section Introduction

  # Get PMC paper examples
  deepxiv pmc PMC544940
  deepxiv pmc PMC544940 --head
  deepxiv pmc PMC514704

ENVIRONMENT:
  Get your free API token:
    🌐 Register at: https://data.rag.ac.cn/register
  
  Set DEEPXIV_TOKEN via:
    - Config command: deepxiv config (recommended)
    - Environment variable: export DEEPXIV_TOKEN=your_token
    - Command option: --token YOUR_TOKEN

For more information, visit: https://data.rag.ac.cn
"""
    click.echo(help_text)


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
