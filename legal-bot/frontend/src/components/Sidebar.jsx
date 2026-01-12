import React, { useState, useEffect } from 'react';
import './Sidebar.css';
import { RESOURCES, ICONS } from '../lib/resources.jsx';

// ResourceTile Component
const ResourceTile = ({ id, label, icon, isActive, onClick, isCollapsed }) => {
  const iconFn = ICONS[icon];
  
  return (
    <button
      className={`resource-tile ${isActive ? 'active' : ''}`}
      onClick={() => onClick(id)}
      aria-pressed={isActive}
      title={isCollapsed ? label : undefined}
    >
      <span className="resource-tile-icon">
        {iconFn && iconFn({ size: 16 })}
      </span>
      {!isCollapsed && <span className="resource-tile-label">{label}</span>}
    </button>
  );
};

// Sidebar Component
const Sidebar = ({
  activeResource,
  onResourceChange,
  onNewChat,
  onSearchChats,
  chatHistory = [],
  currentChatId,
  onSelectChat,
  isCollapsed = false,
  onToggleCollapse,
  lawTypeSelection,
  user
}) => {
  const [searchQuery, setSearchQuery] = useState('');

  // Persist active resource
  useEffect(() => {
    if (activeResource) {
      localStorage.setItem('legid_active_resource', activeResource);
    }
  }, [activeResource]);

  // Load persisted active resource
  useEffect(() => {
    const saved = localStorage.getItem('legid_active_resource');
    if (saved && !activeResource) {
      onResourceChange(saved);
    }
  }, []);

  const filteredChats = chatHistory.filter(chat => 
    chat.title?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleResourceClick = (resourceId) => {
    onResourceChange(resourceId);
  };

  return (
    <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      {/* Sidebar Header */}
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <span className="logo-icon">⚖️</span>
          {!isCollapsed && <span className="logo-text">LEGID</span>}
        </div>
        <button 
          className="collapse-btn"
          onClick={onToggleCollapse}
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? ICONS['chevron-right']({ size: 18 }) : ICONS['chevron-left']({ size: 18 })}
        </button>
      </div>

      {/* New Chat Button */}
      <button className="new-chat-btn" onClick={onNewChat}>
        {ICONS.plus({ size: 16 })}
        {!isCollapsed && <span>New Chat</span>}
      </button>

      {/* Search */}
      {!isCollapsed && (
        <div className="sidebar-search">
          {ICONS.search({ size: 14 })}
          <input
            type="text"
            placeholder="Search chats..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
        </div>
      )}

      <div className="sidebar-divider" />

      {/* Resources Section */}
      <div className="sidebar-section">
        {!isCollapsed && <h3 className="section-title">Resources</h3>}
        <div className={`resources-grid ${isCollapsed ? 'collapsed' : ''}`}>
          {RESOURCES.map((resource) => (
            <ResourceTile
              key={resource.id}
              id={resource.id}
              label={resource.label}
              icon={resource.icon}
              isActive={activeResource === resource.id}
              onClick={handleResourceClick}
              isCollapsed={isCollapsed}
            />
          ))}
        </div>
      </div>

      <div className="sidebar-divider" />

      {/* Chat History Section */}
      <div className="sidebar-section chats-section">
        {!isCollapsed && <h3 className="section-title">Your Chats</h3>}
        <div className="chat-list">
          {filteredChats.length > 0 ? (
            filteredChats.map((chat) => (
              <button
                key={chat.id}
                className={`chat-item ${currentChatId === chat.id ? 'active' : ''}`}
                onClick={() => onSelectChat(chat.id)}
                title={chat.title}
              >
                {ICONS.chat({ size: 14 })}
                {!isCollapsed && (
                  <span className="chat-title">{chat.title || 'Untitled Chat'}</span>
                )}
              </button>
            ))
          ) : (
            !isCollapsed && (
              <div className="no-chats">
                <p>No chats yet</p>
              </div>
            )
          )}
        </div>
      </div>

      {/* Current Law Type */}
      {!isCollapsed && lawTypeSelection && (
        <div className="sidebar-footer">
          <div className="current-context">
            <span className="context-label">Current:</span>
            <span className="context-value">{lawTypeSelection.lawType}</span>
          </div>
        </div>
      )}
    </aside>
  );
};

export default Sidebar;
