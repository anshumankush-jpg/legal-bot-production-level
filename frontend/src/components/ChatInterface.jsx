import React, { useState, useRef, useEffect } from 'react';
import './ChatInterface.css';
import EnhancedLegalResponse from './EnhancedLegalResponse';

const API_URL = 'http://localhost:8000';

const ChatInterface = ({ preferences, onResetPreferences }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingStage, setLoadingStage] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [offenceNumber, setOffenceNumber] = useState('');
  const [userId] = useState('test_user_' + Date.now()); // For demo purposes
  const [showUploadMenu, setShowUploadMenu] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const imageInputRef = useRef(null);
  const pdfInputRef = useRef(null);
  const docInputRef = useRef(null);
  const textInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Close upload menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showUploadMenu && !event.target.closest('.upload-menu-container')) {
        setShowUploadMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showUploadMenu]);

  // Add system message helper
  const addSystemMessage = (content, isTemporary = false) => {
    const message = {
      id: Date.now(),
      role: 'system',
      content,
      timestamp: new Date(),
      isTemporary
    };
    setMessages(prev => [...prev, message]);

    // Auto-remove temporary messages after 5 seconds
    if (isTemporary) {
      setTimeout(() => {
        setMessages(prev => prev.filter(msg => msg.id !== message.id));
      }, 5000);
    }
  };

  // Handle file upload
  const handleFileUpload = async (file) => {
    if (!file) return;

    setUploadProgress(0);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);
    if (offenceNumber) {
      formData.append('offence_number', offenceNumber);
    }

    // Add temporary upload message
    const tempMessage = addSystemMessage(`Uploading ${file.name}...`, true);

    try {
      const response = await fetch(`${API_URL}/api/artillery/upload`, {
        method: 'POST',
        body: formData,
        // Simulate progress (in real implementation, you'd use XMLHttpRequest for progress)
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();

      // Remove temporary message and add success message
      setMessages(prev => prev.filter(msg => !msg.isTemporary));

      addSystemMessage(`✅ Document "${file.name}" uploaded and indexed. ${result.chunks_indexed || 0} chunks processed.`);

      // Auto-fill offence number if detected and not already set
      if (result.detected_offence_number && !offenceNumber) {
        setOffenceNumber(result.detected_offence_number);
        addSystemMessage(`🔍 Detected offence number: ${result.detected_offence_number}`, true);
      }

      setUploadProgress(100);
      setTimeout(() => setUploadProgress(0), 2000); // Hide progress after 2 seconds

    } catch (error) {
      // Remove temporary message and add error message
      setMessages(prev => prev.filter(msg => !msg.isTemporary));
      addSystemMessage(`❌ Upload failed: ${error.message}`);
      console.error('Upload error:', error);
      setUploadProgress(0);
    }
  };

  // Handle file selection
  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      handleFileUpload(file);
      setShowUploadMenu(false);
    }
  };

  // Handle different file type uploads
  const handleImageUpload = () => {
    imageInputRef.current?.click();
  };

  const handlePDFUpload = () => {
    pdfInputRef.current?.click();
  };

  const handleDocUpload = () => {
    docInputRef.current?.click();
  };

  const handleTextUpload = () => {
    textInputRef.current?.click();
  };

  // Get language name from code
  const getLanguageName = (code) => {
    const languages = {
      'en': 'English',
      'fr': 'French',
      'es': 'Spanish',
      'hi': 'Hindi',
      'pa': 'Punjabi',
      'zh': 'Chinese'
    };
    return languages[code] || code;
  };

  // Get country name
  const getCountryName = (code) => {
    return code === 'CA' ? 'Canada' : code === 'US' ? 'United States' : code;
  };

  // Handle chat message send
  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const question = input.trim();
    setInput('');
    setLoading(true);
    setLoadingStage('Searching documents...');

    try {
      // Build request payload with preferences
      const payload = {
        message: question,
        offence_number: offenceNumber || undefined,
        top_k: 5
      };

      // Add preferences if available
      if (preferences) {
        if (preferences.language) {
          payload.language = preferences.language.code;
        }
        if (preferences.country) {
          payload.country = preferences.country;
        }
        if (preferences.province) {
          payload.province = preferences.province;
        }
      }

      // Add timeout warning after 10 seconds
      const timeoutWarning = setTimeout(() => {
        setLoadingStage('Generating response (this may take a moment)...');
      }, 10000);

      const response = await fetch(`${API_URL}/api/artillery/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`Chat failed: ${response.status} ${response.statusText}`);
      }

      clearTimeout(timeoutWarning);
      setLoadingStage('Processing response...');
      const data = await response.json();

      const assistantMessage = {
        id: Date.now(),
        role: 'assistant',
        content: data.answer,
        answer: data.answer, // Also include as 'answer' for EnhancedLegalResponse compatibility
        citations: data.citations || [],
        chunks_used: data.chunks_used || 0,
        confidence: data.confidence || 0,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      clearTimeout(timeoutWarning);
      console.error('Chat error:', error);
      const errorMessage = {
        id: Date.now(),
        role: 'assistant',
        content: `❌ Sorry, I encountered an error: ${error.message}\n\nPlease make sure the backend is running and try again.`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      setLoadingStage('');
    }
  };

  // Quick test functions for browser console
  useEffect(() => {
    window.testUpload = () => {
      const testFile = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
      handleFileUpload(testFile);
    };

    window.testChat = () => {
      setInput('What are the penalties for speeding?');
      setTimeout(() => {
        const form = document.querySelector('form');
        if (form) form.requestSubmit();
      }, 100);
    };

    window.clearChat = () => {
      setMessages([]);
    };
  }, []);

  return (
    <div className="chat-interface">
      {/* Header */}
      <div className="chat-header">
        <div className="header-left">
          <h1>⚖️ PLAZA-AI Legal Assistant</h1>
          {preferences && (
            <div className="preferences-badge">
              <span className="pref-item">
                🌐 {getLanguageName(preferences.language?.code || 'en')}
              </span>
              <span className="pref-item">
                {preferences.country === 'CA' ? '🇨🇦' : '🇺🇸'} {getCountryName(preferences.country)}
              </span>
              {preferences.province && (
                <span className="pref-item">
                  📍 {preferences.province}
                </span>
              )}
              {onResetPreferences && (
                <button className="reset-prefs-btn" onClick={onResetPreferences} title="Change preferences">
                  ⚙️
                </button>
              )}
            </div>
          )}
        </div>
        <div className="offence-input">
          <label>Offence Number (optional):</label>
          <input
            type="text"
            value={offenceNumber}
            onChange={(e) => setOffenceNumber(e.target.value)}
            placeholder="e.g., 123456789"
            className="offence-field"
          />
        </div>
      </div>

      {/* Progress Bar */}
      {uploadProgress > 0 && uploadProgress < 100 && (
        <div className="upload-progress">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
          <span>Uploading... {uploadProgress}%</span>
        </div>
      )}

      {/* Messages Area */}
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <h2>Welcome to PLAZA-AI Legal Assistant</h2>
            <p>Upload a legal document to get started, or ask me questions about traffic laws.</p>
            <div className="quick-actions">
              <button onClick={() => setInput('What are the penalties for speeding?')}>
                🚗 Speeding Penalties
              </button>
              <button onClick={() => setInput('How do I dispute a traffic ticket?')}>
                ⚖️ Dispute Process
              </button>
              <button onClick={() => setInput('What are demerit points?')}>
                📊 Demerit Points
              </button>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div key={message.id} className={`message ${message.role}`}>
              <div className="message-content">
                {/* Enhanced Legal Response for structured answers */}
                {message.role === 'assistant' ? (
                  <EnhancedLegalResponse response={message} />
                ) : (
                  <div className="message-text">
                    {message.content}
                  </div>
                )}

                {/* Fallback citations display for non-enhanced responses */}
                {message.role === 'assistant' && !message.content.includes('🎯 OFFENSE:') && message.citations && message.citations.length > 0 && (
                  <div className="citations">
                    <strong>Legal Citations:</strong>
                    {message.citations.map((citation, index) => (
                      <div key={index} className="citation-item">
                        <span className="citation-file">{citation.filename}</span>
                        {citation.page && <span className="citation-page">Page {citation.page}</span>}
                        {citation.score && <span className="citation-score">({(citation.score * 100).toFixed(0)}% match)</span>}
                      </div>
                    ))}
                    {message.chunks_used && (
                      <div className="chunks-info">
                        Used {message.chunks_used} legal passages from documents
                      </div>
                    )}
                  </div>
                )}

                {/* Message timestamp */}
                <div className="message-time">
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))
        )}

        {/* Typing indicator */}
        {loading && (
          <div className="message assistant">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
              {loadingStage && (
                <div className="loading-stage" style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: '#888' }}>
                  {loadingStage}
                </div>
              )}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form className="input-area" onSubmit={handleSend}>
        <div className="input-container">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about legal documents or traffic laws..."
            className="chat-input"
            disabled={loading}
          />

          {/* Hidden file inputs for different types */}
          <input
            ref={imageInputRef}
            type="file"
            onChange={handleFileSelect}
            accept=".png,.jpg,.jpeg,.gif,.webp"
            style={{ display: 'none' }}
          />
          <input
            ref={pdfInputRef}
            type="file"
            onChange={handleFileSelect}
            accept=".pdf"
            style={{ display: 'none' }}
          />
          <input
            ref={docInputRef}
            type="file"
            onChange={handleFileSelect}
            accept=".doc,.docx"
            style={{ display: 'none' }}
          />
          <input
            ref={textInputRef}
            type="file"
            onChange={handleFileSelect}
            accept=".txt,.md"
            style={{ display: 'none' }}
          />

          {/* Plus icon for upload menu */}
          <div className="upload-menu-container">
            <button
              type="button"
              className="plus-upload-btn"
              onClick={() => setShowUploadMenu(!showUploadMenu)}
              disabled={loading}
              title="Upload document"
            >
              <span className="plus-icon">+</span>
            </button>

            {/* Upload menu dropdown */}
            {showUploadMenu && (
              <div className="upload-menu">
                <button
                  type="button"
                  className="upload-menu-item"
                  onClick={handleImageUpload}
                >
                  <span className="menu-icon">🖼️</span>
                  <span>Image</span>
                </button>
                <button
                  type="button"
                  className="upload-menu-item"
                  onClick={handlePDFUpload}
                >
                  <span className="menu-icon">📄</span>
                  <span>PDF</span>
                </button>
                <button
                  type="button"
                  className="upload-menu-item"
                  onClick={handleDocUpload}
                >
                  <span className="menu-icon">📝</span>
                  <span>Document</span>
                </button>
                <button
                  type="button"
                  className="upload-menu-item"
                  onClick={handleTextUpload}
                >
                  <span className="menu-icon">📃</span>
                  <span>Text</span>
                </button>
              </div>
            )}
          </div>

          {/* Send button */}
          <button
            type="submit"
            className="send-btn"
            disabled={!input.trim() || loading}
          >
            {loading ? '⏳' : '➤'}
          </button>
        </div>

        <div className="input-footer">
          This is general information only, not legal advice. Consult a licensed lawyer for advice about your specific case.
        </div>
      </form>
    </div>
  );
};

export default ChatInterface;