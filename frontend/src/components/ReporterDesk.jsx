import React, { useState, useEffect } from "react";
import { getStories, getStoryDetail } from "../api/stories";
import { updateBrief, submitBrief } from "../api/briefs";

export default function ReporterDesk({ currentUser, initialSelectedStory }) {
  const [stories, setStories] = useState([]);
  const [activeStory, setActiveStory] = useState(initialSelectedStory || null);
  const [headline, setHeadline] = useState("");
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [statusMsg, setStatusMsg] = useState("");
  const [error, setError] = useState("");

  const fetchDraftStories = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await getStories(1, 50);
      // Filter stories in DRAFT or CLUSTERED status
      const draftList = (res.items || []).filter(
        (s) => !s.brief_status || s.brief_status === "DRAFT" || s.status === "CLUSTERED"
      );
      setStories(draftList);
      if (!activeStory && draftList.length > 0) {
        handleSelectStory(draftList[0].id);
      }
    } catch (err) {
      setError(err.message || "Failed to load reporter drafts.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDraftStories();
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

  const handleSaveDraft = async () => {
    if (!activeStory || !activeStory.brief_id) return;
    setSaving(true);
    setError("");
    setStatusMsg("");
    try {
      await updateBrief(activeStory.brief_id, headline, summary);
      setStatusMsg("Draft brief changes saved locally.");
    } catch (err) {
      setError(err.message || "Failed to save draft changes.");
    } finally {
      setSaving(false);
    }
  };

  const handleSubmitForReview = async () => {
    if (!activeStory || !activeStory.brief_id) return;
    setSubmitting(true);
    setError("");
    setStatusMsg("");
    try {
      // First save changes
      await updateBrief(activeStory.brief_id, headline, summary);
      // Submit brief for Editor review
      await submitBrief(activeStory.brief_id);
      setStatusMsg("Brief submitted successfully for Editor review!");
      await fetchDraftStories();
    } catch (err) {
      setError(err.message || "Failed to submit brief for Editor review.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h2>Reporter Workbench</h2>
          <p className="description">
            Review AI story clusters, verify sources, edit brief text, and submit to the Editor. (Reporter cannot publish).
          </p>
        </div>
        <div className="role-badge role-reporter">Logged in: {currentUser.name} (REPORTER)</div>
      </div>

      {error && <div className="error-alert">{error}</div>}
      {statusMsg && <div className="success-alert">{statusMsg}</div>}

      <div className="workbench-layout">
        {/* Left Panel: Draft Stories List */}
        <aside className="workbench-sidebar">
          <h3>Pending Draft Stories ({stories.length})</h3>
          {loading ? (
            <p>Loading drafts...</p>
          ) : stories.length === 0 ? (
            <p className="empty-text">No pending story drafts.</p>
          ) : (
            <div className="draft-list">
              {stories.map((s) => (
                <div
                  key={s.id}
                  className={`draft-item ${activeStory && activeStory.id === s.id ? "active" : ""}`}
                  onClick={() => handleSelectStory(s.id)}
                >
                  <div className="category-tag">{s.category}</div>
                  <h4>{s.brief_headline || s.canonical_headline}</h4>
                  <small>{s.source_count} Source Reports</small>
                </div>
              ))}
            </div>
          )}
        </aside>

        {/* Main Panel: Brief Editor & Sources */}
        <main className="workbench-main">
          {activeStory ? (
            <div>
              <div className="editor-card">
                <div className="card-header">
                  <span className="category-tag">{activeStory.category}</span>
                  <span className="badge badge-info">DRAFT</span>
                </div>

                <div className="form-group">
                  <label>Story Brief Headline:</label>
                  <input
                    type="text"
                    value={headline}
                    onChange={(e) => setHeadline(e.target.value)}
                    className="headline-input"
                  />
                </div>

                <div className="form-group">
                  <label>Newsroom Brief Summary (Edit AI Draft):</label>
                  <textarea
                    rows={6}
                    value={summary}
                    onChange={(e) => setSummary(e.target.value)}
                    className="summary-textarea"
                  />
                </div>

                <div className="action-row">
                  <button className="btn-secondary" onClick={handleSaveDraft} disabled={saving}>
                    {saving ? "Saving..." : "Save Draft"}
                  </button>
                  <button className="action-btn-primary" onClick={handleSubmitForReview} disabled={submitting}>
                    {submitting ? "Submitting..." : "Submit to Editor for Review &rarr;"}
                  </button>
                </div>
                <small className="notice-text">
                  🔒 Security Notice: As a Reporter, you can edit and submit briefs for review. Only Editors possess permission to publish.
                </small>
              </div>

              {/* Sources Section */}
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
            <div className="empty-state">Select a story draft from the list to begin editing.</div>
          )}
        </main>
      </div>
    </div>
  );
}
