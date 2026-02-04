"""
Quick start example - get up and running in minutes.
"""
import os
from deepxiv_sdk import Reader, Agent


def main():
    # Step 1: Set up your API tokens
    ARXIV_TOKEN = os.getenv("ARXIV_API_TOKEN", "your_arxiv_token_here")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_key_here")
    
    # Step 2: Initialize the reader
    reader = Reader(token=ARXIV_TOKEN)
    
    # Step 3: Initialize the agent
    agent = Agent(
        api_key=OPENAI_API_KEY,
        model="gpt-4",
        reader=reader,
        print_process=True,  # See what the agent is thinking
        stream=True  # Stream responses in real-time
    )
    
    # Step 4: Ask a question!
    answer = agent.query("What are the latest papers about large language models?")
    
    print("\n" + "=" * 80)
    print("ANSWER:")
    print("=" * 80)
    print(answer)


if __name__ == "__main__":
    main()
