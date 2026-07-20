# Multi-Agent AI Customer Support Assistant

Status: **Fully deployed and operational.** A production multi-agent customer
support system for TechMart Electronics (a fictional company), built end to
end — real LLM-backed intent classification, five specialized agents, a RAG
pipeline grounded in real policy documents, persistent conversation memory,
authenticated ticketing, and a live analytics dashboard.

- **Live app:** https://multi-agent-ai-customer-support-assistant-e4r89t97y.vercel.app
- **Live API:** https://customer-support-ai-backend-sub.onrender.com
- **API docs:** https://customer-support-ai-backend-sub.onrender.com/docs

LLM: **Groq (free tier, hosts Llama 3.1 8B Instant)**. The app also runs fully
without a key in **stub mode** — leave `GROQ_API_KEY` empty in `backend/.env`
for placeholder responses that still exercise every pipeline stage; add it
whenever you're ready and nothing else changes.

---

## What's implemented

| Component | Status |
|---|---|
| FastAPI app, routing, CORS | Real |
| Auth (register/login/JWT, bcrypt hashing) | Real |
| Conversation memory (MongoDB Atlas + in-memory fallback) | Real |
| RAG pipeline (chunking, embeddings, FAISS) | Real — 8 policy documents, 31 chunks indexed |
| Pipeline wiring (intent → router → agent → RAG → aggregator → memory) | Real |
| Trace/verification system | Real — every `/chat` response includes a full stage-by-stage trace |
| Intent classification | Real — LLM-based (Llama 3.1 via Groq) with a keyword-matching fallback if the LLM call fails |
| Agent routing | Real — intent→agent map plus a multi-agent rule (e.g. "paid but still locked" fires **both** Billing and Technical) |
| Agent behavior | Real — each of the 5 agents has its own tailored system prompt and response pattern, not generic shared behavior |
| LLM calls | Real — Groq API live in production; stub mode still available for local dev without a key |
| Frontend pages (chat, login, register, tickets, analytics) | Real, functional UI |
| Ticket system | Real — authenticated `POST`/`GET /tickets`, plus a separate anonymous `POST /escalation/ticket` for quick escalation |
| Analytics dashboard | Real — live conversation stats and per-agent usage from MongoDB aggregation |
| Escalation | Real — keyword-triggered escalation logic inside the Complaint agent |
| Admin KB upload | **Not built** — knowledge base is currently updated by adding files to `/knowledge_base` and re-running the ingest script |

---

## Project Structure

```
customer-support-ai/
├── frontend/                       Next.js + Tailwind chat UI (deployed on Vercel)
│   ├── pages/
│   │   ├── index.js                 Main chat page
│   │   ├── login.js / register.js   Auth forms
│   │   ├── tickets.js                Raise and track support tickets
│   │   └── analytics.js              Live stats dashboard
│   ├── components/                  ChatWindow, MessageBubble, MessageInput,
│   │                                 TypingIndicator, Sidebar
│   └── services/api.js              Single Axios client, all backend calls
├── backend/                        FastAPI backend (deployed on Render)
│   ├── main.py                      Entrypoint, CORS, router registration
│   ├── api/                         /auth, /chat, /tickets, /analytics, /agents routes
│   ├── agents/                      intent detection, router, aggregator, 5 specialized agents
│   ├── rag/                         chunking, embeddings, FAISS vectorstore, ingest script
│   ├── core/                        config, LLM client (Groq), trace/verification
│   ├── auth/                        JWT + bcrypt utilities
│   ├── database/                    MongoDB + in-memory fallback
│   ├── vectorstore_data/            committed FAISS index + chunk metadata
│   └── tests/                       integration verification suite
├── knowledge_base/                  TechMart's policy documents (FAQ, Refund,
│                                     Shipping, Warranty, Pricing, Products,
│                                     Installation Guide, User Manual)
├── datasets/                        download/benchmark scripts for all 5 required datasets
└── render.yaml                      backend deployment blueprint
```

---

