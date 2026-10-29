import { useEffect, useRef, useState } from "react";
import { getGreeting, getMenu, sendMessage } from "./api";
import Menu from "./Menu";

export default function App() {
  const [sessionId, setSessionId] = useState(() => crypto.randomUUID());
  const [messages, setMessages] = useState([]);
  const [menu, setMenu] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    getMenu().then(setMenu).catch(() => setMenu([]));
  }, []);

  // new session = fresh greeting
  useEffect(() => {
    getGreeting()
      .then((data) => setMessages([{ role: "bot", text: data.reply }]))
      .catch(() => setMessages([{ role: "bot", text: "Can't reach the server. Is the backend running?" }]));
  }, [sessionId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function send(text) {
    if (!text.trim() || loading) return;

    setMessages((prev) => [...prev, { role: "user", text }]);
    setInput("");
    setLoading(true);

    try {
      const data = await sendMessage(sessionId, text);
      setMessages((prev) => [...prev, { role: "bot", text: data.reply }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "bot", text: err.message, error: true }]);
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(e) {
    e.preventDefault();
    send(input);
  }

  return (
    <div className="app">
      <Menu items={menu} onPick={(name) => setInput((prev) => (prev ? `${prev}, ${name}` : `I'd like ${name}`))} />

      <main className="chat">
        <header>
          <h1>Waiter Bot</h1>
          <button className="link" onClick={() => setSessionId(crypto.randomUUID())}>
            New chat
          </button>
        </header>

        <div className="messages">
          {messages.map((m, i) => (
            <div key={i} className={`msg ${m.role} ${m.error ? "error" : ""}`}>
              {m.text}
            </div>
          ))}
          {loading && <div className="msg bot typing">typing...</div>}
          <div ref={bottomRef} />
        </div>

        <form onSubmit={handleSubmit}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about the menu or place an order..."
            autoFocus
          />
          <button type="submit" disabled={loading || !input.trim()}>
            Send
          </button>
        </form>
      </main>
    </div>
  );
}
