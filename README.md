# News Brief Desk

News Brief Desk is an intelligent, AI-assisted newsroom workflow platform designed for high-volume editorial environments. The system ingests raw wire copy, press releases, and articles, automatically identifies reports describing the exact same real-world event, synthesizes multi-source coverage into concise story briefs, and provides a structured workflow for Reporters, Editors, and Desk Heads—preventing duplicate coverage and enforcing journalistic publication controls.

---

## Assessment / Problem Statement

Modern newsrooms receive hundreds of incoming wire items, press releases, blog posts, and social updates daily. This creates significant editorial challenges:
- **Duplicate Coverage**: Multiple news outlets report on the same breaking event using different headlines, phrasing, and structure.
- **False Merges**: Similar-looking events (e.g., two different semiconductor factory investments in different cities) share identical keywords/topics but describe completely distinct real-world incidents.
- **Workflow Inefficiency**: Reporters waste hours manually cross-referencing wire copy instead of refining stories.
- **Lack of Governance**: Without role enforcement and publication locking, raw drafts can be published directly or modified after going live.

**News Brief Desk solves this by making EVENT similarity—not mere topic similarity—the core clustering objective.** The platform retrieves candidate reports using semantic embeddings, verifies true event identity via Google Gemini LLM reasoning (evaluating Who, What, Where, When, and key facts), generates a canonical brief with linked source evidence, and routes the story through a role-gated editorial workflow.

---

## Key Features

- **JWT Authentication & RBAC**: Secure role-based access control supporting `REPORTER`, `EDITOR`, and `DESK_HEAD` roles with backend-enforced route protection.
- **Raw Wire Desk**: Real-time view of incoming unclustered news items restricted to Reporter triage.
- **AI Event Grouping Engine**: Two-stage clustering combining fast vector search with LLM event verification.
- **Dense Embedding Generation**: Converts article bodies into 384-dimensional dense vectors using `SentenceTransformers` (`all-MiniLM-L6-v2`).
- **FAISS Candidate Retrieval**: Fast cosine-similarity candidate pair discovery (`IndexFlatIP`) operating at a configured threshold (`0.60`).
- **Gemini Event Verification**: Uses `gemini-2.5-flash` to evaluate candidate pairs against factual criteria (Who, What, Where, When), outputting structured decisions (`SAME_EVENT`, `DIFFERENT_EVENT`, `UNCERTAIN`).
- **Connected-Components Clustering**: Formulates canonical story clusters from verified `SAME_EVENT` graph edges.
- **Multi-Source Brief Generation**: Automatically synthesizes multi-source story clusters into structured briefs with source evidence attribution.
- **Reporter Workspace**: Interface for triggering AI grouping, reviewing generated briefs, editing draft content, and submitting briefs to the Editor queue.
- **Editor Workspace**: Review queue for inspecting source evidence, rewriting briefs, publishing stories, and manually merging related stories.
- **Server-Enforced Publication Locking**: Immutability guard preventing any modification to briefs once published.
- **Editor-Only Story Merging**: Enables Editors to merge duplicate stories with full audit logging.
- **Desk Head Analytics Dashboard**: Executive metrics tracking total stories, published counts, average time-to-publish, category distribution, and system audit logs.
- **One-Click Demo Reset**: Restores the database to its post-seeded 81-item baseline state for repeatable assessment testing.
- **Topic vs. Event Interactive Sandbox**: Live demonstration module allowing evaluators to compare semantic topic similarity against LLM event-level verification.
- **Supabase PostgreSQL Database**: Relational schema enforcing referential integrity and audit logging.
- **Google Cloud Run Backend**: Containerized Python 3.11 Flask service with Google Cloud Build CI/CD (`backend/Dockerfile`, `cloudbuild.yaml`).
- **Modern React Frontend**: Dark-themed, responsive SPA built with React, Vite, and custom CSS design system hosted on Vercel.
- **Automated Test Suite**: 46 backend unit/integration tests and automated dataset clustering evaluation script.

---

## User Roles & Permissions

Access control is strictly enforced both on the backend (via `@require_role` decorators) and on the frontend (via navigation guards and component boundaries).

