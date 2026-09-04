import { useEffect, useState } from "react";
import Navbar from "./components/Navbar";
import RawWireView from "./components/RawWireView";
import StoryQueueView from "./components/StoryQueueView";
import ReporterDesk from "./components/ReporterDesk";
import EditorDesk from "./components/EditorDesk";
import DeskHeadView from "./components/DeskHeadView";
import SandboxView from "./components/SandboxView";
import LoginModal from "./components/LoginModal";
import { getMe, logout } from "./api/auth";

export default function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [activeTab, setActiveTab] = useState("stories");
  const [loading, setLoading] = useState(true);
  const [selectedStoryForEdit, setSelectedStoryForEdit] = useState(null);

  const fetchUser = async () => {
    setLoading(true);
    try {
      const user = await getMe();
      setCurrentUser(user);
      // Default view per role
      if (user.role === "REPORTER") setActiveTab("reporter");
      else if (user.role === "EDITOR") setActiveTab("editor");
      else if (user.role === "DESK_HEAD") setActiveTab("deskhead");
    } catch (err) {
      setCurrentUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUser();

    const handleUnauthorized = () => {
      setCurrentUser(null);
    };

    window.addEventListener("auth_unauthorized", handleUnauthorized);
    return () => window.removeEventListener("auth_unauthorized", handleUnauthorized);
  }, []);

  const handleLogout = () => {
    logout();
    setCurrentUser(null);
  };

  const handleSelectStoryForEdit = (story) => {
    setSelectedStoryForEdit(story);
    if (currentUser?.role === "EDITOR") setActiveTab("editor");
    else setActiveTab("reporter");
  };

  if (loading) {
    return <div className="app-loading">Loading News Brief Desk...</div>;
  }

  if (!currentUser) {
    return <LoginModal onLoginSuccess={fetchUser} />;
  }

  return (
    <div className="app">
      <Navbar
        currentUser={currentUser}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onLogout={handleLogout}
      />

      <main className="main-content">
        {activeTab === "wire" && currentUser?.role === "REPORTER" && <RawWireView />}

        {activeTab === "stories" && (
          <StoryQueueView
            currentUser={currentUser}
            onSelectStoryForEdit={handleSelectStoryForEdit}
          />
        )}

        {activeTab === "reporter" && currentUser?.role === "REPORTER" && (
          <ReporterDesk
            currentUser={currentUser}
            initialSelectedStory={selectedStoryForEdit}
          />
        )}

        {activeTab === "editor" && currentUser?.role === "EDITOR" && (
          <EditorDesk currentUser={currentUser} />
        )}

        {activeTab === "deskhead" && currentUser?.role === "DESK_HEAD" && (
          <DeskHeadView currentUser={currentUser} />
        )}

        {activeTab === "sandbox" && <SandboxView />}
      </main>
    </div>
  );
}
