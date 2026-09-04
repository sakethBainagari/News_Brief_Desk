# News Brief Desk Architecture

```text
Synthetic Raw Wire Feed (81 items)
        │
        ▼
   Flask Ingestion
        │
        ▼
   Text Embeddings (SentenceTransformers: all-MiniLM-L6-v2)
        │
        ▼
  FAISS Candidate Retrieval (Cosine Similarity >= 0.60)
        │
        ▼
Google Gemini API Event Verification
 (Evaluates WHO, WHAT, WHERE, WHEN, KEY NUMBERS)
  ↳ Decision: SAME_EVENT / DIFFERENT_EVENT / UNCERTAIN
        │
        ▼
   Story Clusters (Connected Components Graph Persistence)
        │
        ▼
   Gemini AI Brief Draft (Saved in briefs table with status 'DRAFT')
        │
        ▼
   Reporter Workspace (Review / Edit / Submit Brief)
        │
        ▼
   Editor Review Desk (Edit / Approve / Publish Story)
        │
        ▼
   Publication History & Desk Head Analytics
```

## Core Principle

> **Semantic similarity is used for candidate retrieval, not as the final event identity decision.**

Two reports can share nearly identical topic language (e.g., semiconductor investment, government approval, central bank interest rates) while describing completely different real-world events (e.g. Hyderabad $2B chip manufacturing plant vs. Bengaluru $800M R&D center, or RBI 25bps rate cut vs. US Fed rate hold).

1. **SentenceTransformers**: Generates local L2-normalized 384-dimensional vector embeddings combining headline + body.
2. **FAISS Index**: Rapidly filters candidate pairs with cosine similarity $\ge 0.60$, avoiding $O(n^2)$ LLM calls across the entire corpus.
3. **Google Gemini API**: Performs deep factual event verification on candidate pairs, comparing location, organization, date, event type, and monetary amounts before rendering a structured `SAME_EVENT`, `DIFFERENT_EVENT`, or `UNCERTAIN` decision.
4. **Graph Clustering**: Constructs connected components from verified `SAME_EVENT` edges to form immutable story clusters.
5. **Brief Generation**: Synthesizes corroborating multi-source articles into a concise newsroom draft brief.

## Role Permissions Boundary

- **Reporter**: Views raw items, reviews AI story clusters, edits draft briefs, submits for editor review. Cannot publish.
- **Editor**: Reviews submissions, rewrites briefs, approves, publishes stories, merges duplicate clusters.
- **Desk Head**: Inspects publication analytics, history, total story counts, and time-to-publication.
