import React, { useState } from 'react';
import './NotProvisioned.css';

const API_BASE_URL = 'http://localhost:8000';

const NotProvisioned = ({ email }) => {
  const [formData, setFormData] = useState({
    email: email || '',
    name: '',
    organization: '',
    requested_role: 'client',
    reason: ''
  });
  const [status, setStatus] = useState({ type: '', message: '' });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatus({ type: '', message: '' });
    try {
      const response = await fetch(`${API_BASE_URL}/api/profile/request-access`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail?.message || data.detail || 'Request failed');
      }
      setStatus({ type: 'success', message: 'Access request submitted. We will reach out shortly.' });
    } catch (err) {
      setStatus({ type: 'error', message: err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="not-provisioned-container">
      <div className="not-provisioned-card">
        <h1 className="not-provisioned-title">Account not found / not provisioned</h1>
        <p className="not-provisioned-message">
          This account is not yet provisioned for LEGID. You can request access below or contact our team.
        </p>

        <div className="not-provisioned-contact">
          Contact: <a href="mailto:info@predictivetechlabs.com">info@predictivetechlabs.com</a>
        </div>

        <form className="request-access-form" onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder="you@example.com"
              />
            </div>
            <div className="form-group">
              <label>Full Name</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="Your name"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Organization</label>
              <input
                type="text"
                name="organization"
                value={formData.organization}
                onChange={handleChange}
                placeholder="Company or firm"
              />
            </div>
            <div className="form-group">
              <label>Requested Role</label>
              <select name="requested_role" value={formData.requested_role} onChange={handleChange}>
                <option value="client">Client</option>
                <option value="lawyer">Lawyer</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Reason for Access</label>
            <textarea
              name="reason"
              value={formData.reason}
              onChange={handleChange}
              rows={4}
              placeholder="Briefly describe your use case"
            />
          </div>

          {status.message && (
            <div className={`request-status ${status.type}`}>
              {status.message}
            </div>
          )}

          <div className="form-actions">
            <button type="submit" className="request-access-btn" disabled={loading}>
              {loading ? 'Submitting...' : 'Request Access'}
            </button>
            <button
              type="button"
              className="back-to-login-btn"
              onClick={() => window.location.href = '/'}
            >
              Back to Login
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default NotProvisioned;
