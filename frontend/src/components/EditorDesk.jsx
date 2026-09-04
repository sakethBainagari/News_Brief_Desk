import React, { useState, useEffect } from "react";
import { getStories, getStoryDetail, mergeStories } from "../api/stories";
import { updateBrief, publishBrief } from "../api/briefs";

export default function EditorDesk({ currentUser }) {
  const [stories, setStories] = useState([]);
  const [activeStory, setActiveStory] = useState(null);
  const [headline, setHeadline] = useState("");
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(true);
  const [publishing, setPublishing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [statusMsg, setStatusMsg] = useState("");
  const [error, setError] = useState("");

  // Merge modal state
  const [showMergeModal, setShowMergeModal] = useState(false);
  const [sourceStoryId, setSourceStoryId] = useState("");
  const [targetStoryId, setTargetStoryId] = useState("");
  const [mergeReason, setMergeReason] = useState("Editor initiated story cluster merge.");
  const [merging, setMerging] = useState(false);

  const fetchEditorStories = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await getStories(1, 100);
      const list = res.items || [];
      setStories(list);

      // Select first in EDITOR_REVIEW or first available
      const inReview = list.find((s) => s.brief_status === "EDITOR_REVIEW" || s.status === "EDITOR_REVIEW");
      const initial = inReview || list[0];
      if (initial && (!activeStory || activeStory.id !== initial.id)) {
        handleSelectStory(initial.id);
      }
    } catch (err) {
      setError(err.message || "Failed to load review queue.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEditorStories();
  }, []);

  const handleSelectStory = async (storyId) => {
    setError("");
    setStatusMsg("");
    try {
      const detail = await getStoryDetail(storyId);
      setActiveStory(detail);
      setHeadline(detail.brief_headline || detail.canonical_headline || "");
      setSummary(detail.brief_summary || "");
    } catch (err) {
      setError("Unable to load story details.");
    }
  };

  const handleSaveRewrite = async () => {
    if (!activeStory || !activeStory.brief_id) return;
    setSaving(true);
    setError("");
    setStatusMsg("");
    try {
      await updateBrief(activeStory.brief_id, headline, summary);
      setStatusMsg("Editor brief rewrite saved.");
    } catch (err) {
      setError(err.message || "Failed to save brief rewrite.");
    } finally {
      setSaving(false);
    }
  };

  const handlePublish = async () => {
    if (!activeStory || !activeStory.brief_id) return;
    setPublishing(true);
    setError("");
    setStatusMsg("");
    try {
      // First save any edits
      await updateBrief(activeStory.brief_id, headline, summary);
      // Publish brief
      await publishBrief(activeStory.brief_id);
      setStatusMsg(`Story brief published successfully by Editor ${currentUser.name}!`);
      await fetchEditorStories();
    } catch (err) {
      setError(err.message || "Failed to publish story brief.");
    } finally {
      setPublishing(false);
    }
  };

  const handleExecuteMerge = async () => {
    if (!sourceStoryId || !targetStoryId) {
      alert("Select both source and target stories to merge.");
      return;
    }
    if (sourceStoryId === targetStoryId) {
      alert("Source and target stories cannot be the same.");
      return;
    }
    setMerging(true);
    try {
      await mergeStories(sourceStoryId, targetStoryId, mergeReason);
      alert("Story clusters merged successfully!");
      setShowMergeModal(false);
      await fetchEditorStories();
    } catch (err) {
      alert(err.message || "Failed to merge story clusters.");
    } finally {
      setMerging(false);
    }
  };

  const reviewQueue = stories.filter((s) => s.brief_status === "EDITOR_REVIEW" || s.status === "EDITOR_REVIEW");
  const isPublished = activeStory && (activeStory.brief_status === "PUBLISHED" || activeStory.status === "PUBLISHED");

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h2>Editor Review Desk</h2>
          <p className="description">
            Review reporter submissions, rewrite briefs, authorize publication, and merge duplicate stories.
          </p>
        </div>
        <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
          <button className="btn-secondary" onClick={() => setShowMergeModal(true)}>
            🔀 Merge Stories
          </button>
          <div className="role-badge role-editor">Logged in: {currentUser.name} (EDITOR)</div>
        </div>
      </div>

      {error && <div className="error-alert">{error}</div>}
      {statusMsg && <div className="success-alert">{statusMsg}</div>}

      <div className="workbench-layout">
        {/* Left Panel: Review Queue */}
        <aside className="workbench-sidebar">
          <h3>Review Queue ({reviewQueue.length})</h3>
          {loading ? (
            <p>Loading queue...</p>
          ) : stories.length === 0 ? (
            <p className="empty-text">Queue empty.</p>
          ) : (
            <div className="draft-list">
              {stories.map((s) => (
                <div
                  key={s.id}
                  className={`draft-item ${activeStory && activeStory.id === s.id ? "active" : ""}`}
                  onClick={() => handleSelectStory(s.id)}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span className="category-tag">{s.category}</span>
                    <span className={`status-pill pill-${(s.brief_status || s.status).toLowerCase()}`}>
                      {s.brief_status || s.status}
                    </span>
                  </div>
                  <h4>{s.brief_headline || s.canonical_headline}</h4>
                  <small>{s.source_count} Sources</small>
                </div>
              ))}
            </div>
          )}
        </aside>

        {/* Main Panel: Editor Brief Approval & Publishing */}
        <main className="workbench-main">
          {activeStory ? (
            <div>
              <div className="editor-card">
                <div className="card-header">
                  <span className="category-tag">{activeStory.category}</span>
                  {isPublished ? (
                    <span className="badge badge-success">PUBLISHED</span>
                  ) : (
                    <span className="badge badge-warning">EDITOR REVIEW</span>
                  )}
                </div>

                <div className="form-group">
                  <label>Headline (Editor Approval/Rewrite):</label>
                  <input
                    type="text"
                    value={headline}
                    onChange={(e) => setHeadline(e.target.value)}
                    disabled={isPublished}
                    className="headline-input"
                  />
                </div>

                <div className="form-group">
                  <label>Newsroom Brief Copy (Editor Final Rewrite):</label>
                  <textarea
                    rows={6}
                    value={summary}
                    onChange={(e) => setSummary(e.target.value)}
                    disabled={isPublished}
                    className="summary-textarea"
                  />
                </div>

                {isPublished ? (
                  <div className="published-locked-banner">
                    ✅ <b>STORY PUBLISHED</b> &bull; Published at: {new Date(activeStory.published_at || activeStory.created_at).toLocaleString()}
                    <br />
                    <small>Once a brief is published, it is out. Editing and re-publishing are locked.</small>
                  </div>
                ) : (
                  <div className="action-row">
                    <button className="btn-secondary" onClick={handleSaveRewrite} disabled={saving}>
                      {saving ? "Saving..." : "Save Rewrite"}
                    </button>
                    <button className="action-btn-success" onClick={handlePublish} disabled={publishing}>
                      {publishing ? "Publishing..." : "🚀 Approve & Publish Story"}
                    </button>
                  </div>
                )}
              </div>

              {/* Source Articles */}
              <div className="sources-section" style={{ marginTop: "24px" }}>
                <h3>Corroborating Source Reports ({activeStory.source_count})</h3>
                <div className="source-list">
                  {activeStory.sources && activeStory.sources.map((src, idx) => (
                    <div key={src.id} className="source-item">
                      <div className="source-meta">
                        <strong>Source [{idx + 1}]: {src.source_name}</strong> &bull; 
                        <span> Received: {new Date(src.source_published_at || src.ingested_at).toLocaleString()}</span>
                      </div>
                      <h4>{src.headline}</h4>
                      <p>{src.body}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="empty-state">Select a story from the queue to review and publish.</div>
          )}
        </main>
      </div>

      {/* Story Merge Modal */}
      {showMergeModal && (
        <div className="modal-backdrop" onClick={() => setShowMergeModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>🔀 Merge Story Clusters</h2>
              <button className="close-btn" onClick={() => setShowMergeModal(false)}>&times;</button>
            </div>
            <p>Reassign source articles from a source story into a target story. Only an Editor can perform merges.</p>

            <div className="form-group">
              <label>Source Story (To be merged & archived):</label>
              <select value={sourceStoryId} onChange={(e) => setSourceStoryId(e.target.value)}>
                <option value="">-- Select Source Story --</option>
                {stories.map((s) => (
                  <option key={s.id} value={s.id}>{s.canonical_headline || s.brief_headline}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Target Story (Primary story receiving sources):</label>
              <select value={targetStoryId} onChange={(e) => setTargetStoryId(e.target.value)}>
                <option value="">-- Select Target Story --</option>
                {stories.map((s) => (
                  <option key={s.id} value={s.id}>{s.canonical_headline || s.brief_headline}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Merge Reason / Audit Note:</label>
              <input
                type="text"
                value={mergeReason}
                onChange={(e) => setMergeReason(e.target.value)}
              />
            </div>

            <div className="modal-footer">
              <button onClick={() => setShowMergeModal(false)}>Cancel</button>
              <button className="action-btn-primary" onClick={handleExecuteMerge} disabled={merging}>
                {merging ? "Merging..." : "Confirm & Merge Stories"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
