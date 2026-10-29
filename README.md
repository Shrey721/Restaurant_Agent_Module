# Restaurant Bot

AI waiter for an Indian restaurant. You chat in plain English, it answers menu questions using RAG over the menu and takes your order.

- **Frontend:** React (Vite)
- **Backend:** FastAPI
- **Agent:** LangChain `create_agent` with tools, LLM via OpenRouter
- **RAG:** each dish from the Excel menu is embedded with `all-MiniLM-L6-v2` and stored in FAISS

```
backend/
  server.py        FastAPI app (API + serves built frontend)
  agent.py         LLM, system prompt, agent with memory
  tools.py         tools the agent can call (menu search, order, receipt)
  menu_loader.py   reads the Excel menu and builds the FAISS index
  config.py        settings, reads .env
  main.py          terminal version
frontend/
  src/App.jsx      chat UI
  src/Menu.jsx     menu sidebar
  src/api.js       calls to the backend
```

## Run locally

Backend:

```
cd backend
python -m venv venv
venv\Scripts\activate          # mac/linux: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env         # mac/linux: cp .env.example .env, then add your key
uvicorn server:app --reload --port 8000
```

Frontend (new terminal):

```
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

Terminal version still works: `cd backend && python main.py`

## API

| Method | Path | |
|---|---|---|
| GET | /api/greeting | first bot message |
| GET | /api/menu | full menu |
| POST | /api/chat | `{session_id, message}` → `{reply, order}` |
| GET | /api/orders | pending orders for staff |

## Deploy (Docker)

```
docker build -t restaurant-bot .
docker run -p 8000:8000 -e OPENROUTER_API_KEY=your-key restaurant-bot
```

Works on any host that runs a Dockerfile (Render, Railway, Hugging Face Spaces). Set `OPENROUTER_API_KEY` as an environment variable on the host. The embedding model needs around 1GB RAM, so very small free tiers can run out of memory.
