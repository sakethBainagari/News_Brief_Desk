import React, { useState, useEffect } from "react";
import { getStories, getStoryDetail, runClustering } from "../api/stories";

export default function StoryQueueView({ currentUser, onSelectStoryForEdit }) {
  const [stories, setStories] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [clusteringLoading, setClusteringLoading] = useState(false);
  const [selectedStory, setSelectedStory] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const fetchStories = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await getStories(1, 100);
      setStories(res.items || []);
      setTotal(res.total || 0);
    } catch (err) {
      setError(err.message || "Failed to load story clusters.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStories();
  }, []);

  const handleRunClustering = async () => {
    setClusteringLoading(true);
    setError("");
    try {
      await runClustering();
      await fetchStories();
    } catch (err) {
      setError(err.message || "Failed to execute AI Event Grouping pipeline.");
    } finally {
      setClusteringLoading(false);
    }
  };

  const handleOpenDetail = async (storyId) => {
    setDetailLoading(true);
    try {
      const detail = await getStoryDetail(storyId);
      setSelectedStory(detail);
    } catch (err) {
      alert("Unable to fetch story cluster details.");
    } finally {
      setDetailLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const s = (status || "CLUSTERED").toUpperCase();
    if (s === "PUBLISHED") return <span className="badge badge-success">PUBLISHED</span>;
    if (s === "EDITOR_REVIEW") return <span className="badge badge-warning">IN EDITOR REVIEW</span>;
    if (s === "MERGED") return <span className="badge badge-muted">MERGED</span>;
    return <span className="badge badge-info">DRAFT STORY</span>;
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h2>AI Grouped Story Clusters</h2>
          <p className="description">
            Multiple wire reports grouped into real-world event clusters via SentenceTransformers + FAISS + Gemini Verification.
          </p>
        </div>
        <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
          {currentUser?.role === "REPORTER" && (
            <button
              className="action-btn-primary"
              onClick={handleRunClustering}
              disabled={clusteringLoading}
            >
              {clusteringLoading ? "Running AI Grouping Pipeline..." : "⚡ Run AI Event Grouping"}
            </button>
          )}
          <div className="header-badge">Total Stories: {total}</div>
        </div>
      </div>

      {error && <div className="error-alert">{error}</div>}

      {loading ? (
        <div className="loading-state">Loading story clusters...</div>
      ) : stories.length === 0 ? (
        <div className="empty-state">
          <p>
            {currentUser?.role === "REPORTER"
              ? 'No story clusters found. Click "Run AI Event Grouping" above to group raw wire items into real-world stories!'
              : "No story clusters found. A Reporter must run AI Event Grouping to group raw wire items."}
          </p>
        </div>
      ) : (
        <div className="story-grid">
          {stories.map((story) => (
            <article key={story.id} className="story-card" onClick={() => handleOpenDetail(story.id)}>
              <div className="story-card-header">
                <span className="category-tag">{story.category || "General"}</span>
                {getStatusBadge(story.brief_status || story.status)}
              </div>
              <h3 className="story-title">{story.brief_headline || story.canonical_headline}</h3>
              <p className="story-brief-preview">
                {story.brief_summary ? story.brief_summary.slice(0, 160) + "..." : "Draft brief generated."}
              </p>
              <div className="story-card-footer">
                <span className="sources-count">📰 <b>{story.source_count}</b> Source Reports</span>
                <span className="confidence-label">Match Confidence: <b>{(floatVal(story.confidence) * 100).toFixed(0)}%</b></span>
              </div>
            </article>
          ))}
        </div>
      )}

      {selectedStory && (
        <div className="modal-backdrop" onClick={() => setSelectedStory(null)}>
          <div className="modal-content large-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <span className="category-tag">{selectedStory.category}</span>
              {getStatusBadge(selectedStory.brief_status || selectedStory.status)}
              <button className="close-btn" onClick={() => setSelectedStory(null)}>&times;</button>
            </div>

            <h2>{selectedStory.brief_headline || selectedStory.canonical_headline}</h2>

            <div className="story-explainability-box">
              <h4>🤖 AI Event Grouping Explanation</h4>
              <p>{selectedStory.confidence_reason || "All source reports describe the exact same real-world event."}</p>
              <div className="confidence-pill">Confidence: {(floatVal(selectedStory.confidence) * 100).toFixed(0)}%</div>
            </div>

            <div className="brief-section">
              <h3>AI Newsroom Brief Draft</h3>
              <div className="brief-box">
                <p>{selectedStory.brief_summary || "No draft summary available."}</p>
              </div>
            </div>

            <div className="sources-section">
              <h3>Source Wire Articles ({selectedStory.source_count})</h3>
              <div className="source-list">
                {selectedStory.sources && selectedStory.sources.map((src, idx) => (
                  <div key={src.id} className="source-item">
                    <div className="source-meta">
                      <strong>Source [{idx + 1}]: {src.source_name}</strong> &bull; 
                      <span> Published: {new Date(src.source_published_at || src.ingested_at).toLocaleString()}</span>
                    </div>
                    <h4>{src.headline}</h4>
                    <p>{src.body}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="modal-footer">
              {onSelectStoryForEdit && (
                <button
                  className="action-btn-primary"
                  onClick={() => {
                    const s = selectedStory;
                    setSelectedStory(null);
                    onSelectStoryForEdit(s);
                  }}
                >
                  Edit / Work on Brief &rarr;
                </button>
              )}
              <button onClick={() => setSelectedStory(null)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function floatVal(val) {
  const parsed = parseFloat(val);
  return isNaN(parsed) ? 1.0 : parsed;
}
