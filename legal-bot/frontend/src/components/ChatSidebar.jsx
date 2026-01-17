import React, { useState, useEffect } from 'react';
import './ChatSidebar.css';
import SidebarResourcesGrid from './SidebarResourcesGrid';
import AccountSwitcherModal from './AccountSwitcherModal';

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
  onLogout,
  activeResource,
  onResourceClick,
  onNavigate
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredChats, setFilteredChats] = useState(savedChats);
  const [hoveredChatId, setHoveredChatId] = useState(null);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [showHelpMenu, setShowHelpMenu] = useState(false);
  const [showAccountSwitcher, setShowAccountSwitcher] = useState(false);

  useEffect(() => {
    if (searchQuery.trim()) {
      const filtered = savedChats.filter(chat => 
        chat.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        chat.messages?.some(msg => 
          msg.content?.toLowerCase().includes(searchQuery.toLowerCase())
        )
      );
      setFilteredChats(filtered);
    } else {
      setFilteredChats(savedChats);
    }
  }, [searchQuery, savedChats]);

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const handleDeleteClick = (e, chatId) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this chat?')) {
      onDeleteChat && onDeleteChat(chatId);
    }
  };

  const groupChatsByTime = (chats) => {
    const groups = {
      Today: [],
      Yesterday: [],
      'Previous 7 days': [],
      Older: []
    };
    const now = new Date();
    chats.forEach(chat => {
      const dateValue = chat.last_message_at || chat.updated_at || chat.created_at;
      const chatDate = dateValue ? new Date(dateValue) : new Date();
      const diffMs = now - chatDate;
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
      if (diffDays === 0) {
        groups.Today.push(chat);
      } else if (diffDays === 1) {
        groups.Yesterday.push(chat);
      } else if (diffDays <= 7) {
        groups['Previous 7 days'].push(chat);
      } else {
        groups.Older.push(chat);
      }
    });
    return groups;
  };

  const getInitials = (name) => {
    if (!name) return '?';
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
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

  const handleResourceClick = (resourceId) => {
    if (onResourceClick) {
      onResourceClick(resourceId);
    }
  };

  return (
    <div className="chat-sidebar">
      {/* LEGID Logo/Title Section - Matching Screenshot */}
      <div className="sidebar-logo">
        <div className="logo-container">
          <div className="logo-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 17L12 22L22 17" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 12L12 17L22 12" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <span className="logo-text">LEGID</span>
        </div>
        <button className="collapse-toggle" onClick={onToggleCollapse} title="Collapse sidebar">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>
      </div>

      {/* New Chat Button */}
      <div className="sidebar-new-chat">
        <button className="new-chat-button" onClick={onNewChat}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          <span>New Chat</span>
        </button>
      </div>

      {/* Search Chats Input - Always Visible */}
      <div className="sidebar-search">
        <svg className="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="11" cy="11" r="8"></circle>
          <path d="m21 21-4.35-4.35"></path>
        </svg>
        <input
          type="text"
          placeholder="Search chats..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        {searchQuery && (
          <button className="clear-search" onClick={() => setSearchQuery('')}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        )}
      </div>

      {/* Divider */}
      <div className="sidebar-divider"></div>

      {/* RESOURCES Section */}
      <div className="sidebar-resources-section">
        <div className="resources-header">
          <span>RESOURCES</span>
        </div>
        <SidebarResourcesGrid 
          activeResource={activeResource}
          onResourceClick={handleResourceClick}
          isCollapsed={false}
        />
      </div>

      {/* Your Chats Section */}
      <div className="sidebar-section chats-section">
        <div className="section-header">
          <span>Your Chats</span>
          <span className="chat-count">{filteredChats.length}</span>
        </div>
        <div className="chats-list">
          {filteredChats.length === 0 ? (
            <div className="empty-state">
              <p>{searchQuery ? 'No chats found' : 'No chats yet'}</p>
            </div>
          ) : (
            Object.entries(groupChatsByTime(filteredChats)).map(([groupName, chats]) => (
              chats.length > 0 && (
                <div key={groupName} className="chat-group">
                  <div className="chat-group-title">{groupName}</div>
                  {chats.map((chat) => (
                    <div
                      key={chat.id}
                      className={`chat-item ${currentChatId === chat.id ? 'active' : ''}`}
                      onClick={() => onLoadChat && onLoadChat(chat.id)}
                      onMouseEnter={() => setHoveredChatId(chat.id)}
                      onMouseLeave={() => setHoveredChatId(null)}
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                      </svg>
                      <span className="chat-title">{chat.title || 'Untitled Chat'}</span>
                      
                      {hoveredChatId === chat.id && (
                        <button 
                          className="delete-chat-btn"
                          onClick={(e) => handleDeleteClick(e, chat.id)}
                          title="Delete chat"
                        >
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <polyline points="3 6 5 6 21 6"></polyline>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                          </svg>
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )
            ))
          )}
        </div>
      </div>

      {/* User Profile Footer - Matching Screenshot */}
      <div className="sidebar-footer">
        <div className="user-profile-item" onClick={() => setShowProfileMenu(!showProfileMenu)}>
          <div className="user-avatar">
            {user?.profile_photo_url ? (
              <img src={user.profile_photo_url} alt={user.name} />
            ) : (
              <span>{getInitials(user?.name || 'User')}</span>
            )}
          </div>
          <div className="user-info">
            <div className="user-name">{user?.name || 'User'}</div>
            <div className="user-role">{user?.role || 'client'}</div>
          </div>
          <button className="profile-menu-btn" onClick={(e) => { e.stopPropagation(); setShowProfileMenu(!showProfileMenu); }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="1"></circle>
              <circle cx="12" cy="5" r="1"></circle>
              <circle cx="12" cy="19" r="1"></circle>
            </svg>
          </button>
        </div>
        
        {showProfileMenu && (
          <div className="profile-menu-dropdown">
            <div className="profile-menu-header">
              <div className="profile-menu-name">{user?.name || 'User'}</div>
              <div className="profile-menu-email">{user?.email || ''}</div>
            </div>
            <div className="profile-menu-divider"></div>
            <button className="profile-menu-item" onClick={() => { setShowProfileMenu(false); setShowAccountSwitcher(true); }}>
              Add account
            </button>
            <button className="profile-menu-item" onClick={() => { setShowProfileMenu(false); onNavigate && onNavigate('settings'); }}>
              Settings
            </button>
            <button className="profile-menu-item" onClick={() => { setShowProfileMenu(false); onNavigate && onNavigate('personalization'); }}>
              Personalization
            </button>
            <button className="profile-menu-item" onClick={() => { setShowHelpMenu(!showHelpMenu); }}>
              Help
            </button>
            {showHelpMenu && (
              <div className="profile-menu-submenu">
                <button className="profile-menu-item" onClick={() => { setShowProfileMenu(false); onNavigate && onNavigate('help-center'); }}>
                  Help Center
                </button>
                <button className="profile-menu-item" onClick={() => { setShowProfileMenu(false); onNavigate && onNavigate('release-notes'); }}>
                  Release Notes
                </button>
                <button className="profile-menu-item" onClick={() => { setShowProfileMenu(false); onNavigate && onNavigate('terms'); }}>
                  Terms & Policies
                </button>
                <button className="profile-menu-item" onClick={() => window.open('mailto:info@predictivetechlabs.com?subject=Report%20a%20bug')}>
                  Report Bug
                </button>
                <button className="profile-menu-item" onClick={() => { setShowProfileMenu(false); onNavigate && onNavigate('keyboard-shortcuts'); }}>
                  Keyboard Shortcuts
                </button>
              </div>
            )}
            <button className="profile-menu-item logout" onClick={() => { setShowProfileMenu(false); onLogout && onLogout(); }}>
              Log out
            </button>
          </div>
        )}
      </div>

      <AccountSwitcherModal
        isOpen={showAccountSwitcher}
        onClose={() => setShowAccountSwitcher(false)}
        onAddAccount={() => window.location.href = '/'}
        onSwitched={() => window.location.reload()}
      />
    </div>
  );
};

export default ChatSidebar;
