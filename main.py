# main.py
# Entry point - run this file to start the bot

import textwrap
from agent import setup_agent
from tools import greet_customer, review_orders, Context
from config import MAX_MESSAGES


def print_wrapped(text, width=60):
    print("-" * width)
    for line in text.split('\n'):
        if line.strip():
            print(textwrap.fill(line, width=width))
        else:
            print()
    print("-" * width)


def main():
    # setup agent
    agent = setup_agent()

    # conversation history
    conversation_history = []
    config = {"configurable": {"thread_id": "1"}}

    # greet customer
    print(greet_customer())

    while True:
        user_input = input("\nYou: ")

        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye! Have a great day!")
            break

        if not user_input.strip():
            print("Waiter: Please say something!")
            continue

        conversation_history.append({"role": "user", "content": user_input})

        if len(conversation_history) > MAX_MESSAGES:
            conversation_history = conversation_history[-MAX_MESSAGES:]

        try:
            response = agent.invoke(
                {"messages": conversation_history},
                config=config,
                context=Context(Name_User=None, Receipt_User=None)
            )

            message = response['messages'][-1].content
            conversation_history.append({"role": "assistant", "content": message})

            if not message or message.strip() == "":
                pass  # tool already printed directly
            else:
                print("\nWaiter:")
                print_wrapped(message)

        except Exception as e:
            print("Waiter: Sorry, something went wrong. Please try again.")
            print(f"DEBUG: {e}")

    # show pending orders for staff review
    review_orders()


if __name__ == "__main__":
    main()