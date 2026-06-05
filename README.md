# AI Medical Symptom Triage Assistant

A full-stack, production-grade web application where patients describe their symptoms in natural language and an AI system triages urgency, suggests probable conditions, and routes them to the right care tier — Emergency Room, Urgent Care, GP, or Self-care. Doctors get a dashboard to review flagged high-risk or low-confidence cases.

---

## What Problem It Solves

- Reduces unnecessary ER visits by helping patients assess urgency before showing up
- Supports patients in underserved or rural areas who cannot quickly reach a doctor
- Gives clinicians a prioritized queue for remote triage review — only the cases that actually need attention get flagged

---

## Key Features

- **Multi-step RAG reasoning chain** — not a basic chatbot. Retrieves relevant medical guidelines from a vector store before generating a triage decision
- **Hardcoded safety rules** — chest pain, stroke symptoms, suicidal ideation, overdose → always ER, always bypasses the AI
- **Human-in-the-loop doctor review** — every AI decision is reviewable. Doctors can agree, override, and leave notes
- **Auto-flagging** — cases are automatically flagged when urgency is high (ER/Urgent Care) or AI confidence is below 65%
- **HIPAA-compliant audit logging** — append-only log of every action. Never updated or deleted
- **Role-based access** — patient / doctor / admin

---

## How It Works

### The 4-Step AI Pipeline

Every symptom submission runs through four stages in sequence:

```
Patient submits symptoms
        │
        ▼
┌───────────────────┐
│  1. Safety Rules  │  ← Keyword match. No LLM involved.
│  (hardcoded)      │    "chest pain" → immediate ER, pipeline stops
└────────┬──────────┘
         │ (no emergency keyword found)
         ▼
┌───────────────────┐
│  2. Symptom       │  ← Claude API call.
│  Extraction       │    Free text → structured JSON
│                   │    (severity, duration, onset, location…)
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  3. RAG Triage    │  ← LangChain retrieves relevant medical
│  Pipeline         │    guideline chunks from Pinecone, then
│                   │    Claude reasons over them to produce
│                   │    urgency level + conditions + reasoning
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  4. Auto-Flag     │  ← If urgency = ER/Urgent Care OR
│  Logic            │    confidence < 0.65 → flagged for
│                   │    doctor review + notification sent
└───────────────────┘
```

### Why Two Separate Claude Calls?

**Step 2 (extraction)** uses the raw Anthropic SDK — a single structured output call with no retrieval needed.

**Step 3 (triage)** uses LangChain — because retrieval-augmented generation requires a chain that first fetches relevant medical guidelines, then passes them as context to the LLM. The separation means retrieval quality can be improved independently of the prompt.

### Safety Rules First, Always

The safety rule check runs **before any LLM call**. This is intentional — LLMs can hallucinate or get edge cases wrong. For life-threatening keywords (chest pain, stroke, suicidal ideation, overdose, anaphylaxis), the system always escalates to ER with confidence 1.0, no exceptions.

### Confidence Threshold

The AI returns a confidence score (0–1) with every triage decision. Below **0.65**, the case is automatically flagged for doctor review regardless of the urgency level. This threshold is configurable via environment variable.

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Next.js 14 (App Router) + TypeScript | SSR, routing, UI |
| UI Components | Tailwind CSS + shadcn/ui | Styling, accessible components |
| Backend | FastAPI (Python 3.11+) | Async REST API, Pydantic validation |
| AI Orchestration | LangChain + Claude API (`claude-sonnet-4-20250514`) | RAG chains, symptom extraction |
| Vector Store | Pinecone | Semantic search over medical guidelines corpus |
| Primary Database | PostgreSQL 15 + pgvector | Relational data, session storage, audit log |
| Cache / Sessions | Redis 7 | Session tokens, rate limiting |
| Auth | JWT + OAuth2 | RBAC: patient / doctor / admin |
| Notifications | SendGrid (email) + Twilio (SMS) | Doctor alerts on flagged cases |
| Deployment | Docker + Docker Compose | Local dev orchestration |
| CI/CD | GitHub Actions | Test + lint on every push |

