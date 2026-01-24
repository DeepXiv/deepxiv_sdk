"""
Example of using the Agent class for intelligent paper analysis.
"""
import os
from py1stauthor import Reader, Agent


def main():
    # Initialize the reader with your API token
    token = os.getenv("ARXIV_API_TOKEN", "your_api_token_here")
    reader = Reader(token=token)
    
    # Initialize the agent
    # You can use different providers:
    
    # Option 1: OpenAI
    agent = Agent(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4",
        reader=reader,
        print_process=True,  # Show reasoning process
        stream=True,  # Stream responses
        max_llm_calls=15,
        temperature=0.7
    )
    
    # Option 2: DeepSeek (uncomment to use)
    # agent = Agent(
    #     api_key=os.getenv("DEEPSEEK_API_KEY"),
    #     model="deepseek-chat",
    #     base_url="https://api.deepseek.com",
    #     reader=reader,
    #     print_process=True,
    #     stream=True
    # )
    
    # Option 3: OpenRouter (uncomment to use)
    # agent = Agent(
    #     api_key=os.getenv("OPENROUTER_API_KEY"),
    #     model="anthropic/claude-3-opus",
    #     base_url="https://openrouter.ai/api/v1",
    #     reader=reader,
    #     print_process=True
    # )
    
    print("\n" + "=" * 80)
    print("Example 1: Search and analyze papers on a topic")
    print("=" * 80)
    
    answer = agent.query(
        "What are the latest papers about agent memory? "
        "Summarize the key approaches."
    )
    print(f"\n📝 Answer:\n{answer}\n")
    
    print("\n" + "=" * 80)
    print("Example 2: Follow-up question with context")
    print("=" * 80)
    
    answer = agent.query(
        "How do these memory approaches compare in terms of efficiency?"
    )
    print(f"\n📝 Answer:\n{answer}\n")
    
    print("\n" + "=" * 80)
    print("Example 3: Detailed analysis of a specific paper")
    print("=" * 80)
    
    # Manually add a paper
    agent.add_paper("2503.04975")
    
    answer = agent.query(
        "Explain the methodology used in paper 2503.04975 in detail."
    )
    print(f"\n📝 Answer:\n{answer}\n")
    
    print("\n" + "=" * 80)
    print("Example 4: Reset and start a new topic")
    print("=" * 80)
    
    # Reset papers for a new topic
    agent.reset_papers()
    
    answer = agent.query(
        "What are the main components of the transformer architecture? "
        "Find relevant papers and explain."
    )
    print(f"\n📝 Answer:\n{answer}\n")
    
    print("\n" + "=" * 80)
    print("Example 5: Comparison across multiple papers")
    print("=" * 80)
    
    answer = agent.query(
        "Find papers about vision transformers and compare their "
        "architectural differences."
    )
    print(f"\n📝 Answer:\n{answer}\n")
    
    # Show loaded papers
    loaded_papers = agent.get_loaded_papers()
    print(f"\n📚 Currently loaded papers: {len(loaded_papers)}")
    for arxiv_id, paper in loaded_papers.items():
        print(f"  - {arxiv_id}: {paper['title']}")


if __name__ == "__main__":
    main()
