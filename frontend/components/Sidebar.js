import { useEffect, useState } from "react";
import { listConversations } from "../services/api";

export default function Sidebar({ activeSessionId, onSelect, onNewChat, refreshKey }) {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listConversations()
      .then((data) => setConversations(data))
      .catch(() => setConversations([]))
      .finally(() => setLoading(false));
  }, [refreshKey]);

  return (
    <div className="w-64 shrink-0 bg-slate-900 text-white flex flex-col h-[85vh] rounded-l-2xl">
      <div className="p-4 border-b border-slate-700">
        <button
          onClick={onNewChat}
          className="w-full bg-blue-600 hover:bg-blue-700 rounded-lg py-2 text-sm font-medium transition-colors"
        >
          + New Chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {loading && (
          <p className="text-xs text-slate-400 p-4">Loading conversations...</p>
        )}

        {!loading && conversations.length === 0 && (
          <p className="text-xs text-slate-400 p-4">
            No conversations yet. Start chatting and it'll show up here.
          </p>
        )}

        {conversations.map((c) => (
          <button
            key={c.session_id}
            onClick={() => onSelect(c.session_id)}
            className={`w-full text-left px-4 py-3 text-sm border-b border-slate-800 hover:bg-slate-800 transition-colors ${
              c.session_id === activeSessionId ? "bg-slate-800" : ""
            }`}
          >
            <p className="truncate font-medium">{c.title}</p>
            <p className="text-xs text-slate-400">{c.message_count} messages</p>
          </button>
        ))}
      </div>
    </div>
  );
}
