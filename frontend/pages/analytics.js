import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import api from "../services/api";

export default function Analytics() {
  const router = useRouter();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const RENDER = process.env.NEXT_PUBLIC_API_URL;

  useEffect(() => {
    fetch(`${RENDER}/analytics/stats`)
      .then((r) => r.json())
      .then((d) => { setStats(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const agentColors = {
    billing: "#3B82F6",
    technical: "#8B5CF6",
    product: "#10B981",
    complaint: "#EF4444",
    faq: "#F59E0B",
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-white">Analytics Dashboard</h1>
            <p className="text-slate-400 text-sm">TechMart AI Support — Live Stats</p>
          </div>
          <button onClick={() => router.push("/")}
            className="text-sm text-slate-300 hover:text-white border border-slate-600 rounded-full px-4 py-2">
            ← Back to Chat
          </button>
        </div>

        {loading ? (
          <div className="text-center text-slate-400 py-20">Loading stats...</div>
        ) : !stats ? (
          <div className="text-center text-slate-400 py-20">Could not load stats.</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Total Conversations */}
            <div className="bg-white rounded-xl p-6 shadow">
              <p className="text-sm text-gray-500 mb-1">Total Conversations</p>
              <p className="text-4xl font-bold text-blue-600">{stats.total_conversations}</p>
              <p className="text-xs text-gray-400 mt-1">All time</p>
            </div>

            {/* Total Agents Fired */}
            <div className="bg-white rounded-xl p-6 shadow">
              <p className="text-sm text-gray-500 mb-1">Total Agent Calls</p>
              <p className="text-4xl font-bold text-indigo-600">
                {Object.values(stats.agent_usage || {}).reduce((a, b) => a + b, 0)}
              </p>
              <p className="text-xs text-gray-400 mt-1">Across all sessions</p>
            </div>

            {/* Agent Usage Breakdown */}
            <div className="bg-white rounded-xl p-6 shadow md:col-span-2">
              <p className="text-sm font-semibold text-gray-700 mb-4">Agent Usage Breakdown</p>
              {Object.entries(stats.agent_usage || {}).length === 0 ? (
                <p className="text-gray-400 text-sm">No agent data yet.</p>
              ) : (
                <div className="space-y-3">
                  {Object.entries(stats.agent_usage || {})
                    .sort((a, b) => b[1] - a[1])
                    .map(([agent, count]) => {
                      const total = Object.values(stats.agent_usage).reduce((a, b) => a + b, 0);
                      const pct = total > 0 ? Math.round((count / total) * 100) : 0;
                      return (
                        <div key={agent}>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="capitalize font-medium text-gray-700">{agent} Agent</span>
                            <span className="text-gray-500">{count} calls ({pct}%)</span>
                          </div>
                          <div className="w-full bg-gray-100 rounded-full h-2">
                            <div className="h-2 rounded-full transition-all"
                              style={{ width: `${pct}%`, backgroundColor: agentColors[agent] || "#6B7280" }}>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                </div>
              )}
            </div>

            {/* Agents Info */}
            <div className="bg-white rounded-xl p-6 shadow md:col-span-2">
              <p className="text-sm font-semibold text-gray-700 mb-4">Agent Capabilities</p>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {[
                  { name: "Billing", desc: "Payments, invoices, subscriptions", color: "blue" },
                  { name: "Technical", desc: "Login, errors, installation", color: "purple" },
                  { name: "Product", desc: "Features, pricing, comparisons", color: "green" },
                  { name: "Complaint", desc: "Escalations, dissatisfaction", color: "red" },
                  { name: "FAQ", desc: "Policies, shipping, warranty", color: "yellow" },
                ].map((a) => (
                  <div key={a.name} className={`p-3 rounded-lg bg-${a.color}-50 border border-${a.color}-100`}>
                    <p className={`font-semibold text-${a.color}-700 text-sm`}>{a.name}</p>
                    <p className="text-xs text-gray-500 mt-0.5">{a.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
