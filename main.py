import dotenv
dotenv.load_dotenv()

from agent.graph import app
from langchain_core.messages import HumanMessage
import sys

def main():
    print("Inventory Chatbot (type 'exit' to quit)")
    config = {"configurable": {"thread_id": "session-1"}}

    while True:
        question = input("\nYou: ").strip()
        if not question:
            continue
        if question.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        state = {
            "messages": [HumanMessage(content=question)],
            "question": question,
            "sql_query": None,
            "sql_result": None,
            "error": None,
            "revision_count": 0,
        }
        print("Bot: Thinking...", end="", flush=True)
        result = app.invoke(state, config=config)
        sys.stdout.write("\r" + " " * 30 + "\r")
        print(f"\nBot: {result['sql_result']}")


if __name__ == "__main__":
    main()
