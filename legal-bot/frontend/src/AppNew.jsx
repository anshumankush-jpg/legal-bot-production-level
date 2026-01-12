import React, { useState, useEffect } from 'react';
import RoleSelection from './components/RoleSelection';
import AuthPage from './components/AuthPage';
import OAuthCallback from './components/OAuthCallback';
import ResetPassword from './components/ResetPassword';
import EmployeePortal from './components/EmployeePortal';
import ChatInterface from './components/ChatInterface';
import './App.css';

function AppNew() {
  const [currentView, setCurrentView] = useState('role-selection');
  const [selectedRole, setSelectedRole] = useState(null);
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Check if user is already logged in
    const storedUser = localStorage.getItem('user');
    const accessToken = localStorage.getItem('access_token');

    if (storedUser && accessToken) {
      try {
        const userData = JSON.parse(storedUser);
        setUser(userData);
        setSelectedRole(userData.role);
        routeToPortal(userData.role);
      } catch (err) {
        console.error('Failed to parse stored user:', err);
        localStorage.clear();
      }
    }

    // Check if this is an OAuth callback
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('code')) {
      setCurrentView('oauth-callback');
    } else if (window.location.pathname === '/reset-password') {
      setCurrentView('reset-password');
    }
  }, []);

  const handleRoleSelect = (role) => {
    setSelectedRole(role);
    setCurrentView('auth');
  };

  const handleAuthSuccess = (userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
    routeToPortal(userData.role);
  };

  const routeToPortal = (role) => {
    switch (role) {
      case 'client':
        setCurrentView('client-portal');
        break;
      case 'employee':
      case 'employee_admin':
        setCurrentView('employee-portal');
        break;
      case 'lawyer':
        setCurrentView('lawyer-portal');
        break;
      default:
        setCurrentView('client-portal');
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    sessionStorage.clear();
    setUser(null);
    setSelectedRole(null);
    setCurrentView('role-selection');
  };

  // Render based on current view
  if (currentView === 'role-selection') {
    return <RoleSelection onRoleSelect={handleRoleSelect} />;
  }

  if (currentView === 'auth') {
    return <AuthPage role={selectedRole} onAuthSuccess={handleAuthSuccess} />;
  }

  if (currentView === 'oauth-callback') {
    return <OAuthCallback onAuthSuccess={handleAuthSuccess} />;
  }

  if (currentView === 'reset-password') {
    return <ResetPassword />;
  }

  if (currentView === 'employee-portal') {
    return <EmployeePortal user={user} onLogout={handleLogout} />;
  }

  if (currentView === 'client-portal') {
    // Use existing ChatInterface for clients
    return (
      <div>
        <div style={{ padding: '20px', background: '#2d3748', color: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2>LEGID - Client Portal</h2>
            <p>Welcome, {user?.name || user?.email}</p>
          </div>
          <button
            onClick={handleLogout}
            style={{
              padding: '10px 20px',
              background: '#e53e3e',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer'
            }}
          >
            Logout
          </button>
        </div>
        <ChatInterface preferences={{ name: user?.name }} />
      </div>
    );
  }

  if (currentView === 'lawyer-portal') {
    return (
      <div style={{ minHeight: '100vh', background: '#f7fafc', padding: '40px' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <div style={{ background: 'white', padding: '40px', borderRadius: '12px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
            <h1 style={{ color: '#E94B3C', marginBottom: '20px' }}>Lawyer Portal</h1>
            <p>Welcome, {user?.name || user?.email}</p>
            <p style={{ color: '#718096', marginTop: '20px' }}>
              Lawyer portal features coming soon:
            </p>
            <ul style={{ color: '#718096', marginTop: '10px' }}>
              <li>View shared matters from clients</li>
              <li>Manage booking requests</li>
              <li>Access client documents</li>
              <li>Update lawyer profile</li>
            </ul>
            <button
              onClick={handleLogout}
              style={{
                marginTop: '30px',
                padding: '12px 24px',
                background: '#e53e3e',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: '600'
              }}
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    );
  }

  return null;
}

export default AppNew;
