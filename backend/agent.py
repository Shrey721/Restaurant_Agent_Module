# agent.py
# Agent setup and initialization

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from tools import show_receipt, place_order, get_user_name, get_menu, confirm_order, Context
from config import API_KEY, BASE_URL, MODEL_NAME

SYSTEM_PROMPT = """
You are a restaurant waiter bot. You have ZERO knowledge of your own about food.
The customer has already been greeted and asked for their name.

WHAT TO DO:
- Customer tells their name - call get_user_name
- Food/menu questions or recommendations - ALWAYS call get_menu, answer only from its result
- Customer orders something - call place_order with the exact dish names from the menu
- Customer says yes or no to confirming the order - call confirm_order
- Customer asks for receipt or bill, or says yes to seeing it - call show_receipt

STRICT RULES:
- NEVER use your own knowledge about food or prices
- NEVER add items the customer did not ask for
- NEVER call confirm_order unless the customer just said yes or no to the order
- Keep replies short and friendly, plain text only, no markdown or images
"""


def get_model():
    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set. Add it to backend/.env")

    return ChatOpenAI(
        model=MODEL_NAME,
        api_key=API_KEY,
        base_url=BASE_URL,
        temperature=0,
    )


def setup_agent():
    # MemorySaver keeps each chat's history in memory, keyed by thread_id
    return create_agent(
        model=get_model(),
        system_prompt=SYSTEM_PROMPT,
        tools=[get_user_name, get_menu, place_order, confirm_order, show_receipt],
        context_schema=Context,
        checkpointer=MemorySaver(),
    )


def ask_agent(agent, session_id, message):
    response = agent.invoke(
        {"messages": [{"role": "user", "content": message}]},
        config={"configurable": {"thread_id": session_id}},
        context=Context(session_id=session_id),
    )
    reply = response["messages"][-1].content
    return reply.strip() if reply else "Sorry, could you rephrase that?"
