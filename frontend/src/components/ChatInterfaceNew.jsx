import React, { useState } from 'react';
import './ChatInterfaceNew.css';
import ChatSidebar from './ChatSidebar';
import ChatHeader from './ChatHeader';

const ChatInterfaceNew = ({ preferences, lawTypeSelection, onResetPreferences, onChangeLawType, user }) => {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'user',
      content: 'hii',
      timestamp: new Date().toLocaleTimeString('en-US', { hour12: true })
    },
    {
      id: 2,
      role: 'assistant',
      content: 'Hi 👋\n\nHow can I help you today?\n\nIf you want, we can jump straight into:\n\n• Recent legal updates for your area\n• Case lookup and legal research\n• Document generation & amendments\n• Legal advice for your specific situation\n• or anything else on your mind\n\nJust tell me what you\'d like to work on.',
      timestamp: new Date().toLocaleTimeString('en-US', { hour12: true })
    }
  ]);

  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const newMessage = {
      id: Date.now(),
      role: 'user',
      content: input,
      timestamp: new Date().toLocaleTimeString('en-US', { hour12: true })
    };

    setMessages([...messages, newMessage]);
    setInput('');
    setLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'TITLE: RESPONSE\n\nEXECUTIVE SUMMARY\n\n• Processing your request.\n\n• Providing relevant legal information.',
        timestamp: new Date().toLocaleTimeString('en-US', { hour12: true })
      };
      setMessages(prev => [...prev, aiResponse]);
      setLoading(false);
    }, 2000);
  };

  const handleNewChat = () => {
    setMessages([]);
    setInput('');
    setLoading(false);
  };

  return (
    <div className="chat-layout-container">
      {/* Sidebar */}
      <ChatSidebar 
        savedChats={[]}
        currentChatId={null}
        onLoadChat={() => {}}
        onNewChat={handleNewChat}
        onDeleteChat={() => {}}
        onSearchChats={() => {}}
        isCollapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        user={user}
        preferences={preferences}
        lawTypeSelection={lawTypeSelection}
        onChangeLawType={onChangeLawType}
        onResetPreferences={onResetPreferences}
        onShowRecentUpdates={() => {}}
        onShowCaseLookup={() => {}}
        onShowAmendmentGenerator={() => {}}
        onShowDocumentGenerator={() => {}}
        onShowChatHistory={() => {}}
        onShowSettings={onResetPreferences}
      />

      {/* Main Chat Area */}
      <div className="main-chat-container">
        {/* Header */}
        <ChatHeader
          preferences={preferences}
          user={user}
          lawTypeSelection={lawTypeSelection}
          onNewChat={handleNewChat}
          onChangeLawType={onChangeLawType}
          onResetPreferences={onResetPreferences}
          onShowRecentUpdates={() => {}}
          onShowCaseLookup={() => {}}
          onShowAmendmentGenerator={() => {}}
          onShowDocumentGenerator={() => {}}
          onShowChatHistory={() => {}}
          onShowSettings={onResetPreferences}
          onShowAISummary={() => {}}
          onShowQuickSummary={() => {}}
        />

        {/* Messages Area */}
        <div className="messages-display-area">
          <div className="thread-inner">
            {messages.map((message) => (
              <div key={message.id} className={`message-row ${message.role}`}>
                <div className="message-box">
                  <div className="message-text-content">{message.content}</div>
                  {message.timestamp && (
                    <div className="message-timestamp">{message.timestamp}</div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* LEGID THINKING Indicator (Typing Dots) */}
          {loading && (
            <div className="thinking-indicator">
              <span className="thinking-pulse"></span>
              <span className="thinking-pulse"></span>
              <span className="thinking-pulse"></span>
              <span className="thinking-label">LEGID THINKING</span>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="input-section">
          <form onSubmit={handleSend} className="input-form-container">
            <div className="input-field-wrapper">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about legal documents or traffic laws..."
                className="main-input-field"
                disabled={loading}
                autoFocus
              />

              <div className="input-buttons-group">
                <button type="button" className="plus-btn" title="Attach files">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <line x1="12" y1="5" x2="12" y2="19"></line>
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                  </svg>
                </button>

                <button type="button" className="mic-btn" title="Voice input">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"></path>
                    <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"></path>
                  </svg>
                </button>

                <button type="submit" className="send-btn-text" disabled={!input.trim() || loading}>
                  Send
                </button>
              </div>
            </div>

            <div className="input-footer-disclaimer">
              This is general information only, not legal advice. Consult a licensed lawyer for advice about your specific case.
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ChatInterfaceNew;
