"""
Advanced examples showing more complex Agent usage patterns.
"""
import os
from deepxiv_sdk import Reader, Agent


def example_literature_review():
    """Example: Conducting a literature review on a topic."""
    print("\n" + "=" * 80)
    print("Advanced Example 1: Conducting a Literature Review")
    print("=" * 80)
    
    token = os.getenv("ARXIV_API_TOKEN", "your_api_token_here")
    reader = Reader(token=token)
    
    agent = Agent(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4",
        reader=reader,
        print_process=True,
        max_llm_calls=25,  # More calls for complex tasks
        temperature=0.5  # Lower temperature for more focused responses
    )
    
    answer = agent.query(
        "Conduct a brief literature review on 'self-attention mechanisms in transformers'. "
        "Find at least 3 relevant papers, summarize their contributions, "
        "and identify common themes and differences."
    )
    print(f"\n📝 Literature Review:\n{answer}\n")


def example_methodology_comparison():
    """Example: Comparing methodologies across papers."""
    print("\n" + "=" * 80)
    print("Advanced Example 2: Methodology Comparison")
    print("=" * 80)
    
    token = os.getenv("ARXIV_API_TOKEN", "your_api_token_here")
    reader = Reader(token=token)
    
    agent = Agent(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4",
        reader=reader,
        print_process=False,  # Clean output
        stream=True
    )
    
    # Pre-load some papers
    papers = ["2503.04975", "2410.12345"]  # Replace with actual arXiv IDs
    for paper_id in papers:
        agent.add_paper(paper_id)
    
    answer = agent.query(
        "Compare the methodologies used in the loaded papers. "
        "Focus on their experimental setups, datasets, and evaluation metrics."
    )
    print(f"\n📝 Methodology Comparison:\n{answer}\n")


def example_concept_explanation():
    """Example: Deep dive into a specific concept."""
    print("\n" + "=" * 80)
    print("Advanced Example 3: Concept Explanation from Papers")
    print("=" * 80)
    
    token = os.getenv("ARXIV_API_TOKEN", "your_api_token_here")
    reader = Reader(token=token)
    
    agent = Agent(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        model="deepseek-chat",
        base_url="https://api.deepseek.com",
        reader=reader,
        print_process=True,
        stream=True
    )
    
    answer = agent.query(
        "Explain the concept of 'cross-attention' in transformers. "
        "Find papers that discuss this, read the relevant sections, "
        "and provide a comprehensive explanation with examples."
    )
    print(f"\n📝 Concept Explanation:\n{answer}\n")


def example_trend_analysis():
    """Example: Analyzing research trends."""
    print("\n" + "=" * 80)
    print("Advanced Example 4: Research Trend Analysis")
    print("=" * 80)
    
    token = os.getenv("ARXIV_API_TOKEN", "your_api_token_here")
    reader = Reader(token=token)
    
    agent = Agent(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4",
        reader=reader,
        print_process=False,
        max_tokens=6000  # Allow longer responses
    )
    
    answer = agent.query(
        "Analyze the trends in 'multimodal learning' research over recent papers. "
        "What are the common approaches? What datasets are popular? "
        "What future directions are suggested?"
    )
    print(f"\n📝 Trend Analysis:\n{answer}\n")


def example_related_work():
    """Example: Finding related work for a research topic."""
    print("\n" + "=" * 80)
    print("Advanced Example 5: Finding Related Work")
    print("=" * 80)
    
    token = os.getenv("ARXIV_API_TOKEN", "your_api_token_here")
    reader = Reader(token=token)
    
    agent = Agent(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-3.5-turbo",  # Can use cheaper model for simpler tasks
        reader=reader,
        print_process=True
    )
    
    answer = agent.query(
        "I'm working on a project about 'few-shot learning in NLP'. "
        "Find related papers and organize them by approach (e.g., prompt-based, "
        "meta-learning, retrieval-augmented). Suggest which papers I should read first."
    )
    print(f"\n📝 Related Work:\n{answer}\n")


def example_multi_query_session():
    """Example: Interactive multi-query session."""
    print("\n" + "=" * 80)
    print("Advanced Example 6: Multi-Query Interactive Session")
    print("=" * 80)
    
    token = os.getenv("ARXIV_API_TOKEN", "your_api_token_here")
    reader = Reader(token=token)
    
    agent = Agent(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4",
        reader=reader,
        print_process=True,
        stream=True
    )
    
    # Query 1: Initial search
    print("\n[Query 1: Initial Search]")
    answer1 = agent.query("Find papers about graph neural networks for molecular property prediction")
    print(f"\n📝 Answer 1:\n{answer1}\n")
    
    # Query 2: Deep dive into a specific aspect
    print("\n[Query 2: Deep Dive]")
    answer2 = agent.query("What graph convolution operations do these papers use? Explain in detail.")
    print(f"\n📝 Answer 2:\n{answer2}\n")
    
    # Query 3: Practical application
    print("\n[Query 3: Practical Application]")
    answer3 = agent.query("Which of these approaches would be best for drug discovery? Why?")
    print(f"\n📝 Answer 3:\n{answer3}\n")
    
    # Show context
    loaded_papers = agent.get_loaded_papers()
    print(f"\n📚 Papers loaded during session: {len(loaded_papers)}")
    for arxiv_id, paper in loaded_papers.items():
        print(f"  - {arxiv_id}: {paper['title'][:80]}...")


def main():
    """Run all advanced examples."""
    examples = [
        ("Literature Review", example_literature_review),
        ("Methodology Comparison", example_methodology_comparison),
        ("Concept Explanation", example_concept_explanation),
        ("Trend Analysis", example_trend_analysis),
        ("Finding Related Work", example_related_work),
        ("Multi-Query Session", example_multi_query_session),
    ]
    
    print("\n" + "=" * 80)
    print("Advanced Agent Examples")
    print("=" * 80)
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    
    # Run all examples (comment out specific ones if needed)
    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    # Run all examples
    main()
    
    # Or run individual examples:
    # example_literature_review()
    # example_methodology_comparison()
    # example_concept_explanation()
    # example_trend_analysis()
    # example_related_work()
    # example_multi_query_session()