| Feature / Action | API Endpoint | Reporter | Editor | Desk Head |
| :--- | :--- | :---: | :---: | :---: |
| **View Raw Wire Items** | `GET /api/raw-items` | ✅ | ❌ | ❌ |
| **Trigger AI Event Grouping** | `POST /api/stories/cluster` | ✅ | ❌ | ❌ |
| **View Story Queue & Details** | `GET /api/stories`, `GET /api/stories/:id` | ✅ | ✅ | ✅ |
| **View Story Sources** | `GET /api/stories/:id/sources` | ✅ | ✅ | ✅ |
| **Edit Brief Drafts** | `PUT /api/briefs/:id` | ✅ *(Drafts only)* | ✅ *(Review queue)* | ❌ |
| **Submit Brief to Editor** | `POST /api/briefs/:id/submit` | ✅ | ❌ | ❌ |
| **Publish Brief** | `POST /api/briefs/:id/publish` | ❌ | ✅ | ❌ |
| **Merge Stories** | `POST /api/stories/merge` | ❌ | ✅ | ❌ |
| **Desk Head Analytics & Audits** | `GET /api/analytics`, `GET /api/audit-logs` | ❌ | ❌ | ✅ |
| **Reset Demo Data** | `POST /api/demo/reset` | ❌ | ❌ | ✅ |
| **Topic vs. Event Sandbox** | Shared Component | ✅ | ✅ | ✅ |

---

## System Architecture

```mermaid
graph TD
    A["Raw News Wire Items"] --> B["SentenceTransformers Embeddings (all-MiniLM-L6-v2)"]
    B --> C["FAISS Candidate Pair Retrieval (IndexFlatIP, Cosine >= 0.60)"]
    C --> D["Gemini Event Verification (gemini-2.5-flash)"]
    D -->|SAME_EVENT Edges| E["Connected Components Graph Clustering"]
    E --> F["Gemini Brief Generation & Source Attribution"]
    F --> G["Reporter Desk: Review & Submit Draft"]
    G -->|Status: EDITOR_REVIEW| H["Editor Desk: Review, Rewrite & Publish"]
    H -->|Status: PUBLISHED| I["Server-Enforced Publication Lock"]
    I --> J["Desk Head Analytics & Output History"]
```

### Stage Breakdown
1. **Embedding Generation**: Raw text bodies are transformed into dense 384-dimensional vector representations.
2. **FAISS Candidate Retrieval**: FAISS performs vector inner-product search to find candidate article pairs with cosine similarity $\ge 0.60$. Candidate filtering reduces $O(N^2)$ LLM calls down to potential matches.
3. **Gemini Event Verification**: Each candidate pair is analyzed by `gemini-2.5-flash` with strict JSON schema constraints to verify if both reports describe the *exact same real-world incident*.
4. **Graph Clustering**: Verified `SAME_EVENT` pairs form graph edges. Disjoint set (connected components) algorithms group these edges into canonical story clusters.
5. **Brief Generation**: Gemini synthesizes all source items in a cluster into a clean headline, concise summary, and key facts list.
6. **Editorial Workflow**: Drafts move through `DRAFT` $\rightarrow$ `EDITOR_REVIEW` $\rightarrow$ `PUBLISHED` states, concluding with an immutable publication lock.

---

## AI Event Grouping

A fundamental challenge in news processing is distinguishing **Topic Similarity** from **Event Identity**:

```
[TOPIC SIMILARITY] (High Vector Similarity, DIFFERENT Real-World Events)
Article A: "Government clearance for $2 Billion Semiconductor Facility in Hyderabad"
Article B: "$800 Million Semiconductor R&D Center Commitment in Bengaluru"
Result: Both discuss Indian semiconductor investments, but represent TWO DISTINCT EVENTS.

[EVENT IDENTITY] (High Vector Similarity + Verified Fact Alignment, SAME Real-World Event)
Article A: "Govt approves ₹15,000 Cr chip plant in Hyderabad's Fab City"
Article B: "Telangana gets $2B semiconductor manufacturing unit clearance"
Result: Both describe the EXACT SAME EVENT in Hyderabad.
```

### Verification Criteria
The Gemini verification module extracts and compares:
- **Who**: Primary entities, government bodies, corporations.
- **What**: Action, announcement, incident details.
- **Where**: Precise location (city/region).
- **When**: Specific date or time frame.
- **Key Figures**: Monetary values, statistics, percentages.

Candidate pairs that match on topic but fail on specific entities or locations are classified as `DIFFERENT_EVENT` and kept in separate stories.

---

## Dataset

