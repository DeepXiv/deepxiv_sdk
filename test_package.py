"""
Test script to verify the package installation and basic functionality.
"""
import sys


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from py1stauthor import Reader
        print("✓ Reader imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Reader: {e}")
        return False
    
    try:
        from py1stauthor import Agent
        print("✓ Agent imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Agent (this is OK if agent dependencies not installed): {e}")
        print("  To use Agent, install with: pip install py1stauthor[all]")
    
    return True


def test_reader_initialization():
    """Test Reader initialization."""
    print("\nTesting Reader initialization...")
    
    try:
        from py1stauthor import Reader
        reader = Reader(token="test_token")
        print("✓ Reader initialized successfully")
        print(f"  Base URL: {reader.base_url}")
        print(f"  Token: {'*' * len(reader.token)}")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize Reader: {e}")
        return False


def test_agent_initialization():
    """Test Agent initialization (if available)."""
    print("\nTesting Agent initialization...")
    
    try:
        from py1stauthor import Reader, Agent
        reader = Reader(token="test_token")
        agent = Agent(
            api_key="test_key",
            model="gpt-4",
            reader=reader
        )
        print("✓ Agent initialized successfully")
        print(f"  Model: {agent.model}")
        print(f"  Max LLM calls: {agent.max_llm_calls}")
        return True
    except ImportError:
        print("⚠ Agent not available (install with: pip install py1stauthor[all])")
        return None
    except Exception as e:
        print(f"✗ Failed to initialize Agent: {e}")
        return False


def test_package_metadata():
    """Test package metadata."""
    print("\nTesting package metadata...")
    
    try:
        import py1stauthor
        print(f"✓ Package version: {py1stauthor.__version__}")
        print(f"  Available exports: {py1stauthor.__all__}")
        return True
    except Exception as e:
        print(f"✗ Failed to get package metadata: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 80)
    print("py1stauthor Package Test Suite")
    print("=" * 80)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Reader Initialization", test_reader_initialization()))
    results.append(("Agent Initialization", test_agent_initialization()))
    results.append(("Package Metadata", test_package_metadata()))
    
    print("\n" + "=" * 80)
    print("Test Results Summary")
    print("=" * 80)
    
    for test_name, result in results:
        if result is True:
            status = "✓ PASS"
        elif result is False:
            status = "✗ FAIL"
        else:
            status = "⚠ SKIP"
        print(f"{status}: {test_name}")
    
    print("\n" + "=" * 80)
    
    failed = sum(1 for _, r in results if r is False)
    if failed > 0:
        print(f"⚠ {failed} test(s) failed")
        sys.exit(1)
    else:
        print("✓ All tests passed (or skipped)")
        sys.exit(0)


if __name__ == "__main__":
    main()
