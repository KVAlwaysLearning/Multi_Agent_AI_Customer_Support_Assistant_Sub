export default function MessageBubble({ role, text, agentUsed }) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-3`}>
      <div
        className={`max-w-md px-4 py-2 rounded-2xl text-sm whitespace-pre-wrap ${
          isUser ? "bg-blue-600 text-white" : "bg-white border border-gray-200 text-gray-800"
        }`}
      >
        {text}
        {!isUser && agentUsed && (
          <div className="text-xs text-gray-400 mt-1">via {agentUsed}</div>
        )}
      </div>
    </div>
  );
}