The project includes a curated synthetic dataset designed specifically to test multi-source aggregation and false-match separation:

- **Total Raw Wire Items**: 81 items
- **Ground Truth Real-World Events**: 24 distinct events
- **Multi-Source Events**: 19 events (2 to 5 reports per event)
- **Single-Source Events**: 5 events
- **Engineered False-Match Pairs**: 9 pairs (18 events specifically crafted with overlapping vocabulary/topics in different cities/dates to test separation capabilities)

Ground truth event mappings are maintained independently in `data/ground_truth_events.json` to allow objective offline evaluation without biasing production clustering tables.

---

## AI Evaluation

Running the automated evaluation script (`python backend/scripts/evaluate_clustering.py`) against the 81-item dataset yields the following results:

```
==================================================
      AI EVENT GROUPING EVALUATION REPORT         
==================================================
Total Raw Items Processed : 81
Ground Truth Events       : 24
Predicted Clusters        : 24
Evaluated Candidate Pairs : 113
Verified SAME_EVENT Pairs : 110
--------------------------------------------------
True Merges (TP)          : 114
False Merges (FP)         : 0
Missed Merges (FN)        : 0
True Separations (TN)     : 3126
--------------------------------------------------
Pairwise Precision        : 100.00%
Pairwise Recall           : 100.00%
Pairwise F1 Score         : 100.00%
==================================================
[SUCCESS] All 9 false-match test pairs were correctly kept SEPARATE!
```

---

## Newsroom Workflow

The platform implements a strict state machine for newsroom governance:

```
[Raw Wire] ──(AI Grouping)──> [CLUSTERED / DRAFT]
                                      │
                             (Reporter Submit)
                                      ▼
                              [EDITOR_REVIEW]
                                      │
                              (Editor Publish)
                                      ▼
                                 [PUBLISHED] ──(Locked)
```

1. **Ingestion & Triage**: Raw wire items arrive at the Reporter's Raw Wire desk.
2. **AI Clustering**: The Reporter clicks **⚡ Run AI Event Grouping**, triggering candidate discovery, Gemini verification, and story cluster creation.
3. **Draft Preparation**: Reporter opens the generated story, edits the brief if necessary, and clicks **Submit to Editor**.
4. **Editor Review**: The Editor accesses the **Review Queue**, compares the draft against linked raw source articles, and refines the text.
5. **Publication**: The Editor clicks **Publish Brief**. The story status transitions to `PUBLISHED`.
6. **Immutability Lock**: The backend locks the brief against further modifications.
7. **Desk Head Analytics**: Desk Heads monitor throughput, publication velocity, and audit histories.

---

## Publication Lock

Journalistic integrity requires that published articles cannot be silently altered. 

