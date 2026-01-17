import React from 'react';
import './ProfessionalSidebar.css';

const ProfessionalSidebar = ({ 
  onNewChat, 
  onNavigate,
  currentView,
  isCollapsed,
  onToggleCollapse 
}) => {
  const resources = [
    { id: 'recent', icon: '🔔', title: 'Recent Updates', route: 'recent-updates' },
    { id: 'lookup', icon: '🔍', title: 'Case Lookup', route: 'case-lookup' },
    { id: 'amendments', icon: '📝', title: 'Amendments', route: 'amendments' },
    { id: 'documents', icon: '📄', title: 'Documents', route: 'documents' },
    { id: 'history', icon: '🕐', title: 'History', route: 'history' },
    { id: 'change-law', icon: '🔄', title: 'Change Law Type', route: 'change-law' },
    { id: 'settings', icon: '⚙️', title: 'Settings', route: 'settings' },
    { id: 'ai-summary', icon: '⚡', title: 'AI Summary', route: 'ai-summary' },
    { id: 'quick-summary', icon: '📊', title: 'Quick Summary', route: 'quick-summary' },
  ];

  return (
    <div className={`professional-sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      {/* Brand Section */}
      <div className="sidebar-brand">
        <div className="brand-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
            <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
        </div>
        {!isCollapsed && <h1 className="brand-title">LEGID</h1>}
      </div>

      {/* New Chat Button */}
      <button className="sidebar-new-chat" onClick={onNewChat}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        {!isCollapsed && <span>New Chat</span>}
      </button>

      {/* Search Chats */}
      {!isCollapsed && (
        <div className="sidebar-search">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
          <input type="text" placeholder="Search chats..." />
        </div>
      )}

      {/* Resources Header */}
      {!isCollapsed && (
        <div className="sidebar-section-header">
          <span>RESOURCES</span>
        </div>
      )}

      {/* Resource Grid */}
      <div className="sidebar-resources-grid">
        {resources.map((resource) => (
          <button
            key={resource.id}
            className={`resource-tile ${currentView === resource.route ? 'active' : ''}`}
            onClick={() => onNavigate(resource.route)}
            title={resource.title}
          >
            <span className="resource-icon">{resource.icon}</span>
            {!isCollapsed && <span className="resource-title">{resource.title}</span>}
          </button>
        ))}
      </div>

      {/* Spacer */}
      <div className="sidebar-spacer"></div>

      {/* User Profile (Bottom) */}
      <div className="sidebar-user-profile">
        <div className="user-avatar">
          <span>AP</span>
        </div>
        {!isCollapsed && (
          <div className="user-info">
            <div className="user-name">Achint Pal singh</div>
            <div className="user-role">Plus</div>
          </div>
        )}
        {!isCollapsed && (
          <button className="user-menu-btn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="1"></circle>
              <circle cx="12" cy="5" r="1"></circle>
              <circle cx="12" cy="19" r="1"></circle>
            </svg>
          </button>
        )}
      </div>
    </div>
  );
};

export default ProfessionalSidebar;
