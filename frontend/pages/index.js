import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import ChatWindow from "../components/ChatWindow";
import MessageInput from "../components/MessageInput";
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

export default function Chat() {
  const router = useRouter();
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const id = getOrCreateSessionId();
    setSessionId(id);
    getHistory(id)
      .then((data) => setMessages(data.messages || []))
      .catch(() => {
        // No history yet, or backend not reachable - not fatal, chat still works.
      });
  }, []);

  async function handleSend(text) {
    setError(null);
    setMessages((prev) => [...prev, { role: "user", text }]);
    setIsTyping(true);
    try {
      const data = await sendMessage(sessionId, text);
      setMessages((prev) => [
        ...prev,
        { role: "ai", text: data.response, agent_used: data.agents_used?.join(", ") },
      ]);
    } catch (e) {
      setError("Couldn't reach the server. Check the backend is running and try again.");
    } finally {
      setIsTyping(false);
    }
  }

  function handleNewConversation() {
    localStorage.removeItem("session_id");
    const id = getOrCreateSessionId();
    setSessionId(id);
    setMessages([]);
  }

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto bg-gray-50 border-x border-gray-200">
      <header className="flex items-center justify-between px-4 py-3 border-b bg-white">
        <h1 className="font-semibold text-gray-800">TechMart Support Assistant</h1>
        <button onClick={handleNewConversation} className="text-xs text-blue-600 hover:underline">
          New conversation
        </button>
      </header>

      <ChatWindow messages={messages} isTyping={isTyping} />

      {error && <div className="px-4 py-2 text-xs text-red-600 bg-red-50">{error}</div>}

      <MessageInput onSend={handleSend} disabled={isTyping || !sessionId} />
    </div>
  );
}
