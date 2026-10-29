// empty in dev (vite proxy handles it), set VITE_API_URL if backend is hosted separately
const API_URL = import.meta.env.VITE_API_URL || "";

async function request(path, options) {
  const res = await fetch(API_URL + path, options);
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Request failed");
  return data;
}

export const getGreeting = () => request("/api/greeting");
export const getMenu = () => request("/api/menu");

export const sendMessage = (sessionId, message) =>
  request("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message }),
  });
