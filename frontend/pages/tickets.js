import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import { createTicket, listTickets } from "../services/api";

const STATUS_COLORS = {
  "Under Review": "bg-yellow-100 text-yellow-800",
  "In Progress": "bg-blue-100 text-blue-800",
  "Resolved": "bg-green-100 text-green-800",
};

export default function Tickets() {
  const router = useRouter();
  const [subject, setSubject] = useState("");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }
    refreshTickets();
  }, []);

  function refreshTickets() {
    setLoading(true);
    listTickets()
      .then((data) => setTickets(data))
      .catch(() => setError("Could not load your tickets."))
      .finally(() => setLoading(false));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!subject.trim() || !description.trim() || submitting) return;
    setSubmitting(true);
    setError(null);
    setSuccess(null);
    try {
      const sessionId = typeof window !== "undefined" ? localStorage.getItem("session_id") : null;
      const ticket = await createTicket(subject.trim(), description.trim(), sessionId);
      setSuccess(`Ticket raised — reference number ${ticket.ticket_id}`);
      setSubject("");
      setDescription("");
      refreshTickets();
    } catch (err) {
      if (err.response?.status === 401) {
        setError("Your session expired. Please log in again.");
      } else {
        setError("Could not raise the ticket. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 p-6">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-white">Support Tickets</h1>
            <p className="text-slate-400 text-sm">Raise a new ticket or track existing ones</p>
          </div>
          <button onClick={() => router.push("/")}
            className="text-sm text-slate-300 hover:text-white border border-slate-600 rounded-full px-4 py-2">
            ← Back to Chat
          </button>
        </div>

        {/* Raise a ticket */}
        <div className="bg-white rounded-2xl shadow-2xl p-6 mb-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Raise a new ticket</h2>
          <form onSubmit={handleSubmit} className="space-y-3">
            <input
              type="text"
              placeholder="Subject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              required
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <textarea
              placeholder="Describe your issue..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
              rows={4}
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            />
            {error && <p className="text-xs text-red-600">{error}</p>}
            {success && <p className="text-xs text-green-600">{success}</p>}
            <button
              type="submit"
              disabled={submitting}
              className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg px-5 py-2.5 text-sm font-medium transition-colors"
            >
              {submitting ? "Submitting..." : "Raise Ticket"}
            </button>
          </form>
        </div>

        {/* Ticket history */}
        <div className="bg-white rounded-2xl shadow-2xl p-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Your tickets</h2>
          {loading ? (
            <p className="text-sm text-gray-400">Loading...</p>
          ) : tickets.length === 0 ? (
            <p className="text-sm text-gray-400">You haven't raised any tickets yet.</p>
          ) : (
            <div className="space-y-3">
              {tickets.map((t) => (
                <div key={t.ticket_id} className="border border-gray-100 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-mono text-gray-400">{t.ticket_id}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_COLORS[t.status] || "bg-gray-100 text-gray-700"}`}>
                      {t.status}
                    </span>
                  </div>
                  <p className="font-medium text-gray-800 text-sm">{t.subject}</p>
                  <p className="text-xs text-gray-500 mt-1">{t.description}</p>
                  <p className="text-xs text-gray-400 mt-2">
                    Raised {new Date(t.created_at * 1000).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
