# Multi-Agent AI Customer Support Assistant

Status: **scaffold / blank-bucket build.** Every wire is real and verifiable.
Feature logic (real intent classification, real agent reasoning beyond
generic RAG+LLM, real escalation/admin features) is intentionally left as
placeholders — see "Buckets" below for exactly what's stubbed and where.

LLM: **Groq (free tier, hosts Llama 3)**. The app runs fully without a key
(stub mode) — add `GROQ_API_KEY` to `backend/.env` whenever you're ready,
nothing else changes.

---

## What's real vs. what's a bucket

| Component | Status |
|---|---|
| FastAPI app, routing, CORS | Real |
| Auth (register/login/JWT) | Real |
| Conversation memory (Mongo + in-memory fallback) | Real |
| RAG pipeline (chunking, embeddings, FAISS) | Real, just needs PDFs in `/knowledge_base` |
| Pipeline wiring (intent → router → agent → RAG → aggregator → memory) | Real |
| Trace/verification system | Real |
| Intent classification logic | **Bucket** — simple keyword match placeholder |
| Agent routing rules | **Bucket** — simple intent→agent map (multi-agent example from the doc is real) |
| Agent "reasoning" beyond generic RAG+LLM | **Bucket** — all 5 agents currently share generic behavior |
| LLM calls | **Bucket** — stub mode until `GROQ_API_KEY` is set |
| Frontend pages (chat, login, register) | Real, functional UI |
| Escalation, admin KB upload, analytics dashboard | **Not built** — bonus items per the build checklist, not started |

Every bucket is marked with a `# --- BUCKET START/END ---` comment in code.

---

## Project Structure

```
customer-support-ai/
├── frontend/              Next.js + Tailwind chat UI
├── backend/
│   ├── main.py             FastAPI entrypoint
│   ├── api/                /chat, /auth, /conversations routes
│   ├── agents/              intent detection, router, 5 specialized agents, aggregator
│   ├── rag/                 chunking, embeddings, FAISS vectorstore, ingest script
│   ├── core/                 config, LLM client (Groq), trace/verification
│   ├── auth/                 JWT utilities
│   ├── database/             Mongo + in-memory fallback
│   └── tests/                integration verification suite
├── knowledge_base/          put your company PDFs here (currently empty)
├── datasets/                download scripts for all 5 required datasets
└── render.yaml              backend deployment config
```

---

## Quickstart

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # leave GROQ_API_KEY and MONGO_URI empty for now
uvicorn main:app --reload
```

Verify the wiring (this is the answer to "how do we know everything is
integrated correctly" — run this before touching any feature logic):

```bash
pytest tests/test_integration.py -v
```

All 7 tests check that input flows through every required stage and calls
the right function — not whether any agent's answer is "good" yet (that
needs a real Groq key).

Once you have PDFs in `/knowledge_base`:

```bash
python rag/ingest.py
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Visit `http://localhost:3000` — register, log in, chat. Try:
- `"I was charged twice on my invoice"` → routes to Billing
- `"I can't log in, password reset isn't working"` → routes to Technical
- `"I paid yesterday but Premium is still locked"` → routes to **both** (multi-agent case from the project doc)

With no Groq key set, every agent response will say `[STUB RESPONSE...]` —
that's expected, it confirms the LLM wiring fired without needing a real key yet.

---

## Adding the Groq key later

1. Get a free key: https://console.groq.com
2. Add to `backend/.env`: `GROQ_API_KEY=your-key-here`
3. Restart the backend. `GET /` will show `"llm_stub_mode": false`.
4. Nothing else changes — same endpoints, same trace structure, just real answers.

---

## Datasets (required per project doc)

All 5 download scripts are in `/datasets/<name>/download.py`. They need real
internet access (not run yet in this build) — run them from your own machine:

| Dataset | Use |
|---|---|
| Banking77 | Benchmark Intent Detection Agent accuracy |
| CFPB Complaints | Realistic complaint phrasing for Complaint Agent test cases |
| DailyDialog | Multi-turn conversation coherence testing |
| SQuAD 2.0 | RAG retrieval/answer-generation evaluation |
| MS MARCO | Stress-test retrieval at larger scale |

---

## Deployment

- **Frontend → Vercel**: `frontend/vercel.json` included. Set `NEXT_PUBLIC_API_URL` env var to your Render backend URL.
- **Backend → Render**: `render.yaml` included at project root (Render's "Blueprint" deploy will pick it up automatically). Set `GROQ_API_KEY`, `MONGO_URI`, and `FRONTEND_ORIGIN` in the Render dashboard once you have them.

---

## Recommended build order from here

1. Run the integration test suite, confirm all green (already done in this scaffold).
2. Add a few PDFs to `/knowledge_base`, run `rag/ingest.py`, confirm retrieval returns real chunks.
3. Add `GROQ_API_KEY`, confirm one agent (FAQ) gives a real, grounded answer.
4. Replace the keyword-matching bucket in `agents/intent_detection.py` with real classification.
5. Refine each agent's behavior beyond generic RAG+LLM as needed.
6. Move to bonus items (escalation, admin dashboard, analytics) only once the above is solid.
