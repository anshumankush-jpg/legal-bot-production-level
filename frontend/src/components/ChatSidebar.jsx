import React, { useState, useEffect } from 'react';
import './ChatSidebar.css';

const ChatSidebar = ({ 
  savedChats = [], 
  currentChatId, 
  onLoadChat, 
  onNewChat,
  onDeleteChat,
  onSearchChats,
  isCollapsed = false,
  onToggleCollapse,
  user,
  preferences = null,
  lawTypeSelection = null,
  onChangeLawType,
  onResetPreferences,
  onShowRecentUpdates,
  onShowCaseLookup,
  onShowAmendmentGenerator,
  onShowDocumentGenerator,
  onShowChatHistory,
  onShowSettings
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showProfileMenu, setShowProfileMenu] = useState(false);

  const getStoredUser = () => {
    try {
      const raw =
        localStorage.getItem('user_data') ||
        localStorage.getItem('legid_user') ||
        localStorage.getItem('auth_user');
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      return parsed?.user || parsed;
    } catch {
      return null;
    }
  };

  const getResolvedUser = () => {
    return user || getStoredUser() || preferences?.user || null;
  };

  const getUserName = () => {
    const resolved = getResolvedUser();
    return (
      resolved?.display_name ||
      resolved?.name ||
      resolved?.email ||
      preferences?.userName ||
      'User'
    );
  };

  const getUserInitials = () => {
    const name = getUserName();
    if (!name) return 'U';
    const base = name.includes('@') ? name.split('@')[0] : name;
    return base
      .split(' ')
      .filter(Boolean)
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  if (isCollapsed) {
    return (
      <div className="chat-sidebar collapsed">
        <button className="collapse-toggle" onClick={onToggleCollapse} title="Expand sidebar">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </button>
      </div>
    );
  }

  return (
    <div className="chat-sidebar">
      {/* Logo Header */}
      <div className="sidebar-logo-header">
        <div className="logo-brand">
          <div className="brand-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 3v18" />
              <path d="M5 7l7-4 7 4" />
              <circle cx="5" cy="11" r="3" />
              <circle cx="19" cy="11" r="3" />
              <path d="M5 14v4a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-4" />
            </svg>
          </div>
          <h1 className="brand-title">LEGID</h1>
        </div>
        <button className="back-btn" onClick={onToggleCollapse}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>
      </div>

      {/* New Chat Button */}
      <div className="new-chat-section">
        <button className="new-chat-btn" onClick={onNewChat}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          <span>New Chat</span>
        </button>
      </div>

      {/* Search */}
      <div className="search-section">
        <div className="search-wrapper">
          <svg className="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
          <input
            type="text"
            className="search-input"
            placeholder="Search chats..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Resources Section */}
      <div className="resources-section">
        <h2 className="section-title">RESOURCES</h2>
        
        <div className="resources-grid">
          {/* Recent Updates */}
          <button className="resource-card" onClick={onShowRecentUpdates}>
            <div className="card-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
              </svg>
            </div>
            <span className="card-label">Recent Updates</span>
          </button>

          {/* Case Lookup */}
          <button className="resource-card" onClick={onShowCaseLookup}>
            <div className="card-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8"></circle>
                <path d="m21 21-4.35-4.35"></path>
              </svg>
            </div>
            <span className="card-label">Case Lookup</span>
          </button>

          {/* Amendments */}
          <button className="resource-card" onClick={onShowAmendmentGenerator}>
            <div className="card-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="12" y1="18" x2="12" y2="12"></line>
                <line x1="9" y1="15" x2="15" y2="15"></line>
              </svg>
            </div>
            <span className="card-label">Amendments</span>
          </button>

          {/* Documents */}
          <button className="resource-card" onClick={onShowDocumentGenerator}>
            <div className="card-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <line x1="10" y1="9" x2="8" y2="9"></line>
              </svg>
            </div>
            <span className="card-label">Documents</span>
          </button>

          {/* History */}
          <button className="resource-card" onClick={onShowChatHistory}>
            <div className="card-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
            </div>
            <span className="card-label">History</span>
          </button>

          {/* Change Law Type */}
          <button className="resource-card" onClick={onChangeLawType}>
            <div className="card-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="23 4 23 10 17 10"></polyline>
                <polyline points="1 20 1 14 7 14"></polyline>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
              </svg>
            </div>
            <span className="card-label">Change Law Type</span>
          </button>

          {/* Settings */}
          <button className="resource-card" onClick={onShowSettings}>
            <div className="card-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="3"></circle>
                <path d="M12 1v6m0 6v6"></path>
                <path d="m4.93 4.93 2.83 2.83m8.48 8.48 2.83 2.83"></path>
                <path d="M1 12h6m6 0h6"></path>
                <path d="m4.93 19.07 2.83-2.83m8.48-8.48 2.83-2.83"></path>
              </svg>
            </div>
            <span className="card-label">Settings</span>
          </button>

          {/* AI Summary */}
          <button className="resource-card" onClick={onShowRecentUpdates}>
            <div className="card-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path>
              </svg>
            </div>
            <span className="card-label">AI Summary</span>
          </button>

          {/* Quick Summary */}
          <button className="resource-card" onClick={onShowRecentUpdates}>
            <div className="card-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
              </svg>
            </div>
            <span className="card-label">Quick Summary</span>
          </button>
        </div>
      </div>

      {/* Spacer */}
      <div className="flex-spacer"></div>

      {/* User Profile */}
      <div className="user-profile-section">
        <div className="profile-card" onClick={() => setShowProfileMenu(!showProfileMenu)}>
          <div className="profile-avatar">
            <span>{getUserInitials()}</span>
          </div>
          <span className="profile-name">{getUserName()}</span>
          <button className="profile-menu-btn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="1"></circle>
              <circle cx="19" cy="12" r="1"></circle>
              <circle cx="5" cy="12" r="1"></circle>
            </svg>
          </button>
        </div>

        {showProfileMenu && (
          <div className="profile-dropdown">
            <button className="dropdown-item" onClick={onChangeLawType}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M4 7h16M4 12h16M4 17h16"></path>
              </svg>
              <span>Change Law Type</span>
            </button>
            <button className="dropdown-item" onClick={onResetPreferences}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="3"></circle>
                <path d="M12 1v6m0 6v6"></path>
              </svg>
              <span>Change Settings</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatSidebar;
