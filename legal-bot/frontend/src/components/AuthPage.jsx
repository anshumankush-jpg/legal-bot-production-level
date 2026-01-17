import React, { useState } from 'react';
import './AuthPage.css';

const API_BASE_URL = 'http://localhost:8000';

// SVG Icons for OAuth
const GoogleIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24">
    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
  </svg>
);

const MicrosoftIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24">
    <path fill="#F25022" d="M1 1h10v10H1z"/>
    <path fill="#00A4EF" d="M1 13h10v10H1z"/>
    <path fill="#7FBA00" d="M13 1h10v10H13z"/>
    <path fill="#FFB900" d="M13 13h10v10H13z"/>
  </svg>
);

const AuthPage = ({ role, onAuthSuccess, onNotProvisioned }) => {
  const [mode, setMode] = useState('login'); // 'login', 'forgot'
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const roleConfig = {
    client: { title: 'User Portal', accent: '#00d4ff' },
    lawyer: { title: 'Lawyer Portal', accent: '#ff6b6b' }
  };

  const config = roleConfig[role] || roleConfig.client;

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');
    setLoading(true);

    try {
      if (mode === 'login') {
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: formData.email,
            password: formData.password
          })
        });

        const data = await response.json();

        if (response.status === 403 && data?.detail?.code === 'NOT_PROVISIONED') {
          if (onNotProvisioned) {
            onNotProvisioned(formData.email);
          }
          return;
        }

        if (!response.ok) {
          throw new Error(data.detail?.message || data.detail || 'Login failed');
        }

        // Check if user role matches selected role
        if (data.user.role !== role) {
          throw new Error(`This account is registered as ${data.user.role}, not ${role}`);
        }

        // Store tokens
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        localStorage.setItem('user', JSON.stringify(data.user));

        onAuthSuccess(data.user);
      } else if (mode === 'forgot') {
        const response = await fetch(`${API_BASE_URL}/api/auth/forgot-password`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: formData.email })
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail?.message || data.detail || 'Request failed');
        }

        setMessage('If the email exists, a password reset link has been sent. Check your console (dev mode).');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleOAuthLogin = async (provider) => {
    try {
      setLoading(true);
      setError('');

      // Get OAuth start URL
      const response = await fetch(
        `${API_BASE_URL}/api/auth/oauth/${provider}/start?intended_role=${role}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail?.message || data.detail || 'OAuth start failed');
      }

      // Store state and code_verifier in sessionStorage
      sessionStorage.setItem('oauth_state', data.state);
      sessionStorage.setItem('oauth_code_verifier', data.code_verifier);
      sessionStorage.setItem('oauth_provider', provider);
      sessionStorage.setItem('oauth_intended_role', role);

      // Redirect to OAuth provider
      window.location.href = data.auth_url;
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <div className="auth-page-container">
      <div className="auth-page-content">
        <div className="auth-card" data-role={role}>
          <div className="auth-header">
            <h1 className="auth-title">
              {config.title}
            </h1>
            <p className="auth-subtitle">
              {mode === 'login' && 'Sign in to your account'}
              {mode === 'register' && 'Create a new account'}
              {mode === 'forgot' && 'Reset your password'}
            </p>
          </div>

          {error && (
            <div className="auth-error">
              {error}
            </div>
          )}

          {message && (
            <div className="auth-message">
              {message}
            </div>
          )}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label htmlFor="email">Email Address</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder="you@example.com"
              />
            </div>

            {mode !== 'forgot' && (
              <div className="form-group">
                <label htmlFor="password">Password</label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  placeholder="••••••••"
                />
              </div>
            )}

            <button
              type="submit"
              className="auth-submit-button"
              disabled={loading}
            >
              {loading ? 'Please wait...' : (
                mode === 'login' ? 'Sign In →' :
                'Send Reset Link →'
              )}
            </button>
          </form>

          {mode !== 'forgot' && (
            <>
              <div className="auth-divider">
                <span>OR</span>
              </div>

              <div className="oauth-buttons">
                <button
                  className="oauth-button google"
                  onClick={() => handleOAuthLogin('google')}
                  disabled={loading}
                >
                  <span className="oauth-icon"><GoogleIcon /></span>
                  Continue with Google
                </button>

                <button
                  className="oauth-button microsoft"
                  onClick={() => handleOAuthLogin('microsoft')}
                  disabled={loading}
                >
                  <span className="oauth-icon"><MicrosoftIcon /></span>
                  Continue with Microsoft
                </button>
              </div>
            </>
          )}

          <div className="auth-footer">
            {mode === 'login' && (
              <>
                <button
                  className="auth-link-button"
                  onClick={() => setMode('forgot')}
                >
                  Forgot password?
                </button>
              </>
            )}

            {mode === 'forgot' && (
              <>
                <span>Remember your password?</span>
                <button
                  className="auth-link-button"
                  onClick={() => setMode('login')}
                >
                  Back to sign in
                </button>
              </>
            )}
          </div>

          <div className="auth-support">
            <p>
              Need help? Contact{' '}
              <a href="mailto:info@predictivetechlabs.com">
                info@predictivetechlabs.com
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