- **Backend Enforcement**: In [backend/routes/briefs.py](file:///c:/Users/saket/Desktop/news-brief-desk/backend/routes/briefs.py), `PUT /api/briefs/<brief_id>` inspects current brief status. If `status == 'PUBLISHED'`, the request is rejected with `400 Bad Request` ("Published briefs are locked and cannot be edited.").
- **Frontend Protection**: The Editor UI replaces editing inputs with a read-only locked view and explicit badge indicator.

---

## Database

The application utilizes PostgreSQL (hosted on Supabase in production) with the following primary tables:

- `users`: User accounts, role definitions (`REPORTER`, `EDITOR`, `DESK_HEAD`), and bcrypt password hashes.
- `raw_items`: Raw wire articles, source names, headlines, body copy, and ingestion timestamps.
- `story_clusters`: Clustered events, canonical headlines, confidence scores, and lifecycle status (`CLUSTERED`, `DRAFT`, `EDITOR_REVIEW`, `PUBLISHED`, `MERGED`).
- `story_sources`: Many-to-many junction mapping raw items to story clusters with Gemini verification labels (`SAME_EVENT`, `DIFFERENT_EVENT`, `UNCERTAIN`) and reasoning.
- `briefs`: Story brief headlines, summary text, author/editor references, and submission/publication timestamps.
- `story_merges`: Audit record of manual story merges performed by Editors.
- `audit_logs`: Detailed activity log capturing user actions, timestamps, entity IDs, and metadata.

---

## Authentication & Security

- **JWT Tokens**: Authenticated requests require a `Bearer <token>` HTTP Authorization header signed via HMAC-SHA256.
- **Password Security**: Passwords are standard-hashed using `bcrypt`.
- **Role Enforcement**: Every protected route uses `@jwt_required` and `@require_role(...)` decorators to reject unauthorized access attempt with `401 Unauthorized` or `403 Forbidden`.
- **Secret Isolation**: Gemini API keys, JWT secrets, and database connection strings remain server-side on Google Cloud Run and are never sent to the client bundle.

---

## API Overview

| Method | Endpoint | Description | Auth Required | Allowed Roles |
| :--- | :--- | :--- | :---: | :---: |
| `POST` | `/api/auth/login` | Authenticate user and issue JWT | Public | Anyone |
| `GET` | `/api/auth/me` | Fetch active user session | Yes | All Roles |
| `GET` | `/api/raw-items` | Fetch unclustered raw wire items | Yes | `REPORTER` |
| `GET` | `/api/raw-items/<id>` | Fetch single raw wire item details | Yes | `REPORTER` |
| `POST` | `/api/stories/cluster` | Trigger AI Event Grouping pipeline | Yes | `REPORTER` |
| `GET` | `/api/stories` | List stories (filterable by status) | Yes | All Roles |
| `GET` | `/api/stories/<id>` | Fetch story cluster details & brief | Yes | All Roles |
| `GET` | `/api/stories/<id>/sources` | Fetch linked raw source articles | Yes | All Roles |
| `PUT` | `/api/briefs/<id>` | Update brief headline/summary text | Yes | `REPORTER`, `EDITOR` |
| `POST` | `/api/briefs/<id>/submit` | Submit brief for Editor review | Yes | `REPORTER` |
| `POST` | `/api/briefs/<id>/publish` | Publish brief (enforces lock) | Yes | `EDITOR` |
| `POST` | `/api/stories/merge` | Merge two stories into one | Yes | `EDITOR` |
| `GET` | `/api/analytics` | Fetch Desk Head publication metrics | Yes | `DESK_HEAD` |
| `GET` | `/api/audit-logs` | Fetch system audit logs | Yes | `DESK_HEAD` |
| `POST` | `/api/demo/reset` | Reset database state to 81 raw items | Yes | `DESK_HEAD` |
| `GET` | `/api/health` | Service and database status check | Public | Anyone |

---

## Project Structure

```
news-brief-desk/
├── cloudbuild.yaml             # Google Cloud Build CI/CD workflow
├── backend/
│   ├── Dockerfile              # Production Python 3.11 Docker build container
│   ├── .dockerignore           # Container build ignore rules
│   ├── cloudbuild.yaml         # Subdirectory Google Cloud Build trigger config
│   ├── app.py                  # Flask entry point & Blueprint registration
│   ├── config.py               # Environment & configuration management
│   ├── requirements.txt        # Python dependencies
│   ├── auth/                   # JWT & RBAC decorator implementation
│   ├── db/                     # PostgreSQL connection pool & SQL query modules
│   ├── routes/                 # REST API route handlers
│   ├── services/               # AI pipeline (Embeddings, FAISS, Gemini, Clustering)
│   ├── scripts/                # Database seeding & clustering evaluation scripts
│   └── tests/                  # Backend unit & integration test suite
├── data/
│   ├── synthetic_raw_items.json # 81-item raw wire dataset
│   └── ground_truth_events.json # 24 ground-truth event definitions
├── database/
│   ├── schema.sql              # PostgreSQL DDL table schema
│   └── seed.sql                # SQL seed script
├── docs/                       # Architecture documentation & demo checklists
└── frontend/
    ├── index.html              # Single page application entry HTML
    ├── package.json            # Node.js dependencies & scripts
    ├── vite.config.js          # Vite build configuration
    └── src/
        ├── App.jsx             # Main application container & view router
        ├── api/                # Axios API client & modular endpoints
        ├── components/         # Workspace views (Reporter, Editor, DeskHead, Sandbox)
        └── styles.css          # Design system stylesheet
```

---

## Tech Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React 18, Vite | Component-based Single Page Application |
| **Backend** | Python 3.11, Flask, Gunicorn | REST API service & WSGI application server |
| **Database** | PostgreSQL, Supabase | Relational data persistence & JSON query support |
| **Vector Search** | FAISS (`faiss-cpu`) | Dense vector index for fast similarity candidate search |
| **Embeddings** | `SentenceTransformers` (`all-MiniLM-L6-v2`) | Local 384-dimensional text embedding generation |
| **LLM Provider** | Google Gemini (`gemini-2.5-flash`) | Fact verification & brief synthesis |
| **Authentication** | PyJWT, bcrypt | JWT token signing & secure password hashing |
| **Backend Deployment** | Google Cloud Run (Docker) | Containerized serverless backend hosting |
| **Frontend Deployment** | Vercel | Jamstack SPA hosting |

---

## Environment Variables

### Backend (`backend/.env` / Google Cloud Run Variables)
```env
FLASK_ENV=production
FLASK_DEBUG=0
PORT=8080
DATABASE_URL=postgresql://user:password@host:5432/postgres
JWT_SECRET=your-secure-jwt-secret
GEMINI_API_KEY=your-google-gemini-api-key
GEMINI_MODEL=gemini-2.5-flash
FRONTEND_URL=https://your-vercel-app.vercel.app
CORS_ORIGINS=https://your-vercel-app.vercel.app
```

### Frontend (`frontend/.env` / Vercel Variables)
```env
VITE_API_BASE_URL=https://news-brief-desk-xxxx-el.a.run.app/api
```

---

## Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL database (or Supabase instance)
- Docker (optional for local container testing)

### 1. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your credentials
cp .env.example .env
# Edit backend/.env with your DATABASE_URL and GEMINI_API_KEY

# Seed database schema & 81 synthetic raw items
python scripts/seed_db.py --reset

# Start development backend server
python app.py
```
*Backend server runs at `http://localhost:5000`.*

### 2. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```
*Frontend app runs at `http://localhost:5173`.*

---

## Demo Accounts

The database includes three pre-configured demo user accounts:

| Role | Name | Email | Permissions |
| :--- | :--- | :--- | :--- |
| **REPORTER** | Saketh | `saketh@example.com` | Triage Raw Wire, Run AI Grouping, Edit Drafts, Submit to Editor |
| **EDITOR** | Rahul | `rahul@example.com` | Review Queue, Rewrite Briefs, Publish Stories, Merge Stories |
| **DESK_HEAD** | Priya | `priya@example.com` | Executive Analytics, Audit Logs, Reset Demo Data |

> *Note: Demo passwords are provided separately in the assessment environment submission documentation. For production deployments, change default passwords immediately.*

---

## Demo / Evaluation Flow

For evaluators reviewing the application end-to-end:

1. **Reporter Triage**:
   - Log in as `saketh@example.com` (`REPORTER`).
   - Navigate to **Raw Wire** to view 81 unclustered wire items.
   - Click **⚡ Run AI Event Grouping**. Watch the system perform candidate discovery, Gemini verification, and clustering.
   - Navigate to **Story Queue** $\rightarrow$ **My Drafts**, edit a generated brief, and click **Submit to Editor**.

2. **Editor Review & Publishing**:
   - Switch user to `rahul@example.com` (`EDITOR`).
   - Open **Review Queue** to locate the submitted brief.
   - Click **View Sources** to inspect original raw wire evidence.
   - Edit/rewrite brief summary and click **Publish Brief**.
   - Verify that the brief transitions to **PUBLISHED** and editing controls become locked.

3. **Desk Head Oversight**:
   - Switch user to `priya@example.com` (`DESK_HEAD`).
   - Navigate to **Analytics & History** to inspect publication metrics, average time-to-publish, and system audit logs.
   - Click **Reset Demo Data** if you wish to reset the database back to the post-seeded state.

---

## Deployment Architecture

The application is deployed on production cloud infrastructure:

- **Backend**: Containerized via **Docker** (`backend/Dockerfile`) and deployed to **Google Cloud Run** in `asia-south1` via **Google Cloud Build** (`cloudbuild.yaml`).
- **Frontend**: Deployed on **Vercel** (`frontend` root, Vite build target `dist`).
- **Database**: Managed **Supabase PostgreSQL** instance.
- **Repository**: [https://github.com/sakethBainagari/News_Brief_Desk.git](https://github.com/sakethBainagari/News_Brief_Desk.git)

---

## Testing & Quality Assurance

- **Backend Unit & Workflow Tests**: 46 automated tests covering authentication, RBAC decorators, brief lifecycle, publication locking, story merging, and health checks. Run via:
  ```bash
  python -m unittest discover backend/tests
  ```
- **Clustering Evaluation**: Automated evaluation against 24 ground-truth events verifying 100% Precision, Recall, and F1 score:
  ```bash
  python backend/scripts/evaluate_clustering.py
  ```
- **Frontend Production Build**: Verified Vite production bundle compilation:
  ```bash
  cd frontend && npm run build
  ```

---

## Key Design Decisions

1. **Event-Level Grouping over Category Classification**: Categorization groups articles into broad buckets (e.g., "Technology"), whereas newsrooms require exact event identity to avoid duplicate reporting.
2. **Two-Stage Architecture (FAISS + Gemini)**: Running Gemini LLM calls across all pairs of $N$ articles is $O(N^2)$ and expensive. FAISS candidate search filters pair comparisons down to candidates with $\ge 0.60$ vector similarity.
3. **Structured Fact Comparison**: Prompting Gemini to compare Who, What, Where, and When prevents high-level topic overlap from causing false merges.
4. **Conservative Fallback (`UNCERTAIN`)**: If Gemini output fails or expresses uncertainty, items remain unmerged to prioritize precision over false merging.
5. **Human-in-the-Loop Publishing**: AI generates initial briefs, but Reporters and Editors retain complete control over editing, submission, and publishing decisions.
6. **Strict RBAC Separation**: Reporters focus on draft preparation; only Editors can publish or merge stories, matching real-world newsroom governance.
7. **Server-Side Publication Lock**: Enforcing lock state in Python backend logic ensures API clients cannot bypass UI restrictions.
8. **Decoupled Ground Truth**: Ground truth events are stored in JSON data files for objective script evaluation, keeping runtime database tables clean.
9. **Relational Database (PostgreSQL)**: Supabase PostgreSQL provides transactional integrity for story-source mappings and audit logging.
10. **Containerized Serverless Execution**: Running on Google Cloud Run with Docker guarantees identical runtime environments between local development and cloud production.

---

## Assumptions & Scope Limits

- **Data Ingestion**: News items are seeded from structured dataset files rather than real-time RSS/API crawlers.
- **Payment & Subscriptions**: Out of scope for this editorial workflow assessment.
- **LLM Rate Limits**: Assumes standard Google Gemini API quota availability during clustering execution.

---

## Known Limitations & Future Enhancements

- **Live Crawler Integration**: Adding automated RSS and Twitter/X wire crawlers for live ingestion.
- **Async Task Queue**: Integrating Celery / Redis for asynchronous background processing of large scale (10,000+) wire feeds.
- **Source Credibility Scoring**: Weighting story confidence scores based on publisher domain authority.
- **Temporal Reasoning**: Incorporating publication timestamp deltas into candidate scoring.

---

## Assessment Requirement Mapping

| Assessment Requirement | Implementation Details | Status |
| :--- | :--- | :---: |
| **Group same-event reports into one story** | Embeddings + FAISS + Gemini verification + Connected Components | ✅ Verified |
| **Avoid false merges of similar events** | Who/What/Where/When factual verification + false-match evaluation | ✅ Verified (100% F1) |
| **Generate short brief with source evidence** | Gemini brief synthesis + `story_sources` junction tracking | ✅ Verified |
| **Reporter / Editor editorial workflow** | JWT + RBAC + `DRAFT` $\rightarrow$ `EDITOR_REVIEW` $\rightarrow$ `PUBLISHED` states | ✅ Verified |
| **Prevent Reporter from publishing** | Backend `@require_role("EDITOR")` on `/api/briefs/:id/publish` | ✅ Verified |
| **Lock published briefs from editing** | Backend status check in `PUT /api/briefs/:id` rejecting edits | ✅ Verified |
| **Desk Head analytics & output history** | Executive dashboard calculating stories, time-to-publish, audit logs | ✅ Verified |
| **Curated evaluation dataset** | 81 raw items, 24 ground-truth events, 9 false-match pairs | ✅ Verified |
| **Automated Test Suite** | 46 backend unit tests & evaluation script | ✅ Verified |
| **Backend Cloud Deployment** | Google Cloud Run (Docker + Google Cloud Build) | ✅ Prepared |
| **Public GitHub Repository** | [https://github.com/sakethBainagari/News_Brief_Desk.git](https://github.com/sakethBainagari/News_Brief_Desk.git) | ✅ Published |

---

## Author & Credits

**Saketh Bainagari**  
Computer Science / AI & ML  
GitHub: [https://github.com/sakethBainagari](https://github.com/sakethBainagari)