## Quickstart (local development)

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # leave GROQ_API_KEY and MONGO_URI empty to run locally in stub mode
uvicorn main:app --reload
```

Verify the wiring:

```bash
pytest tests/test_integration.py -v
```

All 7 tests check that a request flows through every required pipeline stage
and calls the right function.

The FAISS index is already built and committed under `backend/vectorstore_data/`,
so retrieval works out of the box. To rebuild it after changing knowledge base
documents:

```bash
python rag/ingest.py
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local   # set NEXT_PUBLIC_API_URL=http://localhost:8000 for local backend
npm run dev
```

Visit `http://localhost:3000` — register, log in, chat. Try:
- `"I was charged twice on my invoice"` → routes to Billing
- `"I can't log in, password reset isn't working"` → routes to Technical
- `"I paid yesterday but Premium is still locked"` → routes to **both** Billing and Technical (multi-agent case)
- `"How much does the TechMart ProBook cost?"` → routes to Product
- `"I am very disappointed, this is unacceptable"` → routes to Complaint
- `"What are your shipping times and return policy?"` → routes to FAQ

With no Groq key set, agent responses will say `[STUB RESPONSE...]` — that
confirms the LLM wiring fired without needing a real key. On the live
deployment, `GROQ_API_KEY` is set, so every response above comes from a real
Llama 3.1 call.

---

## Adding your own Groq key

1. Get a free key: https://console.groq.com
2. Add to `backend/.env`: `GROQ_API_KEY=your-key-here`
3. Restart the backend. `GET /` will show `"llm_stub_mode": false`.
4. Nothing else changes — same endpoints, same trace structure, just real answers.

---

## Datasets

All 5 download/benchmark scripts live in `/datasets/<name>/`. They need real
internet access — run them from your own machine:

| Dataset | Use |
|---|---|
| Banking77 | Benchmarks Intent Detection agent accuracy (`datasets/banking77/benchmark.py`) |
| CFPB Complaints | Informed complaint phrasing and escalation-keyword design for the Complaint agent |
| DailyDialog | Informed conversation-memory design (context window of 6 messages) |
| SQuAD 2.0 | Reference evaluation methodology for RAG retrieval quality |
| MS MARCO | Reference for the semantic passage-retrieval design in the RAG pipeline |

---

## Deployment

- **Frontend → Vercel**: `frontend/vercel.json` included. `NEXT_PUBLIC_API_URL` is set in the Vercel project's environment variables, pointing at the live Render backend. Every push to the connected GitHub repo redeploys automatically.
- **Backend → Render**: `render.yaml` at the project root is picked up automatically by Render's Blueprint deploy. Environment variables (`GROQ_API_KEY`, `GROQ_MODEL`, `MONGO_URI`, `MONGO_DB_NAME`, `JWT_SECRET`, `FRONTEND_ORIGIN`, `DISABLE_EMBEDDINGS`) are set in the Render dashboard.
- **Database**: MongoDB Atlas (free M0 tier), storing users, conversations, and tickets.

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/` | None | App info and LLM mode status |
| GET | `/health` | None | Health check |
| POST | `/auth/register` | None | Create account, returns JWT |
| POST | `/auth/login` | None | Authenticate, returns JWT |
| POST | `/chat` | Optional | Main pipeline — intent → route → agent → response + trace |
| GET | `/conversations/{session_id}` | Optional | Retrieve conversation history |
| GET | `/analytics/stats` | None | Total conversations and per-agent usage |
| GET | `/analytics/conversations` | None | Recent conversation list (last 50) |
| POST | `/escalation/ticket` | None | Quick anonymous escalation ticket |
| POST | `/tickets` | Required | Raise a support ticket tied to the logged-in user |
| GET | `/tickets` | Required | List the logged-in user's support tickets |
| GET | `/agents` | None | List active agents (used by the analytics dashboard) |

---

## Project history

This repo started as a wiring-first scaffold: real FastAPI/Next.js/Mongo/FAISS
plumbing with intent classification, agent behavior, and LLM calls left as
placeholders so the pipeline's shape could be verified end to end before
investing in any single feature. Since then, the placeholders have been
replaced with real logic (LLM-backed intent classification, five distinctly
prompted agents, a live Groq key), bonus features have been added (ticketing,
analytics dashboard, escalation), and the whole system has been deployed to
Vercel + Render + MongoDB Atlas.
