# test_agent.py
from src.agent.core import PersonalAIAgent

def main():
    agent = PersonalAIAgent()
    # This query should trigger the QueryDailyLogs tool
    question = "What did I work on for my career in the last 8 weeks, and what should I focus on next according to the latest industry trends?"
    response = agent.process_query(question)
    print("Agent response:")
    print(response)

if __name__ == "__main__":
    main()