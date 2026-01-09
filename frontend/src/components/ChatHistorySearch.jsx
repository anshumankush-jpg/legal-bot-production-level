import React, { useState, useEffect } from 'react';
import './ChatHistorySearch.css';

const ChatHistorySearch = ({ userId, onClose, onMessageSelect, onLoadChat }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [sessions, setSessions] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [activeTab, setActiveTab] = useState('sessions'); // 'sessions' or 'search'
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadSessions();
  }, [userId]);

  const loadSessions = async () => {
    setLoading(true);
    setError('');

    try {
      // First try to load from localStorage (fallback)
      const localChats = localStorage.getItem('legubot_chats');
      if (localChats) {
        const chats = JSON.parse(localChats);
        // Convert to session format
        const localSessions = chats.map(chat => ({
          session_id: chat.id || Date.now(),
          last_message: chat.title || chat.messages?.[0]?.content?.substring(0, 100) || 'No messages',
          last_timestamp: chat.timestamp || new Date().toISOString(),
          message_count: chat.messages?.length || 0,
          messages: chat.messages || []
        }));
        setSessions(localSessions);
        setLoading(false);
        return;
      }

      // Try backend API as secondary option
      const response = await fetch(`http://localhost:8000/api/chat-history/sessions/${userId}`);
      
      if (!response.ok) {
        throw new Error('Backend not available');
      }
      
      const data = await response.json();

      if (data.success) {
        setSessions(data.sessions || []);
      } else {
        // If backend fails, show localStorage data
        setSessions([]);
      }
    } catch (err) {
      // Silently fail and show localStorage data (already loaded above)
      console.log('Using localStorage for chat history');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setError('Please enter a search query');
      return;
    }

    setLoading(true);
    setError('');
    setSearchResults([]);

    try {
      // Search in localStorage first
      const localChats = localStorage.getItem('legubot_chats');
      if (localChats) {
        const chats = JSON.parse(localChats);
        const query = searchQuery.toLowerCase();
        
        // Search through all messages
        const results = [];
        chats.forEach(chat => {
          chat.messages?.forEach(msg => {
            const content = (msg.content || msg.answer || '').toLowerCase();
            if (content.includes(query)) {
              results.push({
                message_id: msg.id || Date.now(),
                session_id: chat.id,
                message: msg.role === 'user' ? msg.content : '',
                response: msg.role === 'assistant' ? (msg.content || msg.answer) : '',
                timestamp: msg.timestamp || chat.timestamp,
                metadata: {
                  law_category: chat.lawType || 'General'
                }
              });
            }
          });
        });
        
        setSearchResults(results);
        setActiveTab('search');
        setLoading(false);
        return;
      }

      // Try backend API as fallback
      const response = await fetch('http://localhost:8000/api/chat-history/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          search_query: searchQuery,
          limit: 20
        })
      });

      if (!response.ok) {
        throw new Error('Backend not available');
      }

      const data = await response.json();

      if (data.success) {
        setSearchResults(data.results || []);
        setActiveTab('search');
      }
    } catch (err) {
      console.log('Search completed using localStorage');
    } finally {
      setLoading(false);
    }
  };

  const loadSessionMessages = async (sessionId) => {
    setLoading(true);
    setError('');

    try {
      // Load from localStorage
      const localChats = localStorage.getItem('legubot_chats');
      if (localChats) {
        const chats = JSON.parse(localChats);
        const session = chats.find(c => c.id === sessionId);
        
        if (session && session.messages) {
          // Convert messages to search result format
          const messages = session.messages.map(msg => ({
            message_id: msg.id || Date.now(),
            session_id: sessionId,
            message: msg.role === 'user' ? msg.content : '',
            response: msg.role === 'assistant' ? (msg.content || msg.answer) : '',
            timestamp: msg.timestamp || session.timestamp,
            metadata: {
              law_category: session.lawType || 'General'
            }
          }));
          
          setSearchResults(messages);
          setActiveTab('search');
          setLoading(false);
          return;
        }
      }

      // Try backend as fallback
      const response = await fetch(`http://localhost:8000/api/chat-history/session/${userId}/${sessionId}`);
      
      if (!response.ok) {
        throw new Error('Backend not available');
      }
      
      const data = await response.json();

      if (data.success) {
        setSearchResults(data.messages || []);
        setActiveTab('search');
      }
    } catch (err) {
      console.log('Loaded session from localStorage');
    } finally {
      setLoading(false);
    }
  };

  const deleteSession = async (sessionId, e) => {
    e.stopPropagation();
    
    if (!confirm('Are you sure you want to delete this chat session?')) {
      return;
    }

    try {
      // Delete from localStorage
      const localChats = localStorage.getItem('legubot_chats');
      if (localChats) {
        const chats = JSON.parse(localChats);
        const updated = chats.filter(c => c.id !== sessionId);
        localStorage.setItem('legubot_chats', JSON.stringify(updated));
        
        // Reload sessions
        loadSessions();
        return;
      }

      // Try backend as fallback
      const response = await fetch(`http://localhost:8000/api/chat-history/session/${userId}/${sessionId}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error('Backend not available');
      }

      const data = await response.json();

      if (data.success) {
        loadSessions();
      }
    } catch (err) {
      console.log('Deleted session from localStorage');
      loadSessions();
    }
  };

  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    
    return date.toLocaleDateString();
  };

  const highlightText = (text, query) => {
    if (!query) return text;
    
    const parts = text.split(new RegExp(`(${query})`, 'gi'));
    return parts.map((part, i) => 
      part.toLowerCase() === query.toLowerCase() ? 
        <mark key={i}>{part}</mark> : part
    );
  };

  return (
    <div className="chat-history-overlay">
      <div className="chat-history-modal">
        <div className="chat-history-header">
          <h2>💬 Chat History</h2>
          <button className="close-button" onClick={onClose}>✕</button>
        </div>

        <div className="chat-history-content">
          <div className="search-bar">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search your chat history..."
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button onClick={handleSearch} disabled={loading}>
              {loading ? '⏳' : '🔍'}
            </button>
          </div>

          <div className="tabs">
            <button 
              className={`tab ${activeTab === 'sessions' ? 'active' : ''}`}
              onClick={() => setActiveTab('sessions')}
            >
              📋 Sessions ({sessions.length})
            </button>
            <button 
              className={`tab ${activeTab === 'search' ? 'active' : ''}`}
              onClick={() => setActiveTab('search')}
            >
              🔍 Search Results ({searchResults.length})
            </button>
          </div>

          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}

          {activeTab === 'sessions' && (
            <div className="sessions-list">
              {sessions.length === 0 ? (
                <div className="empty-state">
                  <p>No chat sessions yet</p>
                  <small>Start chatting to create your first session</small>
                </div>
              ) : (
                sessions.map((session) => (
                  <div 
                    key={session.session_id} 
                    className="session-item"
                    onClick={() => {
                      // If onLoadChat callback exists, use it to load the full chat
                      if (onLoadChat) {
                        onLoadChat(session.session_id);
                        onClose && onClose();
                      } else {
                        // Otherwise, show messages in the modal
                        loadSessionMessages(session.session_id);
                      }
                    }}
                  >
                    <div className="session-content">
                      <div className="session-preview">
                        {session.last_message}
                      </div>
                      <div className="session-meta">
                        <span className="session-time">
                          {formatDate(session.last_timestamp)}
                        </span>
                        <span className="session-count">
                          {session.message_count} message{session.message_count !== 1 ? 's' : ''}
                        </span>
                      </div>
                    </div>
                    <button 
                      className="delete-button"
                      onClick={(e) => deleteSession(session.session_id, e)}
                      title="Delete session"
                    >
                      🗑️
                    </button>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'search' && (
            <div className="search-results-list">
              {searchResults.length === 0 ? (
                <div className="empty-state">
                  <p>No results found</p>
                  <small>Try a different search query</small>
                </div>
              ) : (
                searchResults.map((message, index) => (
                  <div 
                    key={message.message_id || index} 
                    className="message-item"
                    onClick={() => onMessageSelect && onMessageSelect(message)}
                  >
                    <div className="message-header">
                      <span className="message-time">
                        {formatDate(message.timestamp)}
                      </span>
                      {message.metadata?.law_category && (
                        <span className="message-category">
                          {message.metadata.law_category}
                        </span>
                      )}
                    </div>
                    <div className="message-content">
                      <div className="message-question">
                        <strong>Q:</strong> {highlightText(message.message, searchQuery)}
                      </div>
                      <div className="message-answer">
                        <strong>A:</strong> {highlightText(message.response?.substring(0, 200) || '', searchQuery)}
                        {message.response?.length > 200 && '...'}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatHistorySearch;
