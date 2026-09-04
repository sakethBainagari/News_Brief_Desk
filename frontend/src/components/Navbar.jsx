import React from "react";

export default function Navbar({ currentUser, activeTab, setActiveTab, onLogout }) {
  const getNavTabs = () => {
    if (!currentUser) return [];
    const role = currentUser.role;

    if (role === "REPORTER") {
      return [
        { id: "wire", label: "Raw Wire" },
        { id: "stories", label: "Story Queue" },
        { id: "reporter", label: "My Drafts" },
        { id: "sandbox", label: "Topic vs Event Sandbox" }
      ];
    } else if (role === "EDITOR") {
      return [
        { id: "editor", label: "Review Queue" },
        { id: "stories", label: "Story Queue" },
        { id: "sandbox", label: "Topic vs Event Sandbox" }
      ];
    } else if (role === "DESK_HEAD") {
      return [
        { id: "deskhead", label: "Desk Head Dashboard" },
        { id: "stories", label: "Published Stories" },
        { id: "sandbox", label: "Topic vs Event Sandbox" }
      ];
    }

    return [
      { id: "stories", label: "Story Queue" },
      { id: "sandbox", label: "Topic vs Event Sandbox" }
    ];
  };

  const tabs = getNavTabs();

  return (
    <header className="topbar">
      <div className="brand">
        <strong>NEWS BRIEF DESK</strong>
        <span className="subtitle">AI Event Grouping & Newsroom Workflow</span>
      </div>

      <nav className="nav-tabs">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`nav-tab ${activeTab === tab.id ? "active" : ""}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      {currentUser && (
        <div className="user-profile">
          <span className="user-name">{currentUser.name}</span>
          <span className={`role-badge role-${currentUser.role.toLowerCase()}`}>
            {currentUser.role}
          </span>
          <button className="logout-btn" onClick={onLogout}>Log Out</button>
        </div>
      )}
    </header>
  );
}
