"""
Basic example of using the Reader class to access arXiv papers.
"""
from py1stauthor import Reader


def main():
    # Initialize the reader with your API token
    token = "your_api_token_here"  # Replace with your actual token
    reader = Reader(token=token)
    
    print("=" * 80)
    print("Example 1: Searching for papers")
    print("=" * 80)
    
    # Search for papers
    query = "agent memory"
    results = reader.search(query, top_k=5)
    
    if results:
        print(f"\nFound {len(results)} papers for '{query}':\n")
        for i, paper in enumerate(results, 1):
            print(f"{i}. {paper.get('title', 'No title')}")
            print(f"   arXiv ID: {paper.get('arxiv_id', 'Unknown')}")
            print(f"   Abstract: {paper.get('abstract', 'No abstract')[:150]}...")
            print()
    else:
        print("No results found or search failed.")
    
    print("\n" + "=" * 80)
    print("Example 2: Getting paper metadata (head)")
    print("=" * 80)
    
    # Get paper head information
    arxiv_id = "2503.04975"  # Replace with a valid arXiv ID
    head_info = reader.head(arxiv_id)
    
    if head_info:
        print(f"\nPaper: {arxiv_id}")
        print(f"Title: {head_info.get('title', 'No title')}")
        print(f"\nAuthors:")
        for i, author in enumerate(head_info.get('authors', [])[:5], 1):
            name = author.get('name', 'Unknown')
            orgs = ', '.join(author.get('orgs', []))
            print(f"  {i}. {name} ({orgs})")
        
        print(f"\nCategories: {', '.join(head_info.get('categories', []))}")
        print(f"Published: {head_info.get('publish_at', 'N/A')}")
        print(f"\nAbstract:\n{head_info.get('abstract', 'No abstract')[:300]}...")
        
        print("\nAvailable sections:")
        sections = head_info.get('sections', {})
        for section_name, section_info in sections.items():
            tldr = section_info.get('tldr', 'No TLDR')
            tokens = section_info.get('token_count', 0)
            print(f"  - {section_name} ({tokens} tokens): {tldr[:100]}...")
    else:
        print(f"Failed to load paper {arxiv_id}")
    
    print("\n" + "=" * 80)
    print("Example 3: Reading a specific section")
    print("=" * 80)
    
    # Read a section
    section_name = "Introduction"
    section_content = reader.section(arxiv_id, section_name)
    
    if section_content:
        print(f"\nSection '{section_name}' from paper {arxiv_id}:")
        print(f"{section_content[:500]}...")
    else:
        print(f"Failed to load section '{section_name}'")
    
    print("\n" + "=" * 80)
    print("Example 4: Getting a paper preview")
    print("=" * 80)
    
    # Get preview
    preview = reader.preview(arxiv_id, max_tokens=1000)
    
    if preview:
        print(f"\nPreview of paper {arxiv_id}:")
        print(f"{preview.get('content', 'No content')[:500]}...")
    else:
        print(f"Failed to get preview for {arxiv_id}")
    
    print("\n" + "=" * 80)
    print("Example 5: Getting full paper content")
    print("=" * 80)
    
    # Get full paper (note: this may be very long)
    full_content = reader.raw(arxiv_id)
    
    if full_content:
        print(f"\nFull paper {arxiv_id} (showing first 500 chars):")
        print(f"{full_content[:500]}...")
        print(f"\nTotal length: {len(full_content)} characters")
    else:
        print(f"Failed to get full content for {arxiv_id}")


if __name__ == "__main__":
    main()
