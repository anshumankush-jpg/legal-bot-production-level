import React from 'react';
import './AccessDenied.css';

const AccessDenied = () => {
  const handleContactSupport = () => {
    window.location.href = 'mailto:support@legalai.work?subject=Access Request';
  };

  const handleBackToLogin = () => {
    // Clear any stored auth data
    localStorage.clear();
    sessionStorage.clear();
    window.location.href = '/';
  };

  return (
    <div className="access-denied-container">
      <div className="access-denied-card">
        <div className="access-denied-icon">
          <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="#ff6b6b" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="15" y1="9" x2="9" y2="15"/>
            <line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
        </div>
        
        <h1 className="access-denied-title">Access Not Found</h1>
        
        <p className="access-denied-message">
          Your account is not authorized to access this application.
        </p>
        
        <p className="access-denied-submessage">
          If you believe this is an error, please contact our support team.
        </p>
        
        <div className="access-denied-actions">
          <button 
            className="btn-primary"
            onClick={handleContactSupport}
          >
            Contact Support
          </button>
          
          <button 
            className="btn-secondary"
            onClick={handleBackToLogin}
          >
            Back to Login
          </button>
        </div>
        
        <div className="access-denied-info">
          <p>Need access to LegalAI?</p>
          <p>Contact your administrator or email support@legalai.work</p>
        </div>
      </div>
    </div>
  );
};

export default AccessDenied;
