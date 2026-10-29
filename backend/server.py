# server.py
# FastAPI backend for the React frontend
# run with: uvicorn server:app --reload

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from agent import setup_agent, ask_agent
from tools import greet_customer, menu_items, review_orders, sessions

app = FastAPI(title="Restaurant Bot")

# needed only when the frontend is hosted on a different domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = setup_agent()


class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.get("/api/greeting")
def greeting():
    return {"reply": greet_customer()}


@app.get("/api/menu")
def menu():
    return menu_items


@app.post("/api/chat")
def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message is empty")

    try:
        reply = ask_agent(agent, req.session_id, req.message)
    except Exception as e:
        print(f"agent error: {e}")
        raise HTTPException(status_code=500, detail="Sorry, something went wrong. Please try again.")

    session = sessions.get(req.session_id, {})
    return {"reply": reply, "order": session.get("order")}


@app.get("/api/orders")
def orders():
    return review_orders()


# in production the built React app is served from here too
dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(dist):
    app.mount("/", StaticFiles(directory=dist, html=True), name="frontend")
