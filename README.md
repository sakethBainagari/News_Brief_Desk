# News Brief Desk

AI-Assisted Newsroom Workflow & Real-World Event Grouping System.

---

## Phase 3 Architecture: AI Event Grouping & Story Clustering

Phase 3 implements a **2-Stage AI Event Grouping Pipeline** using local `SentenceTransformers` embeddings, `FAISS` candidate retrieval, Google Gemini API for deep event verification and brief draft generation, and connected components graph clustering.

```text
[81 Raw News Items]
        │
        ▼
[SentenceTransformers] (Local vector embeddings: headline + '\n' + body)
        │
        ▼
[FAISS Candidate Store] (Cosine similarity search >= 0.60 retrieves candidate pairs)
        │
        ▼
[Google Gemini API] (Factual verification: WHO/WHAT/WHERE/WHEN/KEY NUMBERS)
  ↳ Decision: SAME_EVENT / DIFFERENT_EVENT / UNCERTAIN
        │
        ▼
[Story Clustering Engine] (Graph connected components build story_clusters & story_sources)
        │
        ▼
[Gemini Brief Generator] (Newsroom draft brief saved in briefs table with status 'DRAFT')
```

---

## Why FAISS + Gemini API?

1. **Embeddings & FAISS**: Rapidly search and filter candidate news pairs ($\text{similarity} \ge 0.60$), avoiding $O(n^2)$ LLM API calls across the news corpus.
2. **Why FAISS Alone is Insufficient**: Semantic similarity measures topic overlap, NOT event identity. Two reports about semiconductor investments in different cities (Hyderabad vs Bengaluru) look semantically similar in vector space but describe completely different real-world events.
3. **Google Gemini API**: Analyzes extracted facts (entities, monetary values, locations, dates) to confirm whether two candidate reports describe the exact same real-world event.

---

## Development Demo Accounts & Environment Setup

### Environment Variables (`.env`)
```bash
GEMINI_API_KEY=your_google_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
FAISS_CANDIDATE_THRESHOLD=0.60
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/news_brief_desk
JWT_SECRET=replace-with-a-long-random-secret
PORT=5000 # Local development default (Railway injects PORT dynamically)
```

### Seeding & Evaluation Commands

```bash
# 1. Seed database with demo users & raw items
python backend/scripts/seed_db.py --reset

# 2. Run AI Event Grouping & evaluate against Ground Truth
python backend/scripts/evaluate_clustering.py

# 3. Run full automated unit test suite
python -m unittest discover backend/tests

# 4. Run backend API server
python backend/app.py
```

---

## Phase 3 REST API Specification

- `POST /api/stories/cluster` - Triggers the 2-stage AI Event Grouping pipeline (Requires JWT token).
- `GET /api/stories` - Returns list of story clusters with source count, canonical headline, and draft brief.
- `GET /api/stories/:id` - Detailed view of a single story cluster including source raw items list and brief.
- `GET /api/stories/:id/sources` - Returns list of source articles for a story cluster.

---

## Phase 3 Acceptance Checklist

- [x] All obsolete Ollama references completely purged from codebase, config, requirements, and docs.
- [x] Configured Google Gemini Python SDK (`google-genai`) with `GEMINI_API_KEY` and `GEMINI_MODEL`.
- [x] SentenceTransformers embedding service (`backend/services/embedding_service.py`) generating normalized 384d vectors.
- [x] FAISS candidate retrieval service (`backend/services/faiss_service.py`) filtering candidate pairs $\ge 0.60$.
- [x] Gemini event verification service (`backend/services/gemini_service.py`) evaluating WHO, WHAT, WHERE, WHEN, KEY NUMBERS and returning strict JSON decisions.
- [x] Connected components graph clustering (`backend/services/story_clustering.py`) persisting story clusters, sources, and briefs.
- [x] AI-generated brief saved in `briefs` table with `status = 'DRAFT'`.
- [x] Ground truth evaluator script (`backend/scripts/evaluate_clustering.py`) measuring precision, recall, F1, and auditing false-match test pairs.
- [x] Automated unit test suite (`test_ai_pipeline.py`, `test_auth.py`, `test_raw_items.py`, `test_dataset.py`, `test_health.py`) passing 100%.
- [x] Server-side RBAC enforced across all story routes.
