# tools.py
# All tool functions for the restaurant agent

import re
import json
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from dataclasses import dataclass
from langchain.tools import ToolRuntime
from menu_loader import load_menu

# load menu once
db = load_menu()

# current order id
current_order_id = None


# Context Schema
class Context(BaseModel):
    Name_User: Optional[str] = None
    Receipt_User: Optional[str] = None


def greet_customer() -> str:
    """ALWAYS call this tool first before anything else,
    even before get_user_name. This is the very first thing to run."""

    return "Welcome, I will be your waiter. What's your name?"


def get_user_name(runtime: ToolRuntime[Context]) -> str:
    """Call this tool second, right after greet_customer.
    Extract the name from user message.
    Pass the name if user mentioned it in their message.
    If user said something like 'hello' or 'hi' with no name, pass empty string.
    If user said 'I dont want to share' or similar, pass empty string."""

    name = runtime.context.Name_User
    if name:
        return f"Hello {name}, Welcome to our restaurant. How can I help you today?"
    else:
        return "Hello, Welcome to our restaurant. How can I help you today?"


def get_menu(query: str) -> str:
    """Call this for ANY food or menu related question from the customer.
    This includes dietary needs, ingredients, prices, recommendations,
    or anything else related to food."""

    results = db.similarity_search(query, k=5)

    if not results:
            return "Sorry, I couldn't find any menu items matching your request."
    
    menu_info = "\n".join([doc.page_content for doc in results])

    return f"Based on our menu:\n{menu_info}"
    


def place_order(items: str) -> str:

    """Call this when user wants to order food items.
    ONLY pass items the customer explicitly mentioned.
    NEVER add extra items the customer did not ask for.
    Extract the food items from user message and pass as comma separated string.
    Call this when user says anything like:
    - 'i would like to order'
    - 'i want to order'
    - 'can i get'
    - 'i'll have'
    - 'get me'
    - 'order me'
    After calling this tool STOP and wait for customer to say yes or no.
    NEVER call confirm_order automatically after this tool."""

    return f"You are ordering: {items}. Would you like to confirm? (yes/no)"


def confirm_order(items: str, response: str) -> str:
    """Call this after place_order when customer confirms or denies.
    Pass the same items from place_order.
    Call this when customer says yes or no after being asked to confirm order.
    After calling this tool respond with NOTHING."""

    global current_order_id

  
    if response.lower() == "yes":
            current_order_id = datetime.now().strftime("%H%M%S")

            order = {
                "order_id": current_order_id,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "items": items,
                "status": "PENDING STAFF VERIFICATION"
            }

            with open("orders_log.json", "a") as f:
                f.write(json.dumps(order) + "\n")

            print(f"\nOrder ID: {current_order_id} confirmed! Would you like to see your receipt?")
            return ""
    
    else:
        print("\nYour order has been cancelled. Can I help you with anything else?")
        return ""


def show_receipt(items: str) -> str:
    """Call this when customer asks for receipt or says yes to receipt.
    After calling this tool respond with NOTHING AT ALL.
    Do not add any text after this tool runs."""

    item_list = [item.strip() for item in items.split(",")]
    subtotal = 0
    receipt_lines = []

    for item in item_list:
            results = db.similarity_search(item, k=1)
            item_text = results[0].page_content if results else ""
            match = re.search(r'\b(\d+)\b', item_text)
            price = int(match.group(1)) if match else 0
            subtotal += price
            receipt_lines.append(f"  {item} - Rs.{price}")

    gst = subtotal * 0.18
    total = subtotal + gst

    print("\n===== YOUR RECEIPT =====")
    print(f"Order ID:  {current_order_id}")
    print("------------------------")
    for line in receipt_lines:
            print(line)
    print("------------------------")
    print(f"Subtotal:  Rs.{subtotal}")
    print(f"GST 18%:   Rs.{gst:.2f}")
    print(f"Total:     Rs.{total:.2f}")
    print("========================")
    print("Thank you for dining with us!")

    return ""



def review_orders():
    """Staff runs this to see all pending orders"""
    try:
        with open("orders_log.json", "r") as f:
            orders = [json.loads(line) for line in f.readlines()]

        pending = [o for o in orders if o['status'] == "PENDING STAFF VERIFICATION"]

        if not pending:
            print("No pending orders!")
            return

        print("\n===== PENDING ORDERS =====")
        for order in pending:
            print(f"Order ID: {order['order_id']}")
            print(f"Time:     {order['timestamp']}")
            print(f"Items:    {order['items']}")
            print("---")
        print(f"Total pending: {len(pending)}")

    except FileNotFoundError:
        print("No orders yet!")