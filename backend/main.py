# main.py
# Terminal version of the bot. The web version is server.py

import uuid
import textwrap
from agent import setup_agent, ask_agent
from tools import greet_customer


def print_wrapped(text, width=60):
    print("-" * width)
    for line in text.split("\n"):
        print(textwrap.fill(line, width=width) if line.strip() else "")
    print("-" * width)


def main():
    agent = setup_agent()
    session_id = str(uuid.uuid4())
    print(greet_customer())

    while True:
        user_input = input("\nYou: ")

        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye! Have a great day!")
            break

        if not user_input.strip():
            print("Waiter: Please say something!")
            continue

        try:
            print("\nWaiter:")
            print_wrapped(ask_agent(agent, session_id, user_input))
        except Exception as e:
            print("Waiter: Sorry, something went wrong. Please try again.")
            print(f"DEBUG: {e}")


if __name__ == "__main__":
    main()
