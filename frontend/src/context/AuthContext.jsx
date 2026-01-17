import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

const API_URL = 'http://localhost:8000';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Load user from localStorage on mount
  useEffect(() => {
    const savedToken = localStorage.getItem('legid_token');
    const savedUser = localStorage.getItem('legid_user');

    if (savedToken && savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setToken(savedToken);
        setUser(userData);
        setIsAuthenticated(true);
      } catch (e) {
        console.error('Error loading user:', e);
        logout();
      }
    }
    setLoading(false);
  }, []);

  // Check for OAuth callback parameters in URL
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const tokenParam = urlParams.get('token');
    const emailParam = urlParams.get('email');
    const nameParam = urlParams.get('name');
    const pictureParam = urlParams.get('picture');
    const errorParam = urlParams.get('error');

    if (errorParam) {
      console.error('OAuth error:', errorParam);
      window.history.replaceState({}, document.title, window.location.pathname);
      return;
    }

    if (tokenParam && emailParam) {
      const userData = {
        email: emailParam,
        name: nameParam || emailParam.split('@')[0],
        picture: pictureParam,
        user_id: `user_${emailParam.replace(/[^a-zA-Z0-9]/g, '_')}`
      };

      setToken(tokenParam);
      setUser(userData);
      setIsAuthenticated(true);

      localStorage.setItem('legid_token', tokenParam);
      localStorage.setItem('legid_user', JSON.stringify(userData));

      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  const loginWithEmail = async (email, password) => {
    try {
      const response = await fetch(`${API_URL}/api/auth/v2/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
      }

      const data = await response.json();
      
      const userData = {
        email: data.user?.email || email,
        name: data.user?.name || email.split('@')[0],
        picture: data.user?.picture || null,
        user_id: data.user?.id || `user_${email.replace(/[^a-zA-Z0-9]/g, '_')}`
      };

      setToken(data.access_token);
      setUser(userData);
      setIsAuthenticated(true);

      localStorage.setItem('legid_token', data.access_token);
      localStorage.setItem('legid_user', JSON.stringify(userData));

      return userData;
    } catch (error) {
      console.error('Email login error:', error);
      throw error;
    }
  };

  const registerWithEmail = async (email, password, name) => {
    try {
      const response = await fetch(`${API_URL}/api/auth/v2/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, name }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Registration failed');
      }

      const data = await response.json();
      
      const userData = {
        email: data.user?.email || email,
        name: data.user?.name || name || email.split('@')[0],
        picture: null,
        user_id: data.user?.id || `user_${email.replace(/[^a-zA-Z0-9]/g, '_')}`
      };

      setToken(data.access_token);
      setUser(userData);
      setIsAuthenticated(true);

      localStorage.setItem('legid_token', data.access_token);
      localStorage.setItem('legid_user', JSON.stringify(userData));

      return userData;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  };

  const loginWithGoogle = () => {
    window.location.href = `${API_URL}/api/auth/google/login`;
  };

  const loginWithMicrosoft = () => {
    alert('Microsoft login coming soon! Please use Email or Google login.');
  };

  const loginAsGuest = () => {
    const guestId = `guest_${Date.now()}`;
    const guestUser = {
      email: `${guestId}@guest.local`,
      name: 'Guest User',
      picture: null,
      user_id: guestId,
      isGuest: true
    };

    setToken('guest_token');
    setUser(guestUser);
    setIsAuthenticated(true);

    localStorage.setItem('legid_token', 'guest_token');
    localStorage.setItem('legid_user', JSON.stringify(guestUser));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    
    localStorage.removeItem('legid_token');
    localStorage.removeItem('legid_user');
    localStorage.removeItem('plaza_ai_preferences');
    localStorage.removeItem('plaza_ai_law_type');
  };

  const value = {
    user,
    token,
    loading,
    isAuthenticated,
    loginWithGoogle,
    loginWithMicrosoft,
    loginWithEmail,
    registerWithEmail,
    loginAsGuest,
    logout,
    API_URL
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;
