# main.py
# Run this file to start the bot

import textwrap #importing textwrap to format agent responses in terminal
from agent import setup_agent #function to setup and return the restaurant agent
from tools import greet_customer, review_orders, Context #importing greet_customer tool and Context schema 
from config import MAX_MESSAGES #config setting for max messages 


def print_wrapped(text, width=60): #warping up text to display chat with agent in proper format in terminal
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

    conversation_history = []
    print(greet_customer())

    # conversation history
    config = {"configurable": {"thread_id": "1"}} #config for agent to maintain conversation history in memory with thread_id 1
    conversation_history = [] #initilizing history list as empty to store conversation with agent in memory
    MAX_MESSAGES = 6 #config setting to limit conversation history to last 6 messages 

    while True: #main loop to interact with agent in terminal until user says exit or quit
        user_input = input("\nYou: ")

        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye! Have a great day!")
            break

        if not user_input.strip():
            print("Waiter: Please say something!")
            continue

        conversation_history.append({"role": "user", "content": user_input}) #adding user input to conversation history for agent context

        if len(conversation_history) > MAX_MESSAGES: #limiting conversation history to last MAX_MESSAGES 
            conversation_history = conversation_history[-MAX_MESSAGES:] 

        try: #invoking agent with conversation history and context, then printing agent response in terminal
            response = agent.invoke(
                {"messages": conversation_history},
                config=config,
                context=Context(Name_User=None, Receipt_User=None)
            )

            message = response['messages'][-1].content #getting last message from agent response to print in terminal
            conversation_history.append({"role": "assistant", "content": message}) #adding agent response to conversation history for context

            if not message or message.strip() == "":  
                print("Waiter: Sorry, could you rephrase that?") #if agent response is empty we ask user to rephrase instead of printing empty 
            else:
                print("\nWaiter:") #or else  we print agent response in terminal with proper formatting 
                print_wrapped(message)

        except Exception as e: #catching any errors during agent invocation and printing error message 
            print("Waiter: Sorry, something went wrong. Please try again.")
            print(f"DEBUG: {e}")




if __name__ == "__main__": #running main function to start the bot when this file is executed
    main()