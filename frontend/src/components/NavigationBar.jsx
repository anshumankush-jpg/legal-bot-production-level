import React, { useState } from 'react';
import './NavigationBar.css';

const NavigationBar = ({ 
  onNewChat, 
  onSearchChats, 
  onShowImages, 
  onShowApps,
  onShowCodex,
  onShowProjects,
  currentView = 'chat'
}) => {
  const [activeView, setActiveView] = useState(currentView);

  const handleViewChange = (view, callback) => {
    setActiveView(view);
    if (callback) callback();
  };

  return (
    <div className="navigation-bar">
      <div className="nav-left">
        <div className="nav-logo">
          <span className="logo-icon">⚖️</span>
          <span className="logo-text">LEGID</span>
        </div>
      </div>

      <div className="nav-center">
        <button 
          className={`nav-btn ${activeView === 'chat' ? 'active' : ''}`}
          onClick={() => handleViewChange('chat', onNewChat)}
          title="Start a new chat"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
          <span>New Chat</span>
        </button>

        <button 
          className={`nav-btn ${activeView === 'search' ? 'active' : ''}`}
          onClick={() => handleViewChange('search', onSearchChats)}
          title="Search your chat history"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
          <span>Search Chats</span>
        </button>

        <button 
          className={`nav-btn ${activeView === 'images' ? 'active' : ''}`}
          onClick={() => handleViewChange('images', onShowImages)}
          title="View uploaded images and documents"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
            <circle cx="8.5" cy="8.5" r="1.5"></circle>
            <polyline points="21 15 16 10 5 21"></polyline>
          </svg>
          <span>Images</span>
        </button>

        <button 
          className={`nav-btn ${activeView === 'apps' ? 'active' : ''}`}
          onClick={() => handleViewChange('apps', onShowApps)}
          title="Legal apps and tools"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="3" width="7" height="7"></rect>
            <rect x="14" y="3" width="7" height="7"></rect>
            <rect x="14" y="14" width="7" height="7"></rect>
            <rect x="3" y="14" width="7" height="7"></rect>
          </svg>
          <span>Apps</span>
        </button>

        <button 
          className={`nav-btn ${activeView === 'codex' ? 'active' : ''}`}
          onClick={() => handleViewChange('codex', onShowCodex)}
          title="Legal codex and statutes"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
          </svg>
          <span>Codex</span>
        </button>

        <button 
          className={`nav-btn ${activeView === 'projects' ? 'active' : ''}`}
          onClick={() => handleViewChange('projects', onShowProjects)}
          title="Your legal projects and cases"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
          </svg>
          <span>Projects</span>
        </button>
      </div>

      <div className="nav-right">
        <button className="nav-icon-btn" title="Notifications">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
          </svg>
        </button>

        <button className="nav-icon-btn" title="Settings">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M12 1v6m0 6v6m5.66-13.66l-4.24 4.24m-2.83 2.83l-4.24 4.24m13.66-5.66l-4.24-4.24m-2.83-2.83l-4.24-4.24"></path>
          </svg>
        </button>

        <div className="nav-profile">
          <div className="profile-avatar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NavigationBar;
