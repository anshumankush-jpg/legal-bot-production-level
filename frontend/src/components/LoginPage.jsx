import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import './LoginPage.css';

function LoginPage() {
  const { loginWithGoogle, loginWithMicrosoft, loginWithEmail, registerWithEmail } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [view, setView] = useState('main'); // 'main', 'email-login', 'signup', 'forgot-password'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleGoogleLogin = async () => {
    setIsLoading(true);
    setError('');
    loginWithGoogle();
  };

  const handleMicrosoftLogin = async () => {
    setIsLoading(true);
    setError('');
    loginWithMicrosoft();
    setIsLoading(false);
  };

  const handleEmailLogin = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await loginWithEmail(email, password);
    } catch (err) {
      setError(err.message || 'Login failed. Please check your credentials.');
      setIsLoading(false);
    }
  };

  const handleSignUp = async (e) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setIsLoading(true);

    try {
      await registerWithEmail(email, password, name);
      setSuccess('Account created successfully! You can now log in.');
      setTimeout(() => {
        setView('main');
        setSuccess('');
      }, 2000);
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.');
    }
    setIsLoading(false);
  };

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    // Simulate forgot password API call
    try {
      // In real implementation, call your backend API
      await new Promise(resolve => setTimeout(resolve, 1500));
      setSuccess('Password reset link sent to your email!');
      setTimeout(() => {
        setView('main');
        setSuccess('');
        setEmail('');
      }, 3000);
    } catch (err) {
      setError('Failed to send reset email. Please try again.');
    }
    setIsLoading(false);
  };

  const resetForm = () => {
    setEmail('');
    setPassword('');
    setConfirmPassword('');
    setName('');
    setError('');
    setSuccess('');
  };

  const switchView = (newView) => {
    resetForm();
    setView(newView);
  };

  return (
    <div className="login-page">
      {/* Blurred Background - Chatbot Preview */}
      <div className="login-background">
        {/* Simulated Chat Interface */}
        <div className="bg-chat-interface">
          {/* Sidebar */}
          <div className="bg-sidebar">
            <div className="bg-sidebar-item active"></div>
            <div className="bg-sidebar-item"></div>
            <div className="bg-sidebar-item"></div>
            <div className="bg-sidebar-item"></div>
          </div>
          
          {/* Main Chat Area */}
          <div className="bg-chat-main">
            <div className="bg-chat-header">
              <div className="bg-header-text"></div>
            </div>
            <div className="bg-chat-messages">
              <div className="bg-message user"></div>
              <div className="bg-message assistant"></div>
              <div className="bg-message user short"></div>
              <div className="bg-message assistant long"></div>
            </div>
            <div className="bg-chat-input">
              <div className="bg-input-box"></div>
            </div>
          </div>
        </div>

        {/* Blur Overlay */}
        <div className="blur-overlay"></div>
      </div>

      {/* Login Modal */}
      <div className="login-modal">
        <button className="modal-close" onClick={() => window.history.back()} title="Close">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>

        {/* Logo */}
        <div className="modal-logo">
          <svg viewBox="0 0 50 50" fill="none">
            <path d="M25 5L45 15V35L25 45L5 35V15L25 5Z" stroke="white" strokeWidth="2" fill="none"/>
            <path d="M25 15L35 20V30L25 35L15 30V20L25 15Z" fill="white" opacity="0.3"/>
            <circle cx="25" cy="25" r="5" fill="white"/>
          </svg>
          <span className="modal-logo-text">LEGID AI</span>
        </div>

        {/* Main Login View */}
        {view === 'main' && (
          <>
            <h1 className="modal-title">Log into your account</h1>
            <p className="modal-subtitle">Your AI-powered legal assistant</p>

            {error && <div className="modal-error">{error}</div>}
            {success && <div className="modal-success">{success}</div>}

            <div className="modal-buttons">
              {/* Google Login */}
              <button 
                className="modal-btn google-btn"
                onClick={handleGoogleLogin}
                disabled={isLoading}
              >
                <svg className="btn-icon" viewBox="0 0 24 24" width="20" height="20">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                <span>Continue with Google</span>
              </button>

              {/* Microsoft Login */}
              <button 
                className="modal-btn microsoft-btn"
                onClick={handleMicrosoftLogin}
                disabled={isLoading}
              >
                <svg className="btn-icon" viewBox="0 0 23 23" width="18" height="18">
                  <path fill="#f25022" d="M1 1h10v10H1z"/>
                  <path fill="#00a4ef" d="M12 1h10v10H12z"/>
                  <path fill="#7fba00" d="M1 12h10v10H1z"/>
                  <path fill="#ffb900" d="M12 12h10v10H12z"/>
                </svg>
                <span>Continue with Microsoft</span>
              </button>

              {/* Email and Password */}
              <button 
                className="modal-btn email-btn"
                onClick={() => switchView('email-login')}
                disabled={isLoading}
              >
                <svg className="btn-icon" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="2" y="4" width="20" height="16" rx="2"/>
                  <path d="M22 6L12 13 2 6"/>
                </svg>
                <span>Email and password</span>
              </button>
            </div>

            <div className="modal-divider">
              <span>OR</span>
            </div>

            {/* Quick Email Input */}
            <form className="quick-email-form" onSubmit={(e) => { e.preventDefault(); switchView('email-login'); }}>
              <input
                type="email"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="modal-input"
              />
              <button type="submit" className="modal-continue-btn" disabled={isLoading}>
                Continue
              </button>
            </form>

            <p className="modal-signup-link">
              No account yet? <button onClick={() => switchView('signup')}>Sign up</button>
            </p>
          </>
        )}

        {/* Email Login View */}
        {view === 'email-login' && (
          <>
            <h1 className="modal-title">Sign in with email</h1>
            <p className="modal-subtitle">Enter your credentials to continue</p>

            {error && <div className="modal-error">{error}</div>}

            <form className="modal-form" onSubmit={handleEmailLogin}>
              <div className="form-group">
                <label>Email address</label>
                <input
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="modal-input"
                  required
                  disabled={isLoading}
                />
              </div>

              <div className="form-group">
                <label>Password</label>
                <input
                  type="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="modal-input"
                  required
                  disabled={isLoading}
                />
              </div>

              <button 
                type="button" 
                className="forgot-password-link"
                onClick={() => switchView('forgot-password')}
              >
                Forgot password?
              </button>

              <button type="submit" className="modal-continue-btn" disabled={isLoading}>
                {isLoading ? <span className="spinner"></span> : 'Sign In'}
              </button>
            </form>

            <p className="modal-signup-link">
              No account yet? <button onClick={() => switchView('signup')}>Sign up</button>
            </p>

            <button className="back-link" onClick={() => switchView('main')}>
              ← Back to login options
            </button>
          </>
        )}

        {/* Sign Up View */}
        {view === 'signup' && (
          <>
            <h1 className="modal-title">Create your account</h1>
            <p className="modal-subtitle">Join LEGID and get AI legal assistance</p>

            {error && <div className="modal-error">{error}</div>}
            {success && <div className="modal-success">{success}</div>}

            <form className="modal-form" onSubmit={handleSignUp}>
              <div className="form-group">
                <label>Full Name</label>
                <input
                  type="text"
                  placeholder="John Doe"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="modal-input"
                  required
                  disabled={isLoading}
                />
              </div>

              <div className="form-group">
                <label>Email address</label>
                <input
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="modal-input"
                  required
                  disabled={isLoading}
                />
              </div>

              <div className="form-group">
                <label>Password</label>
                <input
                  type="password"
                  placeholder="At least 6 characters"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="modal-input"
                  required
                  minLength={6}
                  disabled={isLoading}
                />
              </div>

              <div className="form-group">
                <label>Confirm Password</label>
                <input
                  type="password"
                  placeholder="Re-enter your password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="modal-input"
                  required
                  disabled={isLoading}
                />
              </div>

              <button type="submit" className="modal-continue-btn" disabled={isLoading}>
                {isLoading ? <span className="spinner"></span> : 'Create Account'}
              </button>
            </form>

            <p className="modal-signup-link">
              Already have an account? <button onClick={() => switchView('main')}>Sign in</button>
            </p>

            <button className="back-link" onClick={() => switchView('main')}>
              ← Back to login options
            </button>
          </>
        )}

        {/* Forgot Password View */}
        {view === 'forgot-password' && (
          <>
            <h1 className="modal-title">Reset your password</h1>
            <p className="modal-subtitle">We'll send you a link to reset it</p>

            {error && <div className="modal-error">{error}</div>}
            {success && <div className="modal-success">{success}</div>}

            <form className="modal-form" onSubmit={handleForgotPassword}>
              <div className="form-group">
                <label>Email address</label>
                <input
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="modal-input"
                  required
                  disabled={isLoading}
                />
              </div>

              <button type="submit" className="modal-continue-btn" disabled={isLoading}>
                {isLoading ? <span className="spinner"></span> : 'Send Reset Link'}
              </button>
            </form>

            <button className="back-link" onClick={() => switchView('email-login')}>
              ← Back to sign in
            </button>
          </>
        )}

        {/* Footer Links */}
        <div className="modal-footer">
          <p>By using LEGID you agree to the <a href="/terms">Terms</a>, <a href="/privacy">Privacy</a> and <a href="/cookies">Cookies</a></p>
        </div>
      </div>

      {/* Bottom Banner */}
      <div className="bottom-banner">
        <span className="banner-badge">New</span>
        <span className="banner-text">AI-powered legal research for Canada & USA. Get started with LEGID today.</span>
        <button className="banner-btn">Explore</button>
      </div>
    </div>
  );
}

export default LoginPage;
