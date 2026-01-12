import React, { useState, useEffect } from 'react';
import './EmployeePortal.css';

const API_BASE_URL = 'http://localhost:8000';

const EmployeePortal = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [matters, setMatters] = useState([]);
  const [selectedMatter, setSelectedMatter] = useState(null);
  const [messages, setMessages] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [emailConnections, setEmailConnections] = useState([]);
  const [sentEmails, setSentEmails] = useState([]);
  const [showEmailCompose, setShowEmailCompose] = useState(false);
  const [emailForm, setEmailForm] = useState({ to: '', subject: '', body: '', matter_id: null });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [stats, setStats] = useState({ assigned_matters: 0 });

  const getAuthHeaders = () => ({
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
    'Content-Type': 'application/json'
  });

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/employee/dashboard`, {
        headers: getAuthHeaders()
      });
      const data = await response.json();
      setStats(data.stats);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    }
  };

  const loadMatters = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/employee/matters`, {
        headers: getAuthHeaders()
      });
      const data = await response.json();
      setMatters(data);
    } catch (err) {
      setError('Failed to load matters');
    } finally {
      setLoading(false);
    }
  };

  const loadMatterDetails = async (matterId) => {
    try {
      setLoading(true);
      const [matterRes, messagesRes, docsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/employee/matters/${matterId}`, { headers: getAuthHeaders() }),
        fetch(`${API_BASE_URL}/api/employee/matters/${matterId}/messages`, { headers: getAuthHeaders() }),
        fetch(`${API_BASE_URL}/api/employee/matters/${matterId}/documents`, { headers: getAuthHeaders() })
      ]);

      const matter = await matterRes.json();
      const msgs = await messagesRes.json();
      const docs = await docsRes.json();

      setSelectedMatter(matter);
      setMessages(msgs);
      setDocuments(docs);
      setActiveTab('matter-detail');
    } catch (err) {
      setError('Failed to load matter details');
    } finally {
      setLoading(false);
    }
  };

  const loadEmailConnections = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/email/connections`, {
        headers: getAuthHeaders()
      });
      const data = await response.json();
      setEmailConnections(data);
    } catch (err) {
      console.error('Failed to load email connections:', err);
    }
  };

  const connectGmail = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/email/connect/gmail/start`, {
        headers: getAuthHeaders()
      });
      const data = await response.json();
      
      // Store state for callback
      sessionStorage.setItem('email_oauth_state', data.state);
      
      // Redirect to Gmail OAuth
      window.location.href = data.auth_url;
    } catch (err) {
      setError('Failed to start Gmail connection');
    }
  };

  const sendEmail = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/email/send`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(emailForm)
      });

      if (!response.ok) {
        throw new Error('Failed to send email');
      }

      alert('Email sent successfully!');
      setShowEmailCompose(false);
      setEmailForm({ to: '', subject: '', body: '', matter_id: null });
      loadSentEmails();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadSentEmails = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/email/sent`, {
        headers: getAuthHeaders()
      });
      const data = await response.json();
      setSentEmails(data);
    } catch (err) {
      console.error('Failed to load sent emails:', err);
    }
  };

  useEffect(() => {
    if (activeTab === 'matters') {
      loadMatters();
    } else if (activeTab === 'email') {
      loadEmailConnections();
      loadSentEmails();
    }
  }, [activeTab]);

  return (
    <div className="employee-portal">
      <div className="employee-sidebar">
        <div className="employee-header">
          <h2>Employee Portal</h2>
          <p>{user.name}</p>
          <span className="role-badge">{user.role}</span>
        </div>

        <nav className="employee-nav">
          <button
            className={activeTab === 'dashboard' ? 'active' : ''}
            onClick={() => setActiveTab('dashboard')}
          >
            📊 Dashboard
          </button>
          <button
            className={activeTab === 'matters' ? 'active' : ''}
            onClick={() => setActiveTab('matters')}
          >
            📁 Matters
          </button>
          <button
            className={activeTab === 'email' ? 'active' : ''}
            onClick={() => setActiveTab('email')}
          >
            ✉️ Email
          </button>
          <button onClick={onLogout} className="logout-button">
            🚪 Logout
          </button>
        </nav>
      </div>

      <div className="employee-main">
        {error && (
          <div className="employee-error">
            <span>⚠️</span> {error}
            <button onClick={() => setError('')}>✕</button>
          </div>
        )}

        {activeTab === 'dashboard' && (
          <div className="employee-dashboard">
            <h1>Dashboard</h1>
            <div className="dashboard-stats">
              <div className="stat-card">
                <h3>Assigned Matters</h3>
                <p className="stat-number">{stats.assigned_matters}</p>
              </div>
              <div className="stat-card">
                <h3>Role</h3>
                <p className="stat-text">{user.role}</p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'matters' && (
          <div className="employee-matters">
            <h1>Assigned Matters</h1>
            {loading ? (
              <p>Loading...</p>
            ) : (
              <div className="matters-list">
                {matters.map((matter) => (
                  <div
                    key={matter.id}
                    className="matter-card"
                    onClick={() => loadMatterDetails(matter.id)}
                  >
                    <h3>{matter.title}</h3>
                    <p>{matter.description}</p>
                    <div className="matter-meta">
                      <span>Status: {matter.status}</span>
                      <span>Client: {matter.user_email}</span>
                      <span>{matter.message_count} messages</span>
                      <span>{matter.document_count} documents</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'matter-detail' && selectedMatter && (
          <div className="matter-detail">
            <button onClick={() => setActiveTab('matters')} className="back-button">
              ← Back to Matters
            </button>
            <h1>{selectedMatter.title}</h1>
            <p>{selectedMatter.description}</p>
            <div className="matter-info">
              <p><strong>Client:</strong> {selectedMatter.user_email}</p>
              <p><strong>Status:</strong> {selectedMatter.status}</p>
            </div>

            <h2>Chat History</h2>
            <div className="messages-list">
              {messages.map((msg) => (
                <div key={msg.id} className={`message ${msg.role}`}>
                  <strong>{msg.role}:</strong>
                  <p>{msg.content}</p>
                  <small>{new Date(msg.created_at).toLocaleString()}</small>
                </div>
              ))}
            </div>

            <h2>Documents</h2>
            <div className="documents-list">
              {documents.map((doc) => (
                <div key={doc.id} className="document-item">
                  <span>📄 {doc.filename}</span>
                  <span>{doc.document_type}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'email' && (
          <div className="employee-email">
            <h1>Email Management</h1>
            
            <div className="email-connections">
              <h2>Email Connections</h2>
              {emailConnections.length === 0 ? (
                <div className="no-connection">
                  <p>No email account connected</p>
                  <button onClick={connectGmail} className="connect-button">
                    Connect Gmail
                  </button>
                </div>
              ) : (
                <div className="connections-list">
                  {emailConnections.map((conn) => (
                    <div key={conn.id} className="connection-item">
                      <span>{conn.provider}: {conn.provider_email}</span>
                      <span className={conn.is_active ? 'active' : 'inactive'}>
                        {conn.is_active ? '✓ Active' : '✗ Inactive'}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {emailConnections.length > 0 && (
              <>
                <button
                  onClick={() => setShowEmailCompose(true)}
                  className="compose-button"
                >
                  ✉️ Compose Email
                </button>

                {showEmailCompose && (
                  <div className="email-compose-modal">
                    <div className="modal-content">
                      <h2>Compose Email</h2>
                      <input
                        type="email"
                        placeholder="To"
                        value={emailForm.to}
                        onChange={(e) => setEmailForm({ ...emailForm, to: e.target.value })}
                      />
                      <input
                        type="text"
                        placeholder="Subject"
                        value={emailForm.subject}
                        onChange={(e) => setEmailForm({ ...emailForm, subject: e.target.value })}
                      />
                      <textarea
                        placeholder="Email body"
                        value={emailForm.body}
                        onChange={(e) => setEmailForm({ ...emailForm, body: e.target.value })}
                        rows="10"
                      />
                      <div className="modal-actions">
                        <button onClick={sendEmail} disabled={loading}>
                          {loading ? 'Sending...' : 'Send Email'}
                        </button>
                        <button onClick={() => setShowEmailCompose(false)}>Cancel</button>
                      </div>
                    </div>
                  </div>
                )}

                <h2>Sent Emails</h2>
                <div className="sent-emails-list">
                  {sentEmails.map((email) => (
                    <div key={email.id} className="sent-email-item">
                      <strong>To: {email.to_email}</strong>
                      <p>Subject: {email.subject}</p>
                      <small>{new Date(email.sent_at).toLocaleString()}</small>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default EmployeePortal;
