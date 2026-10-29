# tools.py
# All tool functions for the restaurant agent

import re
import json
from datetime import datetime
from dataclasses import dataclass
from langchain.tools import tool, ToolRuntime
from menu_loader import read_menu, build_vector_store
from config import ORDERS_FILE, GST_RATE

# load menu once at startup
menu_items = read_menu()
db = build_vector_store(menu_items)

# per-chat state (name, order waiting for yes/no, confirmed order), keyed by session id
sessions = {}

# FAISS returns L2 distance, lower is closer. Above this we treat it as "not on the menu"
MATCH_THRESHOLD = 1.0


@dataclass
class Context:
    session_id: str


def get_session(session_id):
    if session_id not in sessions:
        sessions[session_id] = {"name": None, "pending": None, "order": None}
    return sessions[session_id]


def greet_customer() -> str:
    return "Welcome, I will be your waiter. What's your name?"


def find_item(name):
    # exact name first, then fall back to vector search
    for item in menu_items:
        if item["name"].lower() == name.lower():
            return item

    doc, score = db.similarity_search_with_score(name, k=1)[0]
    if score < MATCH_THRESHOLD:
        return doc.metadata
    return None


def parse_items(items: str):
    # "2 Butter Naan, Dal Makhani" -> [(2, "Butter Naan"), (1, "Dal Makhani")]
    parsed = []
    for part in items.split(","):
        part = part.strip()
        if not part:
            continue
        m = re.match(r"^(\d+)\s*x?\s+(.*)$", part)
        if m:
            parsed.append((int(m.group(1)), m.group(2).strip()))
        else:
            parsed.append((1, part))
    return parsed


@tool
def get_user_name(name: str, runtime: ToolRuntime[Context]) -> str:
    """Call this when the customer tells you their name.
    Pass only the name, e.g. 'Rahul'. If they don't want to share it, pass empty string."""

    session = get_session(runtime.context.session_id)
    if name.strip():
        session["name"] = name.strip()
        return f"Hello {session['name']}, welcome to our restaurant. How can I help you today?"
    return "Hello, welcome to our restaurant. How can I help you today?"


@tool
def get_menu(query: str) -> str:
    """Call this for ANY food or menu related question from the customer.
    This includes dietary needs, ingredients, prices, recommendations,
    or anything else related to food."""

    results = db.similarity_search(query, k=5)
    if not results:
        return "Sorry, I couldn't find any menu items matching your request."

    menu_info = "\n".join(doc.page_content for doc in results)
    return f"Based on our menu:\n{menu_info}"


@tool(return_direct=True)
def place_order(items: str, runtime: ToolRuntime[Context]) -> str:
    """Call this when the customer wants to order food.
    Pass ONLY the items the customer asked for as a comma separated string,
    with quantity in front if they gave one, e.g. '2 Butter Naan, Dal Makhani'.
    Use the exact dish names from the menu."""

    session = get_session(runtime.context.session_id)
    order_lines = []
    not_found = []

    for qty, name in parse_items(items):
        item = find_item(name)
        if item:
            order_lines.append({"name": item["name"], "qty": qty, "price": item["price"]})
        else:
            not_found.append(name)

    if not order_lines:
        return "Sorry, we don't have " + ", ".join(not_found) + " on our menu."

    session["pending"] = order_lines
    summary = ", ".join(f"{line['qty']} x {line['name']}" for line in order_lines)
    reply = f"You are ordering: {summary}."
    if not_found:
        reply += " I couldn't find: " + ", ".join(not_found) + "."
    return reply + " Would you like to confirm? (yes/no)"


@tool(return_direct=True)
def confirm_order(answer: str, runtime: ToolRuntime[Context]) -> str:
    """Call this ONLY when the customer replies yes or no to confirming their order.
    Pass 'yes' or 'no'."""

    session = get_session(runtime.context.session_id)
    if not session["pending"]:
        return "There's no order waiting for confirmation. What would you like to have?"

    if answer.strip().lower() not in ["yes", "y"]:
        session["pending"] = None
        return "Your order has been cancelled. Can I help you with anything else?"

    order = {
        "order_id": datetime.now().strftime("%H%M%S"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "customer": session["name"],
        "items": session["pending"],
        "status": "PENDING STAFF VERIFICATION",
    }

    with open(ORDERS_FILE, "a") as f:
        f.write(json.dumps(order) + "\n")

    session["order"] = order
    session["pending"] = None
    return f"Order ID {order['order_id']} confirmed! Would you like to see your receipt?"


@tool(return_direct=True)
def show_receipt(runtime: ToolRuntime[Context]) -> str:
    """Call this when the customer asks for the receipt or bill,
    or says yes to seeing the receipt."""

    order = get_session(runtime.context.session_id)["order"]
    if not order:
        return "You don't have a confirmed order yet."

    lines = ["===== YOUR RECEIPT =====", f"Order ID: {order['order_id']}", "------------------------"]
    subtotal = 0
    for line in order["items"]:
        amount = line["qty"] * line["price"]
        subtotal += amount
        lines.append(f"{line['qty']} x {line['name']} - Rs.{amount}")

    gst = subtotal * GST_RATE
    lines += [
        "------------------------",
        f"Subtotal: Rs.{subtotal}",
        f"GST 18%:  Rs.{gst:.2f}",
        f"Total:    Rs.{subtotal + gst:.2f}",
        "========================",
        "Thank you for dining with us!",
    ]
    return "\n".join(lines)


def review_orders():
    """Staff uses this to see all pending orders"""
    try:
        with open(ORDERS_FILE, "r") as f:
            orders = [json.loads(line) for line in f if line.strip()]
    except FileNotFoundError:
        return []

    return [o for o in orders if o["status"] == "PENDING STAFF VERIFICATION"]