---

## Repository Structure

```
ai-medical-triage/
├── frontend/                          # Next.js 14 application
│   ├── app/
│   │   ├── patient/
│   │   │   └── chat/page.tsx          # Symptom intake chat UI
│   │   ├── layout.tsx                 # Root layout, metadata, fonts
│   │   └── page.tsx                   # Landing page with urgency tier overview
│   ├── components/
│   │   └── chat/
│   │       ├── ChatWindow.tsx         # Main chat container — messages, input, state
│   │       ├── MessageBubble.tsx      # Styled user/assistant message bubbles
│   │       └── TriageResult.tsx       # Urgency card, conditions, actions, disclaimer
│   ├── lib/
│   │   ├── api.ts                     # Typed fetch wrapper for backend calls
│   │   └── types.ts                   # TypeScript interfaces (TriageResponse, Message…)
│   ├── .env.local                     # Frontend environment variables
│   └── package.json
│
├── backend/                           # FastAPI application
│   ├── app/
│   │   ├── main.py                    # App factory, CORS middleware, router registration
│   │   ├── config.py                  # pydantic-settings — validates all env vars at startup
│   │   ├── database.py                # Async SQLAlchemy engine + get_db dependency
│   │   ├── redis_client.py            # Redis connection pool (lazy singleton)
│   │   ├── api/
│   │   │   ├── deps.py                # Shared FastAPI dependencies (auth, db)
│   │   │   └── routes/
│   │   │       └── triage.py          # POST /api/triage — main symptom submission endpoint
│   │   ├── models/                    # SQLAlchemy ORM models
│   │   │   ├── patient.py             # patients table
│   │   │   ├── doctor.py              # doctors table
│   │   │   ├── session.py             # triage sessions table
│   │   │   ├── review.py              # doctor reviews table
│   │   │   └── audit.py              # audit_log table (append-only, HIPAA)
│   │   ├── schemas/                   # Pydantic request/response validation
│   │   │   ├── triage.py              # TriageRequest, TriageResponse
│   │   │   ├── auth.py                # LoginRequest, TokenResponse, UserCreate
│   │   │   └── case.py                # CaseDetail, ReviewRequest
│   │   ├── services/
│   │   │   ├── safety_rules.py        # Hardcoded emergency keyword matching (no LLM)
│   │   │   ├── rag_pipeline.py        # LangChain RAG chain — retrieval + Claude triage
│   │   │   ├── triage_ai.py           # 4-step orchestration service
│   │   │   ├── case_manager.py        # Session persistence + doctor review queries
│   │   │   ├── audit_logger.py        # Append-only HIPAA audit log writer
│   │   │   └── notification.py        # SendGrid email alerts for flagged cases
│   │   └── utils/
│   │       └── symptom_extractor.py   # Claude API — free text → structured JSON
│   ├── alembic/                       # Database migrations
│   │   ├── versions/                  # Auto-generated migration files
│   │   └── env.py                     # Alembic async engine configuration
│   ├── tests/
│   │   └── test_safety_rules.py       # 7 pytest tests for emergency escalation logic
│   ├── .env                           # Backend environment variables (never committed)
│   ├── alembic.ini                    # Alembic configuration
│   ├── pytest.ini                     # pytest configuration (asyncio, pythonpath)
│   └── requirements.txt               # Pinned Python dependencies
│
├── docker-compose.yml                 # Local dev: postgres + redis + backend + frontend
└── README.md
```

---

## Database Schema

Five tables power the application:

| Table | Purpose |
|-------|---------|
| `patients` | Patient accounts — email, hashed password, medical history |
| `doctors` | Doctor accounts — email, hashed password, specialty |
| `sessions` | Every triage session — raw symptoms, structured symptoms, AI result, urgency, confidence, flag status |
| `reviews` | Doctor reviews — agree/override decision, override reason, notes |
| `audit_log` | Append-only log of every write action — actor, action, entity, timestamp. Never updated or deleted |

