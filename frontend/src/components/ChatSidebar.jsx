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
  onToggleCollapse
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredChats, setFilteredChats] = useState(savedChats);
  const [hoveredChatId, setHoveredChatId] = useState(null);

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

  const getChatIcon = (chat) => {
    // Determine icon based on chat content or metadata
    if (chat.messages && chat.messages.length > 0) {
      const firstMessage = chat.messages[0].content?.toLowerCase() || '';
      if (firstMessage.includes('criminal') || firstMessage.includes('crime')) return '⚖️';
      if (firstMessage.includes('traffic') || firstMessage.includes('speeding')) return '🚗';
      if (firstMessage.includes('family') || firstMessage.includes('divorce')) return '👨‍👩‍👧';
      if (firstMessage.includes('business') || firstMessage.includes('contract')) return '💼';
      if (firstMessage.includes('real estate') || firstMessage.includes('property')) return '🏠';
    }
    return '💬';
  };

  const handleDeleteClick = (e, chatId) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this chat?')) {
      onDeleteChat && onDeleteChat(chatId);
    }
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
      <div className="sidebar-header">
        <button className="new-chat-button" onClick={onNewChat}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          <span>New Chat</span>
        </button>
        
        <button className="collapse-toggle" onClick={onToggleCollapse} title="Collapse sidebar">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>
      </div>

      <div className="sidebar-search">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
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

      <div className="sidebar-section-header">
        <h3>Your Chats</h3>
        <span className="chat-count">{filteredChats.length}</span>
      </div>

      <div className="chats-list">
        {filteredChats.length === 0 ? (
          <div className="empty-state">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            <p>{searchQuery ? 'No chats found' : 'No chats yet'}</p>
            <small>{searchQuery ? 'Try a different search' : 'Start a new conversation'}</small>
          </div>
        ) : (
          filteredChats.map((chat) => (
            <div
              key={chat.id}
              className={`chat-item ${currentChatId === chat.id ? 'active' : ''}`}
              onClick={() => onLoadChat && onLoadChat(chat.id)}
              onMouseEnter={() => setHoveredChatId(chat.id)}
              onMouseLeave={() => setHoveredChatId(null)}
            >
              <div className="chat-item-icon">
                {getChatIcon(chat)}
              </div>
              
              <div className="chat-item-content">
                <div className="chat-item-title">
                  {chat.title || 'Untitled Chat'}
                </div>
                <div className="chat-item-preview">
                  {chat.messages && chat.messages.length > 0 
                    ? chat.messages[chat.messages.length - 1].content?.substring(0, 60) + '...'
                    : 'No messages'}
                </div>
                <div className="chat-item-meta">
                  <span className="chat-timestamp">
                    {formatTimestamp(chat.timestamp)}
                  </span>
                  <span className="chat-message-count">
                    {chat.messages?.length || 0} msg
                  </span>
                </div>
              </div>

              {hoveredChatId === chat.id && (
                <button 
                  className="delete-chat-btn"
                  onClick={(e) => handleDeleteClick(e, chat.id)}
                  title="Delete chat"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                  </svg>
                </button>
              )}
            </div>
          ))
        )}
      </div>

      <div className="sidebar-footer">
        <button className="footer-btn" onClick={onSearchChats} title="Advanced search">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
          <span>Advanced Search</span>
        </button>
      </div>
    </div>
  );
};

export default ChatSidebar;
