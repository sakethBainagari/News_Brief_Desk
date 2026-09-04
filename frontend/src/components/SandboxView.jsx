import React, { useState } from "react";

export default function SandboxView() {
  const [activeTab, setActiveTab] = useState("false_match");

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h2>Topic vs Real-World Event Sandbox</h2>
          <p className="description">
            Interactive demonstration showing why semantic vector similarity alone is insufficient for news event deduplication.
          </p>
        </div>
      </div>

      <div className="sandbox-tab-bar">
        <button
          className={`sandbox-tab ${activeTab === "false_match" ? "active" : ""}`}
          onClick={() => setActiveTab("false_match")}
        >
          ❌ False Match Prevention (Topic Similarity ≠ Event Identity)
        </button>
        <button
          className={`sandbox-tab ${activeTab === "same_event" ? "active" : ""}`}
          onClick={() => setActiveTab("same_event")}
        >
          ✅ Same Event Grouping (3 Reports → 1 Story)
        </button>
      </div>

      {activeTab === "false_match" ? (
        <div className="sandbox-card">
          <div className="sandbox-badge-row">
            <span className="similarity-badge">High Cosine Vector Similarity: <b>78.4%</b></span>
            <span className="decision-badge badge-different">Gemini Decision: DIFFERENT_EVENT</span>
          </div>

          <h3>Why Vector Embeddings Flagged a Candidate Pair (False Match):</h3>
          <p className="sandbox-explainer">
            Both reports contain identical topic keywords: <code>semiconductor</code>, <code>investment</code>, <code>government</code>, <code>project</code>, <code>technology</code>. FAISS cosine similarity retrieved them as candidates, but Gemini 2nd-stage factual verification identified key discrepancies.
          </p>

          <div className="comparison-grid">
            {/* Left Card */}
            <div className="comparison-card card-left">
              <span className="source-name">Deccan Business Wire</span>
              <h4>Hyderabad semiconductor manufacturing facility receives government approval</h4>
              <p>
                "Authorities have cleared a proposed <b>$2 billion</b> semiconductor <b>manufacturing facility</b> in <b>Hyderabad</b>."
              </p>
              <div className="fact-list">
                <div>📍 <strong>Location:</strong> Hyderabad</div>
                <div>🏢 <strong>Facility:</strong> Mass Manufacturing Plant</div>
                <div>💰 <strong>Value:</strong> $2 Billion</div>
              </div>
            </div>

            {/* VS Divider */}
            <div className="vs-divider">
              <span>VS</span>
            </div>

            {/* Right Card */}
            <div className="comparison-card card-right">
              <span className="source-name">Capital Markets Daily</span>
              <h4>Bengaluru research center gets $800m technology commitment</h4>
              <p>
                "A separate technology <b>research center</b> planned in <b>Bengaluru</b> has secured an <b>$800 million</b> investment commitment."
              </p>
              <div className="fact-list">
                <div>📍 <strong>Location:</strong> Bengaluru</div>
                <div>🏢 <strong>Facility:</strong> R&D Design Lab</div>
                <div>💰 <strong>Value:</strong> $800 Million</div>
              </div>
            </div>
          </div>

          <div className="verification-audit-box">
            <h4>🤖 Gemini Deep Event Verification Summary:</h4>
            <ul>
              <li>❌ <strong>Location Mismatch:</strong> Article A is in <i>Hyderabad</i>; Article B is in <i>Bengaluru</i>.</li>
              <li>❌ <strong>Facility Type Mismatch:</strong> Article A is a <i>manufacturing plant</i>; Article B is an <i>R&D lab</i>.</li>
              <li>❌ <strong>Financial Amount Mismatch:</strong> Article A is <i>$2 Billion</i>; Article B is <i>$800 Million</i>.</li>
            </ul>
            <div className="final-verdict-banner">
              🛡️ <b>RESULT:</b> System prevents merging. Stories remain in <b>SEPARATE CLUSTERS</b>.
            </div>
          </div>
        </div>
      ) : (
        <div className="sandbox-card">
          <div className="sandbox-badge-row">
            <span className="similarity-badge">High Cosine Vector Similarity: <b>92.1%</b></span>
            <span className="decision-badge badge-same">Gemini Decision: SAME_EVENT</span>
          </div>

          <h3>Same Real-World Event (3 Differently Worded Wire Reports → 1 Story Cluster):</h3>
          <p className="sandbox-explainer">
            Three different news agencies published reports using different headlines and phrasing. Gemini verification confirmed identical entity, location, and financial facts, grouping all 3 into <b>ONE STORY CLUSTER</b>.
          </p>

          <div className="same-event-grid">
            <div className="source-box">
              <span className="source-name">Deccan Business Wire</span>
              <h4>Hyderabad semiconductor facility receives government clearance</h4>
              <p>"Authorities cleared a proposed $2 billion semiconductor manufacturing facility in Hyderabad..."</p>
            </div>

            <div className="source-box">
              <span className="source-name">South Asia Technology Review</span>
              <h4>Government clears $2bn chip plant planned for Hyderabad</h4>
              <p>"A major chip manufacturing project planned for Hyderabad has received final government approval..."</p>
            </div>

            <div className="source-box">
              <span className="source-name">Metro Press Network</span>
              <h4>Hyderabad set for major semiconductor investment after project clearance</h4>
              <p>"Hyderabad is set to receive a large semiconductor investment worth about $2 billion..."</p>
            </div>
          </div>

          <div className="arrow-down-divider">&darr; Grouped via AI Event Pipeline &darr;</div>

          <div className="result-cluster-card">
            <div className="cluster-header">
              <span className="category-tag">Technology</span>
              <span className="badge badge-success">ONE STORY CLUSTER (3 SOURCES)</span>
            </div>
            <h3>Government approves $2B semiconductor manufacturing facility in Hyderabad</h3>
            <p className="brief-preview">
              <b>AI Draft Brief:</b> Authorities have officially approved a $2 billion semiconductor manufacturing facility in Hyderabad. The project is expected to create thousands of engineering and technical jobs upon completion.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
