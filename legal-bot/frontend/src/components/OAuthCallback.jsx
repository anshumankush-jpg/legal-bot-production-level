import React, { useEffect, useState } from 'react';
import './OAuthCallback.css';

const API_BASE_URL = 'http://localhost:8000';

const OAuthCallback = ({ onAuthSuccess }) => {
  const [status, setStatus] = useState('processing');
  const [error, setError] = useState('');

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Get URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const state = urlParams.get('state');
        const error = urlParams.get('error');

        if (error) {
          throw new Error(`OAuth error: ${error}`);
        }

        if (!code || !state) {
          throw new Error('Missing authorization code or state');
        }

        // Get stored OAuth data from sessionStorage
        const storedState = sessionStorage.getItem('oauth_state');
        const codeVerifier = sessionStorage.getItem('oauth_code_verifier');
        const provider = sessionStorage.getItem('oauth_provider');
        const intendedRole = sessionStorage.getItem('oauth_intended_role');

        if (!storedState || !codeVerifier || !provider) {
          throw new Error('OAuth session data not found');
        }

        // Validate state (CSRF protection)
        if (state !== storedState) {
          throw new Error('Invalid state parameter - possible CSRF attack');
        }

        // Exchange code for tokens
        const response = await fetch(
          `${API_BASE_URL}/api/auth/oauth/${provider}/exchange`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              code,
              code_verifier: codeVerifier,
              state,
              intended_role: intendedRole || 'client'
            })
          }
        );

        const data = await response.json();

        if (!response.ok) {
          if (response.status === 403 && data?.detail?.code === 'NOT_PROVISIONED') {
            window.location.href = '/not-provisioned';
            return;
          }
          throw new Error(data.detail?.message || data.detail || 'OAuth exchange failed');
        }

        // Clear OAuth session data
        sessionStorage.removeItem('oauth_state');
        sessionStorage.removeItem('oauth_code_verifier');
        sessionStorage.removeItem('oauth_provider');
        sessionStorage.removeItem('oauth_intended_role');

        // Store tokens
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        localStorage.setItem('user', JSON.stringify(data.user));

        setStatus('success');

        // Redirect to appropriate portal
        setTimeout(() => {
          onAuthSuccess(data.user);
        }, 1500);
      } catch (err) {
        console.error('OAuth callback error:', err);
        setError(err.message);
        setStatus('error');
      }
    };

    handleCallback();
  }, [onAuthSuccess]);

  return (
    <div className="oauth-callback-container">
      <div className="oauth-callback-content">
        {status === 'processing' && (
          <div className="oauth-status">
            <div className="oauth-spinner"></div>
            <h2>Completing sign in...</h2>
            <p>Please wait while we verify your credentials</p>
          </div>
        )}

        {status === 'success' && (
          <div className="oauth-status success">
            <div className="oauth-checkmark">✓</div>
            <h2>Sign in successful!</h2>
            <p>Redirecting you to your portal...</p>
          </div>
        )}

        {status === 'error' && (
          <div className="oauth-status error">
            <h2>Sign in failed</h2>
            <p className="error-message">{error}</p>
            <button
              className="oauth-retry-button"
              onClick={() => window.location.href = '/'}
            >
              Return to Home
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default OAuthCallback;
