"""
Example: Proper error handling with deepxiv-sdk.
Demonstrates how to handle different types of errors gracefully.
"""
import os
from deepxiv_sdk import (
    Reader,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    APIError,
)


def main():
    """Demonstrate error handling patterns."""

    print("=" * 80)
    print("Error Handling Examples")
    print("=" * 80)

    # Initialize reader with optional token
    token = os.getenv("DEEPXIV_TOKEN")
    reader = Reader(token=token, max_retries=3)

    # Example 1: Handle search errors
    print("\n1. Searching with error handling:")
    try:
        results = reader.search("agent memory", size=5)
        if results:
            for paper in results.get("results", [])[:3]:
                print(f"  - {paper['title']} ({paper['arxiv_id']})")
        else:
            print("  No results found")
    except RateLimitError:
        print("  ⚠️  Daily limit reached. Try again tomorrow.")
    except AuthenticationError:
        print("  ❌ Authentication failed. Run 'deepxiv config' to set a valid token.")
    except APIError as e:
        print(f"  ❌ API Error: {e}")

    # Example 2: Get paper with error handling
    print("\n2. Getting paper metadata:")
    try:
        paper = reader.head("2409.05591")
        if paper:
            print(f"  Title: {paper.get('title')}")
            print(f"  Authors: {len(paper.get('authors', []))} authors")
            print(f"  Sections: {len(paper.get('sections', {}))}")
    except NotFoundError:
        print("  ❌ Paper not found. Check the arXiv ID.")
    except APIError as e:
        print(f"  ❌ Error: {e}")

    # Example 3: Get section with fallback
    print("\n3. Reading specific section with fallback:")
    try:
        intro = reader.section("2409.05591", "Introduction")
        if intro:
            print(f"  Introduction length: {len(intro)} characters")
            print(f"  First 200 chars: {intro[:200]}...")
    except ValueError as e:
        # Section not found, try alternative approach
        print(f"  Section not found, getting brief instead:")
        try:
            brief = reader.brief("2409.05591")
            print(f"  TLDR: {brief.get('tldr', 'N/A')}")
        except APIError:
            print("  Failed to get alternative content")
    except APIError as e:
        print(f"  ❌ Error: {e}")

    # Example 4: Batch processing with error handling
    print("\n4. Processing multiple papers:")
    arxiv_ids = ["2409.05591", "invalid_id", "2504.21776"]
    successful = 0
    failed = 0

    for arxiv_id in arxiv_ids:
        try:
            brief = reader.brief(arxiv_id)
            if brief:
                print(f"  ✓ {arxiv_id}: {brief.get('title', 'No title')[:50]}")
                successful += 1
            else:
                print(f"  ✗ {arxiv_id}: No data returned")
                failed += 1
        except NotFoundError:
            print(f"  ✗ {arxiv_id}: Not found")
            failed += 1
        except APIError as e:
            print(f"  ✗ {arxiv_id}: {str(e)[:50]}")
            failed += 1

    print(f"\n  Summary: {successful} succeeded, {failed} failed")

    # Example 5: Configuring retry behavior
    print("\n5. Custom retry configuration:")
    reader_with_retries = Reader(
        token=token,
        timeout=120,  # 2 minute timeout
        max_retries=5,  # Up to 5 retries
        retry_delay=1.0,  # Start with 1 second
    )
    print("  Reader configured with:")
    print(f"    - Timeout: {reader_with_retries.timeout}s")
    print(f"    - Max retries: {reader_with_retries.max_retries}")
    print(f"    - Initial retry delay: {reader_with_retries.retry_delay}s")

    # Example 6: Validating input before making requests
    print("\n6. Input validation:")
    test_cases = [
        ("agent memory", "Valid query"),
        ("", "Empty query"),
        ("   ", "Whitespace query"),
    ]

    for query, description in test_cases:
        try:
            if not query or not query.strip():
                raise ValueError("Query cannot be empty")
            print(f"  ✓ {description}: Valid")
        except ValueError as e:
            print(f"  ✗ {description}: {e}")

    print("\n" + "=" * 80)
    print("Error handling examples completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
