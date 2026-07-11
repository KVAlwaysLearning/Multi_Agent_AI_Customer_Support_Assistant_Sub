import { useState, useEffect } from "react";
import { sendMessage, getHistory } from "../services/api";

function getOrCreateSessionId() {
  if (typeof window === "undefined") return null;
  let id = localStorage.getItem("session_id");
  if (!id) {
    id = `session-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    localStorage.setItem("session_id", id);
  }
  return id;
}

const AGENT_COLORS = {
  billing: "bg-blue-100 text-blue-800",
  technical: "bg-purple-100 text-purple-800",
  product: "bg-green-100 text-green-800",
  complaint: "bg-red-100 text-red-800",
  faq: "bg-yellow-100 text-yellow-800",
};

export default function Chat() {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const id = getOrCreateSessionId();
    setSessionId(id);
    getHistory(id)
      .then((d) => setMessages(d.messages || []))
      .catch(() => {});
  }, []);

  useEffect(() => {
    window.scrollTo(0, document.body.scrollHeight);
  }, [messages, isTyping]);

  async function handleSend(e) {
    e.preventDefault();
    if (!input.trim() || isTyping) return;
    const text = input.trim();
    setInput("");
    setError(null);
    setMessages((p) => [...p, { role: "user", text }]);
    setIsTyping(true);
    try {
      const data = await sendMessage(sessionId, text);
      setMessages((p) => [
        ...p,
        {
          role: "ai",
          text: data.response,
          agent_used: data.agents_used?.join(", "),
          agents: data.agents_used || [],
        },
      ]);
    } catch {
      setError("Could not reach the server. Please try again.");
    } finally {
      setIsTyping(false);
    }
  }

  function handleNew() {
    localStorage.removeItem("session_id");
    setSessionId(getOrCreateSessionId());
    setMessages([]);
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl bg-white rounded-2xl shadow-2xl flex flex-col h-[85vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b bg-gradient-to-r from-blue-600 to-indigo-600 rounded-t-2xl">
          <div>
            <h1 className="text-white font-bold text-lg">TechMart Support</h1>
            <p className="text-blue-100 text-xs">Multi-Agent AI Assistant</p>
          </div>
          <div className="flex gap-2">
            <a href="/analytics" className="text-xs text-blue-100 hover:text-white border border-blue-300 rounded-full px-3 py-1">
              Analytics
            </a>
            <button onClick={handleNew} className="text-xs text-blue-100 hover:text-white border border-blue-300 rounded-full px-3 py-1">
              New Chat
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <div className="text-4xl mb-3">🤖</div>
              <p className="text-gray-500 font-medium">How can I help you today?</p>
              <div className="mt-4 grid grid-cols-2 gap-2 max-w-sm mx-auto">
                {["I was charged twice", "Can't log in", "What's your refund policy?", "Compare your laptops"].map((q) => (
                  <button key={q} onClick={() => { setInput(q); }}
                    className="text-xs text-left p-2 bg-gray-50 hover:bg-gray-100 rounded-lg border text-gray-600">
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-xs lg:max-w-md ${m.role === "user" ? "items-end" : "items-start"} flex flex-col gap-1`}>
                <div className={`px-4 py-3 rounded-2xl text-sm whitespace-pre-wrap ${
                  m.role === "user"
                    ? "bg-blue-600 text-white rounded-br-sm"
                    : "bg-gray-100 text-gray-800 rounded-bl-sm"
                }`}>
                  {m.text}
                </div>
                {m.role === "ai" && m.agents && m.agents.length > 0 && (
                  <div className="flex gap-1 flex-wrap">
                    {m.agents.map((a) => (
                      <span key={a} className={`text-xs px-2 py-0.5 rounded-full font-medium ${AGENT_COLORS[a] || "bg-gray-100 text-gray-700"}`}>
                        {a} agent
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-2xl rounded-bl-sm px-4 py-3">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay:"0ms"}}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay:"150ms"}}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay:"300ms"}}></div>
                </div>
              </div>
            </div>
          )}
        </div>

        {error && <div className="px-4 py-2 text-xs text-red-600 bg-red-50 text-center">{error}</div>}

        {/* Input */}
        <form onSubmit={handleSend} className="flex gap-2 p-4 border-t">
          <input
            className="flex-1 border border-gray-300 rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isTyping}
          />
          <button type="submit" disabled={isTyping || !input.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-5 py-2 rounded-full text-sm font-medium transition-colors">
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
