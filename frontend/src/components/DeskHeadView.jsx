import React, { useState, useEffect } from "react";
import { getAnalytics, getAuditLogs } from "../api/analytics";
import { resetDemoData } from "../api/stories";

export default function DeskHeadView({ currentUser }) {
  const [analytics, setAnalytics] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [resetSuccess, setResetSuccess] = useState("");
  const [resetting, setResetting] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getAnalytics();
      setAnalytics(data);

      const logsRes = await getAuditLogs();
      setAuditLogs(logsRes.logs || []);
    } catch (err) {
      setError(err.message || "Failed to load Desk Head analytics.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleResetDemo = async () => {
    const confirmed = window.confirm(
      "Reset Demo Data?\n\nThis will remove generated stories, briefs, merges, and demo activity while keeping the original 81 raw news items and demo users.\n\nYou can run AI clustering again afterward.\n\nContinue?"
    );

    if (!confirmed) return;

    setResetting(true);
    setResetSuccess("");
    setError("");

    try {
      const res = await resetDemoData();
      setResetSuccess(res.message || "Demo data reset successfully. The newsroom is ready for a fresh AI run.");
      await fetchData();
    } catch (err) {
      setError(err.message || "Failed to reset demo data.");
    } finally {
      setResetting(false);
    }
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h2>Desk Head Analytics & Output Dashboard</h2>
          <p className="description">
            Publication metrics, subject distributions, time-to-publication calculations, and operational audit trail.
          </p>
        </div>
        <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
          <button
            className="btn"
            onClick={handleResetDemo}
            disabled={resetting}
            style={{ backgroundColor: "#dc2626", color: "#ffffff", border: "none", fontWeight: 600 }}
          >
            {resetting ? "Resetting..." : "Reset Demo Data"}
          </button>
          <div className="role-badge role-desk_head">Logged in: {currentUser.name} (DESK HEAD)</div>
        </div>
      </div>

      {resetSuccess && (
        <div style={{ marginBottom: "16px", padding: "12px 16px", backgroundColor: "#065f4620", border: "1px solid #10b981", color: "#10b981", borderRadius: "8px", fontWeight: 500 }}>
          {resetSuccess}
        </div>
      )}

      {error && <div className="error-alert">{error}</div>}


      {loading ? (
        <div className="loading-state">Calculating publication metrics...</div>
      ) : !analytics ? (
        <div className="empty-state">No publication analytics available.</div>
      ) : (
        <div>
          {/* Top Metrics Cards */}
          <div className="metrics-grid">
            <div className="metric-card">
              <span className="metric-title">Published Yesterday</span>
              <strong className="metric-value">{analytics.published_yesterday}</strong>
              <small className="metric-subtitle">Stories out yesterday</small>
            </div>

            <div className="metric-card">
              <span className="metric-title">Published Today</span>
              <strong className="metric-value">{analytics.published_today}</strong>
              <small className="metric-subtitle">Stories out today</small>
            </div>

            <div className="metric-card">
              <span className="metric-title">Total Published</span>
              <strong className="metric-value">{analytics.total_published}</strong>
              <small className="metric-subtitle">All time published briefs</small>
            </div>

            <div className="metric-card">
              <span className="metric-title">Avg Time to Publication</span>
              <strong className="metric-value metric-highlight">{analytics.average_time_to_publication_formatted}</strong>
              <small className="metric-subtitle">Published At - First Incoming At</small>
            </div>
          </div>

          {/* Publication History Table */}
          <section className="section-card" style={{ marginTop: "24px" }}>
            <h3>Published Story Output History ({analytics.publication_history.length})</h3>
            {analytics.publication_history.length === 0 ? (
              <p className="empty-text">No stories have been published yet. Editor must approve & publish a draft story first.</p>
            ) : (
              <div className="table-responsive">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Published Story Title</th>
                      <th>Category</th>
                      <th>Sources</th>
                      <th>First Incoming</th>
                      <th>Published At</th>
                      <th>Time to Publication</th>
                      <th>Publisher</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analytics.publication_history.map((story) => (
                      <tr key={story.brief_id}>
                        <td><strong>{story.brief_headline}</strong></td>
                        <td><span className="category-tag">{story.category}</span></td>
                        <td><b>{story.source_count}</b> sources</td>
                        <td>{new Date(story.first_incoming_at || story.created_at).toLocaleString()}</td>
                        <td>{new Date(story.published_at).toLocaleString()}</td>
                        <td><span className="badge badge-success">{story.duration_formatted}</span></td>
                        <td>{story.publisher_name || "Editor"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          {/* Operational Audit Logs */}
          <section className="section-card" style={{ marginTop: "24px" }}>
            <h3>Operational Audit Trail ({auditLogs.length})</h3>
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Actor</th>
                    <th>Action</th>
                    <th>Entity Type</th>
                    <th>Metadata Details</th>
                  </tr>
                </thead>
                <tbody>
                  {auditLogs.map((log) => (
                    <tr key={log.id}>
                      <td>{new Date(log.created_at).toLocaleString()}</td>
                      <td><b>{log.actor_name || "System"}</b> ({log.actor_role || "ADMIN"})</td>
                      <td><span className="code-pill">{log.action}</span></td>
                      <td>{log.entity_type}</td>
                      <td><small>{JSON.stringify(log.metadata || {})}</small></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