---

## The AI Model — How It Works

### Model Used
**Anthropic Claude `claude-sonnet-4-20250514`** — used for both the symptom extraction step and the triage reasoning step.

### Step 1 — Symptom Extraction
The patient's free-text description is passed to Claude with a structured prompt asking it to return a JSON object with fields like `primary_symptoms`, `severity`, `duration`, `onset`, `location`, and `aggravating_factors`. This structured representation is what gets passed to the RAG chain — not the raw text.

```
"I've had a splitting headache for 3 days, gets worse when I bend forward, mild fever"
                              │
                              ▼ Claude extraction
{
  "primary_symptoms": ["headache"],
  "duration": "3 days",
  "severity": "severe",
  "aggravating_factors": ["bending forward"],
  "associated_symptoms": ["fever"]
}
```

### Step 2 — RAG Triage
LangChain retrieves the 5 most relevant chunks from the Pinecone medical guidelines index using semantic similarity to the structured symptoms. These chunks (CDC guidelines, NIH clinical protocols, WHO triage standards) are injected into the system prompt before Claude produces the final triage output.

Claude returns a JSON object with:
- `urgency_level` — `er` | `urgent_care` | `gp` | `self_care`
- `confidence_score` — 0.0 to 1.0
- `conditions_suggested` — list of probable conditions with probability (high/medium/low)
- `reasoning` — step-by-step clinical reasoning
- `recommended_actions` — what the patient should do next
- `disclaimer` — always present, always displayed

### Why RAG Instead of Plain LLM?
Without retrieval, the LLM reasons only from its training data — which may be outdated or too general. With RAG, the model is grounded in specific, curated medical guidelines at inference time. This means:
- Triage decisions are traceable to source documents
- The knowledge base can be updated without retraining the model
- Hallucination risk for clinical facts is reduced

---

## Screenshots

### Landing Page
![Landing Page](screenshots/landing.png)

### Patient Chat — Self-Care Result
![Self-Care](screenshots/chat_self_care.png)

### Patient Chat — Emergency Result
![Emergency](screenshots/chat_emergency.png)

### Patient Chat — ER Result with Reasoning
![ER Result](screenshots/chat_er.png)

> Screenshots are taken from the running local development instance at `http://localhost:3000`

---

## Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker Desktop

### 1. Clone the repository
```bash
git clone https://github.com/Mokshitha1303/AI-Medical-Triage-Project.git
cd AI-Medical-Triage-Project
```

### 2. Start infrastructure
```bash
docker compose up -d postgres redis
```

### 3. Backend setup
```bash
cd backend
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt   # Windows
# or: .venv/bin/pip install -r requirements.txt  # Mac/Linux

# Copy and fill in your API keys
cp .env.example .env
```

Required keys in `backend/.env`:
```
ANTHROPIC_API_KEY=sk-ant-...
PINECONE_API_KEY=...          # optional — falls back to LLM-only mode
JWT_SECRET_KEY=...            # any long random string
```

```bash
# Run database migrations
.venv/Scripts/alembic upgrade head

# Start the API server
.venv/Scripts/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Frontend setup
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000` in your browser.

### 5. Run tests
```bash
cd backend
.venv/Scripts/pytest tests/ -v
```

---

## Environment Variables

### backend/.env

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL async connection string |
| `REDIS_URL` | Yes | Redis connection string |
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key for Claude |
| `PINECONE_API_KEY` | No | Pinecone key — omit to use LLM-only mode |
| `PINECONE_INDEX_NAME` | No | Pinecone index name (default: `medical-guidelines`) |
| `JWT_SECRET_KEY` | Yes | Secret for signing JWT tokens |
| `CONFIDENCE_THRESHOLD` | No | Auto-flag threshold (default: `0.65`) |
| `CORS_ORIGINS` | No | Allowed frontend origin (default: `http://localhost:3000`) |

### frontend/.env.local

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL |
