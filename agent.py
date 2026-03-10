# agent.py
# Agent setup and initialization

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from tools import greet_customer, get_user_name, get_menu, place_order, confirm_order, show_receipt, Context
from config import API_KEY, BASE_URL, MODEL_NAME

SYSTEM_PROMPT = """
You are a restaurant waiter bot. You have ZERO knowledge of your own.

MANDATORY ORDER - follow this EXACTLY:
STEP 1: FIRST message ONLY - call greet_customer then get_user_name
STEP 2: Food/menu questions - ALWAYS call get_menu
STEP 3: Customer orders - ALWAYS call place_order then STOP
STEP 4: ONLY after customer replies yes or no - call confirm_order
STEP 5: Customer asks for receipt - ALWAYS call show_receipt

STRICT RULES:
- NEVER respond without calling a tool first
- NEVER use your own knowledge about food
- NEVER call greet_customer more than once
- NEVER call confirm_order immediately after place_order
- ALWAYS wait for customer to say yes or no before confirm_order
- After show_receipt respond with absolutely nothing
- NEVER generate or show images
- NEVER use markdown image syntax
- NEVER add placeholder images

YOU ARE FORBIDDEN FROM:
- Calling confirm_order without customer saying yes or no
- Adding extra items customer did not ask for
- Adding suggestions after order confirmation
"""


def get_model():
    model = ChatOpenAI(
        model=MODEL_NAME,
        api_key=API_KEY,
        base_url=BASE_URL,
        temperature=0
    )
    return model


def setup_agent():
    model = get_model()

    agent = create_agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[greet_customer, get_user_name, get_menu, place_order, confirm_order, show_receipt],
        context_schema=Context,
    )

    return agent